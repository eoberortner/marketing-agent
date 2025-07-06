#!/usr/bin/env python3
"""
Test script for the Knowledge Graph functionality

This script demonstrates the knowledge graph features and provides examples
of how to use the system.
"""

import json
from datetime import datetime
from functions import query_knowledge_graph, get_knowledge_graph_insights, update_knowledge_base


def test_knowledge_graph():
    """Test the knowledge graph functionality."""
    print("🧪 Testing Knowledge Graph Functionality")
    print("=" * 50)
    
    # Test 1: Get insights
    print("\n1️⃣ Getting Knowledge Graph Insights...")
    try:
        insights = get_knowledge_graph_insights()
        print(f"✅ Successfully retrieved insights")
        print(f"📊 Total Articles: {insights.get('total_articles', 0)}")
        print(f"🏷️ Total Entities: {insights.get('total_entities', 0)}")
        print(f"📰 Total Sources: {insights.get('total_sources', 0)}")
    except Exception as e:
        print(f"❌ Failed to get insights: {e}")
    
    # Test 2: Entity search
    print("\n2️⃣ Testing Entity Search...")
    test_entities = ["Google", "HubSpot", "Facebook", "SEO"]
    for entity in test_entities:
        try:
            print(f"\n🔍 Searching for: {entity}")
            results = query_knowledge_graph(f"Tell me about {entity}")
            if results.get('articles'):
                print(f"✅ Found {len(results['articles'])} articles about {entity}")
                if results.get('summary'):
                    print(f"📝 Summary: {results['summary'][:100]}...")
            else:
                print(f"⚠️ No articles found for {entity}")
        except Exception as e:
            print(f"❌ Failed to search for {entity}: {e}")
    
    # Test 3: Topic search
    print("\n3️⃣ Testing Topic Search...")
    test_topics = ["email marketing", "social media", "content marketing", "analytics"]
    for topic in test_topics:
        try:
            print(f"\n🔍 Searching for: {topic}")
            results = query_knowledge_graph(f"What are the latest trends in {topic}?")
            if results.get('articles'):
                print(f"✅ Found {len(results['articles'])} articles about {topic}")
                if results.get('summary'):
                    print(f"📝 Summary: {results['summary'][:100]}...")
            else:
                print(f"⚠️ No articles found for {topic}")
        except Exception as e:
            print(f"❌ Failed to search for {topic}: {e}")
    
    # Test 4: Trending topics
    print("\n4️⃣ Testing Trending Topics...")
    try:
        results = query_knowledge_graph("What are the current trending topics in marketing?")
        if results.get('trending_topics'):
            print(f"✅ Found {len(results['trending_topics'])} trending topics")
            for i, topic in enumerate(results['trending_topics'][:5], 1):
                print(f"  {i}. {topic['topic']} ({topic['frequency']} mentions)")
        else:
            print("⚠️ No trending topics found")
    except Exception as e:
        print(f"❌ Failed to get trending topics: {e}")
    
    # Test 5: Relationship search
    print("\n5️⃣ Testing Relationship Search...")
    test_relationships = [
        "Google and Facebook",
        "HubSpot and email marketing",
        "SEO and content marketing"
    ]
    for rel in test_relationships:
        try:
            print(f"\n🔍 Searching for relationship: {rel}")
            results = query_knowledge_graph(f"How do {rel} relate to each other?")
            if results.get('articles'):
                print(f"✅ Found {len(results['articles'])} articles about {rel}")
                if results.get('summary'):
                    print(f"📝 Summary: {results['summary'][:100]}...")
            else:
                print(f"⚠️ No articles found for {rel}")
        except Exception as e:
            print(f"❌ Failed to search for {rel}: {e}")


def demo_knowledge_graph_queries():
    """Demonstrate various knowledge graph queries."""
    print("\n🎯 Knowledge Graph Query Demonstrations")
    print("=" * 50)
    
    queries = [
        {
            "type": "Entity Search",
            "query": "What is HubSpot known for in marketing?",
            "description": "Searching for information about a specific company"
        },
        {
            "type": "Topic Search", 
            "query": "What are the latest SEO trends?",
            "description": "Searching for information about a marketing topic"
        },
        {
            "type": "Trending",
            "query": "What's trending in digital marketing?",
            "description": "Searching for current trends"
        },
        {
            "type": "Relationship",
            "query": "How do Google and Facebook compete in digital advertising?",
            "description": "Searching for relationships between entities"
        },
        {
            "type": "General",
            "query": "What are the best practices for email marketing?",
            "description": "General information search"
        }
    ]
    
    for i, query_info in enumerate(queries, 1):
        print(f"\n{i}️⃣ {query_info['type']}")
        print(f"Query: {query_info['query']}")
        print(f"Description: {query_info['description']}")
        
        try:
            results = query_knowledge_graph(query_info['query'])
            
            print(f"✅ Query Type: {results.get('query_type', 'Unknown')}")
            if results.get('articles'):
                print(f"📰 Found {len(results['articles'])} articles")
            if results.get('summary'):
                print(f"📝 Summary: {results['summary'][:150]}...")
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
        
        print("-" * 30)


def update_and_test():
    """Update the knowledge base and then test queries."""
    print("\n🔄 Updating Knowledge Base...")
    print("=" * 50)
    
    try:
        update_knowledge_base()
        print("✅ Knowledge base updated successfully!")
        
        # Wait a moment for processing
        import time
        time.sleep(2)
        
        # Now test queries
        test_knowledge_graph()
        
    except Exception as e:
        print(f"❌ Failed to update knowledge base: {e}")


def main():
    """Main function to run tests."""
    print("🚀 Knowledge Graph Test Suite")
    print("=" * 50)
    
    # Check if we want to update first
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        update_and_test()
    else:
        # Just run tests
        test_knowledge_graph()
        demo_knowledge_graph_queries()


if __name__ == "__main__":
    main() 