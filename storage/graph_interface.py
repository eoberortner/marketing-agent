import os

from neo4j import GraphDatabase


class GraphStorage:
    def __init__(
        self,
        uri="bolt://localhost:7687",
        user: str = None,
        password: str = None,
    ):
        self.user = user
        if self.user is None:
            self.user = os.getenv("NEO4J_USERNAME")

        self.password = password
        if self.password is None:
            self.password = os.getenv("NEO4J_PASSWORD")

        self.driver = GraphDatabase.driver(
            uri, auth=(self.user, self.password)
        )

    def close(self):
        self.driver.close()

    def store_article(self, article):
        with self.driver.session() as session:
            session.run(
                """
                MERGE (source:Source {name: $source})
                MERGE (article:Article {title: $title, link: $link})
                SET article.summary = $summary, article.published = $published
                MERGE (source)-[:PUBLISHES]->(article)
                """,
                {
                    "source": article.get("source", "Unknown"),
                    "title": article["title"],
                    "link": article["link"],
                    "summary": article["summary_processed"],
                    "published": article["published"],
                },
            )
            print(f"🌐 Added to graph: {article['title']}")
