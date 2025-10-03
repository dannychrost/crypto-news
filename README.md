# Crypto News Bot

Containerized backend for storing crypto news from aggregators like CryptoPanic in PostgreSQL, and enabling a local Ollama llama3.1:8b model to generate meaningful analysis and summaries of current and past events in relation to price movements.

## Features

- 🔍 **News Aggregator**: Periodically fetches crypto news from the Crypto Panic API and stores key information in a PostgreSQL database through a scheduled backend process.
- 🗄️ **Database**: Uses Docker to set up and manage a PostgreSQL database container.
- 🌐 **API Endpoints**: Provides RESTful endpoints using FastAPI for accessing and querying the news data.
- 🤖 **Local LLM Integration**: A custom tool-calling setup (via `llm_comm.py`) allows the local LLM to access database information and generate meaningful analysis and summaries of current and past events. Manually needs to be started post setup along with having downloaded Ollama and llama3.1:8b model.

## Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
copy env.example .env

# Edit .env and add your credentials
# Replace placeholder values with your actual credentials
```

### 4. Get Crypto Panic API Key

1. Visit [Crypto Panic API](https://cryptopanic.com/developers/api/)
2. Sign up for a free Developer account
3. Retrieve your API key from the dashboard
4. Add it to your `.env` file

### 5. Start Containers

```bash
# Start PostgreSQL database, Uvicorn server, and background scheduler with Docker
docker-compose up -d

# Check if database is running
docker-compose ps
```
