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
import time
import signal
from contextlib import contextmanager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions import update_knowledge_base
from dotenv import load_dotenv
import logging
import traceback


class TimeoutException(Exception):
    pass


@contextmanager
def timeout(seconds):
    """Context manager for timeout handling."""
    def signal_handler(signum, frame):
        raise TimeoutException(f"Operation timed out after {seconds} seconds")
    
    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def main():
    """Main function with comprehensive error handling and timeouts."""
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    start_time = time.time()
    
    try:
        logging.info("🕒 Starting daily knowledge base update.")
        
        # Set a timeout for the entire operation (30 minutes)
        with timeout(1800):  # 30 minutes timeout
            update_knowledge_base()
        
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"✅ Daily update completed successfully in {duration:.2f} seconds.")
        
    except TimeoutException as e:
        logging.error(f"❌ Operation timed out: {e}")
        logging.error("The script took too long to complete. Check for:")
        logging.error("  - Network connectivity issues")
        logging.error("  - API rate limits")
        logging.error("  - Database connection problems")
        sys.exit(1)
        
    except KeyboardInterrupt:
        logging.warning("⚠️ Script interrupted by user.")
        sys.exit(0)
        
    except Exception as e:
        logging.error("❌ Error during daily update.")
        logging.error(traceback.format_exc())
        logging.error("Check the following:")
        logging.error("  - API keys are set correctly in .env")
        logging.error("  - Neo4j database is running")
        logging.error("  - Network connectivity")
        sys.exit(1)


if __name__ == "__main__":
    main()
