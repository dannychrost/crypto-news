# Crypto News Bot

Tool-powered assistant for exploring recent cryptocurrency headlines. The stack combines a FastAPI backend (for stored news + health checks), LangChain agents, and OpenAI chat models with optional Tavily web search.

## What It Does

- **Scheduled ingestion** – Pulls crypto stories into PostgreSQL so the agent can answer questions from local history.
- **Agent-ready API** – FastAPI exposes `/api/v1/news` and `/health`, which the assistant uses through LangChain tools.
- **OpenAI + LangChain** – `scripts/openai_comm.py` spins up an interactive CLI agent that routes between the database, health check, and a Tavily-backed web search tool.
- **Web search logging** – Every Tavily lookup gets summarized, cleaned, and written to `logs/web_search.log` for traceability.

## Getting Started

### 1. Environment

```powershell
python -m venv venv
.\venv\Scripts\activate      # Windows
# source venv/bin/activate   # macOS/Linux
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure `.env`

Copy `env.example` to `.env` and set:

- `API_BASE_URL` – URL for the FastAPI service (defaults to `http://localhost:8000`).
- `OPENAI_API_KEY` – key for OpenAI’s API.
- `TAVILY_API_KEY` – key for Tavily web search.
- Any other keys used by your ingestion jobs (e.g., CryptoPanic).

### 4. Run the Backend

```powershell
docker compose up -d     # PostgreSQL + FastAPI stack
docker compose ps        # confirm services are healthy
```

### 5. Launch the Agent CLI

```powershell
python -m scripts.openai_comm
```

Sample prompts:

- `what's up with crypto this week?`
- `find the latest Dogecoin news from the web`
- `why did ETH drop yesterday?`

Each turn prints token usage; when the agent calls Tavily, results are also appended to `logs/web_search.log`.

### 6. Explore the Atlas UI Prototype

A TypeScript proof-of-concept lives in `atlas-ui/`. It sketches the “command deck” interface with mock data.

```powershell
cd atlas-ui
npm install
npm run dev
```

Head to http://localhost:5174 to explore the interactive dashboard.

## Files to Know

- `scripts/openai_comm.py` – interactive chat loop for the OpenAI-powered LangChain agent.
- `app/tools/*` – LangChain tools: database news, server health, and Tavily search (with logging).
- `app/prompts/crypto_news_prompt.py` – system prompt guiding tool usage and response style.
- `logs/web_search.log` – plain-text record of every web search query and the URLs returned.
- `atlas-ui/` – React + TypeScript proof-of-concept for the Atlas command deck experience.

## Legacy Ollama Flow

The repo originally included an Ollama-based CLI (`scripts/llm_comm.py`). It’s kept in `scripts/archive/` for reference, but the supported path is now OpenAI + Tavily.

## Contributing

Pull requests are welcome—please keep comments concise and stick to ASCII to avoid platform encoding issues. For big changes (new tools, prompt tweaks), update the README so the workflow stays clear.
