import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime
from functions import query_knowledge_graph, get_knowledge_graph_insights, update_knowledge_base


class TestFunctionsIntegration(unittest.TestCase):
    """Integration tests for functions that use the knowledge graph."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def tearDown(self):
        """Clean up after tests."""
        pass

    @patch('functions.KnowledgeGraphQuery')
    def test_query_knowledge_graph_function(self, mock_kg_query_class):
        """Test the query_knowledge_graph function."""
        # Mock the KnowledgeGraphQuery
        mock_kg_query = Mock()
        mock_kg_query_class.return_value = mock_kg_query
        
        # Mock the query result
        expected_result = {
            "query_type": "entity_search",
            "entity": "HubSpot",
            "summary": "HubSpot is a leading CRM platform",
            "articles": [
                {
                    "title": "HubSpot CRM Review",
                    "link": "https://example.com",
                    "summary": "Comprehensive review of HubSpot CRM",
                    "published": "2024-01-15",
                    "topics": ["CRM"],
                    "source": "Marketing Blog",
                    "entities": ["HubSpot", "CRM"]
                }
            ],
            "network": {
                "entity": "HubSpot",
                "nodes": [{"name": "CRM", "type": "CONCEPT"}],
                "relationships": []
            }
        }
        mock_kg_query.natural_language_query.return_value = expected_result
        
        # Test the function
        result = query_knowledge_graph("Tell me about HubSpot")
        
        # Verify the result
        self.assertEqual(result, expected_result)
        
        # Verify that the query was called correctly
        mock_kg_query.natural_language_query.assert_called_once_with("Tell me about HubSpot")
        
        # Verify that close was called
        mock_kg_query.close.assert_called_once()

    @patch('functions.KnowledgeGraphQuery')
    def test_query_knowledge_graph_function_with_exception(self, mock_kg_query_class):
        """Test the query_knowledge_graph function with exception handling."""
        # Mock the KnowledgeGraphQuery to raise an exception
        mock_kg_query = Mock()
        mock_kg_query_class.return_value = mock_kg_query
        mock_kg_query.natural_language_query.side_effect = Exception("Database error")
        
        # Test that the function handles exceptions gracefully
        with self.assertRaises(Exception):
            query_knowledge_graph("Tell me about HubSpot")
        
        # Verify that close was still called
        mock_kg_query.close.assert_called_once()

    @patch('functions.KnowledgeGraphQuery')
    def test_get_knowledge_graph_insights_function(self, mock_kg_query_class):
        """Test the get_knowledge_graph_insights function."""
        # Mock the KnowledgeGraphQuery
        mock_kg_query = Mock()
        mock_kg_query_class.return_value = mock_kg_query
        
        # Mock the insights result
        expected_insights = {
            "statistics": {
                "nodes": {"Article": 100, "Entity": 50},
                "relationships": {"MENTIONS": 200},
                "articles_by_source": [{"source": "HubSpot", "count": 30}]
            },
            "trending_topics": [
                {"topic": "AI Marketing", "frequency": 15},
                {"topic": "Video Content", "frequency": 12}
            ],
            "total_articles": 100,
            "total_entities": 50,
            "total_sources": 0
        }
        mock_kg_query.get_knowledge_graph_insights.return_value = expected_insights
        
        # Test the function
        result = get_knowledge_graph_insights()
        
        # Verify the result
        self.assertEqual(result, expected_insights)
        
        # Verify that the insights were retrieved correctly
        mock_kg_query.get_knowledge_graph_insights.assert_called_once()
        
        # Verify that close was called
        mock_kg_query.close.assert_called_once()

    @patch('functions.KnowledgeGraphQuery')
    def test_get_knowledge_graph_insights_function_with_exception(self, mock_kg_query_class):
        """Test the get_knowledge_graph_insights function with exception handling."""
        # Mock the KnowledgeGraphQuery to raise an exception
        mock_kg_query = Mock()
        mock_kg_query_class.return_value = mock_kg_query
        mock_kg_query.get_knowledge_graph_insights.side_effect = Exception("Database error")
        
        # Test that the function handles exceptions gracefully
        with self.assertRaises(Exception):
            get_knowledge_graph_insights()
        
        # Verify that close was still called
        mock_kg_query.close.assert_called_once()

    @patch('functions.RSSFetcher')
    @patch('functions.Summarizer')
    @patch('functions.MongoStorage')
    @patch('functions.GraphStorage')
    @patch('functions.KnowledgeGraph')
    @patch('functions.VectorStore')
    def test_update_knowledge_base_with_knowledge_graph(self, mock_vector_store, mock_kg, mock_graph, mock_db, mock_summarizer, mock_fetcher):
        """Test that update_knowledge_base integrates the knowledge graph."""
        # Mock the RSS fetcher
        mock_fetcher_instance = Mock()
        mock_fetcher.return_value = mock_fetcher_instance
        mock_fetcher_instance.fetch.return_value = [
            {
                "title": "Test Article",
                "link": "https://example.com",
                "summary": "Test summary",
                "published": "2024-01-15T10:00:00",
                "source": "Test Source"
            }
        ]
        
        # Mock the summarizer
        mock_summarizer_instance = Mock()
        mock_summarizer.return_value = mock_summarizer_instance
        mock_summarizer_instance.summarize.return_value = "Processed summary"
        
        # Mock the database
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance
        
        # Mock the graph storage
        mock_graph_instance = Mock()
        mock_graph.return_value = mock_graph_instance
        
        # Mock the knowledge graph
        mock_kg_instance = Mock()
        mock_kg.return_value = mock_kg_instance
        
        # Mock the vector store
        mock_vector_store_instance = Mock()
        mock_vector_store.return_value = mock_vector_store_instance
        
        # Test the function
        update_knowledge_base()
        
        # Verify that all components were called
        mock_fetcher_instance.fetch.assert_called_once()
        mock_summarizer_instance.summarize.assert_called_once()
        mock_db_instance.save_article.assert_called_once()
        mock_graph_instance.store_article.assert_called_once()
        mock_kg_instance.store_article_with_knowledge_graph.assert_called_once()
        mock_vector_store_instance.add_documents.assert_called_once()
        mock_kg_instance.close.assert_called_once()

    @patch('functions.RSSFetcher')
    @patch('functions.Summarizer')
    @patch('functions.MongoStorage')
    @patch('functions.GraphStorage')
    @patch('functions.KnowledgeGraph')
    @patch('functions.VectorStore')
    def test_update_knowledge_base_no_articles(self, mock_vector_store, mock_kg, mock_graph, mock_db, mock_summarizer, mock_fetcher):
        """Test update_knowledge_base when no articles are found."""
        # Mock the RSS fetcher to return no articles
        mock_fetcher_instance = Mock()
        mock_fetcher.return_value = mock_fetcher_instance
        mock_fetcher_instance.fetch.return_value = []
        
        # Test the function
        update_knowledge_base()
        
        # Verify that no processing was done
        mock_fetcher_instance.fetch.assert_called_once()
        # Other components should not be called since there are no articles

    @patch('functions.RSSFetcher')
    @patch('functions.Summarizer')
    @patch('functions.MongoStorage')
    @patch('functions.GraphStorage')
    @patch('functions.KnowledgeGraph')
    @patch('functions.VectorStore')
    def test_update_knowledge_base_with_exception(self, mock_vector_store, mock_kg, mock_graph, mock_db, mock_summarizer, mock_fetcher):
        """Test update_knowledge_base with exception handling."""
        # Mock the RSS fetcher to raise an exception
        mock_fetcher_instance = Mock()
        mock_fetcher.return_value = mock_fetcher_instance
        mock_fetcher_instance.fetch.side_effect = Exception("Network error")
        
        # Test that the function handles exceptions gracefully
        with self.assertRaises(Exception):
            update_knowledge_base()


class TestKnowledgeGraphIntegration(unittest.TestCase):
    """Integration tests for knowledge graph functionality."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def tearDown(self):
        """Clean up after tests."""
        pass

    @patch('functions.KnowledgeGraphQuery')
    def test_entity_search_integration(self, mock_kg_query_class):
        """Test entity search integration."""
        mock_kg_query = Mock()
        mock_kg_query_class.return_value = mock_kg_query
        
        # Mock entity search result
        entity_result = {
            "query_type": "entity_search",
            "entity": "Google",
            "summary": "Google is a leading technology company",
            "articles": [
                {
                    "title": "Google Analytics Guide",
                    "link": "https://example.com",
                    "summary": "Complete guide to Google Analytics",
                    "published": "2024-01-15",
                    "topics": ["Analytics"],
                    "source": "Marketing Blog",
                    "entities": ["Google", "Analytics"]
                }
            ],
            "network": {
                "entity": "Google",
                "nodes": [{"name": "Analytics", "type": "TOOL"}],
                "relationships": []
            }
        }
        mock_kg_query.natural_language_query.return_value = entity_result
        
        # Test entity search
        result = query_knowledge_graph("Tell me about Google")
        
        self.assertEqual(result['query_type'], 'entity_search')
        self.assertEqual(result['entity'], 'Google')
        self.assertIn('articles', result)
        self.assertIn('network', result)

    @patch('functions.KnowledgeGraphQuery')
    def test_topic_search_integration(self, mock_kg_query_class):
        """Test topic search integration."""
        mock_kg_query = Mock()
        mock_kg_query_class.return_value = mock_kg_query
        
        # Mock topic search result
        topic_result = {
            "query_type": "topic_search",
            "topic": "SEO",
            "summary": "SEO is important for digital marketing",
            "articles": [
                {
                    "title": "SEO Best Practices",
                    "link": "https://example.com",
                    "summary": "Latest SEO strategies",
                    "published": "2024-01-15",
                    "topics": ["SEO"],
                    "source": "Marketing Blog",
                    "entities": ["Google", "SEO"]
                }
            ],
            "trending_topics": [
                {"topic": "SEO", "frequency": 10},
                {"topic": "Content Marketing", "frequency": 8}
            ]
        }
        mock_kg_query.natural_language_query.return_value = topic_result
        
        # Test topic search
        result = query_knowledge_graph("What are SEO trends?")
        
        self.assertEqual(result['query_type'], 'topic_search')
        self.assertEqual(result['topic'], 'SEO')
        self.assertIn('articles', result)
        self.assertIn('trending_topics', result)

    @patch('functions.KnowledgeGraphQuery')
    def test_relationship_search_integration(self, mock_kg_query_class):
        """Test relationship search integration."""
        mock_kg_query = Mock()
        mock_kg_query_class.return_value = mock_kg_query
        
        # Mock relationship search result
        relationship_result = {
            "query_type": "relationship_search",
            "entities": ["Google", "Facebook"],
            "summary": "Google and Facebook compete in digital advertising",
            "articles": [
                {
                    "title": "Google vs Facebook Advertising",
                    "link": "https://example.com",
                    "summary": "Comparison of advertising platforms",
                    "published": "2024-01-15",
                    "topics": ["Advertising"],
                    "source": "Marketing Blog",
                    "entities": ["Google", "Facebook"]
                }
            ],
            "networks": {
                "Google": {"nodes": [{"name": "Advertising", "type": "CONCEPT"}]},
                "Facebook": {"nodes": [{"name": "Social Media", "type": "CONCEPT"}]}
            }
        }
        mock_kg_query.natural_language_query.return_value = relationship_result
        
        # Test relationship search
        result = query_knowledge_graph("How do Google and Facebook compete?")
        
        self.assertEqual(result['query_type'], 'relationship_search')
        self.assertIn('Google', result['entities'])
        self.assertIn('Facebook', result['entities'])
        self.assertIn('articles', result)
        self.assertIn('networks', result)

    @patch('functions.KnowledgeGraphQuery')
    def test_trending_search_integration(self, mock_kg_query_class):
        """Test trending search integration."""
        mock_kg_query = Mock()
        mock_kg_query_class.return_value = mock_kg_query
        
        # Mock trending search result
        trending_result = {
            "query_type": "trending",
            "summary": "AI and video content are trending in marketing",
            "trending_topics": [
                {"topic": "AI Marketing", "frequency": 15},
                {"topic": "Video Content", "frequency": 12}
            ],
            "recent_articles": [
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
        }
        mock_kg_query.natural_language_query.return_value = trending_result
        
        # Test trending search
        result = query_knowledge_graph("What's trending in marketing?")
        
        self.assertEqual(result['query_type'], 'trending')
        self.assertIn('trending_topics', result)
        self.assertIn('recent_articles', result)
        self.assertIn('summary', result)


if __name__ == '__main__':
    unittest.main() 