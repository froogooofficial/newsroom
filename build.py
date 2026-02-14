#!/usr/bin/env python3
"""Static site generator for The Newsroom"""
import json, os, glob, re
from datetime import datetime

OUT = "docs"  # GitHub Pages serves from /docs
os.makedirs(OUT, exist_ok=True)

# Load all stories
stories = []
for f in sorted(glob.glob("stories/*.json"), reverse=True):
    with open(f) as fh:
        stories.append(json.load(fh))

categories = ["world", "tech", "science", "business", "politics", "health", "culture", "sports", "opinion"]
cat_labels = {
    "world": "🌍 World", "tech": "💻 Tech", "science": "🔬 Science",
    "business": "💰 Business", "politics": "🏛️ Politics", "health": "🏥 Health",
    "culture": "🎭 Culture", "sports": "⚽ Sports", "opinion": "💬 Opinion"
}

def format_date(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except:
        return dt_str

def story_slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s['title'].lower()).strip('-')[:60]

STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Serif+4:wght@400;600&family=Inter:wght@400;500;600&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    font-family: 'Source Serif 4', Georgia, serif;
    background: #faf9f6;
    color: #1a1a1a;
    line-height: 1.6;
  }

  header {
    text-align: center;
    padding: 2rem 1rem 1rem;
    border-bottom: 4px double #1a1a1a;
    margin-bottom: 0.5rem;
    background: #faf9f6;
  }

  header h1 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 3.5rem;
    font-weight: 900;
    letter-spacing: -1px;
    text-transform: uppercase;
  }

  header .tagline {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: #666;
    margin-top: 0.3rem;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  header .date-line {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: #999;
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px solid #ddd;
  }

  nav {
    display: flex;
    justify-content: center;
    gap: 0.3rem;
    padding: 0.8rem 1rem;
    border-bottom: 1px solid #ddd;
    flex-wrap: wrap;
    background: #faf9f6;
    position: sticky;
    top: 0;
    z-index: 100;
  }

  nav a {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    text-decoration: none;
    color: #1a1a1a;
    padding: 0.3rem 0.7rem;
    border-radius: 3px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
    transition: background 0.2s;
  }

  nav a:hover, nav a.active {
    background: #1a1a1a;
    color: #faf9f6;
  }

  .container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
  }

  /* Homepage grid */
  .lead-story {
    border-bottom: 2px solid #1a1a1a;
    padding-bottom: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .lead-story h2 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 0.5rem;
  }

  .lead-story h2 a {
    color: #1a1a1a;
    text-decoration: none;
  }

  .lead-story h2 a:hover {
    text-decoration: underline;
  }

  .lead-story .summary {
    font-size: 1.15rem;
    color: #333;
    line-height: 1.5;
  }

  .lead-story .meta {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: #999;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .stories-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .story-card {
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 1.2rem;
  }

  .story-card h3 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1.25;
    margin-bottom: 0.4rem;
  }

  .story-card h3 a {
    color: #1a1a1a;
    text-decoration: none;
  }

  .story-card h3 a:hover {
    text-decoration: underline;
  }

  .story-card .summary {
    font-size: 0.95rem;
    color: #444;
    line-height: 1.45;
  }

  .story-card .meta {
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: #999;
    margin-bottom: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .cat-badge {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    padding: 0.15rem 0.5rem;
    border-radius: 2px;
    background: #1a1a1a;
    color: #faf9f6;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
  }

  /* Article page */
  article.full {
    max-width: 720px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  article.full h1 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 0.5rem;
  }

  article.full .article-meta {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: #999;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #ddd;
  }

  article.full .article-summary {
    font-size: 1.2rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 1.5rem;
    line-height: 1.5;
  }

  article.full .article-body {
    font-size: 1.1rem;
    line-height: 1.8;
  }

  article.full .article-body p {
    margin-bottom: 1.2rem;
  }

  .back-link {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    display: inline-block;
    margin-bottom: 1.5rem;
  }

  .back-link a {
    color: #666;
    text-decoration: none;
  }

  .back-link a:hover {
    color: #1a1a1a;
  }

  footer {
    text-align: center;
    padding: 2rem;
    border-top: 2px solid #1a1a1a;
    margin-top: 2rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: #999;
  }

  @media (max-width: 600px) {
    header h1 { font-size: 2.2rem; }
    .lead-story h2 { font-size: 1.6rem; }
    .stories-grid { grid-template-columns: 1fr; }
    article.full h1 { font-size: 1.8rem; }
  }
</style>
"""

def nav_html(active_cat=None):
    links = ['<a href="index.html"' + (' class="active"' if active_cat is None else '') + '>All</a>']
    for cat in categories:
        cat_stories = [s for s in stories if s["category"] == cat]
        if cat_stories:
            active = ' class="active"' if active_cat == cat else ''
            links.append(f'<a href="cat-{cat}.html"{active}>{cat.title()}</a>')
    return "<nav>" + "".join(links) + "</nav>"

def page_head(title="The Newsroom"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — The Newsroom</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📰</text></svg>">
  {STYLE}
</head>
<body>
<header>
  <h1>The Newsroom</h1>
  <div class="tagline">AI-Powered Journalism</div>
  <div class="date-line">Built {datetime.now().strftime("%B %d, %Y")}</div>
</header>
"""

def page_foot():
    return """
<footer>
  The Newsroom — Written by AI agents, read by humans.<br>
  Built by <strong>Arlo</strong> 🤖
</footer>
</body>
</html>"""

def render_index(story_list, title="The Newsroom", filename="index.html", active_cat=None):
    html = page_head(title)
    html += nav_html(active_cat)
    html += '<div class="container">\n'

    if story_list:
        lead = story_list[0]
        slug = story_slug(lead)
        html += f"""
<div class="lead-story">
  <div class="meta"><span class="cat-badge">{lead['category']}</span> · {lead['writer']} · {format_date(lead['published'])}</div>
  <h2><a href="story-{slug}.html">{lead['title']}</a></h2>
  <p class="summary">{lead['summary']}</p>
</div>
"""
        if len(story_list) > 1:
            html += '<div class="stories-grid">\n'
            for s in story_list[1:]:
                slug = story_slug(s)
                html += f"""
<div class="story-card">
  <div class="meta"><span class="cat-badge">{s['category']}</span> · {format_date(s['published'])}</div>
  <h3><a href="story-{slug}.html">{s['title']}</a></h3>
  <p class="summary">{s['summary']}</p>
</div>
"""
            html += '</div>\n'

    html += '</div>\n'
    html += page_foot()

    with open(f"{OUT}/{filename}", "w") as f:
        f.write(html)
    print(f"  Built {filename}")

def render_story(s):
    slug = story_slug(s)
    content_html = "".join(f"<p>{p}</p>" for p in s['content'].split('\n\n') if p.strip())

    html = page_head(s['title'])
    html += nav_html()
    html += f"""
<article class="full">
  <div class="back-link"><a href="index.html">← Back to headlines</a></div>
  <div class="article-meta">
    <span class="cat-badge">{s['category']}</span> · {s['writer']} · {format_date(s['published'])}
  </div>
  <h1>{s['title']}</h1>
  <p class="article-summary">{s['summary']}</p>
  <div class="article-body">
    {content_html}
  </div>
</article>
"""
    html += page_foot()

    with open(f"{OUT}/story-{slug}.html", "w") as f:
        f.write(html)
    print(f"  Built story-{slug}.html")

# Build!
print("Building The Newsroom...\n")

# Main index
render_index(stories)

# Category pages
for cat in categories:
    cat_stories = [s for s in stories if s["category"] == cat]
    if cat_stories:
        render_index(cat_stories, f"{cat.title()} — The Newsroom", f"cat-{cat}.html", active_cat=cat)

# Individual story pages
for s in stories:
    render_story(s)

print(f"\n✅ Built {len(stories)} stories + {sum(1 for c in categories if any(s['category']==c for s in stories))} category pages + index")
