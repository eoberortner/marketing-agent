import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime
from storage.knowledge_graph import KnowledgeGraph


class TestKnowledgeGraph(unittest.TestCase):
    """Test cases for the KnowledgeGraph class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the Neo4j driver
        self.mock_driver = Mock()
        self.mock_session = Mock()
        self.mock_driver.session.return_value.__enter__.return_value = self.mock_session
        
        with patch('storage.knowledge_graph.GraphDatabase.driver') as mock_driver_class:
            mock_driver_class.return_value = self.mock_driver
            self.kg = KnowledgeGraph()

    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'kg'):
            self.kg.close()

    def test_initialization(self):
        """Test knowledge graph initialization."""
        self.assertIsNotNone(self.kg)
        self.assertIsNotNone(self.kg.driver)
        self.assertIsNotNone(self.kg.llm_client)

    def test_initialize_schema(self):
        """Test schema initialization."""
        # Verify that schema initialization calls are made
        self.mock_session.run.assert_called()
        calls = self.mock_session.run.call_args_list
        
        # Check that constraint creation calls were made
        constraint_calls = [call for call in calls if 'CREATE CONSTRAINT' in str(call)]
        self.assertGreater(len(constraint_calls), 0)

    def test_basic_entity_extraction(self):
        """Test basic entity extraction without LLM."""
        article = {
            "title": "Google Analytics 4: Complete Guide for 2024",
            "summary": "Learn how to use Google Analytics 4 for better marketing insights. HubSpot integration tips included.",
            "summary_processed": "Google Analytics 4 provides advanced marketing analytics. Works well with HubSpot."
        }
        
        result = self.kg._basic_entity_extraction(article)
        
        self.assertIn('entities', result)
        self.assertIn('relationships', result)
        self.assertIn('topics', result)
        self.assertIn('insights', result)
        self.assertIn('trends', result)
        
        # Check that Google and HubSpot were extracted
        entity_names = [entity['name'] for entity in result['entities']]
        self.assertIn('Google', entity_names)
        self.assertIn('HubSpot', entity_names)

    def test_extract_entities_and_relationships_with_llm_success(self):
        """Test entity extraction with successful LLM response."""
        article = {
            "title": "HubSpot vs Salesforce: Which CRM is Better?",
            "summary_processed": "Comparison of HubSpot and Salesforce CRM platforms for marketing teams."
        }
        
        mock_response = '''
        {
            "entities": [
                {"name": "HubSpot", "type": "COMPANY"},
                {"name": "Salesforce", "type": "COMPANY"},
                {"name": "CRM", "type": "CONCEPT"}
            ],
            "relationships": [
                {"from": "HubSpot", "to": "Salesforce", "relationship": "COMPETES_WITH", "description": "Competing CRM platforms"}
            ],
            "topics": ["CRM", "marketing automation"],
            "insights": ["HubSpot is more marketing-focused"],
            "trends": ["Cloud-based CRM adoption"]
        }
        '''
        
        with patch.object(self.kg.llm_client, 'summarize', return_value=mock_response):
            result = self.kg.extract_entities_and_relationships(article)
            
            self.assertIn('entities', result)
            self.assertIn('relationships', result)
            self.assertIn('topics', result)
            self.assertIn('insights', result)
            self.assertIn('trends', result)
            
            # Check extracted entities
            entity_names = [entity['name'] for entity in result['entities']]
            self.assertIn('HubSpot', entity_names)
            self.assertIn('Salesforce', entity_names)

    def test_extract_entities_and_relationships_with_llm_failure(self):
        """Test entity extraction when LLM fails."""
        article = {
            "title": "Email Marketing Best Practices",
            "summary_processed": "Learn email marketing strategies with Mailchimp and HubSpot."
        }
        
        with patch.object(self.kg.llm_client, 'summarize', side_effect=Exception("LLM Error")):
            result = self.kg.extract_entities_and_relationships(article)
            
            # Should fall back to basic extraction
            self.assertIn('entities', result)
            self.assertIn('relationships', result)
            self.assertIn('topics', result)

    def test_store_article_with_knowledge_graph(self):
        """Test storing an article in the knowledge graph."""
        article = {
            "title": "SEO Trends 2024",
            "link": "https://example.com/seo-trends",
            "summary_processed": "Latest SEO trends including Google updates and content marketing.",
            "published": "2024-01-15T10:00:00",
            "source": "Marketing Blog"
        }
        
        # Mock the entity extraction
        extracted_data = {
            "entities": [
                {"name": "Google", "type": "COMPANY"},
                {"name": "SEO", "type": "TOPIC"}
            ],
            "relationships": [],
            "topics": ["SEO", "content marketing"],
            "insights": ["Mobile-first indexing is important"],
            "trends": ["Voice search optimization"]
        }
        
        with patch.object(self.kg, 'extract_entities_and_relationships', return_value=extracted_data):
            self.kg.store_article_with_knowledge_graph(article)
            
            # Verify that Neo4j operations were called
            self.mock_session.run.assert_called()

    def test_query_knowledge_graph(self):
        """Test querying the knowledge graph."""
        mock_result = Mock()
        mock_result.__iter__ = lambda self: iter([
            {
                'title': 'Test Article',
                'link': 'https://example.com',
                'summary': 'Test summary',
                'published': '2024-01-15',
                'topics': ['SEO'],
                'source': 'Test Source',
                'entities': ['Google', 'SEO']
            }
        ])
        
        self.mock_session.run.return_value = mock_result
        
        results = self.kg.query_knowledge_graph("SEO trends", limit=5)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test Article')

    def test_get_entity_network(self):
        """Test getting entity network."""
        mock_result = Mock()
        mock_path = Mock()
        mock_path.nodes = [Mock(labels=['Entity'], get=lambda key, default: 'Google' if key == 'name' else default)]
        mock_path.relationships = []
        mock_result.__iter__ = lambda self: iter([{'path': mock_path}])
        
        self.mock_session.run.return_value = mock_result
        
        network = self.kg.get_entity_network("Google", depth=2)
        
        self.assertIn('entity', network)
        self.assertIn('nodes', network)
        self.assertIn('relationships', network)
        self.assertEqual(network['entity'], 'Google')

    def test_get_trending_topics(self):
        """Test getting trending topics."""
        mock_result = Mock()
        mock_result.__iter__ = lambda self: iter([
            {'topic': 'SEO', 'frequency': 10},
            {'topic': 'Content Marketing', 'frequency': 8}
        ])
        
        self.mock_session.run.return_value = mock_result
        
        trending = self.kg.get_trending_topics(days=30)
        
        self.assertIsInstance(trending, list)
        self.assertEqual(len(trending), 2)
        self.assertEqual(trending[0]['topic'], 'SEO')
        self.assertEqual(trending[0]['frequency'], 10)

    def test_get_related_articles(self):
        """Test getting related articles."""
        mock_result = Mock()
        mock_result.__iter__ = lambda self: iter([
            {
                'title': 'Related Article',
                'link': 'https://example.com/related',
                'summary': 'Related content',
                'shared_entities': 3
            }
        ])
        
        self.mock_session.run.return_value = mock_result
        
        related = self.kg.get_related_articles("Test Article", limit=5)
        
        self.assertIsInstance(related, list)
        self.assertEqual(len(related), 1)
        self.assertEqual(related[0]['title'], 'Related Article')

    def test_get_knowledge_graph_stats(self):
        """Test getting knowledge graph statistics."""
        # Mock node count results
        node_result = Mock()
        node_result.__iter__ = lambda self: iter([
            {'type': 'Article', 'count': 100},
            {'type': 'Entity', 'count': 50}
        ])
        
        # Mock relationship count results
        rel_result = Mock()
        rel_result.__iter__ = lambda self: iter([
            {'type': 'MENTIONS', 'count': 200},
            {'type': 'PUBLISHES', 'count': 100}
        ])
        
        # Mock source count results
        source_result = Mock()
        source_result.__iter__ = lambda self: iter([
            {'source': 'HubSpot', 'count': 30},
            {'source': 'Moz', 'count': 20}
        ])
        
        # Set up mock to return different results for different calls
        self.mock_session.run.side_effect = [node_result, rel_result, source_result]
        
        stats = self.kg.get_knowledge_graph_stats()
        
        self.assertIn('nodes', stats)
        self.assertIn('relationships', stats)
        self.assertIn('articles_by_source', stats)
        
        self.assertEqual(stats['nodes']['Article'], 100)
        self.assertEqual(stats['nodes']['Entity'], 50)


if __name__ == '__main__':
    unittest.main() 