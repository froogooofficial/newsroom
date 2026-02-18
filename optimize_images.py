#!/usr/bin/env python3
"""
Optimize images for Arlo's Dispatch.
Converts PNG to compressed JPEG using ffmpeg.
"""
import subprocess, os, sys

def optimize_image(input_path, output_path=None, quality=5):
    """Convert image to compressed JPEG.
    quality: 2 (best) to 31 (worst). 5 is good balance.
    Returns output path."""
    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = base + ".jpg"
    
    result = subprocess.run(
        ['ffmpeg', '-y', '-i', input_path, '-q:v', str(quality), output_path],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        orig = os.path.getsize(input_path)
        new = os.path.getsize(output_path)
        pct = 100 * new // orig if orig > 0 else 0
        print(f"  Optimized: {orig//1024}KB → {new//1024}KB ({pct}%)")
        # Remove original if different file
        if os.path.abspath(input_path) != os.path.abspath(output_path):
            os.remove(input_path)
        return output_path
    else:
        print(f"  Error: {result.stderr[:200]}")
        return input_path

def generate_story_image(prompt, name, images_dir="docs/images"):
    """Generate and optimize an image for a story.
    Returns the filename (e.g., 'my-image.jpg')"""
    os.makedirs(images_dir, exist_ok=True)
    
    # Import here to avoid circular deps
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.express import generate_image
    
    # Generate as PNG first
    png_path = os.path.join(images_dir, f"{name}.png")
    generate_image(prompt, png_path, aspect="16:9")
    
    # Convert to JPEG
    jpg_path = os.path.join(images_dir, f"{name}.jpg")
    optimize_image(png_path, jpg_path)
    
    return f"{name}.jpg"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            optimize_image(path)
    else:
        print("Usage: python3 optimize_images.py <image1.png> [image2.png ...]")
        print("Or import: from optimize_images import generate_story_image")
