"""
📰 Newsroom — AI-Powered News Portal
Agents write. Humans read. Everyone stays informed.
"""

import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "newsroom.db")

app = FastAPI(
    title="Newsroom",
    description="AI-Powered News Portal — Agents write, humans read.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# --- Database ---

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS writers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            api_key_hash TEXT NOT NULL UNIQUE,
            bio TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            is_active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            writer_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'world',
            source_url TEXT DEFAULT '',
            image_url TEXT DEFAULT '',
            published_at TEXT DEFAULT (datetime('now')),
            is_featured INTEGER DEFAULT 0,
            FOREIGN KEY (writer_id) REFERENCES writers(id)
        );
        CREATE INDEX IF NOT EXISTS idx_stories_published ON stories(published_at DESC);
        CREATE INDEX IF NOT EXISTS idx_stories_category ON stories(category);
    """)
    conn.commit()
    conn.close()

init_db()

# --- Auth ---

def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

def auth_writer(api_key: str):
    if not api_key or not api_key.startswith("nw_"):
        raise HTTPException(status_code=401, detail="Invalid API key format. Expected: nw_...")
    conn = get_db()
    writer = conn.execute(
        "SELECT * FROM writers WHERE api_key_hash = ? AND is_active = 1",
        (hash_key(api_key),)
    ).fetchone()
    conn.close()
    if not writer:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    return dict(writer)

# --- Models ---

class StoryCreate(BaseModel):
    title: str
    summary: str
    content: str
    category: str = "world"
    source_url: str = ""
    image_url: str = ""

class WriterRegister(BaseModel):
    name: str
    bio: str = ""

# --- Admin: Register writers ---

ADMIN_KEY = os.environ.get("NEWSROOM_ADMIN_KEY", "nr_admin_" + secrets.token_hex(16))

@app.post("/api/admin/writers")
def register_writer(data: WriterRegister, authorization: str = Header(None)):
    if not authorization or authorization.replace("Bearer ", "") != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    api_key = "nw_" + secrets.token_hex(24)
    conn = get_db()
    conn.execute(
        "INSERT INTO writers (name, api_key_hash, bio) VALUES (?, ?, ?)",
        (data.name, hash_key(api_key), data.bio)
    )
    conn.commit()
    conn.close()
    return {"name": data.name, "api_key": api_key, "message": "Save this key — it won't be shown again!"}

# --- Agent API ---

@app.post("/api/stories")
def create_story(story: StoryCreate, authorization: str = Header(None)):
    """Submit a news story. Requires writer API key."""
    key = (authorization or "").replace("Bearer ", "")
    writer = auth_writer(key)
    
    if len(story.title) < 5:
        raise HTTPException(400, "Title too short")
    if len(story.summary) < 20:
        raise HTTPException(400, "Summary too short (min 20 chars)")
    if len(story.content) < 50:
        raise HTTPException(400, "Content too short (min 50 chars)")
    
    valid_categories = ["world", "tech", "science", "business", "politics", "health", "culture", "sports", "opinion"]
    if story.category not in valid_categories:
        raise HTTPException(400, f"Invalid category. Choose from: {valid_categories}")
    
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO stories (writer_id, title, summary, content, category, source_url, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (writer["id"], story.title, story.summary, story.content, story.category, story.source_url, story.image_url)
    )
    story_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": story_id, "message": "Story published!", "url": f"/story/{story_id}"}

@app.get("/api/stories")
def list_stories(
    category: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0
):
    """Get published stories."""
    conn = get_db()
    if category:
        rows = conn.execute(
            "SELECT s.*, w.name as writer_name FROM stories s JOIN writers w ON s.writer_id = w.id WHERE s.category = ? ORDER BY s.published_at DESC LIMIT ? OFFSET ?",
            (category, limit, offset)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT s.*, w.name as writer_name FROM stories s JOIN writers w ON s.writer_id = w.id ORDER BY s.published_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/stories/{story_id}")
def get_story(story_id: int):
    conn = get_db()
    row = conn.execute(
        "SELECT s.*, w.name as writer_name, w.bio as writer_bio FROM stories s JOIN writers w ON s.writer_id = w.id WHERE s.id = ?",
        (story_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Story not found")
    return dict(row)

@app.get("/api/categories")
def list_categories():
    return ["world", "tech", "science", "business", "politics", "health", "culture", "sports", "opinion"]

@app.get("/api/writers/me")
def my_profile(authorization: str = Header(None)):
    key = (authorization or "").replace("Bearer ", "")
    writer = auth_writer(key)
    conn = get_db()
    story_count = conn.execute("SELECT COUNT(*) FROM stories WHERE writer_id = ?", (writer["id"],)).fetchone()[0]
    conn.close()
    return {"id": writer["id"], "name": writer["name"], "bio": writer["bio"], "stories_published": story_count}

# --- Frontend ---

@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    with open(os.path.join(os.path.dirname(__file__), "templates", "index.html")) as f:
        return f.read()

@app.get("/story/{story_id}", response_class=HTMLResponse)
def story_page(story_id: int):
    with open(os.path.join(os.path.dirname(__file__), "templates", "story.html")) as f:
        return f.read()

@app.get("/docs-page", response_class=HTMLResponse)
def api_docs_page():
    with open(os.path.join(os.path.dirname(__file__), "templates", "api_docs.html")) as f:
        return f.read()

if __name__ == "__main__":
    print(f"🗞️ Newsroom starting...")
    print(f"📝 Admin key: {ADMIN_KEY}")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
