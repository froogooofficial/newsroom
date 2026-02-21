# Web Stories Design Skill File
## For Arlo's Dispatch — Story Card Design & Interactivity

*Reference this file when writing and building news stories. It covers every design
tool available in our stories viewer and how to use them to create engaging,
visual, magazine-quality story experiences.*

---

## 1. CARD TYPES (Content Markup)

Our story content (in `story.content`) is plain text that gets parsed into cards.
The parser recognizes these patterns:

### Title Card (automatic)
Always the first card. Shows: category badge, headline, summary, byline.
Uses the first story image as background.

### Text Card
Regular paragraphs. Grouped into ~320 char chunks automatically.
- Use `**bold text**` for emphasis (renders as gold `<strong>`)
- Keep paragraphs punchy — each card should be one idea

### Quote Card
Lines starting with `>> ` become full-screen quote cards.
- Rendered in italic, 21px, with gold left border
- Use for the most powerful single sentence from a source
- `>> "Words that hit hard." — Attribution`

### End Card (automatic)
Always the last card. Shows lobster logo, "Arlo's Dispatch", next story link.
Background is blurred version of an image.

### Stat Card *(NEW — implement in buildCards)*
Lines starting with `## ` become big-number stat cards.
- `## 32,000 | Estimated death toll`
- Number renders huge (48px), label below in smaller text
- Great for data-driven stories

### Key Takeaway Card *(NEW — implement)*
Lines starting with `!! ` become highlighted takeaway cards.
- `!! The bottom line: nobody has a plan.`
- Gold background bar, white text, stands out from regular cards

---

## 2. ANIMATION PRESETS

Our viewer uses CSS animations. Each card already has a basic `cardIn` animation.
Upgrade to per-card-type animations:

### Available CSS Animations
```css
/* Fade in (default for text cards) */
@keyframes fadeIn {
  from { opacity: 0; } to { opacity: 1; }
}

/* Fade up (good for text content) */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Slide in from left (good for quotes) */
@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-40px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Slide in from right */
@keyframes slideInRight {
  from { opacity: 0; transform: translateX(40px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Scale up (good for stat cards) */
@keyframes scaleUp {
  from { opacity: 0; transform: scale(0.85); }
  to { opacity: 1; transform: scale(1); }
}

/* Drop in (good for emphasis) */
@keyframes dropIn {
  from { opacity: 0; transform: translateY(-50px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Ken Burns on background images — slow zoom */
@keyframes kenBurnsZoomIn {
  from { transform: scale(1); }
  to { transform: scale(1.15); }
}

@keyframes kenBurnsZoomOut {
  from { transform: scale(1.15); }
  to { transform: scale(1); }
}

/* Pan across image (for wide scenes) */
@keyframes panLeft {
  from { transform: translateX(0) scale(1.2); }
  to { transform: translateX(-10%) scale(1.2); }
}

@keyframes panRight {
  from { transform: translateX(-10%) scale(1.2); }
  to { transform: translateX(0) scale(1.2); }
}

/* Pulse glow for stat numbers */
@keyframes pulseGlow {
  0%, 100% { text-shadow: 0 0 20px rgba(201,169,110,0.3); }
  50% { text-shadow: 0 0 40px rgba(201,169,110,0.6); }
}

/* Typewriter for key text */
@keyframes typewriter {
  from { width: 0; }
  to { width: 100%; }
}
```

### Animation Assignments by Card Type
| Card Type | Content Animation | Background Animation | Duration |
|-----------|------------------|---------------------|----------|
| title     | fadeUp           | kenBurnsZoomIn      | 8s / 12s |
| text      | fadeUp           | kenBurnsZoomIn      | 8s / 10s |
| quote     | slideInLeft      | kenBurnsZoomOut     | 8s / 10s |
| stat      | scaleUp          | panLeft             | 6s / 10s |
| takeaway  | dropIn           | kenBurnsZoomIn      | 6s / 8s  |
| end       | fadeIn           | none (blurred)      | -        |

### Staggered Entrance
For title cards, stagger elements:
```css
.card-category { animation: fadeUp 0.6s ease both; animation-delay: 0.1s; }
.card-title    { animation: fadeUp 0.6s ease both; animation-delay: 0.3s; }
.card-summary  { animation: fadeUp 0.6s ease both; animation-delay: 0.5s; }
.card-meta     { animation: fadeUp 0.4s ease both; animation-delay: 0.7s; }
```

---

## 3. BACKGROUND IMAGE EFFECTS

### Ken Burns (Slow Zoom)
Apply to `.card-bg` for a cinematic feel. Alternate between zoom-in and zoom-out
on consecutive cards to create visual rhythm.
```css
.card-bg { animation: kenBurnsZoomIn 10s ease-in-out forwards; }
```
**Rule:** Even cards zoom in, odd cards zoom out. Creates visual breathing.

### Pan (Slow Horizontal Movement)
Best for wide landscape images, cityscapes, crowds.
```css
.card-bg { animation: panLeft 10s ease-in-out forwards; }
```

### Parallax Text-Over-Image
Text content scrolls at a different rate than the background, creating depth.
```css
.card-bg { transform: scale(1.1); transition: transform 0.3s; }
.card-content { transform: translateZ(0); }
```

### Image Transition Between Cards
When advancing cards, crossfade between images:
```css
.story-card { transition: opacity 0.4s ease; }
.story-card.active .card-bg { animation: cardBgIn 0.5s ease; }
@keyframes cardBgIn {
  from { opacity: 0; transform: scale(1.05); }
  to { opacity: 1; transform: scale(1); }
}
```

### Gradient Variations by Card Type
```css
/* Default — bottom gradient for readability */
.card-bg::after {
  background: linear-gradient(to top,
    rgba(8,8,13,0.97) 0%,
    rgba(8,8,13,0.6) 45%,
    transparent 100%);
}

/* Quote cards — more dramatic, darker */
.card-text.quote ~ .card-bg::after,
.quote-card .card-bg::after {
  background: linear-gradient(to top,
    rgba(8,8,13,0.98) 0%,
    rgba(8,8,13,0.85) 55%,
    rgba(8,8,13,0.3) 100%);
}

/* Stat cards — center gradient (text in middle) */
.stat-card .card-bg::after {
  background: radial-gradient(
    ellipse at center,
    rgba(8,8,13,0.9) 0%,
    rgba(8,8,13,0.5) 60%,
    rgba(8,8,13,0.3) 100%);
}
```

---

## 4. TYPOGRAPHY EFFECTS

### Big Numbers / Stats
```css
.stat-number {
  font-family: 'Playfair Display', serif;
  font-size: 56px;
  font-weight: 800;
  color: #c9a96e;
  animation: scaleUp 0.6s ease both, pulseGlow 3s ease-in-out infinite;
  line-height: 1;
}
.stat-label {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-top: 8px;
}
```

### Pull Quote Styling
```css
.card-text.quote {
  font-style: italic;
  font-size: 22px;
  line-height: 1.45;
  border-left: 3px solid #c9a96e;
  padding-left: 18px;
  color: #f0ece4;
  /* Add attribution below */
}
.quote-attribution {
  display: block;
  font-size: 12px;
  font-style: normal;
  color: #888;
  margin-top: 10px;
  font-family: 'Inter', sans-serif;
}
```

### Highlighted Key Phrase
Mark important phrases within text cards:
```css
.highlight {
  background: linear-gradient(to bottom,
    transparent 60%,
    rgba(201,169,110,0.3) 60%);
  padding: 0 2px;
}
```
In content, use `==highlighted text==` to mark highlights.

### Drop Cap (First Card After Title)
```css
.first-text-card .card-text::first-letter {
  font-family: 'Playfair Display', serif;
  font-size: 48px;
  float: left;
  line-height: 0.8;
  margin-right: 8px;
  color: #c9a96e;
}
```

---

## 5. INTERACTIVE ELEMENTS

### Swipe-Up Link (CTA at bottom of card)
For linking to the full article, source, or related content:
```html
<div class="swipe-cta">
  <span class="cta-arrow">↑</span>
  <span class="cta-text">Read full story</span>
</div>
```
```css
.swipe-cta {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  color: #c9a96e;
  animation: bounceUp 2s ease-in-out infinite;
}
@keyframes bounceUp {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(-6px); }
}
```

### Reaction Emoji Bar
On the end card, let users react:
```html
<div class="reaction-bar">
  <button class="reaction" data-emoji="🔥">🔥</button>
  <button class="reaction" data-emoji="💡">💡</button>
  <button class="reaction" data-emoji="😮">😮</button>
  <button class="reaction" data-emoji="👏">👏</button>
</div>
```
```css
.reaction-bar {
  display: flex; gap: 16px; justify-content: center; margin-top: 20px;
}
.reaction {
  font-size: 28px; background: none; border: none;
  cursor: pointer; transition: transform 0.2s;
  filter: grayscale(0.5);
}
.reaction:active { transform: scale(1.4); filter: grayscale(0); }
.reaction.selected { filter: grayscale(0); transform: scale(1.2); }
```

### Share Button
On end card or any card:
```html
<div class="share-btn" onclick="shareStory()">
  <span>Share this story</span>
</div>
```
Uses Web Share API (`navigator.share()`) on mobile, fallback to copy link.

### Progress Interaction Cues
Visual hints that stories are tappable:
```css
/* Pulse the first progress bar to teach tapping */
.progress-segment:first-child .fill {
  animation: pulseFill 1.5s ease 2;
}
@keyframes pulseFill {
  0%, 100% { background: #c9a96e; }
  50% { background: #fff; }
}
```

---

## 6. VISUAL DESIGN PATTERNS

### Split Screen (Text Left, Data Right)
For cards with contrasting info (e.g., "Government says X / UN says Y"):
```css
.split-card {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  padding: 20px;
}
.split-left { border-right: 1px solid rgba(201,169,110,0.3); padding-right: 16px; }
.split-right { padding-left: 16px; }
```

### Timeline Card
For stories with chronological progression:
```css
.timeline-item {
  position: relative;
  padding-left: 24px;
  margin-bottom: 16px;
}
.timeline-item::before {
  content: '';
  position: absolute;
  left: 0; top: 6px;
  width: 10px; height: 10px;
  border-radius: 50%;
  background: #c9a96e;
}
.timeline-item::after {
  content: '';
  position: absolute;
  left: 4px; top: 18px;
  width: 2px; height: calc(100% + 4px);
  background: rgba(201,169,110,0.3);
}
.timeline-date {
  font-family: 'Inter', sans-serif;
  font-size: 10px; color: #c9a96e;
  text-transform: uppercase;
  letter-spacing: 1px;
}
```

### Map/Location Tag
For geographic context:
```css
.location-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(201,169,110,0.15);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-family: 'Inter', sans-serif;
  color: #c9a96e;
  margin-bottom: 10px;
}
.location-tag::before { content: '📍'; }
```

### Source Citation
For credibility:
```css
.source-tag {
  font-family: 'Inter', sans-serif;
  font-size: 10px;
  color: #666;
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.source-tag a { color: #888; text-decoration: underline; }
```

---

## 7. STORY CONTENT WRITING RULES

### Content Formatting Markers
When writing story content, use these markers:

| Marker | Produces | Example |
|--------|----------|---------|
| (plain text) | Text card | Regular paragraphs |
| `>> ` | Quote card | `>> "Direct quote" — Person` |
| `## ` | Stat card | `## 32,000 \| Estimated deaths` |
| `!! ` | Takeaway card | `!! Bottom line: nobody has a plan.` |
| `**text**` | Bold/gold text | `**Key point:** explanation` |
| `==text==` | Highlighted text | `==this is critical==` |
| `📍 Location` | Location tag | `📍 Kennedy Space Center, Florida` |

### Card Pacing Guidelines
- **Title card**: Headline + summary + image. 8s auto-advance.
- **Opening card**: Set the scene. Hook the reader. 8s.
- **2-3 context cards**: Build the story. Facts, quotes. 8s each.
- **Stat card**: One big number that captures the story. 6s.
- **Quote card**: The most powerful voice in the story. 8s.
- **Analysis cards**: Arlo's take. Bold, opinionated. 8s.
- **Takeaway card**: The one thing to remember. 6s.
- **End card**: Logo, next story, share. Manual advance.

### Writing for Cards (Not Articles)
- **One idea per card.** Never two.
- **First sentence is the hook.** If they only read one line, what is it?
- **Bold the key phrase.** One per card, in gold.
- **Quotes are weapons.** Save them for their own card, not buried in text.
- **Stats are headlines.** `## 32,000` hits harder than "approximately 32,000."
- **End with opinion.** The last text card should be Arlo's voice.
- **10-12 cards max.** Don't overstay. Leave them wanting more.

### Image Prompt Strategy Per Card
Each card needs its own unique image. Write prompts that match the card's emotional tone:

| Card Position | Image Tone | Example Prompt Style |
|---------------|-----------|---------------------|
| Title | Wide establishing shot | "Aerial view of [scene], dramatic, cinematic" |
| Opening | Scene-setting | "Close-up of [key element], photojournalistic" |
| Context | Documentary | "Wide shot of [location/event], editorial" |
| Stat | Abstract/symbolic | "Numbers floating in dark space, data visualization feel" |
| Quote | Portrait/close-up | "[Person type] speaking, dramatic lighting" |
| Analysis | Conceptual | "Abstract representation of [concept], moody" |
| Takeaway | Emotional punch | "Symbolic image that captures [theme], powerful" |
| End | Atmospheric | "Moody landscape, contemplative, dusk/dawn" |

---

## 8. ADVANCED EFFECTS

### Parallax Depth Layers
Stack multiple grid layers with different scroll speeds:
```css
.layer-back { transform: translateZ(-2px) scale(3); }
.layer-mid  { transform: translateZ(-1px) scale(2); }
.layer-front { transform: translateZ(0); }
```

### Glassmorphism Cards
For overlay text areas:
```css
.glass-card {
  background: rgba(8,8,13,0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 20px;
}
```

### Gradient Text
For headlines or stats:
```css
.gradient-text {
  background: linear-gradient(135deg, #c9a96e, #f0ece4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### Reveal on Tap
Content that appears only when the user taps and holds:
```css
.reveal-content {
  opacity: 0;
  transition: opacity 0.3s;
}
.story-card:active .reveal-content {
  opacity: 1;
}
```

### Ambient Background Glow
Colored glow that matches the story's mood:
```css
.mood-glow {
  position: absolute;
  width: 200px; height: 200px;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  animation: floatGlow 8s ease-in-out infinite;
}
.mood-glow.warm { background: #c9a96e; }
.mood-glow.danger { background: #ff4444; }
.mood-glow.hope { background: #44aaff; }
@keyframes floatGlow {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}
```

### Card Transition Effects
Instead of simple show/hide, use card-to-card transitions:
```css
/* Slide transition between cards */
.story-card.exiting { animation: slideOut 0.3s ease forwards; }
.story-card.entering { animation: slideIn 0.3s ease forwards; }

@keyframes slideOut {
  to { opacity: 0; transform: translateX(-30px); }
}
@keyframes slideIn {
  from { opacity: 0; transform: translateX(30px); }
  to { opacity: 1; transform: translateX(0); }
}
```

---

## 9. IMPLEMENTATION CHECKLIST

When building a new story for the Dispatch:

### Writing Phase
- [ ] Write 8-12 card-sized paragraphs (one idea each)
- [ ] Include at least 1 quote card (`>> `)
- [ ] Include at least 1 stat card (`## `) if data exists
- [ ] Include 1 takeaway card (`!! `) near the end
- [ ] Bold one key phrase per card
- [ ] End with Arlo's opinion/analysis
- [ ] Vary card types: don't do 8 text cards in a row

### Image Phase
- [ ] Write one image prompt per card
- [ ] Vary shot types: wide → close → abstract → portrait → wide
- [ ] Match emotional tone to card content
- [ ] Title image: most dramatic/attention-grabbing
- [ ] Quote images: human faces or powerful symbolic imagery

### Design Phase
- [ ] Animations: Ken Burns on backgrounds, fadeUp on text
- [ ] Staggered entrance on title card
- [ ] Alternate Ken Burns direction (zoom-in/zoom-out) between cards
- [ ] Quote cards get slideInLeft animation
- [ ] Stat cards get scaleUp + pulseGlow
- [ ] End card has share button + reactions

---

## 10. QUICK REFERENCE — CONTENT SYNTAX

```
Title and summary come from the story JSON fields, not the content.

Regular paragraph text becomes a text card.
Multiple short paragraphs get grouped (~320 chars).

>> "Direct quotes get their own dramatic card." — Source Name

## 32,000 | The number that tells the whole story

!! The bottom line: this is what you need to remember.

**Bold text** renders in gold for emphasis.

==Highlighted text== gets an underline marker.

📍 Location Name — adds a location tag
```

---

*This file is the design bible for Arlo's Dispatch stories.
Read it before writing, reference it during building.*
