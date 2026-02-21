#!/usr/bin/env python3
"""
Generate multiple images per story for the Stories format.
Uses flux-schnell (fast & cheap) via Replicate.
Each story gets images for each card/slide.
Card-type-aware prompts: stats get abstract, quotes get portraits, etc.
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
    """Split story content into cards (matches the viewer parser)."""
    paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
    cards = []
    buf = ''

    for p in paragraphs:
        # Quote card
        if p.startswith('>>'):
            if buf:
                cards.append({'type': 'text', 'text': buf.strip()})
                buf = ''
            cards.append({'type': 'quote', 'text': p.replace('>>', '').strip()})
            continue
        # Stat card
        if p.startswith('## '):
            if buf:
                cards.append({'type': 'text', 'text': buf.strip()})
                buf = ''
            parts = p[3:].split('|')
            cards.append({'type': 'stat', 'text': parts[0].strip(),
                          'label': parts[1].strip() if len(parts) > 1 else ''})
            continue
        # Takeaway card
        if p.startswith('!! '):
            if buf:
                cards.append({'type': 'text', 'text': buf.strip()})
                buf = ''
            cards.append({'type': 'takeaway', 'text': p[3:].strip()})
            continue

        if len(buf + '\n\n' + p) > max_chars and buf:
            cards.append({'type': 'text', 'text': buf.strip()})
            buf = p
        else:
            buf += ('\n\n' if buf else '') + p

    if buf.strip():
        cards.append({'type': 'text', 'text': buf.strip()})

    return cards[:12]


# Image mood per card type (from STORY_DESIGN_SKILLS.md)
CARD_IMAGE_STYLE = {
    'text': 'photojournalistic, editorial, medium shot',
    'quote': 'dramatic portrait lighting, close-up, intimate',
    'stat': 'abstract data visualization feel, dark moody, symbolic',
    'takeaway': 'powerful symbolic imagery, emotional, cinematic',
}

def generate_image_prompts(story):
    """Create image prompts per card, matching type to visual mood."""
    title = story['title']
    category = story.get('category', 'world')
    cards = split_story_to_cards(story['content'])

    prompts = []

    # Title card - wide establishing shot, most dramatic
    prompts.append(f"{title}, wide establishing shot, dramatic cinematic editorial photography")

    # Content cards - type-aware prompts
    for card in cards:
        style = CARD_IMAGE_STYLE.get(card['type'], 'editorial photography, cinematic')
        text = card.get('text', '') or card.get('label', '')

        if card['type'] == 'stat':
            label = card.get('label', text)
            prompts.append(f"{label}, {style}, dark background")
        elif card['type'] == 'quote':
            prompts.append(f"Person speaking about {title[:40]}, {style}")
        elif card['type'] == 'takeaway':
            prompts.append(f"{text[:60]}, {style}")
        else:
            # Extract most visual sentence
            sentences = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 20]
            if sentences:
                visual_words = ['strike', 'fire', 'crowd', 'building', 'soldier', 'court',
                    'city', 'night', 'ship', 'missile', 'protest', 'sky', 'ocean',
                    'mountain', 'flag', 'rocket', 'lab', 'office', 'street', 'war',
                    'smoke', 'explosion', 'march', 'rally', 'hospital', 'border']
                best = max(sentences, key=lambda s: sum(1 for w in visual_words if w in s.lower()))
                prompts.append(f"{best}, {style}")
            else:
                prompts.append(f"{title}, atmospheric {category} imagery, {style}")

    return prompts


def generate_story_images(story, force=False):
    """Generate all images for a story. Returns list of image filenames.

    Skips generation if images already exist (unless force=True).
    """
    story_id = story['id']

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
