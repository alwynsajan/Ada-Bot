import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("data/ada.sqlite")


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                summary TEXT,
                popularity INTEGER DEFAULT 0,
                source TEXT,
                content_type TEXT DEFAULT 'metadata',
                fetched_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(article_id) REFERENCES articles(id)
            )
        """)

        conn.commit()


def article_exists(url):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
        return cursor.fetchone() is not None
    
def is_rag_article(article_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content_type FROM articles WHERE id = ?",
            (article_id,)
        )
        row = cursor.fetchone()
        return row and row[0] == "rag"


def save_article(title, url, summary, popularity, source, chunks, content_type="metadata"):
    fetched_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO articles (title, url, summary, popularity, source, content_type, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (title, url, summary, popularity, source, content_type, fetched_at),
        )

        cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
        article_id = cursor.fetchone()[0]

        for chunk_text, embedding in chunks:
            cursor.execute(
                """
                INSERT INTO chunks (article_id, chunk_text, embedding, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    article_id,
                    chunk_text,
                    json.dumps(embedding),
                    fetched_at,
                ),
            )

        conn.commit()


def get_all_chunks():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                chunks.chunk_text,
                chunks.embedding,
                articles.title,
                articles.url,
                articles.fetched_at,
                articles.content_type 
            FROM chunks
            JOIN articles ON chunks.article_id = articles.id
        """)

        return cursor.fetchall()