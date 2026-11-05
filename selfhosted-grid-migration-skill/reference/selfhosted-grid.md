# Self-hosted grids and local runners to TestMu AI

Read this when tests run on docker-selenium, a hand-rolled Selenium Grid, Selenoid, Aerokube Moon, Zalenium (archived), local Playwright/Puppeteer/Cypress/TestCafe, or local Appium. The job is to add a cloud target without breaking local runs.

Contents
1. Fingerprints
2. Selenium Grid / docker-selenium
3. Selenoid
4. Moon
5. Local Playwright and Puppeteer
6. Local Cypress
7. Local TestCafe
8. Local Appium
9. Keeping local and cloud switchable
10. Parallelism: from docker-compose scaling to HyperExecute

## 1. Fingerprints

`localhost:4444`, `127.0.0.1:4444`, `selenium-hub:4444`, `/wd/hub`, `SELENIUM_REMOTE_URL`, `GRID_URL`, `HUB_URL`, `selenium/standalone-chrome`, `selenium/hub`, `selenium/node-chrome`, `SE_EVENT_BUS_HOST`, `SE_NODE_MAX_SESSIONS`, `selenoid:options`, `enableVNC`, `enableVideo`, `browsers.json`, `moon:options`, `moon.example.com`, `aerokube`, `zalenium`, `chromium.launch(`, `puppeteer.launch(`, `cypress run` without a cloud CLI, `appium` server start commands, `4723`.

## 2. Selenium Grid / docker-selenium

Hub `http://localhost:4444` or `http://localhost:4444/wd/hub` -> `https://hub.lambdatest.com/wd/hub` with `LT:Options`. Grid 4 accepts caps without a vendor block; TestMu needs `LT:Options` for anything beyond `browserName`. Minimum addition:

```json
{ "browserName": "chrome", "browserVersion": "latest",
  "LT:Options": { "username": "${LT_USERNAME}", "accessKey": "${LT_ACCESS_KEY}", "platformName": "Windows 11", "build": "${CI_BUILD}", "name": "${TEST_NAME}", "w3c": true } }
```

| Grid construct | TestMu |
|---|---|
| `selenium/standalone-chrome` single node | one session per test, no infra |
| `docker-compose` hub + `node-chrome` + `node-firefox` with `SE_NODE_MAX_SESSIONS` | plan concurrency; HyperExecute `concurrency` for orchestration |
| `SE_SCREEN_WIDTH`/`SE_SCREEN_HEIGHT` (default 1920x1080), `SE_SCREEN_DEPTH`, `SE_SCREEN_DPI` | `resolution: "1920x1080"` |
| `SE_NODE_OVERRIDE_MAX_SESSIONS`, `SE_START_VNC`, `SE_VNC_NO_PASSWORD` | drop |
| `selenium/video` sidecar | `video: true` (default) |
| noVNC on `7900` | TestMu live view in dashboard |
| `--shm-size`, container env, `SE_OPTS` | drop |
| `goog:chromeOptions.args` (`--headless`, `--no-sandbox`, `--disable-dev-shm-usage`) | keep `goog:chromeOptions` for real flags; remove sandbox/shm flags (container-only) |
| hostnames resolvable only inside the compose network (`app:3000`) | LT Tunnel with `--dns` or `--allowHosts`, caps `tunnel: true` |
| self-signed certs | `acceptInsecureCerts: true` |

Grid `/status` health checks in CI -> drop.

## 3. Selenoid

| `selenoid:options` | TestMu |
|---|---|
| `enableVNC` | drop (live view always on) |
| `enableVideo`, `videoName`, `videoScreenSize`, `videoFrameRate` | `video: true` |
| `enableLog`, `logName` | `verboseWebDriverLogging` / `console` |
| `name` | `name` |
| `sessionTimeout` (Go duration string: `"1m"`, `"30m"`) | `idleTimeout` in seconds (`"1m"` -> 60) |
| `videoCodec`, `skin` | drop |
| `dnsServers` | LT tunnel `--dns` |
| `additionalNetworks` | LT tunnel to reach those networks |
| `timeZone` (IANA) | `timezone` (UTC offset) |
| `env` | drop; set in test code |
| `hostsEntries` | tunnel `--dns` |
| `applicationContainers` | tunnel to the app |
| `labels` | `tags` / `customData` |
| `screenResolution` | `resolution` |
| `s3KeyPattern` | drop |
| `browsers.json` image/version matrix | `browserName`/`browserVersion`/`platformName` matrix |

`./cm selenoid start` and the Selenoid UI on 8080 disappear from CI.

## 4. Moon

| Moon | TestMu |
|---|---|
| Selenium `https://moon.example.com/wd/hub` + `moon:options` | `https://hub.lambdatest.com/wd/hub` + `LT:Options` (key table below) |
| Playwright `wss://moon.example.com/playwright/<chromium|chrome|firefox|webkit>/playwright-<full client version>?name=x&enableVideo=true&env=...` | `wss://cdp.lambdatest.com/playwright?capabilities=<encoded {browserName, browserVersion, LT:Options{name, video}}>` with `browserName` `pw-chromium`/`Chrome`/`pw-firefox`/`pw-webkit` |
| `moon:options.name` | `name` |
| `moon:options.enableVideo`, `videoName`, `pattern` (`s3KeyPattern`) | `video: true` |
| `moon:options.enableHAR` | `network: true` |
| `moon:options.screenResolution` | `resolution` |
| `moon:options.sessionTimeout` (duration string) | `idleTimeout` (seconds) |
| `moon:options.env` (incl. `TZ=...`) | `timezone` (UTC offset) for TZ; other env drop |
| `moon:options.hosts` | LT tunnel `--dns` |
| `moon:options.nameservers` | LT tunnel `--dns` |
| `moon:options.labels` | `tags` / `customData` |
| `moon:options.logLevel` | `verboseWebDriverLogging` (approximate) |
| `moon:options.enableAudio`, `mobileDevice`, `windowManager`, `autoSelectClientCerts` | drop (list `mobileDevice` emulation as a gap; use real devices instead) |
| Puppeteer `wss://moon.example.com/devtools/chrome` | `wss://cdp.lambdatest.com/puppeteer?capabilities=...` |
| Cypress `@aerokube/cypress-moon` `cypress-moon https://moon.example.com/cypress/chrome` | `lambdatest-cypress-cli` with `lambdatest-config.json` |
| `additionalFonts`, `context` | drop |
| No auth | add `LT_USERNAME`/`LT_ACCESS_KEY` |

Moon's Playwright URL encodes browser and the exact client version in the path (the client must match); TestMu encodes everything in the `capabilities` query parameter. Moon uses Playwright's own protocol (`browserType.connect`), which TestMu also uses, so the call site stays `chromium.connect(...)`.

## 5. Local Playwright and Puppeteer

`chromium.launch({ headless })` becomes a cloud connection. For Playwright Test, do not edit every spec: add the canonical `lambdatest-setup.js` fixture from `testmu-target.md` §3 (it overrides the test-scoped `page` fixture, connects per test, keeps `baseURL` and other `use` options, reports `setTestStatus`, and leaves local projects untouched), then change one import per spec (`import { test, expect } from './lambdatest-setup'`, a codemod over `from '@playwright/test'` handles the suite).

Map `playwright.config` projects to TestMu project names: `devices['Desktop Chrome']` or `channel: 'chrome'` -> `Chrome:latest:Windows 11@lambdatest`; `devices['Desktop Firefox']` -> `pw-firefox:latest:Windows 11@lambdatest`; `devices['Desktop Safari']` -> `pw-webkit:latest:macOS Sonoma@lambdatest`; `devices['Pixel 5']` -> `Pixel 5:13:android@lambdatest` (real Android device through `_android.connect`, `platformName: android`, `isRealMobile: true`). Keep `workers` at or under plan concurrency. No-code alternative: `@lambdatest/playwright-node-sdk` + `lambdatest.yml`.

Python, Java and C# Playwright: same `connect` swap; see `testmu-target.md` §3 and `languages.md` §2 for the encoding helper.

Puppeteer `puppeteer.launch()` -> `puppeteer.connect({ browserWSEndpoint: 'wss://cdp.lambdatest.com/puppeteer?capabilities=...' })`; call `browser.close()` at the end so the session ends.

Playwright through `SELENIUM_REMOTE_URL` (experimental Selenium Grid mode, Chrome and Edge only) -> use the CDP connect path instead.

## 6. Local Cypress

`npx cypress run --browser chrome --spec ...` -> `npx lambdatest-cypress init` once, fill `lambdatest-config.json` (`browsers`, `run_settings.specs`, `parallels`, `npm_dependencies` from package.json), then `npx lambdatest-cypress run`. Cypress config file stays untouched; `baseUrl` pointing at localhost needs `tunnel_settings.tunnel: true`. `cypress.env.json` values -> `--env` flag or `run_settings`. Plugins that need OS binaries must be installable via npm (`npm_dependencies`).

## 7. Local TestCafe

`testcafe chrome tests/` -> `npm i -D testcafe-browser-provider-lambdatest`, `testcafe "lambdatest:Chrome@latest:Windows 11" tests/`. Multiple browsers: comma-separated aliases. `chrome:headless` has no cloud meaning; drop. `--hostname`/`--ports` for local app access -> LT Tunnel with `LT_TUNNEL_NAME`.

## 8. Local Appium

`http://127.0.0.1:4723` (or `/wd/hub`) with `udid`/emulator `avd` caps -> `https://USER:KEY@mobile-hub.lambdatest.com/wd/hub`; replace `udid`/`avd` with `deviceName` + `platformVersion`, set `isRealMobile` (`true` for real devices, `false` for emulators/simulators), replace local `app` paths with `lt://` ids after upload (`/app/upload/realDevice` or `/virtualDevice`). `appium` server start commands and driver installs (`appium driver install uiautomator2`) leave CI. `newCommandTimeout`, `noReset`, `fullReset`, `appPackage`, `appActivity`, `bundleId`, `autoGrantPermissions` carry over.

## 9. Keeping local and cloud switchable

Most teams want `npm test` to keep working locally. Pattern: one driver/browser factory reading `TARGET=local|testmu` (or reuse an existing `GRID_URL` switch). Local branch keeps `localhost:4444` or `launch()`; cloud branch builds `LT:Options` and the TestMu URL. Status hooks (`lambda-status=`) must be no-ops locally; wrap them in `if (isCloud)`. Put `LT_USERNAME`/`LT_ACCESS_KEY` in CI secrets, never in the repo.

## 10. Parallelism

docker-compose `deploy.replicas` / `SE_NODE_MAX_SESSIONS` / Selenoid `limit` -> two options: (a) keep the existing runner (pytest-xdist, TestNG `parallel`, Playwright `workers`, Cypress `parallels`) and let TestMu run that many concurrent sessions; (b) HyperExecute `hyperexecute.yaml` with `autosplit: true` and `concurrency: N`, which also removes the CI runner's need to host the test process. Option (b) is the one to propose when the grid was also the thing that ran tests at scale.

Sources at research time (26 Oct 2026): github.com/SeleniumHQ/docker-selenium, aerokube.com/selenoid/latest, aerokube.com/moon/latest, github.com/zalando/zalenium, playwright.dev/docs/selenium-grid, playwright.dev/docs/api/class-browsertype, playwright.dev/docs/test-projects, docs.cypress.io/app/reference/command-line, testcafe.io browsers guide.
