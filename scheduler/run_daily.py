"""
run_daily.py

Scheduled entry point for running the Marketing Intelligence Agent's daily update.
This script:
- Loads environment variables (e.g., API keys)
- Calls the agent pipeline to fetch, process, and store marketing insights

Intended to be executed once or twice daily via:
- cron
- APScheduler
- GitHub Actions
- Cloud scheduler

Usage:
    $ python run_daily.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions import update_knowledge_base
from dotenv import load_dotenv
import logging
import traceback

if __name__ == "__main__":
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    try:
        logging.info("🕒 Starting daily knowledge base update.")
        update_knowledge_base()
        logging.info("✅ Daily update completed successfully.")
    except Exception as e:
        logging.error("❌ Error during daily update.")
        logging.error(traceback.format_exc())
