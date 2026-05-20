import json

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)


def classify_user_intent(user_message):
    prompt = f"""
You are an intent classifier for a Discord AI news bot called Ada.

Classify the user's message into exactly one intent.

Valid intents:
- fetch_news
- answer_question

Rules:
- If the user asks for news, articles, updates, headlines, research updates, or latest AI information, use fetch_news.
- If the user asks a question about existing news, stored articles, or asks for an explanation, use answer_question.
- Return only valid JSON.
- Do not include markdown.
- Do not include explanations.

Examples:
{{"intent":"fetch_news"}}
{{"intent":"answer_question"}}

User message:
{user_message}
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
        intent = data.get("intent", "answer_question")

        if intent not in ["fetch_news", "answer_question"]:
            intent = "answer_question"

        return intent

    except Exception:
        return "answer_question"


def summarize_news_item(title, url):
    prompt = f"""
Summarise this AI news article in exactly 2 short informative sentences.

Title: {title}
URL: {url}

Rules:
- Keep it concise but meaningful.
- Do not repeat the title.
- Explain what happened and why it matters.
- Do not use markdown.
- Maximum 60 words total.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()