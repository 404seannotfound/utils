---
name: choir
description: Local `choir` CLI that routes a prompt to one or more specific configured cloud LLMs (OpenAI GPT-5/4.x/o3, Anthropic Claude 4.7/4.6/Haiku, Google Gemini 3/2.5, xAI Grok 4, plus Ollama for local) and returns their raw outputs, with optional saved comparison runs. It is a delegation, parallel-content, and evaluation tool — use it when a sub-task is best handled by a specific non-Anthropic model ("have GPT-5 write this SQL", "use Haiku for the cheap classification step"), when fanning out the same prompt across multiple models in parallel (generating N variations, capability-testing whether a given model can handle a specific input, A/B sampling, building eval/test pipelines), or when a script/test pipeline needs a deterministic CLI-level LLM call. Multi-model fan-out can be saved with `--save` and recalled later via `choir runs`, and a separate "judge" model can summarize/score the participants either inline (`--compare-with`) or after the fact (`choir runs compare <id> --with <model>`) — the latter lets you redo a failed comparison without re-running the participant calls. API keys and model configs live in the Choir macOS app's database and are reused by the CLI; env vars and `--api-key`/`--base-url` override per-call. Single-model output is plain text on stdout; multi-model output is JSON. Summarizing or comparing multi-model results is *only* requested when the user asks for it — usually the caller wants the raw outputs to feed forward. Do not use for sending messages back into this Claude session, for streaming output, or as a substitute for tools the user already has direct access to.
---

# Choir CLI skill

`choir` is a local CLI that wraps Sean's configured LLM keys, model registry, and saved comparison runs, sharing a database with the Choir.app macOS GUI (`~/Library/Application Support/Choir/choir.db`). Use it to route LLM work to specific models without bothering the user about credentials, and to persist multi-model runs that may be summarized/scored later.

## Primary uses

1. **Delegation** — a sub-task is best handled by a specific model.
   `choir ask "Write a regex for IPv6 with zone IDs" --model gpt-5`

2. **Parallel content generation** — same prompt, multiple models, structured output.
   `choir ask "Suggest 3 commit messages" --models gpt-5,claude-opus-4-7,gemini-3-pro --stdin < diff.txt`

3. **Capability / regression testing in pipelines** — pipe JSON to `jq`:
   ```bash
   choir ask "$(cat fixtures/sql.txt)" --model gpt-5 --json --stdin \
     | jq -e '.[0].text | test("SELECT.*FROM users")'
   ```

4. **Saved comparison runs with judge/summarizer** — when the user wants ranked, scored, or compared output.
   ```bash
   choir ask "..." --models gpt-5,claude-opus-4-7,gemini-3-pro \
     --compare-with claude-opus-4-7 --judge "Focus on factual accuracy."
   ```
   The `--compare-with` flag implies `--save`; the run + summary are persisted and visible in the GUI's history.

## Discovery first

Before assuming a model or key exists:
```bash
choir models list --json --enabled-only
choir keys list --json
```

## Single-model query

```bash
choir ask "<prompt>" --model <name-or-model-id> [--system "..."] [--temperature 0.3] [--max-tokens N] [--stdin]
```

Output: plain text on stdout. Stderr gets errors. Exit 0 / 2.

## Multi-model fan-out

```bash
choir ask "<prompt>" --models gpt-5,claude-opus-4-7,gemini-3-pro
```

Without `--save`, output is a JSON **array**:
```json
[{"name": "...", "model_id": "...", "provider": "...", "text": "...", "latency_ms": 1234, "input_tokens": 17, "output_tokens": 42}, ...]
```

With `--save` (or `--compare-with`), output is a JSON **object** with a stable `run_id` you can use later:
```json
{
  "run_id": "4DFA7852-…",
  "participants": [ ... ],
  "summary": { "is_summary": true, "name": "...", "text": "...", ... }   // only if --compare-with was passed
}
```

Errored elements have `"error": "..."` instead of `text`. Exit code 2 if any failed, but JSON still includes successes. **Don't summarize, compare, or pretty-print the responses unless the user explicitly asks** — the common case is feeding outputs forward.

## Comparison & redo (the run-id workflow)

When the user wants a model to judge/rank/summarize multi-model output, prefer the saved-run path so it's redoable on failure:

```bash
# Inline: run participants AND have a judge summarize them, all persisted.
choir ask "..." --models a,b,c --compare-with claude-opus-4-7 [--judge "..."]

# After the fact (or if the inline summary failed): re-run summarizer over saved participants.
choir runs compare <run-id-or-prefix> --with gpt-5 [--judge "..."]
```

`runs compare` **appends** a new summary row by default. Pass `--replace` to delete prior summary rows for that run first. Different summarizer models can be tried sequentially without re-running the participants — that's the whole point.

**Knitting in pre-computed responses**: when the user has output gathered outside choir (manual API calls, web UI copy-paste, transcripts), attach it to the run as if it had been a participant:

```bash
choir runs ingest <run-id> --as-model claude-opus-4-7 --text-file path/to/response.md
choir runs ingest <run-id> --as-model gpt-5 --stdin < response.txt
choir runs ingest <run-id> --as-model gemini-3-pro --text "short response inline" [--replace]
```

`--replace` drops prior participant rows for that config (within the run) before inserting; default is **append**. The imported row has `latency_ms = null` so it's distinguishable from real calls in `runs show`. Pass `--input-tokens N --output-tokens N --latency-ms N` if you have actual metrics. Use `--as-summary` to ingest as a summary row instead of a participant (e.g. importing a hand-edited judgment).

**Retrying failed participants** (the participant analog of summary redo):

```bash
# Re-run all participants in this run that errored, append fresh attempts.
choir runs add <run-id> --retry-failed [--replace] [--temperature N] [--api-key …]

# Add (or re-run) specific models against this run's prompt.
choir runs add <run-id> --models gpt-5,claude-opus-4-7 [--replace]

# Combined: retry the failures AND add new participants in one shot.
choir runs add <run-id> --retry-failed --models gemini-3-pro --replace
```

`--retry-failed` uses each model's *current* stored config (so if the user fixed a model_id or temperature after the original run failed, the retry picks up the fix). `--replace` deletes the prior participant rows (errored or otherwise) for the configs being run; default is **append**, matching `runs compare`. Per-call `--temperature` / `--api-key` / `--base-url` / `--system` overrides apply to the new attempts only — they do not write to the DB.

Other run management:
```bash
choir runs list [--limit 25] [--json]
choir runs show <id> [--json]    # participants + all summaries
choir runs delete <id>           # cascade-deletes results
```

Run IDs accept any unique 8-char prefix.

## Per-call key override (no DB write)

```bash
OPENAI_API_KEY=sk-... choir ask "..." --model gpt-5
choir ask "..." --model gpt-5 --api-key sk-...
choir ask "..." --model llama3.1:8b --base-url http://other:11434/v1
```

Recognized env vars: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` (or `GOOGLE_API_KEY`), `GROK_API_KEY` (or `XAI_API_KEY`).

## Managing config (only when asked)

```bash
choir keys set <openai|anthropic|gemini|grok> <key>      # store in DB
choir keys set <provider> -                              # read key from stdin
choir keys remove <provider>
choir keys test <provider> [--model <ref>]               # 1-token ping

choir models add --name "..." --provider ollama --model-id llama3.1:8b
choir models set <ref> --temperature 0.3 --max-tokens 2048
choir models {enable,disable,remove} <ref>
```

`<ref>` is name, model_id, or LLMConfig id (case-insensitive on the first two).

## Default model picks

- "Fast / cheap": `claude-haiku-4-5-20251001` or `gpt-4o-mini`.
- "Smartest": `claude-opus-4-7` or `gpt-5`.
- "Reasoning": `o3`, `o3-pro`, `o4-mini` — these *ignore* `--temperature`; don't tune it.
- For **judge/summarizer**: prefer a strong instruction-follower (`claude-opus-4-7`, `gpt-5`) over a reasoning model — the summarizer prompt expects a structured response with a fenced `scores` JSON block.

If the user asks for a comparison summary after a run, lead with concrete differences (where models disagree, where they agree on a subtle point, latency/cost tradeoffs), not generic recitation.

## Failure modes

- **`Model not found: <ref>`** — name didn't match any row. Run `choir models list --json` and suggest close matches.
- **`Missing API key: <provider>`** — give the exact `choir keys set …` command. Never solicit a key in chat.
- **HTTP error from provider** — usually transient (429/503/529). Mention the error; offer to retry once. Don't auto-retry more than once.
- **Inline summary failed but participants succeeded** — the run is still saved. Tell the user: "The participant calls succeeded (run id `<prefix>`), but the summarizer errored. I can retry with `choir runs compare <prefix> --with <other-model>`." That's exactly what the redo path is for.
- **Empty response with no error** — provider quirk; surface it rather than silently treating as success.

## Out of scope

- Sending messages back into this Anthropic/Claude session.
- Streaming. All output is batched.
- Replacing the Choir GUI's history/comparison/charts view — for visual analysis (radar charts on judge scores), point the user at the GUI; runs saved by the CLI show up there automatically.
- Local backend lifecycle (download/install of Ollama or LM Studio) — future Phase 2 of the CLI; today it can *call* a running Ollama instance, but not install one.
