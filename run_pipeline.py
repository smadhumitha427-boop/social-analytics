"""
RUN THE WHOLE BACKEND (steps 1 to 4) WITH ONE COMMAND

    python run_pipeline.py            collect fresh posts from the RSS feeds, then run steps 2 to 4
    python run_pipeline.py --sample   use sample_data/raw_posts_sample.csv instead (no internet needed)

Afterwards, see the results in your browser:

    python -m streamlit run 5_dashboard.py
"""
import os
import shutil
import subprocess
import sys

# Step 1. When Reddit approves your API access, change this to "1_data_collection.py".
COLLECTOR = "1b_collect_free_sources.py"

STEPS = [
    "2_text_preprocessing.py",
    "3_sentiment_analysis.py",
    "4_misinformation_flagging.py",
]
SAMPLE_FILE = os.path.join("sample_data", "raw_posts_sample.csv")


def run(script):
    """Run one step. Stop everything if it fails."""
    print(f"\n=== Running {script} ===")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"\nStopped: {script} failed (read the message above). Fix it, then run this again.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # always work inside the project folder

    if "--sample" in sys.argv:
        if not os.path.exists(SAMPLE_FILE):
            print(f"Could not find {SAMPLE_FILE}. Make sure the sample_data folder is in the project folder.")
            sys.exit(1)
        shutil.copyfile(SAMPLE_FILE, "raw_posts.csv")
        print(f"Using the sample data ({SAMPLE_FILE}), so no internet is needed for step 1.")
    else:
        run(COLLECTOR)

    for script in STEPS:
        run(script)

    print("\nBackend finished. Now run:  python -m streamlit run 5_dashboard.py")
