import requests
from datetime import datetime, timezone, timedelta

from database.db import article_exists

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"

AI_KEYWORDS = [
    "ai", "artificial intelligence", "llm", "openai",
    "machine learning", "deep learning", "neural",
    "gpt", "claude", "gemini", "llama",
]


def is_ai_news(title):
    title = title.lower()
    return any(k in title for k in AI_KEYWORDS)


def is_posted_within_5_days(unix_time):
    if not unix_time:
        return False

    posted_time = datetime.fromtimestamp(unix_time, timezone.utc)
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=5)

    return posted_time >= cutoff_time


def fetch_ai_news(limit=5):
    story_ids = requests.get(HN_TOP_STORIES_URL, timeout=10).json()

    ai_stories = []

    for story_id in story_ids[:200]:
        story = requests.get(
            HN_ITEM_URL.format(item_id=story_id),
            timeout=10
        ).json()

        if not story or "title" not in story:
            continue

        title = story["title"]
        url = story.get(
            "url",
            f"https://news.ycombinator.com/item?id={story_id}"
        )

        if not is_posted_within_5_days(story.get("time")):
            continue

        if not is_ai_news(title):
            continue

        # ONLY dedupe here
        if article_exists(url):
            continue

        ai_stories.append(
            {
                "title": title,
                "url": url,
                "popularity": story.get("score", 0),
                "posted_at": story.get("time"),
                "storage_status": "New article",
            }
        )

        if len(ai_stories) >= limit:
            break

    return ai_stories