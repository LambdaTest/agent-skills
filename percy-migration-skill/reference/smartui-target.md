# SmartUI target reference (TestMu AI)

Everything a migrated visual suite needs on the TestMu AI side. Source: TestMu AI docs repo (111 SmartUI pages), read 27 Oct 2026. Doc URLs are `https://www.testmuai.com/support/docs/<page>/`.

Contents
1. Credentials and project
2. Three ways to capture: SDK + `smartui exec`, hooks on the TestMu AI grid, CLI capture/upload
3. SDK per framework and language
4. `.smartui.json`
5. Per-snapshot options
6. CLI commands
7. Environment variables
8. Baselines, branches and approvals
9. Storybook, Figma, PDF, apps
10. CI and PR checks

## 1. Credentials and project

- Create a SmartUI project in the TestMu AI dashboard (type Web/CLI, Hooks, Storybook, App, Figma or PDF). The project gives a `PROJECT_TOKEN` (format `<number>#<uuid>`).
- `PROJECT_TOKEN` drives SDK and CLI runs; hooks runs on the grid use `LT_USERNAME`/`LT_ACCESS_KEY` plus the `smartUI.project` capability. `PROJECT_NAME` can be used instead of a token together with `LT_USERNAME`/`LT_ACCESS_KEY` (smartui-cli-env-variables).

## 2. Three ways to capture

| Mode | When | How |
|---|---|---|
| SDK + `smartui exec` | tests run anywhere (locally, CI, or on the TestMu AI grid); closest to Percy SDKs | install `@lambdatest/smartui-cli` and the framework driver package; call the snapshot function; run tests under `npx smartui --config .smartui.json exec -- <test command>` |
| Hooks on the grid | tests already run on TestMu AI Browser Cloud or Real Device Cloud; closest to Percy on Automate and App Percy on App Automate | capabilities `smartUI.project`, `smartUI.build`, `smartUI.baseline` (Selenium/Appium, inside `LT:Options`); `driver.executeScript("smartui.takeScreenshot=<name>")`; Playwright/Puppeteer use flat `smartUIProjectName`, `smartUIBuildName`, `smartUIBaseline` and `lambdatest_action: {"action":"smartui.takeScreenshot","arguments":{"screenshotName":"x","fullPage":true}}` |
| CLI capture / upload | static URLs, existing screenshot folders, PDFs, Storybook | `smartui capture urls.json`, `smartui upload ./dir`, `smartui upload-pdf ./pdfs`, `smartui storybook <url|dir>` |

## 3. SDK per framework and language

| Framework / language | Install | Import and call |
|---|---|---|
| Selenium JavaScript | `npm i -D @lambdatest/smartui-cli @lambdatest/selenium-driver` | `const { smartuiSnapshot } = require('@lambdatest/selenium-driver'); await smartuiSnapshot(driver, 'Home', options)` |
| Selenium Python | `pip install lambdatest-selenium-driver` + `npm i -D @lambdatest/smartui-cli` | `from lambdatest_selenium_driver import smartui_snapshot; smartui_snapshot(driver, "Home", options)` |
| Selenium Java | Maven `io.github.lambdatest:lambdatest-java-sdk` + smartui-cli | `SmartUISnapshot.smartuiSnapshot(driver, "Home", options)` |
| Selenium C# | NuGet `LambdaTest.Selenium.Driver` + smartui-cli | `SmartUISnapshot.CaptureSnapshot(driver, "Home", options)` |
| Selenium Ruby / Capybara | `gem install lambdatest-selenium-driver` + smartui-cli | `require 'lambdatest/selenium/driver'; Lambdatest::Selenium::Driver.smartui_snapshot(driver, "Home", options)` (module is `Lambdatest`, lowercase t; the docs page's `LambdaTest::` fails). Capybara: pass `page.driver.browser` |
| Playwright JavaScript/TypeScript | `npm i -D @lambdatest/smartui-cli @lambdatest/playwright-driver` | `const { smartuiSnapshot } = require('@lambdatest/playwright-driver'); await smartuiSnapshot(page, 'Home', options)` |
| Playwright Python | `pip install lambdatest-playwright-driver` + smartui-cli | `from lambdatest_playwright_driver import smartui_snapshot; smartui_snapshot(page, "Home")` |
| Playwright Java | `io.github.lambdatest:lambdatest-java-playwright-sdk` (official sample pom; `lambdatest-java-sdk` takes a WebDriver only) | `SmartUISnapshot.smartuiSnapshot(page, "Home", options)` |
| Puppeteer | `npm i -D @lambdatest/smartui-cli @lambdatest/puppeteer-driver` | `const { smartuiSnapshot } = require('@lambdatest/puppeteer-driver'); await smartuiSnapshot(page, 'Home')` |
| Cypress | `npm i -D @lambdatest/smartui-cli @lambdatest/cypress-driver@1.0.8` (the `latest` tag points at a beta); add `import '@lambdatest/cypress-driver'` to `cypress/support/e2e.js` | `cy.smartuiSnapshot('Home', options)` |
| WebdriverIO | `npm i -D @lambdatest/smartui-cli @lambdatest/wdio-driver` | `const { smartuiSnapshot } = require('@lambdatest/wdio-driver'); await smartuiSnapshot(browser, 'Home')` |
| TestCafe | `npm i -D @lambdatest/smartui-cli @lambdatest/testcafe-driver` | `const { smartuiSnapshot } = require('@lambdatest/testcafe-driver'); await smartuiSnapshot(t, 'Home')` |
| Appium Java (apps) | `lambdatest-java-sdk` | instance API: `SmartUIAppSnapshot s = new SmartUIAppSnapshot(); s.start(config); s.smartuiAppSnapshot(driver, "HomeScreen", config); s.stop();` run with plain `mvn test` (no `smartui exec`) |
| Appium other languages | hooks mode (`smartui.takeScreenshot=<name>` on the Real Device Cloud) | smartui-appium-hooks |
| Storybook | `npm i -D @lambdatest/smartui-storybook` (separate package; smartui-cli has no `storybook` command, and both install a `smartui` binary, so avoid a global smartui-cli in the same environment) | `npx smartui storybook <url|static-dir> --config .smartui-storybook.json`; create the config with `npx smartui config create` |
| KaneAI tests | Visual Comparison step | screenshots go to the linked SmartUI project |

Run every SDK suite under the CLI: `PROJECT_TOKEN=... npx smartui --config .smartui.json exec -- <test command>`. Without `exec` (no local SmartUI server) the SDK calls throw "Cannot find SmartUI server." (JS, Python, Ruby; Cypress too under `cypress run`), so a suite that sometimes runs without SmartUI needs its own switch (an env var checked before the call).

## 4. `.smartui.json`

Create with `npx smartui config:create .smartui.json`:
```json
{
  "web": {
    "browsers": ["chrome", "firefox", "safari", "edge"],
    "viewports": [[1920], [1366], [1028]]
  },
  "mobile": {
    "devices": ["iPhone 14", "Galaxy S24"],
    "fullPage": true,
    "orientation": "portrait"
  },
  "waitForTimeout": 1000,
  "waitForPageRender": 50000,
  "enableJavaScript": false,
  "allowedHostnames": ["cdn.example.com"]
}
```
Other keys: `customViewports` (per-browser `{ browser, viewport: { width, height } }`), `lazyLoadConfiguration` (`enabled`, `jumpBackToTop`, `scrollDelay`, `scrollStep`), `basicAuthorization`, `cookies`, `requestHeaders`, `ignoreHTTPSErrors`, `cliEnableJavaScript`, `scrollTime`, `tunnel`, `useGlobalCache`, `skipBuildCreation`, `userAgent`, `smartIgnore`, `ignoreType`, `customCSS` (top level). The smartui-cli schema rejects unknown keys (`additionalProperties: false`), so never put a `storybook` block in the `.smartui.json` used by `exec`; Storybook settings (`browsers`, `viewports`, `include`, `exclude`, `waitForTimeout`, `backgroundTheme`, `useGlobals`, `failOn`, `onlyChanged`, `chunkSize`, `customViewports`) live in the separate smartui-storybook config file. Mobile `devices` use SmartUI device names (`iPhone 15 Pro`, `Galaxy S23`, `iPad Air (2022)`; list on smartui-sdk-config-options).

## 5. Per-snapshot options

Passed as the third argument (`options`):
```js
{
  ignoreDOM: { id: ['ad-banner'], class: ['clock'], cssSelector: ['.price'], xpath: ['//footer'] },
  selectDOM: { cssSelector: ['#main'] },     // compare only these regions
  element: { cssSelector: '#checkout' },     // capture one element
  customCSS: '.spinner { display: none }',   // inject CSS before capture (smartui-custom-css)
  web: { browsers: ['chrome'], viewports: [[1280, 800]] },
  mobile: { devices: ['iPhone 15'], fullPage: true },
  sync: true                                 // wait for the comparison result (smartui-sdk-fetch-results)
}
```
Hooks-mode equivalents: `smartUI.options` capability, `smartUI.captureDom`, `smartUI.cropStatusBar`, `smartUI.cropFooter` (apps), and `smartui.takeScreenshot` with an options object. Comparison behaviour (project settings): mismatch thresholds, SmartIgnore, layout comparison, ignore colours, freeze animations, region ignore, bounding boxes.

## 6. CLI commands

`smartui exec [-P port] [--buildName n] [--fetch-results [file]] [--config f] [--userName u --accessKey k] -- <cmd>`; `smartui exec:start`, `exec:stop`, `exec:ping`, `exec:pingTest`; `smartui capture <urls.json> [--parallel N] [--force]`; `smartui upload <dir> [--ignoreResolutions] [--files jpg,png] [--removeExtensions] [--ignoreDir a,b]`; `smartui upload-pdf <dir|file> [--markBaseline] [--pdfNames]`; `smartui config:create`, `config:create-web-static`, `config:create-figma`, `config:create-figma-web`, `config:create-figma-app`; `smartui upload-figma`, `upload-figma-web`, `upload-figma-app`; `smartui merge branch`, `smartui merge build`. Global flags `--markBaseline`, `--baselineBranch`, `--baselineBuild` set baselines from the CLI (there is no approve verb). Sharing one `--buildName` across parallel shards appends to the same build. Storybook is the separate `@lambdatest/smartui-storybook` CLI (`smartui storybook <url|dir>`, `--fail-on`, `--only-changed`).

## 7. Environment variables

`PROJECT_TOKEN`, `PROJECT_NAME`, `LT_USERNAME`, `LT_ACCESS_KEY`, `BASELINE_BRANCH`, `CURRENT_BRANCH`, `SMARTUI_FAIL_ON` (Storybook CLI only: `none`, `unreviewed`, `changes`, `rejected`; exit code 4), `SMARTUI_GIT_INFO_FILEPATH`, `SMARTUI_DO_NOT_USE_CAPTURED_COOKIES`, `SMARTUI_SERVER_ADDRESS`, `HTTP_PROXY`/`HTTPS_PROXY` (or `SMARTUI_HTTP_PROXY`/`SMARTUI_HTTPS_PROXY`/`SMARTUI_API_PROXY`), `SMARTUI_API_SKIP_CERTIFICATES`, `LT_SDK_DEBUG`, `LT_SDK_SKIP_EXECUTION_LOGS`.

## 8. Baselines, branches and approvals

- First build in a project becomes the baseline. With Git: set the baseline branch in project settings or `BASELINE_BRANCH`; builds on that branch compare with its latest approved build; builds on other branches compare with the baseline branch; approving all screenshots on the baseline branch promotes the build to the new baseline. `CURRENT_BRANCH` overrides the detected branch (detached-HEAD CI).
- Missing screenshots on the baseline branch with no visual change: build auto-approved and marked Incomplete.
- Merges: `smartui merge branch` / `merge build`. Approval workflow, smart comments, draw-on-UI, root-cause analysis, Visual AI agent are dashboard features.

## 9. Storybook, Figma, PDF, apps

- Storybook: `@lambdatest/smartui-storybook`, `npx smartui storybook http://localhost:6006|./storybook-static|https://hosted --config .smartui-storybook.json`; CI gating via `failOn`/`--fail-on`; `onlyChanged`. Story-level rename or skip parameters are not read; use `include`/`exclude` patterns.
- Figma: `config:create-figma*` + `upload-figma*` compare designs with web or app builds.
- PDF: `smartui upload-pdf`, PDF API upload, Java PDF SDK.
- Apps: Appium hooks on Real Device Cloud (`smartUI.project` + `smartui.takeScreenshot=<name>`), Appium Java SDK, Espresso visual regression, Maestro (HyperExecute) SDK.

## 10. CI and PR checks

Wrap the test command: `npx smartui --config .smartui.json exec -- npm test`, with `PROJECT_TOKEN` as a CI secret. GitHub app integration posts PR status checks (smartui-github-app-integration); GitLab PR checks for exec and hooks modes; pages exist for Azure, Bitbucket, Buildkite, CircleCI, GitHub Actions, GitLab, Netlify, Semaphore, Travis. Gate an `exec` job on visual changes with `--fetch-results results.json` and a script (or `sync: true`); Storybook jobs gate with `failOn` / `SMARTUI_FAIL_ON` (exit code 4).
