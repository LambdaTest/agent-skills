# Percy to TestMu AI migration playbook

Companion to `SKILL.md`. The step-by-step workflow lives in `SKILL.md`; the construct-by-construct mappings live in the files below. This page collects the checks, debugging table, CI pattern and checklist that apply to every migration from this source.

## Reference files

- [percy.md](percy.md)
- [smartui-target.md](smartui-target.md)

Full TestMu AI capability and device reference for the whole repository: [../../shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Migration order

1. Run `scripts/detect.py` (when the skill ships it) and agree scope: modules, target product (TestMu AI Browser Cloud / Real Device Cloud, HyperExecute, SmartUI).
2. Convert one test or spec file end to end and run it against TestMu AI before touching the rest.
3. Convert configuration, capabilities, status hooks, uploads, tunnel and CI in that order.
4. Grep for every fingerprint in the vendor reference; each hit is migrated, intentionally kept, or listed as an open item.
5. Write the migration record (`TESTMU_MIGRATION.md`) and the agent-instructions block so future edits stay on TestMu AI.

## Debugging table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | "Cannot find SmartUI server." | snapshot calls run outside `smartui exec` | wrap the test command: `npx smartui --config .smartui.json exec -- <cmd>`; guard calls with an env var if the suite also runs without SmartUI |
| 2 | `PROJECT_TOKEN` rejected | token from the wrong SmartUI project or still `PERCY_TOKEN` | create the SmartUI project, copy its token into the `PROJECT_TOKEN` secret |
| 3 | Every screenshot is "new" on the first build | Percy baselines do not transfer | run the baseline branch once, approve in SmartUI, then switch PR pipelines |
| 4 | `smartui exec` fails on config | a `storybook` block or Percy keys left in `.smartui.json` (schema rejects unknown keys) | keep only SmartUI keys; Storybook config goes in its own file |
| 5 | `smartui storybook` command not found | Storybook is a separate package | install `@lambdatest/smartui-storybook` |
| 6 | Pipeline no longer fails on visual changes | `percy build:wait` gating was dropped | add `--fetch-results results.json` and a script that fails on changed screenshots (Storybook: `failOn`) |
| 7 | Dynamic regions flag diffs | `percyCSS` / ignore regions not converted | map to `customCSS` and `ignoreDOM` options |
| 8 | Parallel shards create several builds | different build names per shard | pass the same `--buildName` in every shard |
| 9 | Ruby snapshot call raises NameError | module spelled `LambdaTest::` | use `Lambdatest::Selenium::Driver.smartui_snapshot` |
| 10 | App screenshots missing | App Percy calls converted to the web SDK | use hooks (`smartUI.project` + `smartui.takeScreenshot`) on the Real Device Cloud or the Java `SmartUIAppSnapshot` API |

## CI/CD integration (GitHub Actions)

```yaml
name: tests-on-testmu
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    env:
      LT_USERNAME: ${{ secrets.LT_USERNAME }}
      LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
      PROJECT_TOKEN: ${{ secrets.PROJECT_TOKEN }}
      LT_BUILD_NAME: ${{ github.workflow }}-${{ github.run_number }}
    steps:
      - uses: actions/checkout@v4
      # install the project's own toolchain here (setup-node, setup-java, setup-python)
      - run: <the test command, unchanged except for the TestMu settings>
```

Replace the old vendor's GitHub Action, orb or plugin step with this. For HyperExecute, download the CLI and run `./hyperexecute --user "$LT_USERNAME" --key "$LT_ACCESS_KEY" --config hyperexecute.yaml` (see the HyperExecute reference in this skill).

## Best practices checklist

- [ ] Every session goes to a TestMu AI endpoint; no old vendor host, SDK, CLI or secret remains (or each remaining one is listed).
- [ ] Credentials come from `LT_USERNAME` / `LT_ACCESS_KEY` env vars; `.env.example` lists them with no values; leaked old keys are reported for rotation.
- [ ] Pass/fail is reported from the real test outcome, before the session closes.
- [ ] Platform and device names use TestMu spelling; mobile entries have `platformVersion`.
- [ ] Apps are uploaded to TestMu and referenced by `lt://` id or `custom_id`.
- [ ] Tunnel starts, is checked for readiness, and is named per CI job.
- [ ] CI fails when tests fail.
- [ ] Assertions and test logic are unchanged; vendor-only gaps carry `TODO(testmu-migration)`.
- [ ] `TESTMU_MIGRATION.md` and the AGENTS.md block are written.
