# Emotion Labeling Task (CSE 594 A1-2)

Flask app that labels tweets from the [dair-ai/emotion dataset](https://huggingface.co/datasets/dair-ai/emotion) with one of six emotions (anger, fear, joy, love, sadness, surprise). Each participant labels 5 randomly sampled tweets; labels are stored in SQLite along with participant ID and tweet ID.

Live link: **https://emotion-labeling-app.onrender.com/**

Hosted on Render's free tier, which spins down after ~15 min idle, so the first request after a while may take up to a minute to respond. Reload if the first load seems stuck.

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5050/. `labels.db` is created automatically on first run.

Set `FLASK_SECRET_KEY` in the environment for a stable session secret; if unset, a random one is generated at process start (fine locally, but sessions won't survive a restart).

Collected data can be viewed at `/admin/data` (HTML table) or `/admin/data.json`.

## Regenerating the tweet sample (optional)

`data/tweets.json` (60 tweets, 10 per emotion) is already generated and checked in. To regenerate:

```bash
pip install datasets
python build_dataset.py
```
