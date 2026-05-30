from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import requests

app = Flask(__name__)
CORS(app)

DATABASE = "database.db"
QUOTE_API_URL = "https://api.quotable.io/random"

FALLBACK_QUOTES = [
    {"content": "Keep going. Everything you need will come to you at the perfect time.", "author": "Unknown"},
    {"content": "Success is the sum of small efforts repeated day in and day out.", "author": "Robert Collier"},
    {"content": "The future depends on what you do today.", "author": "Mahatma Gandhi"},
]

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_text TEXT NOT NULL,
            author TEXT NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_quote(quote_text, author, source):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO quotes (quote_text, author, source) VALUES (?, ?, ?)",
        (quote_text, author, source)
    )
    conn.commit()
    conn.close()

def fetch_external_quote():
    response = requests.get(QUOTE_API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Quotable usually returns one object, but this makes it safer.
    if isinstance(data, list):
        data = data[0]

    quote_text = data.get("content") or data.get("quote")
    author = data.get("author") or "Unknown"

    if not quote_text:
        raise ValueError("Quote text not found in API response")

    return quote_text, author

init_db()

@app.route("/quote", methods=["GET"])
def get_quote():
    try:
        quote_text, author = fetch_external_quote()
        source = "api"
    except Exception:
        fallback = FALLBACK_QUOTES[0]
        quote_text = fallback["content"]
        author = fallback["author"]
        source = "fallback"

    save_quote(quote_text, author, source)

    return jsonify({
        "quote_text": quote_text,
        "author": author,
        "source": source
    }), 200

@app.route("/history", methods=["GET"])
def get_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, quote_text, author, source, created_at
        FROM quotes
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "id": row["id"],
            "quote_text": row["quote_text"],
            "author": row["author"],
            "source": row["source"],
            "created_at": row["created_at"]
        })

    return jsonify(history), 200

if __name__ == "__main__":
    app.run(debug=True)