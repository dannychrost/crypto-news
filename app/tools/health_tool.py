"""Tool for checking API uptime and grabbing the server timestamp."""

import requests
from langchain_core.tools import tool

from app.config import API_BASE_URL


@tool
def get_health():
    """
    Return the /health JSON so the agent knows the service status and current time.
    """
    response = requests.get(f"{API_BASE_URL}/health", timeout=10)
    return response.json()
