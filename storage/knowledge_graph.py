import os
import re
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime
from neo4j import GraphDatabase
from connectors.llm import DeepSeekClient


class KnowledgeGraph:
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
        self.llm_client = DeepSeekClient()
        
        # Initialize the graph schema
        self._initialize_schema()

    def close(self):
        self.driver.close()

    def _initialize_schema(self):
        """Initialize the knowledge graph schema with constraints and indexes."""
        with self.driver.session() as session:
            # Create constraints and indexes for better performance
            session.run("CREATE CONSTRAINT article_id IF NOT EXISTS FOR (a:Article) REQUIRE a.id IS UNIQUE")
            session.run("CREATE CONSTRAINT source_name IF NOT EXISTS FOR (s:Source) REQUIRE s.name IS UNIQUE")
            session.run("CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE")
            session.run("CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
            session.run("CREATE INDEX article_title IF NOT EXISTS FOR (a:Article) ON (a.title)")
            session.run("CREATE INDEX article_published IF NOT EXISTS FOR (a:Article) ON (a.published)")

    def extract_entities_and_relationships(self, article: Dict) -> Dict:
        """
        Extract entities and relationships from an article using LLM.
        """
        text = f"Title: {article['title']}\nSummary: {article.get('summary_processed', article.get('summary', ''))}"
        
        prompt = f"""
        Analyze the following marketing article and extract:
        1. Key entities (companies, tools, platforms, concepts, people)
        2. Relationships between entities
        3. Topics and categories
        4. Key insights and trends
        
        Article:
        {text}
        
        Return the analysis in this JSON format:
        {{
            "entities": [
                {{"name": "entity_name", "type": "COMPANY|TOOL|PLATFORM|CONCEPT|PERSON|TOPIC"}}
            ],
            "relationships": [
                {{"from": "entity1", "to": "entity2", "relationship": "relationship_type", "description": "description"}}
            ],
            "topics": ["topic1", "topic2"],
            "insights": ["insight1", "insight2"],
            "trends": ["trend1", "trend2"]
        }}
        """
        
        try:
            response = self.llm_client.summarize(
                agent_description="You are an expert at analyzing marketing content and extracting structured information.",
                task_description=prompt
            )
            
            # Try to parse JSON from response
            import json
            # Extract JSON from the response (it might be wrapped in markdown)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback to basic extraction
                return self._basic_entity_extraction(article)
        except Exception as e:
            print(f"❌ Failed to extract entities with LLM: {e}")
            return self._basic_entity_extraction(article)

    def _basic_entity_extraction(self, article: Dict) -> Dict:
        """
        Basic entity extraction using keyword matching when LLM fails.
        """
        text = f"{article['title']} {article.get('summary_processed', article.get('summary', ''))}"
        
        # Common marketing entities
        entities = []
        relationships = []
        topics = []
        
        # Extract companies and tools
        company_patterns = [
            r'\b(Google|Facebook|Meta|Twitter|LinkedIn|Instagram|TikTok|YouTube|HubSpot|Mailchimp|Salesforce|Adobe|Microsoft|Apple|Amazon)\b',
            r'\b(WordPress|Shopify|WooCommerce|Squarespace|Wix|Canva|Figma|Slack|Zoom|Trello|Asana)\b'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({"name": match, "type": "COMPANY"})
        
        # Extract topics
        topic_keywords = [
            "SEO", "content marketing", "social media", "email marketing", "PPC", "analytics",
            "conversion", "lead generation", "branding", "customer experience", "automation"
        ]
        
        for topic in topic_keywords:
            if topic.lower() in text.lower():
                topics.append(topic)
                entities.append({"name": topic, "type": "TOPIC"})
        
        return {
            "entities": entities,
            "relationships": relationships,
            "topics": topics,
            "insights": [],
            "trends": []
        }

    def store_article_with_knowledge_graph(self, article: Dict):
        """
        Store an article and build its knowledge graph representation.
        """
        # Extract entities and relationships
        extracted_data = self.extract_entities_and_relationships(article)
        
        with self.driver.session() as session:
            # Create article node
            article_id = f"article_{hash(article['link'])}"
            
            session.run("""
                MERGE (article:Article {id: $article_id})
                SET article.title = $title,
                    article.link = $link,
                    article.summary = $summary,
                    article.published = $published,
                    article.topics = $topics,
                    article.insights = $insights,
                    article.trends = $trends
                """, {
                    "article_id": article_id,
                    "title": article["title"],
                    "link": article["link"],
                    "summary": article.get("summary_processed", article.get("summary", "")),
                    "published": article.get("published", ""),
                    "topics": extracted_data.get("topics", []),
                    "insights": extracted_data.get("insights", []),
                    "trends": extracted_data.get("trends", [])
                })
            
            # Create source node and relationship
            session.run("""
                MERGE (source:Source {name: $source})
                MERGE (source)-[:PUBLISHES]->(article)
                """, {
                    "source": article.get("source", "Unknown")
                })
            
            # Create entity nodes and relationships
            for entity in extracted_data.get("entities", []):
                try:
                    session.run("""
                        MERGE (entity:Entity {name: $name})
                        ON CREATE SET entity.type = $type
                        ON MATCH SET entity.type = CASE 
                            WHEN entity.type IS NULL THEN $type 
                            ELSE entity.type 
                        END
                        MERGE (article)-[:MENTIONS]->(entity)
                        """, {
                            "name": entity["name"],
                            "type": entity["type"]
                        })
                except Exception as e:
                    print(f"⚠️ Warning: Could not create entity {entity['name']}: {e}")
                    continue
            
            # Create relationship nodes
            for rel in extracted_data.get("relationships", []):
                try:
                    session.run("""
                        MERGE (from:Entity {name: $from_name})
                        MERGE (to:Entity {name: $to_name})
                        MERGE (from)-[r:RELATES_TO {type: $rel_type, description: $description}]->(to)
                        MERGE (article)-[:DESCRIBES_RELATIONSHIP]->(from)
                        MERGE (article)-[:DESCRIBES_RELATIONSHIP]->(to)
                        """, {
                            "from_name": rel["from"],
                            "to_name": rel["to"],
                            "rel_type": rel["relationship"],
                            "description": rel.get("description", "")
                        })
                except Exception as e:
                    print(f"⚠️ Warning: Could not create relationship {rel['from']} -> {rel['to']}: {e}")
                    continue
            
            print(f"🌐 Added to knowledge graph: {article['title']}")

    def query_knowledge_graph(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Query the knowledge graph for relevant information.
        """
        with self.driver.session() as session:
            # Search for articles, entities, and relationships
            result = session.run("""
                MATCH (article:Article)
                WHERE toLower(article.title) CONTAINS toLower($query)
                   OR toLower(article.summary) CONTAINS toLower($query)
                   OR any(topic IN article.topics WHERE toLower(topic) CONTAINS toLower($query))
                OPTIONAL MATCH (article)-[:MENTIONS]->(entity:Entity)
                OPTIONAL MATCH (source:Source)-[:PUBLISHES]->(article)
                RETURN article.title as title,
                       article.link as link,
                       article.summary as summary,
                       article.published as published,
                       article.topics as topics,
                       source.name as source,
                       collect(DISTINCT entity.name) as entities
                ORDER BY article.published DESC
                LIMIT $limit
                """, {"query": query, "limit": limit})
            
            return [dict(record) for record in result]

    def get_entity_network(self, entity_name: str, depth: int = 2) -> Dict:
        """
        Get the network of relationships around a specific entity.
        """
        with self.driver.session() as session:
            # Build the relationship pattern based on depth
            if depth == 1:
                rel_pattern = "*1"
            elif depth == 2:
                rel_pattern = "*1..2"
            elif depth == 3:
                rel_pattern = "*1..3"
            else:
                rel_pattern = "*1..5"  # Cap at 5 for performance
            
            query = f"""
                MATCH path = (start:Entity {{name: $entity_name}})-[{rel_pattern}]-(connected)
                WHERE connected:Entity OR connected:Article
                RETURN path
                LIMIT 100
                """
            
            result = session.run(query, {"entity_name": entity_name})
            
            # Process the path results
            nodes = set()
            relationships = set()
            
            for record in result:
                path = record["path"]
                for node in path.nodes:
                    nodes.add((node.labels[0], node.get("name", node.get("title", "Unknown"))))
                for rel in path.relationships:
                    relationships.add((rel.start_node.get("name", "Unknown"), 
                                   rel.end_node.get("name", "Unknown"), 
                                   rel.type))
            
            return {
                "entity": entity_name,
                "nodes": [{"type": node_type, "name": name} for node_type, name in nodes],
                "relationships": [{"from": f, "to": t, "type": r} for f, t, r in relationships]
            }

    def get_trending_topics(self, days: int = 30) -> List[Dict]:
        """
        Get trending topics based on recent articles.
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (article:Article)
                WHERE article.published >= datetime() - duration({days: $days})
                UNWIND article.topics as topic
                RETURN topic, count(*) as frequency
                ORDER BY frequency DESC
                LIMIT 20
                """, {"days": days})
            
            return [{"topic": record["topic"], "frequency": record["frequency"]} 
                   for record in result]

    def get_related_articles(self, article_title: str, limit: int = 5) -> List[Dict]:
        """
        Find articles related to a specific article based on shared entities and topics.
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (article:Article {title: $title})-[:MENTIONS]->(entity:Entity)
                MATCH (other:Article)-[:MENTIONS]->(entity)
                WHERE other.title <> $title
                WITH other, count(DISTINCT entity) as shared_entities
                ORDER BY shared_entities DESC
                LIMIT $limit
                RETURN other.title as title,
                       other.link as link,
                       other.summary as summary,
                       shared_entities
                """, {"title": article_title, "limit": limit})
            
            return [dict(record) for record in result]

    def get_knowledge_graph_stats(self) -> Dict:
        """
        Get statistics about the knowledge graph.
        """
        with self.driver.session() as session:
            stats = {}
            
            # Count nodes by type
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(*) as count
                """)
            stats["nodes"] = {record["type"]: record["count"] for record in result}
            
            # Count relationships by type
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(*) as count
                """)
            stats["relationships"] = {record["type"]: record["count"] for record in result}
            
            # Count articles by source
            result = session.run("""
                MATCH (source:Source)-[:PUBLISHES]->(article:Article)
                RETURN source.name as source, count(*) as count
                ORDER BY count DESC
                """)
            stats["articles_by_source"] = [{"source": record["source"], "count": record["count"]} 
                                         for record in result]
            
            return stats 