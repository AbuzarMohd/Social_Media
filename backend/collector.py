import requests, datetime as dt, os
from typing import List, Dict, Any
from config import get_settings
from backend.utils import log

TWITTER_URL = "https://api.twitter.com/2/tweets/search/recent"
REDDIT_URL = "https://www.reddit.com/user/{username}/submitted.json?limit={limit}"


def _fetch_twitter(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    cfg = get_settings()
    if not cfg["TWITTER_BEARER"]:
        log("Twitter token missing – returning demo data.")
        from data.sample_tweets import demo_tweets
        return demo_tweets[:limit]

    query = f"from:{username} -is:retweet -is:reply"
    headers = {"Authorization": f"Bearer {cfg['TWITTER_BEARER']}"}
    params = {
        "query": query,
        "max_results": min(limit, 100),
        "tweet.fields": "created_at,text",
    }
    r = requests.get(TWITTER_URL, headers=headers, params=params, timeout=10)
    r.raise_for_status()
    tweets = r.json().get("data", [])
    return [{"id": t["id"], "time": t["created_at"], "text": t["text"]} for t in tweets]


def _fetch_reddit(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    url = REDDIT_URL.format(username=username, limit=limit)
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    if r.status_code != 200:
        log("Reddit fetch failed – returning demo data.")
        from data.sample_tweets import demo_tweets
        return demo_tweets[:limit]
    j = r.json()
    posts = j["data"]["children"]
    return [
        {
            "id": p["data"]["id"],
            "time": dt.datetime.fromtimestamp(p["data"]["created_utc"]).isoformat(),
            "text": p["data"]["selftext"][:280] or p["data"]["title"],
        }
        for p in posts
    ]


def get_recent_posts(username: str, platform: str, limit: int = 100):
    if platform == "Twitter":
        return _fetch_twitter(username, limit)
    return _fetch_reddit(username, limit)