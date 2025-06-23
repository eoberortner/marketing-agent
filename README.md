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

---

## 📈 Example Use Cases
Track marketing trends from top blogs.

Build a knowledge base or newsletter from daily summaries.

Perform sentiment or trend analysis on industry news.


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
│ └── vector_store.py
├── scheduler/ # Job scheduling logic
│ └── run_daily.py
├── logs/ # Log files and tracking
├── main.py # Main orchestration script
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



## 🛡️ Ethics & Legal
Scraping adheres to each site’s robots.txt policy.

Content is summarized or stored with attribution to the original source.

Use APIs where available for better reliability and compliance.

## 🧩 TODO
 * Add support for more data sources

 * Integrate a triplet store for semantic search

 * Build a web dashboard or Streamlit UI

 * Implement daily email digests or Slack alerts

## 👥 Contributions
Open to feedback and collaboration! Please file an issue or submit a pull request with ideas or improvements.

## 📄 License
MIT License – see the LICENSE file for full details.
