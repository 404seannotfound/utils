# Style Envelope — the constant prefix for JPEG generation

This is the prompt prefix Sean wraps around every subject when generating cartoon JPEGs via `genimg.sh`. Keep it word-for-word; the wording is what gives Grok the right aesthetic.

## The envelope (canonical)

```
Hand-drawn cartoon illustration in the loose frenetic style of Sergio Aragonés Mad Magazine margin doodles — bold dynamic ink linework with variable line weight, exaggerated cartoon figures with bulbous noses and big expressive eyes, action lines, dust clouds, motion smears, sweat droplets, hand-lettered captions integrated into the scene. Full color in classic Mad-magazine cover palette: deep red, mustard yellow, sky blue, leaf green on warm cream paper. NO photo-realism, NO digital smoothness, NO stiff geometric lines.
```

Concatenate this with the subject prompt as one space-separated string, no double newlines mid-prompt. `genimg.sh` passes the whole thing as a single `prompt` field to the model.

## Anatomy of a good subject prompt

A good subject is **one paragraph**, **3–8 sentences**, and reads like a comic panel description. The patterns below are what consistently get Grok to draw the house style.

### 1. Open with "Subject:" and the action verb

```
Subject: a stocky bearded man with round glasses (PHAETHON the Ranger, dark brown Ranger vest, name-patch PHAETHON) wrestling a giant zombie-like MAP EDITOR monster…
```

The literal word "Subject:" helps Grok parse intent. Then jump straight into who is doing what to whom.

### 2. Tag every recurring character with their name and full visual traits, every time

Don't write "Phaethon does X" — Grok hasn't seen this conversation, doesn't know Phaethon. Write:

> a stocky bearded man with round glasses (PHAETHON the Ranger, dark brown Ranger vest with name-patch PHAETHON)

Repeat the full description every time the character appears. Same for Lazareth, Tugboat, etc. See `character-bible.md`.

### 3. Make captions and on-image text explicit

Grok will only render text you ask for, and even then renders it imperfectly. Spell out exact captions in quotes or ALL CAPS:

> A small handwritten banner across the top reads: 'TWO NIGHTS · ONE BEARD'.

> Caption ribbon: BUGS BROKE AT 2 AM.

> Speech bubble: 'OVERKILL.'

> A signpost reads 'STAY-WITH-FLASK?'.

Multi-line text is unreliable; keep each caption short and single-line. Numbers on labeled items (#73, #44, etc.) generally come out legible when explicit.

### 4. Stuff the scene with specific props, not abstract concepts

Generic: "Phaethon at a desk working hard."
House style:

> Phaethon at a Chromebook at midnight surrounded by a Flask flask spilling code, an SQLite cylinder, a calendar showing MAR 4 2026, a wall clock at 11 PM, twenty-nine little commit-stamps flying off the keyboard like confetti each labeled with a tiny hash, a coffee cup, sweat droplets, motion lines.

The density of named props is what makes the panel read as Sergio. Each prop is a small joke.

### 5. End with action-line vocabulary

Sergio cartoons swarm with motion. Close every subject prompt with a phrase from this menu:

- "Sweat droplets, action lines."
- "Action lines and dust clouds."
- "Motion smears, paper scraps flying."
- "Sparks flying. Smoke puff."
- "Dust clouds, action lines, paper scraps flying."

Grok responds to this — even if it ignores the literal words, it nudges toward the chaotic margin-doodle aesthetic.

### 6. For "future" panels, ask for a dashed-line border

If the subject is something that hasn't happened yet (the EVENT, the after-action, the run-up), tell Grok:

> Dashed-line border around the whole scene to indicate FUTURE.

It will usually render it. Combined with placeholder charms (a `?`, a paintbrush, an empty calendar page), it visually signals "not yet."

## Examples that work

These are subject prompts from Sean's existing work that produced good output. Use them as templates.

### A character-in-action panel

```
Subject: a stocky bearded man with round glasses (PHAETHON the Ranger, dark brown Ranger vest with name-patch PHAETHON, marathon shorts) running an impossibly long road, a marathon bib labeled 126 pinned to his shirt. The road is littered with cartoon bug-shaped potholes, each labeled with a bug number like #73, #44, #50, #75. Sweat flying, motion lines, dust clouds. A finish-line ribbon in the distance reads MAY 5. Caption banner BUGS BROKE AT 2 AM.
```

### A decision-point panel

```
Subject: a stocky bearded man with round glasses (PHAETHON the Ranger, dark brown Ranger vest, name-patch PHAETHON) standing at a forest fork in the road. Left path leads to a shiny modern glass-and-steel castle labeled SVELTEKIT 2026 with smooth lines. Right path leads to a sturdy old castle labeled FLASK · WORKING with scaffolding and people happily using it. Four ranger ghosts hovering above with name banners: LAZ, MALARKEY, TUGBOAT, PHAETHON. Phaethon's hand reaches reluctantly toward FLASK. A signpost reads 'STAY-WITH-FLASK?'. Action lines and motion.
```

### A bug-scene panel

```
Subject: a Ranger in a dark brown Ranger vest with name-patch TUGBOAT holding a fat red MARKER drawing huge X marks across three labeled wooden signs: PERIMETER, GREEN DOT, SANCTUARY. Below the signs, a smaller label reads NOT AT SOAK. Marker-strokes and dust clouds. A stocky bearded man with round glasses (PHAETHON, dark brown Ranger vest, name-patch PHAETHON) in the background nodding approvingly.
```

### A pivot/realization panel

```
Subject: a stocky bearded man with round glasses (PHAETHON the Ranger, dark brown Ranger vest, name-patch PHAETHON) heaving a giant filing cabinet labeled 37-AREA CAPABILITY REGISTRY into a dumpster. In his other hand, three small trading-card-sized TIER CHIPS labeled LEAD, KHAKI, RANGER. A speech bubble OVERKILL. A small banner: PIVOT TAKES ONE HOUR. Dust clouds, motion lines.
```

### A "future" panel (dashed border)

```
Subject: a bustling Burning Man-style base camp at Justesen Ranch. Tents, campfires, a Windows kiosk on a card table at HQ TENT, Rangers running between locations holding walkie-talkies. A giant SOAK*2026 banner stretched between two poles. A T-0 countdown clock at zero. A stocky bearded man with round glasses (PHAETHON the Ranger, dark brown Ranger vest, name-patch PHAETHON) checking the kiosk screen. Dashed-line border to indicate FUTURE. Dust clouds, sun rays, motion.
```

## Failure modes to watch for

- **Smooth digital art.** If the result looks like a vector-app illustration, your subject was too clean. Add "NO digital smoothness" reminders inline, or add more chaos (sweat, dust, action lines).
- **Photo-realistic faces.** Reinforce "exaggerated cartoon figures with bulbous noses." Sergio characters have *big* features.
- **Wrong palette.** If Grok used pastels, reinforce "Mad-magazine cover palette: deep red, mustard yellow, sky blue, leaf green on warm cream paper."
- **No characters when you wanted them.** Lead the subject with the character description; don't bury them mid-sentence.
- **Garbled text labels.** Keep captions short (1–4 words). Numbers tend to render better than letters. If a number-on-label is critical (#73), call it out explicitly.
- **Lower resolution than the rest of the batch.** Grok occasionally returns smaller images on chaotic scenes. Just delete and re-roll — costs another $0.10.

## Re-rolling

`genimg.sh` refuses to clobber existing files. To re-render a single image:

```bash
rm path/to/image.jpeg
bash _gen_batch.sh   # only regenerates the missing file
```

Or rename the old one to `_v1.jpeg` first if you want to keep both for comparison.
