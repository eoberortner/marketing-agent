from scraper.rss_fetcher import RSSFetcher
from processor.summarizer import Summarizer
from storage.graph_interface import GraphStorage
from storage.db_interface import MongoStorage
from datetime import datetime

from dotenv import load_dotenv

def main():
    print(f"🚀 Starting Marketing Agent - {datetime.now().isoformat()}")

    fetcher = RSSFetcher()
    articles = fetcher.fetch()
    print(f"✅ Fetched {len(articles)} relevant articles.")

    if not articles:
        print("⚠️ No relevant articles found. Exiting.")
        return

    summarizer = Summarizer()

    db = MongoStorage()
    graph = GraphStorage()

    for article in articles:
        article["summary_processed"] = summarizer.summarize(
            article["summary"] or article["title"]
        )
        # store in MongoDB
        db.save_article(article)

        # store in GraphDB (neo4j)
        graph.store_article(article)

    print(f"\n✅ Completed at {datetime.now().isoformat()}")


if __name__ == "__main__":
    load_dotenv()

    main()