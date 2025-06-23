from pymongo import MongoClient
from datetime import datetime


class MongoStorage:
    def __init__(
        self, uri="mongodb://localhost:27017/", db_name="marketing_agent"
    ):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["summaries"]

    def save_article(self, article):
        # Use link as unique identifier to avoid duplicates
        if self.collection.find_one({"link": article["link"]}):
            print(f"🔁 Already stored: {article['title']}")
            return
        article["saved_at"] = datetime.utcnow().isoformat()
        self.collection.insert_one(article)
        print(f"💾 Stored: {article['title']}")
