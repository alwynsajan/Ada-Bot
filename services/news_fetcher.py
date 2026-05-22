import requests

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


def fetch_ai_news(limit=5):
    story_ids = requests.get(HN_TOP_STORIES_URL, timeout=10).json()

    ai_stories = []

    for story_id in story_ids[:200]:
        response = requests.get(HN_ITEM_URL.format(item_id=story_id), timeout=10)
        story = response.json()

        if not story or "title" not in story:
            continue

        title = story["title"]
        url = story.get("url", f"https://news.ycombinator.com/item?id={story_id}")

        if article_exists(url):
            continue

        if is_ai_news(title):
            ai_stories.append(
                {
                    "title": title,
                    "url": url,
                    "score": story.get("score", 0),
                }
            )

        if len(ai_stories) >= limit:
            break

    return ai_stories