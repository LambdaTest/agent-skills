# Agent testing checks playbook

Companion to `SKILL.md`. The checklists live in `SKILL.md`; this page holds the debugging table for AI agent failures, a case file format and a CI job.

For TestMu AI cloud capabilities, see [../../shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md). To run agent tests with Rook, use `rook-skill`.

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
| 9 | Evals pass at the API, the product still fails | the widget, streaming or rendering breaks | run key conversations through the real UI with Kane CLI |
| 10 | Quality drops after a model or prompt change | no regression set, or only an average score tracked | pin versions in the run record; compare pass rate per category |
| 11 | The coding agent reports "all tests pass" and the feature is broken | tests were loosened, skipped or mocked | diff the test files; rerun the suite yourself; verify in a browser |
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

```yaml
name: agent-checks
on: [pull_request]
jobs:
  evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm run evals -- --runs 5 --fail-under 0.9
      - name: Run the key conversation through the real UI
        run: |
          npm install -g @testmuai/kane-cli
          kane-cli login --username "${{ secrets.LT_USERNAME }}" --access-key "${{ secrets.LT_ACCESS_KEY }}"
          kane-cli run "Go to ${{ vars.PREVIEW_URL }}, open the support chat, ask 'What is your refund window?', store the assistant's reply as 'reply'" --agent --headless --timeout 180
```

`npm run evals` stands for your own eval runner; replace it with the command your project uses.
