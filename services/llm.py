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
        - general_chat

        Rules:
        - If the user asks for news, articles, updates, headlines, research updates, or latest AI information, use fetch_news.
        - If the user asks a question about fetched/stored news, previous articles, summaries, or wants an explanation based on news, use answer_question.
        - If the user says hello, hi, thanks, asks who you are, or makes casual/general conversation, use general_chat.
        - Return only valid JSON.
        - Do not include markdown.
        - Do not include explanations.

        Examples:
        {{"intent":"fetch_news"}}
        {{"intent":"answer_question"}}
        {{"intent":"general_chat"}}

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
        intent = data.get("intent", "general_chat")

        if intent not in ["fetch_news", "answer_question", "general_chat"]:
            intent = "general_chat"

        return intent

    except Exception:
        return "general_chat"


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
- Maximum 40 words total.
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()


def answer_question_with_context(question, context_chunks):
    context = "\n\n".join(context_chunks)

    prompt = f"""
You are Ada, an AI news assistant.

Answer the user's question using only the provided news context.

Rules:
- Be concise.
- If the answer is not in the context, say you do not have enough stored news context yet.
- Do not make unsupported claims.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()


def generate_general_response(user_message):
    prompt = f"""
You are Ada, a friendly AI news Discord bot.

Reply briefly and naturally to this casual user message.

Rules:
- Keep it under 25 words.
- Be friendly.
- If relevant, mention that you can fetch AI news or answer questions about stored AI news.
- Do not use markdown.

User message:
{user_message}
"""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()