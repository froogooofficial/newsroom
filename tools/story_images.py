#!/usr/bin/env python3
"""
Generate one unique image per story card.
Usage: from tools.story_images import parse_cards, generate_story_images
"""
import json, os, subprocess, time, urllib.request

REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "images")

def parse_cards(content):
    """Split story content into cards, same logic as the JS viewer."""
    cards = [{'type': 'title', 'text': ''}]
    paras = [p.strip() for p in content.split('\n') if p.strip()]
    buf = ''
    
    for p in paras:
        if p.startswith('>>'):
            if buf:
                cards.append({'type': 'text', 'text': buf.strip()})
                buf = ''
            cards.append({'type': 'quote', 'text': p.replace('>> ', '').replace('>>', '')})
            continue
        if len(buf + '\n\n' + p) > 320 and buf:
            cards.append({'type': 'text', 'text': buf.strip()})
            buf = p
        else:
            buf += ('\n\n' + p if buf else p)
    
    if buf.strip():
        cards.append({'type': 'text', 'text': buf.strip()})
    cards.append({'type': 'end', 'text': ''})
    return cards[:12]


def gen_one_image(prompt, output_path, retries=2):
    """Generate one image via flux-schnell."""
    url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
    headers = {
        "Authorization": f"Bearer {REPLICATE_TOKEN}",
        "Content-Type": "application/json",
        "Prefer": "wait"
    }
    data = json.dumps({
        "input": {
            "prompt": f"Editorial photograph, cinematic lighting, photojournalistic: {prompt}",
            "aspect_ratio": "9:16",
            "num_outputs": 1
        }
    }).encode()
    
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            result = json.loads(urllib.request.urlopen(req, timeout=60).read())
            img_url = result.get("output", [None])[0]
            if not img_url:
                continue
            
            png = output_path.replace('.jpg', '.png')
            urllib.request.urlretrieve(img_url, png)
            subprocess.run(['ffmpeg', '-y', '-i', png, '-q:v', '5', output_path], 
                         capture_output=True)
            if os.path.exists(output_path):
                os.remove(png)
                return True
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
            else:
                print(f"  ✗ Failed: {e}")
    return False


def generate_story_images(story_id, prompts, story_file=None):
    """
    Generate images for a story. One prompt per card.
    
    Args:
        story_id: int story ID
        prompts: list of str, one image prompt per card
        story_file: path to story JSON (auto-detected if None)
    
    Returns:
        list of image filenames
    """
    import glob
    
    # Find story file
    if not story_file:
        base = os.path.dirname(os.path.dirname(__file__))
        for f in glob.glob(os.path.join(base, "stories/*.json")):
            with open(f) as fh:
                s = json.load(fh)
            if s['id'] == story_id:
                story_file = f
                break
    
    if not story_file:
        print(f"Story {story_id} not found!")
        return []
    
    with open(story_file) as fh:
        story = json.load(fh)
    
    os.makedirs(IMAGES_DIR, exist_ok=True)
    images = []
    
    for i, prompt in enumerate(prompts):
        fname = f"story-{story_id:03d}-{i}.jpg"
        fpath = os.path.join(IMAGES_DIR, fname)
        
        print(f"  [{i+1}/{len(prompts)}] {prompt[:50]}...")
        ok = gen_one_image(prompt, fpath)
        if ok:
            kb = os.path.getsize(fpath) // 1024
            print(f"    ✓ {fname} ({kb}KB)")
            images.append(fname)
        else:
            # Reuse previous image as fallback
            images.append(images[-1] if images else "")
            print(f"    ✗ Using fallback")
        time.sleep(0.2)
    
    # Update story JSON
    story['images'] = images
    story['image_file'] = images[0] if images else ''
    with open(story_file, 'w') as fh:
        json.dump(story, fh, indent=2)
    
    print(f"\n✅ Story {story_id}: {len(images)} images saved")
    return images


def show_cards(story_id):
    """Show cards for a story to help write prompts."""
    import glob
    base = os.path.dirname(os.path.dirname(__file__))
    for f in glob.glob(os.path.join(base, "stories/*.json")):
        with open(f) as fh:
            s = json.load(fh)
        if s['id'] == story_id:
            cards = parse_cards(s['content'])
            print(f"Story {story_id}: {s['title'][:60]}")
            print(f"Total cards: {len(cards)} (need {len(cards)} image prompts)\n")
            for i, c in enumerate(cards):
                if c['type'] == 'title':
                    print(f"  [{i}] TITLE — {s['title'][:70]}")
                    print(f"       Summary: {s['summary'][:70]}")
                elif c['type'] == 'end':
                    print(f"  [{i}] END — (reuses image, can use any mood shot)")
                else:
                    marker = "QUOTE" if c['type'] == 'quote' else "TEXT"
                    print(f"  [{i}] {marker} — {c['text'][:80]}")
            print()
            return cards
    print(f"Story {story_id} not found")
    return []
