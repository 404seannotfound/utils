---
name: cartoon-doodle
description: Sean's house-style drawing skill — Sergio Aragonés / Mad-Magazine-margin-doodle cartoon JPEGs (rendered via scriptorium's `genimg.sh` against xAI Grok at ~$0.10/image) paired with hand-authored "living document" SVG that uses `feTurbulence` + `feDisplacementMap` for hand-jittered linework. Use this skill whenever Sean asks for ART, CARTOONS, ILLUSTRATIONS, DOODLES, HAND-DRAWN SVG, BANNERS, HERO STRIPS, GANTT CHARTS, PHASE PANELS, ENGAGEMENT-LOG VISUALS, STORY PANELS, MARGINALIA, or any HOUSE-STYLE imagery — even when the request is implicit ("this page needs some visual", "make a banner for X", "illustrate this bug as a panel", "add some art to the audit log", "draw me a charm for the timeline"). The skill encodes a two-vocabulary system (past events → JPEG via Grok; living/future docs → hand-jittered SVG), the constant style envelope, the recurring character bible, the parallel-batch generation workflow via `_gen_batch.sh` + `_prompts.tsv`, the cream-paper palette, and the "augmentable, not redrawn" philosophy for SVG documents that need to grow over time. Do NOT use for photo-realism, technical diagrams (flowcharts/ERDs/UI mockups), or stock-illustration style. Reach for this any time Sean wants something to *look like the NWIOI page* or *the Rangers, Kinda page* — that is the house style.
---

# Cartoon Doodle — Sean's house-style drawing skill

Sean's customer-history engagement logs, blog post panels, dashboards, and any document worth illustrating share **one aesthetic**: Sergio Aragonés / Mad-Magazine margin doodles on cream paper, with hand-jittered SVG for anything meant to be edited as time goes on. He has built this style from scratch across the NWIOI engagement log and the Rangers, Kinda — WAR engagement log, and he is tired of explaining it. This skill captures the whole recipe so you can draw in his voice without him repeating himself.

## The two-vocabulary system

This is the most important thing to internalize.

| Vocabulary | When to use | How to make it |
|---|---|---|
| **Sergio JPEG cartoons** | Concrete moments that have already happened. A bug story. A character in action. A panel of "this is what that day felt like." | xAI Grok via `scriptorium/scripts/genimg.sh` with the style envelope wrapped around a specific subject prompt. ~$0.10/image. |
| **Hand-jittered SVG** | "Living documents" — Gantt charts, hero strips, banners, charm pictographs, marginalia, anything that needs to *grow* without being redrawn. Future/dashed segments. Pure-icon work. | Inline SVG authored directly, using the `feTurbulence` + `feDisplacementMap` filter pair to give every stroke a hand-drawn jitter. Every meaningful unit is a labeled `<g>` group so it can be augmented later. |

The slogan: **the past is drawn, the future is sketched.** JPEGs capture what has happened. SVGs hold space for what hasn't. A typical Sean page mixes both — phase panels are JPEGs, the Gantt and hero strip are SVG, the dashed "still ahead" rows have placeholder SVG charms today and may get JPEG cartoons later when those rows become past.

## Quick start: JPEG cartoon via Grok

1. **Find scriptorium.** Sean's checkout is typically at `~/git/scriptorium/`. The wrapper is `scripts/genimg.sh`. It reads `XAI_API_KEY` from `scriptorium/.env`. If the repo isn't at the expected path, ask before assuming an alternative — don't invent one.
2. **Wrap the subject in the style envelope.** See `references/style-envelope.md` for the canonical envelope. Combine envelope + subject (a single block of prose, no double-newlines mid-prompt — that confuses Grok). Pass the combined string as one argument to `genimg.sh`.
3. **Pick an output path** under the project's `art/cartoon/` folder (creating it if missing). Use descriptive filenames keyed to the panel — `p3-bug73-pin.jpeg`, `phase-2-hardening.jpeg`, `runcible.jpeg`. The script refuses to clobber existing files, so re-rolling means deleting first (or appending `_v2`).
4. **Run.** Single image:

   ```bash
   bash ~/git/scriptorium/scripts/genimg.sh \
     /path/to/project/clients/foo/art/cartoon/p3-bug73-pin.jpeg \
     "$STYLE_ENVELOPE $SUBJECT" \
     xai
   ```

   For many images, see "Batch generation" below.

5. **Read the result with `Read`** so you can spot-check. Grok occasionally returns smaller-resolution images for chaotic scenes; if quality is off, re-roll (delete + re-run).

### Batch generation (parallel)

When you have 4+ images, drive them in parallel from a TSV. Copy `assets/_gen_batch.sh` into the project's `art/cartoon/` folder, write a `_prompts.tsv` file (one `name<TAB>subject` per line), and run. The script runs 4 in parallel by default, logs to `/tmp/genimg-<name>.log` per job, and skips any name whose `.jpeg` already exists — so re-running only generates the missing ones.

`_prompts.tsv` and `_gen_batch.sh` live alongside the JPEGs in `art/cartoon/`. **This is non-negotiable.** Preserving them makes the cartoons reproducible — future-Sean (or a re-roll session) can edit a prompt, delete the corresponding JPEG, and re-run the batch to regenerate just that one. See `references/workflow.md` for the full directory layout.

## Quick start: hand-jittered SVG

Sean's SVGs share four things:

1. **Cream paper background** via a tiny pattern of speckled dots — see `references/svg-patterns.md` for the `<pattern>` definition.
2. **Three roughness filters** — `#rough` (default jitter), `#roughBig` (heavier, used for frame strokes), `#roughTiny` (subtle, used for small charms). Filter defs go in `<defs>`; every meaningful path gets `filter="url(#rough)"` applied.
3. **A labeled `<g>` group per meaningful unit** — every charm, every row, every callout is its own group with a comment header (`<!-- charm: PIN keypad · #73 PIN 2FA -->`). This is the key to "living documents": future-Sean opens the file, finds the right group by comment, copies the closest one, and edits the x/y + label. Nothing is redrawn.
4. **Hand-lettered captions** inside the SVG — labels, dates, milestone names, "YOU ARE HERE" pennants, ribbon banners. Use the cursive font stack: `font-family="'Marker Felt', 'Comic Sans MS', 'Chalkboard SE', cursive"`.

For copy-paste defaults (paper pattern, filters, Gantt time-axis math, charm vocabulary), see `references/svg-patterns.md`. Use `assets/living-svg-skeleton.svg` as a starting point — it has all the defs and a couple of example labeled `<g>` charm groups.

## Where art lives

```
<project>/
└── (path to the page, e.g. clients/<name>/) or art/
    └── art/
        └── cartoon/
            ├── banner.svg              ← hero strip / index thumbnail (SVG)
            ├── gantt.svg               ← living timeline (SVG)
            ├── p0-bootstrap-night.jpeg ← phase panels (JPEG via Grok)
            ├── p1-bug4-timezone.jpeg
            ├── …
            ├── _prompts.tsv            ← name<TAB>subject for every JPEG
            └── _gen_batch.sh           ← parallel-batch driver, copy of assets/
```

Sometimes there's an `_archive/` for earlier drafts (e.g., parchment-style SVG predecessors). That's fine; keep it.

## The palette

Cream paper with a Mad-magazine-cover palette. Use these CSS custom properties (most Sean pages already declare them):

| Token | Hex | Use |
|---|---|---|
| `--paper` | `#FBF5E4` | Page background. The default. |
| `--paper-deep` | `#F1E8C9` | Section dividers, footer, banner box backgrounds. |
| `--ink` | `#1A1A1A` | Linework. The pen. |
| `--ink-soft` | `#3D352A` | Body text. |
| `--muted` | `#6C6033` | Captions, marginalia. |
| `--red` | `#C04D3A` | Accent, milestones, danger, "PILOT", title color. |
| `--yellow` | `#F5C84B` | TODAY badges, YOU ARE HERE pennants, sparkles. |
| `--blue` | `#2A78C2` | Process / hardening / DBs. |
| `--green` | `#2D7A45` | Side quests, success. |

For purple variants in Sean's recent work: `#7448B5` (deep) and `#c8b3e5` (chip background). These show up in iOS side quest and Command Center phases.

## When the request is implicit

Sean often asks for art without saying "draw" or "cartoon." Look for these phrasings and reach for this skill:

- "Make this page prettier" → propose a hero strip + a few phase JPEGs
- "This needs a visual" → propose a JPEG matched to the surrounding prose
- "Add a timeline" → SVG Gantt with charms (not a Mermaid diagram alone)
- "Illustrate the [X] bug" → JPEG panel, one charm, one caption
- "Make it look like the NWIOI page" or "like the Rangers page" → the answer is *always* this skill
- "Add some marginalia" / "doodle in the corner" → small inline SVG charms in the page (or as part of an existing SVG)

When the request could mean a real diagram instead (an ERD, a flowchart, a deployment topology), check — Sean's house style doesn't fit those. Offer the cartoon-doodle option *and* the technical-diagram option and let him choose.

## References

The body of this skill is intentionally short. Detail lives in `references/` — read the file you need, when you need it.

- **`references/style-envelope.md`** — the canonical Sergio / Mad-margin style prompt envelope (the constant prefix you wrap around every subject). Also: what makes a good subject prompt; how to write captions, character traits, props, and on-image text that Grok will actually render legibly.
- **`references/svg-patterns.md`** — the `feTurbulence` filter trio, the cream-paper pattern, the labeled-`<g>` charm pattern, Gantt time-axis math (origin + px-per-day), the EVENT-stage block pattern (sky/sand gradient for future destinations), the YOU ARE HERE pennant, common charm pictographs (SQLite cylinder, Flask flask, megaphone, PIN keypad, escalator, tier chips, tents, campfires, radio towers).
- **`references/character-bible.md`** — recurring characters: how Phaethon (Sean) looks, how Lazareth / Tugboat / Malarkey appear, how to add a new recurring character without breaking continuity. This is where to look when an existing engagement is being illustrated; new engagements can lean on this for consistency or define their own cast.
- **`references/workflow.md`** — the full project setup pattern (creating `art/cartoon/`, writing the TSV, running the batch driver, wiring JPEGs into HTML with `.phase__strip` + `<figure>/<figcaption>`, preserving the build artifacts so the work is reproducible).

## Bundled assets

Copy these into the project. They aren't loaded into context — you `cp` them and use them directly.

- **`assets/_gen_batch.sh`** — the parallel-batch driver. Copy into the project's `art/cartoon/`, drop a `_prompts.tsv` next to it, run.
- **`assets/living-svg-skeleton.svg`** — a starter SVG that already includes the cream paper pattern, the three roughness filters (`#rough` / `#roughBig` / `#roughTiny`), a desert + sky gradient for EVENT-stage blocks, and a couple of commented example `<g>` charm groups. Open it, change the viewBox, start dropping charms.

## Doing this well

A few things that separate "obviously Sean's house style" from "AI-generated art":

- **Specific captions on every image.** A Sergio doodle always has hand-lettered text — character names on vests, milestone dates on banners, "BAM!" "WHACK!" "POW!" action-bursts, "RIP PROD" tombstones, "YOU ARE HERE" pennants. Bake the caption into the subject prompt; don't hope Grok adds it on its own.
- **Specific props.** "Phaethon at a Chromebook" is generic. "Phaethon at a Chromebook surrounded by a Flask flask spilling code, an SQLite cylinder, a calendar showing MAR 4 2026, a wall clock at 11 PM, 29 commit-stamps flying off the keyboard like confetti" is the house style.
- **Charms over text-everywhere.** SVG charts should have many small icon-charms (small `<g>` groups) instead of large blocks of text. Tents, campfires, gears, escalators, tier chips, mail trucks, fire extinguishers, coffee cups, fork-in-the-road signs, padlocks, magnifying glasses. The charts read like a Ranger's hand-drawn battle map with badges sewn onto it.
- **Dashed = future.** Future segments on a Gantt are *always* dashed bars (and ideally have a "?" or a placeholder charm). The moment they happen, the dashes go solid. This visual grammar is load-bearing.
- **A single rubber stamp.** Sean's pages often have one big rotated rubber stamp ("W·A·R", "RIP PROD", "TI = PROD") in red ink — it sets the framing for the whole page. Include one when the engagement has a single defining concept.

If you find yourself drawing something *clean* — straight lines, perfect rectangles, sans-serif labels, smooth gradients with no jitter — back up. Apply the rough filter. Replace the labels with cursive. Add a charm or two.
