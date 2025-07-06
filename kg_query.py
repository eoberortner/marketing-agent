#!/usr/bin/env python3
"""
Knowledge Graph Query Interface

This script provides a command-line interface for querying the marketing knowledge graph.
It supports various types of queries and provides structured results.
"""

import argparse
import json
from typing import Dict, List
from functions import query_knowledge_graph, get_knowledge_graph_insights


def format_article(article: Dict) -> str:
    """Format an article for display."""
    return f"""
📰 {article.get('title', 'No Title')}
🔗 {article.get('link', 'No Link')}
📅 {article.get('published', 'No Date')}
📊 Topics: {', '.join(article.get('topics', []))}
🏷️ Entities: {', '.join(article.get('entities', []))}
📝 {article.get('summary', 'No Summary')[:200]}...
"""


def format_network(network: Dict) -> str:
    """Format network data for display."""
    if not network.get('nodes'):
        return "No network data available."
    
    result = f"\n🌐 Network for {network['entity']}:\n"
    result += "Connected entities:\n"
    
    for node in network['nodes'][:10]:  # Limit to first 10
        result += f"  • {node['name']} ({node['type']})\n"
    
    if network.get('relationships'):
        result += "\nRelationships:\n"
        for rel in network['relationships'][:5]:  # Limit to first 5
            result += f"  • {rel['from']} --[{rel['type']}]--> {rel['to']}\n"
    
    return result


def display_results(results: Dict):
    """Display query results in a formatted way."""
    print(f"\n🔍 Query Type: {results.get('query_type', 'Unknown')}")
    print("=" * 50)
    
    # Display summary
    if results.get('summary'):
        print(f"\n📊 Summary:\n{results['summary']}")
    
    # Display articles
    if results.get('articles'):
        print(f"\n📰 Found {len(results['articles'])} relevant articles:")
        for i, article in enumerate(results['articles'][:5], 1):  # Limit to first 5
            print(f"\n{i}. {format_article(article)}")
    
    # Display network data
    if results.get('network'):
        print(format_network(results['network']))
    
    # Display trending topics
    if results.get('trending_topics'):
        print(f"\n📈 Trending Topics:")
        for topic in results['trending_topics'][:10]:
            print(f"  • {topic['topic']} ({topic['frequency']} mentions)")
    
    # Display statistics
    if results.get('stats'):
        stats = results['stats']
        print(f"\n📊 Knowledge Graph Statistics:")
        if stats.get('nodes'):
            for node_type, count in stats['nodes'].items():
                print(f"  • {node_type}: {count}")
        if stats.get('relationships'):
            for rel_type, count in stats['relationships'].items():
                print(f"  • {rel_type}: {count}")


def display_insights(insights: Dict):
    """Display knowledge graph insights."""
    print("\n📊 Knowledge Graph Insights")
    print("=" * 50)
    
    print(f"\n📈 Total Articles: {insights.get('total_articles', 0)}")
    print(f"🏷️ Total Entities: {insights.get('total_entities', 0)}")
    print(f"📰 Total Sources: {insights.get('total_sources', 0)}")
    
    if insights.get('trending_topics'):
        print(f"\n🔥 Top Trending Topics (Last 30 Days):")
        for i, topic in enumerate(insights['trending_topics'][:10], 1):
            print(f"  {i}. {topic['topic']} ({topic['frequency']} mentions)")
    
    if insights.get('statistics'):
        stats = insights['statistics']
        if stats.get('articles_by_source'):
            print(f"\n📰 Articles by Source:")
            for source in stats['articles_by_source'][:5]:
                print(f"  • {source['source']}: {source['count']} articles")


def main():
    parser = argparse.ArgumentParser(
        description="Query the Marketing Knowledge Graph using natural language."
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the knowledge graph')
    query_parser.add_argument(
        "query",
        type=str,
        nargs="+",
        help="The natural language query (e.g., 'What are the latest trends in email marketing?')",
    )
    query_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    # Insights command
    insights_parser = subparsers.add_parser('insights', help='Get knowledge graph insights')
    insights_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    # Entity command
    entity_parser = subparsers.add_parser('entity', help='Get information about a specific entity')
    entity_parser.add_argument(
        "entity",
        type=str,
        help="The entity name (e.g., 'Google', 'HubSpot')"
    )
    entity_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    # Trending command
    trending_parser = subparsers.add_parser('trending', help='Get trending topics')
    trending_parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)"
    )
    trending_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    args = parser.parse_args()
    
    if args.command == 'query':
        query_str = " ".join(args.query)
        results = query_knowledge_graph(query_str)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            display_results(results)
    
    elif args.command == 'insights':
        insights = get_knowledge_graph_insights()
        
        if args.json:
            print(json.dumps(insights, indent=2))
        else:
            display_insights(insights)
    
    elif args.command == 'entity':
        query_str = f"Tell me about {args.entity}"
        results = query_knowledge_graph(query_str)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            display_results(results)
    
    elif args.command == 'trending':
        # Create a trending query
        query_str = f"What are the trending topics in the last {args.days} days?"
        results = query_knowledge_graph(query_str)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            display_results(results)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 