"""Domain knowledge — real expertise from animation, design, and film schools.

This is the foundation for all reviewers and generators. Every rule here
comes from published research, professional practice, or expert analysis.

Sources: Disney's 12 Principles, Pixar's 22 Rules, Tufte's Information Design,
Mayer's Multimedia Learning, 3Blue1Brown analysis, Kurzgesagt process,
professional motion design studio evaluation criteria.
"""

# ─── COMPOSITION & LAYOUT ───

LAYOUT_RULES = """
## FRAME COMPOSITION

1. THREE-ZONE LAYOUT:
   - Top (y=2.0 to 3.5): Titles, headers only
   - Center (y=-1.5 to 1.5): Primary diagram/visual — this is where teaching happens
   - Bottom (y=-2.0 to -3.5): Labels, subtitles, supplementary text
   Never put primary visuals in top/bottom. Never put titles in center.

2. MAXIMUM 4 ACTIVE ELEMENTS per frame (visual working memory limit — Luck & Vogel, 1997).
   If you need more, group related items into one VGroup that reads as one unit.
   When adding a 5th element, dim or remove the least relevant one.

3. SPATIAL CONTIGUITY: Labels must be adjacent to what they describe (Mayer, d=1.10).
   Use .next_to(shape, direction, buff=0.2). Never put labels in a separate corner.

4. CENTER OF GRAVITY: Most important element at ORIGIN or UP*0.5.
   Eye goes to center first — put your key insight there.

5. CONSISTENT SPATIAL MAPPING:
   - Hierarchy: higher = more powerful/general
   - Time: left = before, right = after
   - Comparison: left vs right, evenly spaced
   Once assigned, never shuffle positions without a Transform animation.
"""

# ─── COLOR ───

COLOR_RULES = """
## COLOR SYSTEM

1. SEMANTIC COLOR LOCKING: One color per concept for the ENTIRE video. Never reuse.
   This is 3Blue1Brown's strongest visual pattern.

2. MAXIMUM 5 SEMANTIC COLORS + white + dim gray:
   - 3-5 saturated colors for concepts
   - WHITE for primary text
   - GREY (#888888) for de-emphasized elements
   - BLACK background is negative space, not a "color"

3. DIM-AND-HIGHLIGHT PATTERN (3B1B signature):
   When focusing on one element:
   a. Fade all others to 30% opacity (.animate.set_opacity(0.3))
   b. Keep focus element at full opacity
   c. Optionally add Indicate() or Circumscribe()
   d. Restore when moving on

4. HIGH-CONTRAST ON DARK BACKGROUND:
   Good: #3498db (blue), #2ecc71 (green), #e74c3c (red), #f39c12 (gold), #9b59b6 (purple)
   Bad: dark brown, dark green, navy — they vanish on black
   All text: WHITE or YELLOW. Never light gray for important text.
"""

# ─── VISUAL VOCABULARY ───

VISUAL_VOCABULARY = """
## VISUAL VOCABULARY FOR ANY TOPIC

1. CONCEPT CARDS (the atomic unit for non-math topics):
   RoundedRectangle(width=3, height=1.2, corner_radius=0.2, color=COLOR, fill_opacity=0.15)
   + Text("Label", font_size=24, color=WHITE) centered inside
   Cards can be arranged, stacked, connected, grouped, transformed.

2. ENTITY-RELATIONSHIP PATTERN (for systems: legal, political, technical):
   - Entities = labeled rounded rectangles
   - Relationships = arrows between them
   - Containment = larger rectangle containing smaller ones
   - Flow = left-to-right or top-to-bottom chain with arrows

3. PIPELINE PATTERN (for processes):
   3-5 boxes connected by arrows, left to right.
   Animate a traveling dot/highlight to show flow.

4. HIERARCHY PATTERN (for power structures, taxonomies):
   Parent at top, children below, connected by lines.
   More important = higher position.

5. COMPARISON PATTERN (for vs/contrast):
   Two columns, left and right of center.
   Color-code each side. Connect corresponding items with dashed lines.

6. EVERY SHAPE MUST HAVE A LABEL. No exceptions.
   A rectangle without text inside is meaningless to the viewer.
   A circle without a label is decoration, not information.
"""

# ─── ANIMATION ───

ANIMATION_RULES = """
## ANIMATION TIMING AND MOTION

1. PROGRESSIVE DISCLOSURE (3B1B core pattern):
   Never show everything at once.
   Show element A, explain (1-3s). Add B, explain (1-3s). Add C.
   Only after all pieces understood, show full picture.

2. ONE ANIMATION PER CONCEPT:
   Each voiceover sentence gets ONE primary animation.
   Viewer's eye can only track one moving thing at a time.
   Exception: coordinated group animations count as one.

3. RUN TIMES:
   - Standard transitions (Create, FadeIn, Write): 1.0-2.0s
   - Emphasis (Indicate, Flash): 0.3-0.5s
   - Exit (FadeOut): 0.5-1.0s
   - Never > 3.0s (sluggish). Never < 0.3s (jumpy).

4. ENTER/EXIT VOCABULARY:
   - Shapes: Create() or GrowFromCenter()
   - Text: Write() or FadeIn()
   - Groups: FadeIn() with lag_ratio=0.2 (staggered)
   - Exit: Always FadeOut(). Never Uncreate() (looks like rewinding).
   - Emphasis: Indicate() or Circumscribe()
   - Transform: Transform() or ReplacementTransform()

5. PAUSE-AFTER-REVEAL: After showing something new, wait 1-2s.
   Viewers need time to read and process. Voiceover fills this time.

6. CLEAN SCENE TRANSITIONS:
   a. FadeOut all current elements
   b. Brief pause (0.3-0.5s)
   c. FadeIn new scene title
   Never cut directly from one complex diagram to another.
"""

# ─── TYPOGRAPHY ───

TYPOGRAPHY_RULES = """
## TYPOGRAPHY

1. THREE-TIER TYPE SCALE:
   - Title: font_size=42-48, position UP*2.5
   - Body: font_size=28-32, ORIGIN area
   - Labels: font_size=20-24, adjacent to what they label
   Never more than 3 font sizes in one video.

2. LINE LENGTH: Max 35 characters per line. Break with newlines if longer.

3. TEXT CONTRAST:
   - Primary text: WHITE on dark background
   - Secondary: #aaaaaa (light gray)
   - Highlighted: use the concept's semantic color
   - White text on colored shapes, colored text only on black background
"""

# ─── ANTI-PATTERNS ───

ANTI_PATTERNS = """
## ANTI-PATTERNS (what makes videos BAD)

1. DECORATIVE SHAPES: Shapes without labels are visual noise. Delete them.
2. DATA DUMP: 8+ items simultaneously. Break into chunks of 3-4.
3. ORPHANED LABELS: Text floating in space, not attached to any visual.
4. COLOR SALAD: 7+ bright colors with no semantic meaning.
5. STATIC TEXT WALLS: Paragraphs on screen. Animation should REPLACE text.
6. ANIMATION FOR DECORATION: Spinning/bouncing for no reason. Motion must mean something.
7. SIMULTANEOUS COMPETING ANIMATIONS: Two unrelated things moving at once.
8. USING SHAPES AS CHARACTERS: Circle ≠ person. Triangle ≠ lawyer. Use labeled cards.
"""

# ─── STORYTELLING ───

STORYTELLING_RULES = """
## STORYTELLING (Pixar + Veritasium + McKee)

1. HOOK (first 10%): Disrupt the viewer's understanding. Question or surprise, never statement.
   "What if courts worked like hospitals?" NOT "Today we'll learn about courts."

2. MISCONCEPTION PHASE (10-30%): Show WHY the viewer's intuition is wrong BEFORE correct explanation.
   People don't pay attention to correct explanations if their wrong model isn't broken first.
   (Veritasium PhD research: "Clarity numbs the mind, confusion can crack it open.")

3. PROGRESSIVE BUILD (30-70%): Each scene raises a NEW question or reveals a new piece.
   The viewer thinks "wait, so what happens next?" at every transition.

4. CLIMAX (70-85%): The aha moment. Must be the most VISUAL moment, not just text.

5. CALLBACK ENDING (85-100%): Reframe the opening question with new understanding.

6. NARRATION: Conversational. Short sentences (<15 words). Active voice.
   "The court decides" NOT "A decision is made by the court."
"""

# ─── COMPLETE REFERENCE FOR CODE GENERATION ───

def get_full_design_knowledge() -> str:
    """Get all domain knowledge as a single string for injection into prompts."""
    return "\n\n".join([
        LAYOUT_RULES,
        COLOR_RULES,
        VISUAL_VOCABULARY,
        ANIMATION_RULES,
        TYPOGRAPHY_RULES,
        ANTI_PATTERNS,
    ])


def get_storytelling_knowledge() -> str:
    """Get storytelling knowledge for story generation/review."""
    return STORYTELLING_RULES


def get_review_knowledge() -> str:
    """Get all knowledge for evaluation/review systems."""
    return "\n\n".join([
        LAYOUT_RULES,
        COLOR_RULES,
        VISUAL_VOCABULARY,
        ANIMATION_RULES,
        TYPOGRAPHY_RULES,
        ANTI_PATTERNS,
        STORYTELLING_RULES,
    ])
