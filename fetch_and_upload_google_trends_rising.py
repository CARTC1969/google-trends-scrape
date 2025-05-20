
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

# Use a generic topic to extract reliable trending queries
keyword_seed = "USA"
pytrends.build_payload([keyword_seed], cat=0, timeframe='now 1-d', geo='US', gprop='')

# Get related rising queries
related_queries = pytrends.related_queries()
rising_queries = related_queries.get(keyword_seed, {}).get("rising", None)

if not rising_queries or rising_queries.empty:
    print("❌ No rising queries found.")
    exit(1)

# Timestamp for insertion
now = datetime.utcnow().isoformat()
headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# Send top rising queries to Supabase
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
