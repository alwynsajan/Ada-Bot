# Ada-Bot

Ada is an AI-powered Discord news assistant that fetches trending AI news, stores article embeddings, and answers user questions using Retrieval-Augmented Generation (RAG). The bot uses semantic search to retrieve relevant article content and generates grounded responses using Groq-hosted LLMs.

---

# Features

- Fetches trending AI news from Hacker News
- AI-generated summaries for fetched articles
- Discord mention-based interaction
- LangGraph workflow routing
- Full webpage scraping for article ingestion
- Semantic chunking and embedding generation
- SQLite-based knowledge storage
- RAG-powered question answering
- Semantic similarity search using cosine similarity
- Duplicate article prevention
- General conversational support

---

# Architecture

```text
HackerNews API
        ↓
Fetch AI News Metadata
        ↓
Scrape Full Webpage Content
        ↓
Chunk Article Text
        ↓
Generate Embeddings
        ↓
Store in SQLite
        ↓
User asks question
        ↓
Generate Query Embedding
        ↓
Cosine Similarity Search
        ↓
Retrieve Relevant Chunks
        ↓
Groq generates grounded response
```

---

# Tech Stack

| Component | Technology |
|---|---|
| Bot Framework | discord.py |
| Workflow Orchestration | LangGraph |
| LLM | Groq (Llama 3) |
| Embeddings | sentence-transformers |
| Vector Search | cosine similarity + NumPy |
| Database | SQLite |
| Web Scraping | BeautifulSoup |
| Hosting | Docker / Railway / Oracle Cloud |

---

# Project Structure

```text
Ada-Bot/
│
├── main.py
├── config.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
│
├── services/
│   ├── ada_graph.py
│   ├── llm.py
│   ├── news_fetcher.py
│   ├── scraper.py
│   ├── embeddings.py
│   └── rag.py
│
├── database/
│   └── db.py
│
└── data/
    └── ada.sqlite
```

---

# Workflow Overview

## 1. News Fetching

Ada fetches trending stories from the Hacker News API. The API returns story IDs, and Ada retrieves article metadata such as titles, URLs, and popularity scores. AI-related stories are identified using keyword filtering.

The Hacker News score represents the popularity and engagement level of the article on Hacker News.

---

# 2. Webpage Scraping

After retrieving article URLs, Ada scrapes the full webpage content using BeautifulSoup. The scraper removes unnecessary webpage elements such as scripts, navigation bars, headers, and advertisements to extract meaningful article text.

This scraped content becomes the knowledge source for the RAG pipeline.

---

# 3. Text Chunking

Large articles are split into smaller overlapping chunks before embedding generation. Chunking improves semantic retrieval accuracy and allows Ada to retrieve only the most relevant parts of an article during question answering.

Overlapping chunks help preserve context between chunk boundaries.

---

# 4. Embedding Generation

Each chunk is converted into a semantic vector using the SentenceTransformers model:

- all-MiniLM-L6-v2

The model generates dense vector embeddings representing the semantic meaning of the chunk rather than relying on exact keyword matching.

Semantically similar sentences produce embeddings that are close together in vector space even if different wording is used.

For example:

- “Llama 4 improves reasoning”
- “Meta enhanced reasoning performance”

Both produce similar embeddings because they convey similar meaning.

Embeddings are stored as JSON arrays inside SQLite.

---

# 5. Database Storage

Ada stores:
- article metadata
- summaries
- chunk text
- embeddings
- timestamps

The SQLite database contains:
- an articles table for article information
- a chunks table for semantic chunk storage

Duplicate articles are prevented using URL-based checks before ingestion.

This ensures previously fetched articles are not processed again during future fetch cycles.

---

# 6. Semantic Search

When a user asks a question, Ada converts the question into an embedding using the same embedding model used during ingestion.

The query embedding is then compared against all stored chunk embeddings using cosine similarity.

Cosine similarity measures how semantically close two vectors are. Higher similarity scores indicate more relevant chunks.

Ada retrieves the highest-scoring chunks and uses them as context for response generation.

---

# 7. RAG Answer Generation

The top matching chunks are passed to Groq as contextual knowledge. Groq then generates a grounded response based only on the retrieved article information.

This allows Ada to answer questions about recently fetched news rather than relying solely on pretrained model knowledge.

Responses can also include source references to the original articles.

---

# LangGraph Workflow

Ada uses LangGraph to dynamically route requests between workflows.

Current workflows include:
- fetch_news
- answer_question
- general_chat

Examples:

- Asking for AI news routes to the news ingestion workflow.
- Asking questions about stored articles routes to the RAG workflow.
- Greetings and casual conversation route to general chat handling.

This modular workflow architecture makes the bot scalable and easier to extend with future features.

---

# Running the Project

## Environment Variables

Create a `.env` file with:
- Discord bot token
- Groq API key
- Groq model configuration

---

# Docker

The project supports Docker-based deployment and development environments.

---

# Example Usage

## Fetch AI news

```text
@Ada latest AI news
```

## Ask RAG-based question

```text
@Ada what improvements did Meta mention?
```

## General conversation

```text
@Ada hi
```

---

# Future Improvements

- Scheduled automatic news ingestion
- Multi-source news aggregation
- Article reranking
- Vector database integration
- Thread-based Discord discussions
- Personalized news feeds
- Sentiment analysis
- FAISS / pgvector support
- Advanced retrieval pipelines

---

# License

MIT License