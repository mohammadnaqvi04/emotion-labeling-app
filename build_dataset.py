import json
import random

from datasets import load_dataset

SEED = 42
PER_EMOTION = 10
MIN_LEN, MAX_LEN = 20, 140
OUTPUT_PATH = "data/tweets.json"


def main():
    random.seed(SEED)
    ds = load_dataset("dair-ai/emotion", "split")["train"]
    label_names = ds.features[
        "label"
    ].names  # ['sadness','joy','love','anger','fear','surprise']

    by_label = {name: [] for name in label_names}
    for ex in ds:
        text = ex["text"].strip()
        if MIN_LEN <= len(text) <= MAX_LEN:
            by_label[label_names[ex["label"]]].append(text)

    sample = []
    for name in label_names:
        picks = random.sample(by_label[name], PER_EMOTION)
        for text in picks:
            sample.append({"text": text, "emotion": name})

    random.shuffle(sample)
    for i, row in enumerate(sample, start=1):
        row["id"] = i

    with open(OUTPUT_PATH, "w") as f:
        json.dump(sample, f, indent=2)

    print(f"Saved {len(sample)} tweets to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
