import json

from database.db import get_all_chunks
from services.embeddings import generate_embedding, cosine_similarity
from services.llm import answer_question_with_context


def answer_from_stored_news(question, top_k=3):
    stored_chunks = get_all_chunks()

    if not stored_chunks:
        return "I do not have any stored news yet. Ask me to fetch the latest AI news first."

    query_embedding = generate_embedding(question)

    scored_chunks = []

    for chunk_text, embedding_json, title, url, fetched_at in stored_chunks:
        embedding = json.loads(embedding_json)
        score = cosine_similarity(query_embedding, embedding)

        scored_chunks.append({
            "score": score,
            "chunk": chunk_text,
            "title": title,
            "url": url,
            "fetched_at": fetched_at,
        })

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    best_chunks = scored_chunks[:top_k]

    context_chunks = [
        f"Source: {item['title']}\nURL: {item['url']}\nContent: {item['chunk']}"
        for item in best_chunks
    ]

    answer = answer_question_with_context(question, context_chunks)

    sources = "\n".join(
        f"- {item['title']}: {item['url']}"
        for item in best_chunks
    )

    # return f"{answer}\n\n**Sources**\n{sources}"
    return f"{answer}"