
from pytrends.request import TrendReq
import json
import requests
import os
from datetime import datetime

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

pytrends = TrendReq(hl='en-US', tz=360)
now = datetime.utcnow().isoformat()

# Fallback to stable list if trending_searches fails
try:
    trending_searches_df = pytrends.trending_searches(pn='united_states')
except:
    trending_searches_df = pytrends.today_searches(pn='US')

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

for rank, row in trending_searches_df.iterrows():
    payload = {
        "trend_rank": rank + 1,
        "trendQuery": row[0],
        "searchVolume": "unknown",
        "articles": "[]",
        "scrapedAt": now,
        "category": "general"
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
