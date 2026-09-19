import json
import os
import random
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "labels.db"
TWEETS_PATH = BASE_DIR / "data" / "tweets.json"
EMOTIONS = ["anger", "fear", "joy", "love", "sadness", "surprise"]
TWEETS_PER_PARTICIPANT = 5

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

with open(TWEETS_PATH) as f:
    TWEETS = json.load(f)
TWEETS_BY_ID = {t["id"]: t for t in TWEETS}


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id TEXT NOT NULL,
                tweet_id INTEGER NOT NULL,
                tweet_text TEXT NOT NULL,
                label TEXT NOT NULL,
                submitted_at TEXT NOT NULL
            )
            """
        )
        db.commit()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    # New participant session: assign a random participant id and 5 random tweets.
    session["participant_id"] = str(uuid.uuid4())[:8]
    session["assigned_ids"] = random.sample(list(TWEETS_BY_ID.keys()), TWEETS_PER_PARTICIPANT)
    session["current_index"] = 0
    return redirect(url_for("label_task"))


@app.route("/label", methods=["GET", "POST"])
def label_task():
    if "participant_id" not in session:
        return redirect(url_for("index"))

    assigned_ids = session["assigned_ids"]
    idx = session["current_index"]

    if request.method == "POST":
        chosen_label = request.form.get("emotion")
        if chosen_label not in EMOTIONS:
            return render_template(
                "label.html",
                tweet=TWEETS_BY_ID[assigned_ids[idx]],
                emotions=EMOTIONS,
                progress=idx + 1,
                total=TWEETS_PER_PARTICIPANT,
                error="Please select an emotion before submitting.",
            )

        tweet = TWEETS_BY_ID[assigned_ids[idx]]
        db = get_db()
        db.execute(
            "INSERT INTO labels (participant_id, tweet_id, tweet_text, label, submitted_at) VALUES (?, ?, ?, ?, ?)",
            (
                session["participant_id"],
                tweet["id"],
                tweet["text"],
                chosen_label,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        db.commit()

        idx += 1
        session["current_index"] = idx

        if idx >= TWEETS_PER_PARTICIPANT:
            return redirect(url_for("done"))
        return redirect(url_for("label_task"))

    tweet = TWEETS_BY_ID[assigned_ids[idx]]
    return render_template(
        "label.html",
        tweet=tweet,
        emotions=EMOTIONS,
        progress=idx + 1,
        total=TWEETS_PER_PARTICIPANT,
        error=None,
    )


@app.route("/done")
def done():
    participant_id = session.get("participant_id")
    return render_template("done.html", participant_id=participant_id)


@app.route("/admin/data")
def admin_data():
    # Simple read-only view of collected data for testing / grading purposes.
    db = get_db()
    rows = db.execute(
        "SELECT id, participant_id, tweet_id, tweet_text, label, submitted_at FROM labels ORDER BY id DESC"
    ).fetchall()
    return render_template("admin.html", rows=rows)


@app.route("/admin/data.json")
def admin_data_json():
    db = get_db()
    rows = db.execute(
        "SELECT id, participant_id, tweet_id, tweet_text, label, submitted_at FROM labels ORDER BY id DESC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5050)
else:
    init_db()
