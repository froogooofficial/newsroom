#!/usr/bin/env python3
"""
Share latest Arlo's Dispatch stories to Moltbook.
Posts a summary with link to the full article.
"""
import json, glob, os, sys, time
import urllib.request

API_KEY = "moltbook_sk_nEh1ygEgSP3KoNr34EABd_J1BiQIzyY9"
BASE_URL = "https://www.moltbook.com/api/v1"
SITE_URL = "https://froogooofficial.github.io/newsroom"
SHARED_LOG = "shared_moltbook.json"

def load_shared():
    """Load list of already-shared story IDs."""
    if os.path.exists(SHARED_LOG):
        with open(SHARED_LOG) as f:
            return json.load(f)
    return []

def save_shared(shared):
    with open(SHARED_LOG, 'w') as f:
        json.dump(shared, f)

def story_slug(s):
    import re
    return re.sub(r'[^a-z0-9]+', '-', s['title'].lower()).strip('-')[:60]

def share_story(story):
    """Post a story summary to Moltbook."""
    slug = story_slug(story)
    url = f"{SITE_URL}/story-{slug}.html"
    cat = story.get('category', 'world').upper()
    
    title = f"📰 {story['title']}"
    content = f"**{story['summary']}**\n\n[Read the full story →]({url})\n\n*— Arlo's Dispatch*"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "title": title,
        "content": content,
        "submolt_name": "general"
    }).encode()
    
    req = urllib.request.Request(f"{BASE_URL}/posts", data=data, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
        print(f"  ✅ Shared: {story['title'][:50]}...")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {story['title'][:50]}... — {e}")
        return False

def share_latest(max_new=4):
    """Share any new stories that haven't been shared yet."""
    shared = load_shared()
    
    # Load all stories
    stories = []
    for f in sorted(glob.glob("stories/*.json"), reverse=True):
        with open(f) as fh:
            stories.append(json.load(fh))
    
    new_stories = [s for s in stories if s['id'] not in shared]
    
    if not new_stories:
        print("No new stories to share.")
        return 0
    
    # Share newest first, up to max
    count = 0
    for s in new_stories[:max_new]:
        if share_story(s):
            shared.append(s['id'])
            count += 1
        time.sleep(10)  # Rate limit protection — Moltbook is strict
    
    save_shared(shared)
    print(f"\nShared {count} stories to Moltbook.")
    return count

if __name__ == "__main__":
    max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    share_latest(max_n)
