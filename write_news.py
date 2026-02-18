#!/usr/bin/env python3
"""
Arlo's Daily News Writer
Researches and writes original news stories.
Called by the daily schedule at 6am.
"""
import json, os, sys, re
from datetime import datetime

# Add brain to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.google_search import search, news
from tools.browse import browse
try:
    from tools.browser import browse_js
except ImportError:
    browse_js = None


def fetch_article(url, max_chars=3000):
    """Fetch article text, trying JS rendering first, then static fallback."""
    if browse_js:
        try:
            result = browse_js(url, max_chars=max_chars, timeout=25)
            if result.get("success") and result.get("length", 0) > 100:
                return result.get("content", "")
        except Exception:
            pass
    # Fallback
    try:
        page = browse(url, max_chars=max_chars)
        return page.get("text", "")
    except Exception:
        return ""

STORIES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stories")
os.makedirs(STORIES_DIR, exist_ok=True)

def get_next_id():
    """Get next story ID based on existing files"""
    existing = [f for f in os.listdir(STORIES_DIR) if f.endswith('.json')]
    if not existing:
        return 1
    nums = []
    for f in existing:
        match = re.match(r'(\d+)', f)
        if match:
            nums.append(int(match.group(1)))
    return max(nums) + 1 if nums else 1

def categorize(title, content):
    """Simple keyword-based categorization"""
    text = (title + " " + content).lower()
    scores = {
        "tech": ["ai ", "artificial intelligence", "software", "google", "apple", "microsoft", "startup", "crypto", "blockchain", "chip", "semiconductor", "openai", "meta ", "nvidia"],
        "science": ["nasa", "space", "climate", "research", "study finds", "scientists", "physics", "biology", "discovery", "mars", "quantum"],
        "world": ["ukraine", "russia", "china", "eu ", "europe", "nato", "middle east", "gaza", "iran", "india", "africa", "diplomat", "summit"],
        "politics": ["congress", "senate", "election", "democrat", "republican", "trump", "biden", "legislation", "vote", "law", "policy", "knesset"],
        "health": ["health", "disease", "vaccine", "medical", "hospital", "drug", "fda", "who ", "pandemic", "mental health", "cancer"],
        "business": ["market", "stock", "economy", "inflation", "fed ", "gdp", "trade", "revenue", "profit", "billion", "trillion", "investment"],
        "culture": ["film", "music", "art", "book", "oscar", "grammy", "culture", "entertainment", "game", "sport"],
    }
    best_cat = "world"
    best_score = 0
    for cat, keywords in scores.items():
        score = sum(1 for k in keywords if k in text)
        if score > best_score:
            best_score = score
            best_cat = cat
    return best_cat

def save_story(title, summary, content, category, source_url=None, image_file=None):
    """Save a story as JSON"""
    story_id = get_next_id()
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:50]
    filename = f"{story_id:03d}-{slug}.json"

    story = {
        "id": story_id,
        "title": title,
        "summary": summary,
        "content": content,
        "category": category,
        "writer": "Arlo",
        "published": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_url": source_url,
        "image_file": image_file
    }

    filepath = os.path.join(STORIES_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(story, f, indent=2)

    print(f"  Saved: {filename}")
    return filepath

if __name__ == "__main__":
    print("This module provides story-writing utilities.")
    print("The actual daily writing is orchestrated by the scheduled task.")
