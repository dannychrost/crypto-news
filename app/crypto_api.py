"""
Crypto Panic API integration
"""
import os
import requests
from fastapi import HTTPException


def fetch_crypto_news(filter_type: str = "hot", currencies: str = "BTC,ETH", kind: str = "news") -> list:
    """Fetch news from Crypto Panic API"""
    api_key = os.getenv('CRYPTO_PANIC_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        raise HTTPException(status_code=400, detail="CRYPTO_PANIC_API_KEY not set in .env file")
    
    # API request
    url = "https://cryptopanic.com/api/developer/v2/posts/"
    params = {
        'auth_token': api_key,
        'public': 'true',
        'filter': filter_type, # rising, hot, bullish, bearish, important, saved, lol (optional)
        'currencies': currencies, # BTC, ETH, XRP, ADA, DOGE, SOL, DOT, LTC, USDT, BNB (optional)
        'kind': kind # news, media, all (optional)
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = data.get('results', [])
        
        return results
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")