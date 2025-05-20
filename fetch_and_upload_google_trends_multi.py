
from pytrends.request import TrendReq
import json
import requests
import os
from datetime import datetime

# Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize pytrends session
pytrends = TrendReq(hl='en-US', tz=360)
fallback_keywords = ["USA", "news", "election", "weather", "sports", "economy"]

rising_queries = None

# Try each keyword until we get a valid response
for keyword in fallback_keywords:
    try:
        pytrends.build_payload([keyword], cat=0, timeframe='now 1-d', geo='US')
        related = pytrends.related_queries()
        rising = related.get(keyword, {}).get("rising", None)

        if rising is not None and not rising.empty:
            rising_queries = rising
            print(f"✅ Using seed keyword: {keyword}")
            break
    except Exception as e:
        print(f"⚠️ Failed for keyword '{keyword}': {e}")
        continue

# Exit if none returned data
if rising_queries is None:
    print("❌ No rising queries found from fallback list.")
    exit(1)

# Timestamp for insertion
now = datetime.utcnow().isoformat()
headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Send top 20 rising queries to Supabase
for i, row in rising_queries.head(20).iterrows():
    payload = {
        "trend_rank": i + 1,
        "trendQuery": row['query'],
        "searchVolume": str(row['value']),
        "articles": "[]",
        "scrapedAt": now,
        "category": "rising"
    }

    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/trending_topics",
        headers=headers,
        json=payload
    )

    if response.status_code not in [200, 201]:
        print(f"❌ Failed: {payload['trendQuery']} – {response.status_code} {response.text}")
    else:
        print(f"✅ Inserted: {payload['trendQuery']}")
