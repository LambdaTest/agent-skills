---
name: rook-skill
license: Apache-2.0
compatibility: Live testing requires the Rook CLI, network access and a TestMu AI account; CI examples require bash and jq.
description: Use rook to test, evaluate, red-team or regression-check an AI agent the user owns, or to interpret saved Rook results. Does not apply to ordinary unit tests, browser automation or web UI checks without an AI agent under test.
---

# Test agents with Rook

Use Rook to derive scenarios, invoke the target and grade the evidence. Respect
requests to use another tool. For saved-result requests, read the supplied files
without starting setup, a new run or paid analysis.

## Your role

You are the orchestrator: you choose and run Rook commands, and Rook does the
testing work. Discovery is `rook explore`, test design is `rook generate`, and
invocation and grading are `rook run` and `rook report`. When the user asks to
explore, understand, plan tests for or test an agent, run the matching command.
Do not read the target's code to describe the agent, or write your own test
plan or verdicts, in its place. Answer from Rook's agents, scenarios and
verdicts. Read the target's source only for a step Rook needs from you, such as
a profile's transport and command, or to explain a Rook result. If credits or
authorization block the next command, name it and what it needs; manual
analysis is not a substitute.

## Setup and execution

Check `rook --version` and use `rook help <command>` for the installed CLI's
options. If Rook is missing, use the
[installation instructions](https://github.com/LambdaTest/rook#install).
Use this workflow across compatible releases; a different version alone is not
a reason to stop or change the installation. If a command or output differs,
consult its help and release notes before adapting that step. Keep completion
and evidence checks intact; do not guess missing fields or retry paid work to
probe compatibility. Installation changes still require authorization.

```bash
rook doctor
rook status --json
rook plan --json
```

Use the next command needed by the current state:

| Need | Command |
| --- | --- |
| Sign in | `rook login`; in CI, export `LT_USERNAME` and `LT_ACCESS_KEY` (no login step) |
| Select a project | `rook project use <id>` or `rook project create <name>` |
| Discover agents | `rook explore . --json` |
| Select an agent | `rook agent use <id>` |
| Generate scenarios | `rook generate --json` |
| Create/test a profile | `rook profile add <name> --from <file>` or `--command '<argv>'`; then `rook profile test --goal "<reply-only goal>"` |
| Run | `rook sync --yes` before `rook run --json`, or `rook run --test --json` for a local result |
| Read results | `rook report <run-id> --json` |

Choose the profile's transport and command from the target's source or the
user's invocation details; ask when unknown. See [profiles](references/profiles.md).
Use `rook help <command>` for flags and [scenarios](references/scenarios.md) to
scope a run with `--only`, classes, categories or tags. When an agent has more
than one profile, check the active profile with `rook profile` or pass
`rook run --profile <id>` to select the intended target.

## Authorization and credits

Before `profile add`, `profile fix`, `profile test` or `run`, inspect the target's
`agent.yaml` for `calls[]` entries with `write: true`. Those commands can reach
the real agent. Use staging and obtain any missing authorization for its effects;
Rook cannot undo them; do not rely on a per-target headless confirmation.
Verify effects through read-only interfaces; inspect available read tools before
concluding that an effect is unverifiable. Keep secrets as `${VAR}` references through
`rook env set`, outside profiles and transcripts.

Announce spending before `explore`, `generate`, `run`, `profile add|fix`, `ask`
and `run|report --rca`. `profile test` invokes the target without Rook model credits.
Use paid RCA only with user authorization. Track the user's budget across
commands; do not assume the CLI enforces an aggregate task cap. Check its help
for available limits. A null balance means unknown.
Prefer scoped `--allow` grants; use `--yes` only within the authorized scope.
See [headless contracts](references/headless-contract.md) for output, grants and
credit accounting.

## Report the evidence

Check the exit status and `discarded`/`halted` fields before claiming completion.
A finished run exits 0 even when scenarios fail; `ok: true` can also describe a
refused run. Parse JSON only when a document exists, otherwise use stderr.
Read the report by this invocation's run ID, not an old default report.

Follow [verdicts](references/verdicts.md): show **Pass**, **Fail** and **Unable to
Verify** separately, quote criterion evidence, identify gaps and compare prior
runs only when their evidence is available. Preserve incomplete results and
unknown metadata; do not invent evidence or replace Rook's verdict with your
own reading of the agent reply.

## References

- [CI](references/ci.md): complete pipeline and verdict gating.
- [MCP](references/mcp.md): server discovery, approval and configuration.
- [Troubleshooting](references/troubleshooting.md): setup failures and version-specific verification limitations.
- [Headless contracts](references/headless-contract.md): JSON shapes and saved-file locations.

Project evidence lives under `.testmuai/rook/`. Credentials and session state
live under `~/.testmuai/rook/`; do not commit that home directory.
