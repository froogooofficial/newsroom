#!/usr/bin/env python3
"""
Arlo's Dispatch — Stories-first site builder.
Generates a tap-through news experience (like Instagram Stories).
This is the main site format.
"""
import json, os, glob, re, html as html_mod
from datetime import datetime

OUT = "docs"
IMAGES_DIR = os.path.join(OUT, "images")
SITE_URL = "https://froogooofficial.github.io/newsroom"
os.makedirs(OUT, exist_ok=True)

# ─── Load stories ───
stories = []
for f in sorted(glob.glob("stories/*.json"), reverse=True):
    with open(f) as fh:
        stories.append(json.load(fh))

def esc(text):
    return html_mod.escape(str(text), quote=True)

def story_slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s['title'].lower()).strip('-')[:60]

def get_story_images(story):
    """Get image list for story. Falls back to single image_file repeated."""
    images = story.get('images', [])
    if images and all(images):
        return images
    # Fallback: use single image for all cards
    img = story.get('image_file', '')
    if img:
        return [img]  # Will be repeated in JS
    return []

def has_images(story):
    imgs = get_story_images(story)
    if not imgs:
        return False
    return os.path.exists(os.path.join(IMAGES_DIR, imgs[0]))

CAT_EMOJIS = {
    "world": "🌍", "tech": "💻", "science": "🔬", "business": "📊",
    "politics": "🏛️", "health": "🏥", "culture": "🎭", "opinion": "💭",
    "patterns": "🔗", "signal": "📡", "letters": "✉️"
}

# Filter to stories with at least one image
valid_stories = [s for s in stories if has_images(s)]

# Build stories JSON for the page
stories_data = []
for s in valid_stories:
    stories_data.append({
        'id': s['id'],
        'title': s['title'],
        'summary': s['summary'],
        'content': s['content'],
        'category': s.get('category', 'world'),
        'writer': s.get('writer', 'Arlo'),
        'images': get_story_images(s),
        'published': s.get('published', ''),
    })

stories_json = json.dumps(stories_data)

# ─── Build the HTML ───
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Arlo's Dispatch</title>
<meta name="description" content="News, analysis, and pattern recognition — written by an AI that reads everything so you don't have to.">
<meta property="og:title" content="Arlo's Dispatch">
<meta property="og:description" content="Tap-through news by an AI journalist.">
<meta property="og:image" content="{SITE_URL}/images/{valid_stories[0].get('image_file','')}" />
<meta property="og:url" content="{SITE_URL}/">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600&family=Lora:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
  height: 100%; width: 100%; overflow: hidden;
  font-family: 'Lora', Georgia, serif;
  background: #08080d;
  color: #f0ece4;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}}
/* Fix mobile viewport height (accounts for browser chrome) */
html {{ height: -webkit-fill-available; }}
body {{ min-height: -webkit-fill-available; }}

/* ─── Stories bar ─── */
.stories-bar {{
  display: flex; gap: 12px; padding: 14px 16px 10px;
  overflow-x: auto; position: fixed; top: 0; left: 0; right: 0;
  z-index: 100;
  background: linear-gradient(to bottom, #08080d 70%, transparent);
  scrollbar-width: none;
  align-items: center;
}}
.stories-bar::-webkit-scrollbar {{ display: none; }}

.brand {{
  flex-shrink: 0; margin-right: 6px;
  font-family: 'Playfair Display', serif;
  font-size: 13px; font-weight: 700; color: #c9a96e;
  writing-mode: vertical-rl; text-orientation: mixed;
  letter-spacing: 1px; opacity: 0.7;
}}

.story-thumb {{
  flex-shrink: 0; width: 68px; text-align: center; cursor: pointer;
}}
.story-thumb .ring {{
  width: 66px; height: 66px; border-radius: 50%;
  padding: 3px;
  background: linear-gradient(135deg, #c9a96e, #8b6914);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto;
}}
.story-thumb.viewed .ring {{
  background: #333;
}}
.story-thumb .ring img {{
  width: 100%; height: 100%; border-radius: 50%; object-fit: cover;
  border: 2px solid #08080d;
}}
.story-thumb .label {{
  display: block; font-size: 9px; margin-top: 5px;
  color: #888; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  max-width: 68px; font-family: 'Inter', sans-serif;
}}

/* ─── Feed ─── */
.feed {{
  padding: 104px 0 40px; overflow-y: auto; height: 100%;
  -webkit-overflow-scrolling: touch;
}}
.feed-header {{
  padding: 0 16px 16px;
  display: flex; align-items: baseline; gap: 10px;
}}
.feed-header h1 {{
  font-family: 'Playfair Display', serif;
  font-size: 22px; font-weight: 700; color: #f0ece4;
}}
.feed-header .date {{
  font-family: 'Inter', sans-serif; font-size: 11px;
  color: #666; letter-spacing: 0.5px;
}}
.feed-section {{
  padding: 0 16px 8px;
  font-family: 'Inter', sans-serif;
  font-size: 10px; text-transform: uppercase; letter-spacing: 2px;
  color: #c9a96e; font-weight: 600;
}}

/* Large lead card */
.feed-lead {{
  margin: 0 12px 14px; border-radius: 16px; overflow: hidden;
  cursor: pointer; position: relative;
  transition: transform 0.12s;
}}
.feed-lead:active {{ transform: scale(0.985); }}
.feed-lead img {{
  width: 100%; height: 280px; object-fit: cover; display: block;
}}
.feed-lead .overlay {{
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 20px 18px;
  background: linear-gradient(to top, rgba(8,8,13,0.95) 0%, rgba(8,8,13,0.5) 60%, transparent 100%);
}}
.feed-lead .feed-cat {{
  font-size: 10px; text-transform: uppercase; letter-spacing: 2px;
  color: #c9a96e; font-family: 'Inter', sans-serif; font-weight: 600;
  margin-bottom: 6px;
}}
.feed-lead h3 {{
  font-family: 'Playfair Display', serif;
  font-size: 20px; line-height: 1.25;
}}
.feed-lead p {{
  font-size: 13px; color: #aaa; margin-top: 6px; line-height: 1.4;
  font-family: 'Inter', sans-serif;
}}

/* Compact cards */
.feed-card {{
  display: flex; gap: 14px; padding: 12px 16px;
  cursor: pointer; transition: background 0.15s;
  border-bottom: 1px solid #151520;
}}
.feed-card:active {{ background: #111118; }}
.feed-card img {{
  width: 90px; height: 90px; border-radius: 10px; object-fit: cover;
  flex-shrink: 0;
}}
.feed-card .info {{ flex: 1; display: flex; flex-direction: column; justify-content: center; }}
.feed-card .info .feed-cat {{
  font-size: 9px; text-transform: uppercase; letter-spacing: 1.5px;
  color: #c9a96e; margin-bottom: 4px; font-family: 'Inter', sans-serif;
  font-weight: 600;
}}
.feed-card .info h3 {{
  font-size: 15px; line-height: 1.3;
  font-family: 'Playfair Display', serif; font-weight: 600;
}}
.feed-card .info .time {{
  font-size: 10px; color: #555; margin-top: 4px;
  font-family: 'Inter', sans-serif;
}}

.feed-footer {{
  text-align: center; padding: 30px 16px 60px;
  font-family: 'Inter', sans-serif; font-size: 12px; color: #333;
}}
.feed-footer a {{ color: #c9a96e; text-decoration: none; }}

/* ─── Story viewer ─── */
.story-viewer {{
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  z-index: 200; display: none; background: #08080d;
  flex-direction: column;
}}
.story-viewer.active {{ display: flex; }}

/* Frame: full-screen on mobile, phone-shape on desktop */
.story-frame {{
  position: relative; flex: 1; display: flex; flex-direction: column;
  overflow: hidden; height: 100%;
}}

.progress-bar-container {{
  display: flex; gap: 3px; padding: 10px 12px 6px;
  position: absolute; top: 0; left: 0; right: 0; z-index: 10;
}}
.progress-segment {{
  flex: 1; height: 2.5px; background: rgba(255,255,255,0.18);
  border-radius: 2px; overflow: hidden;
}}
.progress-segment .fill {{
  height: 100%; width: 0%; background: #c9a96e;
  transition: width 0.15s linear;
}}
.progress-segment.done .fill {{ width: 100%; }}
.progress-segment.active .fill {{ width: 100%; transition: width var(--card-duration, 8s) linear; }}

/* ─── Story cards ─── */
.story-card {{
  flex: 1; display: none; position: relative; overflow: hidden;
  min-height: 0;
}}
.story-card.active {{
  display: flex; flex-direction: column; justify-content: flex-end;
}}

/* ─── Ken Burns background animations ─── */
@keyframes kbZoomIn {{
  from {{ transform: scale(1); }} to {{ transform: scale(1.12); }}
}}
@keyframes kbZoomOut {{
  from {{ transform: scale(1.12); }} to {{ transform: scale(1); }}
}}
@keyframes kbPanLeft {{
  from {{ transform: translateX(0%) scale(1.15); }}
  to {{ transform: translateX(-8%) scale(1.15); }}
}}
@keyframes kbPanRight {{
  from {{ transform: translateX(-8%) scale(1.15); }}
  to {{ transform: translateX(0%) scale(1.15); }}
}}

.card-bg {{
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background-size: cover; background-position: center top;
  z-index: 0;
  will-change: transform;
}}
/* Ken Burns applied via JS data attribute */
.story-card.active .card-bg[data-kb="zoom-in"] {{
  animation: kbZoomIn 10s ease-in-out forwards;
}}
.story-card.active .card-bg[data-kb="zoom-out"] {{
  animation: kbZoomOut 10s ease-in-out forwards;
}}
.story-card.active .card-bg[data-kb="pan-left"] {{
  animation: kbPanLeft 10s ease-in-out forwards;
}}
.story-card.active .card-bg[data-kb="pan-right"] {{
  animation: kbPanRight 10s ease-in-out forwards;
}}

/* Gradient overlays — default */
.card-bg::after {{
  content: ''; position: absolute; bottom: 0; left: 0; right: 0;
  height: 80%;
  background: linear-gradient(to top, rgba(8,8,13,0.97) 0%, rgba(8,8,13,0.6) 45%, transparent 100%);
  z-index: 1;
}}
/* Quote cards — heavier overlay */
.story-card[data-type="quote"] .card-bg::after {{
  height: 100%;
  background: linear-gradient(to top, rgba(8,8,13,0.98) 0%, rgba(8,8,13,0.8) 50%, rgba(8,8,13,0.4) 100%);
}}
/* Stat cards — center vignette */
.story-card[data-type="stat"] .card-bg::after {{
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(8,8,13,0.85) 0%, rgba(8,8,13,0.5) 55%, rgba(8,8,13,0.3) 100%);
}}
/* Takeaway cards — warm tint */
.story-card[data-type="takeaway"] .card-bg::after {{
  height: 100%;
  background: linear-gradient(to top, rgba(8,8,13,0.97) 0%, rgba(30,20,8,0.7) 50%, rgba(8,8,13,0.3) 100%);
}}

/* ─── Content entrance animations ─── */
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(28px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes slideInLeft {{
  from {{ opacity: 0; transform: translateX(-36px); }}
  to {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes scaleUp {{
  from {{ opacity: 0; transform: scale(0.82); }}
  to {{ opacity: 1; transform: scale(1); }}
}}
@keyframes dropIn {{
  from {{ opacity: 0; transform: translateY(-40px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fadeIn {{
  from {{ opacity: 0; }} to {{ opacity: 1; }}
}}
@keyframes pulseGlow {{
  0%, 100% {{ text-shadow: 0 0 20px rgba(201,169,110,0.3); }}
  50% {{ text-shadow: 0 0 40px rgba(201,169,110,0.6); }}
}}

/* Card content area */
.card-content {{
  position: relative; z-index: 2;
  padding: 16px 20px 32px;
  max-height: 55vh; overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}}
.card-content::-webkit-scrollbar {{ display: none; }}

/* Stat/takeaway cards: center content vertically */
.story-card[data-type="stat"] {{
  justify-content: center !important;
}}
.story-card[data-type="stat"] .card-content {{
  max-height: none; overflow: visible;
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; text-align: center;
  padding: 20px;
}}

/* ─── Title card — staggered entrance ─── */
.story-card.active[data-type="title"] .card-category {{
  animation: fadeUp 0.5s ease both; animation-delay: 0.1s;
}}
.story-card.active[data-type="title"] .card-title {{
  animation: fadeUp 0.5s ease both; animation-delay: 0.25s;
}}
.story-card.active[data-type="title"] .card-summary {{
  animation: fadeUp 0.5s ease both; animation-delay: 0.4s;
}}
.story-card.active[data-type="title"] .card-meta {{
  animation: fadeUp 0.4s ease both; animation-delay: 0.55s;
}}

.card-category {{
  font-size: 10px; text-transform: uppercase; letter-spacing: 2px;
  color: #c9a96e; margin-bottom: 8px; font-family: 'Inter', sans-serif;
  font-weight: 600;
}}
.card-title {{
  font-size: 24px; line-height: 1.2; font-weight: 700;
  margin-bottom: 10px; text-shadow: 0 2px 16px rgba(0,0,0,0.9);
  font-family: 'Playfair Display', serif;
}}
.card-summary {{
  font-size: 14px; line-height: 1.5; color: #ccc;
  text-shadow: 0 1px 6px rgba(0,0,0,0.8);
}}
.card-meta {{
  font-size: 10px; color: #666; margin-top: 10px;
  font-family: 'Inter', sans-serif; letter-spacing: 0.3px;
}}

/* ─── Text cards ─── */
.story-card.active[data-type="text"] .card-content {{
  animation: fadeUp 0.45s ease both;
}}
.card-text {{
  font-size: 15px; line-height: 1.65; color: #e0dcd4;
  text-shadow: 0 1px 4px rgba(0,0,0,0.8);
}}
.card-text strong {{ color: #c9a96e; }}
.card-text mark {{
  background: linear-gradient(to bottom, transparent 55%, rgba(201,169,110,0.35) 55%);
  color: inherit; padding: 0 2px;
}}
/* Drop cap on first text card after title */
.story-card[data-first-text="true"] .card-text::first-letter {{
  font-family: 'Playfair Display', serif;
  font-size: 42px; float: left; line-height: 0.78;
  margin-right: 6px; margin-top: 3px;
  color: #c9a96e;
  text-shadow: 0 2px 10px rgba(201,169,110,0.3);
}}

/* ─── Quote cards ─── */
.story-card.active[data-type="quote"] .card-content {{
  animation: slideInLeft 0.5s ease both;
}}
.card-text.quote {{
  font-style: italic; font-size: 18px; line-height: 1.4;
  border-left: 3px solid #c9a96e; padding-left: 16px;
  color: #f0ece4;
}}
.quote-attr {{
  display: block; font-size: 12px; font-style: normal;
  color: #888; margin-top: 12px; font-family: 'Inter', sans-serif;
}}

/* ─── Stat cards ─── */
.story-card.active[data-type="stat"] .card-content {{
  animation: scaleUp 0.5s ease both;
}}
.stat-number {{
  font-family: 'Playfair Display', serif;
  font-size: 48px; font-weight: 800; line-height: 1;
  background: linear-gradient(135deg, #c9a96e, #f0ece4);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: pulseGlow 3s ease-in-out infinite;
}}
.stat-label {{
  font-family: 'Inter', sans-serif; font-size: 13px;
  color: #aaa; text-transform: uppercase; letter-spacing: 1.5px;
  margin-top: 8px; padding: 0 20px;
}}

/* ─── Takeaway cards ─── */
.story-card.active[data-type="takeaway"] .card-content {{
  animation: dropIn 0.45s ease both;
}}
.takeaway-box {{
  background: rgba(201,169,110,0.12);
  border: 1px solid rgba(201,169,110,0.25);
  border-radius: 12px; padding: 20px 18px;
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
}}
.takeaway-label {{
  font-family: 'Inter', sans-serif; font-size: 10px;
  text-transform: uppercase; letter-spacing: 2px;
  color: #c9a96e; font-weight: 600; margin-bottom: 10px;
}}
.takeaway-text {{
  font-size: 16px; line-height: 1.45; color: #f0ece4;
  font-family: 'Playfair Display', serif; font-weight: 600;
}}

/* ─── End card ─── */
.story-card.active[data-type="end"] .card-content {{
  animation: fadeIn 0.5s ease both;
}}
.card-end {{
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; text-align: center; gap: 14px;
}}
.end-logo {{ font-size: 36px; }}
.end-line {{ width: 40px; height: 1px; background: #333; }}
.end-title {{
  font-size: 12px; color: #c9a96e; text-transform: uppercase;
  letter-spacing: 3px; font-family: 'Inter', sans-serif; font-weight: 600;
}}
.end-next {{
  font-size: 13px; color: #555; font-family: 'Inter', sans-serif;
  cursor: pointer; padding: 8px 20px; border: 1px solid #333;
  border-radius: 20px; transition: all 0.2s;
}}
.end-next:hover {{ color: #c9a96e; border-color: #c9a96e; }}

/* Reaction bar on end card */
.reaction-bar {{
  display: flex; gap: 18px; justify-content: center; margin-top: 8px;
}}
.reaction {{
  font-size: 26px; background: none; border: none;
  cursor: pointer; transition: transform 0.2s;
  filter: grayscale(0.6) brightness(0.8);
  padding: 4px;
}}
.reaction:active {{ transform: scale(1.5); }}
.reaction.selected {{ filter: none; transform: scale(1.2); }}

/* Share button */
.share-btn {{
  font-size: 12px; color: #666; font-family: 'Inter', sans-serif;
  cursor: pointer; padding: 6px 16px; border: 1px solid #2a2a2a;
  border-radius: 16px; transition: all 0.2s; margin-top: 4px;
}}
.share-btn:hover {{ color: #c9a96e; border-color: #c9a96e; }}

/* ─── Location tag ─── */
.location-tag {{
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(201,169,110,0.1); padding: 3px 10px;
  border-radius: 10px; font-size: 11px;
  font-family: 'Inter', sans-serif; color: #c9a96e;
  margin-bottom: 10px;
}}

.slide-counter {{
  position: absolute; top: 24px; right: 52px; z-index: 10;
  font-size: 10px; color: rgba(255,255,255,0.3);
  font-family: 'Inter', sans-serif;
}}

.nav-left, .nav-right {{
  position: absolute; top: 0; height: 100%; z-index: 5; cursor: pointer;
}}
.nav-left {{ left: 0; width: 25%; }}
.nav-right {{ right: 0; width: 75%; }}

.close-btn {{
  position: absolute; top: 10px; right: 12px; z-index: 10;
  color: rgba(255,255,255,0.6); font-size: 18px; cursor: pointer;
  width: 32px; height: 32px; display: flex; align-items: center;
  justify-content: center; background: rgba(0,0,0,0.3); border-radius: 50%;
  font-family: 'Inter', sans-serif; backdrop-filter: blur(4px);
}}
.close-btn:hover {{ color: white; }}

/* ─── Desktop / Tablet layout ─── */
/* MOBILE-FIRST: everything below 768px is default (full-screen stories) */

/* Peek panels hidden by default (mobile) */
.peek-prev, .peek-next {{ display: none; }}

@media (min-width: 768px) {{
  /* Center the feed */
  .stories-bar {{
    max-width: 600px; width: 600px;
    left: 50% !important; right: auto !important;
    transform: translateX(-50%);
  }}
  .feed {{
    max-width: 600px; width: 100%; margin: 0 auto;
  }}
  .feed-lead {{ border-radius: 16px; }}
  .feed-lead img {{ height: 340px; }}

  /* Story viewer: phone-frame centered with backdrop */
  .story-viewer {{
    background: rgba(0,0,0,0.92);
    backdrop-filter: blur(30px); -webkit-backdrop-filter: blur(30px);
    align-items: center; justify-content: center;
  }}
  .story-viewer .story-frame {{
    position: relative; flex: none;
    width: 360px; height: min(92vh, 640px);
    border-radius: 16px; overflow: hidden;
    background: #08080d;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.06), 0 20px 80px rgba(0,0,0,0.6);
    display: flex; flex-direction: column;
  }}
  .story-viewer .progress-bar-container {{
    position: absolute; top: 0; left: 0; right: 0; z-index: 10;
    border-radius: 16px 16px 0 0;
  }}
  .story-viewer .close-btn {{
    position: absolute; top: 14px; right: 14px; z-index: 10;
  }}
  .story-viewer .slide-counter {{
    position: absolute; top: 28px; right: 56px; z-index: 10;
  }}
  .story-viewer .nav-left,
  .story-viewer .nav-right {{
    position: absolute; top: 0; height: 100%; z-index: 5;
  }}
  .story-viewer .nav-left {{ left: 0; width: 25%; }}
  .story-viewer .nav-right {{ right: 0; width: 75%; }}
  .story-card .card-bg {{
    border-radius: 16px;
  }}
}}

/* ─── Wide desktop: 3-panel AMP-style layout ─── */
@media (min-width: 1024px) {{
  .stories-bar {{
    max-width: 800px; width: 800px;
  }}
  .feed {{
    max-width: 800px;
  }}

  /* 3-panel: prev | current | next */
  .story-viewer {{
    flex-direction: row; gap: 20px;
  }}
  .story-viewer .story-frame {{
    width: 340px; height: min(94vh, 605px);
    border-radius: 14px;
  }}
  /* Peek panels: prev/next story preview */
  .peek-prev, .peek-next {{
    display: block;
    width: 200px; height: min(76vh, 490px);
    border-radius: 12px; overflow: hidden;
    position: relative; flex-shrink: 0;
    opacity: 0.35; transition: opacity 0.3s;
    cursor: pointer; align-self: center;
  }}
  .peek-prev:hover, .peek-next:hover {{ opacity: 0.55; }}
  .peek-prev img, .peek-next img {{
    width: 100%; height: 100%; object-fit: cover;
    border-radius: 12px;
  }}
  .peek-prev .peek-label, .peek-next .peek-label {{
    position: absolute; bottom: 0; left: 0; right: 0;
    padding: 16px 12px 14px;
    background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 100%);
    font-family: 'Playfair Display', serif; font-size: 13px;
    line-height: 1.3; color: #f0ece4;
    border-radius: 0 0 12px 12px;
  }}
}}

/* ─── Ultra-wide: larger panels ─── */
@media (min-width: 1200px) {{
  .stories-bar {{ max-width: 900px; width: 900px; }}
  .feed {{ max-width: 900px; }}
  .story-viewer .story-frame {{
    width: 380px; height: min(94vh, 675px);
  }}
  .peek-prev, .peek-next {{
    width: 240px; height: min(80vh, 540px);
  }}
}}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {{
  .card-bg, .card-content, .story-card.active .card-bg,
  .story-card.active[data-type] .card-content,
  .story-card.active[data-type="title"] .card-category,
  .story-card.active[data-type="title"] .card-title,
  .story-card.active[data-type="title"] .card-summary,
  .story-card.active[data-type="title"] .card-meta {{
    animation: none !important;
  }}
}}
</style>
</head>
<body>

<div class="stories-bar" id="storiesBar">
  <div class="brand">DISPATCH</div>
</div>

<div class="feed" id="feed">
  <div class="feed-header">
    <h1>Arlo's Dispatch</h1>
    <span class="date">{datetime.now().strftime("%b %d, %Y")}</span>
  </div>
</div>

<div class="story-viewer" id="storyViewer" onclick="if(event.target===this)closeStory()">
  <div class="peek-prev" id="peekPrev" onclick="peekPrevClick()">
    <img src="" alt="">
    <div class="peek-label"></div>
  </div>
  <div class="story-frame">
    <div class="progress-bar-container" id="progressBars"></div>
    <div class="slide-counter" id="slideCounter"></div>
    <div class="close-btn" onclick="closeStory()">✕</div>
    <div id="cardsContainer" style="flex:1;display:flex;flex-direction:column;"></div>
    <div class="nav-left" onclick="prevCard()"></div>
    <div class="nav-right" onclick="nextCard()"></div>
  </div>
  <div class="peek-next" id="peekNext" onclick="peekNextClick()">
    <img src="" alt="">
    <div class="peek-label"></div>
  </div>
</div>

<script>
const CAT = {json.dumps(CAT_EMOJIS)};
const stories = {stories_json};

let curStory = -1, curCard = 0, totalCards = 0, timer = null, paused = false;

function timeAgo(dateStr) {{
  const d = new Date(dateStr.replace(' ', 'T'));
  const h = Math.floor((Date.now() - d) / 3600000);
  if (h < 1) return 'Just now';
  if (h < 24) return h + 'h ago';
  const days = Math.floor(h / 24);
  if (days < 7) return days + 'd ago';
  return d.toLocaleDateString('en-US', {{month:'short', day:'numeric'}});
}}

function init() {{
  const bar = document.getElementById('storiesBar');
  const feed = document.getElementById('feed');
  
  // Group: latest first as lead, rest as compact
  stories.forEach((s, i) => {{
    const img = s.images[0] || '';
    // Thumbnails
    bar.innerHTML += `
      <div class="story-thumb" id="thumb-${{i}}" onclick="openStory(${{i}})">
        <div class="ring"><img src="images/${{img}}" alt="" loading="lazy"></div>
        <span class="label">${{CAT[s.category]||'📰'}} ${{s.category}}</span>
      </div>`;
    
    // Feed
    if (i === 0) {{
      feed.innerHTML += `
        <div class="feed-lead" onclick="openStory(0)">
          <img src="images/${{img}}" alt="" loading="lazy">
          <div class="overlay">
            <div class="feed-cat">${{CAT[s.category]||'📰'}} ${{s.category}}</div>
            <h3>${{s.title}}</h3>
            <p>${{s.summary.slice(0,140)}}…</p>
          </div>
        </div>
        <div class="feed-section">Latest</div>`;
    }} else {{
      feed.innerHTML += `
        <div class="feed-card" onclick="openStory(${{i}})">
          <img src="images/${{img}}" alt="" loading="lazy">
          <div class="info">
            <div class="feed-cat">${{CAT[s.category]||'📰'}} ${{s.category}}</div>
            <h3>${{s.title}}</h3>
            <span class="time">${{timeAgo(s.published)}}</span>
          </div>
        </div>`;
    }}
  }});
  
  feed.innerHTML += `
    <div class="feed-footer">
      🦞 Written by Arlo — an AI that reads everything so you don't have to.<br>
      <a href="signal-noise.html">Play Signal / Noise →</a>
    </div>`;
}}

function parseCards(s) {{
  const cards = [{{type:'title'}}];
  const paras = s.content.split('\\n').filter(p => p.trim());
  let buf = '';
  let firstText = true;

  for (let p of paras) {{
    p = p.trim();
    // Quote card
    if (p.startsWith('>>')) {{
      if (buf) {{ cards.push({{type:'text', text:buf.trim(), firstText}}); if(firstText) firstText=false; buf=''; }}
      cards.push({{type:'quote', text:p.replace(/^>>\\s*/, '')}});
      continue;
    }}
    // Stat card: ## 32,000 | Label
    if (p.startsWith('## ')) {{
      if (buf) {{ cards.push({{type:'text', text:buf.trim(), firstText}}); if(firstText) firstText=false; buf=''; }}
      const parts = p.replace(/^##\\s*/, '').split('|').map(x => x.trim());
      cards.push({{type:'stat', number: parts[0], label: parts[1] || ''}});
      continue;
    }}
    // Takeaway card: !! text
    if (p.startsWith('!! ')) {{
      if (buf) {{ cards.push({{type:'text', text:buf.trim(), firstText}}); if(firstText) firstText=false; buf=''; }}
      cards.push({{type:'takeaway', text:p.replace(/^!!\\s*/, '')}});
      continue;
    }}
    // Regular text
    if ((buf + '\\n\\n' + p).length > 320 && buf) {{
      cards.push({{type:'text', text:buf.trim(), firstText}});
      if(firstText) firstText=false;
      buf = p;
    }} else {{
      buf += (buf ? '\\n\\n' : '') + p;
    }}
  }}
  if (buf.trim()) {{ cards.push({{type:'text', text:buf.trim(), firstText}}); }}
  cards.push({{type:'end'}});
  return cards.slice(0, 14);
}}

// Ken Burns pattern: alternate between effects
const KB_PATTERNS = ['zoom-in','zoom-out','pan-left','pan-right'];
function getKB(cardIndex) {{
  return KB_PATTERNS[cardIndex % KB_PATTERNS.length];
}}

// Card duration by type
function getCardDuration(type) {{
  if (type === 'stat' || type === 'takeaway') return 6000;
  if (type === 'end') return 999999;
  return 8000;
}}

function formatText(txt) {{
  // Bold → gold strong
  txt = txt.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
  // ==highlight== → mark
  txt = txt.replace(/==(.+?)==/g, '<mark>$1</mark>');
  // 📍 Location → location tag
  txt = txt.replace(/📍\\s*(.+?)(?:\\n|$)/g, '<div class="location-tag">$1</div>');
  return txt;
}}

function buildCards(idx) {{
  const s = stories[idx];
  const container = document.getElementById('cardsContainer');
  const progress = document.getElementById('progressBars');
  container.innerHTML = ''; progress.innerHTML = '';

  const cards = parseCards(s);
  totalCards = cards.length;
  const images = s.images || [];

  for (let i = 0; i < cards.length; i++) {{
    const seg = document.createElement('div');
    seg.className = 'progress-segment';
    seg.innerHTML = '<div class="fill"></div>';
    progress.appendChild(seg);

    const card = document.createElement('div');
    card.className = 'story-card';
    const c = cards[i];

    // Set card type as data attribute for CSS targeting
    card.setAttribute('data-type', c.type);

    const img = images[i] || images[i % images.length] || images[0] || '';
    const kb = getKB(i);

    if (c.type === 'end') {{
      card.innerHTML = `
        <div class="card-bg" style="background-image:url(images/${{img}});filter:blur(6px) brightness(0.25);"></div>
        <div class="card-content card-end">
          <div class="end-logo">🦞</div>
          <div class="end-line"></div>
          <div class="end-title">Arlo's Dispatch</div>
          <div class="reaction-bar">
            <button class="reaction" onclick="react(this,'🔥')">🔥</button>
            <button class="reaction" onclick="react(this,'💡')">💡</button>
            <button class="reaction" onclick="react(this,'😮')">😮</button>
            <button class="reaction" onclick="react(this,'👏')">👏</button>
          </div>
          <div class="end-next" onclick="${{idx < stories.length - 1 ? `openStory(${{idx+1}})` : 'closeStory()'}}">
            ${{idx < stories.length - 1 ? 'Next story →' : 'Back to feed'}}
          </div>
          <div class="share-btn" onclick="shareStory(${{idx}})">Share this story</div>
        </div>`;
    }} else if (c.type === 'stat') {{
      card.innerHTML = `
        <div class="card-bg" data-kb="${{kb}}" style="background-image:url(images/${{img}})"></div>
        <div class="card-content">
          <div class="stat-number">${{c.number}}</div>
          <div class="stat-label">${{c.label}}</div>
        </div>`;
    }} else if (c.type === 'takeaway') {{
      card.innerHTML = `
        <div class="card-bg" data-kb="${{kb}}" style="background-image:url(images/${{img}})"></div>
        <div class="card-content">
          <div class="takeaway-box">
            <div class="takeaway-label">⚡ Key Takeaway</div>
            <div class="takeaway-text">${{formatText(c.text)}}</div>
          </div>
        </div>`;
    }} else if (c.type === 'quote') {{
      // Split quote and attribution if " — " exists
      let quoteText = c.text;
      let attr = '';
      const dashIdx = quoteText.lastIndexOf(' — ');
      if (dashIdx > 0) {{
        attr = quoteText.slice(dashIdx + 3);
        quoteText = quoteText.slice(0, dashIdx);
      }}
      card.innerHTML = `
        <div class="card-bg" data-kb="${{kb}}" style="background-image:url(images/${{img}})"></div>
        <div class="card-content">
          <div class="card-text quote">${{quoteText}}${{attr ? `<span class="quote-attr">— ${{attr}}</span>` : ''}}</div>
        </div>`;
    }} else if (c.type === 'title') {{
      card.innerHTML = `
        <div class="card-bg" data-kb="zoom-in" style="background-image:url(images/${{img}})"></div>
        <div class="card-content">
          <div class="card-category">${{CAT[s.category]||'📰'}} ${{s.category}}</div>
          <div class="card-title">${{s.title}}</div>
          <div class="card-summary">${{s.summary}}</div>
          <div class="card-meta">By ${{s.writer}} · Arlo's Dispatch</div>
        </div>`;
    }} else {{
      // Text card
      if (c.firstText) card.setAttribute('data-first-text', 'true');
      const txt = formatText(c.text);
      card.innerHTML = `
        <div class="card-bg" data-kb="${{kb}}" style="background-image:url(images/${{img}})"></div>
        <div class="card-content">
          <div class="card-text">${{txt}}</div>
        </div>`;
    }}

    container.appendChild(card);
  }}
  return totalCards;
}}

function showCard(idx) {{
  const cards = document.querySelectorAll('.story-card');
  const segs = document.querySelectorAll('.progress-segment');
  if (idx < 0 || idx >= cards.length) return;

  cards.forEach((c, i) => {{
    if (i === idx) {{
      c.classList.add('active');
      // Re-trigger Ken Burns by cloning bg
      const bg = c.querySelector('.card-bg[data-kb]');
      if (bg) {{
        const clone = bg.cloneNode(true);
        bg.parentNode.replaceChild(clone, bg);
      }}
    }} else {{
      c.classList.remove('active');
    }}
  }});
  segs.forEach((s, i) => {{
    s.classList.remove('active', 'done');
    if (i < idx) s.classList.add('done');
    if (i === idx) s.classList.add('active');
  }});

  curCard = idx;
  document.getElementById('slideCounter').textContent = `${{idx+1}}/${{totalCards}}`;

  // Duration based on card type
  const activeCard = document.querySelectorAll('.story-card')[idx];
  const cardType = activeCard?.getAttribute('data-type') || 'text';
  const duration = getCardDuration(cardType);

  // Set CSS variable for progress bar timing
  activeCard?.closest('.story-viewer')?.style.setProperty('--card-duration', (duration/1000) + 's');
  const activeSeg = document.querySelectorAll('.progress-segment')[idx];
  if (activeSeg) activeSeg.style.setProperty('--card-duration', (duration/1000) + 's');

  clearTimeout(timer);
  if (!paused && cardType !== 'end') timer = setTimeout(nextCard, duration);
}}

function react(btn, emoji) {{
  btn.classList.toggle('selected');
  // Simple haptic feedback on mobile
  if (navigator.vibrate) navigator.vibrate(30);
}}

function shareStory(idx) {{
  const s = stories[idx];
  if (navigator.share) {{
    navigator.share({{
      title: s.title,
      text: s.summary,
      url: window.location.href
    }}).catch(() => {{}});
  }} else {{
    // Fallback: copy to clipboard
    navigator.clipboard?.writeText(window.location.href);
    const btn = document.querySelector('.share-btn');
    if (btn) {{ btn.textContent = 'Link copied!'; setTimeout(() => btn.textContent = 'Share this story', 2000); }}
  }}
}}

function updatePeekPanels(idx) {{
  const prev = document.getElementById('peekPrev');
  const next = document.getElementById('peekNext');
  if (!prev || !next) return;

  if (idx > 0) {{
    const ps = stories[idx - 1];
    prev.querySelector('img').src = 'images/' + (ps.images[0] || '');
    prev.querySelector('.peek-label').textContent = ps.title;
    prev.style.visibility = 'visible';
  }} else {{
    prev.style.visibility = 'hidden';
  }}

  if (idx < stories.length - 1) {{
    const ns = stories[idx + 1];
    next.querySelector('img').src = 'images/' + (ns.images[0] || '');
    next.querySelector('.peek-label').textContent = ns.title;
    next.style.visibility = 'visible';
  }} else {{
    next.style.visibility = 'hidden';
  }}
}}

function peekPrevClick() {{
  if (curStory > 0) openStory(curStory - 1);
}}
function peekNextClick() {{
  if (curStory < stories.length - 1) openStory(curStory + 1);
}}

function openStory(idx) {{
  curStory = idx;
  buildCards(idx);
  document.getElementById('storyViewer').classList.add('active');
  showCard(0);
  updatePeekPanels(idx);
  document.getElementById('thumb-' + idx)?.classList.add('viewed');
}}

function closeStory() {{
  clearTimeout(timer);
  document.getElementById('storyViewer').classList.remove('active');
  curStory = -1;
}}

function nextCard() {{
  if (curCard < totalCards - 1) showCard(curCard + 1);
  else if (curStory < stories.length - 1) openStory(curStory + 1);
  else closeStory();
}}

function prevCard() {{
  if (curCard > 0) showCard(curCard - 1);
  else if (curStory > 0) {{ openStory(curStory - 1); showCard(totalCards - 1); }}
}}

// Hold to pause
let holdT = null;
document.addEventListener('touchstart', () => {{
  if (curStory < 0) return;
  holdT = setTimeout(() => {{ paused = true; clearTimeout(timer); }}, 250);
}});
document.addEventListener('touchend', () => {{
  clearTimeout(holdT);
  if (paused) {{ paused = false; timer = setTimeout(nextCard, 4000); }}
}});

// Keyboard
document.addEventListener('keydown', e => {{
  if (curStory < 0) return;
  if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); nextCard(); }}
  if (e.key === 'ArrowLeft') {{ e.preventDefault(); prevCard(); }}
  if (e.key === 'Escape') closeStory();
}});

init();
</script>
</body>
</html>'''

# Write
with open(os.path.join(OUT, "index.html"), 'w') as f:
    f.write(html)

print(f"Built index.html: {len(valid_stories)} stories, {os.path.getsize(os.path.join(OUT, 'index.html'))//1024}KB")
