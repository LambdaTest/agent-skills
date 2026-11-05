# Percy (BrowserStack) to SmartUI mapping

Every Percy construct and its SmartUI equivalent. Percy facts come from the Percy source repos (`github.com/percy/cli` packages and each SDK README), read 27 Oct 2026; SmartUI facts are in `smartui-target.md`.

Contents
1. Fingerprints
2. Project types and tokens
3. CLI commands
4. Environment variables
5. `.percy.yml` to `.smartui.json`
6. Snapshot options
7. SDK calls per framework and language
8. Percy on Automate and App Percy (screenshot mode)
9. Storybook, static sites, uploads
10. Review workflow, baselines, branches, CI gating
11. Gaps

## 1. Fingerprints

Grep for: `@percy/` (any package), `percy exec`, `percy snapshot`, `percy upload`, `percy app:exec`, `percy storybook`, `percy build:`, `PERCY_TOKEN`, `PERCY_BRANCH`, `PERCY_TARGET_BRANCH`, `PERCY_PARALLEL_TOTAL`, `PERCY_PARALLEL_NONCE`, `PERCY_PARTIAL_BUILD`, `PERCY_` (any), `.percy.yml`, `.percy.yaml`, `.percy.json`, `.percy.js`, `.percyrc`, `percy.config.js`, `"percy"` key in package.json, `percySnapshot`, `percyScreenshot`, `percy_snapshot`, `percy_screenshot`, `cy.percySnapshot`, `page.percy_snapshot`, `Percy.Snapshot`, `Percy.Screenshot`, `io.percy`, `percy-java-selenium`, `percy-playwright-java`, `percy-appium-app`, `PercyIO.Selenium`, `PercyIO.Playwright`, `percy-selenium` (pip), `percy-playwright` (pip), `percy-capybara`, `AppPercy`, browserstack.yml `percy: true` / `percyCaptureMode`, wdio `percy`/`percyCaptureMode`/`percyOptions`.

## 2. Project types and tokens

| Percy | SmartUI |
|---|---|
| Web project, token `web_...`: Percy renders captured DOM in its own browsers (set in project settings or config) | Web/CLI project with `PROJECT_TOKEN`; SmartUI renders captured DOM in `.smartui.json` `web.browsers` x `viewports` (SDK + `smartui exec`) |
| Automate project, token `auto_...`: screenshots from real BrowserStack Automate sessions (`percyScreenshot`) | Hooks project: screenshots from TestMu AI grid sessions (`smartUI.project` cap + `smartui.takeScreenshot`), or SDK mode |
| App project, token `app_...`: App Percy screenshots from App Automate (`percy app:exec`) | App/Hooks project: Appium hooks on the Real Device Cloud, or the Appium Java SDK |
| Generic/screenshot project, token `ss_...`: uploaded images (`percy upload`) | CLI project: `smartui upload <dir>` |
| `PERCY_TOKEN` | `PROJECT_TOKEN` (one per SmartUI project; or `PROJECT_NAME` + `LT_USERNAME`/`LT_ACCESS_KEY`) |

## 3. CLI commands

| Percy (`@percy/cli`) | SmartUI (`@lambdatest/smartui-cli`) |
|---|---|
| `npx percy exec -- <cmd>` | `npx smartui --config .smartui.json exec -- <cmd>` |
| `percy exec:start` / `exec:stop` / `exec:ping` | `smartui exec:start` / `exec:stop` / `exec:ping` |
| `percy snapshot <dir|sitemap|snapshots.yml>` | `smartui capture urls.json` (web static config from `smartui config:create-web-static`) |
| `percy upload <dir>` | `smartui upload <dir>` (`--ignoreResolutions`, `--files`, `--removeExtensions`, `--ignoreDir`) |
| `percy app:exec -- <cmd>` | Appium hooks on the Real Device Cloud (no wrapper needed) or the Appium Java `SmartUIAppSnapshot` API under plain `mvn test` |
| `percy storybook <url|dir>` (`@percy/storybook`) | `@lambdatest/smartui-storybook`: `npx smartui storybook <url|dir> --config .smartui-storybook.json` |
| `percy config:create` / `config:validate` / `config:migrate` | `smartui config:create` (and `config:create-web-static`, `config:create-figma*`) |
| `percy build:finalize` (with `PERCY_PARALLEL_TOTAL=-1`) | not needed: one `smartui exec` per build; use the same `--buildName` in every shard (it appends to one build) |
| `percy build:wait` | `smartui exec --fetch-results results.json` (then fail the job from the results in a script) or `sync: true` per snapshot |
| `percy build:approve` / `build:reject` / `build:unapprove` / `build:delete` | dashboard approval workflow; no CLI approve verb, but `--markBaseline`, `--baselineBranch`, `--baselineBuild` set baselines from the CLI |
| `percy build:id` | `--fetch-results` output |
| `percy doctor` | `smartui exec:pingTest` and `LT_SDK_DEBUG=true` |
| (Figma) | `smartui upload-figma*` (no Percy equivalent) |
| (PDF) | `smartui upload-pdf` (no Percy equivalent) |

## 4. Environment variables

| Percy | SmartUI |
|---|---|
| `PERCY_TOKEN` | `PROJECT_TOKEN` |
| `PERCY_BRANCH` | `CURRENT_BRANCH` |
| `PERCY_TARGET_BRANCH` | `BASELINE_BRANCH` (or set the baseline branch in project settings) |
| `PERCY_COMMIT`, `PERCY_TARGET_COMMIT`, `PERCY_PULL_REQUEST` | `SMARTUI_GIT_INFO_FILEPATH` (git info JSON) when CI hides git data; otherwise detected |
| `PERCY_PARALLEL_TOTAL`, `PERCY_PARALLEL_NONCE`, `PERCY_PARTIAL_BUILD` | no equivalent; run one `smartui exec` per build or share `--buildName` (verify) |
| `PERCY_ENABLE=0` | no direct equivalent: without `smartui exec` the SDK calls throw "Cannot find SmartUI server."; guard the calls with your own env var (e.g. `if (process.env.SMARTUI_ENABLED)`) |
| `PERCY_SERVER_ADDRESS` | `SMARTUI_SERVER_ADDRESS` |
| `PERCY_LOGLEVEL=debug` | `LT_SDK_DEBUG=true` |
| `PERCY_EXIT_WITH_ZERO_ON_ERROR` | `smartui exec` does not fail the test command on visual diffs; add `--fetch-results` and a script to gate |
| `PERCY_BROWSER_EXECUTABLE`, `PERCY_GZIP`, `PERCY_PAC_FILE_URL`, `PERCY_PAGE_LOAD_TIMEOUT`, `PERCY_NETWORK_IDLE_WAIT_TIMEOUT`, `PERCY_CDP_TIMEOUT`, `PERCY_SKIP_GIT_CHECK`, `PERCY_DOMAINS`, `PERCY_PRIORITY` | drop; network idle and page wait map to `waitForPageRender`/`waitForTimeout`; proxies to `HTTP_PROXY`/`HTTPS_PROXY` |

## 5. `.percy.yml` to `.smartui.json`

| Percy config | `.smartui.json` |
|---|---|
| `version: 2` | none |
| `snapshot.widths: [375, 1280]` | `web.viewports: [[375], [1280]]` (and `web.browsers`) |
| `snapshot.minHeight` | none; SmartUI captures full page; use `customViewports` with height when a fixed height mattered |
| `snapshot.percyCSS` | per-snapshot `customCSS` (or a project-level custom CSS, smartui-custom-css) |
| `snapshot.enableJavaScript` | `enableJavaScript` |
| `snapshot.cliEnableJavaScript` | `cliEnableJavaScript` |
| `snapshot.disableShadowDOM` / `forceShadowAsLightDOM` | smartui-shadow-dom settings |
| `snapshot.enableLayout` | layout comparison mode (project setting or smartui-layout-comparison) |
| `snapshot.scope` | per-snapshot `selectDOM` or `element` |
| `snapshot.responsiveSnapshotCapture` | multiple `viewports`; responsive DOM capture (smartui-cli-responsive-dom) |
| `snapshot.fullPage`, `scaleToFit` | `mobile.fullPage`; web is full page by default |
| `snapshot.freezeAnimatedImage`, `freezeImageBySelectors/Xpaths` | freeze animations (smartui-freeze-animations) |
| `snapshot.readiness` (`domStability`, `networkIdleWindowMs`, `readySelectors`, ...) | `waitForPageRender`, `waitForTimeout`, lazy-load config |
| `snapshot.labels`, `testCase` | build name / project tags; group by test case (smartui-group-by-test-cases) |
| `snapshot.browsers` | `web.browsers` (`chrome`, `firefox`, `safari`, `edge`) |
| `percy.platforms` (Automate `browserName`/`os`/`deviceName`) | sessions on the TestMu AI grid (hooks mode); see the matching grid skill |
| `percy.diffSensitivity`, `imageIgnoreThreshold` | project mismatch thresholds (smartui-mismatch-thresholds) |
| `percy.carouselsEnabled`, `bannersEnabled`, `adsEnabled` (Visual AI ignores) | SmartIgnore / Visual AI agent settings; or `ignoreDOM` selectors |
| `discovery.allowedHostnames` | `allowedHostnames` |
| `discovery.disallowedHostnames` | none; list as a gap if used |
| `discovery.networkIdleTimeout` | `waitForPageRender` |
| `discovery.requestHeaders`, `authorization`, `cookies`, `userAgent` | `requestHeaders`, `basicAuthorization`, `cookies` (smartui-cli-request-headers, smartui-basic-auth) |
| `discovery.disableCache`, `concurrency`, `captureMockedServiceWorker` | `useGlobalCache` (inverse), others drop |
| `static.include`/`exclude`/`baseUrl`/`cleanUrls` | the `urls.json` list for `smartui capture` |
| `upload.files`/`ignore` | `smartui upload --files` / `--ignoreDir` |

## 6. Snapshot options

| Percy option | SmartUI option |
|---|---|
| `name` | second argument |
| `widths` | `web: { viewports: [[w]] }` |
| `minHeight` | none |
| `percyCSS` | `customCSS` |
| `scope` | `selectDOM: { cssSelector: [...] }` or `element: { cssSelector }` |
| `enableJavaScript` | per-config `enableJavaScript` |
| `domTransformation` | none; use `customCSS` or an `ignoreDOM` region |
| `ignoreRegionSelectors` / `ignoreRegionXpaths` / `customIgnoreRegions` | `ignoreDOM: { cssSelector: [...], xpath: [...] }` (also `id`, `class`) |
| `considerRegionSelectors` / `considerRegionXpaths` | `selectDOM` |
| `regions: [{ elementSelector, algorithm: 'ignore'|'standard'|'intelliignore'|'layout' }]` | `ignoreDOM` for ignore; `selectDOM` for consider; layout regions (smartui-layout-regions) for layout |
| `sync: true` | `sync: true` |
| `fullPage` (screenshot mode) | `fullPage` / `mobile.fullPage` |
| `freezeAnimatedImage`, `freezeImageBySelectors` | freeze animations |
| `labels`, `testCase` | build tags / group by test case |

## 7. SDK calls per framework and language

| Percy | SmartUI |
|---|---|
| Playwright JS: `@percy/playwright`, `percySnapshot(page, name, opts)` | `@lambdatest/playwright-driver`, `smartuiSnapshot(page, name, opts)` |
| Playwright JS screenshot mode: `percyScreenshot(page, name, opts)` | hooks mode on the TestMu AI grid: `page.evaluate(_ => {}, 'lambdatest_action: {"action":"smartui.takeScreenshot","arguments":{"screenshotName":"name","fullPage":true}}')` with `smartUIProjectName` in `LT:Options` |
| Playwright Python: `percy-playwright`, `from percy import percy_snapshot`, `percy_snapshot(page, name, **kw)` | `lambdatest-playwright-driver`, `from lambdatest_playwright_driver import smartui_snapshot`, `smartui_snapshot(page, name)` |
| Playwright Java: `percy-playwright-java`, `percy.snapshot(name, ...)` / `percy.screenshot(name)` | `io.github.lambdatest:lambdatest-java-playwright-sdk`, `SmartUISnapshot.smartuiSnapshot(page, name, options)` |
| Playwright .NET: `PercyIO.Playwright`, `Percy.Snapshot(page, name, opts)` | no SmartUI Playwright .NET SDK documented; use hooks mode on the grid, or flag as a gap |
| Selenium JS: `@percy/selenium-webdriver`, `percySnapshot(driver, name, opts)`; `percyScreenshot(driver, name, opts)` | `@lambdatest/selenium-driver`, `smartuiSnapshot(driver, name, opts)`; screenshot mode -> hooks `driver.executeScript('smartui.takeScreenshot=name')` |
| Selenium Python: `percy-selenium`, `from percy import percy_snapshot, percy_screenshot` | `lambdatest-selenium-driver`, `from lambdatest_selenium_driver import smartui_snapshot`; screenshot mode -> hooks |
| Selenium Java: `io.percy:percy-java-selenium`, `Percy percy = new Percy(driver); percy.snapshot(name)`; `percy.screenshot(driver, name, opts)` | `io.github.lambdatest:lambdatest-java-sdk`, `SmartUISnapshot.smartuiSnapshot(driver, name, options)` (no instance) |
| Selenium .NET: `PercyIO.Selenium`, `Percy.Snapshot(driver, name, opts)`; `Percy.Screenshot(name)` | NuGet `LambdaTest.Selenium.Driver`, `SmartUISnapshot.CaptureSnapshot(driver, name, options)` |
| Selenium Ruby: `percy-selenium` gem, `Percy.snapshot(driver, name)`; `Percy.percy_screenshot(driver, name)` | `lambdatest-selenium-driver` gem, `require 'lambdatest/selenium/driver'`, `Lambdatest::Selenium::Driver.smartui_snapshot(driver, name, options)` (lowercase t in `Lambdatest`) |
| Capybara: `percy-capybara`, `page.percy_snapshot(name)` | `Lambdatest::Selenium::Driver.smartui_snapshot(page.driver.browser, name)` with the Ruby gem (Selenium driver only; no Capybara doc, the gem only calls `execute_script`) |
| Cypress: `@percy/cypress`, `cy.percySnapshot(name, opts)` | `@lambdatest/cypress-driver@1.0.8`, `cy.smartuiSnapshot(name, opts)`; or Cypress CLI hooks flow (`cy.screenshot` + `run_settings.smart_ui`) |
| Puppeteer: `@percy/puppeteer`, `percySnapshot(page, name)` | `@lambdatest/puppeteer-driver`, `smartuiSnapshot(page, name)` |
| WebdriverIO: `@percy/webdriverio`, `percySnapshot(browser, name)` or `percySnapshot(name)` | `@lambdatest/wdio-driver`, `smartuiSnapshot(browser, name)` |
| TestCafe: `@percy/testcafe`, `percySnapshot(t, name)` | `@lambdatest/testcafe-driver`, `smartuiSnapshot(t, name)` |
| Nightwatch: `@percy/nightwatch`, `browser.percySnapshot(name)` | no SmartUI Nightwatch driver documented; run on the TestMu AI grid and use hooks `browser.execute('smartui.takeScreenshot=name')`, or flag |
| Ember: `@percy/ember`, `percySnapshot(name)` | no SmartUI Ember SDK; flag as a gap (or capture via Storybook/static URLs) |
| Storybook: `@percy/storybook`, story `parameters.percy` (`skip`, `name`, `args`, `waitForSelector`) | `@lambdatest/smartui-storybook`; `include`/`exclude` patterns, `waitForTimeout`, `customViewports`; story parameters (rename, per-story skip, args) are not read: gap |
| Robot Framework (percy-selenium-python) | `lambdatest-selenium-driver` from a Python keyword library, or hooks mode |

Every SDK suite runs under `npx smartui --config .smartui.json exec -- <test command>` with `PROJECT_TOKEN`, replacing `npx percy exec -- <test command>` with `PERCY_TOKEN`.

## 8. Percy on Automate and App Percy

- Percy on Automate (`percyScreenshot`/`percy_screenshot`, `auto_` token, BrowserStack SDK `percy: true`, `percyCaptureMode`): first migrate the Automate sessions with the BrowserStack to TestMu AI skill, then use SmartUI hooks: `LT:Options` gets `smartUI.project` (and `smartUI.build`, `smartUI.baseline`), each `percyScreenshot(driver, 'x')` becomes `driver.executeScript('smartui.takeScreenshot=x')` (Selenium/Appium) or the `lambdatest_action` form (Playwright/Puppeteer, flat `smartUIProjectName`). `percyCaptureMode: auto` (capture on every command) has no equivalent; place explicit calls.
- App Percy (`percy app:exec`, `percy-appium-app` Python/Java/JS/Ruby/.NET, `AppPercy percy = new AppPercy(driver); percy.screenshot(name)`, options `fullscreen`, `statusBarHeight`, `navBarHeight`, `orientation`, ignore regions): migrate the App Automate sessions to the Real Device Cloud, then hooks: `smartUI.project` capability plus `driver.executeScript("smartui.takeScreenshot=name")`; status bar and footer cropping via `smartUI.cropStatusBar` / `smartUI.cropFooter`. Java teams can use the `SmartUIAppSnapshot` instance API from `lambdatest-java-sdk` (`start`, `smartuiAppSnapshot(driver, name, config)`, `stop`) under plain `mvn test`. Flutter helpers (`percyScreenshotFlutter`) have no equivalent: flag.

## 9. Storybook, static sites, uploads

- `@percy/storybook` + `percy storybook ./storybook-static` -> `npm i -D @lambdatest/smartui-storybook` + `npx smartui storybook ./storybook-static --config .smartui-storybook.json` (separate config file; a `storybook` block in `.smartui.json` breaks `smartui exec`); story-level `parameters.percy.skip` -> `storybook.exclude` patterns (`id:`, `title:`, `name:`, `path:` prefixes); `parameters.percy.name` -> rename not supported; `waitForSelector` -> `waitForTimeout` (story-level supported in `customViewports`).
- `percy snapshot snapshots.yml` (list of `{ name, url, waitForSelector, execute }`) -> `urls.json` (`[{ "name": "...", "url": "...", "waitForTimeout": 1000 }]`) + `smartui capture urls.json`; `execute` scripts have no equivalent.
- `percy upload ./screenshots` -> `smartui upload ./screenshots`.

## 10. Review workflow, baselines, branches, CI gating

| Percy | SmartUI |
|---|---|
| Baseline = latest approved build on `PERCY_TARGET_BRANCH` (default branch) | baseline branch in project settings or `BASELINE_BRANCH`; latest approved build on it |
| Auto-approve branches setting | approve on the baseline branch to promote; auto-update baseline (project setting) |
| PR status checks via BrowserStack GitHub/GitLab/Bitbucket/Azure integration | SmartUI GitHub app, GitLab PR checks (exec and hooks), Bitbucket, Azure, Buildkite, CircleCI, Netlify, Semaphore, Travis pages |
| `percy build:wait` + fail on diffs | `--fetch-results` and a script for `exec` suites; Storybook: `SMARTUI_FAIL_ON=changes|unreviewed|rejected` / `failOn` (exit code 4) |
| Visual Review Agent / AI review | SmartUI Visual AI agent, root-cause analysis, smart comments |
| Build history | stays in Percy; export what must be kept |

Baselines never transfer. Plan a first SmartUI run on the baseline branch, review and approve it, then switch PR builds over.

## 11. Gaps

Percy features with no documented SmartUI equivalent: parallel-build nonce and `build:finalize` semantics, `disallowedHostnames`, `minHeight`, `domTransformation`, snapshot `execute` scripts, `percyCaptureMode: auto`, Ember and Nightwatch SDKs, Playwright .NET SDK, Flutter helpers, Percy CLI build approval verbs. Leave `TODO(testmu-migration)` at each call site that needed one and list them in the summary.
