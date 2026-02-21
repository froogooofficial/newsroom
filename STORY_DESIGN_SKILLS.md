# Web Stories Design Skill File v2
## Based on AMP Web Stories Spec + Real-World Examples (USA Today, etc.)

*This is the authoritative reference for building Arlo's Dispatch stories.
Based on the official AMP amp-story spec, amp-story-grid-layer docs,
and analysis of production stories from USA Today.*

---

## 1. AMP STORY ARCHITECTURE

Every AMP Web Story follows this hierarchy:

```
amp-story (the whole story)
  └── amp-story-page (one full-screen slide)
        └── amp-story-grid-layer (a layout layer — multiple stacked)
              └── content (text, images, video)
```

### Key Principles from the Spec
- **Pages stack vertically** — user taps/swipes to advance
- **Layers stack bottom-up** (first in DOM = bottom, last = top)
- **Each page is its own full-screen canvas** — 9:16 portrait
- **One idea per page** — like a slide deck, not an article
- **Content should be visual-first** — text overlaid on media
- **Auto-advance** is optional per page (`auto-advance-after="5s"`)

### Grid Layer Templates (4 built-in layouts)

| Template | Behavior | Use For |
|----------|----------|---------|
| `fill` | First child fills entire screen | Background images/video |
| `vertical` | Stack children top-to-bottom | Text content, lists |
| `horizontal` | Stack children left-to-right | Side-by-side elements |
| `thirds` | Three equal rows: upper/middle/lower | Precise text placement |

**Named grid areas** (for `thirds` template):
- `upper-third`
- `middle-third`  
- `lower-third`

### Layer Stacking Pattern
Every page should have AT LEAST two layers:

```html
<!-- Layer 1: Background (fill template) -->
<amp-story-grid-layer template="fill">
  <amp-img src="bg.jpg" layout="fill" alt="..."></amp-img>
</amp-story-grid-layer>

<!-- Layer 2: Content (vertical/thirds template) -->
<amp-story-grid-layer template="vertical">
  <h1>Headline text</h1>
</amp-story-grid-layer>
```

This is the fundamental pattern. Background is ALWAYS a separate fill layer.
Text goes in a content layer ON TOP of it.

### Vertical Alignment via CSS Classes
USA Today pattern (used in their Beyonce story):
```css
amp-story-grid-layer.middle { align-content: center; }
amp-story-grid-layer.bottom { align-content: end; }
```
Then: `<amp-story-grid-layer template="vertical" class="middle">`

---

## 2. ANIMATION SYSTEM

### All 20 Built-in Animation Presets

| Preset | Default Duration | Best For |
|--------|-----------------|----------|
| `fade-in` | 600ms | Text, subtle reveals |
| `fly-in-left` | 600ms | Text entering from left |
| `fly-in-right` | 600ms | Text entering from right |
| `fly-in-top` | 600ms | Headers dropping down |
| `fly-in-bottom` | 600ms | Content rising up |
| `drop` | 1600ms | Dramatic stat reveals |
| `pulse` | 600ms | Emphasis on existing element |
| `twirl-in` | 1000ms | Playful/fun content |
| `rotate-in-left` | 1000ms | Dynamic entrance |
| `rotate-in-right` | 1000ms | Dynamic entrance |
| `scale-fade-down` | 600ms | Subtle zoom + fade |
| `scale-fade-up` | 600ms | Subtle zoom + fade |
| `whoosh-in-left` | 600ms | Fast, energetic entrance |
| `whoosh-in-right` | 600ms | Fast, energetic entrance |
| `pan-left` | 1000ms | Ken Burns on images |
| `pan-right` | 1000ms | Ken Burns on images |
| `pan-up` | 1000ms | Ken Burns on images |
| `pan-down` | 1000ms | Ken Burns on images |
| `zoom-in` | 1000ms | Ken Burns on images |
| `zoom-out` | 1000ms | Ken Burns on images |

### Animation Attributes

```html
<element
  animate-in="fade-in"              <!-- required: which preset -->
  animate-in-duration="0.5s"        <!-- optional: override duration -->
  animate-in-delay="0.3s"           <!-- optional: wait before starting -->
  animate-in-after="element-id"     <!-- optional: chain after another -->
  animate-in-timing-function="ease-out"  <!-- optional: easing curve -->
>
```

### Zoom/Pan Specific Attributes
```html
<!-- Zoom from 2x to 5x over 4 seconds -->
<amp-img animate-in="zoom-in" scale-start="2" scale-end="5"
         animate-in-duration="4s" ...>

<!-- Pan 200px left over 10 seconds -->  
<amp-img animate-in="pan-left" translate-x="200px"
         animate-in-duration="10s" ...>

<!-- Pan 50px down, scale factor 1.3 -->
<amp-img animate-in="pan-down" translate-y="50px"
         pan-scaling-factor="1.3" animate-in-duration="15s" ...>
```

### Sequencing (Critical Pattern)
Chain animations so they play in order:

```html
<p id="line1" animate-in="fade-in" animate-in-delay="0.5s">
  First line appears
</p>
<p id="line2" animate-in="fade-in" animate-in-after="line1" 
   animate-in-delay="0.2s">
  Then this line
</p>
<p id="line3" animate-in="fade-in" animate-in-after="line2"
   animate-in-delay="0.2s">
  Then this one
</p>
```

**USA Today uses this pattern heavily** — staggered word reveals:
```html
<p>
  <span animate-in="fade-in" animate-in-delay="0.5s">Madonna,</span><br>
  <span animate-in="fade-in" animate-in-delay="0.8s">Rihanna,</span><br>
  <span animate-in="fade-in" animate-in-delay="1.1s">Cher,</span><br>
  <span animate-in="fade-in" animate-in-delay="1.4s">Adele...</span>
</p>
```

### Combining Multiple Animations
Nest elements to combine effects:
```html
<div animate-in="fly-in-left">
  <div animate-in="fade-in">
    <!-- This element flies in AND fades in simultaneously -->
  </div>
</div>
```

---

## 3. PAGE TYPES & PATTERNS (from USA Today analysis)

The Beyonce story (24 pages) uses these recurring patterns:

### Cover Page
- Full-bleed background VIDEO (not image)
- Staggered text: small intro text → BIG headline
- Text centered vertically

### Statement Page (most common)
- Full-bleed image/video background
- One short statement (< 2 lines)
- Text centered or bottom-aligned
- fade-in with 0.5s delay
- **ONE IDEA. That's it.**

### Big Number Page
- Full-bleed video background
- Small label text fades in first
- GIANT number fades in second (100px+ font)
- Used for: Grammy nominations (63), wins (22)

### Reveal/List Page  
- Background image
- Multiple items fade in sequentially (staggered delays)
- Each item 0.3s apart
- Great for: lists, timelines, multiple stats

### Quote Page
- Background image/video
- Quote text in body font (not italic — italic is an option)
- Attribution below: "— Name"
- Text centered

### CTA Page
- Same layout as statement page
- `<amp-story-cta-layer>` at bottom
- Button with link to full article
- "Tap: [action]" format

### Video-Only Page
- Just a full-screen video, no text overlay
- Used as transition/breathing room between text-heavy pages

---

## 4. DESKTOP BEHAVIOR

### Default Desktop (3-panel)
AMP stories on desktop show THREE panels side by side:
- Previous page (dimmed) | Current page | Next page (dimmed)
- Phone-shaped frames
- Background behind the panels

### Full-Bleed Desktop (opt-in)
With `supports-landscape` attribute:
- Story fills the full viewport
- No phone frames
- Immersive experience

### Our Implementation
We use a phone-frame approach on desktop:
- Dark blurred backdrop
- Centered 9:16 phone frame (380-400px wide)
- Rounded corners, subtle shadow
- Click outside to close
- Feed is centered at 600-720px width

### Responsive Text Sizing
USA Today uses media queries:
```css
@media only screen and (min-width: 650px) {
  p.text-pages { font-size: 25px; }  /* smaller on desktop */
}
```
Important: text that looks right on phone (35-45px) looks huge on desktop.

---

## 5. WHAT WE BUILD vs REAL AMP

We don't use the AMP framework directly — we build a custom story viewer
that mimics AMP story behavior. Here's our mapping:

| AMP Concept | Our Implementation |
|-------------|-------------------|
| `amp-story` | `.story-viewer` |
| `amp-story-page` | `.story-card` |
| `amp-story-grid-layer template="fill"` | `.card-bg` (background image) |
| `amp-story-grid-layer template="vertical"` | `.card-content` |
| `animate-in="fade-in"` | CSS `@keyframes fadeUp` |
| `animate-in-delay` | CSS `animation-delay` |
| `animate-in-after` | CSS staggered delays |
| `auto-advance-after` | JS `setTimeout(nextCard, duration)` |
| `amp-story-cta-layer` | Not yet implemented |
| `amp-story-bookend` | End card with reactions/share |
| Progress bar | Custom progress segments |

---

## 6. CARD TYPES IN OUR SYSTEM

### Content Markers (in story.content field)

| Marker | Card Type | Renders As |
|--------|-----------|-----------|
| (plain text) | `text` | Paragraph with fadeUp animation |
| `>> "quote" — Attribution` | `quote` | Italic quote, gold border, slideInLeft |
| `## 32,000 \| Label text` | `stat` | Giant gradient number + small label, scaleUp |
| `!! Important takeaway` | `takeaway` | Glassmorphism box, dropIn animation |
| `**bold text**` | (inline) | Gold `<strong>` text |
| `==highlighted==` | (inline) | Underline highlight mark |
| `📍 Location Name` | (inline) | Location pill/tag |

### Card-Specific Styling

**Title Card** — staggered entrance:
- Category badge: fadeUp, 0.1s delay
- Headline: fadeUp, 0.25s delay  
- Summary: fadeUp, 0.4s delay
- Byline: fadeUp, 0.55s delay

**Text Card** — fadeUp on content block. First text card gets drop-cap.

**Quote Card** — slideInLeft. Darker gradient overlay. Attribution separated.

**Stat Card** — scaleUp with pulseGlow. Center-vignette gradient. Gradient text.

**Takeaway Card** — dropIn. Warm-tint gradient. Glassmorphism box with border.

**End Card** — Blurred background. Logo, reactions (🔥💡😮👏), share button, next story link.

---

## 7. BACKGROUND ANIMATIONS (Ken Burns)

Every card has a background image with a Ken Burns effect.
Patterns alternate to create visual rhythm:

```
Card 0 (title): zoom-in
Card 1: zoom-out
Card 2: pan-left
Card 3: pan-right
Card 4: zoom-in
Card 5: zoom-out
...
```

Duration: 10s per animation (longer than the card's advance time,
so the animation is still moving when the user taps forward — feels alive).

### Gradient Overlays by Card Type

**Default (text):** Bottom gradient, 80% height
```css
linear-gradient(to top, rgba(8,8,13,0.97) 0%, rgba(8,8,13,0.6) 45%, transparent 100%)
```

**Quote:** Full-height, heavier darkness for readability
```css
linear-gradient(to top, rgba(8,8,13,0.98) 0%, rgba(8,8,13,0.8) 50%, rgba(8,8,13,0.4) 100%)
```

**Stat:** Center vignette (text is centered, not bottom)
```css
radial-gradient(ellipse at center, rgba(8,8,13,0.85) 0%, rgba(8,8,13,0.5) 55%, rgba(8,8,13,0.3) 100%)
```

**Takeaway:** Warm tint
```css
linear-gradient(to top, rgba(8,8,13,0.97) 0%, rgba(30,20,8,0.7) 50%, rgba(8,8,13,0.3) 100%)
```

---

## 8. WRITING FOR STORY CARDS

### Rules from AMP Best Practices + USA Today Analysis

1. **One sentence per page when possible.** USA Today averages 1-2 sentences per page across their entire story. NOT paragraphs.

2. **Text is LARGE.** 35-50px on mobile. Short words hit harder. "GIRLS!" not "Girls are running the world."

3. **Bold the key number or word.** One bold per card. `<span class="bold">$355 million</span>`

4. **Stagger reveals for drama.** Don't show the whole sentence at once. Show pieces: word by word, line by line, with 0.3s gaps.

5. **Use video backgrounds whenever possible.** Video > still images for engagement. Even 3-second loops work.

6. **Breathing pages.** Not every page needs text. A full-screen video with no text = a beat, a pause, dramatic tension.

7. **Keep it under 30 pages.** Ideal: 12-20 pages.

8. **Big numbers get their own page.** "63" is more powerful alone than buried in a sentence.

9. **Quotes get their own page.** Never bury a quote in a paragraph.

10. **CTA links go in their own layer** at the bottom — "Tap: Read more"

### Card Pacing for News Stories

| Position | Card Type | Duration | Purpose |
|----------|-----------|----------|---------|
| 1 | Title | 8s | Hook: headline + summary + image |
| 2 | Text | 8s | Set the scene. One sentence. |
| 3 | Text | 8s | Key context. One-two sentences. |
| 4 | Quote | 8s | The voice that matters most. |
| 5 | Stat | 6s | The number that captures the story. |
| 6 | Text | 8s | What this means / why it matters. |
| 7 | Text | 8s | Counter-argument or complication. |
| 8 | Quote | 8s | Second voice or rebuttal. |
| 9 | Takeaway | 6s | Bottom line — one sentence. |
| 10 | End | ∞ | Reactions, share, next story. |

### Image Prompts Per Card Position

| Position | Shot Type | Mood |
|----------|-----------|------|
| Title | Wide establishing / aerial | Dramatic, cinematic |
| Scene-setter | Documentary wide | Editorial, atmospheric |
| Context | Medium shot | Photojournalistic |
| Quote | Close-up / portrait | Intimate, dramatic lighting |
| Stat | Abstract / symbolic | Data-viz feel, moody |
| Analysis | Conceptual | Thoughtful, complex |
| Takeaway | Symbolic / emotional | Powerful, memorable |
| End | Atmospheric | Contemplative, dusk/dawn |

---

## 9. RESPONSIVE DESIGN RULES

### Mobile (default)
- Story cards: full-screen
- Text: 16-28px for body, 28-56px for headlines
- Progress bar: full width at top
- Tap left (25%) = back, tap right (75%) = forward

### Desktop (600px+)
- Feed: centered at 600px max-width
- Story viewer: phone-frame (380px × ~675px), centered
- Blurred dark backdrop behind frame
- Rounded corners (20px) on frame
- Click outside frame = close
- All elements inside frame, absolutely positioned

### Tablet/Wide Desktop (900px+)
- Feed: 720px max-width
- Story frame: 400px × ~710px
- More breathing room

### Text Scaling
Reduce font sizes on desktop to avoid text looking enormous:
```css
@media (min-width: 650px) {
  .card-title { font-size: 24px; }
  .card-text { font-size: 14px; }
  .stat-number { font-size: 48px; }
}
```

---

## 10. FEATURES NOT YET IMPLEMENTED

These exist in the AMP spec but we haven't built them yet:

- [ ] **Video backgrounds** — `<amp-video>` with autoplay loop
- [ ] **CTA layer** — `<amp-story-cta-layer>` button at bottom of page
- [ ] **Background audio** — per-page or per-story audio tracks
- [ ] **Live story** — polling for new pages in real-time
- [ ] **Interactive elements** — polls, quizzes (`amp-story-interactive`)
- [ ] **Bookend** — end screen with related stories grid
- [ ] **Landscape mode** — `supports-landscape` responsive layout
- [ ] **Branching** — non-linear story paths
- [ ] **Auto-advance per page** — different durations per card
- [ ] **Custom animations** — beyond presets, via `amp-story-animation`
- [ ] **Landscape half-half** — split screen on tablets
- [ ] **aspect-ratio layers** — `preset="2021-foreground"`

### Priority to implement next:
1. **Auto-advance per page** (different durations) ← partially done
2. **Video backgrounds** ← highest impact visual upgrade
3. **CTA layer** ← links to sources
4. **Bookend** ← related stories grid at end

---

## 11. QUICK REFERENCE — OUR CONTENT SYNTAX

```
The title, summary, category, writer come from the story JSON.
The content field gets parsed into cards:

Regular paragraph text → text card (grouped at ~320 chars)

>> "Direct quote here" — Source Name → quote card

## 32,000 | Description of this number → stat card

!! The bottom line: this is what matters. → takeaway card

**Bold text** → renders in gold
==Highlighted text== → underline marker
📍 Location Name → location pill tag
```

### Story JSON Structure
```json
{
  "id": "unique-id",
  "title": "Headline Here",
  "summary": "One-sentence hook.",
  "content": "Card content with markers...",
  "category": "world",
  "writer": "Arlo",
  "images": ["img1.jpg", "img2.jpg", "img3.jpg"],
  "published": "2025-02-21 06:00"
}
```

---

*This file is the design bible for Arlo's Dispatch stories.
Read before writing, reference during building.
Based on: AMP amp-story spec (38K), amp-story-grid-layer spec (18K),
amp-story-page spec, and USA Today Beyonce story (24 pages) source analysis.*
