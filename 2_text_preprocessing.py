"""
MODULE 2: TEXT PRE-PROCESSING
Reads raw_posts.csv (made by Module 1) and writes clean_posts.csv.

Setup (run once in the terminal):
    python -m pip install pandas nltk

Run:
    python 2_text_preprocessing.py
"""
import re

import nltk
import pandas as pd

nltk.download("stopwords", quiet=True)  # one-time download; skipped if already there
from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words("english"))


def clean_text(text):
    """Turn one raw post into a string of clean, lowercase words."""
    if not isinstance(text, str):
        return ""
    text = text.lower()                                 # 1. make everything lowercase
    text = re.sub(r"http\S+|www\S+", " ", text)         # 2. remove links
    text = re.sub(r"[^a-z\s]", " ", text)               # 3. keep letters only
    words = text.split()                                # 4. split into words
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]  # 5. drop filler words
    return " ".join(words)


def preprocess_dataframe(df):
    """Add raw_text and clean_text columns, then drop posts that end up empty."""
    df["raw_text"] = (df["title"].fillna("") + " " + df["text"].fillna("")).str.strip()
    df["clean_text"] = df["raw_text"].apply(clean_text)
    df = df[df["clean_text"].str.len() > 0].reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = pd.read_csv("raw_posts.csv")
    total = len(df)
    df = preprocess_dataframe(df)
    df.to_csv("clean_posts.csv", index=False)

    print(f"Read {total} posts, kept {len(df)} after cleaning -> saved to clean_posts.csv")
    print("\nFirst 3 cleaned posts:")
    for number, text in enumerate(df["clean_text"].head(3), start=1):
        print(f"{number}. {text}")
