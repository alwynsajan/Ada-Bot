import feedparser
from datetime import datetime, timezone, timedelta

from database.db import article_exists

REDDIT_RSS_FEEDS = [
    "https://www.reddit.com/r/artificial/.rss",
]


def is_recent_story(posted_datetime):
    if not posted_datetime:
        return False

    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

    return posted_datetime >= cutoff_time


def fetch_reddit_articles(limit=3):

    articles = []

    for rss_url in REDDIT_RSS_FEEDS:

        try:
            feed = feedparser.parse(rss_url)

            index = 0

            while (
                len(articles) < limit
                and index < len(feed.entries)
            ):

                entry = feed.entries[index]
                index += 1

                title = getattr(entry, "title", None)
                url = getattr(entry, "link", None)

                if not title or not url:
                    continue

                if hasattr(entry, "published_parsed"):

                    posted_time = datetime(
                        *entry.published_parsed[:6],
                        tzinfo=timezone.utc
                    )

                    if not is_recent_story(posted_time):
                        continue

                if article_exists(url):
                    continue

                articles.append(
                    {
                        "title": title,
                        "url": url,
                        "source": "Reddit r/artificial",
                        "popularity": 0,
                        "posted_at": (
                            posted_time.isoformat()
                            if hasattr(
                                entry,
                                "published_parsed"
                            )
                            else None
                        ),
                        "storage_status": "New article",
                    }
                )

        except Exception as e:

            print(
                f"Reddit RSS error: {e}",
                flush=True
            )

    return articles