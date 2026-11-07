"""
MODULE 3: SENTIMENT ANALYSIS
Reads clean_posts.csv (made by Module 2) and writes sentiment_posts.csv.

VADER is a ready-made, rule-based sentiment tool built for social media text.
It needs no training. We give it raw_text (the original wording) instead of
clean_text, because VADER uses words like "not", CAPITAL LETTERS and "!!!"
to judge feeling, and cleaning would throw those away.

Setup (run once in the terminal):
    python -m pip install pandas vaderSentiment

Run:
    python 3_sentiment_analysis.py
"""
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


def get_sentiment(text):
    """Return (score, label). The score runs from -1 (very negative) to +1 (very positive)."""
    if not isinstance(text, str) or not text.strip():
        return 0.0, "neutral"
    score = analyzer.polarity_scores(text)["compound"]
    if score >= 0.05:
        label = "positive"
    elif score <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return score, label


def add_sentiment(df):
    """Add sentiment_score and sentiment_label columns."""
    if "raw_text" not in df.columns:  # safety net if Module 2 was an older version
        df["raw_text"] = df["title"].fillna("") + " " + df["text"].fillna("")
    results = df["raw_text"].apply(get_sentiment)
    df["sentiment_score"] = results.apply(lambda pair: pair[0])
    df["sentiment_label"] = results.apply(lambda pair: pair[1])
    return df


if __name__ == "__main__":
    df = pd.read_csv("clean_posts.csv")
    df = add_sentiment(df)
    df.to_csv("sentiment_posts.csv", index=False)

    print(f"Scored {len(df)} posts -> saved to sentiment_posts.csv")
    print(df["sentiment_label"].value_counts().to_string())
