from scraper.rss_fetcher import RSSFetcher
from scraper.parallel_rss_fetcher import ParallelRSSFetcher, ParallelArticleProcessor, ParallelStorageManager
from processor.summarizer import Summarizer
from storage.graph_interface import GraphStorage
from storage.knowledge_graph import KnowledgeGraph
from storage.db_interface import MongoStorage
from datetime import datetime
from typing import Dict

from connectors.llm import DeepSeekClient
from storage.vector_store import VectorStore
import traceback


def update_knowledge_base():
    """
    Ingests and updates the agent's marketing knowledge base.

    This function:
    - Fetches new marketing-related articles from RSS feeds.
    - Summarizes the content using a local or LLM summarizer.
    - Persists the processed articles in:
        - MongoDB (raw and summarized data)
        - Neo4j (triplet-based graph knowledge)
        - FAISS vector store (OpenAI embeddings for semantic search)

    It should be scheduled to run daily or at regular intervals as part of a
    long-running knowledge agent.

    Side effects:
    - Writes to MongoDB, Neo4j, and vector index on disk.
    - Prints log-style status messages to stdout.

    Returns:
        None
    """
    import time
    start_time = time.time()
    
    print(f"🚀 Starting Marketing Agent - {datetime.now().isoformat()}")

    try:
        # Step 1: Fetch articles
        print("📡 Fetching articles from RSS feeds...")
        fetcher = RSSFetcher()
        articles = fetcher.fetch()
        print(f"✅ Fetched {len(articles)} relevant articles.")

        if not articles:
            print("⚠️ No relevant articles found. Exiting.")
            return

        # Step 2: Initialize components
        print("🔧 Initializing components...")
        summarizer = Summarizer()
        db = MongoStorage()
        graph = GraphStorage()
        kg = KnowledgeGraph()
        vs = VectorStore()

        # Step 3: Process articles
        print(f"🔄 Processing {len(articles)} articles...")
        processed_articles = []
        
        for i, article in enumerate(articles, 1):
            try:
                print(f"  📝 Processing article {i}/{len(articles)}: {article['title'][:50]}...")
                
                # Summarize article
                article["summary_processed"] = summarizer.summarize(
                    article["summary"] or article["title"]
                )
                processed_articles.append(article)

                # Store in MongoDB
                try:
                    db.save_article(article)
                except Exception as e:
                    print(f"⚠️ Warning: Failed to save to MongoDB: {e}")

                # Store in Neo4j (legacy)
                try:
                    graph.store_article(article)
                except Exception as e:
                    print(f"⚠️ Warning: Failed to save to Neo4j: {e}")

                # Store in Knowledge Graph
                try:
                    kg.store_article_with_knowledge_graph(article)
                except Exception as e:
                    print(f"⚠️ Warning: Failed to save to Knowledge Graph: {e}")

            except Exception as e:
                print(f"❌ Error processing article {i}: {e}")
                continue

        # Step 4: Store in Vector Store
        print("💾 Storing articles in vector store...")
        try:
            vs.add_documents(processed_articles)
        except Exception as e:
            print(f"⚠️ Warning: Failed to save to vector store: {e}")
        
        # Step 5: Cleanup
        try:
            kg.close()
        except Exception as e:
            print(f"⚠️ Warning: Failed to close knowledge graph: {e}")

        end_time = time.time()
        duration = end_time - start_time
        print(f"\n✅ Completed at {datetime.now().isoformat()}")
        print(f"⏱️ Total time: {duration:.2f} seconds")
        print(f"📊 Processed: {len(processed_articles)}/{len(articles)} articles successfully")

    except Exception as e:
        print(f"❌ Critical error in update_knowledge_base: {e}")
        print(traceback.format_exc())
        raise


def update_knowledge_base_parallel(
    max_fetch_workers: int = 5,
    max_process_workers: int = 3,
    max_storage_workers: int = 2,
    use_async_fetch: bool = True
):
    """
    Parallelized version of update_knowledge_base for improved performance.

    This function:
    - Fetches RSS feeds concurrently using async/threading
    - Processes articles in parallel (summarization)
    - Stores articles in parallel across different storage systems
    - Provides detailed performance metrics

    Args:
        max_fetch_workers (int): Number of workers for RSS fetching
        max_process_workers (int): Number of workers for article processing
        max_storage_workers (int): Number of workers for storage operations
        use_async_fetch (bool): Whether to use async for RSS fetching

    Returns:
        None
    """
    import time
    print(f"🚀 Starting Parallel Marketing Agent - {datetime.now().isoformat()}")
    start_time = time.time()
    
    # Step 1: Fetch articles in parallel
    fetcher = ParallelRSSFetcher(max_workers=max_fetch_workers)
    articles = fetcher.fetch(use_async=use_async_fetch)
    
    if not articles:
        print("⚠️ No relevant articles found. Exiting.")
        return
    
    # Step 2: Process articles in parallel
    processor = ParallelArticleProcessor(max_workers=max_process_workers)
    processed_articles = processor.process_articles_parallel(articles)
    
    # Step 3: Store articles in parallel
    storage_manager = ParallelStorageManager(max_workers=max_storage_workers)
    storage_results = storage_manager.store_articles_parallel(processed_articles)
    
    # Step 4: Store in Vector Store (this is already optimized)
    vs = VectorStore()
    vs.add_documents(processed_articles)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n✅ Parallel processing completed in {total_time:.2f} seconds")
    print(f"📊 Summary:")
    print(f"  - Fetched: {len(articles)} articles")
    print(f"  - Processed: {len(processed_articles)} articles")
    print(f"  - Stored: {len([r for r in storage_results if r['status'] == 'success'])} articles")
    print(f"  - Failed: {len([r for r in storage_results if r['status'] == 'error'])} articles")


def query_knowledge_base(query: str) -> str:
    """
    Queries the agent's knowledge base using a natural language question.

    This function:
    - Performs a semantic search over the vector store using the given query.
    - Retrieves the most relevant marketing article summaries.
    - Sends the result to an LLM client to generate a professional summary.

    Args:
        query (str): The user’s natural language question (e.g., "What are the latest SEO trends?").

    Returns:
        str: A synthesized and fluent answer generated by the LLM based on retrieved knowledge.
    """
    vs = VectorStore()
    results = vs.search(query)

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


def query_knowledge_graph(query: str) -> Dict:
    """
    Queries the knowledge graph using natural language and returns structured results.

    This function:
    - Analyzes the query type (entity search, topic search, trending, etc.)
    - Searches the knowledge graph for relevant information
    - Returns structured results with summaries, articles, and network data

    Args:
        query (str): The user's natural language question.

    Returns:
        Dict: Structured results including summary, articles, and network data.
    """
    from storage.knowledge_graph_query import KnowledgeGraphQuery
    
    kg_query = KnowledgeGraphQuery()
    try:
        results = kg_query.natural_language_query(query)
        return results
    finally:
        kg_query.close()


def get_knowledge_graph_insights() -> Dict:
    """
    Get insights and analytics from the knowledge graph.

    Returns:
        Dict: Statistics and insights about the knowledge graph.
    """
    from storage.knowledge_graph_query import KnowledgeGraphQuery
    
    kg_query = KnowledgeGraphQuery()
    try:
        insights = kg_query.get_knowledge_graph_insights()
        return insights
    finally:
        kg_query.close()
