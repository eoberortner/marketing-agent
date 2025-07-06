import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBasicFunctionality(unittest.TestCase):
    """Basic functionality tests to ensure components can be imported and initialized."""

    def test_import_knowledge_graph(self):
        """Test that KnowledgeGraph can be imported."""
        try:
            from storage.knowledge_graph import KnowledgeGraph
            self.assertTrue(True, "KnowledgeGraph imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import KnowledgeGraph: {e}")

    def test_import_knowledge_graph_query(self):
        """Test that KnowledgeGraphQuery can be imported."""
        try:
            from storage.knowledge_graph_query import KnowledgeGraphQuery
            self.assertTrue(True, "KnowledgeGraphQuery imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import KnowledgeGraphQuery: {e}")

    def test_import_functions(self):
        """Test that the new functions can be imported."""
        try:
            from functions import query_knowledge_graph, get_knowledge_graph_insights
            self.assertTrue(True, "Knowledge graph functions imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import knowledge graph functions: {e}")

    def test_knowledge_graph_initialization(self):
        """Test that KnowledgeGraph can be initialized (with mocked dependencies)."""
        try:
            from unittest.mock import patch
            from storage.knowledge_graph import KnowledgeGraph
            
            with patch('storage.knowledge_graph.GraphDatabase.driver'):
                with patch('storage.knowledge_graph.DeepSeekClient'):
                    kg = KnowledgeGraph()
                    self.assertIsNotNone(kg)
                    kg.close()
        except Exception as e:
            self.fail(f"Failed to initialize KnowledgeGraph: {e}")

    def test_knowledge_graph_query_initialization(self):
        """Test that KnowledgeGraphQuery can be initialized (with mocked dependencies)."""
        try:
            from unittest.mock import patch
            from storage.knowledge_graph_query import KnowledgeGraphQuery
            
            with patch('storage.knowledge_graph_query.KnowledgeGraph'):
                with patch('storage.knowledge_graph_query.DeepSeekClient'):
                    kg_query = KnowledgeGraphQuery()
                    self.assertIsNotNone(kg_query)
                    kg_query.close()
        except Exception as e:
            self.fail(f"Failed to initialize KnowledgeGraphQuery: {e}")

    def test_basic_entity_extraction(self):
        """Test basic entity extraction functionality."""
        try:
            from unittest.mock import patch
            from storage.knowledge_graph import KnowledgeGraph
            
            with patch('storage.knowledge_graph.GraphDatabase.driver'):
                with patch('storage.knowledge_graph.DeepSeekClient'):
                    kg = KnowledgeGraph()
                    
                    article = {
                        "title": "Google Analytics 4: Complete Guide",
                        "summary": "Learn how to use Google Analytics 4 for better marketing insights.",
                        "summary_processed": "Google Analytics 4 provides advanced marketing analytics."
                    }
                    
                    result = kg._basic_entity_extraction(article)
                    
                    self.assertIn('entities', result)
                    self.assertIn('relationships', result)
                    self.assertIn('topics', result)
                    self.assertIn('insights', result)
                    self.assertIn('trends', result)
                    
                    # Check that Google was extracted
                    entity_names = [entity['name'] for entity in result['entities']]
                    self.assertIn('Google', entity_names)
                    
                    kg.close()
        except Exception as e:
            self.fail(f"Failed to test basic entity extraction: {e}")

    def test_query_classification(self):
        """Test query classification functionality."""
        try:
            from unittest.mock import patch
            from storage.knowledge_graph_query import KnowledgeGraphQuery
            
            with patch('storage.knowledge_graph_query.KnowledgeGraph'):
                with patch('storage.knowledge_graph_query.DeepSeekClient'):
                    kg_query = KnowledgeGraphQuery()
                    
                    # Test entity extraction
                    entity = kg_query._extract_entity_name("Tell me about Google Analytics")
                    self.assertEqual(entity, "Google")
                    
                    # Test multiple entity extraction
                    entities = kg_query._extract_entities_from_query("Compare Google and Facebook")
                    self.assertIn("Google", entities)
                    self.assertIn("Facebook", entities)
                    
                    kg_query.close()
        except Exception as e:
            self.fail(f"Failed to test query classification: {e}")

    def test_function_imports(self):
        """Test that the new functions are available in the functions module."""
        try:
            from functions import query_knowledge_graph, get_knowledge_graph_insights
            
            # Check that functions are callable
            self.assertTrue(callable(query_knowledge_graph))
            self.assertTrue(callable(get_knowledge_graph_insights))
            
        except Exception as e:
            self.fail(f"Failed to import or verify functions: {e}")


if __name__ == '__main__':
    unittest.main() 