import asyncio
import aiohttp
import feedparser
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from tqdm import tqdm

# RSS feed URLs from the original fetcher
RSS_FEEDS = [
    "https://blog.hubspot.com/marketing/rss.xml",
    "https://www.marketingprofs.com/rss/rss.asp?i=1",
    "https://moz.com/blog/rss",
    "https://socialmediaexaminer.com/feed",
    "https://unbounce.com/feed/",
]

KEYWORDS = ["marketing", "seo", "content", "strategy", "branding"]


class ParallelRSSFetcher:
    """
    Parallel RSS fetcher that can fetch multiple feeds concurrently
    and process articles in parallel.
    """
    
    def __init__(
        self, 
        feeds: List[str] = RSS_FEEDS, 
        keywords: List[str] = KEYWORDS,
        max_workers: int = 5,
        timeout: int = 30
    ):
        self.feeds = feeds
        self.keywords = [kw.lower() for kw in (keywords or [])]
        self.max_workers = max_workers
        self.timeout = timeout

    async def fetch_feed_async(self, session: aiohttp.ClientSession, feed_url: str) -> List[Dict]:
        """
        Fetch a single RSS feed asynchronously.
        """
        try:
            async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    articles = []
                    for entry in feed.entries:
                        if self._is_relevant(entry):
                            article = self._parse_entry(entry, feed_url)
                            articles.append(article)
                    
                    print(f"✅ Fetched {len(articles)} articles from {feed_url}")
                    return articles
                else:
                    print(f"❌ Failed to fetch {feed_url}: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            print(f"❌ Error fetching {feed_url}: {e}")
            return []

    def fetch_all_feeds_async(self) -> List[Dict]:
        """
        Fetch all RSS feeds concurrently using asyncio.
        """
        async def fetch_all():
            async with aiohttp.ClientSession() as session:
                tasks = [self.fetch_feed_async(session, feed_url) for feed_url in self.feeds]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                all_articles = []
                for result in results:
                    if isinstance(result, list):
                        all_articles.extend(result)
                    else:
                        print(f"❌ Feed fetch failed: {result}")
                
                return all_articles
        
        return asyncio.run(fetch_all())

    def fetch_all_feeds_threaded(self) -> List[Dict]:
        """
        Fetch all RSS feeds using thread pool executor.
        """
        def fetch_single_feed(feed_url: str) -> List[Dict]:
            try:
                import requests
                response = requests.get(feed_url, timeout=self.timeout)
                if response.status_code == 200:
                    feed = feedparser.parse(response.text)
                    
                    articles = []
                    for entry in feed.entries:
                        if self._is_relevant(entry):
                            article = self._parse_entry(entry, feed_url)
                            articles.append(article)
                    
                    print(f"✅ Fetched {len(articles)} articles from {feed_url}")
                    return articles
                else:
                    print(f"❌ Failed to fetch {feed_url}: HTTP {response.status_code}")
                    return []
                    
            except Exception as e:
                print(f"❌ Error fetching {feed_url}: {e}")
                return []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(fetch_single_feed, feed_url): feed_url 
                           for feed_url in self.feeds}
            
            all_articles = []
            for future in tqdm(as_completed(future_to_url), total=len(self.feeds), 
                              desc="Fetching RSS feeds"):
                url = future_to_url[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                except Exception as e:
                    print(f"❌ Exception for {url}: {e}")
            
            return all_articles

    def _is_relevant(self, entry) -> bool:
        """Check if an entry is relevant based on keywords."""
        if not self.keywords:
            return True
        content = (
            f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        )
        return any(kw in content for kw in self.keywords)

    def _parse_entry(self, entry, feed_url: str) -> Dict:
        """Parse a feed entry into a standardized article format."""
        return {
            "title": entry.get("title", "No Title"),
            "link": entry.get("link", ""),
            "published": self._parse_date(entry.get("published", "")),
            "summary": entry.get("summary", ""),
            "source": entry.get("source", {}).get("title", "Unknown Source"),
            "feed_url": feed_url,
        }

    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format."""
        try:
            return datetime(*entry.published_parsed[:6]).isoformat()
        except Exception:
            return ""

    def fetch(self, use_async: bool = True) -> List[Dict]:
        """
        Fetch all RSS feeds using either async or threaded approach.
        
        Args:
            use_async (bool): Whether to use asyncio (True) or threading (False)
            
        Returns:
            List[Dict]: List of articles from all feeds
        """
        print(f"🚀 Starting parallel RSS fetch with {len(self.feeds)} feeds...")
        start_time = time.time()
        
        if use_async:
            articles = self.fetch_all_feeds_async()
        else:
            articles = self.fetch_all_feeds_threaded()
        
        end_time = time.time()
        print(f"✅ Fetched {len(articles)} total articles in {end_time - start_time:.2f} seconds")
        
        return articles


class ParallelArticleProcessor:
    """
    Process articles in parallel for summarization and storage.
    """
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers

    def process_article(self, article: Dict) -> Dict:
        """
        Process a single article (summarize and prepare for storage).
        """
        try:
            from processor.summarizer import Summarizer
            summarizer = Summarizer()
            
            # Create a copy to avoid modifying the original
            processed_article = article.copy()
            processed_article["summary_processed"] = summarizer.summarize(
                article["summary"] or article["title"]
            )
            
            return processed_article
            
        except Exception as e:
            print(f"❌ Error processing article '{article.get('title', 'Unknown')}': {e}")
            # Return original article if processing fails
            return article

    def process_articles_parallel(self, articles: List[Dict]) -> List[Dict]:
        """
        Process all articles in parallel.
        """
        print(f"🔄 Processing {len(articles)} articles in parallel...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            processed_articles = list(tqdm(
                executor.map(self.process_article, articles),
                total=len(articles),
                desc="Processing articles"
            ))
        
        end_time = time.time()
        print(f"✅ Processed {len(processed_articles)} articles in {end_time - start_time:.2f} seconds")
        
        return processed_articles


class ParallelStorageManager:
    """
    Store articles in parallel across different storage systems.
    """
    
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers

    def store_article_parallel(self, article: Dict) -> Dict:
        """
        Store a single article across all storage systems.
        """
        try:
            from storage.db_interface import MongoStorage
            from storage.graph_interface import GraphStorage
            from storage.knowledge_graph import KnowledgeGraph
            
            # Store in MongoDB
            db = MongoStorage()
            db.save_article(article)
            
            # Store in Neo4j (legacy)
            graph = GraphStorage()
            graph.store_article(article)
            
            # Store in Knowledge Graph
            kg = KnowledgeGraph()
            kg.store_article_with_knowledge_graph(article)
            kg.close()
            
            return {"status": "success", "article": article["title"]}
            
        except Exception as e:
            print(f"❌ Error storing article '{article.get('title', 'Unknown')}': {e}")
            return {"status": "error", "article": article.get("title", "Unknown"), "error": str(e)}

    def store_articles_parallel(self, articles: List[Dict]) -> List[Dict]:
        """
        Store all articles in parallel.
        """
        print(f"💾 Storing {len(articles)} articles in parallel...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(tqdm(
                executor.map(self.store_article_parallel, articles),
                total=len(articles),
                desc="Storing articles"
            ))
        
        end_time = time.time()
        print(f"✅ Stored {len(articles)} articles in {end_time - start_time:.2f} seconds")
        
        # Count successes and failures
        successes = [r for r in results if r["status"] == "success"]
        failures = [r for r in results if r["status"] == "error"]
        
        print(f"📊 Storage results: {len(successes)} successful, {len(failures)} failed")
        
        return results


def update_knowledge_base_parallel(
    max_fetch_workers: int = 5,
    max_process_workers: int = 3,
    max_storage_workers: int = 2,
    use_async_fetch: bool = True
):
    """
    Parallelized version of update_knowledge_base.
    
    Args:
        max_fetch_workers (int): Number of workers for RSS fetching
        max_process_workers (int): Number of workers for article processing
        max_storage_workers (int): Number of workers for storage operations
        use_async_fetch (bool): Whether to use async for RSS fetching
    """
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
    from storage.vector_store import VectorStore
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


if __name__ == "__main__":
    # Example usage
    update_knowledge_base_parallel() 