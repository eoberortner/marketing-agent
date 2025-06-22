from neo4j import GraphDatabase


class GraphStorage:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="RqM933mqEFs7ApypkJ"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

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
                    "published": article["published"]
                },
            )
            print(f"🌐 Added to graph: {article['title']}")
