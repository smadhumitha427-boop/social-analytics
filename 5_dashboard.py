"""
MODULE 5: DASHBOARD (Streamlit)
Reads flagged_posts.csv (made by Module 4) and shows charts and a table
in your web browser.

Setup (run once in the terminal):
    python -m pip install streamlit plotly pandas

Run (from the project folder):
    python -m streamlit run 5_dashboard.py

If Streamlit asks for your email the first time, just press Enter.
Stop the dashboard with Ctrl+C in the terminal.
"""
import os

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Social Media Analytics - Netra", layout="wide")
st.title("Social Media Analytics Platform")
st.caption("SIH26152 | Team Netra")

if not os.path.exists("flagged_posts.csv"):
    st.error("flagged_posts.csv was not found. Run the pipeline first:  python run_pipeline.py --sample")
    st.stop()

df = pd.read_csv("flagged_posts.csv")
if df.empty:
    st.warning("flagged_posts.csv has no posts in it yet. Run the pipeline again.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Posts analysed", len(df))
col2.metric("Negative sentiment %", f"{(df['sentiment_label'] == 'negative').mean() * 100:.1f}%")
col3.metric("High-risk posts", int((df["rule_flag"] == "high_risk").sum()))

st.subheader("Sentiment distribution")
st.plotly_chart(px.pie(df, names="sentiment_label"))

st.subheader("Misinformation risk levels")
risk_counts = df["rule_flag"].value_counts().rename_axis("rule_flag").reset_index(name="count")
st.plotly_chart(px.bar(risk_counts, x="rule_flag", y="count"))

st.subheader("Flagged posts")
flagged = df[df["rule_flag"] != "low_risk"][["title", "sentiment_label", "rule_flag"]]
if flagged.empty:
    st.info("No medium or high risk posts in this batch.")
else:
    st.dataframe(flagged)
