from typing import List, Dict, Optional
from storage.knowledge_graph import KnowledgeGraph
from connectors.llm import DeepSeekClient


class KnowledgeGraphQuery:
    def __init__(self):
        self.kg = KnowledgeGraph()
        # Initialize LLM client with explicit API key
        import os
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        self.llm_client = DeepSeekClient(api_key=api_key)

    def close(self):
        self.kg.close()

    def natural_language_query(self, query: str) -> Dict:
        """
        Process a natural language query and return structured results.
        """
        # First, try to understand the query type
        query_type = self._classify_query(query)
        
        if query_type == "entity_search":
            return self._handle_entity_search(query)
        elif query_type == "topic_search":
            return self._handle_topic_search(query)
        elif query_type == "trending":
            return self._handle_trending_search(query)
        elif query_type == "relationship_search":
            return self._handle_relationship_search(query)
        else:
            return self._handle_general_search(query)

    def _classify_query(self, query: str) -> str:
        """
        Classify the type of query being asked.
        """
        classification_prompt = f"""
        Classify this marketing knowledge base query into one of these categories:
        - entity_search: Looking for information about a specific company, tool, or platform
        - topic_search: Looking for information about a marketing topic or concept
        - trending: Asking about trends, what's popular, or recent developments
        - relationship_search: Asking about relationships between entities or how things connect
        - general_search: General information search
        
        Query: "{query}"
        
        Return only the category name.
        """
        
        try:
            task_description = {
                "task": "Classify the query type",
                "prompt": classification_prompt,
                "format": "category"
            }
            response = self.llm_client.summarize(
                agent_description="You are an expert at classifying queries.",
                task_description=task_description
            )
            return response.strip().lower()
        except:
            return "general_search"

    def _handle_entity_search(self, query: str) -> Dict:
        """
        Handle queries about specific entities (companies, tools, platforms).
        """
        # Extract entity name from query
        entity_name = self._extract_entity_name(query)
        
        if entity_name:
            # Get entity network
            network = self.kg.get_entity_network(entity_name)
            
            # Get articles mentioning this entity
            articles = self.kg.query_knowledge_graph(entity_name, limit=10)
            
            # Generate summary
            summary = self._generate_entity_summary(entity_name, articles, network)
            
            return {
                "query_type": "entity_search",
                "entity": entity_name,
                "summary": summary,
                "articles": articles,
                "network": network
            }
        else:
            return self._handle_general_search(query)

    def _handle_topic_search(self, query: str) -> Dict:
        """
        Handle queries about marketing topics and concepts.
        """
        # Extract key terms from the query
        key_terms = self._extract_key_terms(query)
        
        # Search for articles using key terms
        articles = []
        for term in key_terms:
            term_articles = self.kg.query_knowledge_graph(term, limit=10)
            articles.extend(term_articles)
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in articles:
            if article.get('title') not in seen_titles:
                seen_titles.add(article.get('title'))
                unique_articles.append(article)
        
        # Get trending topics related to the query
        trending = self.kg.get_trending_topics(days=30)
        
        # Generate summary
        summary = self._generate_topic_summary(query, unique_articles, trending)
        
        return {
            "query_type": "topic_search",
            "topic": query,
            "key_terms": key_terms,
            "summary": summary,
            "articles": unique_articles[:15],  # Limit to 15 articles
            "trending_topics": trending
        }

    def _handle_trending_search(self, query: str) -> Dict:
        """
        Handle queries about trends and recent developments.
        """
        trending_topics = self.kg.get_trending_topics(days=30)
        recent_articles = self.kg.query_knowledge_graph("trend", limit=10)
        
        summary = self._generate_trending_summary(trending_topics, recent_articles)
        
        return {
            "query_type": "trending",
            "summary": summary,
            "trending_topics": trending_topics,
            "recent_articles": recent_articles
        }

    def _handle_relationship_search(self, query: str) -> Dict:
        """
        Handle queries about relationships between entities.
        """
        # Extract entities from query
        entities = self._extract_entities_from_query(query)
        
        if len(entities) >= 2:
            # Find articles that mention both entities
            articles = self.kg.query_knowledge_graph(f"{entities[0]} {entities[1]}", limit=10)
            
            # Get networks for both entities
            networks = {}
            for entity in entities[:2]:  # Limit to first 2 entities
                networks[entity] = self.kg.get_entity_network(entity, depth=1)
            
            summary = self._generate_relationship_summary(entities, articles, networks)
            
            return {
                "query_type": "relationship_search",
                "entities": entities,
                "summary": summary,
                "articles": articles,
                "networks": networks
            }
        else:
            return self._handle_general_search(query)

    def _handle_general_search(self, query: str) -> Dict:
        """
        Handle general information searches.
        """
        articles = self.kg.query_knowledge_graph(query, limit=10)
        
        # Get knowledge graph stats
        stats = self.kg.get_knowledge_graph_stats()
        
        summary = self._generate_general_summary(query, articles)
        
        return {
            "query_type": "general_search",
            "summary": summary,
            "articles": articles,
            "stats": stats
        }

    def _extract_entity_name(self, query: str) -> Optional[str]:
        """
        Extract entity name from a query.
        """
        # Common marketing entities
        entities = [
            "Google", "Facebook", "Meta", "Twitter", "LinkedIn", "Instagram", "TikTok",
            "YouTube", "HubSpot", "Mailchimp", "Salesforce", "Adobe", "Microsoft",
            "Apple", "Amazon", "WordPress", "Shopify", "WooCommerce", "Squarespace",
            "Wix", "Canva", "Figma", "Slack", "Zoom", "Trello", "Asana"
        ]
        
        query_lower = query.lower()
        for entity in entities:
            if entity.lower() in query_lower:
                return entity
        
        return None

    def _extract_entities_from_query(self, query: str) -> List[str]:
        """
        Extract multiple entities from a query.
        """
        entities = [
            "Google", "Facebook", "Meta", "Twitter", "LinkedIn", "Instagram", "TikTok",
            "YouTube", "HubSpot", "Mailchimp", "Salesforce", "Adobe", "Microsoft",
            "Apple", "Amazon", "WordPress", "Shopify", "WooCommerce", "Squarespace",
            "Wix", "Canva", "Figma", "Slack", "Zoom", "Trello", "Asana"
        ]
        
        found_entities = []
        query_lower = query.lower()
        for entity in entities:
            if entity.lower() in query_lower:
                found_entities.append(entity)
        
        return found_entities

    def _extract_key_terms(self, query: str) -> List[str]:
        """
        Extract key terms from a natural language query for topic search.
        """
        # Common marketing topics and terms
        marketing_terms = [
            "A/B testing", "AB testing", "split testing", "conversion optimization",
            "email marketing", "social media", "content marketing", "SEO", "PPC",
            "lead generation", "customer acquisition", "branding", "analytics",
            "automation", "personalization", "retargeting", "influencer marketing",
            "video marketing", "mobile marketing", "local SEO", "voice search",
            "chatbots", "AI marketing", "machine learning", "data-driven",
            "customer experience", "user experience", "conversion rate",
            "click-through rate", "bounce rate", "engagement", "ROI"
        ]
        
        # Extract terms that appear in the query
        found_terms = []
        query_lower = query.lower()
        
        for term in marketing_terms:
            if term.lower() in query_lower:
                found_terms.append(term)
        
        # If no specific terms found, try to extract general words
        if not found_terms:
            # Remove common words and extract meaningful terms
            import re
            words = re.findall(r'\b\w+\b', query.lower())
            stop_words = {'what', 'can', 'you', 'tell', 'me', 'about', 'and', 'its', 'in', 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall'}
            meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
            found_terms = meaningful_words[:5]  # Limit to 5 most relevant words
        
        return found_terms

    def _generate_entity_summary(self, entity: str, articles: List[Dict], network: Dict) -> str:
        """
        Generate a summary about an entity based on articles and network data.
        """
        if not articles:
            return f"No information found about {entity} in the knowledge base."
        
        # Prepare context for LLM
        context = f"Entity: {entity}\n\n"
        context += "Recent articles:\n"
        for article in articles[:5]:
            context += f"- {article['title']}\n"
        
        if network.get("nodes"):
            context += f"\nRelated entities: {', '.join([n['name'] for n in network['nodes'][:5]])}\n"
        
        prompt = f"""
        Based on the following information about {entity}, provide a concise summary of:
        1. What {entity} is known for in marketing
        2. Recent developments or mentions
        3. Key relationships with other entities
        
        Information:
        {context}
        
        Provide a professional, informative summary in 2-3 paragraphs.
        """
        
        try:
            task_description = {
                "task": "Generate entity summary",
                "prompt": prompt,
                "format": "markdown"
            }
            return self.llm_client.summarize(
                agent_description="You are a marketing expert providing insights about companies and tools.",
                task_description=task_description
            )
        except:
            return f"Found {len(articles)} articles about {entity} in the knowledge base."

    def _generate_topic_summary(self, topic: str, articles: List[Dict], trending: List[Dict]) -> str:
        """
        Generate a summary about a marketing topic.
        """
        if not articles:
            return f"No information found about {topic} in the knowledge base."
        
        context = f"Topic: {topic}\n\n"
        context += "Recent articles:\n"
        for article in articles[:5]:
            context += f"- {article['title']}\n"
        
        if trending:
            context += f"\nTrending topics: {', '.join([t['topic'] for t in trending[:5]])}\n"
        
        prompt = f"""
        Based on the following information about {topic}, provide a concise summary of:
        1. Current state and importance of {topic} in marketing
        2. Recent developments and trends
        3. Key insights and best practices
        
        Information:
        {context}
        
        Provide a professional, informative summary in 2-3 paragraphs.
        """
        
        try:
            task_description = {
                "task": "Generate topic summary",
                "prompt": prompt,
                "format": "markdown"
            }
            return self.llm_client.summarize(
                agent_description="You are a marketing expert providing insights about marketing topics.",
                task_description=task_description
            )
        except:
            return f"Found {len(articles)} articles about {topic} in the knowledge base."

    def _generate_trending_summary(self, trending: List[Dict], articles: List[Dict]) -> str:
        """
        Generate a summary about trending topics.
        """
        if not trending:
            return "No trending topics found in the recent data."
        
        context = "Top trending topics:\n"
        for topic in trending[:10]:
            context += f"- {topic['topic']} (mentioned {topic['frequency']} times)\n"
        
        context += "\nRecent articles:\n"
        for article in articles[:5]:
            context += f"- {article['title']}\n"
        
        prompt = f"""
        Based on the following trending topics and recent articles, provide a summary of:
        1. Current marketing trends and hot topics
        2. What's gaining attention in the marketing world
        3. Key insights about recent developments
        
        Information:
        {context}
        
        Provide a professional, informative summary in 2-3 paragraphs.
        """
        
        try:
            task_description = {
                "task": "Generate trending summary",
                "prompt": prompt,
                "format": "markdown"
            }
            return self.llm_client.summarize(
                agent_description="You are a marketing expert analyzing trends and developments.",
                task_description=task_description
            )
        except:
            return f"Found {len(trending)} trending topics in the recent data."

    def _generate_relationship_summary(self, entities: List[str], articles: List[Dict], networks: Dict) -> str:
        """
        Generate a summary about relationships between entities.
        """
        if not articles:
            return f"No information found about the relationship between {', '.join(entities)}."
        
        context = f"Entities: {', '.join(entities)}\n\n"
        context += "Related articles:\n"
        for article in articles[:5]:
            context += f"- {article['title']}\n"
        
        context += "\nEntity networks:\n"
        for entity, network in networks.items():
            if network.get("nodes"):
                context += f"{entity} connects to: {', '.join([n['name'] for n in network['nodes'][:3]])}\n"
        
        prompt = f"""
        Based on the following information about {', '.join(entities)}, provide a summary of:
        1. How these entities relate to each other in marketing
        2. Their roles and interactions
        3. Key insights about their relationship
        
        Information:
        {context}
        
        Provide a professional, informative summary in 2-3 paragraphs.
        """
        
        try:
            task_description = {
                "task": "Generate relationship summary",
                "prompt": prompt,
                "format": "markdown"
            }
            return self.llm_client.summarize(
                agent_description="You are a marketing expert analyzing relationships between companies and tools.",
                task_description=task_description
            )
        except:
            return f"Found {len(articles)} articles about the relationship between {', '.join(entities)}."

    def _generate_general_summary(self, query: str, articles: List[Dict]) -> str:
        """
        Generate a general summary for a query.
        """
        if not articles:
            return f"No information found about '{query}' in the knowledge base."
        
        context = f"Query: {query}\n\n"
        context += "Relevant articles:\n"
        for article in articles[:5]:
            context += f"- {article['title']}\n"
        
        prompt = f"""
        Based on the following articles, provide a comprehensive answer to: "{query}"
        
        Articles:
        {context}
        
        Provide a professional, informative answer that directly addresses the query.
        """
        
        try:
            task_description = {
                "task": "Generate general summary",
                "prompt": prompt,
                "format": "markdown"
            }
            return self.llm_client.summarize(
                agent_description="You are a marketing expert providing comprehensive answers to queries.",
                task_description=task_description
            )
        except:
            return f"Found {len(articles)} articles related to '{query}' in the knowledge base."

    def get_knowledge_graph_insights(self) -> Dict:
        """
        Get insights and analytics from the knowledge graph.
        """
        stats = self.kg.get_knowledge_graph_stats()
        trending = self.kg.get_trending_topics(days=30)
        
        return {
            "statistics": stats,
            "trending_topics": trending,
            "total_articles": stats.get("nodes", {}).get("Article", 0),
            "total_entities": stats.get("nodes", {}).get("Entity", 0),
            "total_sources": stats.get("nodes", {}).get("Source", 0)
        } 