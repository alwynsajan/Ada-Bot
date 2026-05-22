import requests
from bs4 import BeautifulSoup


def scrape_article_text(url):
    headers = {
        "User-Agent": "AdaBot/1.0 AI news research bot"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    paragraphs = soup.find_all("p")
    text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)

    return " ".join(text.split())