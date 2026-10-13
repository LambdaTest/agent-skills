# Troubleshooting

Start with the environment, it is free and safe:

```bash
rook doctor
rook auth status
rook plan --json
rook status --json
```

`doctor` prints version, node, workspace, environment, controller and api
reachability, identity, auth state, project, mode (`cli`, `tui` or `headless`)
and tty.

## Failure documents

Parse stdout only when it contains JSON. A refused run can exit 1 with
`ok: true, discarded: "refused"`: use `reason`, not a missing `error` field.
Gate refusals on `report`, `status` and `ask`, and parser errors, may have no
JSON document; use the stderr diagnostic. Do not infer successful execution
from `ok: true` or from an old report on disk.

| `error` says                | Do                                                                                                                                 |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `remedy: login`             | you are not signed in — `rook login`; in CI, export `LT_USERNAME` and `LT_ACCESS_KEY`                                              |
| `remedy: repair_auth`       | a stored sign-in could not be refreshed or saved — not a sign-out; run `rook login` again and check `~/.testmuai/rook` permissions |
| `remedy: new_session`       | that session has been used up — run the command again                                                                              |
| `remedy: retry`             | could not reach the service — it may be down, or the network; wait and try again, or `rook doctor`                                 |
| `remedy: wait`              | rate-limited — wait the stated time, then retry                                                                                    |
| `remedy: server_error`      | the service answered with an error — retry later; include the status in a bug report                                               |
| `remedy: request_access`    | you do not have access to this project — ask the org admin for access                                                              |
| `remedy: create_project`    | this org has no projects yet — `rook project create <name>`                                                                        |
| `remedy: pick_project`      | no project selected — `rook project use <id>`                                                                                      |
| `remedy: agent_missing`     | the active agent is gone — `rook agent use <id>`                                                                                   |
| `remedy: explore_agents`    | no agents registered — `rook explore`                                                                                              |
| `remedy: pick_agent`        | no agent selected — `rook agent use <id>`                                                                                          |
| `remedy: topup`             | you are out of credits — check `rook plan` and add credits                                                                         |
| `remedy: reconcile`         | this agent has diverged from upstream — `rook sync`                                                                                |
| `remedy: update`            | this version is too old to be served — announce that `rook update` may install a newer version, then recheck skill compatibility   |
| `remedy: report`            | a client bug — file an issue with `rook export logs` attached                                                                      |
| no active agent             | `rook agent use <id>` after `rook explore`                                                                                         |
| no project selected         | `rook project use <id>` or `rook project create <name>`                                                                            |
| could not reach the service | check the network; `doctor` shows both endpoints                                                                                   |

## Discovery succeeds but registers no agents

An exit-zero `explore` with `0 analysed` does not establish that the target is
ready for generation. Check `rook status --json` and the saved agent tree.
Inspect whether the source was indexed and whether it contains the agent or
only a deterministic simulator. When the source supports it and the user's
scope/budget permits, retry once on the relevant file or directory with a
truthful description of the target; `--force` re-derives cached analysis.
Do not claim a simulator has an LLM backend, manufacture a declaration to hide
the discovery gap, or keep repeating paid discovery without new evidence.

## Unable to Verify everywhere

`unverifiable_reason: agent_never_ran` on every scenario means the profile
does not reach the agent. `rook profile test --goal "hello"` shows the raw
exchange; `rook profile fix` repairs it. `not_observable` means the criteria
are about something rook cannot see (a tool call the agent made off-record,
an image); that is a gap to report, not a failure to fix.

Inspect the saved raw response and hook records before concluding that the
target omitted evidence. In 0.1.1, an explicitly empty execute `calls` array
could be omitted from the hook record. It is not established whether later
releases still do this. If the saved raw response contains `calls: []` but the
hook record has no `calls`, report that gap and retain the recorded verdict;
do not invent calls or change scenario criteria just to obtain a pass.

The JSON-string decoding limitation observed in 0.1.1 is fixed in 0.1.6:
deterministic `json_path` checks can traverse valid JSON saved as a string in
`raw_response`. Invalid JSON, a raw string over the 8 MiB decode limit, or a
path that does not resolve yields Unable to Verify; the criterion's `achieved`
field explains why. Report that explanation and retain the recorded verdict;
do not invent evidence to fill the path.

## A verdict you disagree with

Quote the criterion and the evidence it cited, and open an issue with the
repo's "verdict dispute" template. Those are the most useful reports rook
gets.

## Bug reports

```bash
rook export logs --out ./rook-logs
rook export logs --out ./rook-logs.zip --all-sessions
```

Include `rook --version`, the OS, and the scenario and run ids. Never paste a
transcript, a credential, or the contents of `~/.testmuai/rook/`.
