#!/usr/bin/env python3
"""
Generate multiple images per story for the Stories format.
Uses flux-schnell (fast & cheap) via Replicate.
Each story gets images for each card/slide.
"""
import json, os, sys, re, subprocess, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "images")
os.makedirs(IMAGES_DIR, exist_ok=True)


def generate_image_fast(prompt, output_path, aspect="9:16"):
    """Generate image with flux-schnell (fastest, cheapest).
    Default 9:16 for phone-first stories format."""
    url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
    headers = {
        "Authorization": f"Bearer {REPLICATE_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "wait"
    }
    data = json.dumps({
        "input": {
            "prompt": f"Editorial photograph, cinematic lighting, dramatic: {prompt}",
            "aspect_ratio": aspect,
            "num_outputs": 1
        }
    }).encode()
    
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        result = json.loads(urllib.request.urlopen(req, timeout=60).read())
        img_url = result.get("output", [None])[0]
        if not img_url:
            print(f"  ⚠ No image returned for: {prompt[:50]}")
            return False
        
        # Download
        png_path = output_path.replace('.jpg', '.png')
        urllib.request.urlretrieve(img_url, png_path)
        
        # Convert to compressed JPEG
        subprocess.run(
            ['ffmpeg', '-y', '-i', png_path, '-q:v', '5', output_path],
            capture_output=True, text=True
        )
        
        # Cleanup PNG
        if os.path.exists(output_path) and os.path.exists(png_path):
            os.remove(png_path)
        
        size_kb = os.path.getsize(output_path) // 1024
        print(f"  ✓ {os.path.basename(output_path)} ({size_kb}KB)")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def split_story_to_cards(content, max_chars=320):
    """Split story content into cards (same logic as the viewer)."""
    paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
    cards = []
    buf = ''
    
    for p in paragraphs:
        if p.startswith('>>'):
            if buf:
                cards.append({'type': 'text', 'text': buf.strip()})
                buf = ''
            cards.append({'type': 'quote', 'text': p.replace('>>', '').strip()})
            continue
        
        if len(buf + '\n\n' + p) > max_chars and buf:
            cards.append({'type': 'text', 'text': buf.strip()})
            buf = p
        else:
            buf += ('\n\n' if buf else '') + p
    
    if buf.strip():
        cards.append({'type': 'text', 'text': buf.strip()})
    
    return cards[:10]


def generate_image_prompts(story):
    """Create image prompts for each card of a story."""
    title = story['title']
    category = story.get('category', 'world')
    cards = split_story_to_cards(story['content'])
    
    prompts = []
    
    # Title card - hero image
    prompts.append(f"{title}, editorial news photography, dramatic angle")
    
    # Content cards - extract key visual from each
    for card in cards:
        text = card['text']
        # Extract the most visual/concrete sentence
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 20]
        if sentences:
            # Pick the most concrete/visual sentence
            best = max(sentences, key=lambda s: sum(1 for w in ['strike', 'fire', 'crowd', 'building', 'soldier', 'court', 'city', 'night', 'ship', 'missile', 'protest', 'sky', 'ocean', 'mountain', 'flag', 'rocket', 'lab', 'office', 'street'] if w in s.lower()))
            prompts.append(f"{best}, photojournalistic style, cinematic")
        else:
            prompts.append(f"{title}, abstract editorial illustration, {category}")
    
    return prompts


def generate_story_images(story, force=False):
    """Generate all images for a story. Returns list of image filenames.
    
    Skips generation if images already exist (unless force=True).
    """
    story_id = story['id']
    slug = re.sub(r'[^a-z0-9]+', '-', story['title'].lower()).strip('-')[:40]
    
    cards = split_story_to_cards(story['content'])
    total_cards = len(cards) + 1  # +1 for title card
    
    # Check existing images
    existing = []
    for i in range(total_cards):
        fname = f"story-{story_id:03d}-{i}.jpg"
        fpath = os.path.join(IMAGES_DIR, fname)
        if os.path.exists(fpath) and not force:
            existing.append(fname)
        else:
            existing.append(None)
    
    if all(existing) and not force:
        print(f"  Story {story_id}: all {total_cards} images exist, skipping")
        return existing
    
    prompts = generate_image_prompts(story)
    
    # Ensure we have enough prompts
    while len(prompts) < total_cards:
        prompts.append(f"{story['title']}, abstract editorial, moody atmospheric")
    
    filenames = []
    for i in range(total_cards):
        fname = f"story-{story_id:03d}-{i}.jpg"
        fpath = os.path.join(IMAGES_DIR, fname)
        
        if existing[i] and not force:
            filenames.append(fname)
            continue
        
        print(f"  Generating image {i+1}/{total_cards} for story {story_id}...")
        ok = generate_image_fast(prompts[i], fpath, aspect="9:16")
        
        if ok:
            filenames.append(fname)
        else:
            # Fall back to hero image or first successful image
            fallback = next((f for f in filenames if f), story.get('image_file', ''))
            filenames.append(fallback)
        
        time.sleep(0.3)  # Brief pause between API calls
    
    return filenames


def update_story_json(story_path, images):
    """Update story JSON with multi-image list."""
    with open(story_path) as f:
        story = json.load(f)
    
    story['images'] = images
    # Keep image_file as first image for backwards compat
    if images:
        story['image_file'] = images[0]
    
    with open(story_path, 'w') as f:
        json.dump(story, f, indent=2)
    
    print(f"  Updated {os.path.basename(story_path)} with {len(images)} images")


if __name__ == "__main__":
    import glob
    
    # Process specific story or all
    if len(sys.argv) > 1:
        story_file = sys.argv[1]
        with open(story_file) as f:
            story = json.load(f)
        images = generate_story_images(story)
        update_story_json(story_file, images)
    else:
        # Generate for all stories missing multi-images
        for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stories", "*.json"))):
            with open(f) as fh:
                story = json.load(fh)
            if 'images' not in story or not story['images']:
                print(f"\nStory {story['id']}: {story['title'][:50]}")
                images = generate_story_images(story)
                update_story_json(f, images)
