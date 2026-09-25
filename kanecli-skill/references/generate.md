<!-- Read this when the user wants to GENERATE or AUTHOR test cases / scenarios from a plain-language description or requirement (not run a browser). Owns the generate modes (new / refine / save), the refine→save→run workflow, clarification handling, result presentation, and the generate→testmd handoff. The wire/event schema lives in references/generate-parsing.md. -->

# Generating Test Cases with `kane-cli generate`

`kane-cli generate` turns a plain-language description of *what to test* into structured **Test Scenarios** (logical groupings) each containing **Test Cases** (typed Positive / Negative / Edge). It calls the AI Test Case Generator — **no browser is launched**. The result is a tree of scenarios + cases you present to the user, refine conversationally, and optionally save as runnable `_test.md` files.

**Use this whenever a task needs test cases or scenarios written — don't hand-author them in chat or a scratch file.** Reach for it to: turn a requirement / feature description into a test suite; expand or refine coverage (more edge cases, negative paths, a narrower or broader focus); or save the Functional cases as runnable `_test.md`. It is **not** for driving a browser — that's `kane-cli run` (§3 of SKILL.md).

> For the full web-product picture (dashboards, issue-link inputs), see the public docs: <https://www.testmuai.com/support/docs/generate-test-cases-with-ai/>. The CLI takes a **text objective**, optionally with local files attached via **`--files`** (see "Attaching files" below).

## The three modes — one turn per invocation, then exit

There is **no interactive session**. Each invocation runs exactly one generation turn and exits. Continuity across turns is carried by a **request id** (`--req <id>`) that the previous turn's terminal line hands back.

| Mode | Command | Notes |
|---|---|---|
| **New** | `kane-cli generate "<what to test>" --agent` | Starts a fresh request. Capture the request id from the terminal line. |
| **Refine** | `kane-cli generate "<change>" --refine --req <id> --agent` | Adjusts an existing request. `--refine` **and** `--req` required; needs a change description. |
| **Save** | `kane-cli generate --save --req <id> [--out <dir>] --agent` | Writes the request's Functional cases to `_test.md`. No new turn, takes no objective. |

`--refine` and `--save` always run headless (even from a terminal).

### Flags

| Flag | Purpose |
|---|---|
| `--agent` | Typed NDJSON on stdout (auto-on when stdin is not a TTY) |
| `--req <id>` | The request id to `--refine` or `--save` |
| `--out <dir>` | Save target — **only** with `--save`; default `<cwd>/.testmuai/tests` |
| `--name <name>` | Names the run and the saved suite folder |
| `--scenario-limit <n>` / `--per-scenario-limit <n>` | Cap scenarios / cases-per-scenario |
| `--memory` | Use the memory layer — reuse relevant existing cases, reduce duplicates |
| `--files <paths>` | Comma-separated local files to attach as context (new / refine only — see "Attaching files") |
| `--project <id>` / `--folder <id>` | Test Manager project / folder |
| `--username` / `--access-key` | Auth (same as `run`) |

If neither `--project`/`--folder` nor a saved project/folder is set when generation starts, kane-cli auto-resolves one headlessly and emits a `project_folder_auto_defaulted` event before `generate_start`. Translate it to a one-line note for the user — full handling lives in `references/test-manager.md`.

## Attaching files

Pass local files as extra context with `--files <comma-separated paths>` on a **new** generation or a **`--refine`** (not `--save`). The generator reads them and reflects them in the scenarios + cases — attach a spec, a screenshot of the UI, a PDF / Word doc, or a CSV of inputs.

```bash
kane-cli generate "test the login flow described in the attached spec" --files ./login-spec.pdf,./wireframe.png --agent
```

- **Supported types** — documents (`.txt .json .xml .csv .pdf .docx .xlsx`), images (`.jpg .jpeg .png .gif .bmp .webp`), audio (`.mp3 .wav .m4a`), video (`.mp4 .mov .webm .mpeg .mpga`).
- **Limits** — up to **10 files**, each **≤ 50 MB**.
- **Validated as a set, up front** — if any path is missing, an unsupported type, too large, or over the count, the whole command is rejected (exit `2`) **before anything is sent** and the offending paths are listed; fix and re-run. Files outside the current directory are allowed but flagged with a warning on stderr.
- **`new` / `--refine` only** — combining `--files` with `--save` exits `2`.

Under `--agent`, each file emits a `generate_upload` line (`status` `uploading` → `done`) **before** `generate_start` — see `references/generate-parsing.md`. *(Interactively in the TUI, type `@` in the generate prompt to attach a file inline.)*

## Presenting a result (adaptive)

The terminal data carries the full scenarios + cases. **Present it based on size**:

- **≤ ~30 cases → a nested tree** (scenario, then each case with its type tag):
  ```
  ✓ Generated 3 scenarios · 11 cases  (request 23271)

  ▸ Login
     - Valid credentials [Positive]
     - Wrong password [Negative]
     - Empty fields [Edge]
  ▸ Checkout
     - Guest checkout [Positive]
     - Expired card [Negative]
     ...
  ```
- **more than ~30 cases → a summary + scenario list** (cases on request):
  ```
  ✓ Generated 6 scenarios · 84 cases  (request 23271)

    • Login (12 cases)
    • Checkout (20 cases)
    • Cart management (14 cases)
    ...
  ```

Always end with the **next-step commands the terminal line provides** (Refine / Save) — they already carry the request id, so don't hand-build them.

## Clarifications — act on them, never drop them

If a turn ends with a **clarification question**, that is **success (exit 0)**, not an error — the generator needs an answer before it can continue. You must act on it:

1. Read the question.
2. **Decide** — answer it yourself from context, **or** surface it to your user and get an answer.
3. **Re-invoke** with the answer as a refine:
   ```bash
   kane-cli generate "<your answer>" --refine --req <id> --agent
   ```

## The refine → save → run loop

```bash
# 1. New request
kane-cli generate "checkout flow on a shopping site" --agent
#    → terminal line carries request id 23271 + Refine/Save hints

# 2. Refine (repeat as needed)
kane-cli generate "also cover an expired card and an out-of-stock item" --refine --req 23271 --agent

# 3. Save the Functional cases as runnable _test.md
kane-cli generate --save --req 23271 --agent
#    → <cwd>/.testmuai/tests/<suite>/<scenario>/<case>_test.md

# 4. Run / replay them
kane-cli testmd run .testmuai/tests/<suite>/<scenario>/<case>_test.md --agent
```

**Save is Functional-only.** `--save` writes only test cases whose category is **Functional** — those are the ones runnable as `_test.md`. Non-functional cases (Security, Performance, etc.) are generated and shown in the result but are **not** written; saving a request with no Functional cases writes nothing and says so. Saved files are ordinary `_test.md` tests — see `references/testmd.md` for running, editing, and replay. This is the **generate → testmd** pipeline: author cases here, run them there.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Turn completed (including a turn that ended with a clarification) |
| 1 | Generation failed (or ended) |
| 2 | Error — auth / setup / transport, or an invalid flag combination |
| 3 | Generation stopped / cancelled |
| 130 | Interrupted (Ctrl-C) |

Invalid flag combinations exit `2` with a message on stderr. The full set:

- `--refine` and `--save` together
- `--refine` without `--req`
- `--refine` without a change description
- `--refine` combined with `--out` (`--out` is save-only)
- `--save` without `--req`
- `--save` with a description (it takes none)
- `--out` without `--save`
- `--files` with `--save` (files attach to a new generation or a refine, not a save)
- `--req` without `--refine` or `--save`
- a new generation with no description

## Reading the output

`--agent` emits one typed JSON object per line. For the full event schema and the parse strategy, Read **`references/generate-parsing.md`**. As with all `--agent` output, the field names are for parsing only — **never show them to the user**; present plain-language scenarios and cases (per "Presenting a result" above).
