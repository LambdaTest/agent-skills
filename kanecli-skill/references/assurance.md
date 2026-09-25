<!-- kane-cli skill reference: assurance (requirements → designed suite → coverage → upkeep). Read when the user has a requirements document and wants tests designed from it, coverage accounting, or suite upkeep. Requires kane-cli 0.6.1+; features marked with a release (0.7.1+ … 0.8.14+) need at least that release. -->

# Assurance — Agent Surface

When the user has **requirements** — a PRD, a spec, acceptance notes — and wants tests designed from them, wants to know what's covered, or wants the suite kept current, use the **assurance commands** (`kane-cli context`, `design`, `cover`, `maintain`). Do not hand-write the tests, and do not reach for `generate`:

- `kane-cli generate` = quick scenarios/cases from a one-line description. No requirement linkage.
- **Assurance** = tests derived from the actual documents, every claim cited, every test permanently tagged with the acceptance criteria it verifies, coverage measured against requirements. Use it whenever the user cares about "what exactly is covered, and how do we know?"

Everything here works over a local store (`.context/` in the project directory) that the commands create and manage themselves.

**Version gate — check before improvising.** The assurance commands exist on kane-cli **0.6.1 and later**; flags and events marked with a release (**0.7.1+** … **0.8.14+**) below need at least that release. On an older CLI, `kane-cli context …` fails as an *unknown command* (exit 2 with a "did you mean" suggestion) — that error means the CLI is too old, not that you typed it wrong. Confirm with `kane-cli --version`, tell the user to update (`npm install -g @testmuai/kane-cli`, or `brew upgrade kane-cli`), and stop — do not try to reproduce the workflow with other commands.

## 1. The journey — follow in order, stop at the checkpoints

```bash
kane-cli context ingest ./prd.md --mode agent                # 1. snapshot AND extract (0.7.1+ one flow; may pause — §2)
kane-cli context review --verdicts <file> --json             # 2. CHECKPOINT: user approves use-cases
kane-cli design tests --use-case <uc-ref> --mode agent --max 8   # 3. design ACs, scenarios, tests
kane-cli context review --verdicts <file> --json             # 4. CHECKPOINT: user approves the design
kane-cli testmd run .testmuai/tests/<t>_test.md --agent      # 5. author each kept test once (real browser)
kane-cli testrun run --match 't-'                            # 6. batch replays from then on
kane-cli cover gaps                                          # 7. designed % × proven % + per-use-case debt
kane-cli maintain reconcile --from <new.md> --source-id <id> --mode agent   # when a source changes (§11)
```

On 0.7.1+, `context ingest --mode agent` lands the files and runs the extraction in one flow (one `ingested` event per landing, then the extract stream). Run `kane-cli context extract --mode agent` separately for re-runs, `--source <id>` pins, and resumes; on pre-0.7.1 releases run it after every ingest.

Two hard rules:

1. **The two checkpoints are the user's, not yours.** Everything the extract and design agents emit is *derived* (unreviewed) until a human decision promotes it — see §4. Do not start authoring (step 5) until the user has approved the design output or explicitly told you to proceed.
2. **One step at a time, one store-writer at a time.** Never run two store-mutating commands concurrently (`ingest`, `extract`, `review` with verdicts, `design`, `reconcile`) — the store is single-writer (§8), and extraction additionally holds a store-wide lock (a concurrent extract refuses `EXTRACT_LOCKED`, exit 2 — wait, never delete locks).

Extract, design, and reconcile call the KaneAI service and consume credits; everything else is local and free.

## 2. The pause loop — exit 3 is a pause, NOT a failure

**Scope: this rule applies to `context extract`/`context ingest`, `design tests`, and `maintain reconcile` (§11).** (For `run`/`testmd`/`testrun`/`generate`, exit 3 still means timeout/cancelled.)

These commands take **`--mode agent`** — not `--agent`; they reject that flag, and a bare non-TTY invocation exits `2` asking for an explicit mode. In `--mode agent`, **every question pauses the run** (0.8.8+ — earlier CLIs auto-answered low/medium-risk questions with their recommended defaults and paused only on high risk):

- The run exits `3`, emits `session_paused` with the session id, the questions in full (text, options, the recommended one, risk, rationale), and the verbatim resume command.
- **Never drop a pause** (same rule as generate clarifications). Answer it: if your own context clearly resolves the question, answer it yourself; otherwise surface the question — with its options and recommendation — to your user and get their answer.
- **0.7.1+ sessions are durable from the first turn**: a crash that left a checkpoint exits `3` with a `session_paused` carrying `crashed: true` (no `pending_questions`) and the resume command — exit 3 always means "resumable". A crash before anything durable was saved still exits `1`; check `context sessions --json` before retrying anything paid.

Three ways to resume:

```bash
# plain words — the agent maps your statement to its own questions:
kane-cli context extract --resume <sid> --mode agent --message "Account required — the update section supersedes the older text"

# by id (0.7.1+) — for precise scripted answers; each echoes a panel_resolved event:
kane-cli context extract --resume <sid> --mode agent --answer q1=1 --answer q2="https://staging.example.com"

# land a new source instead of answering (0.7.1+) — the batch defers (ask_deferred), the agent
# reads the source and re-asks only what's still open:
kane-cli context extract --resume <sid> --mode agent --with-source ./addendum.md
```

- If the answer leaves any question standing, the run pauses again with refreshed questions — repeat.
- Sessions live 24 hours. Inspect without contending a live run: `kane-cli context sessions --json` (all resumable sessions + their resume commands) and `kane-cli context sessions show <sid> --json` (the pending questions in wire shape). A session written by a NEWER kane-cli than the installed one lists as unknown with no resume command (0.7.1+) — that means "upgrade to resume it", not corruption. If you abandon a session deliberately, remove it with `kane-cli context sessions clean <sid>` — bare `clean` only collects *expired* sessions, and `--all` is a purge that needs explicit user authorization.

Full event schema: `references/assurance-parsing.md`.

## 3. Ingest and extract — propose use-cases

```bash
kane-cli context ingest <files-or-urls...> --mode agent   # lands + extracts (0.7.1+); --mode ci lands ONLY (exit 0)
kane-cli context extract --mode agent                     # re-run entry: sweeps every pending source
```

Accepted sources (each with a size cap; oversized = `FILE_TOO_LARGE`, wrong type = `UNSUPPORTED_MEDIA`):

- text `.txt`/`.md`/`.markdown` and structured text `.json`/`.yaml`/`.yml`/`.toml`/`.xml`/`.log` (≤2MB, must be UTF-8);
- images `png`/`jpeg`/`webp` (≤5MB);
- **PDF** (≤25MB; 0.6.7+) — needs a text layer: scanned docs refuse `PDF_NO_TEXT_LAYER`, password-protected `PDF_ENCRYPTED`;
- **DOCX** (≤25MB; 0.6.10+) — password-protected/legacy `.doc` refuse `DOCX_ENCRYPTED_OR_LEGACY`; save-as-`.docx` is the remedy;
- **Jira issue URLs** (0.6.11+) — `kane-cli context ingest https://<site>/browse/PROJ-123`. Prerequisite: Jira connected in the user's LambdaTest Integrations screen (the refusal says so if not). 0.7.2+ ingests **all comments** (author, timestamp, body — citable; a failed comments read refuses the whole ingest); pre-0.7.2 comments were not ingested. Re-runs are `unchanged`/`versioned` like files — and an issue last ingested pre-0.7.2 versions ONCE on its next re-ingest: report that as the upgrade catching up, not a content change;
- **Confluence page URLs** (0.7.2+) — `kane-cli context ingest https://<site>/wiki/spaces/<KEY>/pages/<id>/…` (the full URL — short-links refuse). Same Atlassian connection as Jira, but it must have Confluence access; a Jira-only connection refuses with reconnect guidance. Default id `page-<id>`; a body change versions the source, a no-op edit or bare version bump does not;
- **Linear issue URLs** (0.8.6+) — `kane-cli context ingest https://linear.app/<workspace>/issue/KEY-123` (slug/query/#comment variants converge). Prerequisite: a Linear connection (the refusal points at the Integrations screen). Comments incl. threaded replies are identity-bearing — a failed or partial comments read refuses the whole ingest; a recycled key (same key, different issue) refuses with retire/`--as` recovery; default id = the lowercased key (`eng-42`);
- **Linear document URLs** (0.8.6+) — `…/document/<slug>` (the slug must end in the document's 12-hex id; the connection needs document access — resync hint otherwise). Default id `doc-<id>`. Workspace pages (project/team/view) refuse — ingest their issues or documents individually;
- **Web page URLs** (0.8.3+) — any public http(s) URL that is not a Jira/Confluence/Linear URL; fetched server-side (the CLI never fetches pages). Default id = a URL slug + short hash; `--as` adopts a custom id, and re-pointing an adopted id at a DIFFERENT URL asks on a TTY / refuses headless. Inaccessible pages (not found, login/paywall, bot-blocked, non-HTML, too large, timeout) and private/internal addresses refuse in plain language.

Remote ids share ONE space (0.8.6+): a URL whose id is already backed by a different kind of source refuses with retire/`--as` recovery — report it as an id collision; never retry blindly.

**Landing-phase failures.** 0.7.2+ is strictly NDJSON in `--mode agent`: a bad path, an unsupported or oversized file, a refused URL, or a misused `--mode`/`--as` arrives ON the stream as `error` (codes `MODE_USAGE`, `AS_SINGLE_SOURCE`, `UNSUPPORTED_URL`, `INGEST_FAILED`) + `done`, and nothing ever precedes the stream. On 0.7.1 the same failures end with a prose error line and exit `1`/`2` BEFORE any NDJSON begins — no `done` event. Either way it is a refusal (fix the input and re-run; sources already landed stay safe — the run says so), never a crash.

Re-ingesting changed bytes under the same id **versions** the source and marks everything derived from the old snapshot stale — but for a changed document, prefer `maintain reconcile` (§11), which does the version move AND triages the fallout.

Extract behavior to expect (0.7.1+): the sweep **continues past a per-source failure** (one line each; exit 1 at the end if anything failed — the failed source simply retries next run, no `--force` needed). `--trust hold` holds everything new for the user's review instead of committing (headless-only; `--mode ci` refuses the flag entirely; use it one source at a time — resuming held work from a multi-source run is not yet supported). The agent cites every claim (fabrication is rejected before write), asks when the source contradicts itself, and commits proposals as `derived`. Watch the `commit` event and say it in plain language ("5 use-cases extracted from the PRD").

## 4. Review — trust is the user's decision

Promotion from `derived` to `trusted` **always requires explicit user confirmation** — even when the user asked for an "end-to-end" run. End-to-end authorizes completing the workflow, not making product-requirement judgements.

**Present the material, not the counts.** The `commit` event carries counts and ids only — to run a checkpoint, enumerate what's waiting with `kane-cli context list --json --inferred` (one JSON row per unreviewed node) and pull any item's full content, citations, and history with `kane-cli context explain <ref> --json`. Present titles, descriptions, and the cited evidence; collect the user's decisions; build the verdicts from those same refs. The same recipe runs the design checkpoint. Then land the decisions atomically:

```bash
kane-cli context review --verdicts verdicts.json --json
kane-cli context review --approve uc-a uc-b       # 0.7.1+: structured flags for single decisions
kane-cli context review --skip uc-c               # skip/defer leave NO fact — the item stays queued
```

`verdicts.json` is an array of `{"ref": "<slug-or-cid>", "resolution": "..."}` where resolution is exactly `approved | edited | rejected | skipped | supersede` (optional `reason`, `edit`, `supersede_target`). One unresolvable ref fails the whole file (exit `2`, nothing lands). The structured flags (`--approve`/`--skip`/`--defer`) are mutually exclusive with `--verdicts`.

**Archives need consent (0.7.1+).** A `--verdicts` rejection no longer destroys anything — it lands as a non-destructive `pending_archive` fact (exit 0, loud summary). Actually archiving requires `--allow-archive --because "<reason>"`, and `--mode ci` refuses archives under any flag. Never pass `--allow-archive` without the user's explicit instruction and their reason.

Auto-approving is allowed **only** when the user explicitly says so ("approve the recommended items without asking me") — and even then, enumerate everything you promoted in your summary and still surface warnings and conflicts.

## 5. Design — from a trusted use-case to runnable tests

```bash
kane-cli design tests --use-case <uc-ref> --mode agent --max 8
```

- **Always pass `--max`** (start at 8; narrow for a smoke slice, widen only when the requirement breadth or the user justifies it). It caps **scenario+test pairs — deliverable size, NOT credits**. There is no spend cap: track the `usage` events' `total_credits` and report the total. If consumption looks runaway or a turn errors, stop and report — never auto-retry a paid turn.
- Omitting `--max` makes the agent estimate a size and ask — which in agent mode is a pause.
- **Gates return commands, not dead ends (0.7.1+).** Designing against an *unreviewed* use-case exits 2 with the runnable review command in the event's `next` (bypass only on explicit user instruction: `--allow-unreviewed`). An *already-designed* use-case exits 2 with the `--force` redesign and evolve alternatives in `next`. Offer the `next` commands to the user; never auto-run a `--force`.
- There is **no `--because` flag on `design tests`** — interactively the session collects the redesign reason itself; headless `--force` proceeds with an auto-stamped reason.
- `--phase <grounding|acs|scenarios|wiring|tests>` (0.7.1+) re-enters a design at a phase, re-seeded from the committed earlier phases; missing predecessors exit 2 with the commands to run first in `next`.
- Output: acceptance criteria, scenarios, exactly one test per scenario — written as runnable files under `.testmuai/tests/*_test.md`, each assert step tagged with the criteria it verifies. Plus **gaps** (recorded, ranked missing pieces) and **warnings** (e.g. a test claiming more criteria than its check asserts). Citations are verified against the pinned source text before commit (0.7.1+) — a `CITE_UNVERIFIED` error means a citation could not be verified even after repair.
- **Variables (0.8.12+).** Design reads every `*.json` in the user's variable directories (names + has-value only, never values) and reuses a name that exists before inventing one. Each name it invents is declared: an empty stub lands in `.testmuai/variables/assurance.json`, never a value, never over an existing key. The stream tells you which: `variables_declared` at the commit that wrote them, `variables_summary` at the end (schema in `references/assurance-parsing.md`). **Surface these as a to-do** — "2 variables need values: login_email, login_password — in .testmuai/variables/assurance.json" — because a designed test refuses to author until they are filled (SKILL.md §3, Unresolved variables). Fill them yourself only if the user gave you the values.
- **Present tests, gaps, warnings, AND variables needing values** — first-class output, not noise. Then go to the review checkpoint (§4) before any authoring.
- `kane-cli design explain <t-ref>` replays *why* a test exists (technique, boundary values, criteria) with zero AI cost — use it when the user asks "why this test?".

## 6. The authoring bridge — from designed files to batch runs

A freshly designed test has never been executed. On 0.8.4+ hand the set straight to `kane-cli testrun run`: unauthored members classify as `author`, the run authors them in a real browser, and afterwards the authored and replayed evidence consolidates into one published execution — best-effort: when consolidation cannot complete, evidence stays split rather than lost. `--from-context` (0.8.4+) selects members by assurance test ids and follows edit supersessions. Designed tests may carry `{{variables}}` for values the requirements never pinned (a store URL, a product name) — supply them per `references/testmd.md`. `kane-cli testmd run <file> --agent` remains the single-test authoring path, and on pre-0.8.4 CLIs it is REQUIRED first — `testrun` there refuses never-authored members (`missing_meta`). Evidence packs seal per `references/evidence.md`.

### 6.1 A designed test is the design — do not edit it by hand

Every designed `_test.md` carries an `assurance:` block in its frontmatter: `id: t-<slug>` and a `base:` pin naming the design version the file came from. The graph follows edits through that pin (0.8.4+): an edit made on top of the current design version is adopted at the file's next `testmd run` / `testrun run` as the next version of that test — no review checkpoint, no warning — and from then on the edit IS the design; coverage, gaps and reconcile build on it. An edit made on top of an older version is kept out of the graph, and the run reports a sync warning naming the test.

So a failing authored run is never, by itself, a reason to rewrite the step. Classify the failure first (the pack's `failure.yaml` and the network capture it references — `references/debug.md`), then route it:

| The run failed because… | Do | Never |
|---|---|---|
| the app misbehaved (wrong status, missing header, wrong data) | keep the test as it is; report the finding with the evidence | edit the step until it passes |
| the requirement changed | `kane-cli maintain reconcile --from <new source> --source-id <id> --mode agent` (§11) | patch the step text to match the new requirement |
| the step wording sends the agent the wrong way (ambiguous target, no end state) | redesign through the CLI so the new wording is minted as a design version: offer the user `kane-cli design tests --use-case <uc-ref> --force` (never auto-run a `--force`; interactively the session collects the reason, headless it is auto-stamped) or `kane-cli maintain evolve … --because "<reason>"` in a terminal — `cover gaps <uc-id>` names the remedy in its `next` block | rewrite the sentence in place |
| the platform cannot perform what the step asks for (a hash of a downloaded file, a request that must carry the browser's login — `references/objectives-cookbook.md` §3.2 and §3.5) | tell the user and stop; different wording will not make the capability appear | paste the triage's `suggested_fix.summary` into the step |

**If you still judge a hand edit necessary**, do all of the following, in order:

1. **Read `references/objectives-cookbook.md` in full before writing a word.** The edited step must be something kane-cli can actually run: an intent action with literal data, then an observable end state (§1); assertions phrased as checkpoints (§3); a direct API call only where §3.5 applies.
2. Change only the step body. Leave the `assurance:` block, the `# title`, the `>` blockquote under it, and every `## Step …` heading with its `@verifies` tags (e.g. `## Step 4 — assert @verifies ac-…`) exactly as they are — the pin and the tags tie the test to its requirement.
3. Describe the user action and the observable outcome, never the mechanism: "open the invoice from the order page, then verify the request to `/api/orders/42/invoice` returned 200 with `content-disposition: attachment`", not "use DevTools to intercept the response and issue a GET".
4. Tell the user, before running, that the edit becomes the next design version of that test on the run, and what changed.
5. Re-author with `kane-cli testmd run <file> --agent` and read the result against the ACs the step `@verifies`.

## 7. What's next — let the tool tell you

```bash
kane-cli cover                    # the pack audit: what it proved, plus the live-graph completeness worklist
kane-cli cover gaps               # the coverage ribbon: one row per use-case, both axes
kane-cli cover gaps <uc-id>       # 0.8.2+: the dossier — every AC of that use-case + next actions
kane-cli cover gaps --json        # the nested document (designed axis, proven axis, per-UC pending rows with ready_command)
kane-cli cover gaps --mode agent  # 0.7.1+: same data as ONE `gaps` event + done.next[] ready-commands
```

On 0.8.2+ the default `cover gaps` output is the **coverage ribbon** — a high-level band-table: one severity-ordered row per use-case with designed/proven bars and per-class debt counts, deliberately carrying NO commands. To act, drill in: `cover gaps <uc-id>` (the dossier) renders every AC of that use-case plus a `next` actions block — evidence first; surface its warning that re-running an authored test on a broken app may heal the test around the failure — or read `--json`, whose per-UC pending rows keep `ready_command`. `--rollup lenient|strict` selects the proven-axis formula. BREAKING at 0.8.2: `--flat` and gaps' `--from` are REMOVED and refuse (pre-0.8.2 CLIs still have the flat worklist). With a `<uc-id>`, `--json` and agent mode close the document over that use-case.

## 8. Store rules — don't corrupt the user's graph

- `.context/` is **append-only and single-writer**. Never run two store-mutating commands concurrently (extract, review verdicts, design, ingest, reconcile, retire/revert/rebuild). On a lock error (`EXTRACT_LOCKED`, or reconcile's walk lock), another run is live: report it and wait — never delete lock files; a dead run's lock clears itself.
- Never hand-edit anything under `.context/`, and never `git merge` it — two histories merge cleanly in git and brick the store on the next read. Keep it gitignored — kane-cli 0.8.14 adds `.context/` to the folder's `.gitignore` itself when it creates the store inside a git repository — `gitignore_updated` on the stream, or a `warning{message}` when the line could not be written (relay it and add the line yourself); `KANE_CONTEXT_GITIGNORE=0` keeps it out. To share it with a team, use a **location** (a GitHub repository, an S3-compatible bucket, or a folder) through `kane-cli context sync`, `kane-cli context push`, `kane-cli context pull` and `kane-cli context clone` (0.8.14+) — a Git repository used as a location is not the same as committing `.context/`. While a sync rebase is open the store refuses every other write with `SYNC_REBASE_PENDING` (the fence) — finish it or `kane-cli context sync doctor --abort`, never delete files. Rules, events and decisions: `references/context-sync.md`.
- Safe inspection any time: `kane-cli context list --json` (nodes with trust + freshness), `kane-cli context explain <ref>` (a node's full recorded history, no AI), `kane-cli context fsck` (integrity check), `kane-cli context view --no-open --out <path>` (writes a self-contained HTML graph snapshot to that path — never opens a browser, never touches the graph).
- Destructive verbs (`context retire`, `revert`, `rebuild`, `name --backfill`) exist and take `--yes` headless — run them **only on an explicit user request**, never autonomously.

## 9. When things fail

| Signal | Meaning | Do |
|---|---|---|
| `context`/`design`/`cover` is an *unknown command* (exit 2) | the CLI predates 0.6.1 | `kane-cli --version` to confirm; have the user update; stop |
| an assurance flag from this reference is *unknown* (exit 2) | the installed CLI predates the version that flag is marked with here (0.7.1 for most; 0.8.14 for the sync flags), or the flag is misspelled or on the wrong command | check the full command, then `kane-cli --version` against the feature's stated minimum; have the user update; stop |
| `error` code `NO_STORE` | no `.context/` here | `context ingest` the sources first (confirm the cwd is the project root) |
| `SOURCE_MISSING` / `BLOB_MISSING` | store references a missing source | re-ingest the source file |
| `STALE_BASIS` | the graph moved under the session | re-run the extract — it re-grounds |
| `HIGH_RISK_CI` | a `--mode ci` run hit a judgement call | re-run with `--mode agent` and handle the pause |
| `EXTRACT_LOCKED` (exit 2) | another extraction is live on this store | wait for it; never break locks |
| `TRUST_USAGE` / `TRUST_UNDER_CI` | `--trust` used where it can't apply (interactive hold / any ci) | drop the flag, or run headless `agent` mode |
| `HOLD_MULTI_SOURCE` (exit 2) | a `--resume --with-source` landing was refused — the resume carries `--trust hold`, or the session already holds items for review | finish the held review first; run hold one source at a time |
| `UC_UNREVIEWED` (exit 2) | design target is unreviewed | run the review command from `next`; `--allow-unreviewed` only on explicit user instruction |
| `UNKNOWN_PHASE` / `PHASE_ORDER` (exit 2) | bad `--phase` entry | run the predecessor commands named in `next` |
| `CITE_UNVERIFIED` | a citation failed verification even after repair | report it; the item did not commit with bad provenance |
| `INGEST_UNAUTHORIZED_REF` | a source ref not provided by the user tried to land | only user-provided paths/URLs can land — ask the user for the source |
| `WRONG_VERB` (exit 2) | resuming a session with the wrong command family | use the resume command from `sessions --json` verbatim |
| `STRUCTURED_FLAGS_USAGE` / `STRUCTURED_TARGET_UNKNOWN` (exit 2) | a misused `--answer`/structured verdict, or an unknown question/item id | fix the `<id>=<value>` form, or use an id from the refusal's list (it names the addressable ids) |
| `PAIR_MISMATCH` / `BINDING_MISMATCH` (exit 2) | the installed release pair is broken, or the session belongs to another release | reinstall/upgrade kane-cli; a session from before an upgrade either resumes under its original release or restarts fresh (committed work is kept) |
| message ends `[SOURCE_HELD]` (exit 2, 0.7.2+) | a reconcile head-move refused — a live session holds review items pinned to that source | finish that review first (the refusal names the session: `context extract --resume <sid>`), then re-run |
| message ends `[SESSIONS_UNREADABLE]` (exit 2, 0.7.2+) | a session file can't be read, so the hold check fails **closed** | `context sessions --json` to list, `context sessions clean <sid>` for the broken one, then re-run |
| message ends `[HELD_REVIEW]` (exit 2, 0.7.2+) | a headless `--apply` met a live held review that needs a human | have the user run `kane-cli maintain reconcile --apply` in a terminal — it resumes the cards agent-free |
| "this version of kane-cli is no longer supported" (runtime failure, exit 1) | the service requires a newer CLI | have the user upgrade, then retry |
| media refusals (`PDF_*`, `DOCX_*`, `ENCODING_UNSUPPORTED`, `UNSUPPORTED_MEDIA`, `FILE_TOO_LARGE`) | the source file can't be ingested as-is | relay the message — each names its remedy (save-as, split, re-encode) |
| a remote URL refuses because its id is backed by a different kind of source (0.8.6+) | cross-provider id collision — remote ids share one space | retire the existing source, or adopt the new one with `--as`; never retry blindly |
| lock held | another assurance run is live | wait for it; never break locks |
| `sync_error` code `SYNC_REBASE_PENDING` (exit 2, 0.8.14+) | a sync rebase is open on this store — the fence refuses every other write | the user finishes it (`kane-cli context sync`, answering decisions) or closes it (`kane-cli context sync doctor --abort`); never delete files — `references/context-sync.md` §7 |
| `sync_error` code `SYNC_BEHIND` / `SYNC_DIVERGED` (exit 3, 0.8.14+) | the location has records this store has not pulled / both sides added work — a pull or a rebase is needed, not a failure | relay the `remedy` verbatim (`kane-cli context pull <name>`, or `--rebase` on the user's go-ahead) — `references/context-sync.md` §6 |
| `sync_behind` event on an extract/design/reconcile stream (0.8.14+) | advisory: the location has moved past this store | one line ("origin has records you have not pulled"); the run continues |
| `sync_error` code `SYNC_STORE_BUSY` (exit 2, 0.8.14+) | a sync verb met a live session or lock on this store | wait; `kane-cli context sync doctor` when it names an interrupted rebase |
| `error` + `done` with exit `1` | runtime failure (incl. a sweep where some sources failed) | report the message; **do not blindly re-run a paid command** |
| auth/credit failure mid-run | token or balance problem | keep the `sid`, have the user fix auth/balance (`kane-cli whoami`, `kane-cli balance`), then resume |
| stream ends with no `done` event | the process crashed — outcome unknown (the one designed exception: `kane-cli context review --mode agent` keeps its `--json` shape and ends its listings without `done`; read its exit code) | check `context sessions --json` and `context list` before any retry, to avoid duplicate paid work |
| exit `130` | force-interrupted | extract/design: resumable only if a `session_paused` event was actually received. Sync verbs: the rebase state is on disk — `kane-cli context sync doctor`, then `kane-cli context sync` resumes it |

## 10. Narration

Same philosophy as SKILL.md §1 — translate, don't transcribe:

- Surface: pause questions (the deliverable when paused), commits ("5 use-cases extracted, 3 promoted to trusted"), held items ("4 items are held for your review"), designed tests + gaps + warnings, the credit total, and each checkpoint decision you're asking the user for.
- Fold: `agent_activity` lines (thinking/tool noise) into at most one progress remark.
- (0.8.2+) In a terminal, every session ends with a **session summary** block — state, facts, the resume command, credits on pause/crash/held. Narrate from it; don't re-derive.
- Never show event/field names, cids, or raw NDJSON to the user.

## 11. When requirements change — reconcile

A changed requirements document is **one command**, not a re-ingest:

```bash
kane-cli maintain reconcile --from ./prd-v2.md --source-id prd --mode agent
```

Never `context ingest` the new version first — reconcile does its own re-ingest, records the version move, and triages the fallout into rows: ADD (new use-case → design it), MODIFY (content moved → update or re-design), ARCHIVE (evidence decayed — **never applied headless**, always waits for the user's interactive session). It emits its own event family (`reconcile_plan` → `reconcile_row_start`/`reconcile_row_end` per row → `reconcile_paused`? → `reconcile_summary` → `done`; see `references/assurance-parsing.md`). Modes: `agent` auto-applies the safe ADD/MODIFY tier and exits 3 with the stored plan when ARCHIVE rows need a human; `ci` fail-closes (plan stored, exit 2); `--plan` is a safe staged preview. Re-running the same command is idempotent — it resumes a pending plan rather than re-billing.

0.7.2+ additions:

- **Interactive is an in-chat review.** In a terminal, every proposed change holds behind a review card: **approve** commits it (an ADD offers a design run, a MODIFY mints a successor version, an ARCHIVE retires non-destructively), **reject** drops it with zero residue (it may be re-proposed on a later reconcile), **defer** mints ONE durable gap that appears in `cover gaps` with the reconcile command as its remedy, and typing steers a re-finalize of the remaining changes. Verdicts persist as they land — Ctrl+C loses nothing, and bare `--apply` resumes a held review as cards **agent-free** (no model, no network); a headless run that meets a held review refuses with a `[HELD_REVIEW]` message marker. While a deferred change is on the record, the store **fails integrity checks and refuses commits on older kane-cli versions** — machines sharing a store upgrade together.
- **`--from` takes URLs.** The same remote URLs ingest takes (§3): Jira/Confluence (0.7.2+), web pages (0.8.3+), Linear issues and documents (0.8.6+). `--source-id` is then optional — the URL carries its own id, and a contradicting `--source-id` refuses. Kind continuity holds both ways: a URL can't version a file-backed source and a file can't version a remote one — each refusal names the correct `--from`. A source ingested under a custom id (`--as`) is maintained by re-running that ingest with the same `--as`. The first reconcile of a Jira issue last ingested pre-0.7.2 may report the one-time upgrade re-version (§3) — not a content edit.
- **One stream.** The re-extract child's events ride the reconcile stream itself, stamped `verb: "reconcile"` — parse per `references/assurance-parsing.md`.

For staleness that arrived outside a reconcile, `kane-cli maintain evolve` re-designs a use-case — it is interactive-only (the blast-radius confirmation is the point); suggest the user run it in a terminal rather than scripting around it.

## Sharing a context store

For location setup, sync, pull, push, clone and rebase recovery, see [Sharing the context store](context-sync.md).

## Lifecycle automation contracts

`context name`, `context retire`, and `context revert` accept `--mode agent` and emit an envelope ending in `done`. Destructive agent-mode operations require `--yes` even when stdin is a TTY. Other modes retain human output. Read commands use their documented `--json` flags; do not assume they all accept `--mode`.

`context review --mode agent` / `--json` returns review outcome rows on success rather than the conversational `done` contract. Early agent-mode errors may emit `error` plus `done`; check command-specific output and process exit.
