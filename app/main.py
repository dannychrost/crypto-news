"""
Crypto News API - Main FastAPI Application

This application provides endpoints for fetching, storing, and retrieving cryptocurrency news
using the Crypto Panic API and PostgreSQL database.
"""

import json
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
import uvicorn

from .models import NewsItem, FetchRequest, FetchResponse, NewsQueryResponse
from .database import save_to_database, get_news_from_database
from .crypto_api import fetch_crypto_news

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Crypto News AI API",
    description="AI-powered cryptocurrency news analysis and data extraction",
    version="1.0.0"
)


def fetch_and_save_news(filter_type: str, currencies: str, kind: str):
    """Background task to fetch and save news"""
    try:
        results = fetch_crypto_news(filter_type, currencies, kind)
        save_to_database(results)
        print(f"✅ Background fetch completed: {len(results)} items")
    except Exception as e:
        print(f"❌ Background fetch failed: {e}")


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Crypto News AI API",
        "version": "1.0.0",
        "endpoints": {
            "fetch": "/api/v1/fetch",
            "health": "/health",
            "docs": "/docs",
            "news_from_db": "/api/v1/news"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }


@app.post("/api/v1/fetch", response_model=FetchResponse)
async def fetch_news(request: FetchRequest):
    """
    Fetch crypto news from Crypto Panic API and store in database
    
    - **filter**: News filter (hot, rising, bullish, bearish, important, saved, lol)
    - **currencies**: Comma-separated currency codes (e.g., BTC,ETH)
    - **kind**: Content type (news, media, all)
    """
    try:
        # Fetch news from API
        results = fetch_crypto_news(
            filter_type=request.filter,
            currencies=request.currencies,
            kind=request.kind
        )
        
        if not results:
            return FetchResponse(
                success=False,
                message="No news items retrieved from API",
                items_retrieved=0,
                items_saved=0
            )
        
        # Save to database
        db_success = save_to_database(results)
        
        # Save raw data to JSON file (in data directory)
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        with open(os.path.join(data_dir, "crypto_news_data.json"), "w", encoding="utf-8") as f:
            json.dump({"results": results}, f, ensure_ascii=False, indent=2)
        
        # Convert to Pydantic models for response
        news_items = [NewsItem(**item) for item in results]
        
        return FetchResponse(
            success=db_success,
            message="News fetched and saved successfully" if db_success else "News fetched but database save failed",
            items_retrieved=len(results),
            items_saved=len(results) if db_success else 0,
            data=news_items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/api/v1/fetch", response_model=FetchResponse)
async def fetch_news_get(
    filter: str = "hot",
    currencies: str = "BTC,ETH", 
    kind: str = "news"
):
    """GET version of fetch endpoint for simple requests"""
    request = FetchRequest(filter=filter, currencies=currencies, kind=kind)
    return await fetch_news(request)


@app.post("/api/v1/fetch/background")
async def fetch_news_background(
    request: FetchRequest,
    background_tasks: BackgroundTasks
):
    """Fetch news in background (non-blocking)"""
    background_tasks.add_task(
        fetch_and_save_news,
        request.filter,
        request.currencies,
        request.kind
    )
    
    return {
        "message": "News fetch started in background",
        "status": "processing"
    }


@app.get("/api/v1/news", response_model=NewsQueryResponse)
async def get_news(
    start: Optional[str] = Query(
        None,
        description="Start timestamp (inclusive) in ISO8601 format, e.g. 2024-06-01T00:00:00"
    ),
    end: Optional[str] = Query(
        None,
        description="End timestamp (inclusive) in ISO8601 format, e.g. 2024-06-30T23:59:59"
    )
):
    """
    Fetch crypto news directly from the database.
    Optionally filter by published_at between start and end timestamps (ISO8601).
    """
    try:
        news_items = get_news_from_database(start, end)
        return NewsQueryResponse(
            success=True,
            message="News items retrieved from database",
            items_retrieved=len(news_items),
            data=[NewsItem(**item) for item in news_items]
        )
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting Crypto News AI API Server")
    print("📖 API Documentation available at: http://localhost:8000/docs")
    print("🔍 Health check available at: http://localhost:8000/health")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )