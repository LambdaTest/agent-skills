# Agent testing checks playbook

Companion to `SKILL.md`. The checklists live in `SKILL.md`; this page holds the debugging table for AI agent failures, a case file format and a CI job.

For TestMu AI cloud capabilities, see [../../shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md). To drive Rook end to end, use `rook-skill`; its `references/ci.md` has the complete pipeline with verdict gating.

## Debugging table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | The agent states a price, policy or name that does not exist | no grounding, or retrieval returned nothing | return "not found" from the tool and instruct the agent to say so; add a grounding check against the source of truth |
| 2 | Same input passes and fails across runs | sampling variance | run each case several times, report the pass rate, lower temperature for deterministic steps |
| 3 | The agent follows instructions hidden in a document or web page | prompt injection through retrieved content | mark retrieved text as data, restrict tools after untrusted input, add injection cases to the regression set |
| 4 | Wrong tool, or right tool with wrong arguments | vague tool descriptions or overlapping tools | tighten the tool schema and descriptions; assert on tool name and arguments in code |
| 5 | An action runs twice | retry after a timeout without idempotency | idempotency keys on write tools; assert on the end state |
| 6 | It forgets an earlier turn | context truncated or summary dropped a fact | test long conversations; assert on facts from turn one at turn ten |
| 7 | It reveals the system prompt or another user's data | no output filtering or over-broad retrieval scope | scope retrieval to the user; add must-not-include checks |
| 8 | The LLM judge passes obviously bad answers | the rubric is vague, or the judge was never validated | write a pass or fail rubric with examples; check the judge against human labels |
| 9 | Evals pass at the API, the product still fails | the widget, streaming or rendering breaks | invoke the deployed agent through its real entry point with a Rook profile |
| 10 | Quality drops after a model or prompt change | no regression set, or only an average score tracked | pin versions in the run record; compare pass rate per category |
| 11 | Passes in staging, fails in production | different model version, tools or data between the two | pin versions; test a staging target that mirrors production |
| 12 | Latency or cost doubles | extra tool loops or a larger context | cap steps per turn; log tokens and tool calls per case |

## Case file format

```json
{
  "id": "refund-window-01",
  "area": "grounding",
  "turns": ["What is your refund window?"],
  "runs": 5,
  "checks": [
    { "type": "must_include", "value": "30 days" },
    { "type": "must_not_include", "value": "60 days" },
    { "type": "tool_called", "name": "get_policy", "args": { "topic": "refunds" } }
  ]
}
```

## CI: GitHub Actions

A person must review the target, its real writes, the credit spend and the tool grants before this job is enabled.

```yaml
name: agent-tests
on: [pull_request]
jobs:
  rook:
    runs-on: ubuntu-latest
    env:
      LT_USERNAME: ${{ secrets.LT_USERNAME }}
      LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - run: npm install -g @testmuai/rook@latest
      - run: rook project use "${{ vars.ROOK_PROJECT_ID }}"
      - run: rook agent use "${{ vars.ROOK_AGENT_ID }}"
      - run: rook sync --yes
      - run: rook run --yes --json > run.json
      - run: rook report "$(jq -r .run_id run.json)" --json > report.json
      - name: Fail the build unless every scenario ran and passed
        run: |
          jq -e '.report.totals.failed == 0 and .report.totals.unjudged == 0
            and .report.totals.not_run == 0 and .report.totals.executed > 0' report.json
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: rook-report, path: report.json }
```

`rook run` exits 0 when the run finishes, whether scenarios passed or failed, so the gate reads the verdict counts from the report. The job expects a committed `.testmuai/rook/` tree with a configured profile. This is the short form; the recipe in `rook-skill` adds the full completion checks.
