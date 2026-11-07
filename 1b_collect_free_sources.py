"""
MODULE 1B: DATA COLLECTION WITHOUT REDDIT
No account, no API keys, no approval needed.

Reads public news / community RSS feeds and writes raw_posts.csv in the SAME
columns as the Reddit version (Module 1), so Modules 2-5 work without changes.
The feed name is stored in the 'subreddit' column.

Setup (run once in the terminal):
    python -m pip install pandas

Run:
    python 1b_collect_free_sources.py
"""
import hashlib
import html
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

import pandas as pd

# name (goes into the 'subreddit' column)  ->  feed address
FEEDS = {
    "bbc_world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "bbc_india": "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
    "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "guardian_world": "https://www.theguardian.com/world/rss",
    "npr_news": "https://feeds.npr.org/1001/rss.xml",
    "hacker_news": "https://news.ycombinator.com/rss",
}
MAX_PER_FEED = 50
OUTPUT_FILE = "raw_posts.csv"
COLUMNS = ["id", "title", "text", "score", "num_comments", "created_utc", "subreddit"]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NetraStudentProject/1.0)"}
ATOM = "{http://www.w3.org/2005/Atom}"


def strip_html(raw):
    """Remove HTML tags and symbols like &amp; from a piece of feed text."""
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def to_timestamp(date_text):
    """Turn a feed date (RSS or Atom style) into seconds since 1970."""
    if date_text:
        try:
            return parsedate_to_datetime(date_text).timestamp()
        except (TypeError, ValueError):
            pass
        try:
            return datetime.fromisoformat(date_text.strip().replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    return time.time()  # no usable date in the feed: use "now"


def parse_feed(xml_bytes, source, limit=MAX_PER_FEED):
    """Read RSS or Atom XML and return a list of posts (one dictionary each)."""
    root = ET.fromstring(xml_bytes)
    rows = []
    for element in root.iter():
        if element.tag == "item":  # RSS format
            title = element.findtext("title")
            link = element.findtext("link")
            body = element.findtext("description")
            guid = element.findtext("guid")
            date = element.findtext("pubDate")
        elif element.tag == ATOM + "entry":  # Atom format
            title = element.findtext(ATOM + "title")
            link_tag = element.find(ATOM + "link")
            link = link_tag.get("href") if link_tag is not None else None
            body = element.findtext(ATOM + "summary") or element.findtext(ATOM + "content")
            guid = element.findtext(ATOM + "id")
            date = element.findtext(ATOM + "updated") or element.findtext(ATOM + "published")
        else:
            continue

        title = strip_html(title)
        if not title:
            continue
        text = strip_html(body)
        if text.lower() == "comments":  # Hacker News puts only a 'Comments' link here
            text = ""

        key = (guid or link or title).strip()
        rows.append({
            "id": hashlib.md5(key.encode("utf-8")).hexdigest()[:10],
            "title": title,
            "text": text,
            "score": 0,
            "num_comments": 0,
            "created_utc": to_timestamp(date),
            "subreddit": source,
        })
        if len(rows) >= limit:
            break
    return rows


def download(url):
    """Download one feed (gives up after 20 seconds)."""
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def collect_posts():
    """Try every feed. A broken feed is skipped; the others still run."""
    all_rows = []
    for source, url in FEEDS.items():
        try:
            rows = parse_feed(download(url), source)
            print(f"  OK    {source}: {len(rows)} posts")
            all_rows.extend(rows)
        except Exception as error:
            print(f"  SKIP  {source}: {type(error).__name__}: {error}")
    return pd.DataFrame(all_rows, columns=COLUMNS)


if __name__ == "__main__":
    print("Collecting posts from free RSS feeds...")
    df = collect_posts()
    df = df.drop_duplicates(subset="id").reset_index(drop=True)

    if df.empty:
        print("\nNo posts were collected, so", OUTPUT_FILE, "was NOT changed.")
        print("Check your internet. Try a different network (for example your phone's hotspot) and run again.")
        sys.exit(1)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nCollected {len(df)} posts -> saved to {OUTPUT_FILE}")
