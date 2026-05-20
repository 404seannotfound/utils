# Card recipes — copy-paste configs for common services

Each recipe below is a complete `cards[]` entry. Drop into your config JSON, edit the service-specific bits (price, callback URL, app name) for the project at hand. Order them in the array as Step 1, 2, 3 in the order the user should tackle them.

The recipes are battle-tested from the redbotbluebot example. When you add a new service, follow the same patterns — direct link to the dashboard, exact strings to type with copy buttons, regex validation, hint that affirms the default when it's correct.

## Table of contents

- [Auth basics (no external service)](#auth-basics)
- [GitHub OAuth app](#github-oauth-app)
- [Stripe — API keys + products + webhook](#stripe)
- [Anthropic API key](#anthropic-api-key)
- [xAI API key](#xai-api-key)
- [Resend (email) — domain + API key](#resend)
- [Cloudflare API token (for non-wrangler-bound integrations)](#cloudflare-api-token)
- [Sentry DSN](#sentry-dsn)
- [PostHog project API key](#posthog)

---

## Auth basics

For BetterAuth-style setups. Generate a session-signing secret client-side; pre-fill the canonical callback origin and tell the user to leave it alone until the custom domain is wired.

```json
{
  "step": "Step 1",
  "title": "Auth basics",
  "subtitle": "No external service needed — generate these locally.",
  "fields": [
    {
      "key": "BETTER_AUTH_SECRET",
      "required": true,
      "placeholder": "hex string, 64 chars",
      "validate": "^[a-f0-9]{64}$",
      "hint": "Random 256-bit secret for BetterAuth session signing. Click Generate to fill it client-side via <code>crypto.getRandomValues</code>.",
      "actions": [{ "kind": "generate-hex", "bytes": 32, "label": "Generate" }]
    },
    {
      "key": "BETTER_AUTH_URL",
      "required": true,
      "default": "https://PROJECT.pages.dev",
      "validate": "^https://[a-z0-9.-]+(:\\d+)?$",
      "hint": "Where BetterAuth callback URLs are built against. <strong>The default value above is correct right now</strong> — don't change it. Only switch to your custom domain AFTER it's wired up in Cloudflare Pages.",
      "actions": [{ "kind": "test-fetch", "label": "🌐 Ping" }]
    }
  ]
}
```

Substitute `PROJECT.pages.dev` with the real preview URL.

---

## GitHub OAuth app

Full repo scope when the project audits source. For content-only access, drop `repo` from the scopes you describe in the hint.

```json
{
  "step": "Step 2",
  "title": "GitHub OAuth app",
  "subtitle": "Don't reuse another project's OAuth app — scopes and callback differ.",
  "links": [
    { "label": "Open GitHub → new OAuth app", "url": "https://github.com/settings/applications/new" }
  ],
  "instructions": [
    "<strong>Application name</strong>: <code>PROJECT — short description</code>",
    "<strong>Homepage URL</strong>: <code>https://www.PROJECT.com</code>",
    "<strong>Authorization callback URL</strong>: <code>https://www.PROJECT.com/api/auth/callback/github</code>",
    "Click <strong>Register application</strong>.",
    "On the next page, the <strong>Client ID</strong> is visible. Click <strong>Generate a new client secret</strong>, copy it once (you won't see it again)."
  ],
  "fields": [
    {
      "key": "GITHUB_CLIENT_ID",
      "required": true,
      "placeholder": "Ov23li...",
      "validate": "^Ov23li[A-Za-z0-9]+$",
      "hint": "Test opens GitHub's authorize page in a new tab. If GitHub shows a consent screen, the client id is real. If it shows an error, it's not.",
      "actions": [{ "kind": "test-github-oauth", "label": "🔍 Test OAuth flow" }]
    },
    {
      "key": "GITHUB_CLIENT_SECRET",
      "required": true,
      "secret": true,
      "placeholder": "hex string, 40 chars",
      "validate": "^[a-f0-9]{40}$",
      "hint": "Hidden input — paste safely. Can't be live-tested without a real OAuth round-trip; format-check only."
    }
  ]
}
```

---

## Stripe

Three cards' worth of stuff often gets folded into one Stripe card. Fields needed: publishable key, secret key, one or two price IDs (per product), webhook signing secret. The webhook is deferred — note that in the hint.

```json
{
  "step": "Step 3",
  "title": "Stripe (products + keys)",
  "subtitle": "Two products, three required secrets. Webhook secret comes later (after first deploy on the custom domain).",
  "links": [
    { "label": "Stripe → API keys", "url": "https://dashboard.stripe.com/apikeys" }
  ],
  "instructions": [
    "Copy the <strong>Publishable key</strong> (<code>pk_live_...</code>) and the <strong>Secret key</strong> (<code>sk_live_...</code>). Use live keys for production; test keys for staging."
  ],
  "fields": [
    {
      "key": "STRIPE_PUBLISHABLE_KEY",
      "required": true,
      "placeholder": "pk_live_...",
      "validate": "^pk_(live|test)_[A-Za-z0-9]+$"
    },
    {
      "key": "STRIPE_SECRET_KEY",
      "required": true,
      "secret": true,
      "placeholder": "sk_live_...",
      "validate": "^sk_(live|test)_[A-Za-z0-9]+$",
      "hint": "Cross-field check below auto-flags any test/live mismatch with the publishable key."
    },
    {
      "key": "STRIPE_PRICE_ONESHOT",
      "required": true,
      "placeholder": "price_...",
      "validate": "^price_[A-Za-z0-9]+$",
      "hint": "From <a href=\"https://dashboard.stripe.com/products/create\" target=\"_blank\" rel=\"noopener\">Stripe → new product</a>, name <code>PROJECT — one-shot</code>, One time, <code>$AMOUNT USD</code>. Copy the resulting <code>price_</code> id."
    },
    {
      "key": "STRIPE_WEBHOOK_SECRET",
      "required": false,
      "secret": true,
      "placeholder": "whsec_...",
      "validate": "^whsec_[A-Za-z0-9]+$",
      "hint": "Defer until custom domain is wired. After first prod deploy: <a href=\"https://dashboard.stripe.com/webhooks/create\" target=\"_blank\" rel=\"noopener\">Stripe → Webhooks → Add endpoint</a>, point at <code>https://www.PROJECT.com/api/stripe/webhook</code>."
    }
  ]
}
```

The Stripe mode-mismatch check (pk_live + sk_test, etc.) is built into the template's sanity-checks panel. Fires automatically when both keys are present.

---

## Anthropic API key

```json
{
  "step": "Step 4",
  "title": "Anthropic API key",
  "subtitle": "Claude calls for the LLM passes.",
  "links": [
    { "label": "Anthropic → API keys", "url": "https://console.anthropic.com/settings/keys" }
  ],
  "instructions": [
    "Click <strong>Create Key</strong>. Name it after the project.",
    "Copy the <code>sk-ant-api03-...</code> key once (won't be shown again).",
    "If the project uses Opus, <strong>confirm Opus access is enabled</strong> on this workspace."
  ],
  "fields": [
    {
      "key": "ANTHROPIC_API_KEY",
      "required": true,
      "secret": true,
      "placeholder": "sk-ant-api03-...",
      "validate": "^sk-ant-(api03|admin01)-[A-Za-z0-9_\\-]+$",
      "hint": "Format-checked only. Anthropic's API blocks browser-origin secret-key calls (CORS), so the key can't be live-tested from this page."
    }
  ]
}
```

---

## xAI API key

```json
{
  "step": "Step 5",
  "title": "xAI API key",
  "subtitle": "Grok calls for image generation.",
  "links": [
    { "label": "xAI → API keys", "url": "https://console.x.ai/team/default/api-keys" }
  ],
  "instructions": [
    "Click <strong>Create API key</strong>. Name it after the project.",
    "Copy the <code>xai-...</code> key."
  ],
  "fields": [
    {
      "key": "XAI_API_KEY",
      "required": true,
      "secret": true,
      "placeholder": "xai-...",
      "validate": "^xai-[A-Za-z0-9]+$"
    }
  ]
}
```

---

## Resend

Has two parts — domain verification (which lives in Resend + Cloudflare DNS) and the API key.

```json
{
  "step": "Step 6",
  "title": "Resend (email)",
  "subtitle": "Transactional email — audit-complete notices, alerts, digests.",
  "links": [
    { "label": "Resend → sign up", "url": "https://resend.com/signup" },
    { "label": "Resend → Domains", "url": "https://resend.com/domains" },
    { "label": "Resend → API Keys", "url": "https://resend.com/api-keys" }
  ],
  "instructions": [
    "Add <code>PROJECT.com</code> as a sending domain. Resend returns DKIM/SPF/return-path records — add them in <a href=\"https://dash.cloudflare.com/\" target=\"_blank\" rel=\"noopener\">Cloudflare DNS</a> for the domain.",
    "Create an API key named after the project. Permission: <code>Sending access</code> only (NOT full access — defense in depth)."
  ],
  "fields": [
    {
      "key": "RESEND_API_KEY",
      "required": true,
      "secret": true,
      "placeholder": "re_...",
      "validate": "^re_[A-Za-z0-9_]+$"
    }
  ]
}
```

---

## Cloudflare API token

For projects that need to call the Cloudflare API directly (D1 admin tools, R2 outside the binding, etc.). `wrangler`-bound resources don't need this.

```json
{
  "step": "Step N",
  "title": "Cloudflare API token",
  "subtitle": "Only needed if the worker calls the Cloudflare API directly (not via bindings).",
  "links": [
    { "label": "Cloudflare → API Tokens → Create", "url": "https://dash.cloudflare.com/profile/api-tokens" }
  ],
  "instructions": [
    "Click <strong>Create Token</strong> → start from <code>Edit Cloudflare Workers</code> template (or build a custom one with only the scopes the worker actually needs).",
    "Scope to the specific account + zone if possible — least privilege.",
    "Copy the token (40-char string starting with letters)."
  ],
  "fields": [
    {
      "key": "CLOUDFLARE_API_TOKEN",
      "required": true,
      "secret": true,
      "placeholder": "40 characters",
      "validate": "^[A-Za-z0-9_-]{40,}$"
    },
    {
      "key": "CLOUDFLARE_ACCOUNT_ID",
      "required": true,
      "placeholder": "32-char hex",
      "validate": "^[a-f0-9]{32}$",
      "hint": "Found at the bottom-right of any zone's Overview tab, or in the account URL after `accounts/`."
    }
  ]
}
```

---

## Sentry DSN

```json
{
  "step": "Step N",
  "title": "Sentry (error tracking)",
  "links": [
    { "label": "Sentry → Settings → Client Keys (DSN)", "url": "https://sentry.io/settings/projects/" }
  ],
  "instructions": [
    "Create a project for this app if you don't have one. Pick the right platform (JavaScript / Node / Cloudflare Workers).",
    "Copy the DSN."
  ],
  "fields": [
    {
      "key": "SENTRY_DSN",
      "required": true,
      "placeholder": "https://...@sentry.io/...",
      "validate": "^https://[a-f0-9]+@[a-z0-9.]+\\.ingest\\.[a-z0-9.]*sentry\\.io/[0-9]+$"
    }
  ]
}
```

---

## PostHog

```json
{
  "step": "Step N",
  "title": "PostHog (product analytics)",
  "links": [
    { "label": "PostHog → Project settings → Project API Key", "url": "https://us.posthog.com/settings/project" }
  ],
  "fields": [
    {
      "key": "POSTHOG_PROJECT_API_KEY",
      "required": true,
      "placeholder": "phc_...",
      "validate": "^phc_[A-Za-z0-9]+$",
      "hint": "Safe to ship to the browser — this is the public ingestion key, not the personal API key."
    },
    {
      "key": "POSTHOG_HOST",
      "required": false,
      "default": "https://us.i.posthog.com",
      "placeholder": "https://us.i.posthog.com",
      "hint": "EU customers use <code>https://eu.i.posthog.com</code>. US default is correct unless your PostHog project lives in the EU region."
    }
  ]
}
```

---

## Adding a new recipe

When you need a service that isn't here:

1. **The "go" link** points at the deepest dashboard page where the user actually retrieves the value (not the marketing landing). Most providers have a stable `/settings/keys` or `/dashboard/...` URL.

2. **The instructions** name buttons literally (`Click <strong>Create Token</strong>`) and copy-paste-friendly values (`Name it <code>...</code>`). The build-time copy-button injection runs on every `<code>` inside `.card ol li` — so the more values you wrap in `<code>`, the more one-click pastes the user gets.

3. **The regex** matches the published key shape from the vendor's docs. Test against a real example before committing. If the vendor doesn't publish a shape, leave `validate` off — the green border just won't appear, no harm done.

4. **The hint** explains:
   - What the value IS (one short sentence)
   - Any cross-field consequences ("matches mode of pk key")
   - Why no live test if relevant ("Anthropic blocks browser-origin CORS")
   - Affirmation if a default is correct ("the default above is correct right now")

5. **Actions** only when the test is safe (no secret-key fetches). Use `test-fetch` for public URLs, `test-github-oauth` for GitHub Client IDs, `generate-hex` for client-side-generatable secrets.

Add the recipe to this file when it's worked on a real project. The corpus pays compound interest.
