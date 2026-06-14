import requests
from datetime import datetime, timezone, timedelta

from database.db import article_exists

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"

AI_KEYWORDS = [
    "ai",
    "artificial intelligence",
    "llm",
    "openai",
    "machine learning",
    "deep learning",
    "neural",
    "gpt",
    "claude",
    "gemini",
    "llama",
]


def is_ai_news(title):
    title = title.lower()
    return any(keyword in title for keyword in AI_KEYWORDS)


def is_recent_story(unix_time):
    if not unix_time:
        return False

    posted_time = datetime.fromtimestamp(unix_time, timezone.utc)
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

    return posted_time >= cutoff_time


def fetch_hacker_news_articles(limit=3):

    story_ids = requests.get(
        HN_TOP_STORIES_URL,
        timeout=10
    ).json()

    articles = []

    index = 0

    while len(articles) < limit and index < len(story_ids):

        story_id = story_ids[index]
        index += 1

        try:
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

            if not is_recent_story(story.get("time")):
                continue

            if not is_ai_news(title):
                continue

            if article_exists(url):
                continue

            articles.append(
                {
                    "title": title,
                    "url": url,
                    "source": "Hacker News",
                    "popularity": story.get("score", 0),
                    "posted_at": story.get("time"),
                    "storage_status": "New article",
                }
            )

        except Exception:
            continue

    return articles