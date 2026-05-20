# Workflow — setting up a new engagement page

This is the operational pattern. The aesthetic is in `style-envelope.md` and `svg-patterns.md`; the *process* lives here.

## The art-cartoon folder layout

Every project that wants art creates an `art/cartoon/` subfolder (typically inside the page's own folder, e.g. `clients/<name>/art/cartoon/`). The folder ends up looking like this:

```
art/cartoon/
├── banner.svg              ← hand-drawn (hero strip or index thumbnail)
├── gantt.svg               ← hand-drawn (living timeline)
├── p0-bootstrap-night.jpeg ← Grok JPEG (phase 0 panel 1)
├── p0-map-editor.jpeg
├── p1-reframe-fork.jpeg
├── p1-bug4-timezone.jpeg
├── …
├── _prompts.tsv            ← name<TAB>subject for every JPEG (preserved)
└── _gen_batch.sh           ← parallel-batch driver (copy of skill asset)
```

Files prefixed with `_` are build artifacts. They're not loaded by the page, but they make the work reproducible — delete a JPEG, re-run the batch, regenerate just that one image.

## File-naming convention

JPEGs use a `pN-shortname.jpeg` pattern keyed to the phase + scene:

- `p0-bootstrap-night.jpeg` (phase 0, the bootstrap-night scene)
- `p3-bug73-pin.jpeg` (phase 3, bug #73 scene)
- `p4-acl-pivot.jpeg` (phase 4, the ACL pivot scene)
- `runcible.jpeg` (a one-off side-quest scene, no phase prefix needed)

The prefix makes the cartoons sort naturally in `ls`, and the shortname is a hint at what's in it. Aim for ~3 words; lowercase; dashes between words.

SVGs use plain semantic names: `banner.svg`, `gantt.svg`, occasionally `hero-strip.svg` if it differs from `banner.svg`.

## The `_prompts.tsv` format

Two columns, tab-separated, no header row:

```
p0-bootstrap-night	Subject: a stocky bearded man with round glasses (PHAETHON…
p1-reframe-fork	Subject: a stocky bearded man with round glasses (PHAETHON…
```

The first column is the filename **without `.jpeg`**. The second is the full subject prompt (no style envelope — the batch script prepends that). One line per image, no blank lines, no comments.

When you re-roll a single image:

```bash
rm art/cartoon/p3-bug73-pin.jpeg
bash art/cartoon/_gen_batch.sh   # skips existing, regenerates the missing one
```

When you change a prompt and want to re-roll:

```bash
# Edit _prompts.tsv to update the subject
rm art/cartoon/p3-bug73-pin.jpeg
bash art/cartoon/_gen_batch.sh
```

When you add a new image, just append a row to `_prompts.tsv` and re-run the batch.

## Running the batch driver

The batch driver lives in this skill at `assets/_gen_batch.sh`. Copy it into the project's `art/cartoon/` folder:

```bash
cp ~/.claude/skills/cartoon-doodle/assets/_gen_batch.sh ./art/cartoon/
chmod +x ./art/cartoon/_gen_batch.sh
```

It runs **4 jobs in parallel by default** (controlled by `MAXP` at the top of the script). Each job:

- Reads one `name<TAB>subject` line from `_prompts.tsv`
- Skips if `art/cartoon/<name>.jpeg` already exists (`genimg.sh` refuses to clobber anyway)
- Otherwise calls `genimg.sh` with the style envelope + subject
- Logs per-job to `/tmp/genimg-<name>.log` so concurrent stderr doesn't get tangled
- Reports `[done]` / `[FAIL]` per image

If a job fails, the log file has the curl response so you can diagnose (usually rate limits, occasionally a malformed prompt). Re-running picks up where the failures left off.

## Wiring JPEGs into the page

Sean's pages use a `.phase__strip` CSS grid of `<figure>/<figcaption>` cards. Inside each phase section, drop:

```html
<div class="phase__strip">
  <figure>
    <img src="art/cartoon/p3-bug73-pin.jpeg"
         alt="Cartoon: a ranger enters a 4-digit PIN on a giant keypad. Sign overhead: 15 ATTEMPTS THEN LOCKOUT. Phaethon nearby with a clipboard marked #73.">
    <figcaption><strong>#73 · per-callsign PIN as login 2FA</strong> — the most significant feature of the marathon. 15-attempt lockout, Lead-only reset.</figcaption>
  </figure>
  <figure>
    <img src="art/cartoon/p3-bug44-leadership-edit.jpeg" alt="…">
    <figcaption><strong>#44 · OOH placed in the wrong leadership row</strong> — the canonical_role() bug.</figcaption>
  </figure>
  <!-- more figures -->
</div>
```

The `.phase__strip` CSS (from the customer-history `style.css`):

```css
.phase__strip {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  margin: 6px 0 22px;
}
.phase__strip figure {
  margin: 0;
  border: 2.5px solid var(--ink);
  border-radius: var(--radius);
  background: #fff;
  box-shadow: var(--shadow);
  overflow: hidden;
  display: flex; flex-direction: column;
}
.phase__strip img {
  display: block;
  width: 100%;
  height: auto;
  border-bottom: 1.5px dashed var(--rule);
}
.phase__strip figcaption {
  padding: 8px 12px 10px;
  font-size: 0.85rem;
  color: var(--ink-soft);
  font-style: italic;
  flex: 1;
}
.phase__strip figcaption strong {
  font-family: var(--font-display);
  color: var(--red);
  font-style: normal;
  letter-spacing: 0.3px;
}
```

The figcaption pattern is: **`<strong>caption-keyword</strong> — italicized one-line explanation`**. The keyword is hand-lettered-feeling (display font, red); the explanation is the prose.

## Wiring SVG into the page

Inline SVG (small charms, marginalia embedded directly in HTML) goes inside a wrapper div for styling:

```html
<div class="hero__strip" aria-label="…">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 240">
    <!-- the SVG -->
  </svg>
</div>
```

External SVG (the Gantt, the banner — anything large enough to be its own file) is referenced like a JPEG:

```html
<div class="gantt-frame">
  <img src="art/cartoon/gantt.svg" alt="Living Gantt: …">
</div>
```

The relevant CSS classes (`.hero__strip`, `.gantt-frame`) live in the page's own `style.css` — see Sean's `customer-history` repo `css/style.css` for the canonical version, including the print stylesheet that makes "Save as PDF" work.

## The two-vocabulary decision tree

When a new section of a page needs art, ask:

1. **Is this a specific moment that has already happened?** → JPEG via Grok. One panel. Hand-lettered caption in the figcaption.
2. **Is this a timeline / structure / overview that needs to be edited later?** → SVG. Labeled `<g>` groups. Charms over text.
3. **Is this a future placeholder that may become a JPEG later?** → SVG charm now (a `?`, a paintbrush, a dashed bar). When it becomes the past, replace with a JPEG cartoon.
4. **Is this *both* an overview AND a hero?** → SVG hero strip *and* a JPEG banner thumbnail for the index card. They can coexist.

## Preserving the build artifacts (don't skip this)

After generating cartoons, **always commit `_prompts.tsv` and `_gen_batch.sh` alongside the JPEGs**. The git diff for a Sean-style art commit looks like:

```
clients/foo/art/cartoon/_gen_batch.sh
clients/foo/art/cartoon/_prompts.tsv
clients/foo/art/cartoon/banner.svg
clients/foo/art/cartoon/gantt.svg
clients/foo/art/cartoon/p0-bootstrap-night.jpeg
clients/foo/art/cartoon/p0-map-editor.jpeg
…
clients/foo/art/cartoon/p7-after-action.jpeg
```

The TSV and the SH together mean: anyone who comes back to this six months later can re-roll a single image (or all of them) without reverse-engineering the prompts. They are *load-bearing* — leave them in the tree, even though they're not loaded by the page.

## Cost guide

- ~$0.10 per Grok JPEG (one `genimg.sh` call).
- A typical engagement page has 15–25 JPEGs. Budget ~$2–3.
- SVG is free — author time only.
- Re-rolls of unsatisfying images are $0.10 each. Don't over-iterate.

## Common mistakes

- **Forgetting the style envelope.** Always wrap. Pure subjects without the envelope come back wildly off-style.
- **Generic character descriptions.** Always use the full visual description from `character-bible.md`, every time.
- **Not preserving the TSV.** Cartoons become unreproducible. Always commit it.
- **Drawing the Gantt in Mermaid only.** Mermaid is for the appendix (machine-readable form); the *primary* timeline is always the hand-drawn SVG. Both exist on a Sean page.
- **Cleaning up the SVG.** Stop. Sergio is messy. Add jitter, not subtract it.
- **Using sans-serif fonts inside an SVG.** Use the cursive stack. Always.
