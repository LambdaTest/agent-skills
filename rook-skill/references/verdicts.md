# Verdicts and reporting

Read `report` from `rook run --json` or `rook report <run-id> --json`. For
criterion details, read `runs/<run-id>/scenarios/<scenario-id>/verdict.yaml`.

## Fields needed for a summary

| Record | Fields |
| --- | --- |
| Scenario verdict | `scenario_id`, `status`, `criteria[]`, `unverifiable_reason`, `compromised`, `forbidden_hits[]` |
| Criterion | `criterion_id`, `criterion`, `expected`, `achieved`, `status`, quoted `evidence`, `confidence` |
| Report | `run_id`, `agent_id`, `agent_version_id?`, `generated`, `headline`, optional `narrative` and `next[]`, `totals`, `metrics`, `clusters[]`, `credits` |
| Totals | `planned`, `executed`, `passed`, `failed`, `unverifiable`, `unjudged`, `not_run`, `unrunnable`, `decided`, `pass_rate`, `carried_forward` |
| Cluster | `id`, `why`, `kind` (`failed`, `unverifiable`, `compromised`), `scenarios[]`; RCA may add `cause`, `remedy`, `confidence`, `fault`, `where`, `summary` |

Statuses are **Pass**, **Fail**, and **Unable to Verify**. Unverifiable reasons:
`agent_never_ran`, `not_observable`, or `undecidable`. A scenario that never ran
has no verdict; do not turn its absence into a failure.

## Pass rate

In 0.1.6, `totals.pass_rate` is `Pass / (Pass + Fail + Unable to Verify)`.
`totals.decided` still means `Pass + Fail`. Unable to Verify contributes to the
pass-rate denominator as a recorded result, but remains a separate verdict;
never describe it as Fail. If every recorded result is Unable to Verify,
`pass_rate` is `0`; if there are no recorded Pass, Fail or Unable to Verify
results, it is `null`, not zero.
Unjudged, not-run and unrunnable work does not enter this denominator.

## Presenting results

Use a table like this, populated from the records:

| Field | Result |
| --- | --- |
| Agent / run | Name, agent ID and run ID |
| Scope | Planned/executed counts; incomplete, unjudged and not-run work |
| Pass / Fail / Unable to Verify | Separate counts, with reasons for unverifiables |
| Compromised | Observed adversarial compromises; unknown when evidence is absent |
| Credits | Total command spend when supplied |
| Evidence | The returned `dir`, or state that no directory was supplied |

For each failed or compromised scenario, include its ID/title, criterion,
expected versus achieved result and an evidence quote. Group unverifiables by
reason and explain what observation would make them checkable. Distinguish a
recorded verdict from a suspected problem in its criterion or verification.

Report a refused/declined invocation as no run and a halted invocation as
incomplete. Preserve recorded planned/executed counts; a halt does not prove
that scenarios were skipped. Read `error` or `reason`, translate a supplied
`remedy`, and use stderr when there is no JSON error document.

Use only supplied metadata. Missing summary/RCA fields do not establish which
flags or roles ran. An empty compromised cluster list does not establish that
no adversarial scenarios ran. Identify missing criterion evidence instead of
inventing quotes; label any example path as unverified.

## Credits and comparisons

Top-level `credits` from `run --json` includes report generation.
`report.metrics.credits` covers execution/judging, while `report.credits` covers
that report's generation. If only a saved report is available, show those two
amounts separately: later RCA can rewrite the report spend, so their sum is not
necessarily the command's cumulative billing history.

For comparisons, use each scenario's `snapshot.yaml` and verdicts from both
runs. Distinguish newly failing, fixed, flaky (flips on an unchanged scenario)
and redefined (scenario text changed). Find prior runs under the agent's `runs/`
folder or in `rook status --agent <id> --json`. Omit comparisons when the prior
evidence is unavailable.
