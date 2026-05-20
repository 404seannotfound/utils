---
name: make-a-seansheet
description: Generate a self-contained HTML "seansheet" — a local setup worksheet that walks the user through gathering external credentials (Stripe, GitHub OAuth, Resend, Anthropic, xAI, Cloudflare, etc.) and exports them as a .dev.vars file or a `wrangler pages secret put` shell script. Use this skill whenever the user wants a "seansheet", "setup worksheet", "credentials worksheet", or any one-page wizard for external API keys + secret values; whenever they ask to gather secrets for a Cloudflare Pages / Workers project; whenever they reference setup steps like "domain + GitHub OAuth + Stripe + Resend + LLM keys" together; or whenever they describe needing to track which secrets are filled and which still need to be retrieved from a vendor dashboard. Output is a single .html file opened locally via file://, with localStorage persistence, per-field validation, inline copy buttons, green-state card completion, embedded tests where safe (no-cors fetch, OAuth new-tab open), cross-field sanity checks, and a four-way export (copy/download .dev.vars, copy/download set-secrets.sh, vscode:// open link, clear-all).
---

# make-a-seansheet

> "I open the sheet, populate it, then click a link which opens VSCode with the ENV file you are going to use and shows me how to add the value."

A skill for generating a Sean-style setup worksheet from a JSON config. The worksheet is a single self-contained HTML file (opens via `file://` in Safari or any browser) that holds the user's hand through gathering external service credentials and shipping them into a Cloudflare Pages secrets store.

## When this triggers

The user says one of:
- "make a seansheet"
- "build me a setup worksheet for <project>"
- "I need to gather a bunch of API keys for <project>, help me track which ones I have"
- "scaffold a credentials sheet"

Or implicitly when they describe a new Cloudflare-Pages-shaped project (BetterAuth + GitHub OAuth + Stripe + Resend + LLM keys is the canonical surface area) and they want a checklist.

## Why this exists

Most setup docs are READMEs. The user has to scroll up and down, mentally track which steps they've done, paste secrets into a `.dev.vars` file by hand, then transcribe each one again into `wrangler pages secret put` commands at the terminal.

A seansheet collapses that into a single page with:

- **Direct links** to each vendor's dashboard (label + URL both clickable; URL visible underneath the label so the user can copy or click).
- **Step-by-step instructions** with inline `<code>` values that ALL get auto-injected tiny copy buttons — one click to clipboard, no select-drag.
- **Form fields per secret** with regex validation (green border when shape looks right).
- **Per-field tests** where they're browser-safe: `no-cors` fetch to ping a URL host; new-tab open of an OAuth `authorize` URL to visually verify a client ID is real. **Never** send secret keys via fetch from a browser — those tests get format-check only with a hint explaining why.
- **Card completion green-state**: each step's whole card turns green with a ✓ when every required field in it is filled and passes validation.
- **Progress bar** at the top (red→blue gradient).
- **Cross-field sanity checks** for current problems only (Stripe mode mismatch, duplicate price IDs, wrong-length secrets). Future-state advice belongs in field hints, not warnings.
- **Generate buttons** for client-side secret generation (`crypto.getRandomValues` for `BETTER_AUTH_SECRET`).
- **LocalStorage persistence** keyed by project name so closing the tab keeps progress.
- **Four-way export**: copy/download `.dev.vars`, copy/download `set-secrets.sh` (pipes via stdin to `wrangler pages secret put` so secrets don't end up in shell history), `vscode://file/...` open link, plus clear-all with confirm.

The canonical example lives at `~/git/redbotbluebot/setup-worksheet.html` — that's the reference implementation this skill generalizes from.

## How to use this skill

When invoked, you (Claude) follow this flow:

### 1. Interview the user briefly

Ask whichever of these isn't obvious from context:

- **Project name** (used for the localStorage key, the wrangler `--project-name` arg, and a few display labels). Defaults to `setup`.
- **Wordmark halves** — two strings that color-split red/blue (e.g. `redbot` / `bluebot`, `code` / `backstory`, `foo` / `bar`). If they don't care, default to splitting the project name in half.
- **Preview URL** — the pages.dev URL where the project lives pre-custom-domain. Used as the lockup link target and as the OAuth `redirect_uri` fallback for the GitHub-OAuth test.
- **Dev-vars path** — absolute path where the `.dev.vars` file should live; powers the `vscode://file/...` open link. Default `~/<repo>/.dev.vars` expanded against the user's home.
- **The list of external services** — which dashboards do they need to visit. Use `references/recipes.md` as the source of truth for common ones (GitHub OAuth, Stripe, Anthropic, xAI, Resend, etc.). The user might want a subset, or might want to add something exotic (e.g., Sentry, PostHog) — handle those by following the recipe format.

If they say "use the same shape as redbotbluebot," skip the interview and load `assets/example-config.json` as the starting point.

### 2. Write a config JSON

Build a JSON file at `<project-root>/seansheet-config.json` (or wherever the user prefers) following this shape:

```json
{
  "project": {
    "name": "myproject",
    "title": "myproject — setup worksheet",
    "wordmark_left": "my",
    "wordmark_right": "project",
    "subtitle": "setup worksheet",
    "page_title": "External credentials, gathered in one go.",
    "preview_url": "https://myproject.pages.dev",
    "storage_key": "myproject-setup",
    "wrangler_project": "myproject",
    "dev_vars_path": "/Users/seansp/git/myproject/.dev.vars",
    "repo_path": "~/git/myproject/"
  },
  "cards": [
    {
      "step": "Step 1",
      "title": "Card title",
      "subtitle": "Optional italic subhead under the title",
      "links": [
        { "label": "Open the vendor's dashboard", "url": "https://example.com/keys" }
      ],
      "instructions": [
        "<strong>Field name</strong>: <code>value to type</code>",
        "Click <strong>some button</strong>."
      ],
      "fields": [
        {
          "key": "ENV_VAR_NAME",
          "required": true,
          "secret": false,
          "default": "optional pre-filled value",
          "placeholder": "what the value looks like",
          "validate": "^regex$",
          "hint": "HTML allowed. Lead with affirmation when the default value is correct.",
          "actions": [
            { "kind": "generate-hex", "bytes": 32, "label": "Generate" }
          ]
        }
      ]
    }
  ]
}
```

Field-level details — see `references/recipes.md` for ready-to-paste card configs for the common services. Reuse those wholesale; only invent new ones for services not already covered.

**Field action kinds** (built into the template):
- `generate-hex` — fill with N random bytes of hex via `crypto.getRandomValues`. Params: `bytes` (default 32). Use for session secrets, signing keys.
- `test-fetch` — no-cors fetch the URL value. Reports green if the host resolves. Use for callback URLs / public origins.
- `test-github-oauth` — open `github.com/login/oauth/authorize?client_id=...` in a new tab. User visually verifies the consent screen renders (real ID) vs an error page (typo). Use ONLY for GitHub client IDs.

**Cross-field sanity checks** are baked into the template and fire only when their relevant fields are present:
- Stripe pk/sk mode mismatch (`pk_test_` + `sk_live_`)
- Duplicate `STRIPE_PRICE_ONESHOT` / `STRIPE_PRICE_CONTINUOUS` values
- `BETTER_AUTH_SECRET` not 64 hex chars
- Test-mode keys with what look like live prices

If you need additional checks beyond these, mention it to the user — they'll go in the template, not the config.

### 3. Run the build script

```bash
python3 ~/.claude/skills/make-a-seansheet/scripts/build_seansheet.py \
    <path/to/config.json> \
    <path/to/output/setup-worksheet.html>
```

The script reads the config, generates per-card HTML from the `cards` array, and stamps the placeholders in the template. Output is a single ~45 KB HTML file with no external dependencies (Google Fonts is the only network reference, and the worksheet still works offline if fonts fall back).

### 4. Show the user the result

Open the file:

```bash
open <path/to/output/setup-worksheet.html>
```

Tell the user:

> Worksheet is at `<path>`. Double-click in Finder to reopen later, or use the `vscode://` button at the bottom for direct file access. Your values persist in localStorage, scoped to `<storage_key>`.

## Field schema quick reference

| field | required | meaning |
|---|---|---|
| `key` | yes | ENV var name. Becomes the input's `data-secret`, the `.dev.vars` line key, the `wrangler pages secret put` arg. |
| `required` | no, default true | If false, gets `data-optional` and is excluded from the progress count. |
| `secret` | no, default false | If true, input type=password (masked). |
| `default` | no | Pre-filled value. Use sparingly — only when the default is genuinely correct. |
| `placeholder` | no | The grey hint inside the empty input. |
| `validate` | no | Regex. When the value matches, the input border turns green. |
| `hint` | no | HTML below the input. Lead with affirmation. |
| `actions` | no | Array of `{kind, label, ...}` action buttons inline with the input. |

## Writing good hint text

The most-broken design pattern in setup tools is "do X until Y, then switch to Z" — users interpret that as a sequence to execute *right now*. **Lead with affirmation when the default is correct**:

> The default value above is correct right now — don't change it. Only switch to `<other-value>` AFTER `<future-condition>`.

This phrasing avoids the trap.

## Anti-patterns to avoid

- **Future-state warnings in the sanity-checks panel.** Sanity checks must only fire for *current* problems. Future reminders go in field hints. (We learned this the hard way — a "BETTER_AUTH_URL still on pages.dev" warning fired prematurely and made users edit a correct value.)
- **Sending secret keys via fetch from the browser.** Stripe / Anthropic / xAI / Resend all block browser-origin secret-key calls via CORS — and that's correct security posture. Format-check only; explain why in the hint.
- **Per-field bespoke handlers.** Use the three generic kinds (`generate-hex`, `test-fetch`, `test-github-oauth`). If a service needs something more exotic, add a new generic handler to the template — don't bake project-specific logic into the action buttons.
- **Dumping a fat README into the worksheet.** Each card is one focused step. If you have 12 substeps, break it into 3 cards.

## Files in this skill

```
make-a-seansheet/
├── SKILL.md                 (this file)
├── assets/
│   ├── template.html        (the chassis — ~30KB, all CSS+JS+static panels)
│   └── example-config.json  (canonical config that regenerates redbotbluebot's sheet)
├── scripts/
│   └── build_seansheet.py   (config + template → output HTML)
└── references/
    └── recipes.md           (copy-paste card configs for common services)
```

The recipes file is the most-frequently-consulted reference — read it whenever you're building a new sheet so you reuse battle-tested patterns instead of reinventing each card.
