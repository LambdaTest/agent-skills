# Headless output contracts

Use `rook help <command>` for installed command flags. The shapes below describe
the outputs used by this workflow. Validate required fields in actual responses;
if they differ, consult the installed CLI's documentation before adapting the
parser. Extra fields need not block a run; missing completion or verdict fields
must not be treated as success.

## Completion and output

Exit 0 means command completion, including a finished run with failed scenarios.
Exit 1 covers failures; there are no separate authorization/budget exit codes.
Check run verdicts as well as command status.

Commands that emit JSON write one document to stdout and prose to stderr.
`--verbose` writes text events to stderr, not a machine-readable event stream.

| Command with `--json` | Output |
| --- | --- |
| `plan` | `{ username, user_id, org_name, org_id, subscription, credits }`; null credits means the balance could not be read |
| `run` | `{ ok, error?, run_id?, halted, reason?, discarded?, unrunnable?, flag_problems?, credits, report? }` |
| `report` | `{ run_id, name?, dir, report }`; `dir` is the evidence folder |
| `scenarios list` | `{ agent_id, profile_id, total, runnable, scenarios: [{ scenario_id, title, feature_id, class, category?, state, excluded, unrunnable, multi_turn, criteria }] }` |
| `scenarios exclude/include/delete` | `{ ok: true, verb, ... }` |
| `status` | `{ project_id, offline, agents: [{ local_id, name, tree, offline, features, scenarios, profiles, unfinished_runs, owed_runs }], runs? }` |
| `mcp list` | `{ errors, servers: [{ name, origin, transport, state, source, changed_since_approval, shadowed_by }] }` |
| Other `mcp` operations | `{ ok, lines: string[] }`, with configuration inside `lines` |
| `ask` | `{ answer, command?, blocked_by?, summary? }`; the suggested command is not executed |
| `update auto` | `{ ok, pinned }`; changes the update-notice preference |

`status.agents[].tree` is `unsynced`, `clean`, `ahead`, `diverged`, `behind` or
`unknown`. Unknown means offline, not clean.

Some releases emit text despite accepting `--json` on `explore`, `generate`,
`sync`, `profile add/fix/test`, `report --rca` and `update` without `auto`.
Check for a JSON document before parsing; otherwise inspect exit status and
saved files. After authorized RCA, use `rook report <run-id> --json` to read the result.
`rook update` may replace the CLI; check its version afterward.

## Errors and partial runs

An error document can contain `{ "ok": false, "error": "...", "remedy": "..." }`.
Use `error`, or `reason` when present. Translate remedy tokens with
[troubleshooting](troubleshooting.md).

- `discarded: "refused"` can accompany `ok: true` and exit 1. Nothing ran.
- `discarded: "declined"` can exit 0 without a run.
- `halted: true` can retain a report and exit 0. Present it as incomplete.
- Gate refusals on `report`, `status` and `ask`, and parser errors, may leave
  stdout empty. Use the stderr diagnostic rather than inventing an error object.

## Grants and accounting

`--allow 'bash(npm test)'` grants one call shape; repeat it for more grants or use
`'bash(git *)@explore'` to scope a grant to one phase. `--yes` grants broadly for
that command without changing stored settings. Existing deny policy still applies.
Stored/session grants can authorize calls even when neither flag is present;
omitting flags is not a read-only guarantee.

Record reported spend when available. `profile add` may print no total. A change
in `rook plan --json` balance reflects the whole account, possibly including
other activity. Keep it distinct from a command receipt, and retain both figures
when they differ without inventing a billing explanation. A free command can
still use the network, change state or invoke the target.

## On disk

In 0.1.6, `.testmuai/rook/settings.json` keeps a project selection per
environment in `selections[environment]`. After a switch, rook
uses the new environment's selection, which may be empty even when another
environment has one. Run `rook doctor` to see the active environment and
`rook status --json` to read its `project_id`; if it is missing or wrong, run
`rook project use <id>`.

New project directories usually use
`.testmuai/rook/projects/<project-slug>--<project-id>/`; existing `<project-id>`
directories are reused. Find the directory by its project ID rather than
assuming either form. Under its `agents/<agent-id>/` directory:

| Path | Contents |
| --- | --- |
| `agent.yaml`, `features/`, `findings.yaml` | Agent specification, capabilities and findings |
| `profiles/`, `scenarios/` | Invocation profiles, generated profile READMEs and current scenarios |
| `runs/<run-id>/run.yaml` | Run manifest and pinned profile revision |
| `runs/<run-id>/` | Snapshots: `agent.yaml`, `features.yaml`, `profile.yaml` |
| `runs/<run-id>/report.yaml` | Report returned by `report --json` |
| `runs/<run-id>/scenarios/<scenario-id>/` | `snapshot.yaml`, `request.json`, `response.json`, artifacts and `verdict.yaml` |

Home state at `~/.testmuai/rook/` includes credentials, grants and session
transcripts. Keep it outside commits and shared evidence.
