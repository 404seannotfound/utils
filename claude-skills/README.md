# Claude skills

Reusable [Claude Code](https://claude.com/claude-code) skills exported from `~/.claude/skills/`. One folder per skill; each is self-contained.

## What's in here

| Skill | What it does |
|---|---|
| [`cartoon-doodle`](./cartoon-doodle/) | Sean's house drawing style. Sergio-Aragonés / Mad-Magazine-margin cartoon JPEGs (rendered via [scriptorium](https://github.com/404seannotfound/scriptorium)'s `genimg.sh` against xAI Grok, ~$0.10/image) paired with hand-jittered "living document" SVG using `feTurbulence` + `feDisplacementMap`. The two-vocabulary system: **past events → JPEG** (a thing that happened, drawn), **living/future docs → SVG** (a thing that grows, sketched). Constant style envelope + character bible + parallel batch-generation workflow. Use whenever a page needs art, banners, hero strips, Gantt charts, phase panels, marginalia, or anything in Sean's house style. |
| [`choir`](./choir/) | Local [`choir`](https://github.com/404seannotfound/choir) CLI that routes a prompt to one or more specific cloud LLMs (OpenAI GPT-5/4.x/o3, Anthropic Claude 4.x/Haiku, Google Gemini 3/2.5, xAI Grok 4, plus Ollama for local) and returns their raw outputs. Multi-model fan-out, saveable comparison runs, optional judge-model summarization. Use when a sub-task is best handled by a specific non-Anthropic model, when fanning out the same prompt across many models in parallel, or when a script/test pipeline needs a deterministic CLI-level LLM call. Requires the [Choir macOS app](https://choir.so) installed for keys/configs. |
| [`make-a-seansheet`](./make-a-seansheet/) | Generate a self-contained HTML "seansheet" — a local setup worksheet that walks you through gathering external credentials (Stripe, GitHub OAuth, Resend, Anthropic, xAI, Cloudflare, etc.) and exports them as a `.dev.vars` file or a `wrangler pages secret put` shell script. Single-file output, opens via `file://`, dark theme, copy buttons next to every value, embedded browser-safe tests (no-cors fetch URL ping, OAuth new-tab open), card-completion green-state, four-way export. |

## Installing a skill on another machine

Skills live at `~/.claude/skills/<skill-name>/`. To install one of these:

```bash
# Pick which skill, then:
mkdir -p ~/.claude/skills
cp -R claude-skills/make-a-seansheet ~/.claude/skills/
```

Claude Code picks the skill up the next time it starts. Verify with the `/skills` slash command or by checking the available-skills list at session start.

## Folder layout (per skill)

```
make-a-seansheet/
├── SKILL.md          ← frontmatter (name + description) + instructions
├── assets/           ← bundled templates / example configs
├── scripts/          ← executable helpers invoked by SKILL.md
└── references/       ← longer docs loaded into context only when needed
```

Skills use [progressive disclosure](https://docs.anthropic.com/en/docs/claude-code/skills) — the name + description is always in Claude's context (~100 words), the body of SKILL.md loads when the skill triggers, and the bundled files load only as needed. Keep SKILL.md under ~500 lines and push the long stuff into `references/`.

## Authoring a new skill

Use the `anthropic-skills:skill-creator` skill bundled with Claude Code:

```
/skill-creator
```

Or just describe what you want and it'll walk you through it. After the skill works, copy it from `~/.claude/skills/<name>/` to this folder and commit.

## Why export them here

Two reasons:

1. **Cross-machine portability.** Re-clone `utils` on a new laptop, copy the relevant skills, you're back in business.
2. **Diffable history.** Skills evolve as the tasks they handle do. Tracking them in git means I can see the change that shifted a behavior, revert if needed, and share specific versions with other people.
