from scraper.rss_fetcher import RSSFetcher
from processor.summarizer import Summarizer
from storage.graph_interface import GraphStorage
from storage.db_interface import MongoStorage
from datetime import datetime

from dotenv import load_dotenv

from storage.vector_store import VectorStore
from connectors.llm import DeepSeekClient


def update_knowledge_base():
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
    vs = VectorStore()

    i = 0
    processed_articles = list()
    for article in articles:
        article["summary_processed"] = summarizer.summarize(
            article["summary"] or article["title"]
        )
        processed_articles.append(article)

        # store in MongoDB
        db.save_article(article)

        # store in GraphDB (neo4j)
        graph.store_article(article)

    # store in Vector store
    vs.add_documents(processed_articles)

    print(f"\n✅ Completed at {datetime.now().isoformat()}")


def query_knowledge_base(query: str) -> str:

    vs = VectorStore()
    results = vs.search(query)

    # for r in results:
    #     print(f"\n📰 {r['title']}\n📝 {r['summary_processed']}\n🔗 {r['link']}")

    task_description = f"""
    TASK: Summarize the following information in a professionally sound manner.

    {results}
    """

    llm_client = DeepSeekClient()
    summary = llm_client.summarize(
        agent_description="You are a marketing expert.",
        task_description=task_description,
    )
    return summary


def main():

    update_knowledge_base()

    # query = "What are the latest key takeaways for strategies in email marketing?"
    # summary = query_knowledge_base(query)
    # print(summary)


if __name__ == "__main__":
    load_dotenv()

    main()
