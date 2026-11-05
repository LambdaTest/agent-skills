# Cypress Cloud to TestMu AI

Read this when the source is Cypress Cloud (formerly Cypress Dashboard): `cypress run --record --key`, `projectId`, `--parallel`, `--group`, `--ci-build-id`. Cypress Cloud records results and balances specs across your CI machines; the browsers run on your CI. The migration moves browser execution and reporting to TestMu AI (`lambdatest-cypress-cli` on the grid, or HyperExecute) and removes Cypress Cloud recording.

Contents
1. Fingerprints
2. Target choice: grid CLI or HyperExecute
3. CLI flag mapping (`cypress run` to `lambdatest-cypress run`)
4. lambdatest-config.json from an existing Cypress project
5. Parallelism, grouping, retries, exit codes
6. Local servers, env vars and plugins
7. Visual testing to SmartUI
8. Worked example (GitHub Actions)
9. Gotchas and unverified

## 1. Fingerprints

Grep for: `--record`, `--key`, `CYPRESS_RECORD_KEY`, `projectId` in `cypress.config.*` or `cypress.json`, `--parallel`, `--group`, `--ci-build-id`, `--tag`, `--auto-cancel-after-failures`, `cypress-io/github-action` with `record: true`, `cypress run` in CI, `cypress.env.json`, `cy.percySnapshot`, `cy.eyesOpen`, `cy.eyesCheckWindow`.

## 2. Target choice

| Target | What it means |
|---|---|
| Grid via `lambdatest-cypress-cli` | One CI job runs `npx lambdatest-cypress run`; specs execute on TestMu AI browsers, `parallels` at a time; results in the TestMu AI dashboard. Smallest change. |
| HyperExecute | `hyperexecute.yaml` with `cypress: true` and `cypressOps`; HyperExecute VMs run the specs with `autosplit` and `concurrency`; see `hyperexecute.md`. |

Cypress Cloud recording is removed in both cases (migration policy). Remove `--record`, `--key`, `CYPRESS_RECORD_KEY` and, unless the team asks to keep it for a transition, `projectId`. Cypress Cloud features with no TestMu AI counterpart (Test Replay, spec prioritisation by flake history, branch review) go in the summary as gaps.

## 3. CLI flag mapping

| `cypress run` | `lambdatest-cypress run` |
|---|---|
| `--record --key <k>` | drop |
| `--parallel` | `--parallels N` / `run_settings.parallels` |
| `--group <name>` | `--bn` / `run_settings.build_name` |
| `--ci-build-id <id>` | append to the build name: `--bn "e2e-<id>"` |
| `--tag a,b` | `-t a,b` / `run_settings.tags` (array, at most 15 tags of 50 characters) |
| `--browser chrome` | `--brs "Windows 11:Chrome:latest"` / `browsers[]` |
| `--headed` / `--headless` | `--headless` / `run_settings.headless` |
| `--spec "cypress/e2e/**/*.cy.js"` | `-s` / `run_settings.specs` |
| `--config-file cypress.config.ts` (Cypress 10+) | `--cy="--config-file cypress.config.ts"` (the CLI rejects `cypress_config_file` and `--ccf` for Cypress 10+) |
| `--config-file cypress.json` (Cypress 9 and below) | `run_settings.cypress_config_file` / `--ccf` |
| `--env a=1,b=2` (Cypress env vars) | `--envs a=1,b=2` / `run_settings.envs` (the CLI's `--env` selects the LambdaTest environment, not Cypress env vars) |
| OS env vars read by `cypress.config` | `--sys-envs` |
| `--config video=false` | `run_settings.video: false` |
| `--reporter junit --reporter-options ...` | `run_settings.reporter_config_file` (default `base_reporter_config.json`, mochawesome-based); there is no `--reporter` flag |
| `--project ./sub` | run the CLI from that directory |
| `--auto-cancel-after-failures`, `--runner-ui`, `--port`, `--quiet`, `--no-exit` | drop |

`--cy` passes extra flags to `cypress run`; it blocks `--spec`, `--browser`, `-b`, `--no-exit`, `--parallel`, `-p`, `--port`, `--headed`, `--help`, `-h`.

## 4. lambdatest-config.json

```
npm i -D lambdatest-cypress-cli
npx lambdatest-cypress init
```
Then fill (Cypress 10+):
```json
{
  "browsers": [
    { "browser": "Chrome", "platform": "Windows 11", "versions": ["latest"] },
    { "browser": "MicrosoftEdge", "platform": "Windows 11", "versions": ["latest"] }
  ],
  "run_settings": {
    "build_name": "checkout-e2e",
    "parallels": 4,
    "specs": "./cypress/e2e/**/*.cy.js",
    "ignore_files": "",
    "npm_dependencies": { "cypress": "13.13.0", "@faker-js/faker": "8.4.1" },
    "headless": false,
    "network": true,
    "video": true,
    "useNodeVersion": "20",
    "reporter_config_file": "base_reporter_config.json"
  },
  "tunnel_settings": { "tunnel": false, "tunnel_name": null }
}
```
Rules: `npm_dependencies` lists everything `cypress/support` and the specs import (copy from `package.json` `devDependencies`); Cypress 9 and below add `"cypress_config_file": "cypress.json"`; `browsers[].platform` is a full OS string; Node runtime via `useNodeVersion` (`18`, `20`, `22`). Leave `lambdatest_auth` out of the file: the CLI reads `LT_USERNAME`/`LT_ACCESS_KEY` from the environment (or `.env`) only when the block is missing or still holds the exact default placeholder `<Your LambdaTest username>`; any other placeholder is sent as the real username. JSON values are sent literally (no `${VAR}` expansion), so pass per-run values on the command line: `--user $LT_USERNAME --ak $LT_ACCESS_KEY --bn "e2e-$RUN_ID" --tname "$TUNNEL"`.

## 5. Parallelism, grouping, retries, exit codes

Cypress Cloud's `--parallel` splits specs across CI machines; `parallels` runs N specs at a time on TestMu AI browsers from one CI job, so the CI matrix of N runners collapses to one job (or move to HyperExecute `autosplit` for time-balanced splitting). `retries` in `cypress.config` keep working. `--group` + `--ci-build-id` -> one shared build name. Always run with `--sync=true --eof=true`. Boolean flags take a value: the CLI defines them as strings and compares with `"true"` (set_args.js), so a bare `--sync` or `--eof` counts as false, the run goes async and exits 0 on failures, turning red builds green. Same for `--tun=true`, `--headless=true`, `--net=true`.

## 6. Local servers, env vars and plugins

- `baseUrl: http://localhost:3000` with a server started in CI (`start-server-and-test`, `wait-on`): keep the server start and pass `--tun=true --tname $RUN_ID` (or `tunnel_settings: { "tunnel": true, "tunnel_name": "..." }`). The CLI starts and stops the tunnel itself (`autostart` defaults to true); do not also launch the LT binary, or two tunnels share one name. Use `--autostart=false` only when a tunnel is already running under that name. `geo_location` must be empty when the tunnel is on.
- `cypress.env.json` is uploaded with the project; pass secrets through `--envs` / `--sys-envs` instead.
- `setupNodeEvents` plugins that shell out or need OS packages must be npm-installable; otherwise mark them `TODO(testmu-migration)` and list them as a gap.
- `cypress-io/github-action` -> plain `run: npx lambdatest-cypress run --sync=true --eof=true ...` (keep `actions/setup-node` and `npm ci`).

## 7. Visual testing to SmartUI

Pick one SmartUI flow per suite:
- CLI hooks flow: `cy.screenshot('home')` captures, with `run_settings.smart_ui: { "project": "checkout", "build": "...", "baseline": false }` or `--vip checkout --vib <build> --vibase`.
- SDK flow: `npm i -D @lambdatest/cypress-driver`, `import '@lambdatest/cypress-driver'` in `cypress/support/e2e.js`, `cy.smartuiSnapshot('home')`, run with `npx smartui --config .smartui.json exec -- npx cypress run` and `PROJECT_TOKEN`.
`cy.percySnapshot` and Applitools `cy.eyesCheckWindow` calls map to either flow; seed baselines with a first run.

## 8. Worked example (GitHub Actions)

Before:
```yaml
strategy: { matrix: { containers: [1, 2, 3, 4] } }
steps:
  - uses: cypress-io/github-action@v6
    with: { record: true, parallel: true, group: 'e2e', browser: chrome, start: npm start, wait-on: 'http://localhost:3000' }
    env: { CYPRESS_RECORD_KEY: ${{ secrets.CYPRESS_RECORD_KEY }} }
```
After:
```yaml
steps:
  - uses: actions/setup-node@v4
    with: { node-version: 20 }
  - run: npm ci
  - run: npm start &
  - run: npx wait-on http://localhost:3000
  - run: npx lambdatest-cypress run --sync=true --eof=true --user "$LT_USERNAME" --ak "$LT_ACCESS_KEY" --bn "e2e-${GITHUB_RUN_ID}" --tun=true --tname "gh-${GITHUB_RUN_ID}" --parallels 4
    env: { LT_USERNAME: ${{ secrets.LT_USERNAME }}, LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }} }
```
Four containers become one job with `--parallels 4`; `CYPRESS_RECORD_KEY` is deleted from secrets.

## 9. Gotchas and unverified

- Browsers and platforms: TestMu Cypress runs Chrome, Edge, Firefox and Webkit on Windows 10/11 and macOS. Electron (the Cypress default) and Linux are not listed: map Electron to Chrome and Linux to Windows 11, and say so in the summary.
- Lockfile: running the CLI through `npx -p lambdatest-cypress-cli@<version> lambdatest-cypress run ...` works without touching the lockfile; prefer adding it to `devDependencies` and regenerating the lockfile when installs are possible.

- Everything under the project root is uploaded; exclude large or secret files with `run_settings.ignore_files`.
- Component testing (`testingType: component`, `cypress run --component`): the `lambdatest-cypress-cli` source (3.0.51) has no component-testing support; keep component tests running locally in CI and list them as a gap.
- `--cy="--config-file cypress.config.ts"` passes the string through unchanged, and for Cypress 10+ the CLI rejects `cypress_config_file`/`--ccf` and tells you to use `--cy` (validate.js). Whether the remote side accepts every `cypress run` flag is decided by a server-side blocklist at run time; check the first run's log.
- Sources: docs.cypress.io (cloud/get-started/setup, app/reference/command-line); TestMu docs run-settings, cypress-cli-commands, smart-ui-cypress, smartui-cypress-sdk, supported-cypress-versions; lambdatest-cypress-cli 3.0.51 source (validate.js, set_args.js, run.js, index.js).
