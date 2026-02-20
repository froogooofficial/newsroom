#!/usr/bin/env python3
"""
Newsletter Sender — Send the latest Dispatch edition to subscribers.

Reads subscriber list from Google Sheets, latest stories, and sends
a formatted email digest via Gmail.

Usage:
    python3 newsletter.py [morning|evening]
"""

import json
import glob
import sys
import os
from datetime import datetime

# Add brain to path for tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SUBSCRIBERS_SHEET = "17M7uoRnWE2JolQYMfLlVbKcoKP4Bx4Rrn9j-jPJb8iY"
SITE_URL = "https://froogooofficial.github.io/newsroom"


def get_latest_stories(count=4):
    """Get the most recent stories."""
    stories = []
    for f in sorted(glob.glob("stories/*.json"), reverse=True)[:count]:
        with open(f) as fh:
            stories.append(json.load(fh))
    return stories


def build_email_html(stories, edition="morning"):
    """Build a nice HTML email from stories."""
    date_str = datetime.now().strftime("%B %d, %Y")
    edition_label = "Morning" if edition == "morning" else "Evening"
    
    html = f"""
    <div style="max-width:600px; margin:0 auto; font-family:Georgia,serif; color:#1a1a1a; padding:20px;">
      <div style="text-align:center; border-bottom:2px solid #1a1a1a; padding-bottom:15px; margin-bottom:20px;">
        <h1 style="font-size:28px; margin:0;">Arlo's Dispatch</h1>
        <p style="font-size:14px; color:#666; margin:5px 0 0;">{edition_label} Edition — {date_str}</p>
      </div>
    """
    
    for i, story in enumerate(stories):
        title = story.get('title', 'Untitled')
        summary = story.get('summary', '')
        category = story.get('category', '').upper()
        slug = f"story-{title.lower()[:60].replace(' ', '-').replace('/', '-')}"
        url = f"{SITE_URL}/{slug}.html"
        
        html += f"""
      <div style="margin-bottom:25px; {'border-top:1px solid #e5e5e5; padding-top:20px;' if i > 0 else ''}">
        <span style="font-size:11px; color:#2563eb; font-family:sans-serif; letter-spacing:1px;">{category}</span>
        <h2 style="font-size:20px; margin:5px 0 8px;"><a href="{url}" style="color:#1a1a1a; text-decoration:none;">{title}</a></h2>
        <p style="font-size:15px; color:#555; line-height:1.5;">{summary}</p>
        <a href="{url}" style="font-size:13px; color:#2563eb; text-decoration:none;">Read full story →</a>
      </div>
        """
    
    html += f"""
      <div style="border-top:2px solid #1a1a1a; padding-top:15px; margin-top:20px; text-align:center;">
        <p style="font-size:13px; color:#999;">
          Written by <strong>Arlo</strong> — an AI journalist<br>
          <a href="{SITE_URL}" style="color:#2563eb;">Read more at Arlo's Dispatch</a>
        </p>
        <p style="font-size:11px; color:#ccc; margin-top:10px;">
          You're receiving this because you subscribed. Reply to unsubscribe.
        </p>
      </div>
    </div>
    """
    
    return html


def preview(edition="morning"):
    """Preview the newsletter HTML."""
    stories = get_latest_stories(4 if edition == "morning" else 3)
    html = build_email_html(stories, edition)
    
    with open("/tmp/newsletter_preview.html", "w") as f:
        f.write(html)
    
    print(f"Preview saved to /tmp/newsletter_preview.html")
    print(f"Stories: {len(stories)}")
    for s in stories:
        print(f"  - {s['title'][:60]}")
    return html


if __name__ == "__main__":
    edition = sys.argv[1] if len(sys.argv) > 1 else "morning"
    preview(edition)
    print(f"\n{edition.title()} edition newsletter ready for preview.")
    print("Note: Actual sending requires integration with gmail_send tool.")
