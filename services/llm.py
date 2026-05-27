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
        - Use fetch_news ONLY when the user explicitly wants fresh/latest/new AI news fetched.
        - Use answer_question when the user asks about:
        - previously discussed articles
        - fetched news
        - article numbers
        - details, explanations, impacts, summaries, or follow-up questions
        - topics already mentioned earlier in the conversation
        - Treat follow-up conversational questions as answer_question even if they contain words like "news" or "article".
        - Use general_chat for greetings, thanks, casual conversation, or unrelated chat.
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
        You are Ada, a friendly and conversational AI news assistant on Discord.

        Your job is to reply naturally to casual conversation while subtly guiding users toward your AI news features when appropriate.

        Rules:
        - Sound human, warm, and polite.
        - Avoid sounding robotic, scripted, or overly promotional.
        - Keep replies short and natural.
        - Maximum 30 words.
        - Do not always mention features unless it fits naturally.
        - If relevant, casually mention that you can fetch latest AI news, headlines, or answer questions about recent AI developments.
        - Do not use markdown.
        - Avoid repeating the same phrasing often.

        Examples of good behavior:
        - "Hey! Hope you're doing well."
        - "Hi! I can also help you stay updated with the latest AI news."
        - "Glad to help. I can also fetch recent AI updates if you'd like."
        - "Hello! Feel free to ask me about the latest happenings in AI."

        User message:
        {user_message}
        """

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

def reconstruct_news_query(user_message,recent_news_items,previous_topic=None,previous_article=None):
    news_context = []

    for index, item in enumerate(recent_news_items, start=1):
        news_context.append(
            f"{index}. {item['title']}"
        )

    formatted_news = "\n".join(news_context)

    previous_context = ""

    if previous_topic:
        previous_context += f"\nPrevious topic: {previous_topic}"

    if previous_article:
        previous_context += (
            f"\nPrevious referenced article: "
            f"{previous_article.get('title')}"
        )

    prompt = f"""
    You are Ada, an AI news assistant helping improve semantic search retrieval.

    Your task:
    Rewrite the user's query into a fully self-contained news-related query.

    The user may:
    - refer to articles using numbers
    - refer indirectly to previous news
    - ask follow-up questions
    - use vague references like "that one", "article 2", "the NVIDIA news"
    - continue discussing the previous topic without naming it again

    Use:
    - the recent news list
    - the previous conversation topic
    - the previous referenced article

    to resolve references correctly.

    Rules:
    - Preserve the original meaning.
    - Make the query explicit and semantic-search friendly.
    - Include the article/topic name if referenced.
    - Do not answer the question.
    - Do not invent facts.
    - If the user is continuing the previous topic, incorporate it naturally.
    - Return ONLY valid JSON.
    - Do not use markdown.

    JSON format:
    {{
        "query": "rewritten query",
        "referenced_article_number": 1
    }}

    Use null if no article number/reference was identified.

    Recent news list:
    {formatted_news}

    {previous_context}

    User query:
    {user_message}
    """

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.1,
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)

        reconstructed_query = data.get("query", user_message)
        article_number = data.get("referenced_article_number")

        referenced_article = None

        if (
            isinstance(article_number, int)
            and 1 <= article_number <= len(recent_news_items)
        ):
            referenced_article = recent_news_items[article_number - 1]

        return reconstructed_query, referenced_article

    except Exception:
        return user_message, previous_article