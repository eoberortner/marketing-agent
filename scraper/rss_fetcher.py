import feedparser
from datetime import datetime
from typing import List, Dict

# took these RSS feed URLs from
# https://rss.feedspot.com/marketing_rss_feeds/
RSS_FEEDS = [
    "https://blog.hubspot.com/marketing/rss.xml",
    "https://www.marketingprofs.com/rss/rss.asp?i=1",
    "https://moz.com/blog/rss",
    "https://socialmediaexaminer.com/feed",
    "https://unbounce.com/feed/",
]
KEYWORDS = ["marketing", "seo", "content", "strategy", "branding"]



class RSSFetcher:
    def __init__(self, feeds: List[str] = RSS_FEEDS, keywords: List[str] = KEYWORDS):
        self.feeds = feeds
        self.keywords = [kw.lower() for kw in (keywords or [])]

    def fetch(self) -> List[Dict]:
        entries = []
        for feed_url in self.feeds:
            print(f"Fetching from: {feed_url}")
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if self._is_relevant(entry):
                    entries.append(self._parse_entry(entry))
        return entries

    def _is_relevant(self, entry) -> bool:
        if not self.keywords:
            return True
        content = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        return any(kw in content for kw in self.keywords)

    def _parse_entry(self, entry) -> Dict:
        return {
            "title": entry.get("title", "No Title"),
            "link": entry.get("link", ""),
            "published": self._parse_date(entry.get("published", "")),
            "summary": entry.get("summary", ""),
            "source": entry.get("source", {}).get("title", "Unknown Source")
        }

    def _parse_date(self, date_str: str) -> str:
        try:
            return datetime(*entry.published_parsed[:6]).isoformat()
        except Exception:
            return ""


# Example usage
# if __name__ == "__main__":
#     rss_feeds = [
#         "https://blog.hubspot.com/marketing/rss.xml",
#         "https://www.marketingprofs.com/rss/rss.asp?i=1",
#         "https://moz.com/blog/rss"
#     ]
#
#     keywords = ["marketing", "seo", "content", "strategy"]
#
#     fetcher = RSSFetcher(rss_feeds, keywords)
#     articles = fetcher.fetch()
#
#     for article in articles:
#         print(f"\n📰 {article['title']}\n🔗 {article['link']}\n📅 {article['published']}")
