# In CI

Requires bash, jq, the Rook CLI, a committed `.testmuai/rook/` tree containing
`ROOK_AGENT_ID` and a selected, configured profile. Supply the profile's declared
environment variables through CI secrets, alongside `LT_USERNAME`, `LT_ACCESS_KEY`
and `ROOK_PROJECT_ID`. Rook signs in from `LT_USERNAME`/`LT_ACCESS_KEY` directly, ahead
of any stored sign-in, so the recipe needs no `rook login` step and the key never
appears on a command line. Set `GITHUB_RUN_ID` to a job label outside GitHub Actions.
A person must review the target, its real writes, credit spend and tool grants
before enabling this workflow. Install the CLI before this recipe; pin its
version in your own CI for reproducibility. Compatibility is checked through required output fields, not
an exact version string. Recheck changed commands with `rook help <command>`.

```bash
set -euo pipefail
printf 'Rook CLI: %s\n' "$(rook --version)" >&2
rook project use "$ROOK_PROJECT_ID"
rook agent use "$ROOK_AGENT_ID"
rook explore . --yes
rook generate --yes --json
# A committed tree is not an upstream record. Publish the profile/scenarios first.
rook sync --yes
run_code=0
rook run --concurrency 3 --name "ci-$GITHUB_RUN_ID" --yes --json > run.json || run_code=$?
if [ "$run_code" -ne 0 ]; then
  jq -r '.error // .reason // "rook failed; inspect stderr"' run.json >&2 || true
  echo "rook run exited $run_code; inspect stderr if no diagnostic was returned" >&2
  exit "$run_code"
fi
# A declined or interrupted run can exit 0; neither is a completed suite.
jq -e '.ok == true and .discarded == null and .halted == false
  and (.run_id | type == "string" and length > 0)
  and (.report | type == "object") and (.credits | type == "number")' run.json >/dev/null
run_id=$(jq -er '.run_id' run.json)
rook report "$run_id" --json > report.json
# Missing/malformed counts or a mismatched report must not become a green build.
jq -e --arg id "$run_id" '.run_id == $id and .report.run_id == $id
  and (.dir | type == "string" and length > 0)
  and (.report.totals | [.planned, .executed, .passed, .failed, .unverifiable,
    .unjudged, .not_run, .unrunnable] | all(.[]; type == "number" and . >= 0 and floor == .))
  and (.report.totals | .planned == (.executed + .not_run)
    and .executed == (.passed + .failed + .unverifiable + .unjudged))
  and (.report.clusters | type == "array")' report.json >/dev/null
jq -r '.report.totals | "Pass: \(.passed) · Fail: \(.failed) · Unable to Verify: \(.unverifiable)",
  "Unjudged: \(.unjudged) · Not run: \(.not_run) · Unrunnable: \(.unrunnable)"' report.json
jq -r '"Total credits: \(.credits)"' run.json
jq -r '"Evidence: \(.dir)/", (.report.clusters[] |
  "\(.kind): \(.why) [\([.scenarios[].scenario_id] | join(", "))]")' report.json
jq -e '.report.totals.failed == 0 and .report.totals.unjudged == 0
  and .report.totals.not_run == 0 and .report.totals.executed > 0
  and ([.report.clusters[] | select(.kind == "compromised")] | length == 0)' report.json >/dev/null
```

Gate on both command completion and verdicts: a finished run exits 0 even when
scenarios failed. A refused run can exit 1 with `ok: true, discarded: "refused"`;
its diagnostic is `reason`. Read the report by the ID from this invocation,
never by the default “latest” after an error. An interrupted run retains evidence
worth reading but is not a completed suite.

Fail the job on any Fail or compromised scenario, command error, or incomplete
run. Do not fail on Unable to Verify alone; print its count and reasons. For
per-criterion evidence, read the verdicts under the returned run directory as
shown in `verdicts.md`. Unrunnable scenarios are printed as an assurance gap;
this recipe does not fail on that gap alone. Optional summary fields are not
required for the gate.

`rook sync --yes` records the scenarios/profile upstream. If the requested CI
result should remain local instead, omit sync and use `rook run --test` with the
same flags and result checks. Do not silently switch between these policies.

Cache the project `.testmuai/rook/` for history and comparisons. Never cache or
commit `~/.testmuai/rook/`. `--yes` supplies broad command-scoped tool consent;
existing deny policy still applies. Rook uses headless mode when `--yes` is passed,
stdin is not a TTY, or any of `CI`, `GITHUB_ACTIONS`, `GITLAB_CI`, `BUILDKITE` or
`JENKINS_URL` is set (to any value, including `false`).
