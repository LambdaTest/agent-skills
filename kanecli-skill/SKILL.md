---
name: kanecli-skill
description: Browser automation + AI test authoring via kane-cli - run browser objectives, generate & refine test scenarios/cases from a description, design requirement-linked test suites from a PRD/spec (assurance), parse NDJSON output, inspect logs, save runnable _test.md. Use for any task requiring a real browser (navigate, click, fill forms, test web UI, take screenshots), or to author test cases, quick cases from a description via kane-cli generate; a designed, coverage-accounted suite from requirement documents via the assurance commands. Never write test cases by hand. Also runs mobile app tests - native Android app on a virtual emulator or iOS app on a simulator via --target emulator|simulator (desktop browser stays the default target): locally on macOS Apple Silicon, or on the LambdaTest cloud grid from any machine via kane-cli testrun run --remote. Also shares the assurance store (.context/) with a team through a location (a GitHub repository, an S3-compatible bucket, or a folder) via kane-cli context sync, and resolves the decisions a sync rebase asks.
---

# Kane CLI — Browser Automation Skill

Use `kane-cli` for **any task that requires a real browser**: navigating websites, clicking elements, filling forms, searching, testing web UI, taking screenshots, or verifying deployments. Do NOT use Playwright, Puppeteer, or Selenium directly. Use `--agent` for `run`, `testmd run`, and `generate`. `testrun run` has no `--agent`: it emits NDJSON when **stdin** is not a TTY (use `< /dev/null` for terminal automation). Assurance conversational commands use `--mode agent`.

**Authoring test cases or scenarios?** Never write them by hand — kane-cli has two authoring pipelines, and the routing matters:

- The user describes what to test in a sentence or two, or wants quick scenario/case ideas → `kane-cli generate` (§6).
- The user has **requirement documents** (a PRD, a spec, acceptance notes) and wants a designed suite, requirement-linked coverage, or "what exactly is covered?" answers → the **assurance** commands — Read `references/assurance.md` first.

Don't draft test cases in chat or scratch files: both pipelines produce structured, refinable, runnable `_test.md` output.

---

## 1. Every session: ready check, launch, result card. READ THIS FIRST

A one-line "Test passed" instead of the result card is a bug. A run that starts with no ready check is a bug too. This section is first so you don't miss it. Follow it exactly.

The order never changes: **ready check → launch line → the run → result card**. On a person's first session two things are added: a short tour sent with the launch line, and three choices asked after the first result. Nothing is asked before the first result.

### 1.1 Start with the ready check

Before the first kane-cli command of a session, run the preflight script that ships with this skill and show the ready card. It is one short command and takes about two seconds:

```bash
sh "<skill dir>/scripts/preflight.sh"
```

`<skill dir>` is the folder that holds this `SKILL.md`. **Read `references/ready-check.md`** for the card (a full table on the first session, one line afterwards), the problems that stop a run, and the sign-in flow. Two rules matter enough to repeat here: you start sign-in yourself with `kane-cli login --oauth`, and you **never ask for an access key or password in chat**.

If the preflight shows no saved preferences (its `## agent-config` section is `none`, or has no `onboarding.completed_at`), this is the person's first session: **Read `references/first-run.md`** before you launch.

### 1.2 How to launch kane-cli

**All platforms use your shell tool** (`Bash`) to launch kane-cli. Do NOT use `Monitor`: it creates excessive noise.

**Tag every command with your runtime.** Put `KANE_CLI_USER_AGENT=<your-runtime>` in front of every `kane-cli` command you run. Pick a short, stable identifier for the AI assistant or IDE running this skill (e.g. `claude-code`, `codex`, `gemini`, `cursor`, `kiro`, `aider`) and use the same value for the whole session. Do it inline on each command: an `export` does not survive from one shell call to the next in most agent hosts. Do not show the prefix in commands you quote to the person.

```bash
KANE_CLI_USER_AGENT=<your-runtime> kane-cli run "<objective>" --agent <other-flags>
```

On Windows PowerShell: `$env:KANE_CLI_USER_AGENT='<your-runtime>'; kane-cli run "<objective>" --agent <other-flags>`.

**Watch mode.** Use the person's saved preference (`references/agent-config.md`). With none saved, show the browser unless the preflight says there is no display, an SSH session, or CI: then add `--headless`.

**Keeping runs.** When the person's saved purpose is `suite` or `ask`, add `--name <short-slug>` to every one-off `run`. A named run is recorded as a `_test.md` while it runs, so keeping it afterwards costs nothing, and a run launched without a name cannot be kept without running again. With `one-off`, leave the flag out. Details: `references/first-run.md` §4.

Bash blocks until kane-cli exits, then hands you the complete stdout. Parse it, summarize what happened, and present the result card. Wait for process completion on `testmd run` and `generate` too, but parse their own completion events: `test_md_done` and `generate_done`, respectively. An intermediate `run_end` does not finish a saved test.

Set a generous timeout (up to 600000ms) since browser runs can take a while.

### 1.3 Before you launch

In one message, **before** invoking Bash, send the ready card and then:

```text
Starting browser task: <one-line restatement of the user's objective>.
```

That line tells the user something is in progress. No todos needed: Bash returns all output at once and you summarize it below. On a first session, the tour from `references/first-run.md` goes in this same message, right after the launch line, so the person reads it while the run works.

### 1.4 After the run: summarize what happened

Once Bash returns, parse the captured NDJSON stdout and present a **concise summary** of what happened. Not every event deserves a line. Surface what matters and skip the noise. (Skip the summary entirely when the person's preference is `results-only`.)

Progress events have `step`/`status`/`remark` fields and **no `type` field**.

#### What to surface

| Show | Which events | How |
|------|-------------|-----|
| **Failures** | Any step with `status: "failed"` | `Step <n> failed: <remark>` |
| **Flow changes** | `bifurcation`, `child_agent_start`, `child_agent_end` | Plain-language one-liner (e.g. "The agent split the objective into 2 sub-tasks") |
| **Errors** | `error` typed events | `Error: <message>`. The exception is `code: "unresolved_variables"`, which is a pre-run refusal, not a failure: see §3 **Unresolved variables** |
| **Overall progress** | All passing steps | One summary line: `<total> steps completed: <2–4 key actions from remarks>` |

#### What to skip

- Individual passing steps: fold them into the overall progress line
- Internal field names (`step`, `status`, `remark`, `run_end`, `final_state`, `bifurcation`, `session_dir`, `stream_start`, `project_folder_auto_defaulted`, etc.): translate to plain language. A `project_folder_auto_defaulted` event fires before progress when the run-startup gate auto-resolves a project/folder; surface it as one line ("kane-cli auto-selected project X / folder Y for this run") and move on. Details: `references/test-manager.md`.

For short runs (≤ 3 steps), you may list each step individually since there's nothing to fold.

### 1.5 The result card

The terminal event has `type: "run_end"` and stable fields: `status`, `summary`, `one_liner`, `duration`, `credits_consumed`, `final_state`, `test_url`, `session_dir`, `run_dir`.

**For a passing run, always emit this exact table** (substituting the field values):

```markdown
| | |
|-------|-------|
| 🟢 **Result** | Passed |
| 🎯 **Task** | <one_liner> |
| ⏱️ **Duration** | <duration, as 1m 54s> |
| 👣 **Steps taken** | <count of completed progress events (done/failed), retaining child/execution context> |
| 💳 **Credits** | <credits_consumed, rounded> used · about <ready check balance minus used> left |
| 📝 **What happened** | <summary> |
| 📁 **Evidence** | Want to open the run evidence in your browser? |
| 🔗 **Test case** | [Open in Test Manager](<test_url>) |
| ➡️ **Next** | <two things you can do right now, e.g. add a payment step · run it headless in CI> |
```

**If `final_state` has values** (the user used "store as X", see §4), append a second table:

```markdown
| 📦 What was found | Value |
|-------------|----------------|
| <key from final_state, humanized> | <value> |
```

**If the objective used assertions** ("assert …", "verify …"), append a pass/fail table per assertion derived from the run summary and step remarks.

Every other result has its own card in **`references/cards.md`**: a run that didn't start, one that stopped early, a possible product bug, a saved test, and a suite (local or cloud grid). Read it before presenting any of those. The rules there apply to every card: one short sentence per cell, failures first, `➡️ Next` is an offer you can act on, and secret-looking values never go in chat.

### 1.6 On failure

For exit code 1 (or `status: "failed"` in `run_end`), present the failure card. Never show raw paths or NDJSON.

```markdown
| | |
|-------|-------|
| 🔴 **Result** | Failed at step <n> of <total> |
| 🎯 **Task** | <one_liner, or the objective in a few words> |
| ⏱️ **Duration** | <duration, as 1m 12s> |
| 💳 **Credits** | <credits_consumed, rounded> used |
| 📝 **What happened** | <plain-language description of the failing step's remark> |
| 🔍 **Likely cause** | <your diagnosis: missing element, slow page, ambiguous objective, auth wall, etc.> |
| 📁 **Evidence** | Want to open the run evidence in your browser? |
| ➡️ **Next** | <a retry you can run now> · <walk through the failing step> |
```

The failing step's screenshot lives inside the run's evidence pack (the stderr hint names the pack path): extract it with `unzip <pack> "tests/*/steps/*/screenshot.png" -d <tmpdir>`, Read it, and show it **under** the card. For the pack layout and deeper diagnosis, see `references/debug.md`.

Exit code 2 means nothing ran: that is a `🟡 Didn't start` card, not a failure (`references/cards.md` §4).

### 1.7 After the first result: three choices, then save

On a first session only, right after the first result card, save the defaults this run used, then ask the three choices from `references/first-run.md` §4 (watch mode, where results go, one-off or saved suite) as the **last thing in your turn**, and save the answers when they arrive. Some hosts hand control back before the person answers: end your turn there and save on their reply. On every later session none of this is asked again.

**The live status strip (Claude Code only) has its own once-only question.** Onboarding is shared by every agent the person uses, but the strip exists only in Claude Code, so the person may have finished their first session in another agent without ever being asked. In Claude Code, in **any** session: if the preflight's `## agent-config` has no `strip.claude-code.offered_at`, kane-cli is 0.8.17 or newer, and `node=` is not empty, ask the strip question once, after that session's first result card, as the last thing in your turn. On a first session it simply rides along as the fourth choice. It is recommended, never turned on without a yes, and you record `offered_at` either way so it is never asked twice. **Read `references/live-strip.md` §3** for the wording.

---

## 2. Decision tree

When the user's request involves a browser — or writing test cases:

**Is kane-cli installed, signed in and ready?**
- Unknown → run the preflight and show the ready card (§1.1, `references/ready-check.md`)
- A problem that stops the run → offer the fix from the card; deeper setup lives in `references/setup-and-config.md`
- Ready ↓

**What does the user want?**
- A single one-shot browser task → build a `kane-cli run --agent` command (§3 + §4)
- A test they want to save / re-run / commit → Read `references/testmd.md` first, then use `kane-cli testmd`
- Run a suite of saved tests (several `_test.md` at once) → Read `references/testrun.md` first, then use `kane-cli testrun run`
- Need test cases or scenarios from a short description — because the user asked, or because the task needs them (no browser) → **don't hand-write them**; Read `references/generate.md` first, then use `kane-cli generate` (§6)
- Has requirement documents (PRD/spec) and wants a designed suite, coverage accounting, or suite upkeep → Read `references/assurance.md` first — the assurance commands (`context`/`design`/`cover`/`maintain reconcile`, kane-cli 0.6.1+; several features need newer releases, up to 0.8.14+ — the reference marks each), NOT `generate`
- A **designed** test (its `_test.md` carries an `assurance:` block) failed a run → Read `references/assurance.md` §6.1 **before touching the file** — an edit is adopted as the next design version on the next run; classify the failure first (app bug → report it; requirement changed → reconcile; wording → redesign through the CLI; capability missing → stop), and edit a step of an existing designed test by hand only after reading `references/objectives-cookbook.md`
- Share the context store with a team, join a teammate's, keep two stores level, or resolve a sync conflict → Read `references/context-sync.md` first — `kane-cli context sync`, `kane-cli context push`, `kane-cli context pull` and `kane-cli context clone` (kane-cli 0.8.14+); the store is shared through a location, never by copying or git-merging `.context/`
- Multiple independent browser tasks → Read `references/parallel.md` first
- View, share, or validate run evidence (`.evidence` packs) → Read `references/evidence.md`
- Debug a failed run → Read `references/debug.md`
- Configure kane-cli or check directory layout → Read `references/setup-and-config.md`
- Browse / create / pick a Test Manager project or folder, or interpret the auto-default event → Read `references/test-manager.md`
- The person wants results saved somewhere else ("change project") → Read `references/test-manager.md` §6. The change is global, and the question must say so
- The person wants to change how runs behave ("kane preferences": watch or quiet, one-off or suite) → Read `references/agent-config.md`
- The person asks what kane-cli can do, or for the tour again ("kane tour") → show the tour from `references/first-run.md` §2
- The person wants to watch runs live, or asks about the status line → Read `references/live-strip.md` (Claude Code only)
- You need the full NDJSON event schema (rare — §5's summary covers 90% of cases) → Read `references/parsing.md`
- Compare / evaluate / justify kane-cli against another tool or approach (cost, tokens, effort, ROI) → Read `references/fair-evaluation.md` first — comparisons are only honest like-for-like across the test lifecycle
- **Mobile**: drive a native app on a virtual Android emulator or iOS simulator instead of the browser → Read `references/mobile.md` first. Desktop (the browser) stays the **default** target; mobile is opt-in via `--target emulator|simulator` and always drives an app you provide (`--app <build|APPid>`), never a URL. **Local** mobile runs (`run`, `testmd run`, `testrun run`) need macOS Apple Silicon. **From any other machine** (Linux, Windows, Intel Mac, a Mac without Xcode/Android Studio), run saved mobile `_test.md` files on the cloud grid with `kane-cli testrun run <paths> --remote --device-name "<grid device>" --os-version <v>` — the grid boots the emulator/simulator on a HyperExecute macOS host (the account needs a HyperExecute plan with macOS runners). Never tell a non-Mac user mobile is impossible: point them at `--remote`.

**Every run, always:** follow §1 above.

---

## 3. Building a `run` command

```bash
kane-cli run "<objective>" --agent [options]
```

> The `run` subcommand is **mandatory**. `kane-cli "<objective>"` (no `run`) does **not** work — unknown first tokens exit `2` with a "did you mean" suggestion. Same rule applies to `kane-cli testmd run …` and `kane-cli generate …`.

`--agent` is mandatory — it switches stdout to NDJSON. Most-used flags:

| Flag | Purpose | Default |
|------|---------|---------|
| `--headless` | No visible browser window | Off |
| `--max-steps <n>` | Cap agent reasoning steps | 30 |
| `--timeout <s>` | Hard kill after N seconds | No limit |
| `--url <url>` | Start URL for the run (overrides config `default_url`; bare domains get `https://`) | Config `default_url` |
| `--variables <json>` | Inline variables JSON (for `{{key}}` in objective) | None |
| `--variables-file <path>` | Load variables from a JSON file | None |
| `--ws-endpoint <url>` | Remote browser (LambdaTest grid) | Local Chrome |
| `--code-export` | Generate code export after upload | config (`true` by default) |
| `--bug-detection <mode>` | Flag suspected product bugs while authoring: `off`/`stop`/`continue` (`stop` halts on a confirmed bug; `continue` records and keeps going) | config value (`off`) |

Other flags (`--global-context`, `--local-context`, `--cdp-endpoint`, `--allow-missing-url`) and the full variables precedence chain live in `references/setup-and-config.md`.

**Start URL:** every run needs a start URL for the first navigation. Provide it the simplest way — start the objective with the site ("Go to https://… and …") — or pass `--url <url>`; a configured `default_url` is the fallback (`kane-cli config set-url`). There is no silent default site: if none of these supply one, a non-TTY run **fails** rather than guessing (pass `--allow-missing-url` to start from the current page instead).

**Exit codes:** `0` passed · `1` failed · `2` auth/infra error · `3` timeout/cancelled.

**Unresolved variables (0.8.12+):** every `{{name}}` in the objective must have a value before the run starts. If one does not, the run **refuses before anything launches** — exit `2`, and with `--agent` a single `{"type":"error","code":"unresolved_variables", ...}` event carrying `variables[]` (`name`, `reason`: `value_missing` = the key exists in `file` with no value · `not_declared` = the key is in no file, add it to `suggested_file`; `used_by[]`). **This is terminal — do not retry the same command.** Either ask the user for the values, or write them yourself (`--variables '{"name":{"value":"…"}}'`, or `{"name":{"value":""}}` stubs into `suggested_file` for the user to fill), then run again. There is no bypass flag. Never checked: `{{smart.*}}`/`{{environment.*}}`/`{{secrets.*}}`/`{{totp.*}}`, and names an earlier step stores (`store … as 'x'`). Numbers in a variable file count as values (loaded as strings); booleans do not.

### Examples

```bash
# One-shot
kane-cli run "Go to https://www.amazon.in and search for 'laptop'" --agent

# Headless with timeout
kane-cli run "Go to https://app.example.com and verify login page loads" --agent --headless --timeout 60

# With inline credentials
kane-cli run "Go to https://app.example.com and login with {{username}} and {{password}}" --agent \
  --variables '{"username":{"value":"alice"},"password":{"value":"s3cret","secret":true}}'
```

---

## 4. Writing objectives

How you phrase the objective string determines what the agent does. Four patterns:

> For the full catalog — every action verb, every assertion analyze method (Visual / Textual-DOM / URL / Title / DevTools→Network/Console/Performance/Cookies/localStorage/Clipboard), direct API calls, operators, chaining, conditional/negative patterns, and worked examples — Read `references/objectives-cookbook.md`. Same grammar applies to one-shot `kane-cli run` objectives and `_test.md` step bodies.

| Pattern | Trigger words | Behavior |
|---|---|---|
| 🎯 **Action** | "go to", "click", "type", "search", "fill" | Performs browser actions |
| ✅ **Assertion** | "assert", "verify", "confirm", "check that" | Pass/fail check on a condition |
| 📦 **Extraction** | "store X as 'name'" | Persists a value into `run_end.final_state` |
| 🔌 **API call** | "call", "POST/GET a URL", a pasted `curl` | The agent makes the HTTP request itself; "save the response as X", then assert on it in plain English: "assert the response status is 200", "store the id from the response body as 'order_id'" |

### Two rules that make an objective replayable

1. **End every flow in a terminal assertion.** Close with a check of the resulting page state (`verify the cart shows 1 item`), not a bare `submit` or `confirm the dialog`. A run only earns a replayable pass/fail from a verify/assert — a pure-action objective (`add a laptop to the cart`) gets none. If the objective has several phases, each ends in its own check. Phrase the closing check as what is on screen once the last action completes, so it verifies with no further click or navigation; if the evidence is elsewhere, make getting there an explicit action (`place the order, open Order History, then verify the newest order shows "Processing"`), never `verify the order succeeded by checking Order History`. Two traps: `confirm the dialog` is an action, not a check; and `verify the Submit button is visible` fails exactly when the action worked (the control disappears on success) — assert the outcome, not the trigger.
2. **Intent for the actions, literal for the data.** Phrase actions as goals (`Log in with {{user}}`) so the run absorbs layout drift; keep exact values literal or in `{{variables}}`. An expected-optional branch (a sometimes-there cookie banner) goes in an `if/else`, not assumed away.

**Shape:** an intent action carrying literal data, then a verify of an observable end state — `Search for "{{query}}" and open the first result, then verify the title contains "{{query}}"`. Full grammar in `references/objectives-cookbook.md §1`.

### The "store as" rule (critical for extraction)

Vague phrasing like "read", "tell me", "report" does NOT reliably extract data — the agent may see the value but won't capture it. Use "store as".

❌ `"go to example.com and read the page title"`
✅ `"go to example.com, store the page title as 'page_title'"`

Stored values appear in `run_end.final_state` and become the second results table per §1.4. Refer back to a stored value in plain English (`the stored price value`), never as `{{price}}`; `{{name}}` is for global variables and secrets only.

### Calling APIs directly

The agent can make API calls itself — not just observe the page's traffic. Phrase an explicit call and name the response:

```text
"Call POST https://api.example.com/login with body {...}, save the response as login,
 assert the response status is 200"
```

Use the response in plain English: `the response status`, `store the id from the response body as 'order_id'`, and later `the stored order_id value`. Never `{{login.status}}`: `{{name}}` is reserved for global variables and secrets. A pasted `curl` works too. Full grammar in `references/objectives-cookbook.md` §3.5.

### Chaining

Action → extraction → assertion in one objective:

```text
"go to {{app_url}}/dashboard,
 store the welcome message as 'welcome_text',
 assert the user role in the sidebar is 'Admin'"
```

### Dos and don'ts

| ✅ Do | ❌ Don't |
|---|---|
| Imperative verbs: "go to", "click", "store as" | Vague verbs: "check out", "look at", "explore" |
| Specific: "click the 'Add to Cart' button" | Vague: "add the item" |
| Name extractions: "store X as 'price'" | Hope for values: "tell me the price" |
| `{{variables}}` for credentials/URLs | Hardcode secrets in the objective |
| Plain English for values the run produces: "the stored price value", "the response status" | `{{price}}` / `{{login.status}}` for a stored value or an API response |
| Always include starting URL | Assume the agent knows where to start |
| Split mega-objectives (>15 steps) into multiple runs | Cram everything into one |

---

## 5. Parsing one-shot `run --agent` output — essentials

> Internal reference only. Never expose these field names to the user — translate them per §1.

Stdout is NDJSON, one event per line. On kane-cli 0.8.17+ every line also carries `v` (contract version, `1`) and `ts` (when it was emitted), and the first line is `{"type":"stream_start","cli_version":…,"surface":"run"|"testmd"|"testrun"}`. Ignore fields and event types you do not know: new ones can appear in any release. There are two shapes:

- **Progress events** (most events) have `step` (1-based), `status` (`running` at start, `done`/`failed` at completion), `remark` — and **no `type` field**.
- **Typed events** have a `type` field: `project_folder_auto_defaulted` (run-startup gate, fires before any progress when no project/folder is configured), `bifurcation`, `child_agent_start`, `child_agent_end`, `ask_user`, `error` (an `error` with `code: "unresolved_variables"` is a pre-run refusal and the **only** line — no `run_end` follows; handle per §3), and finally `run_end`.

Parsing strategy:

```text
for each line:
  if obj.type === "run_end"  → terminal, stop parsing
  else if obj.type exists    → typed flow event (rare)
  else if obj.step exists    → progress event → summarize per §1.3
```

For one-shot `run`, build post-run logic on `run_end` and process exit. Saved tests and suites use their own completion events (see Command-specific completion below).

For full event schemas (`bifurcation` flow fields, `child_agent_*`, `ask_user` semantics, `cancel`/`user_response` outbound events, complete `run_end` field list), Read `references/parsing.md`.

`kane-cli generate` (§6) emits a **different** stream — every line is typed `generate_*` (no untyped progress lines), terminated by `generate_done`. Its schema is in `references/generate-parsing.md`.

The assurance conversational commands (`context ingest`/`context extract`, `design tests`, `maintain reconcile`, `cover`) do NOT take `--agent` — they take **`--mode agent`** and speak their own typed stream ending in `done` (open vocabulary — tolerate unknown event types; on 0.7.2+ the stream is strict — every stdout line parses, stderr silent — while on 0.7.1 a merged `context ingest` prints a few prose receipt lines BEFORE the stream — skip to the first `{` line, harmless on 0.7.2+ — and a landing-phase ingest failure ends with prose + exit 1/2 and no stream at all: a refusal, not a crash; on 0.7.2+ those failures ride the stream as `error` + `done`); **for those commands only, exit `3` means paused-and-resumable, not timeout** — schema in `references/assurance-parsing.md`, behavior in `references/assurance.md`. The context sync verbs (`kane-cli context sync`, `kane-cli context push`, `kane-cli context pull`, `kane-cli context clone`; kane-cli 0.8.14+) take `--mode agent` the same way and speak a `sync_*` family ending in `done`; there too exit `3` means a decision or a pull is needed, not a failure — `references/context-sync.md`. `kane-cli context sync setup` refuses without a terminal (`TTY_REQUIRED`): agents use `kane-cli context sync add` and `kane-cli context clone`.

`kane-cli testrun run` also emits its own typed stream (`testrun_plan` … terminal `testrun_done`) — schema in `references/testrun.md`. `kane-cli testmd run` may additionally emit `test_md_evidence_ingest` (replay evidence published) and `test_md_bundle_sync` (test bundle synced) — informational; describe in plain language, never surface raw names. The post-run evidence hint (`` evidence: view locally with `kane-cli evidence serve <path>` ``) is a **stderr** text line, not a stdout event — don't try to parse it from the NDJSON stream; see `references/evidence.md` for how to act on it.

---

## 6. Generate test cases (authoring — no browser)

`kane-cli generate` authors **Test Scenarios → Test Cases** from a plain-language description. It does **not** drive a browser. **Use it whenever a task needs quick test cases or scenarios from a description — don't hand-author them in chat or a file.** (Requirement documents + coverage accounting → assurance instead: `references/assurance.md`.) Reach for it to: turn a feature / requirement description into a test suite; expand or refine coverage (more edge cases, negative paths, a narrower focus); or save the Functional cases as runnable `_test.md` and hand them to `kane-cli testmd run`. Full details + event schema: **Read `references/generate.md`**.

Three explicit modes, each runs **one turn then exits**:

| Mode | Command |
|---|---|
| **New** | `kane-cli generate "<what to test>" --agent` |
| **Refine** | `kane-cli generate "<change>" --refine --req <id> --agent` |
| **Save** | `kane-cli generate --save --req <id> --agent` → writes runnable `_test.md` |

**Launch + present** — same as §1: use `Bash` (not Monitor), emit "Generating test cases…" before launch, then parse the output when it returns. Generate is a **quick single turn** — it exits on its own at `generate_done`.

**After Bash returns**, parse the NDJSON and present only what matters:

| Show | Event | How |
|------|-------|-----|
| **The deliverable** | `generate_snapshot` | Present scenarios + cases (see below) |
| **Clarifications** | `generate_clarification` | Surface the question — it needs an answer |
| **Save results** | `generate_save_result` | List files written |
| **Errors** | `error` | Surface the message |
| **Skip everything else** | `generate_thinking`, `generate_progress`, `generate_chat`, `generate_start` | Noise — don't narrate |

At `generate_done`, **present the result adaptively**:
- **≤ ~30 cases** → a nested tree: each scenario, then its cases tagged Positive / Negative / Edge.
- **more than that** → a summary line + a bulleted scenario list (title + case count); expand a scenario's cases only when asked.

Then offer the next commands from the terminal line's Refine / Save hints (they carry the request id) — don't hand-build them.

**Clarification → refine (do not skip):** if the turn ends with a clarification, that's **exit 0 — not an error**. Act on it: answer it yourself, or ask your own user, then **re-invoke** `kane-cli generate "<answer>" --refine --req <id> --agent`. Never drop a clarification.

**Attach files:** `--files a,b,c` adds local files (docs / images / PDF / CSV — up to 10, ≤ 50 MB each) as generation context on a **new** or **`--refine`** turn (not `--save`); each emits a `generate_upload` line before `generate_start`. Details in `references/generate.md`.

**Save is Functional-only:** `--save` writes only **Functional** cases to `_test.md` (under `<cwd>/.testmuai/tests` by default). Non-functional cases (Security, Performance, …) are generated and shown but not saved. Run saved files with **`kane-cli testmd run`** (`references/testmd.md`) — that's the generate → testmd pipeline.

Internal event/field names (`generate_snapshot`, `request_id`, …) are for parsing only — never show them to the user (§5 rule). Wire schema: `references/generate-parsing.md`.

---

## 7. When to read which reference

| Situation | Read |
|---|---|
| User wants to save/persist/re-run a test | `references/testmd.md` |
| Run a suite of saved `_test.md` tests as one batch | `references/testrun.md` |
| Run a suite on the cloud grid (`--remote`), incl. mobile suites from any machine | `references/testrun.md` §Remote + `references/mobile.md` §Remote |
| You need quick test cases or scenarios from a description | `references/generate.md` |
| User has requirement docs (PRD/spec) → designed suite, coverage, or suite upkeep | `references/assurance.md` |
| Need the assurance NDJSON event schema (`--mode agent`) | `references/assurance-parsing.md` |
| Share the context store with a team, join one, keep stores level, or resolve a sync conflict (kane-cli 0.8.14+) | `references/context-sync.md` |
| Run failed, need to diagnose | `references/debug.md` |
| View, share, validate, or merge evidence packs | `references/evidence.md` |
| Multiple independent browser tasks | `references/parallel.md` |
| Need full NDJSON event schema (`run`) | `references/parsing.md` |
| Need the `generate` NDJSON event schema | `references/generate-parsing.md` |
| Browse / create projects or folders, or parse the auto-default event | `references/test-manager.md` |
| Start of every session: preflight, the ready card, sign-in | `references/ready-check.md` |
| A person's first session: run first, the tour, three choices | `references/first-run.md` |
| Any result other than a plain passed or failed run (didn't start, stopped early, product bug, saved test, suite) | `references/cards.md` |
| Read, save or change the person's preferences | `references/agent-config.md` |
| Watch runs live in the Claude Code status bar | `references/live-strip.md` |
| First-time install, auth, or full config | `references/setup-and-config.md` |
| Compare / evaluate / benchmark kane-cli vs another tool or approach (cost, tokens, effort, ROI) | `references/fair-evaluation.md` |

## Command-specific completion

The `run_end` parsing strategy applies to one-shot `run` only. For `testmd run`, collect `test_md_done.overall_status`, `duration_s`, `session_id`, and optional `share_url`; embedded `run_end` events can finish individual steps. Local suites emit `testrun_done`; dispatched remote suites then emit `remote_done` (retain `status`, `exit`, `sessions_path`). `generate` emits `generate_done`. Assurance conversational agent streams end in `done`; review/read verbs have their own contracts. Always check process exit too: early refusal, invalid plan or dry-run can exit without the normal completion event.

Progress is for live display: count only `done`/`failed` completions, retaining child and execution context when step indices repeat.


For assertion mode, optional final validation, current-page `--analyzer-only` checks, streaming-network capture, and code-export defaults, read [Execution controls](references/execution-controls.md).
