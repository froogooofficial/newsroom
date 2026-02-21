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

.story-card {{
  flex: 1; display: none; position: relative; overflow: hidden;
}}
.story-card.active {{
  display: flex; flex-direction: column; justify-content: flex-end;
  animation: cardIn 0.2s ease;
}}
@keyframes cardIn {{ from {{ opacity: 0.6; transform: scale(1.01); }} to {{ opacity: 1; transform: scale(1); }} }}

.card-bg {{
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background-size: cover; background-position: center top;
  z-index: 0; transition: opacity 0.3s;
}}
.card-bg::after {{
  content: ''; position: absolute; bottom: 0; left: 0; right: 0;
  height: 80%;
  background: linear-gradient(to top, rgba(8,8,13,0.97) 0%, rgba(8,8,13,0.6) 45%, transparent 100%);
  z-index: 1;
}}

.card-content {{
  position: relative; z-index: 2;
  padding: 20px 22px 48px;
  max-height: 60vh; overflow: hidden;
}}
.card-category {{
  font-size: 11px; text-transform: uppercase; letter-spacing: 2.5px;
  color: #c9a96e; margin-bottom: 10px; font-family: 'Inter', sans-serif;
  font-weight: 600;
}}
.card-title {{
  font-size: 28px; line-height: 1.2; font-weight: 700;
  margin-bottom: 14px; text-shadow: 0 2px 16px rgba(0,0,0,0.9);
  font-family: 'Playfair Display', serif;
}}
.card-summary {{
  font-size: 15px; line-height: 1.55; color: #ccc;
  text-shadow: 0 1px 6px rgba(0,0,0,0.8);
}}
.card-text {{
  font-size: 16px; line-height: 1.7; color: #e0dcd4;
  text-shadow: 0 1px 4px rgba(0,0,0,0.8);
}}
.card-text.quote {{
  font-style: italic; font-size: 21px; line-height: 1.45;
  border-left: 3px solid #c9a96e; padding-left: 18px;
  color: #f0ece4;
}}
.card-text strong {{ color: #c9a96e; }}
.card-meta {{
  font-size: 11px; color: #666; margin-top: 14px;
  font-family: 'Inter', sans-serif; letter-spacing: 0.3px;
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

/* End card */
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

/* Desktop constraint */
@media (min-width: 500px) {{
  .story-viewer {{ max-width: 420px; margin: 0 auto; box-shadow: 0 0 60px rgba(0,0,0,0.5); }}
  .feed {{ max-width: 500px; margin: 0 auto; }}
  .stories-bar {{ max-width: 500px; margin: 0 auto; left: auto; }}
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

<div class="story-viewer" id="storyViewer">
  <div class="progress-bar-container" id="progressBars"></div>
  <div class="slide-counter" id="slideCounter"></div>
  <div class="close-btn" onclick="closeStory()">✕</div>
  <div id="cardsContainer" style="flex:1;display:flex;flex-direction:column;"></div>
  <div class="nav-left" onclick="prevCard()"></div>
  <div class="nav-right" onclick="nextCard()"></div>
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
  
  for (let p of paras) {{
    p = p.trim();
    if (p.startsWith('>>')) {{
      if (buf) {{ cards.push({{type:'text', text:buf.trim()}}); buf=''; }}
      cards.push({{type:'quote', text:p.replace(/^>>\\s*/, '')}});
      continue;
    }}
    if ((buf + '\\n\\n' + p).length > 320 && buf) {{
      cards.push({{type:'text', text:buf.trim()}});
      buf = p;
    }} else {{
      buf += (buf ? '\\n\\n' : '') + p;
    }}
  }}
  if (buf.trim()) cards.push({{type:'text', text:buf.trim()}});
  cards.push({{type:'end'}});
  return cards.slice(0, 12);
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
    // Progress bar
    const seg = document.createElement('div');
    seg.className = 'progress-segment';
    seg.innerHTML = '<div class="fill"></div>';
    progress.appendChild(seg);
    
    // Card
    const card = document.createElement('div');
    card.className = 'story-card';
    const c = cards[i];
    
    // Pick image: use card-specific image or cycle through available
    const img = images[i] || images[i % images.length] || images[0] || '';
    
    if (c.type === 'end') {{
      card.innerHTML = `
        <div class="card-bg" style="background-image:url(images/${{img}});filter:blur(6px) brightness(0.25);"></div>
        <div class="card-content card-end">
          <div class="end-logo">🦞</div>
          <div class="end-line"></div>
          <div class="end-title">Arlo's Dispatch</div>
          <div class="end-next" onclick="${{idx < stories.length - 1 ? `openStory(${{idx+1}})` : 'closeStory()'}}">
            ${{idx < stories.length - 1 ? 'Next story →' : 'Back to feed'}}
          </div>
        </div>`;
    }} else {{
      const bgStyle = `background-image:url(images/${{img}})`;
      let inner = '';
      
      if (c.type === 'title') {{
        inner = `
          <div class="card-category">${{CAT[s.category]||'📰'}} ${{s.category}}</div>
          <div class="card-title">${{s.title}}</div>
          <div class="card-summary">${{s.summary}}</div>
          <div class="card-meta">By ${{s.writer}} · Arlo's Dispatch</div>`;
      }} else if (c.type === 'quote') {{
        inner = `<div class="card-text quote">${{c.text}}</div>`;
      }} else {{
        const txt = c.text.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
        inner = `<div class="card-text">${{txt}}</div>`;
      }}
      
      card.innerHTML = `
        <div class="card-bg" style="${{bgStyle}}"></div>
        <div class="card-content">${{inner}}</div>`;
    }}
    
    container.appendChild(card);
  }}
  return totalCards;
}}

function showCard(idx) {{
  const cards = document.querySelectorAll('.story-card');
  const segs = document.querySelectorAll('.progress-segment');
  if (idx < 0 || idx >= cards.length) return;
  
  cards.forEach((c, i) => c.classList.toggle('active', i === idx));
  segs.forEach((s, i) => {{
    s.classList.remove('active', 'done');
    if (i < idx) s.classList.add('done');
    if (i === idx) s.classList.add('active');
  }});
  
  curCard = idx;
  document.getElementById('slideCounter').textContent = `${{idx+1}}/${{totalCards}}`;
  
  clearTimeout(timer);
  if (!paused) timer = setTimeout(nextCard, 8000);
}}

function openStory(idx) {{
  curStory = idx;
  buildCards(idx);
  document.getElementById('storyViewer').classList.add('active');
  showCard(0);
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
