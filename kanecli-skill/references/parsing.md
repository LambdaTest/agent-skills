<!-- Read this when you need the full NDJSON event schema for kane-cli --agent output, or when SKILL.md §5's summary is not enough. Owns event types (progress / bifurcation / child_agent_start|end / ask_user / error), parsing strategy, run_end terminal-event schema, and ask_user/cancel responses. -->

# Parsing --agent Output

> **Internal reference only.** Everything in this section (field names, event types, JSON structure) is for you to parse programmatically. **Never expose these internal terms to the user.** The user should see plain-language summaries, not `run_end`, `final_state`, `bifurcation`, `NDJSON`, `session_dir`, or any raw JSON fields.

With `--agent`, kane-cli outputs one JSON object per line to **stdout**. Progress UI renders to **stderr**.

## The stream contract (0.8.17+)

On `run`, `testmd run` and `testrun run`, every stdout line carries two extra fields, and nothing that existed before changed:

| Field | Meaning |
|---|---|
| `v` | Contract version, `1`. It only bumps on a breaking change |
| `ts` | ISO timestamp of when the event was emitted |

The first line on every surface is an opening event:

```json
{"type":"stream_start","cli_version":"0.8.17","surface":"run","pid":16664,"v":1,"ts":"2026-09-21T08:47:26.889Z"}
```

`surface` is `run`, `testmd` or `testrun`. Use `cli_version` to tell whether a newer event or flag is available. `session_dir` may also be present when a session already exists.

Rules a parser must follow:

- **Ignore unknown fields and unknown event types.** New ones can appear in any release without a `v` bump.
- **Never assume the first line is a progress line**, and skip any line that is not JSON.
- Step lines on `run` stay **typeless** (below). Do not look for `type: "step"`.
- The documented completion event is always the last line: `run_end` for `run`, `test_md_done` for `testmd run`, `testrun_done` for `testrun run` (then `remote_done` on cloud grid runs).

**The same stream is also written to disk**, line by line as it happens: `<session_dir>/events.ndjson`, byte for byte what stdout printed. While a run is live, kane-cli keeps a small pointer file at `~/.testmuai/kaneai/sessions/active/<pid>.json` (`pid`, `cwd`, `surface`, `session_dir`, `started`, `cli_version`, `host_agent`) and removes it on exit. You normally need neither: one blocking call hands you the whole stdout. They exist for watchers such as the live strip (`references/live-strip.md`), and the log is where a suite keeps each test's own events (`references/testrun.md`). The log holds exactly what stdout held, so treat it with the same care.

## Event Types

**Progress events** (a start and completion event per step):

```json
{"step": 1, "status": "running", "remark": "Navigate to amazon.in"}
{"step": 1, "status": "done", "remark": "Navigated to amazon.in"}
{"step": 2, "status": "done", "remark": "Typed 'laptop' in search box"}
{"step": 3, "status": "failed", "remark": "Could not find Add to Cart button"}
```

| Field | Type | Description |
|-------|------|-------------|
| `step` | number | Step index. It can run one ahead of the step the person would count (a `bifurcation` takes the first slot), so count completed `done`/`failed` lines for "steps taken" rather than reading the last index |
| `status` | string | `"running"` at start; `"done"` or `"failed"` at completion |
| `remark` | string | What the agent did or why it failed |

These are **untyped** — they have no `type` field. Do **not** key on `event.type === 'step_start'` or `'step_end'`; those event types are not emitted.

**Flow events:**

| Event (`type` field) | Key Fields | Purpose |
|-------|-----------|---------|
| `project_folder_auto_defaulted` | resolved project + folder (id, name) | Run-startup gate auto-resolved a project/folder when none was configured (or the cached one was stale/invalid). Fires before any progress event on `run` / `testmd run` / `generate`. Translate to plain language (see `references/test-manager.md`). |
| `bifurcation` | `flows[]`, `count` | Agent split objective into sub-flows |
| `child_agent_start` | `child_id`, `objective`, `parent_step` | Child agent spawned |
| `child_agent_end` | `child_id`, `success`, `steps_taken`, `summary` | Child agent finished |
| `ask_user` | `question`, `step_index`, `options?` | Agent needs user input |
| `error` | `message`, `code?` | Error occurred. With `code: "unresolved_variables"` it is the pre-run refusal — the only event of the run, no `run_end` follows; schema below. |
| `test_md_evidence_ingest` | `status: "ok"\|"failed"`, `evidence_id`, `stage?` (failure only) | `testmd run` only: a replay's evidence pack published to the dashboard. Informational. |
| `test_md_bundle_sync` | `status: "ok"\|"failed"`, `commit_id`, `bytes?` (success) / `stage?` (failure) | `testmd run` / `testmd sync`: test bundle pushed to the cloud after an authored commit. Informational. |
| `testrun_*` family | see `references/testrun.md` | Emitted only by `kane-cli testrun run`; terminal event is `testrun_done`, not `run_end`. |

**Note:** The `run` stream has no `run_start` event; startup metadata or errors can precede progress.

### `error` with `code: "unresolved_variables"` (0.8.12+)

Emitted by `run`, `testmd run` and (after `testrun_plan`) `testrun run` when an authored step references a `{{name}}` that has no value. Nothing was dispatched; exit code `2`; stderr is silent.

```json
{"type":"error","code":"unresolved_variables","message":"2 variable(s) have no value — nothing was dispatched",
 "suggested_file":".testmuai/variables/variables.json",
 "variables":[
   {"name":"checkout_url","reason":"not_declared","used_by":[{"file":"objective","step":1}]},
   {"name":"login_password","reason":"value_missing","file":".testmuai/variables/assurance.json","used_by":[{"file":"login_test.md","step":2}]}
 ]}
```

| Field | Meaning |
|---|---|
| `variables[].reason` | `value_missing` — the key exists in `variables[].file` with an empty value · `not_declared` — the key is in no variable file |
| `variables[].file` | the pool file that holds the empty key (`value_missing` only); `--variables` when it came inline |
| `variables[].used_by[]` | `{file, step}` — `file` is `objective` for `kane-cli run`, else the test file (flattened step index) |
| `suggested_file` | where to add a `not_declared` key: `.testmuai/variables/assurance.json` inside an assurance store, `variables.json` otherwise |

Terminal: do not re-run the same command. Supply values (`--variables`, or fill the file) and run again.

**Note:** `ask_user` is auto-disabled when stdin is not a TTY. Since agents typically run kane-cli as a subprocess, ask_user events will not be emitted. Write objectives that don't require interactive input.

## Parsing Strategy for one-shot `run`

Since progress events lack a `type` field, distinguish them from typed events like this:

```
for each line of NDJSON:
  if obj.type === "run_end"    → terminal event, stop parsing
  if obj.type === "bifurcation" → flow split
  if obj.type exists           → other typed event
  if obj.step exists           → progress event (step/status/remark)
```

For one-shot `run`, build automation on `run_end` and process exit; other commands use the completion events listed below. Use progress events for live status display only.

**One-shot `run` completion event** (early refusals may exit without it):

```json
{
  "type": "run_end",
  "status": "passed",
  "summary": "Searched for laptop and added first result to cart",
  "one_liner": "Searched for laptop on Amazon and added to cart",
  "reason": "Objective completed",
  "duration": 45.2,
  "credits_consumed": 11.9,
  "final_state": {
    "price": "$29.99",
    "product_name": "Wireless Headphones"
  },
  "context": {
    "memory": {},
    "variables": {},
    "pointer": "(passed) Searched for laptop and added first result to cart"
  },
  "session_dir": "~/.testmuai/kaneai/sessions/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "run_dir": "~/.testmuai/kaneai/sessions/a1b2c3d4-e5f6-7890-abcd-ef1234567890/runs/0",
  "test_url": "https://test-manager.lambdatest.com/projects/123/test-cases/456"
}
```

Key `run_end` fields:
- `status` — `"passed"` or `"failed"`
- `summary` — what the agent did
- `one_liner` — short summary for display
- `reason` — why it stopped
- `credits_consumed`: credits the run used, a decimal number (when reported). Round it for display. Older releases and docs called this `credits`
- `final_state` — extracted values from "store as" objectives
- `test_url` — link to KaneAI dashboard (if upload succeeded)
- `session_dir` — session directory (session log + the sealed evidence pack under `evidence/`)
- `run_dir` — **legacy**: this directory is no longer created; run logs and screenshots live inside the evidence pack (`references/debug.md` has the layout)
- `result_code` (string, optional) — machine result classification. Under `--bug-detection`, a **confirmed product bug** arrives as `result_code: "740"` plus a `verdict` object (`confirmed`, `family`, `category`, `severity`, `one_liner`, `confidence`). Report it to the user as a product bug found, distinct from a test failure.

**The evidence hint is not an event.** After a run, kane-cli prints `` evidence: view locally with `kane-cli evidence serve <path>` `` on **stderr**. Never look for it on stdout; see `references/evidence.md` for how to act on it. `run_end` itself carries no evidence-pack field.

## Responding to `ask_user` (if stdin is a TTY)

```json
{"type": "user_response", "answer": "Medium size"}
```

To cancel a run:

```json
{"type": "cancel"}
```

## Command-specific completion

The `run_end` parsing strategy applies to one-shot `run` only. For `testmd run`, collect `test_md_done.overall_status`, `duration_s`, `session_id`, and optional `share_url`; embedded `run_end` events can finish individual steps. Local suites emit `testrun_done`; dispatched remote suites then emit `remote_done` (retain `status`, `exit`, `sessions_path`). `generate` emits `generate_done`. Assurance conversational agent streams end in `done`; review/read verbs have their own contracts. Always check process exit too: early refusal, invalid plan or dry-run can exit without the normal completion event.

Progress is for live display: count only `done`/`failed` completions, retaining child and execution context when step indices repeat.
