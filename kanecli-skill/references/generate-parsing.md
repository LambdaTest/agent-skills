<!-- Read this when you need the full NDJSON event schema of `kane-cli generate --agent`, or when references/generate.md's summary isn't enough. Owns the generate_* event types, their fields, the parse strategy, and the terminal generate_done schema. The run/testmd event schema lives in parsing.md. -->

# Reading `generate --agent` Output

> **Internal reference only.** The event types and field names below are for you to parse programmatically. **Never expose them to the user** — present plain-language scenarios/cases per `references/generate.md`, never `generate_snapshot`, `request_id`, `generate_done`, or raw JSON.

With `--agent`, `kane-cli generate` writes **one JSON object per line** to **stdout**. Unlike `run` (which has untyped `step`/`status` progress lines), **every generate line is typed** — it always has a `type` field. That makes parsing simpler:

```
for each line of NDJSON:
  parse JSON, switch on obj.type
  if obj.type === "generate_done"          → terminal event, stop parsing
  if obj.type === "generate_snapshot"      → the deliverable (full scenarios + cases)
  if obj.type === "generate_clarification" → turn ended awaiting an answer (still exit 0)
  else                                     → progress / informational
```

Build post-turn logic on **`generate_done`** (terminal, stable schema) and read the result from **`generate_snapshot`** (emitted once, at turn end).

## Event types

Generate-specific (typed `generate_*`):

| `type` | Key fields | Meaning → what to do |
|---|---|---|
| `generate_upload` | `file`, `index`, `total`, `status` | Only when `--files` is used. Emitted once per attached file **before `generate_start`**, while the file uploads; `status` goes `"uploading"` → `"done"` (or `"failed"`). Progress only — narrate "attaching <file>…" or ignore. A failed upload surfaces as an `error` + non-zero exit. |
| `generate_start` | `request_id`, `objective_chars`, `scenario_limit`, `per_scenario_limit`, `is_refine` | Turn began. **Capture `request_id`** — it's the handle for every later `--refine` / `--save`. `is_refine` distinguishes a new request from a continuation. |
| `generate_thinking` | `took_ms` | Liveness only. Narrate "thinking…" or ignore. |
| `generate_progress` | `pct` | Milestone (25 / 50 / 75 / 100). Optional progress display — not a completion signal. |
| `generate_snapshot` | `scenario_count`, `case_count`, `scenarios[]` | **The deliverable** — full scenarios, each with its cases. Each case carries `title`, `polarity` (`"p"`/`"n"`/`"e"` = Positive / Negative / Edge), `category` (`"Functional"`, `"Security"`, …), `priority`. Present it per `generate.md`. Emitted exactly once. |
| `generate_clarification` | `text` | The generator needs an answer; the turn ended (exit 0) awaiting it. **Not an error** — answer via `--refine --req` (see `generate.md`). |
| `generate_chat` | `text` | The model's prose reply (e.g. what a refine changed). Show as info. |
| `generate_save_result` | `suite_dir`, `saved`, `fell_back`, `warning?` | `--save` wrote files. `saved` = files written; `fell_back` = cases written as prose because they couldn't be expanded; `warning` e.g. `"no functional test cases"`. |
| `generate_done` | `request_id`, `status`, `scenario_count`, `case_count`, `refine_hint`, `save_hint`, `suite_dir?` | **Terminal line.** Branch on `status`; use `refine_hint` / `save_hint` **verbatim** as the next command. `suite_dir` present only after a `--save`. |

Shared with `run` (NOT generate-specific — don't treat as part of the generate contract):

| `type` | Fields | Meaning |
|---|---|---|
| `project_folder_auto_defaulted` | resolved project + folder (id, name) | Run-startup gate auto-resolved a project/folder when none was configured (or the cached one was stale/invalid). Fires before `generate_start`. Translate to plain language (see `references/test-manager.md`). |
| `error` | `message` | A failure occurred; pair with the exit code to decide retry vs abort. |
| `update_available` | `current`, `latest`, `severity` | A newer kane-cli exists. Informational; emitted before `generate_start`. |

## Terminal `generate_done`

Example after a **`--save`** run (note `suite_dir` — a new/refine turn omits it):

```json
{
  "type": "generate_done",
  "request_id": "23271",
  "status": "completed",
  "scenario_count": 3,
  "case_count": 11,
  "refine_hint": "kane-cli generate \"<refinement>\" --refine --req 23271",
  "save_hint": "kane-cli generate --save --req 23271",
  "suite_dir": ".testmuai/tests/checkout-23271"
}
```

`status`: `completed` (exit 0 — including a turn that ended with a clarification) · `failed` or `ended` (exit 1) · `stopped` (exit 3). `suite_dir` is present only after a `--save`. The hints carry no `--agent` flag, but it is auto-on for non-TTY callers (agents/pipes), so re-invoking a hint verbatim still yields NDJSON.

## Exit codes

`0` completed · `1` failed · `2` error (auth / setup / transport, or an invalid flag combination) · `3` stopped / cancelled · `130` interrupted (Ctrl-C). Interactive `--refine`/`--save` continuity is by re-invocation with `--req` — there is no stdin relay.
