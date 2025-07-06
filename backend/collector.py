'''
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
    '''

'''
"""Fetch recent posts from Twitter or Reddit with graceful fallback and rate‑limit handling."""
import requests, datetime as dt
from typing import List, Dict, Any
from config import get_settings
from backend.utils import log

TWITTER_URL = "https://api.twitter.com/2/tweets/search/recent"
REDDIT_URL = "https://www.reddit.com/user/{username}/submitted.json?limit={limit}"

# Handy helper to return demo data if live fetch fails
def _demo(limit):
    from data.sample_tweets import demo_tweets
    return demo_tweets[:limit]


def _fetch_twitter(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get up to `limit` recent tweets by @username.

    Uses the v2 Recent Search endpoint. Falls back to demo data if:
    * Twitter bearer token is missing
    * HTTP 4xx/5xx errors occur (incl. 429 rate limit)
    """
    cfg = get_settings()

    if not cfg["TWITTER_BEARER"]:
        log("[Twitter] Bearer token missing – using sample tweets.")
        return _demo(limit)

    query = f"from:{username} -is:retweet -is:reply"
    headers = {"Authorization": f"Bearer {cfg['TWITTER_BEARER']}"}
    params = {
        "query": query,
        "max_results": min(limit, 100),
        "tweet.fields": "created_at,text",
    }

    try:
        r = requests.get(TWITTER_URL, headers=headers, params=params, timeout=10)
        if r.status_code == 429:
            log("[Twitter] Rate limit hit (HTTP 429). Using sample data.")
            return _demo(limit)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        log(f"[Twitter] API error: {e}. Using sample data.")
        return _demo(limit)

    tweets = r.json().get("data", [])
    if not tweets:
        log("[Twitter] No tweets found – using sample data.")
        return _demo(limit)

    return [{"id": t["id"], "time": t["created_at"], "text": t["text"]} for t in tweets]


def _fetch_reddit(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    url = REDDIT_URL.format(username=username, limit=limit)
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        log(f"[Reddit] API error: {e}. Using sample data.")
        return _demo(limit)

    j = r.json()
    posts = j.get("data", {}).get("children", [])
    if not posts:
        log("[Reddit] No posts found – using sample data.")
        return _demo(limit)

    return [
        {
            "id": p["data"].get("id"),
            "time": dt.datetime.fromtimestamp(p["data"].get("created_utc", 0)).isoformat(),
            "text": (p["data"].get("selftext") or p["data"].get("title", ""))[:280],
        }
        for p in posts
    ]


def get_recent_posts(username: str, platform: str, limit: int = 100):
    if platform == "Twitter":
        return _fetch_twitter(username, limit)
    return _fetch_reddit(username, limit)
'''

'''
"""Fetch recent posts from Twitter or Reddit with graceful fallback and rate‑limit handling."""
import requests, datetime as dt
from typing import List, Dict, Any
from config import get_settings
from backend.utils import log

TWITTER_URL = "https://api.twitter.com/2/tweets/search/recent"
REDDIT_URL = "https://www.reddit.com/user/{username}/submitted.json?limit={limit}"

# Handy helper to return demo data if live fetch fails
def _demo(limit):
    import json, pathlib
    json_path = pathlib.Path(__file__).parent.parent / "data" / "sample_tweets.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tweets = json.load(f)
    except Exception as e:
        log(f"[Demo] Could not load sample_tweets.json: {e}")
        tweets = []
    return tweets[:limit]


def _fetch_twitter(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get up to `limit` recent tweets by @username.

    Uses the v2 Recent Search endpoint. Falls back to demo data if:
    * Twitter bearer token is missing
    * HTTP 4xx/5xx errors occur (incl. 429 rate limit)
    """
    cfg = get_settings()

    if not cfg["TWITTER_BEARER"]:
        log("[Twitter] Bearer token missing – using sample tweets.")
        return _demo(limit)

    query = f"from:{username} -is:retweet -is:reply"
    headers = {"Authorization": f"Bearer {cfg['TWITTER_BEARER']}"}
    params = {
        "query": query,
        "max_results": min(limit, 100),
        "tweet.fields": "created_at,text",
    }

    try:
        r = requests.get(TWITTER_URL, headers=headers, params=params, timeout=10)
        if r.status_code == 429:
            log("[Twitter] Rate limit hit (HTTP 429). Using sample data.")
            return _demo(limit)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        log(f"[Twitter] API error: {e}. Using sample data.")
        return _demo(limit)

    tweets = r.json().get("data", [])
    if not tweets:
        log("[Twitter] No tweets found – using sample data.")
        return _demo(limit)

    return [{"id": t["id"], "time": t["created_at"], "text": t["text"]} for t in tweets]


def _fetch_reddit(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    url = REDDIT_URL.format(username=username, limit=limit)
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        log(f"[Reddit] API error: {e}. Using sample data.")
        return _demo(limit)

    j = r.json()
    posts = j.get("data", {}).get("children", [])
    if not posts:
        log("[Reddit] No posts found – using sample data.")
        return _demo(limit)

    return [
        {
            "id": p["data"].get("id"),
            "time": dt.datetime.fromtimestamp(p["data"].get("created_utc", 0)).isoformat(),
            "text": (p["data"].get("selftext") or p["data"].get("title", ""))[:280],
        }
        for p in posts
    ]


def get_recent_posts(username: str, platform: str, limit: int = 100):
    if platform == "Twitter":
        return _fetch_twitter(username, limit)
    return _fetch_reddit(username, limit)
'''

'''

"""Fetch recent posts from Twitter or Reddit with graceful fallback and rate‑limit handling."""
import requests, datetime as dt
from typing import List, Dict, Any
from config import get_settings
from backend.utils import log

TWITTER_URL = "https://api.twitter.com/2/tweets/search/recent"
REDDIT_URL = "https://www.reddit.com/user/{username}/submitted.json?limit={limit}"

# Handy helper to return demo data if live fetch fails
def _demo(limit):
    import json, pathlib
    json_path = pathlib.Path(__file__).parent.parent / "data" / "sample_tweets.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tweets = json.load(f)
    except Exception as e:
        log(f"[Demo] Could not load sample_tweets.json: {e}")
        tweets = []
    return tweets[:limit]


def _fetch_twitter(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get up to `limit` recent tweets by @username.

    Uses the v2 Recent Search endpoint. Falls back to demo data if:
    * Twitter bearer token is missing
    * HTTP 4xx/5xx errors occur (incl. 429 rate limit)
    """
    cfg = get_settings()

    if not cfg["TWITTER_BEARER"]:
        log("[Twitter] Bearer token missing – using sample tweets.")
        return _demo(limit)

    query = f"from:{username} -is:retweet -is:reply"
    headers = {"Authorization": f"Bearer {cfg['TWITTER_BEARER']}"}
    params = {
        "query": query,
        "max_results": min(limit, 100),
        "tweet.fields": "created_at,text",
    }

    try:
        r = requests.get(TWITTER_URL, headers=headers, params=params, timeout=10)
        if r.status_code == 429:
            log("[Twitter] Rate limit hit (HTTP 429). Using sample data.")
            return _demo(limit)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        log(f"[Twitter] API error: {e}. Using sample data.")
        return _demo(limit)

    tweets = r.json().get("data", [])
    if not tweets:
        log("[Twitter] No tweets found – using sample data.")
        return _demo(limit)

    return [{"id": t["id"], "time": t["created_at"], "text": t["text"]} for t in tweets]


def _fetch_reddit(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch recent Reddit submissions from a user.

    Tries the native Reddit JSON endpoint first. If that returns 403 (often due to
    bot blocking), falls back to the public **Pushshift** API which is more
    tolerant of server‑side rate limits.
    """
    # 1️⃣ Native Reddit endpoint
    url = REDDIT_URL.format(username=username, limit=limit)
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; MHMonitor/1.0)"}, timeout=10)
        if r.status_code == 403:
            raise requests.exceptions.HTTPError("403 – blocked by Reddit", response=r)
        r.raise_for_status()
        j = r.json()
        posts = j.get("data", {}).get("children", [])
        if posts:
            return [
                {
                    "id": p["data"].get("id"),
                    "time": dt.datetime.fromtimestamp(p["data"].get("created_utc", 0)).isoformat(),
                    "text": (p["data"].get("selftext") or p["data"].get("title", ""))[:280],
                }
                for p in posts
            ][:limit]
    except requests.exceptions.RequestException as e:
        log(f"[Reddit] Native endpoint error: {e}. Trying Pushshift …")

    # 2️⃣ Pushshift fallback
    ps_url = f"https://api.pushshift.io/reddit/search/submission/?author={username}&size={limit}&sort=desc"
    try:
        r = requests.get(ps_url, timeout=10)
        r.raise_for_status()
        posts = r.json().get("data", [])
        if posts:
            return [
                {
                    "id": p.get("id"),
                    "time": dt.datetime.fromtimestamp(p.get("created_utc", 0)).isoformat(),
                    "text": (p.get("selftext") or p.get("title", ""))[:280],
                }
                for p in posts
            ][:limit]
    except requests.exceptions.RequestException as e:
        log(f"[Reddit] Pushshift error: {e}. Using sample data.")

    # 3️⃣ Fallback to demo data
    return _demo(limit)

    j = r.json()
    posts = j.get("data", {}).get("children", [])
    if not posts:
        log("[Reddit] No posts found – using sample data.")
        return _demo(limit)

    return [
        {
            "id": p["data"].get("id"),
            "time": dt.datetime.fromtimestamp(p["data"].get("created_utc", 0)).isoformat(),
            "text": (p["data"].get("selftext") or p["data"].get("title", ""))[:280],
        }
        for p in posts
    ]


def get_recent_posts(username: str, platform: str, limit: int = 100):
    if platform == "Twitter":
        return _fetch_twitter(username, limit)
    return _fetch_reddit(username, limit)
'''
#using praw method
"""Fetch recent posts from Twitter or Reddit with graceful fallback and rate-limit handling."""
import requests, datetime as dt
from typing import List, Dict, Any
from config import get_settings
from backend.utils import log

TWITTER_URL = "https://api.twitter.com/2/tweets/search/recent"

def _demo(limit):
    import json, pathlib
    json_path = pathlib.Path(__file__).parent.parent / "data" / "sample_tweets.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tweets = json.load(f)
    except Exception as e:
        log(f"[Demo] Could not load sample_tweets.json: {e}")
        tweets = []
    return tweets[:limit]


def _fetch_twitter(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    cfg = get_settings()

    if not cfg["TWITTER_BEARER"]:
        log("[Twitter] Bearer token missing – using sample tweets.")
        return _demo(limit)

    query = f"from:{username} -is:retweet -is:reply"
    headers = {"Authorization": f"Bearer {cfg['TWITTER_BEARER']}"}
    params = {
        "query": query,
        "max_results": min(limit, 100),
        "tweet.fields": "created_at,text",
    }

    try:
        r = requests.get(TWITTER_URL, headers=headers, params=params, timeout=10)
        if r.status_code == 429:
            log("[Twitter] Rate limit hit (HTTP 429). Using sample data.")
            return _demo(limit)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        log(f"[Twitter] API error: {e}. Using sample data.")
        return _demo(limit)

    tweets = r.json().get("data", [])
    if not tweets:
        log("[Twitter] No tweets found – using sample data.")
        return _demo(limit)

    return [{"id": t["id"], "time": t["created_at"], "text": t["text"]} for t in tweets]


def _fetch_reddit(username: str, limit: int = 100) -> List[Dict[str, Any]]:
    import praw

    cfg = get_settings()
    try:
        reddit = praw.Reddit(
            client_id=cfg["REDDIT_CLIENT_ID"],
            client_secret=cfg["REDDIT_CLIENT_SECRET"],
            user_agent=cfg["REDDIT_USER_AGENT"]
        )
        user = reddit.redditor(username)
        posts = []
        for submission in user.submissions.new(limit=limit):
            posts.append({
                "id": submission.id,
                "time": dt.datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                "text": (submission.selftext or submission.title)[:280],
            })
        if not posts:
            log("[Reddit] No posts found – using sample data.")
            return _demo(limit)
        return posts
    except Exception as e:
        log(f"[Reddit] PRAW error: {e} – using sample data.")
        return _demo(limit)


def get_recent_posts(username: str, platform: str, limit: int = 100):
    if platform == "Twitter":
        return _fetch_twitter(username, limit)
    return _fetch_reddit(username, limit)
