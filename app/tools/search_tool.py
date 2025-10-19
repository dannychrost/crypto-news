"""Tool wrapper for Tavily web search plus lightweight logging."""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from langchain_core.tools import tool

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
LOG_PATH = Path("logs/web_search.log")


def _format_error(message: str) -> Dict[str, Any]:
    """Return a standard error payload for the agent."""
    return {"success": False, "message": message, "results": []}


def _write_log(entry: str) -> None:
    """Append a timestamped line to the search log (creates folders on demand)."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {entry}\n")


@tool
def search_web(query: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Call the Tavily Search API for the given query and return trimmed results.
    """
    if not query:
        return _format_error("Query must not be empty.")

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return _format_error("TAVILY_API_KEY is not configured.")

    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max(1, min(max_results, 10)),
        "search_depth": "advanced",
        "include_answer": True,
        "include_images": False,
        "include_raw_content": True,
    }

    try:
        response = requests.post(TAVILY_SEARCH_URL, json=payload, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        error_message = f"Tavily request failed: {exc}"
        _write_log(f"ERROR query={query!r} msg={error_message}")
        return _format_error(error_message)

    data: Dict[str, Any] = response.json()
    results = data.get("results", [])

    if not results:
        _write_log(f"NO_RESULTS query={query!r}")
        return {"success": True, "message": "No external results found.", "results": []}

    formatted_results: List[Dict[str, Any]] = []
    for item in results:
        raw_content = (
            item.get("raw_content")
            or item.get("content")
            or item.get("snippet")
            or ""
        )
        # Strip markdown links and compress whitespace so the agent has readable text.
        snippet = re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", raw_content)
        snippet = re.sub(r"\s+", " ", snippet).strip()
        if len(snippet) > 400:
            snippet = snippet[:397].rstrip() + "..."

        formatted_results.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": snippet,
                "published_date": item.get("published_date"),
            }
        )

    log_summary = "; ".join(
        f"title={entry['title']!r} url={entry['url']!r}" for entry in formatted_results
    )
    _write_log(f"SUCCESS query={query!r} answer={data.get('answer')!r} results={log_summary}")

    return {
        "success": True,
        "message": data.get("answer") or "Search completed.",
        "results": formatted_results,
    }
