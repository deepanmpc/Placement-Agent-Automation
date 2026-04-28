# PORTFOLIO SYSTEM — INTERACTION FLOW v3 (REFINED)

## CORE RULES

- UI theme, colors, typography remain EXACTLY the same
- Only one primary layer visible at a time
- All transitions must feel fast, intentional, and consistent
- User should never feel blocked or waiting unnecessarily

---

# STAGE 1 — LANDING (ENTRY STATE)

### Visible:
- Headline: “A designer who engineers experiences.”
- System label (SYS://PORTFOLIO)
- CTA: “INITIALIZE SYSTEM” with blinking cursor

### Hidden:
- HUD
- Navigation
- All scenes
- Terminal & Chatbot

### Interaction:
- Press Enter OR click → move to Stage 2 instantly

### Behavior:
- CTA has subtle flicker (not aggressive)
- Cursor blinks continuously
- No delay on interaction

---

# STAGE 2 — BOOT SEQUENCE (SKIPPABLE)

### Sequence:
Display lines one-by-one:

1. Loading modules...
2. Initializing interface...
3. Mounting scene graph...
4. System ready.

+ progress bar fills gradually

### Timing:
- Total: ~2.0–2.5 seconds (NOT 3.2s)
- Each line ~400–500ms

### Important:
- ANY key press / click → instantly skip to end state

### Exit:
- Quick fade-out (0.3–0.4s)
- Transition directly into Stage 3

---

# STAGE 3 — HUD + NAV INITIALIZATION

### Appears in sequence:
1. HUD label (top corner)
2. Coordinates
3. Right-side navigation dots

### Animation:
- Fade + slight upward motion
- Staggered (100–150ms gap)

### Behavior:
- No interaction delay
- User can click nav immediately

### Next:
- Intro scene slides in AFTER HUD is visible

---

# STAGE 4 — INTRO SCENE (PRIMARY IDENTITY)

### Visible:
- Name (typewriter)
- Role (typewriter)
- Short description
- Minimal nav pills (Skills / Projects / Contact)

### Hidden:
- Skills content
- Projects content
- Contact content

### Behavior:
- Typewriter speed: fast, not dramatic
- Subtle cursor blink at end

### Interaction:
- Click nav OR scroll → go to next scene

---

# STAGE 5 — SCENE TRANSITION SYSTEM

### Rule:
ONLY ONE SCENE ACTIVE AT A TIME

### Transition Style (GLOBAL):
- Fade (opacity 0 → 1)
- Scale (0.98 → 1)
- Duration: 0.4–0.6s
- Ease: smooth (ease-in-out)

### Exit:
- Clean fade-out
- No overlapping content

### Applies to:
- Skills
- Projects
- Contact

---

# STAGE 6 — PROJECTS (PROGRESSIVE REVEAL)

### Initial View:
- Show ONLY 3 project cards
- Cards appear with stagger (120ms)

### Interaction:
- Hover → highlight + slight lift
- Click → open modal (Stage 7)

### Load More:
Replace generic button with:
- “+ Expand Projects” OR
- subtle animated reveal trigger

Behavior:
- Reveals remaining projects smoothly
- No page jump

---

# STAGE 7 — PROJECT MODAL (FOCUS MODE)

### On Open:
- Background dims (overlay ~60–70%)
- Modal scales + fades in (0.3s)

### Behavior:
- Locks interaction to modal
- ESC closes instantly
- Click outside closes

### Content:
- Project title
- Tech stack
- Description
- Actions (View / Back)

### Important:
- No clutter
- Keep reading focus strong

---

# STAGE 8 — TERMINAL (SYSTEM CONTROL)

### Activation:
- Button OR keyboard shortcut

### Behavior:
- Slides in from bottom/side (0.3s)
- Background slightly dims
- Takes focus

### Commands:
- help
- about
- skills
- projects
- nav skills
- nav contact
- clear

### Advanced:
- goto <scene>
- open <project>

### Errors:
- Show clear feedback for invalid commands

### Exit:
- ESC closes terminal instantly

---

# STAGE 9 — CHATBOT (GUIDED INTERACTION)

### Activation:
- Floating button

### On Open:
- Expands smoothly
- Background dims slightly
- Terminal auto-closes if open

### Behavior:
- Starts with typing indicator
- First message feels human, not robotic

### Default Prompts:
- Specialties?
- Best work?
- Available for hire?

### Response Rules:
- Max 2–3 lines
- Clear, confident tone
- No generic AI phrasing

### Smart Actions:
- Can trigger navigation
  (e.g., “Show projects” → go to Projects)

### Exit:
- ESC closes chatbot

---

# GLOBAL FOCUS SYSTEM

### Rule:
Only ONE focus layer active:
- Normal UI
- Project Modal
- Terminal
- Chatbot

### When active:
- Background dims or soft blur
- Other interactions disabled

---

# MICRO INTERACTIONS

- Cursor reacts to hover
- Click feedback (visual or subtle sound)
- Terminal typing delay (minimal)
- Chatbot typing dots

---

# PERFORMANCE RULES

- No blocking animations
- All transitions interruptible
- Lazy load heavy sections
- Keep everything responsive

---

# FINAL EXPERIENCE GOAL

User should feel:
- entering a system
- discovering layers
- interacting with intelligence

NOT:
- browsing a static portfolio
- waiting for animations
- overwhelmed by UI
