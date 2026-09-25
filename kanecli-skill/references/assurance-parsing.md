<!-- kane-cli skill reference: NDJSON wire contract for the assurance conversational commands (context ingest/extract / design tests / maintain reconcile / cover with --mode agent). Internal parsing reference — never show these names to the user. -->

# Assurance NDJSON — Wire Contract

`kane-cli context extract --mode agent`, `kane-cli context ingest … --mode agent`, and `kane-cli design tests --mode agent` speak a versioned NDJSON vocabulary on stdout — one JSON object per line, envelope `{"type": "<name>", "v": 1, "verb": "extract"|"design", ...}`. On 0.7.2+ the stream is **strict**: stdout carries only NDJSON and stderr stays silent (crash traces excepted); on 0.7.1, prose diagnostics could ride stderr. `maintain reconcile --mode agent` (verb `reconcile`) and `cover`/`cover gaps --mode agent` (verbs `cover`/`gaps`) share the envelope with their own event sets (below).

**The vocabulary is open**: new event types and fields may appear in any release — tolerate unknowns, never fail on them.

**Prefix handling:** on 0.7.2+ there is NO stdout impurity — nothing precedes the stream (the landing receipts ARE the `ingested` events) and every line parses as JSON. On 0.7.1, a merged `context ingest … --mode agent` run prints its landing receipts — a few prose lines per file — BEFORE the NDJSON begins. Skip non-JSON prefix lines and start parsing at the first line that begins with `{` — correct on both releases, a harmless no-op on 0.7.2+.

## Terminal detection — the `done` guarantee

Except for `kane-cli context review --mode agent` (below), every `--mode agent` invocation ends its stream with exactly one `{"type":"done","status":…,"exit_code":…}` — including refusals. Build all post-run logic on it, exactly like `run_end` for browser runs:

```text
for each line:
  if obj.type === "done"           → terminal: status ∈ complete|paused|error|refused|interrupted|aborted; stop
  else if obj.type === "session_paused" → capture sid + resume + pending_questions (the pause deliverable)
  else                             → per-type handling below
```

A stream that ends **without** `done` means the process crashed — outcome unknown; inspect `context sessions --json` and `context list` before retrying anything paid. One designed exception: `kane-cli context review --mode agent` keeps its `--json` shape — verdict and drift listings are one JSON object per line with no `done` (an empty listing prints nothing, exit `0`); its early refusals — no store, an open rebase, a verdict queue that needs a terminal (`TTY_REQUIRED`) — are typed events followed by `done`; its later refusals exit without `done`. Read its exit code instead. One version-scoped rule for merged-ingest landing failures (bad path, unsupported media, refused URL, a misused `--mode` or `--as`): on 0.7.2+ they ride the stream as `error` (codes `MODE_USAGE`, `AS_SINGLE_SOURCE`, `UNSUPPORTED_URL`, `INGEST_FAILED`) + `done` — the guarantee covers the whole invocation; on 0.7.1 they end with prose + exit `1`/`2` **before any NDJSON begins** — no stream at all is a refusal to fix, not a crash, and the guarantee starts with the extraction stream.

## Events (extract / design)

| type | payload highlights | handle |
|---|---|---|
| `ingested` *(0.7.1+)* | per source landed by a merged ingest run: `source_id`, `status` (`created`/`unchanged`/`versioned`), `cid`; arrives before the extraction's events | fold into one landing line |
| `run_start` | `mode`, `trace` (per-run log path); design adds `use_case`; *(0.7.2+)* `session` — a support id, present when telemetry is on | note the trace path for debugging |
| `corpus` | extract: `sources[]` this run covers + already-extracted `skipped[]` | fold into one line |
| `source_start` / `source_skipped` | `source_id`, `index`/`total`, `resumed` / `reason` | progress |
| `plan` | the `--plan` transcription payload | present as the preview |
| `assumed_default` | a question auto-answered with its recommended default: `id`, `selected_index`, `risk` — 0.8.8+ agent mode never emits it (every question pauses instead); seen only on older CLIs' streams | mention that defaults were assumed (they are flagged in the commit) |
| `agent_activity` | `kind` (`tool`/`decision`/`progress`/`thinking_done`) + display `label` | noise — fold; **never script against labels** |
| `agent_message` *(0.7.2+)* | the agent's narrative `text` — the lead-in before a question batch, the closing statement | the story around the structured events; quote or fold, never script against it |
| `warning` *(0.7.2+)* | actionable non-fatal condition: `message`, plus `code` when there is one (`ZERO_USE_CASES`, `SAVE_FAILED`); a `.gitignore` that could not be written or a lifecycle note carries `message` alone | surface it — non-fatal but user-relevant, with or without a `code` |
| `lock_steal` *(0.7.2+)* | a stale run lock was taken over: `key`, `stale_owner`, `by`, `ts` | observability only — fold or ignore |
| `usage` | per agent turn: `credits`, running `total_credits` (*(0.7.2+)* rounded to two decimals) | track; report the final total |
| `validate_failed` | kane-side validation failed: `codes[]`, `repairing` | the agent self-repairs; only surface if the run then errors |
| `degraded` *(0.7.1+)* | duplicate detection running in a reduced mode (`reason`) — new items will be HELD, not committed | tell the user their items will be held for review |
| `held` / `update_held` *(0.7.1+)* | items held for the user's review instead of committed: `source_id` + `count` + `reason` / `count` + `targets[]` | surface the count and that review happens at resume/`context review` |
| `commit` | what landed: counts + `minted[]` (`cid` + `logical_id`); extract adds `proposal_id` | translate ("5 use-cases extracted"); `logical_id` slugs are how you reference nodes later |
| `receipt` | per-phase commit receipt (design; extract also emits one at its commits): `commit_n`, `phase`, `committed[]`, `reused`, `rejected[]`, `warnings[]`, `next`, and (design only) `parity` | surface non-empty `rejected[]` and `warnings[]` in plain language; meaningful reuse is worth one line |
| `variables_declared` *(0.8.12+)* | design: stubs written by a phase commit — `file` (pool file) + `variables[]` (`name`, `description`, `secret`); only names that existed in no variable file | surface as a to-do ("N variables need values — in <file>") |
| `variables_summary` *(0.8.12+)* | design, end of run: every declared name still needing a value — same shape | repeat the to-do in the closing summary; fills gate authoring |
| `message_sent` | `--message` delivered: `sid`, `chars` | confirmation only |
| `panel_resolved` *(0.7.1+)* | a `--answer` flag landed on a pending question: `id`, `by`, `via` | confirmation only |
| `ask_deferred` *(0.7.1+)* | `--with-source` set the pending batch aside: `source_id`, `cid`, `questions` (count) | tell the user the questions were deferred while the agent reads the new source |
| `session_paused` | `sid`, verbatim `resume` command, `expires_at` (24 h), **`pending_questions[]`** | THE pause deliverable — see below |
| `session_complete` | `sid` | the session finished cleanly |
| `gate_refused` | a design gate refused the run (may be the first event); may carry `next[]` | surface the reason + offer the `next` commands |
| `phase_entry_override` *(0.7.1+)* | a design `--phase` entry applied: `phase`, `missing[]` | note the entry point |
| `error` | `message` + stable `code` when one exists — the 0.6.x set (`NO_STORE`, `PREFLIGHT`, `SOURCE_MISSING`, `BLOB_MISSING`, `HIGH_RISK_CI`, `STALE_BASIS`) plus the 0.7.1+ set (`EXTRACT_LOCKED`, `TRUST_USAGE`, `TRUST_UNDER_CI`, `HOLD_MULTI_SOURCE`, `UC_UNREVIEWED`, `UNKNOWN_PHASE`, `PHASE_ORDER`, `CITE_UNVERIFIED`, `WRONG_VERB`, `INGEST_UNAUTHORIZED_REF`, `STRUCTURED_FLAGS_USAGE`/`STRUCTURED_TARGET_UNKNOWN`, `PAIR_MISMATCH`/`BINDING_MISMATCH`, media families `PDF_*`/`DOCX_*`) plus the 0.7.2+ landing codes above. Three 0.7.2+ reconcile refusals carry NO `code` — instead a bracketed marker ends the `message`: `[SOURCE_HELD]`, `[SESSIONS_UNREADABLE]`, `[HELD_REVIEW]`; match on the marker. Many runtime failures are message-only — never require a code | map per `references/assurance.md` §9 |
| `done` | **always last**: `status` + `exit_code`; may carry `next[]` | terminal |

**`next[]`** on pauses, refusals, and `done` lists ready-to-run follow-up commands. Usual shape: objects `{cmd, why, title}`; a few refusal sites emit plain strings — handle both. Offer them to the user; never auto-run a mutating `next` command.

## `session_paused` — the shapes the pause loop parses

The full pause (questions pending):

```json
{"type":"session_paused","v":1,"verb":"extract","sid":"ext-…",
 "resume":"kane-cli context extract --resume ext-… --mode agent",
 "expires_at":"…",
 "pending_questions":[{
   "id":"q1","text":"…the question…","risk":"high",
   "rationale":"…why it matters, with the conflicting evidence…",
   "options":[{"label":"…","detail":"…"},{"label":"…","detail":"…","input":true}],
   "recommended_index":0,"allow_free_text":true}]}
```

Two sibling shapes *(0.7.1+)*, distinguished by their fields — branch on presence:

- `crashed: true` and **no** `pending_questions` — a crash-paused session; the `resume` command re-enters the conversation, nothing to answer up front.
- `held` (a count) — only `sid`, `resume`, and `held` are present (no `expires_at`); the session holds items awaiting the user's review; resume presents them.

Use `text` + `options[].label` + `recommended_index` + `rationale` to decide or to present the question. An option carrying `input: true` *(0.7.1+)* needs a typed value with the pick — answer it via `--answer <id>="<value>"` or plain-words `--message`. The `resume` field is the exact command to run — append `--message "<plain words>"`, `--answer <id>=<v>` pairs, or `--with-source <ref>`.

## Reconcile events (verb `reconcile`)

*(0.7.2+)* the stream opens with a minimal `run_start` (`session` only — no `trace`) and the re-extract child rides the SAME stream: extract-vocabulary events (`source_start`, `agent_activity`, `plan`, `commit`, …) interleave between the `reconcile_*` events, all stamped `verb: "reconcile"` — dispatch on `type`, never on position. The reconcile family: `reconcile_plan` `{source_id, plan_path, rows[], archive[]}` → per row `reconcile_row_start` `{kind, ref, stale?, direct?}` + `reconcile_row_end` `{kind, ref, outcome: applied|failed|skipped|plan-only|paused, exit_code?, detail?}` → `reconcile_paused` `{plan_path, pending[]}` when ARCHIVE rows remain (exit 3; a human resumes with `--apply <plan_path>` in a terminal) → `reconcile_summary` `{applied, skipped, deferred, plan_only, failed, paused, stale_created}` on every path → `done` always last. Validation refusals ride the stream as `error` + `done` (exit 2), never stderr alone.

## Sync events (verb `sync`) *(0.8.14+)*

`kane-cli context sync`, `kane-cli context push`, `kane-cli context pull` and `kane-cli context clone` under `--mode agent` (and `kane-cli context sync add`, `kane-cli context sync list`, `kane-cli context sync remove`, `kane-cli context sync status`, `kane-cli context sync doctor`) share the envelope with `verb: "sync"` and their own `sync_*` family — `sync_probe_started`/`sync_probe`, `sync_status`, `sync_pull_done`/`sync_push_done`, `sync_rebase_started`/`sync_rebase_decision`/`sync_rebase_done`/`sync_rebase_open`, `sync_error{code, detail, remedy}` — then `done`. Two of them cross into the assurance streams: `sync_behind` (an advisory on `extract`/`design`/`reconcile` streams: the location has records this store has not pulled — one line, not a failure) and `sync_error` code `SYNC_REBASE_PENDING` (the fence: a sync rebase is open, so the write verb refused; `verb` carries that verb's own name). Schema, refusal codes and the `--answer` loop: `references/context-sync.md`.

## Coverage events (verbs `cover` / `gaps`) *(0.7.1+)*

One payload event carrying the full `--json` document — `coverage` for `cover`, `gaps` for `cover gaps`; with a `<uc-id>` (0.8.2+) the `gaps` document closes over that use-case — then `done` (with the worklist's ready-commands in `next[]`). Refusal = `error` + `done{refused, 2}`.

## Exit codes (these commands only)

| Code | Meaning |
|---|---|
| `0` | complete |
| `1` | runtime failure — incl. an extract sweep where some sources failed (each got one line; they retry next run). Report, don't blindly retry (turns already consumed credits) |
| `2` | usage/auth/refusal — bad flags, no store, bare non-TTY without `--mode`, gates (unreviewed target, phase order, trust misuse, lock held, release-pair mismatch); earlier writes may already have landed: `kane-cli context ingest` keeps landed sources when the extraction then refuses, and `kane-cli context sync` (0.8.14+) keeps its completed pull when the push refuses (`SYNC_READ_ONLY`) — read the events before the `error` or `sync_error` |
| `3` | **paused and resumable** — not a failure; run the pause loop. Includes crash-pauses (0.7.1+). On the sync verbs (0.8.14+) `done{status: "paused"}` means decisions are waiting: after a rebase walk the rebase is open (answer with `--answer`); after `kane-cli context sync doctor --abort` it is closed and the unanswered decisions stayed in the backup — the `sync_rebase_done` before it says which (`status` `paused` or `aborted`); `paused` with no `sync_rebase_done` means doctor set aside a rebase whose saved state it could not read — `sync_doctor.detail` says the next `kane-cli context sync` reapplies the saved backup. `done{status: "refused", exit_code: 3}` means a pull or a rebase is needed first — `references/context-sync.md` §4 |
| `130` | force-interrupted — for extract and design, resumable only if a `session_paused` event arrived; on the sync verbs the rebase state is on disk: `kane-cli context sync doctor --mode agent` shows it, `kane-cli context sync --mode agent` resumes it |

Reminder: this exit-3 meaning is **specific to these assurance commands**. `run` / `testmd` / `testrun` / `generate` keep their own meanings (3 = timeout/cancelled).
