from typing import TypedDict, List, Dict, Any

from langgraph.graph import END, StateGraph

from database.db import article_exists, save_article
from services.news_fetcher import fetch_ai_news
from services.llm import summarize_news_item, generate_general_response
from services.scraper import scrape_article_text
from services.embeddings import chunk_text, generate_embedding
from services.rag import answer_from_stored_news


class AdaState(TypedDict):
    user_message: str
    intent: str
    news_items: List[Dict[str, Any]]
    response: str


def start_node(state: AdaState):
    return state


def fetch_news_node(state: AdaState):
    news_items = fetch_ai_news(limit=5)
    processed_news = []

    for item in news_items:
        title = item["title"]
        url = item["url"]
        score = item["score"]

        summary = summarize_news_item(title, url)
        item["summary"] = summary

        if not article_exists(url):
            try:
                article_text = scrape_article_text(url)

                if article_text:
                    chunks = chunk_text(article_text)

                    embedded_chunks = [
                        (chunk, generate_embedding(chunk))
                        for chunk in chunks
                    ]

                    save_article(
                        title=title,
                        url=url,
                        summary=summary,
                        score=score,
                        chunks=embedded_chunks,
                    )

                    item["storage_status"] = "Article Saved."
                else:
                    item["storage_status"] = "No article text found"

            except Exception:
                item["storage_status"] = "Could not scrape article"
        else:
            item["storage_status"] = "Already stored"

        processed_news.append(item)

    return {
        **state,
        "news_items": processed_news,
        "response": "Fetched latest AI news.",
    }


def answer_question_node(state: AdaState):
    answer = answer_from_stored_news(state["user_message"])

    return {
        **state,
        "news_items": [],
        "response": answer,
    }


def general_chat_node(state: AdaState):
    response = generate_general_response(state["user_message"])

    return {
        **state,
        "news_items": [],
        "response": response,
    }


def route_intent(state: AdaState):
    if state["intent"] == "fetch_news":
        return "fetch_news"

    if state["intent"] == "answer_question":
        return "answer_question"

    return "general_chat"


graph_builder = StateGraph(AdaState)

graph_builder.add_node("start", start_node)
graph_builder.add_node("fetch_news", fetch_news_node)
graph_builder.add_node("answer_question", answer_question_node)
graph_builder.add_node("general_chat", general_chat_node)

graph_builder.set_entry_point("start")

graph_builder.add_conditional_edges(
    "start",
    route_intent,
    {
        "fetch_news": "fetch_news",
        "answer_question": "answer_question",
        "general_chat": "general_chat",
    },
)

graph_builder.add_edge("fetch_news", END)
graph_builder.add_edge("answer_question", END)
graph_builder.add_edge("general_chat", END)

ada_graph = graph_builder.compile()


def run_ada_graph(user_message, intent):
    result = ada_graph.invoke(
        {
            "user_message": user_message,
            "intent": intent,
            "news_items": [],
            "response": "",
        }
    )

    return result