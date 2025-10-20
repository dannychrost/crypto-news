import os
import sys
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import json


# Load environment variables and define globals
load_dotenv()
BASE_URL = "https://pro-api.coinmarketcap.com"
CMC_API_KEY = (
    os.getenv("CMC_API_KEY")
)
HEADERS = {"X-CMC_PRO_API_KEY": CMC_API_KEY} if CMC_API_KEY else {}


 
def test_fear_and_greed() -> dict | None:
    """Call v3/fear-and-greed/historical for the last 30 days. No JSON parsing."""
    url = f"{BASE_URL}/v3/fear-and-greed/historical"
    end = datetime.utcnow().replace(microsecond=0)
    start = end - timedelta(days=30)
    params = {
        "start": 1,   # integer >= 1, default = 1 → index of first record (1 = most recent)
        "limit": 30   # integer range [1..500], default = 50 → number of records to return
        }
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        print(f"GET /v3/fear-and-greed/historical -> {resp.status_code}")
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"Error calling fear-and-greed/historical: {e}")
        return None


def main() -> int:
    if not CMC_API_KEY:
        print("Missing CoinMarketCap API key. Set CMC_API_KEY or COINMARKETCAP_API_KEY.")
        return 1
 
    ok_fng = test_fear_and_greed()
    # output to json file
    with open("cmc_api_test.json", "w") as f:
        json.dump({"ok_fng": ok_fng}, f)
    return 0 if ok_fng else 1


if __name__ == "__main__":
    sys.exit(main())
