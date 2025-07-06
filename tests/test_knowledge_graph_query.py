import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from storage.knowledge_graph_query import KnowledgeGraphQuery


class TestKnowledgeGraphQuery(unittest.TestCase):
    """Test cases for the KnowledgeGraphQuery class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the KnowledgeGraph
        self.mock_kg = Mock()
        
        with patch('storage.knowledge_graph_query.KnowledgeGraph') as mock_kg_class:
            mock_kg_class.return_value = self.mock_kg
            self.kg_query = KnowledgeGraphQuery()

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'kg_query'):
            self.kg_query.close()

    def test_initialization(self):
        """Test knowledge graph query initialization."""
        self.assertIsNotNone(self.kg_query)
        self.assertIsNotNone(self.kg_query.kg)
        self.assertIsNotNone(self.kg_query.llm_client)

    def test_classify_query_entity_search(self):
        """Test query classification for entity search."""
        with patch.object(self.kg_query.llm_client, 'summarize', return_value="entity_search"):
            query_type = self.kg_query._classify_query("Tell me about HubSpot")
            self.assertEqual(query_type, "entity_search")

    def test_classify_query_topic_search(self):
        """Test query classification for topic search."""
        with patch.object(self.kg_query.llm_client, 'summarize', return_value="topic_search"):
            query_type = self.kg_query._classify_query("What are SEO trends?")
            self.assertEqual(query_type, "topic_search")

    def test_classify_query_fallback(self):
        """Test query classification fallback."""
        with patch.object(self.kg_query.llm_client, 'summarize', side_effect=Exception("Error")):
            query_type = self.kg_query._classify_query("Random query")
            self.assertEqual(query_type, "general_search")

    def test_extract_entity_name(self):
        """Test entity name extraction."""
        # Test with known entity
        entity = self.kg_query._extract_entity_name("Tell me about Google Analytics")
        self.assertEqual(entity, "Google")
        
        # Test with unknown entity
        entity = self.kg_query._extract_entity_name("Tell me about some random company")
        self.assertIsNone(entity)

    def test_extract_entities_from_query(self):
        """Test multiple entity extraction."""
        entities = self.kg_query._extract_entities_from_query("Compare Google and Facebook")
        self.assertIn("Google", entities)
        self.assertIn("Facebook", entities)
        
        # Test with no entities
        entities = self.kg_query._extract_entities_from_query("Tell me about marketing")
        self.assertEqual(len(entities), 0)

    def test_handle_entity_search_with_entity(self):
        """Test entity search handling with found entity."""
        # Mock entity network
        mock_network = {
            "entity": "HubSpot",
            "nodes": [{"name": "CRM", "type": "CONCEPT"}],
            "relationships": []
        }
        
        # Mock articles
        mock_articles = [
            {
                "title": "HubSpot CRM Review",
                "link": "https://example.com",
                "summary": "Comprehensive review of HubSpot CRM",
                "published": "2024-01-15",
                "topics": ["CRM"],
                "source": "Marketing Blog",
                "entities": ["HubSpot", "CRM"]
            }
        ]
        
        self.mock_kg.get_entity_network.return_value = mock_network
        self.mock_kg.query_knowledge_graph.return_value = mock_articles
        
        # Mock summary generation
        with patch.object(self.kg_query, '_generate_entity_summary', return_value="HubSpot is a leading CRM platform"):
            result = self.kg_query._handle_entity_search("Tell me about HubSpot")
            
            self.assertEqual(result['query_type'], 'entity_search')
            self.assertEqual(result['entity'], 'HubSpot')
            self.assertEqual(result['summary'], 'HubSpot is a leading CRM platform')
            self.assertEqual(result['articles'], mock_articles)
            self.assertEqual(result['network'], mock_network)

    def test_handle_entity_search_without_entity(self):
        """Test entity search handling without found entity."""
        # Mock general search
        with patch.object(self.kg_query, '_handle_general_search') as mock_general:
            mock_general.return_value = {"query_type": "general_search"}
            
            result = self.kg_query._handle_entity_search("Tell me about something random")
            
            self.assertEqual(result['query_type'], 'general_search')

    def test_handle_topic_search(self):
        """Test topic search handling."""
        # Mock articles
        mock_articles = [
            {
                "title": "SEO Best Practices",
                "link": "https://example.com",
                "summary": "Latest SEO strategies",
                "published": "2024-01-15",
                "topics": ["SEO"],
                "source": "Marketing Blog",
                "entities": ["Google", "SEO"]
            }
        ]
        
        # Mock trending topics
        mock_trending = [
            {"topic": "SEO", "frequency": 10},
            {"topic": "Content Marketing", "frequency": 8}
        ]
        
        self.mock_kg.query_knowledge_graph.return_value = mock_articles
        self.mock_kg.get_trending_topics.return_value = mock_trending
        
        # Mock summary generation
        with patch.object(self.kg_query, '_generate_topic_summary', return_value="SEO is important for marketing"):
            result = self.kg_query._handle_topic_search("What are SEO trends?")
            
            self.assertEqual(result['query_type'], 'topic_search')
            self.assertEqual(result['topic'], 'What are SEO trends?')
            self.assertEqual(result['summary'], 'SEO is important for marketing')
            self.assertEqual(result['articles'], mock_articles)
            self.assertEqual(result['trending_topics'], mock_trending)

    def test_handle_trending_search(self):
        """Test trending search handling."""
        # Mock trending topics
        mock_trending = [
            {"topic": "AI Marketing", "frequency": 15},
            {"topic": "Video Content", "frequency": 12}
        ]
        
        # Mock recent articles
        mock_articles = [
            {
                "title": "AI in Marketing",
                "link": "https://example.com",
                "summary": "How AI is changing marketing",
                "published": "2024-01-15",
                "topics": ["AI", "Marketing"],
                "source": "Marketing Blog",
                "entities": ["AI", "Marketing"]
            }
        ]
        
        self.mock_kg.get_trending_topics.return_value = mock_trending
        self.mock_kg.query_knowledge_graph.return_value = mock_articles
        
        # Mock summary generation
        with patch.object(self.kg_query, '_generate_trending_summary', return_value="AI and video content are trending"):
            result = self.kg_query._handle_trending_search("What's trending?")
            
            self.assertEqual(result['query_type'], 'trending')
            self.assertEqual(result['summary'], 'AI and video content are trending')
            self.assertEqual(result['trending_topics'], mock_trending)
            self.assertEqual(result['recent_articles'], mock_articles)

    def test_handle_relationship_search_with_entities(self):
        """Test relationship search handling with multiple entities."""
        # Mock articles
        mock_articles = [
            {
                "title": "Google vs Facebook",
                "link": "https://example.com",
                "summary": "Comparison of advertising platforms",
                "published": "2024-01-15",
                "topics": ["Advertising"],
                "source": "Marketing Blog",
                "entities": ["Google", "Facebook"]
            }
        ]
        
        # Mock networks
        mock_networks = {
            "Google": {"nodes": [{"name": "Advertising", "type": "CONCEPT"}]},
            "Facebook": {"nodes": [{"name": "Social Media", "type": "CONCEPT"}]}
        }
        
        self.mock_kg.query_knowledge_graph.return_value = mock_articles
        self.mock_kg.get_entity_network.side_effect = lambda entity, depth: mock_networks.get(entity, {"nodes": []})
        
        # Mock summary generation
        with patch.object(self.kg_query, '_generate_relationship_summary', return_value="Google and Facebook compete in advertising"):
            result = self.kg_query._handle_relationship_search("How do Google and Facebook compete?")
            
            self.assertEqual(result['query_type'], 'relationship_search')
            self.assertIn('Google', result['entities'])
            self.assertIn('Facebook', result['entities'])
            self.assertEqual(result['summary'], 'Google and Facebook compete in advertising')
            self.assertEqual(result['articles'], mock_articles)
            self.assertEqual(result['networks'], mock_networks)

    def test_handle_relationship_search_without_entities(self):
        """Test relationship search handling without multiple entities."""
        with patch.object(self.kg_query, '_handle_general_search') as mock_general:
            mock_general.return_value = {"query_type": "general_search"}
            
            result = self.kg_query._handle_relationship_search("Tell me about marketing")
            
            self.assertEqual(result['query_type'], 'general_search')

    def test_handle_general_search(self):
        """Test general search handling."""
        # Mock articles
        mock_articles = [
            {
                "title": "Marketing Best Practices",
                "link": "https://example.com",
                "summary": "General marketing advice",
                "published": "2024-01-15",
                "topics": ["Marketing"],
                "source": "Marketing Blog",
                "entities": ["Marketing"]
            }
        ]
        
        # Mock stats
        mock_stats = {
            "nodes": {"Article": 100, "Entity": 50},
            "relationships": {"MENTIONS": 200},
            "articles_by_source": [{"source": "HubSpot", "count": 30}]
        }
        
        self.mock_kg.query_knowledge_graph.return_value = mock_articles
        self.mock_kg.get_knowledge_graph_stats.return_value = mock_stats
        
        # Mock summary generation
        with patch.object(self.kg_query, '_generate_general_summary', return_value="Marketing is important"):
            result = self.kg_query._handle_general_search("What is marketing?")
            
            self.assertEqual(result['query_type'], 'general_search')
            self.assertEqual(result['summary'], 'Marketing is important')
            self.assertEqual(result['articles'], mock_articles)
            self.assertEqual(result['stats'], mock_stats)

    def test_generate_entity_summary(self):
        """Test entity summary generation."""
        articles = [
            {
                "title": "HubSpot CRM Review",
                "link": "https://example.com",
                "summary": "Comprehensive review of HubSpot CRM",
                "published": "2024-01-15",
                "topics": ["CRM"],
                "source": "Marketing Blog",
                "entities": ["HubSpot", "CRM"]
            }
        ]
        
        network = {
            "nodes": [{"name": "CRM", "type": "CONCEPT"}]
        }
        
        with patch.object(self.kg_query.llm_client, 'summarize', return_value="HubSpot is a leading CRM platform"):
            summary = self.kg_query._generate_entity_summary("HubSpot", articles, network)
            self.assertEqual(summary, "HubSpot is a leading CRM platform")

    def test_generate_entity_summary_no_articles(self):
        """Test entity summary generation with no articles."""
        summary = self.kg_query._generate_entity_summary("Unknown", [], {})
        self.assertIn("No information found", summary)

    def test_generate_topic_summary(self):
        """Test topic summary generation."""
        articles = [
            {
                "title": "SEO Best Practices",
                "link": "https://example.com",
                "summary": "Latest SEO strategies",
                "published": "2024-01-15",
                "topics": ["SEO"],
                "source": "Marketing Blog",
                "entities": ["Google", "SEO"]
            }
        ]
        
        trending = [{"topic": "SEO", "frequency": 10}]
        
        with patch.object(self.kg_query.llm_client, 'summarize', return_value="SEO is important for marketing"):
            summary = self.kg_query._generate_topic_summary("SEO", articles, trending)
            self.assertEqual(summary, "SEO is important for marketing")

    def test_generate_trending_summary(self):
        """Test trending summary generation."""
        trending = [
            {"topic": "AI Marketing", "frequency": 15},
            {"topic": "Video Content", "frequency": 12}
        ]
        
        articles = [
            {
                "title": "AI in Marketing",
                "link": "https://example.com",
                "summary": "How AI is changing marketing",
                "published": "2024-01-15",
                "topics": ["AI", "Marketing"],
                "source": "Marketing Blog",
                "entities": ["AI", "Marketing"]
            }
        ]
        
        with patch.object(self.kg_query.llm_client, 'summarize', return_value="AI and video content are trending"):
            summary = self.kg_query._generate_trending_summary(trending, articles)
            self.assertEqual(summary, "AI and video content are trending")

    def test_generate_relationship_summary(self):
        """Test relationship summary generation."""
        entities = ["Google", "Facebook"]
        articles = [
            {
                "title": "Google vs Facebook",
                "link": "https://example.com",
                "summary": "Comparison of advertising platforms",
                "published": "2024-01-15",
                "topics": ["Advertising"],
                "source": "Marketing Blog",
                "entities": ["Google", "Facebook"]
            }
        ]
        
        networks = {
            "Google": {"nodes": [{"name": "Advertising", "type": "CONCEPT"}]},
            "Facebook": {"nodes": [{"name": "Social Media", "type": "CONCEPT"}]}
        }
        
        with patch.object(self.kg_query.llm_client, 'summarize', return_value="Google and Facebook compete in advertising"):
            summary = self.kg_query._generate_relationship_summary(entities, articles, networks)
            self.assertEqual(summary, "Google and Facebook compete in advertising")

    def test_generate_general_summary(self):
        """Test general summary generation."""
        articles = [
            {
                "title": "Marketing Best Practices",
                "link": "https://example.com",
                "summary": "General marketing advice",
                "published": "2024-01-15",
                "topics": ["Marketing"],
                "source": "Marketing Blog",
                "entities": ["Marketing"]
            }
        ]
        
        with patch.object(self.kg_query.llm_client, 'summarize', return_value="Marketing is important"):
            summary = self.kg_query._generate_general_summary("What is marketing?", articles)
            self.assertEqual(summary, "Marketing is important")

    def test_natural_language_query_entity_search(self):
        """Test natural language query with entity search."""
        with patch.object(self.kg_query, '_classify_query', return_value="entity_search"):
            with patch.object(self.kg_query, '_handle_entity_search') as mock_entity:
                mock_entity.return_value = {"query_type": "entity_search", "entity": "HubSpot"}
                
                result = self.kg_query.natural_language_query("Tell me about HubSpot")
                
                self.assertEqual(result['query_type'], 'entity_search')
                self.assertEqual(result['entity'], 'HubSpot')

    def test_natural_language_query_topic_search(self):
        """Test natural language query with topic search."""
        with patch.object(self.kg_query, '_classify_query', return_value="topic_search"):
            with patch.object(self.kg_query, '_handle_topic_search') as mock_topic:
                mock_topic.return_value = {"query_type": "topic_search", "topic": "SEO"}
                
                result = self.kg_query.natural_language_query("What are SEO trends?")
                
                self.assertEqual(result['query_type'], 'topic_search')
                self.assertEqual(result['topic'], 'SEO')

    def test_get_knowledge_graph_insights(self):
        """Test getting knowledge graph insights."""
        # Mock stats
        mock_stats = {
            "nodes": {"Article": 100, "Entity": 50},
            "relationships": {"MENTIONS": 200},
            "articles_by_source": [{"source": "HubSpot", "count": 30}]
        }
        
        # Mock trending topics
        mock_trending = [
            {"topic": "AI Marketing", "frequency": 15},
            {"topic": "Video Content", "frequency": 12}
        ]
        
        self.mock_kg.get_knowledge_graph_stats.return_value = mock_stats
        self.mock_kg.get_trending_topics.return_value = mock_trending
        
        insights = self.kg_query.get_knowledge_graph_insights()
        
        self.assertIn('statistics', insights)
        self.assertIn('trending_topics', insights)
        self.assertEqual(insights['total_articles'], 100)
        self.assertEqual(insights['total_entities'], 50)
        self.assertEqual(insights['total_sources'], 0)  # Not in mock stats


if __name__ == '__main__':
    unittest.main() 