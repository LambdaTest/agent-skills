# Perfecto to TestMu AI migration playbook

Companion to `SKILL.md`. The step-by-step workflow lives in `SKILL.md`; the construct-by-construct mappings live in the files below. This page collects the checks, debugging table, CI pattern and checklist that apply to every migration from this source.

## Reference files

- [hyperexecute.md](hyperexecute.md)
- [languages.md](languages.md)
- [perfecto.md](perfecto.md)
- [testmu-target.md](testmu-target.md)

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
| 1 | 401 Unauthorized on session create | old vendor credentials or unset `LT_USERNAME`/`LT_ACCESS_KEY` | export both env vars (CI secrets too); never hard-code them; check no placeholder string survived in config files |
| 2 | Session starts but ignores build, name, video or tunnel | TestMu keys sent flat and prefixed `appium:` by the client, or left inside the old vendor block | put TestMu keys in `LT:Options` (`w3c: true`); remove `bstack:options`, `sauce:options` and similar blocks |
| 3 | Every session shows passed, even failing tests | status hook sends a hard-coded `passed`, or runs after `driver.quit()` | send `lambda-status=` from the real outcome before quit (see the framework rows in reference/languages.md or the skill's status section) |
| 4 | Status hook throws "no such session" | framework closed the session first (JUnit 4 `@After`, Nightwatch `end_session_on_fail`) | move quit into the same hook that sends the status |
| 5 | "Platform not found" or session queued forever | vendor platform strings (`OS X Ventura`, `macOS 10.15`, `Windows 8`) | use TestMu names (`macOS Sequoia`, `MacOS Tahoe`, `Windows 11`); check the platforms API for old OS versions |
| 6 | "Device not found" for app or mobile web | vendor device names (`Samsung Galaxy S23`, `Google Pixel 8`) or missing `platformVersion` | use TestMu names without vendor prefix (`Galaxy S23`, `Pixel 8`) or a regex, and set `platformVersion` |
| 7 | App not installed / invalid app | `bs://`, `storage:` or local path passed as `app` | upload to TestMu (`/app/upload/realDevice`) and pass the `lt://` id or the upload `custom_id` |
| 8 | Local or staging site unreachable | tunnel not started, not ready yet, or name mismatch | start the LT binary with `--tunnelName` and `--infoAPIPort`, wait for `/api/v1.0/info`, set the same `tunnelName` in caps; on HyperExecute let the YAML own the tunnel |
| 9 | CI job green while tests fail | runner exits 0 (Cypress CLI without `--sync=true --eof=true`, async build APIs) | use the documented exit-code flags or HyperExecute, whose CLI exit code reflects the result |
| 10 | Tests run but nothing appears on the dashboard | tests still pointed at a localhost hub or the old vendor hub | grep for every fingerprint in the vendor reference; route all drivers to `hub.lambdatest.com` / `mobile-hub.lambdatest.com` / `cdp.lambdatest.com` |
| 11 | Sessions queue and time out under parallel load | parallelism above the TestMu plan's concurrency | cap runner workers/threads at the plan limit; use HyperExecute `concurrency` for larger suites |
| 12 | Build fails after removing the vendor SDK | the SDK brought Selenium, JUnit, TestNG or other libraries in transitively | add them back as direct dependencies at the versions the old lockfile showed |

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
