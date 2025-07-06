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
- **Parallel Processing**: Optimized for performance with concurrent RSS fetching and article processing.

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
│   ├── hubspot_scraper.py
│   ├── rss_fetcher.py
│   └── parallel_rss_fetcher.py # Parallel RSS processing
├── processor/ # NLP processing, summarization, filtering
│   ├── summarizer.py
│   ├── relevance_checker.py
│   └── keyword_extractor.py
├── storage/ # Database and vector store interfaces
│   ├── db_interface.py
│   ├── vector_store.py
│   ├── knowledge_graph.py # Knowledge graph with entity extraction
│   └── knowledge_graph_query.py # Query interface for knowledge graph
├── scheduler/ # Job scheduling logic
│   └── run_daily.py
├── logs/ # Log files and tracking
├── main.py # Main orchestration script
├── kg_query.py # Knowledge graph query interface
├── test_knowledge_graph.py # Test script for knowledge graph
├── performance_comparison.py # Performance testing
├── run_tests.py # Test runner
└── requirements.txt # Python dependencies
```

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.9+
- Conda (recommended) or pip
- Neo4j Database (for knowledge graph)
- MongoDB (optional, for document storage)
- OpenAI API key (for embeddings and summarization)

### Step 1: Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/marketing-agent.git
cd marketing-agent

# Create and activate Conda environment
conda create --name marketing_agent python=3.9
conda activate marketing_agent

# Install core dependencies with conda (recommended for numpy/scikit-learn)
conda install -c conda-forge numpy scikit-learn "blas=*=openblas"
conda install -c conda-forge python-dotenv

# Install remaining dependencies
pip install -r requirements.txt
```

### Step 2: Setup Dependent Services

#### Option A: Neo4j (Required for Knowledge Graph)

**Using Docker (Recommended):**
```bash
# Pull and run Neo4j
docker run \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  -v neo4j_data:/data \
  -v neo4j_logs:/logs \
  neo4j:5.17.0

# Access Neo4j Browser at: http://localhost:7474
# Username: neo4j, Password: password
```

**Using Neo4j Desktop:**
1. Download from [neo4j.com](https://neo4j.com/download/)
2. Create a new database
3. Install APOC plugin for advanced functionality

#### Option B: MongoDB (Optional for Document Storage)

**Using Docker:**
```bash
docker run --name mongodb -p 27017:27017 -d mongo:latest
```

**Using MongoDB Atlas (Cloud):**
1. Create account at [mongodb.com](https://mongodb.com)
2. Create a free cluster
3. Get connection string

### Step 3: Environment Configuration

Create a `.env` file in the project root:

```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# MongoDB Configuration (Optional)
MONGODB_URI=mongodb://localhost:27017/marketing_agent

# Optional: Vector Store Path
VECTOR_STORE_PATH=./vector_store
```

### Step 4: Verify Installation

```bash
# Test basic imports
python -c "import numpy, sklearn, feedparser, requests; print('✅ Core dependencies working')"

# Test knowledge graph connection
python -c "from storage.knowledge_graph import KnowledgeGraph; kg = KnowledgeGraph(); print('✅ Neo4j connection working')"
```

---

## 🚀 Usage Examples

### 1. Knowledge Gathering

#### Basic Knowledge Base Update
```bash
# Run the daily update (sequential processing)
python scheduler/run_daily.py
```

#### Parallel Knowledge Base Update (Recommended)
```bash
# Use parallel processing for better performance
python -c "from functions import update_knowledge_base_parallel; update_knowledge_base_parallel()"
```

#### Custom RSS Feed Processing
```bash
# Process specific RSS feeds with custom settings
python -c "
from scraper.parallel_rss_fetcher import ParallelRSSFetcher
fetcher = ParallelRSSFetcher(max_workers=10)
articles = fetcher.fetch_all_feeds_threaded()
print(f'Fetched {len(articles)} articles')
"
```

### 2. Knowledge Querying

#### Query Knowledge Base
```bash
# Natural language query
python main.py "What are the latest trends in email marketing?"

# Or use the functions directly
python -c "
from functions import query_knowledge_base
result = query_knowledge_base('What are the latest SEO trends?')
print(result)
"
```

#### Query Knowledge Graph

**Entity Search:**
```bash
# Find information about specific companies
python kg_query.py entity "HubSpot"
python kg_query.py entity "Google Analytics"
```

**Topic Search:**
```bash
# Explore marketing topics
python kg_query.py query "What are the latest SEO trends?"
python kg_query.py query "How do companies use social media marketing?"
```

**Relationship Analysis:**
```bash
# Understand connections between entities
python kg_query.py query "How do Google and Facebook compete?"
python kg_query.py query "What tools integrate with HubSpot?"
```

**Trending Analysis:**
```bash
# Discover trending topics
python kg_query.py trending --days 30
python kg_query.py trending --days 7
```

**Graph Insights:**
```bash
# Get statistics and analytics
python kg_query.py insights
```

### 3. Testing and Development

#### Run Tests
```bash
# Run all tests
python run_tests.py

# Run specific test modules
python run_tests.py test_knowledge_graph
python run_tests.py test_knowledge_graph_query
python run_tests.py test_functions_integration
```

#### Performance Testing
```bash
# Compare sequential vs parallel processing
python performance_comparison.py --quick

# Full performance analysis
python performance_comparison.py
```

#### Test Knowledge Graph
```bash
# Test knowledge graph functionality
python test_knowledge_graph.py
```

### 4. Scheduling

#### Using Cron (Linux/macOS)
```bash
# Add to crontab (runs daily at 9 AM)
0 9 * * * cd /path/to/marketing-agent && conda activate marketing_agent && python scheduler/run_daily.py
```

#### Using Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to daily
4. Action: Start a program
5. Program: `python`
6. Arguments: `scheduler/run_daily.py`
7. Start in: `C:\path\to\marketing-agent`

#### Using Python APScheduler
```python
from apscheduler.schedulers.blocking import BlockingScheduler
from functions import update_knowledge_base_parallel

scheduler = BlockingScheduler()
scheduler.add_job(update_knowledge_base_parallel, 'interval', hours=24)
scheduler.start()
```

---

## 🔧 Configuration

### RSS Feed Sources
Edit `scraper/parallel_rss_fetcher.py` to add/remove RSS feeds:

```python
RSS_FEEDS = [
    "https://blog.hubspot.com/marketing/rss.xml",
    "https://www.marketingprofs.com/rss/rss.asp?i=1",
    "https://moz.com/blog/rss",
    # Add your preferred sources here
]
```

### Keywords for Relevance Filtering
```python
KEYWORDS = [
    "marketing", "seo", "content", "strategy", "branding",
    # Add relevant keywords
]
```

### Vector Store Configuration
```python
# In storage/vector_store.py
VECTOR_DIMENSION = 1536  # OpenAI embedding dimension
MODEL = "text-embedding-3-small"  # OpenAI model
```

---

## 🛠️ Troubleshooting

### Common Issues

**1. Neo4j Connection Error:**
```
Failed to establish connection to ResolvedIPv4Address(('127.0.0.1', 7687))
```
**Solution:** Start Neo4j server or check connection settings in `.env`

**2. NumPy/MKL Errors:**
```
Library not loaded: @rpath/libmkl_rt.2.dylib
```
**Solution:** Use OpenBLAS instead of MKL (already configured in installation)

**3. Missing Dependencies:**
```
ModuleNotFoundError: No module named 'dotenv'
```
**Solution:** Install with conda: `conda install -c conda-forge python-dotenv`

**4. OpenAI API Errors:**
```
openai.AuthenticationError: Invalid API key
```
**Solution:** Check your `OPENAI_API_KEY` in `.env` file

### Performance Optimization

**For Large Datasets:**
- Increase `max_workers` in parallel functions
- Use async fetching for RSS feeds
- Consider using cloud databases for Neo4j/MongoDB

**Memory Usage:**
- Monitor vector store size
- Implement data retention policies
- Use batch processing for large article sets

---

## 🛡️ Ethics & Legal
Scraping adheres to each site's robots.txt policy.

Content is summarized or stored with attribution to the original source.

Use APIs where available for better reliability and compliance.

## 🧩 TODO
 * Add support for more data sources
 * Integrate a triplet store for semantic search
 * Build a web UI and APIs
 * Add data visualization for knowledge graph
 * Implement automated trend detection
