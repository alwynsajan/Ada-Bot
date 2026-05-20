from typing import TypedDict, List, Dict, Any

from langgraph.graph import END, StateGraph

from services.news_fetcher import fetch_ai_news
from services.llm import summarize_news_item


class AdaState(TypedDict):
    user_message: str
    intent: str
    news_items: List[Dict[str, Any]]
    response: str


def start_node(state: AdaState):
    return state


def fetch_news_node(state: AdaState):
    news_items = fetch_ai_news(limit=5)

    for item in news_items:
        item["summary"] = summarize_news_item(item["title"], item["url"])

    return {
        **state,
        "news_items": news_items,
        "response": "Fetched latest AI news.",
    }


def answer_question_node(state: AdaState):
    return {
        **state,
        "news_items": [],
        "response": (
            "I can answer questions after the RAG knowledge base is added. "
            "For now, ask me to fetch the latest AI news."
        ),
    }


def route_intent(state: AdaState):
    if state["intent"] == "fetch_news":
        return "fetch_news"

    return "answer_question"


graph_builder = StateGraph(AdaState)

graph_builder.add_node("start", start_node)
graph_builder.add_node("fetch_news", fetch_news_node)
graph_builder.add_node("answer_question", answer_question_node)

graph_builder.set_entry_point("start")

graph_builder.add_conditional_edges(
    "start",
    route_intent,
    {
        "fetch_news": "fetch_news",
        "answer_question": "answer_question",
    },
)

graph_builder.add_edge("fetch_news", END)
graph_builder.add_edge("answer_question", END)

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