# 🧠 Marketing Intelligence Agent

An autonomous AI agent that scrapes the internet for marketing-related information, processes it, and stores it for retrieval and analysis. The agent runs automatically once or twice a day, continuously learning from trusted sources and summarizing key insights.

---

## 📌 Features

- **Web Scraping**: Gathers fresh marketing content from sources like HubSpot, MarketingProfs, Moz, etc.
- **Relevance Filtering**: Identifies content related to marketing using semantic and keyword-based techniques.
- **Summarization**: Generates concise summaries and key takeaways using an LLM or NLP tools.
- **Storage**: Saves raw and processed data into structured databases and optionally a vector store for semantic search.
- **Scheduling**: Runs automatically on a daily schedule via a task scheduler.
- **Extensibility**: Modular architecture makes it easy to add new sources, processing steps, or output formats.
- **Knowledge Graph**: Builds a comprehensive knowledge graph with entities, relationships, and insights from gathered content.

---

## 📈 Example Use Cases
Track marketing trends from top blogs.

Build a knowledge base or newsletter from daily summaries.

Perform sentiment or trend analysis on industry news.

Query the knowledge graph for entity relationships and insights.

## 🧠 Knowledge Graph Features

The system now includes a comprehensive knowledge graph that:

- **Entity Extraction**: Automatically identifies companies, tools, platforms, and concepts from articles
- **Relationship Mapping**: Maps relationships between entities (competitors, integrations, partnerships)
- **Topic Analysis**: Tracks trending topics and their evolution over time
- **Network Analysis**: Provides insights into entity networks and connections
- **Intelligent Querying**: Supports natural language queries with context-aware responses

### Knowledge Graph Query Types

1. **Entity Search**: Find information about specific companies or tools
   ```bash
   python kg_query.py entity "HubSpot"
   ```

2. **Topic Search**: Explore marketing topics and trends
   ```bash
   python kg_query.py query "What are the latest SEO trends?"
   ```

3. **Relationship Analysis**: Understand connections between entities
   ```bash
   python kg_query.py query "How do Google and Facebook compete?"
   ```

4. **Trending Analysis**: Discover what's currently trending
   ```bash
   python kg_query.py trending --days 30
   ```

5. **Graph Insights**: Get statistics and analytics
   ```bash
   python kg_query.py insights
   ```


## 🗂️ Project Structure

```
marketing-agent/
├── scraper/ # Web scrapers and data fetchers
│ ├── hubspot_scraper.py
│ └── rss_fetcher.py
├── processor/ # NLP processing, summarization, filtering
│ ├── summarizer.py
│ ├── relevance_checker.py
│ └── keyword_extractor.py
├── storage/ # Database and vector store interfaces
│ ├── db_interface.py
│ ├── vector_store.py
│ ├── knowledge_graph.py # Knowledge graph with entity extraction
│ └── knowledge_graph_query.py # Query interface for knowledge graph
├── scheduler/ # Job scheduling logic
│ └── run_daily.py
├── logs/ # Log files and tracking
├── main.py # Main orchestration script
├── kg_query.py # Knowledge graph query interface
├── test_knowledge_graph.py # Test script for knowledge graph
└── requirements.txt # Python dependencies
```


---

## ⚙️ Installation (Using Conda)

```bash
# Clone the repository
git clone https://github.com/yourusername/marketing-agent.git
cd marketing-agent

# Create and activate Conda environment
conda create --name marketing-agent python=3.10
conda activate marketing-agent

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

### Create an `.env` file

Example:

```
OPENAI_API_KEY="***"
DEEPSEEK_API_KEY="***"
NEO4J_USERNAME="***"
NEO4J_PASSWORD="***"
```


### Manually run the agent:

#### * to build the knowledge base

```commandline
python scheduler/run_daily.py
```

To schedule it to run daily, consider using:

* cron (Linux/macOS)

* Task Scheduler (Windows)

* Python-based job scheduler (e.g., APScheduler)

* Cloud schedulers (AWS Lambda, GitHub Actions, etc.)


#### * to query the knowledge base
```commandline
python main.py 'What are the latest trends in email marketing?'
```

#### * to update knowledge base (parallel processing)
```commandline
# Use parallel processing for better performance
python -c "from functions import update_knowledge_base_parallel; update_knowledge_base_parallel()"

# Or run the parallel fetcher directly
python scraper/parallel_rss_fetcher.py
```

#### * to query the knowledge graph
```commandline
# Query specific entity
python kg_query.py entity "HubSpot"

# Query trending topics
python kg_query.py trending --days 30

# Get knowledge graph insights
python kg_query.py insights

# Natural language query
python kg_query.py query "How do Google and Facebook compete in digital advertising?"

# Test knowledge graph functionality
python test_knowledge_graph.py

# Run unit tests
python run_tests.py

# Performance comparison
python performance_comparison.py --quick

# Run specific test module
python run_tests.py test_knowledge_graph
python run_tests.py test_knowledge_graph_query
python run_tests.py test_functions_integration
```



## 🛡️ Ethics & Legal
Scraping adheres to each site’s robots.txt policy.

Content is summarized or stored with attribution to the original source.

Use APIs where available for better reliability and compliance.

## 🧩 TODO
 * Add support for more data sources

 * Integrate a triplet store for semantic search

 * Build a web UI and APIs

 * Implement daily email digests or Slack alerts

 * Enhance knowledge graph with more entity types and relationships

 * Add visualization tools for the knowledge graph

## 🚀 Parallel Processing

The system now supports parallel processing for improved performance:

### Features
- **Parallel RSS Fetching**: Fetch multiple RSS feeds concurrently using async/threading
- **Parallel Article Processing**: Process articles (summarization) in parallel
- **Parallel Storage**: Store articles across different storage systems concurrently
- **Performance Monitoring**: Detailed timing and success/failure metrics

### Usage

```bash
# Use parallel processing for knowledge base updates
python -c "from functions import update_knowledge_base_parallel; update_knowledge_base_parallel()"

# Configure parallel processing parameters
python -c "
from functions import update_knowledge_base_parallel
update_knowledge_base_parallel(
    max_fetch_workers=5,      # RSS fetching workers
    max_process_workers=3,     # Article processing workers  
    max_storage_workers=2,     # Storage workers
    use_async_fetch=True       # Use async for RSS fetching
)
"
```

### Performance Comparison

```bash
# Quick performance test
python performance_comparison.py --quick

# Full performance comparison
python performance_comparison.py
```

## 🧪 Testing

The project includes comprehensive unit tests for the knowledge graph functionality:

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test modules
python run_tests.py test_knowledge_graph
python run_tests.py test_knowledge_graph_query
python run_tests.py test_functions_integration
```

### Test Coverage

The tests cover:
- **KnowledgeGraph**: Entity extraction, storage, querying, and statistics
- **KnowledgeGraphQuery**: Query classification, entity search, topic search, and relationship analysis
- **Integration**: Function integration with the main system
- **Error Handling**: Exception handling and fallback mechanisms
- **Parallel Processing**: RSS fetching, article processing, and storage operations

## 👥 Contributions
Open to feedback and collaboration! Please file an issue or submit a pull request with ideas or improvements.

## 📄 License
MIT License – see the LICENSE file for full details.
