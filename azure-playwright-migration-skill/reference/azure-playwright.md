# Azure Playwright Workspaces (Microsoft Playwright Testing) to TestMu AI

Read this when the source is Azure App Testing's Playwright Workspaces, or its predecessor Microsoft Playwright Testing (preview retired 8 March 2026): `playwright.service.config.ts`, `@azure/playwright`, `@azure/microsoft-playwright-testing`, `PLAYWRIGHT_SERVICE_URL`.

Contents
1. Fingerprints
2. How the service works and what replaces it
3. Option mapping
4. Two target shapes: CDP fixture vs the TestMu Playwright SDK
5. Auth and CI
6. Reporter and artifacts
7. Worked example (TypeScript, Playwright Test)
8. Gotchas and unverified

## 1. Fingerprints

Grep for: `playwright.service.config.ts` / `.js`, `@azure/playwright`, `createAzurePlaywrightConfig`, `ServiceOS`, `ServiceAuth`, `@azure/identity` next to Playwright, `DefaultAzureCredential`, `@azure/microsoft-playwright-testing`, `getServiceConfig`, `PLAYWRIGHT_SERVICE_URL`, `PLAYWRIGHT_SERVICE_ACCESS_TOKEN`, `PLAYWRIGHT_SERVICE_RUN_ID`, `api.playwright.microsoft.com`, `@azure/playwright/reporter`, `exposeNetwork`, `--config=playwright.service.config.ts`, `az login` in test CI, `runName`, `runId`.

## 2. How the service works and what replaces it

The service is a wrapper that makes Playwright Test connect each worker's browser to a remote Playwright server (`connect()`), keeps your `playwright.config.ts` as is, and adds a reporter that uploads results. TestMu's Browser Cloud exposes the same `connect()` surface at `wss://cdp.lambdatest.com/playwright?capabilities=...`, so the migration is: delete the Azure service config, add either a fixture that connects per project or the `@lambdatest/playwright-node-sdk`, and swap credentials. Specs do not change.

| Azure | TestMu |
|---|---|
| `playwright.service.config.ts` (`defineConfig(config, createAzurePlaywrightConfig(config, {...}))`) | `fixtures.ts` overriding `browser`, or `lambdatest.yml` via the SDK |
| `npx playwright test --config=playwright.service.config.ts --workers=20` | `npx playwright test --workers=<plan concurrency>` (fixture) or `npx playwright-node-sdk playwright test` (SDK) |
| remote browsers on Linux or Windows (`ServiceOS`) | TestMu cloud browsers on Windows and macOS (`LT:Options.platform`) |
| `exposeNetwork: '<loopback>'` (service browser reaches your localhost) | LT Tunnel + `tunnel: true`, `tunnelName` |
| Entra ID (`az login`) or access token | `LT_USERNAME` / `LT_ACCESS_KEY` |
| `@azure/playwright/reporter` (results in the Azure portal) | TestMu dashboard (automatic per session) plus any local reporter you keep |

## 3. Option mapping

| `createAzurePlaywrightConfig` / `getServiceConfig` option | TestMu |
|---|---|
| `os: ServiceOS.LINUX` | `platform: "Windows 11"` (Linux is not in TestMu's documented Selenium/Playwright desktop platforms, so use Windows; rendering differs from Linux) |
| `os: ServiceOS.WINDOWS` | `platform: "Windows 11"` |
| `runName`, `runId` | `build` |
| `connectTimeout` (older `timeout`) | drop (`chromium.connect` `timeout` option if you want one) |
| `exposeNetwork` | `tunnel: true` + `tunnelName` |
| `credential`, `serviceAuthType: ServiceAuth.ACCESS_TOKEN` | `user`/`accessKey` in `LT:Options` |
| `useCloudHostedBrowsers: false` | keep tests local (no TestMu caps) |
| `PLAYWRIGHT_SERVICE_URL` region endpoint | single `wss://cdp.lambdatest.com/playwright` |
| `--workers=20` (service max 50) | your plan's parallel sessions |
| `playwright.config.ts` `projects[].use.browserName: 'chromium'|'firefox'|'webkit'` | `browserName: 'pw-chromium'|'pw-firefox'|'pw-webkit'` (or `'Chrome'`/`'MicrosoftEdge'` branded) |
| `channel: 'chrome'` / `'msedge'` | `browserName: 'Chrome'` / `'MicrosoftEdge'` |
| `devices['Pixel 5']` etc. | `platform: 'android'`, `deviceName: 'Pixel 5'`, `platformVersion` (real device via Playwright) |

## 4. Two target shapes

Fixture (explicit, no extra service): use the canonical `lambdatest-setup.js` in `testmu-target.md` §3. It overrides the test-scoped `page` fixture (overriding `browser` is a bug: `browser` is worker-scoped, so the third argument is WorkerInfo, one TestMu session is shared by every test in a worker and per-test names and statuses are lost), connects per test with `chromium.connect` for desktop and `_android.connect` for Android, and passes `testInfo.project.use` to `newPage` so `baseURL`, viewport and `storageState` survive. Turn each Azure project into a TestMu project name:

| `playwright.config.ts` project | TestMu project name |
|---|---|
| `{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }` | `Chrome:latest:Windows 11@lambdatest` |
| `{ name: 'firefox', use: { ...devices['Desktop Firefox'] } }` | `pw-firefox:latest:Windows 11@lambdatest` |
| `{ name: 'webkit', use: { ...devices['Desktop Safari'] } }` | `pw-webkit:latest:macOS Sonoma@lambdatest` |
| `channel: 'msedge'` | `MicrosoftEdge:latest:Windows 11@lambdatest` |
| `devices['Pixel 7']` | `Pixel 7:14:android@lambdatest` (real device) |

Specs change one import: `import { test, expect } from './lambdatest-setup'`. Keep local projects (without `@lambdatest`) if the team runs locally; the fixture leaves them untouched. Read the Playwright version with `execSync('npx playwright --version')` (as the official sample does) rather than importing `package.json` with import attributes.

SDK (no spec changes): `npm i -D @lambdatest/playwright-node-sdk`, `npx playwright-node-sdk init` (writes `lambdatest.yml` with platforms, build and tunnel), `npx playwright-node-sdk playwright test`. Choose this when the team valued Azure's "no code change" property.

HyperExecute: if the team wants the whole run off their CI (Azure ran workers in the cloud), add `hyperexecute.yaml` per `hyperexecute.md` with `autosplit` over spec files and `concurrency` equal to the old `--workers`.

## 5. Auth and CI

Remove: `az login`, `azure/login` action, `AZURE_CLIENT_ID`/`AZURE_TENANT_ID`/`AZURE_SUBSCRIPTION_ID` federated credential steps for tests, `PLAYWRIGHT_SERVICE_URL`, `PLAYWRIGHT_SERVICE_ACCESS_TOKEN`, old-package `PLAYWRIGHT_SERVICE_OS`, `PLAYWRIGHT_SERVICE_EXPOSE_NETWORK_ENVIRONMENT_VARIABLE`, `PLAYWRIGHT_SERVICE_REPORTING_URL`, and the workflow's `permissions: id-token: write` if it existed only for Azure login.
Add: `LT_USERNAME`, `LT_ACCESS_KEY` secrets; if `exposeNetwork` was used, a step that downloads the LT binary and runs `./LT --user $LT_USERNAME --key $LT_ACCESS_KEY --tunnelName $GITHUB_RUN_ID &` before the tests, and `LT_TUNNEL_NAME=$GITHUB_RUN_ID`.
`npm uninstall @azure/playwright @azure/identity @azure/microsoft-playwright-testing`.

## 6. Reporter and artifacts

`reporter: [['html', { open: 'never' }], ['@azure/playwright/reporter']]` -> keep `html`/`junit`/`list`; drop the Azure reporter. Video, console, network and command logs come from the TestMu session (`video: true`, `network: true`, `console: true`) and are visible in the dashboard and REST API; Playwright traces (`trace: 'on-first-retry'`) still work locally through the connected browser.

## 7. Worked example

Before:
```ts
// playwright.service.config.ts
import { defineConfig } from '@playwright/test';
import { createAzurePlaywrightConfig, ServiceOS } from '@azure/playwright';
import { DefaultAzureCredential } from '@azure/identity';
import config from './playwright.config';
export default defineConfig(config, createAzurePlaywrightConfig(config, {
  exposeNetwork: '<loopback>', connectTimeout: 3 * 60 * 1000, os: ServiceOS.LINUX, credential: new DefaultAzureCredential(),
}));
```
CI: `npx playwright test --config=playwright.service.config.ts --workers=20`.

After: delete the file; add `tests/fixtures.ts` from §4; CI runs the LT tunnel then `npx playwright test --workers=10`; `playwright.config.ts` untouched except `use.baseURL` stays `http://localhost:3000` (reached through the tunnel).

## 8. Gotchas and unverified

- Azure ran browsers on Linux by default; TestMu runs on Windows/macOS. Font rendering and scrollbar widths differ, so visual snapshots (`toHaveScreenshot`) need re-baselining. SmartUI (`@lambdatest/playwright-driver`) is the TestMu visual option if the team wants cloud baselines.
- Playwright version: TestMu supports a range of client versions; set `playwrightClientVersion` from the installed package and check the supported list when upgrading.
- `--workers` above plan concurrency queues sessions; set `idleTimeout` if tests wait on slow fixtures.
- The Azure endpoint pattern is `wss://<region>.api.playwright.microsoft.com/playwrightworkspaces/<workspace-id>/browsers` (grep for it as a fingerprint). Azure setup came from `npm init @azure/playwright@latest`; remove what it generated.
- Unverified at research time (27 Oct 2026): `lambdatest.yml` key names for the SDK beyond what `init` generates; Linux availability on TestMu desktop.
- Sources: learn.microsoft.com azure/app-testing/playwright-workspaces (quickstart-run-end-to-end-tests, quickstart-automate-end-to-end-testing, how-to-manage-authentication, overview); TestMu playwright-testing, playwright-sample repo, playwright-node-sdk docs.
