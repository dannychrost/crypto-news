"""
Pydantic models for Crypto News API
"""
from pydantic import BaseModel
from typing import List, Optional


class NewsItem(BaseModel):
    """Model for a single news item"""
    id: int
    slug: str
    title: str
    description: str
    published_at: str
    created_at: str
    kind: str


class FetchRequest(BaseModel):
    """Request model for fetching news"""
    filter: str = "hot"
    currencies: str = "BTC,ETH"
    kind: str = "news"


class FetchResponse(BaseModel):
    """Response model for fetch endpoints"""
    success: bool
    message: str
    items_retrieved: int
    items_saved: int
    data: Optional[List[NewsItem]] = None


class NewsQueryResponse(BaseModel):
    """Response model for database news queries"""
    success: bool
    message: str
    items_retrieved: int
    data: Optional[List[NewsItem]] = None