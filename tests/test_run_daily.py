#!/usr/bin/env python3
"""
Test script for run_daily.py with improved error handling.

This script tests the daily update process with better error handling,
timeouts, and progress tracking.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if all required environment variables are set."""
    required_vars = [
        'DEEPSEEK_API_KEY',
        'NEO4J_URI',
        'NEO4J_USER',
        'NEO4J_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please check your .env file.")
        return False
    
    print("✅ All required environment variables are set.")
    return True

def test_imports():
    """Test if all required modules can be imported."""
    try:
        from functions import update_knowledge_base
        from scraper.rss_fetcher import RSSFetcher
        from processor.summarizer import Summarizer
        from storage.db_interface import MongoStorage
        from storage.graph_interface import GraphStorage
        from storage.knowledge_graph import KnowledgeGraph
        from storage.vector_store import VectorStore
        print("✅ All modules imported successfully.")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without running the full update."""
    try:
        print("🧪 Testing basic functionality...")
        
        # Test RSS fetcher
        from scraper.rss_fetcher import RSSFetcher
        fetcher = RSSFetcher()
        print("✅ RSSFetcher initialized")
        
        # Test summarizer
        from processor.summarizer import Summarizer
        summarizer = Summarizer()
        print("✅ Summarizer initialized")
        
        # Test vector store
        from storage.vector_store import VectorStore
        vs = VectorStore()
        print("✅ VectorStore initialized")
        
        print("✅ Basic functionality test passed.")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing run_daily.py improvements...")
    
    # Test 1: Environment variables
    if not test_environment():
        return False
    
    # Test 2: Module imports
    if not test_imports():
        return False
    
    # Test 3: Basic functionality
    if not test_basic_functionality():
        return False
    
    print("\n✅ All tests passed! The run_daily.py script should work properly.")
    print("\nTo run the full daily update:")
    print("python scheduler/run_daily.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 