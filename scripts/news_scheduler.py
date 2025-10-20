import time
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

API_URL = "http://app:8000/api/v1/fetch"

# You can adjust these parameters as needed
FETCH_PARAMS = {
    "filter": "hot",         # rising, newest, hot, bullish, bearish, important, saved, lol (optional)
    "currencies": "BTC,ETH", # BTC, ETH, XRP, ADA, DOGE, SOL, DOT, LTC, USDT, BNB (optional)
    "kind": "news"           # news, media, all (optional)
}

FETCH_INTERVAL_SECONDS = 60 * 60 * 24 # 1 day

def fetch_and_store_news():
    try:
        logging.info("Fetching news from API endpoint...")
        response = requests.post(API_URL, json=FETCH_PARAMS)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                logging.info(f"✅ News fetched and saved. Items retrieved: {data.get('items_retrieved', 0)}")
            else:
                logging.warning(f"⚠️ News fetch failed: {data.get('message')}")
        else:
            logging.error(f"❌ API call failed with status {response.status_code}: {response.text}")
    except Exception as e:
        logging.error(f"❌ Exception during fetch: {e}")

if __name__ == "__main__":
    logging.info("Starting scheduled news fetcher (every 1 day)...")
    while True:
        fetch_and_store_news()
        logging.info(f"Sleeping for {FETCH_INTERVAL_SECONDS // 60} minutes...")
        time.sleep(FETCH_INTERVAL_SECONDS)
