"""
MODULE 4: MISINFORMATION FLAGGING (Layer 1: simple rules)
Reads sentiment_posts.csv (made by Module 3) and writes flagged_posts.csv.

Layer 1 looks for clickbait and sensational phrases and gives every post a
risk level: low_risk, medium_risk or high_risk. This is a quick warning sign,
NOT proof that a post is false. (Layer 2, a trained classifier, comes in Level 3.)

We search raw_text (the original wording), because the cleaned text has
words like "you", "to" and "up" removed, so some phrases could never match.

Run:
    python 4_misinformation_flagging.py
"""
import re

import pandas as pd

SENSATIONAL_PATTERNS = [
    r"\bshocking\b",
    r"\bthey don'?t want you to know\b",
    r"\bbreaking\b.*\bconfirmed\b",
    r"\b100% true\b",
    r"\bmiracle\b",
    r"\bgovernment hiding\b",
    r"\bwake up\b",
]


def prepare(text):
    """Lowercase the text and turn curly apostrophes into normal ones."""
    if not isinstance(text, str):
        return ""
    return text.lower().replace("\u2019", "'")


def rule_based_flag(text):
    """2 or more phrases = high_risk, 1 phrase = medium_risk, none = low_risk."""
    text = prepare(text)
    hits = sum(1 for pattern in SENSATIONAL_PATTERNS if re.search(pattern, text, re.DOTALL))
    if hits >= 2:
        return "high_risk"
    if hits == 1:
        return "medium_risk"
    return "low_risk"


def add_misinfo_flags(df):
    """Add the rule_flag column."""
    if "raw_text" not in df.columns:  # safety net if an older Module 2 was used
        df["raw_text"] = df["title"].fillna("") + " " + df["text"].fillna("")
    df["rule_flag"] = df["raw_text"].apply(rule_based_flag)
    return df


if __name__ == "__main__":
    df = pd.read_csv("sentiment_posts.csv")
    df = add_misinfo_flags(df)
    df.to_csv("flagged_posts.csv", index=False)

    print(f"Flagged {len(df)} posts -> saved to flagged_posts.csv")
    print(df["rule_flag"].value_counts().to_string())
