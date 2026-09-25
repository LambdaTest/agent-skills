<!-- kane-cli skill reference: evidence packs (view, share, validate, merge) -->

# Evidence Packs — Agent Surface

Every kane-cli run seals an **evidence pack**: one `.evidence` file (a zip) holding the test definition, results, per-step screenshots + annotated screenshots, per-step console/network logs, run logs, and failure records. It is the **only** place run artifacts live — the legacy `runs/<n>/` session subdirectory is no longer created — and the primary artifact for showing a user what happened and for debugging.

## Inside a pack

A `.evidence` file is a standard zip: `unzip -l <pack>` lists it, `unzip -p <pack> <entry>` prints one entry.

```text
<execution_id>.evidence
├── run.yaml                          # run manifest: title, status, started/ended, totals
├── failure.yaml                      # run-level failure rollup
└── tests/<test-id>/                  # one per test (testrun packs have many)
    ├── test.md                       # the definition
    ├── result.yaml                   # verdict + steps[] (ordinal, status, kind, duration_ms, action_id)
    ├── logs/                         # meta.yaml, tui.log, and per run index n:
    │                                 #   <n>-run.log, <n>-actions.ndjson,
    │                                 #   <n>-console.ndjson, <n>-network.har
    ├── steps/<ordinal>-<step-id>/    # screenshot.png, annotated.png, step.json
    │                                 #   (+ failure.yaml on failed steps)
    ├── auteur/execution.json         # full execution trajectory
    └── v16-trajectory/               # per-run planning summaries
```

Reading and debugging from the pack (unzip recipes, failure records): `references/debug.md`.

## Where packs land

| Surface | Sealed pack location |
|---|---|
| `kane-cli run` / TUI | `<sessionDir>/evidence/<execution_id>.evidence`; **also** copied to `<cwd>/.testmuai/evidence/` when the session is named (`--name`) |
| `kane-cli testmd run` | always copied to `<cwd>/.testmuai/evidence/` |
| `kane-cli testrun run` | created directly in `<cwd>/.testmuai/evidence/` |

## The stderr hint — and how to act on it

After a successful agent-mode run, kane-cli prints one hint line to **stderr** (it is NOT an NDJSON event; never look for it on stdout):

```
evidence: view locally with `kane-cli evidence serve <packPath>`
```

**On a person's first run, do not just offer:** start the server and put the viewer link in the result card, so the tour's "evidence" becomes something they can click (`references/first-run.md` §3). From the second run on, go back to offering.

When you see it (or when the user asks to see run evidence): **offer** — "Want to view the run evidence in your browser?" If yes, run the serve command via Bash (`run_in_background` so it keeps serving) and give the user the `viewer` URL from its stdout:

```
serving 1 pack on http://127.0.0.1:<port>
<name>.evidence
  pack    http://127.0.0.1:<port>/<token>/<name>.evidence
  viewer  https://evidence.lambdatest.com/?pack=<encoded pack url>
press Ctrl-C to stop
```

Present only the `viewer` line as a clickable link. Tell the user the server is local-only (nothing uploads; their browser reads the pack from their machine) and stays up until stopped. Stop the background process when they're done.

## Validate — integrity checks

```bash
kane-cli evidence validate <execution-id-or-path> --json
```

Exit `0` valid · `1` invalid · `2` not found. Use it when a pack won't open in the viewer (truncated / unsealed / killed run) or as a CI gate. `--profile L0|L1` selects strictness (default `L1`).

## Merge — many packs into one

```bash
kane-cli evidence merge <targets...> --run-id <id>
```

Combines packs (execution ids or paths, order-significant) into one, sealed by default at `.testmuai/evidence/<run-id>.evidence`. `--run-id` is required. Exit `0` merged · `1` policy abort (e.g. mixed projects, duplicate run ids) · `2` usage. Full policy detail is in the user guide — for anything beyond a simple merge, point the user there rather than improvising flags.

## Debugging with a pack

The pack is the first place to look on a failure: the failed step's **failure record** (error + page state), its **console/network slice** (4xx/5xx or JS errors usually explain it), and the **annotated screenshot** (what the agent actually acted on). Full failure workflow: `references/debug.md`.

## Evidence merge identity

For ordinary runs, default merge identity distinguishes the test and commit (`external_id.test_id`, `external_id.commit_id`) and the environment (`environment.os`, `environment.os_version`, `environment.browser`, `environment.browser_version`). Re-runs with the same identity nest as attempts; a different environment produces a separate sibling.

Explicit collision policies can change grouping; a custom `--rules` file replaces the default rules rather than extending them. Check the selected identity rules before interpreting two runs as retries of the same test.
