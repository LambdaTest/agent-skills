<!-- Read this when the user wants to save, persist, version-control, or re-run a browser test. Owns _test.md file format, replay/cascade rules, testmd subcommands, and parse errors. -->

# Saving & Replaying Tests with testmd

The §3 `run` command is the **primary** mode — one-shot, ephemeral. `testmd` is the **secondary** mode: tests live as `_test.md` files on disk, each step is cached on the first run, and every later run **replays from cache** with no LLM cost.

Use `testmd` whenever the user wants the test to persist. The decision is binary — once a test exists as a file, every later invocation is `testmd run`, never `run`.

> **Mobile test?** `target: emulator|simulator` in the frontmatter — with the app as its own root `app:` key — makes a `_test.md` drive a native app on an Android emulator or iOS simulator (macOS Apple Silicon); `chrome`/`cdp`/`ws` on the same key is the browser. Read `references/mobile.md`.

## When to switch from `run` to `testmd`

| User says | Use |
|---|---|
| "save this test", "commit this", "keep this", "add this to the suite" | `testmd` |
| "regression test", "smoke test", "make this replayable" | `testmd` |
| "this is a test", "test the X flow end-to-end" (suite-shaped) | `testmd` |
| "run this once", "check if X works right now", "try X" | `run` (§3) |
| "search for", "click", "fill", "verify" (one-shot) | `run` (§3) |

If unclear, ask: "Do you want me to save this test so you can re-run it later?"

## Quick start

Write the file (any path; filename must end in `_test.md`):

```markdown
---
mode: testing
max_steps: 30
---

# Amazon search

## Open Amazon
Open https://www.amazon.com.

## Search for headphones
Type "wireless headphones" into the search box and submit.
Verify at least one product result is visible.
```

Run it:

```bash
kane-cli testmd run amazon_test.md --agent
```

> Before the test launches, kane-cli validates the cached project/folder. If none is configured (or the cached one is stale/invalid), the run-startup gate auto-defaults a project/folder and emits a `project_folder_auto_defaulted` event on stdout. Surface it as a one-line note for the user and keep parsing — full handling lives in `references/test-manager.md`.

## File format

Four parts in order:

1. **YAML frontmatter** — between `--- ... ---` at the very top.
2. **`# Title`** — decorative; everything before the first `## ` is ignored.
3. **`## H2` step headings** — one per step. The agent reads the step body; the parser also interprets heading markers for replay-only steps, imports and structured control flow.
4. **Step body** — either prose **or** a single `@import <path>` line. Never both. Prose bodies are objectives with the same grammar as `kane-cli run` — for the full pattern catalog (action verbs, assertion analyze methods, checkpoint types, chaining, worked examples), Read `references/objectives-cookbook.md`.

Per-step `yaml` overrides go immediately under the heading, in a fenced block:

````markdown
## Submit the form
```yaml
timeout: 90
optional: true
```
Click submit and verify the confirmation banner.
````

**Frontmatter keys to use:**

| Key | Scope | Description |
|---|---|---|
| `mode` | root | `action` (halts on auth walls) or `testing` (default — pushes through so negative-test assertions can fire) |
| `url` | root | Start URL for the first step (bare domains get `https://`). Overridden by `--url`; falls back to config `default_url`. |
| `tags` | root | Labels for batch selection: YAML list, `[a, b]`, or bare `a, b`. Trimmed, lowercased, deduped. Selected with `testrun --tags` (`references/testrun.md`); shown by `testmd list`. Empty → parse error; per-step → parse error. |
| `max_steps` | root + step | Max agent reasoning steps. Engine fallback `30`; CLI default `50` (step config overrides). |
| `timeout` | root + step | Hard kill per step in seconds. |
| `headless` | root | No browser window. |
| `variables` | root + step | `{{name}}` params, same shape as §3, with `secret: true` for credentials. Counts as a value for the pre-run check (0.8.12+) — a `{{name}}` with no value anywhere refuses the run before it starts |
| `global_context` / `local_context` | root + step | Inline Markdown or path |
| `code_export` / `code_language` | root + step | Generate Playwright after the run; language `python` or `javascript` |

Files ending in `_test.md` are tests (valid entry points). Any other `.md` is a helper — reachable only via `@import`.

## The replay & cascade rule (CRITICAL)

On the **first** run of a test, the agent authors each step and saves a recording. On **every later run**, each step replays from its recording — no agent, no LLM cost, much faster.

An authorable step replays only if **all** of these hold (replay-only marked steps always require their recording):
- A recording for that step exists,
- Its prose is unchanged since the recording,
- Its `yaml` block is unchanged,
- No earlier step in the file invalidated it.

**Editing step N re-authors authorable steps from N onwards in that file. Replay-only marked steps still replay.** Each step starts where the previous step left off (URL, login, tabs). When step 3 changes, step 4 cannot safely replay against state that no longer exists.

Consequences when editing tests:
- A one-line tweak at the top of a 20-step test re-authors all authorable steps on the next run; replay-only steps keep their recordings.
- To re-record only one step, edit only that step (or steps after it).
- `--author` forces authorable steps to re-author; replay-only marked steps still require their recordings.
- Do not delete output recordings for replay-only marked steps; they cannot be recovered by re-authoring.

## `@import` for reusing flows

Extract a repeating flow (login, setup, cookie banner dismissal) into a helper file:

```markdown
## Sign in
@import ./helpers/login.md
```

Rules:
- Helper filename **must not** end in `_test.md`.
- Path resolves relative to the **importing file**, not the shell's cwd.
- The step body must be exactly `@import <path>` — no mixed prose, no extra lines.
- The step's `yaml` block may contain **only** `optional`. Other keys are rejected.
- `optional: true` on `@import` is allowed only at the root file, not on a nested import.

Variables and context propagate into helpers. Chrome / `mode` / auth do not (root-only).

Editing a helper re-authors that step in **every test that imports it**, plus everything after the import in those tests. Same cascade rule.

## Commands

| Command | Use |
|---|---|
| `kane-cli testmd run <path> --agent [flags]` | Run a test |
| `kane-cli testmd list` | List `*_test.md` files under cwd (NDJSON when non-TTY; records include `tags`) |
| `kane-cli testmd status <path>` | Test Manager identity + local-sync state |
| `kane-cli testmd export <path> [--language python\|javascript]` | Regenerate code export from existing recordings (no browser launch) |
| `kane-cli testmd delete <path>` | Local-only delete: removes source + `output-<stem>/`. Does NOT delete from Test Manager. |
| `kane-cli testmd sync <path>` | Re-push the test bundle (test + imports + outputs) to the cloud. Rarely needed — it happens automatically after every authored commit; use only to recover a failed auto-sync. |

**Running several tests at once?** Use `kane-cli testrun run` — one execution, one pack, isolated parallel Chromes. Read `references/testrun.md`.

**Flags on `testmd run` that don't exist on §3 `run`:**

| Flag | Default | Description |
|---|---|---|
| `--url <url>` | frontmatter `url:` / config `default_url` | Start URL for the first step. Overrides the `url:` frontmatter key and config `default_url`. |
| `--allow-missing-url` | off | Non-TTY only: start from the browser's current page instead of failing when the first step has no start URL. |
| `--name <name>` | none | Persist the run under this name. Regex `[a-zA-Z0-9_-]+`. |
| `--on-lock-conflict <readonly\|fail\|wait>` | none | Behavior when another user holds the test's edit lock. `readonly` = replay-only / no upload, `fail` = exit 2, `wait` = block until released |
| `--no-adaptive-heal` | healing enabled | Disable adaptive healing after replay failure |
| `--author` | off | Force authorable steps to re-author; replay-only steps still replay |
| `--bug-detection <off\|stop\|continue>` | config (`off`) | Flag suspected product bugs while **authoring** (`stop` halts on a confirmed bug; `continue` records it). Replay failures always investigate regardless. |

Common flags include `--agent`, `--headless`, `--max-steps`, `--timeout`, and `--variables`. Command-specific flags differ; check `kane-cli testmd run --help`.

Flag wins over frontmatter for everything **except** `variables` — the file owns variables; you can add new keys via flags but cannot override file-defined ones.

## Output: `output-<stem>/` and `Result.md`

After a run:

```text
amazon_test.md
output-amazon/
  Result.md                      # human-readable run report
  .internal/                     # cached recordings — do not edit
  playwright-python-code/        # only if code_export enabled
```

**`output-<stem>/` is commit-safe and should be committed to git.** That's how teammates and CI replay the same recordings.

For tests using `@import`, helper recordings land next to the helper file in `helper-output-<helper>-<root>-<step>/` directories. Also commit-safe.

**`Result.md`** opens in any Markdown viewer. It contains:
- Frontmatter — `status`, `started`, `duration_s`, `session_id`
- One entry per root step with one of `✓ passed`, `✗ failed`, `⏭ skipped`, optionally suffixed `(optional)` when a soft-failing step failed but the run continued
- For `@import` steps that failed, a path to the failing sub-step inside the helper

When the user asks "did the test pass?" or "where did it fail?" for a previously-run test, read `Result.md` rather than re-running the test.

**Evidence pack:** every `testmd run` also seals an evidence pack into `<cwd>/.testmuai/evidence/` (screenshots, per-step console/network logs, failure records) — the richer artifact for debugging a failure; see `references/evidence.md`. Packs are run artifacts: do NOT commit `.testmuai/evidence/`.

**Replays are self-sufficient:** a pure replay (all steps cached) needs no project/folder configuration — no picker, no auto-default event, no exit-2 setup dead end. It also publishes its pack to the test's own project automatically (`test_md_evidence_ingest` event, informational), and a failed replay is always investigated — the failure record lands in the pack.

## Recording a `_test.md` from a live session

If the user runs an ad-hoc objective with §3 `run` and decides to keep it:

```bash
kane-cli run "Search for noise-cancelling headphones on amazon.com" --name amazon-search
```

On exit, kane-cli writes `<cwd>/.testmuai/tests/amazon-search_test.md`. Move that file into the user's repo and re-run it with `testmd run`. Without `--name`, an ad-hoc `run` is ephemeral and nothing is written.

## CI invocation

```bash
kane-cli testmd run ./tests/checkout_test.md \
  --agent \
  --headless \
  --on-lock-conflict wait
```

- `--agent` — NDJSON to stdout (auto-enabled when stdin is not a TTY; pass explicitly anyway).
- `--headless` — no window.
- `--on-lock-conflict wait` — block instead of failing if a teammate is editing the same test.
- Adaptive healing recovers replay failures by default; `--no-adaptive-heal` opts out.

In non-TTY runs, interactive `ask_user` prompts are disabled — a step that would wait for input fails cleanly instead of hanging forever. Write CI test steps that don't depend on mid-run prompts. (Likewise, supply a start URL via the objective, `url:` frontmatter, or `--url`; a non-TTY run with no resolvable start URL fails unless you pass `--allow-missing-url`.)

Exit codes:

| Code | Meaning |
|------|---------|
| 0 | ✅ Passed |
| 1 | ❌ Failed |
| 2 | ⚠️ Error (auth, setup, infra) — for `testmd`, also includes parse errors and `--on-lock-conflict fail` |
| 3 | ⏱️ Timeout or cancelled — for `testmd`, also includes `--on-lock-conflict wait` timeout |

## Parse errors (when writing a `_test.md`)

Parse errors abort **before** any browser launch with exit `2`. Common ones and the fix:

| Message | Fix |
|---|---|
| `frontmatter is missing closing '---'` | Add the trailing `---` |
| `invalid YAML in frontmatter` | Re-validate the YAML block |
| `step body must be exactly one of prose / @import` | Split into two steps |
| `step config on @import may only contain 'optional'` | Remove other keys from the yaml block |
| `cannot @import a test file` | Imports may only reference helpers (not ending in `_test.md`) |
| `cyclic reference` | Restructure helpers to break the loop |
| `chrome config is global-only` | Move Chrome key to root frontmatter |
| `'<key>' is run-level and cannot be set per-step` | Move `mode` / `tags` / `on_lock_conflict` to root frontmatter |
| `tags must be a non-empty list of non-empty strings` | Give `tags:` at least one non-empty entry, or remove the key |
| `unknown config key` | Remove or fix the key |
| `auth/identity keys are CLI-only` | Pass `username` / `access_key` as CLI flags, not in frontmatter |

When the user reports a parse error, fix the file before retrying — don't loop on the same error.

## Replay policy and completion

Adaptive healing is enabled by default: after a replay failure the runner tries up to three shrinking replay windows, then full re-authoring of authorable steps. `--no-adaptive-heal` disables this recovery. Retired `--retry` and `--retry-count` are accepted only to print a notice; they do not enable healing or change the fixed budget.

Headings marked `@db`, `@api`, `@js`, `@smartui`, `@network_query`, or `@network_assertion` are replay-only. They still replay under `--author`, downstream divergence and adaptive healing. Missing recordings cannot be re-authored through these markers: restore the recording or recreate it through the originating workflow. Do not delete their tapes to force authoring; adding a marker does not create an operation.

Structured control flow uses balanced heading markers: `@if`, `@elif`, `@else`, `@end-if`, `@while`, `@end-while`. An `@else` must be last in its conditional; end markers must match the opened block type. These are distinct from natural-language conditionals. Markers are excluded from the step body hash. Only one replay-only kind is allowed per step, and an import cannot also be marked replay-only.

Under `--agent`, wait for `test_md_done` (file-level `overall_status`, `duration_s`, `session_id`, optional `share_url`) and process exit. Individual `run_end` events do not complete the file.

### The saved-test stream (what `testmd run --agent` prints)

This stream is **not** the one-shot `run` stream. Every line is typed, and the file-level events wrap a small inner stream per step. Read it for the result card (`references/cards.md` §7). Never show these names to the person.

| Event | Key fields | Use |
|---|---|---|
| `stream_start` *(0.8.17+)* | `cli_version`, `surface: "testmd"` | First line (`references/parsing.md`) |
| `test_md_step_start` | `step_index` (1-based), `heading`, `ref` | A `## ` step began. `heading` is its title |
| inner step events | `bifurcation`, `run_start`, `step_start {index}`, `step_event {index, event, detail}`, `step_end {index, status, summary, kind}`, `describe_trigger`, `run_end` | What happened inside the step. A `step_event` with `event: "replay_started"` means the step is replaying its recording. A `bifurcation` instead means it is being authored. The inner `run_end` closes the step, not the file |
| `test_md_step_end` | `step_index`, `status`, `duration_s`, `failed_sub_step_index` | The step finished. `status` is `passed`, `failed` or `skipped` |
| `test_md_evidence_ingest`, `test_md_bundle_sync` | `status` | Informational, before the summary |
| `test_md_summary` | `overall_status`, `duration_s`, `steps: {total, passed, failed, skipped, replay_decisions, author_decisions}` | The numbers for the card. `replay_decisions` is how many steps replayed, `author_decisions` how many were authored |
| `test_md_done` | `overall_status`, `duration_s`, `session_id`, `share_url?` | Completion. Always the last line. `share_url` is absent on a pure replay |

Most lines are inner `step_event`s (screenshots, reasoning, actions). Skip them unless you are diagnosing a failure: for the card you need only the step starts and ends, the summary and the completion event. On a failure, the failing step is the `test_md_step_end` with `status: "failed"`, its title comes from the matching `test_md_step_start`, and the last inner `step_end` or `step_event` before it says what went wrong.
