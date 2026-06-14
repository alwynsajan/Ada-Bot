from concurrent.futures import ThreadPoolExecutor

from services.news_sources.hacker_news import (
    fetch_hacker_news_articles
)

from services.news_sources.reddit import (
    fetch_reddit_articles
)


def fetch_ai_news(limit=5):

    with ThreadPoolExecutor(max_workers=2) as executor:

        hn_future = executor.submit(
            fetch_hacker_news_articles
        )

        reddit_future = executor.submit(
            fetch_reddit_articles
        )

        hacker_news_articles = hn_future.result()
        reddit_articles = reddit_future.result()

        print(f"Fetched {len(hacker_news_articles)} articles from Hacker News",flush=True)
        print(f"Fetched {len(reddit_articles)} articles from Reddit",flush=True)

    source_groups = {
        "Hacker News": hacker_news_articles,
        "Reddit": reddit_articles,
    }

    selected_articles = []
    remaining_articles = []
    selected_urls = set()

    # Take best article from each source first
    for articles in source_groups.values():

        if articles:

            article = articles[0]

            selected_articles.append(article)

            selected_urls.add(article["url"])

            remaining_articles.extend(
                articles[1:]
            )

    # Rank remaining by popularity
    remaining_articles.sort(
        key=lambda item: item["popularity"],
        reverse=True
    )

    for article in remaining_articles:

        if len(selected_articles) >= limit:
            break

        if article["url"] in selected_urls:
            continue

        selected_articles.append(article)

        selected_urls.add(article["url"])

    return selected_articles[:limit]