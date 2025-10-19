"""Tool for pulling time-bounded news rows from the API backend."""

import requests
from langchain_core.tools import tool

from app.config import API_BASE_URL


@tool
def get_db_news(start_date: str, end_date: str):
    """
    Hit the news endpoint so the agent can summarise rows already stored in our DB.
    """
    response = requests.get(
        f"{API_BASE_URL}/api/v1/news",
        params={"start": start_date, "end": end_date},
        timeout=15,
    )
    return response.json()
