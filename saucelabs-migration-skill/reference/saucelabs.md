# Sauce Labs to TestMu AI

Read this when the source is Sauce Labs (Selenium, Appium, saucectl, Sauce Connect, wdio sauce-service).

Contents
1. Fingerprints
2. Credentials and endpoints
3. sauce:options to LT:Options (web)
4. Appium and App Storage
5. saucectl (Playwright, Cypress, TestCafe, Espresso, XCUITest)
6. Sauce Connect to LT Tunnel
7. Test status and annotations
8. WebdriverIO, Nightwatch, TestCafe, Robot
9. REST API
10. Value translation
11. Gotchas

## 1. Fingerprints

Grep for: `ondemand.us-west-1.saucelabs.com`, `ondemand.eu-central-1.saucelabs.com`, `ondemand.us-east-4.saucelabs.com`, `ondemand.asia-south-2.saucelabs.com`, `ondemand.saucelabs.com`, `saucelabs.com/wd/hub`, `sauce:options`, `SAUCE_USERNAME`, `SAUCE_ACCESS_KEY`, `SAUCE_REGION`, `SAUCE_TUNNEL_NAME`, `sauce:job-result`, `sauce:job-name`, `sauce:context`, `saucectl`, `.sauce/config.yml`, `kind: playwright` with `sauce:` block, `@wdio/sauce-service`, `@saucelabs/playwright-reporter`, `testcafe-browser-provider-saucelabs`, `sc run`, `sauce-connect`, `storage:filename=`, `storage:<uuid>`, `api.us-west-1.saucelabs.com/v1/storage`, `api.eu-central-1.saucelabs.com`, `app.saucelabs.com` / `app.eu-central-1.saucelabs.com` (dashboard links in READMEs and reporters), `.sauceignore`, Sauce Bindings (`com.saucelabs:saucebindings-*` Maven artifacts, `SauceSession`, `SauceOptions`, `SauceBaseTest`, `SauceBindingsExtension`, Python `saucebindings`, Ruby `sauce_bindings`, C# `Sauce.Bindings`), `sauce:visual` / `@saucelabs/visual` (Sauce Visual).

## 2. Credentials and endpoints

| Sauce Labs | TestMu AI |
|---|---|
| `SAUCE_USERNAME` / `SAUCE_ACCESS_KEY` | `LT_USERNAME` / `LT_ACCESS_KEY` |
| `https://ondemand.<region>.saucelabs.com[:443]/wd/hub` (us-west-1, us-east-4, eu-central-1, asia-south-2) | `https://hub.lambdatest.com/wd/hub` (web); `https://mobile-hub.lambdatest.com/wd/hub` (Appium) |
| `https://USER:KEY@ondemand.<region>.saucelabs.com/wd/hub` | `https://USER:KEY@hub.lambdatest.com/wd/hub` |
| `https://api.<region>.saucelabs.com/rest/v1/...` | `https://api.lambdatest.com/automation/api/v1/...` |
| `https://api.<region>.saucelabs.com/v1/storage/upload` | `https://manual-api.lambdatest.com/app/upload/realDevice` |

Region: Sauce picks the data centre by hostname. TestMu has a single web hub; for Appium use the `region` cap (`EU`, `US`, `AP`), and for REST the `eu-api.lambdatest.com` host. `eu-central-1` -> `region: "EU"`, `asia-south-2` -> `region: "AP"`, `us-*` -> `region: "US"`.

## 3. sauce:options to LT:Options (web)

W3C keys (`browserName`, `browserVersion`, `platformName`) stay top-level on both sides. Sauce `platformName` strings (`Windows 11`, `macOS 13`) are already in TestMu's one-string format; only the macOS spelling changes (version number to codename, see §10).

| sauce:options key | LT:Options key | Transform |
|---|---|---|
| `username` / `accessKey` | `username` / `accessKey` | env var rename |
| `name` | `name` | same |
| `build` | `build` | same |
| `tags` | `tags` | same (array) |
| `custom-data` | `customData` | same object |
| `public` | drop | flag; TestMu shares via dashboard |
| `tunnelName` | `tunnelName` + `tunnel: true` | add the boolean |
| `tunnelOwner` | drop | TestMu tunnels are account-scoped; use a shared tunnel (`--shared-tunnel`) and the same `tunnelName` |
| `screenResolution` | `resolution` | same value |
| `seleniumVersion` | `selenium_version` | same |
| `chromedriverVersion`, `geckodriverVersion`, `edgedriverVersion`, `iedriverVersion` | `driver_version` | one key |
| `extendedDebugging` | `network: true` + `console: true` | HAR + console |
| `capturePerformance` | drop | TestMu Lighthouse report is separate; flag |
| `devTools` | drop | CDP available by default on TestMu Playwright |
| `recordVideo` | `video` | same bool |
| `videoUploadOnPass` | drop | |
| `recordScreenshots` | `visual` | step screenshots |
| `recordLogs` | `verboseWebDriverLogging` | approximate |
| `captureHtml` | drop | |
| `idleTimeout` (90, max 1000) | `idleTimeout` | same number |
| `commandTimeout` | drop | |
| `maxDuration` (sec) | drop for web; HyperExecute `globalTimeout` (min) if orchestrated | |
| `timeZone` (city) | `timezone` (`UTC+HH:MM`) | convert, see §10 |
| `priority` | HyperExecute `jobLabel` priority | approximate |
| `avoidProxy`, `prerun` | drop | flag `prerun` (HyperExecute `pre:` steps are the equivalent) |
| `armRequired` (Apple Silicon page) | drop | TestMu picks hardware |

Always add `w3c: true`.

Java before / after:
```java
MutableCapabilities sauce = new MutableCapabilities();
sauce.setCapability("username", System.getenv("SAUCE_USERNAME")); sauce.setCapability("accessKey", System.getenv("SAUCE_ACCESS_KEY"));
sauce.setCapability("build", "b1"); sauce.setCapability("name", "t1"); sauce.setCapability("tunnelName", "ci");
options.setCapability("sauce:options", sauce);
driver = new RemoteWebDriver(new URL("https://ondemand.us-west-1.saucelabs.com:443/wd/hub"), options);
// ->
HashMap<String, Object> lt = new HashMap<>();
lt.put("username", System.getenv("LT_USERNAME")); lt.put("accessKey", System.getenv("LT_ACCESS_KEY"));
lt.put("build", "b1"); lt.put("name", "t1"); lt.put("tunnel", true); lt.put("tunnelName", "ci"); lt.put("w3c", true);
options.setCapability("LT:Options", lt);
driver = new RemoteWebDriver(new URL("https://hub.lambdatest.com/wd/hub"), options);
```

Python:
```python
options.set_capability('sauce:options', {'username': ..., 'accessKey': ..., 'build': 'b1', 'name': 't1', 'extendedDebugging': True})
driver = webdriver.Remote(command_executor='https://ondemand.eu-central-1.saucelabs.com:443/wd/hub', options=options)
# ->
options.set_capability('LT:Options', {'username': os.getenv('LT_USERNAME'), 'accessKey': os.getenv('LT_ACCESS_KEY'), 'build': 'b1', 'name': 't1', 'network': True, 'console': True, 'w3c': True})
driver = webdriver.Remote(command_executor='https://hub.lambdatest.com/wd/hub', options=options)
```

C#: `browserOptions.AddAdditionalOption("sauce:options", sauceOptions)` -> `AddAdditionalOption("LT:Options", ltOptions)`; URL swap as above.

## 4. Appium and App Storage

Re-upload apps. `storage:filename=app.apk` and `storage:<uuid>` references do not transfer.
```
# Sauce
curl -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" -X POST https://api.us-west-1.saucelabs.com/v1/storage/upload --form 'payload=@app.apk' --form 'name=app.apk'
# TestMu
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST https://manual-api.lambdatest.com/app/upload/realDevice -F "appFile=@app.apk" -F "name=app"
```
Form field `payload` -> `appFile`. Reference `storage:filename=app.apk` -> `lt://APP...` from the upload response.

| Sauce cap | TestMu |
|---|---|
| `platformName` | `platformName` |
| `appium:deviceName` (regex: `Samsung.*Galaxy.*`, `iPhone .*`) | `deviceName` regex in TestMu naming (`Galaxy.*`, `iPhone.*`) or an exact name (`Galaxy S23`); TestMu App Automation supports regex (regular-expression-appium) |
| `appium:platformVersion` (substring) | `platformVersion` (exact major) |
| `appium:automationName` | `automationName` |
| `appium:app` (`storage:...`) | `app` (`lt://...`) |
| `appium:otherApps` | `otherApps` (max 3 on TestMu) |
| `appium:bundleId`, `appPackage`, `appActivity`, `noReset`, `newCommandTimeout` | same names |
| `appium:timeZone` / `appTimeZone` | `timezone` (UTC offset) |
| `sauce:options.appiumVersion` (`latest`/`stable`/pinned) | `appiumVersion` (TestMu supports it on real devices: Android 1.21.0 to 3.0.2, iOS 15+ 1.22.3 to 3.0.2, default 2.2.1; check the version is in that list); `latest`/`stable` have no TestMu equivalent, so set an explicit version or omit for the default |
| `sauce:options.name`, `build`, `tags` | `name`, `build`, `tags` |
| `sauce:options.deviceOrientation` | `deviceOrientation` |
| `sauce:options.cacheId`, `allowCacheFallback` | drop |
| `sauce:options.resigningEnabled` | `resignApp` |
| `sauce:options.phoneOnly`, `tabletOnly`, `privateDevicesOnly`, `publicDevicesOnly`, `carrierConnectivityOnly` | express phone/tablet through the `deviceName` pattern (`Galaxy S.*` vs `Galaxy Tab.*`); `privateCloud: true` for private devices |
| `sauce:options.sessionCreationTimeout` (ms) | `queueTimeout` (sec, 300 to 900) |
| `sauce:options.networkCapture` | `network` |
| `sauce:options.audioCapture`, `vitals`, `crashReporting` | drop |
| `sauce:options.imageInjection` | `enableImageInjection` |
| `sauce:options.biometricsInterception` | drop (flag) |
| `sauce:options.enableAnimations` | `disableAnimation` (inverted) |
| `sauce:options.networkProfile`, `networkConditions` | `lambda-throttle-network` hook |
| `sauce:options.logFilters`, `filterSendKeys` | `lambdaMaskCommands` |
| `sauce:options.customLogFiles`, `setupDeviceLock`, `disableImmersiveModePopUp`, `android.gpu.mode` | drop |
| Virtual devices (`iPhone 8 Simulator`, `... GoogleAPI Emulator`) | `isRealMobile: false`, `deviceName: "iPhone 8"`, upload via `/app/upload/virtualDevice` |
| Real devices | `isRealMobile: true` |

Sauce real devices are regex-selected. TestMu App Automation accepts regular expressions in `deviceName` and `platformVersion` (`Galaxy.*`, `iPhone 1[45].*`, `Pixel [6-8]$`, comma or `|` for alternatives); translate the pattern to TestMu device names (no `Samsung `/`Google ` prefixes) or pick exact devices.

## 4a. Sauce Bindings

Sauce Bindings wrap driver creation (`SauceSession session = new SauceSession(options); driver = session.start(); session.stop(passed)`) and ship JUnit 4/5 and TestNG base classes (`SauceBaseTest`, `SauceBindingsExtension`). There is no TestMu equivalent library, so replace them with a small driver factory or base class in the repo:
- Java: one `TestMuBaseTest` (or JUnit 5 extension) that builds options with `LT:Options`, creates `RemoteWebDriver` on `https://hub.lambdatest.com/wd/hub`, and in teardown sends `lambda-status=passed|failed` then `driver.quit()` (status hook table in languages.md §3). `SauceOptions.chrome()/firefox()/edge()/safari()` -> `new ChromeOptions()` etc.; `setPlatformName(SaucePlatform.MAC_VENTURA)` -> `LT:Options.platformName = "macOS Ventura"`; `setName`/`setBuild` -> `name`/`build`.
- Python (`saucebindings.session.SauceSession`), Ruby (`SauceBindings::Session`), C# (`Sauce.Bindings`): same pattern with a fixture or helper.
- The bindings bring Selenium, JUnit/TestNG and WebDriverManager in transitively. After removing them, add `org.seleniumhq.selenium:selenium-java` and the test framework (and its Maven Surefire/Gradle config) as direct dependencies at the versions the lockfile or `mvn dependency:tree` showed before removal.

## 4b. Sauce native Playwright endpoint (no saucectl)

Some repos open Playwright sessions on Sauce directly (a `POST https://.../playwright/session` or a `wss://...saucelabs.com/...playwright...` URL, often behind a `TARGET=sauce` switch). Replace with `chromium.connect(\`wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(JSON.stringify(caps))}\`)` and `LT:Options` (`platform`, `build`, `name`, `user`, `accessKey`); Python `p.chromium.connect(...)` with the same URL. Status goes through `lambdatest_action: setTestStatus` per test (testmu-target.md §8); if one browser is shared across tests, send the status per test page before closing it, or open one connection per test. Linux is a documented web platform on TestMu, so Linux runs can stay Linux.

## 5. saucectl

saucectl uploads the project and runs it on Sauce VMs. TestMu equivalents: Cypress -> `lambdatest-cypress-cli`; Playwright/TestCafe/anything else -> HyperExecute (`hyperexecute.yaml`), or the Playwright CDP connect / TestCafe provider if the team prefers hub-style execution.

`.sauce/config.yml` (Playwright) -> `hyperexecute.yaml` v0.1 (`testDiscovery` + `testRunnerCommand`; v0.2 has no Playwright framework block). This is execution model B in `hyperexecute.md` §2a: browsers launch on the HyperExecute VM, no grid session, no status hook.

| saucectl | HyperExecute / TestMu |
|---|---|
| `sauce.region` | drop (or `region` on Appium) |
| `sauce.concurrency` | `concurrency` |
| `sauce.retries` | `retryOnFailure: true`, `maxRetries` |
| `sauce.metadata.build`, `tags` | `jobLabel` list |
| `sauce.tunnel.name`, `owner` | `tunnel: true`, `tunnelNames: [name]` |
| `env` | `env` |
| `npm.packages` / `dependencies` | `pre: [npm ci]` + `cacheDirectories: [node_modules]` |
| `nodeVersion` | `runtime: [{language: node, version: "20"}]` |
| `playwright.version` | the `@playwright/test` version in package.json |
| `playwright.configFile` | `--config <file>` in `testRunnerCommand` |
| `suites[].excludedTestFiles` | exclude in the discovery command |
| `suites[].params.grep` / `grepInvert` / `headless` | `--grep` / `--grep-invert` / `--headed` in `testRunnerCommand` |
| `suites[].preExec` | `pre:` |
| `suites[].timeZone`, `screenResolution` | `LT:Options.timezone` (UTC offset), `resolution` in the fixture capabilities |
| `passThreshold`, `smartRetry.failedOnly` | `retryOnFailure` / `maxRetries` (failed tests only) |
| `artifacts`, `reporters` | `uploadArtefacts`, `report` / `partialReports` |
| `sauce.tunnel.timeout` | drop |
| `rootDir` | `workingDirectory` |
| `suites[].name` | one `testSuites` entry / matrix row |
| `suites[].platformName` | `runson: win|mac|linux` |
| `suites[].testMatch` | `testDiscovery.command` glob or `--grep` |
| `suites[].params.browserName` / `project` | `--project=<name>` in `testRunnerCommand` |
| `suites[].shard: spec` / `numShards` | `autosplit: true` |
| `suites[].params.workers` | `concurrency` |
| `defaults.timeout`, `suites[].timeout` | `globalTimeout` (minutes) |
| `showConsoleLog` | drop |
| `kind: playwright-cucumberjs` (`@saucelabs/playwright-cucumberjs` runner, `cucumberjs`/`playwright` blocks) | `testRunnerCommand: npx cucumber-js $test` with discovery over `features/**/*.feature`; Sauce injected `BROWSER_NAME` into the world, so set it yourself in `env:` (or the matrix) and read it in the world/hooks; drop `@saucelabs/cucumber-reporter` and keep a standard cucumber formatter (`--format json:reports/cucumber.json`) collected via `report`/`uploadArtefacts` |
| `.sauceignore` | `.hyperexecuteignore` (same gitignore syntax; `.gitignore` takes precedence if both exist) |
| `SAUCE_VM`, `SAUCE_JOB_ID`, other `SAUCE_*` runtime env read by tests | remove the branches; `HYPEREXECUTE_PLATFORM` is set on the VM if the code needs to know it runs on HyperExecute |
| saucectl GitHub Action (`saucelabs/saucectl-run-action`), CircleCI orb, `.gitpod.yml` saucectl steps | download and run the HyperExecute CLI (`hyperexecute.md` §10) |

Model B example (browsers on the VM):
```yaml
version: 0.1
runson: linux
autosplit: true
concurrency: 5
retryOnFailure: true
maxRetries: 1
runtime:
  - language: node
    version: "20"
pre:
  - npm ci
  - npx playwright install --with-deps chromium
cacheKey: '{{ checksum "package-lock.json" }}'
cacheDirectories:
  - node_modules
testDiscovery:
  type: raw
  mode: local
  command: grep -rl "test(" tests --include="*.spec.ts"
testRunnerCommand: npx playwright test $test --project=chromium
jobLabel: [playwright, smoke]
```
Browsers inside HyperExecute run on the VM (install with `npx playwright install --with-deps` in `pre`). To run against TestMu cloud browsers instead, keep the Playwright Test runner local or on HyperExecute and use a fixture that calls `chromium.connect` with `LT:Options` (see testmu-target.md §3).

Cypress `.sauce/config.yml` -> `lambdatest-config.json`: `cypress.version` -> `run_settings.npm_dependencies.cypress`; `suites[].browser` + `browserVersion` + `platformName` -> `browsers[]` entries (`{ "browser": "Chrome", "platform": "Windows 10", "versions": ["latest"] }`); `suites[].config.specPattern` -> `run_settings.specs`; `suites[].config.excludeSpecPattern` -> `run_settings.ignore_files`; `suites[].config.env` -> `--envs`; `sauce.concurrency` -> `run_settings.parallels` (`suites[].shard` is a mode, not a count); `suites[].headless` -> `run_settings.headless`; Cypress 10+ config file -> `--cy="--config-file <file>"` (not `cypress_config_file`); `sauce.tunnel.name` -> `tunnel_settings.tunnel_name`; `sauce.metadata.build` -> `run_settings.build_name`. Then `saucectl run` -> `npx lambdatest-cypress run --sync=true --eof=true`.

TestCafe `.sauce/config.yml` -> provider: `testcafe "lambdatest:<Browser>@<version>:<platform>" <src>` with `testcafe-browser-provider-lambdatest`; `simulators` -> real devices on TestMu via `LT_CAPABILITY_PATH` JSON with `deviceName`/`platformVersion`/`isRealMobile`.

Espresso / XCUITest `kind: espresso|xcuitest`: `espresso.app`, `espresso.testApp` -> upload both via `POST https://manual-api.lambdatest.com/app/uploadFramework` (`type=espresso-android` or `xcuit-ios`); `suites[].devices[].name` regex + `platformVersion` -> `device: ["<name>-<version>"]`; `emulators` -> virtual device upload; `testOptions.class/package/size/annotation` (and `notClass`/`notPackage`/`notAnnotation`) -> build body `class`, `package`, `size`, `annotation`, `skipClass`, `skipPackage`, `skipAnnotation`; XCUITest `testOptions.only/skip`-style lists -> `only-testing` / `skip-testing`; `testOptions.numShards` -> run multiple builds. POST to `https://mobile-api.lambdatest.com/framework/v1/espresso/build` or `.../xcui/build`.

`@saucelabs/playwright-reporter` (results upload only): drop; TestMu dashboards populate from cloud sessions. If tests stay local, there is no equivalent results-only upload; flag it.

## 6. Sauce Connect to LT Tunnel

| Sauce Connect 5 | LT Tunnel |
|---|---|
| `sc run --username U --access-key K --region us-west --tunnel-name N` | `LT --user $LT_USERNAME --key $LT_ACCESS_KEY --tunnelName N` |
| `--region` | drop |
| `-s, --shared all` | `--shared-tunnel` |
| `-t, --tunnel-pool` | run several tunnels with the same name; `--load-balanced` |
| `-T, --tunnel-domains` | `--allowHosts` |
| `-D, --direct-domains` | `--bypassHosts` |
| `--deny-domains` | drop (flag) |
| `-x, --proxy` | `--proxy-host` + `--proxy-port` (+ user/pass) |
| `--proxy-sauce` | `--ingress-only` is the nearest; flag |
| `--dns-server` | `--dns` |
| `--cacert-file` | `--clientCert` |
| `--tls-passthrough-domains` | `--mTLSHosts`/`--mitm` (flag) |
| `--api-address` | `--infoAPIPort` |
| `-c, --config-file` (yaml) | `--config .lt.yaml` |
| `-M, --metadata` | drop |
| Docker `saucelabs/sauce-connect` | TestMu Docker tunnel image (docs: "Docker Tunnel" page) |
| Sauce Connect 4 flags (`--user`, `--api-key`, `--shared-tunnel`, `--dns`, `--pidfile`) | same mapping as above |

Caps `tunnelName: N` (+ `tunnelOwner`) -> `tunnel: true, tunnelName: N`. saucectl `sauce.tunnel.name` -> HyperExecute `tunnel: true`, `tunnelNames`.

## 7. Test status and annotations

| Sauce | TestMu |
|---|---|
| `driver.executeScript("sauce:job-result=passed")` | `driver.executeScript("lambda-status=passed")` |
| `sauce:job-result=failed` (or `false`) | `lambda-status=failed` |
| `sauce:job-name=X` | `lambda-name=X` |
| `sauce:job-build=X` | `lambda-build=X` |
| `sauce:job-tags=a,b` | `lambda-test-tags` with args `["a,b"]` |
| `sauce:job-info={...}` | split into `lambda-name`, `lambda-build` |
| `sauce:context=text` | `lambda-testCase-start=text` (step marker) or `lambda-action=text` (reason) |
| `sauce: break` | `lambda-breakpoint=true` |
| `sauce: stop network` / `start network` | `lambda-throttle-network` ("no network" profile) |
| `sauce:inject-image=<b64>` | `enableImageInjection` cap + TestMu image injection API; flag |
| `sauce:performanceEnable`/`Disable` | drop |
| REST `PUT /rest/v1/{user}/jobs/{id} {"passed": true}` | `PATCH /automation/api/v1/sessions/{id}` |

Note Sauce accepts `true`/`false` as status; TestMu wants `passed`/`failed`. Convert booleans.

## 8. WebdriverIO, Nightwatch, TestCafe, Robot

WebdriverIO: `services: [['sauce', { sauceConnect: true, sauceConnectOpts: {...}, uploadLogs, setJobName, maxErrorStackLength }]]`, `region: 'eu'` -> `npm uninstall @wdio/sauce-service && npm i -D wdio-lambdatest-service`; `services: [['lambdatest', { tunnel: true }]]`; `hostname: 'hub.lambdatest.com'`, `port: 80`, `path: '/wd/hub'`; remove `region`; `user`/`key` from `LT_*`. Caps `'sauce:options'` -> `'LT:Options'` via §3. Job name/status are set by the lambdatest service automatically.

Nightwatch: `selenium.host: 'ondemand.saucelabs.com'`, `port: 443`, `desiredCapabilities['sauce:options']` -> `host: 'hub.lambdatest.com'`, `port: 80`, `['LT:Options']`.

TestCafe: `saucelabs:Chrome@beta:Windows 10` -> `lambdatest:Chrome@latest:Windows 10`; env `SAUCE_JOB` -> `LT_TEST_NAME`, `SAUCE_BUILD` -> `LT_BUILD`, `SAUCE_SCREEN_RESOLUTION` -> `LT_RESOLUTION`, `SAUCE_CAPABILITIES_OVERRIDES_PATH` and `SAUCE_CONFIG_PATH` -> `LT_CAPABILITY_PATH`, `SAUCE_CONNECT_OVERRIDES_PATH` -> LT tunnel flags and `LT_PROXY_HOST`/`LT_PROXY_PORT`, `SAUCE_API_HOST` -> drop.

Robot Framework: `Open Browser ${URL} chrome remote_url=https://%{SAUCE_USERNAME}:%{SAUCE_ACCESS_KEY}@ondemand.us-west-1.saucelabs.com:443/wd/hub options=...` -> `remote_url=https://%{LT_USERNAME}:%{LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub`, options build `LT:Options` instead of `sauce:options`.

## 9. REST API

| Sauce | TestMu |
|---|---|
| `GET /rest/v1/{user}/jobs` | `GET /automation/api/v1/sessions` |
| `GET /rest/v1/{user}/jobs/{id}` | `GET /automation/api/v1/sessions/{id}` |
| `PUT /rest/v1/{user}/jobs/{id}` | `PATCH /automation/api/v1/sessions/{id}` |
| `GET /rest/v1/{user}/jobs/{id}/assets/video.mp4` | `GET /automation/api/v1/sessions/{id}/video` |
| `GET .../assets/log.json` | `GET .../log/command` |
| `GET .../assets/selenium-server.log` | `GET .../log/selenium` |
| `GET /v1/storage/files` | `GET https://manual-api.lambdatest.com/app/data` |
| `GET /rest/v1/info/platforms/all` | `GET /automation/api/v1/platforms` |
| `GET /rest/v1/{user}/tunnels` | `GET /automation/api/v1/tunnels` |

## 10. Value translation

- `platformName`: `Windows 11`, `Windows 10` unchanged. `macOS 11` -> `macOS Big Sur`; `macOS 12` -> `macOS Monterey`; `macOS 13` -> `macOS Ventura`; `macOS 14` -> `macOS Sonoma`; `macOS 15` -> `macOS Sequoia`; `macOS 26` -> `MacOS Tahoe`; `macOS 27` -> check TestMu platform list. `Linux` -> `Linux`.
- `browserName`: `chrome` -> `Chrome`; `MicrosoftEdge` unchanged; `firefox` -> `Firefox`; `safari` -> `Safari`. TestMu is case-insensitive so the lowercase forms also work.
- `browserVersion`: `latest`, `latest-1`, `latest-2` unchanged.
- `screenResolution` default `1024x768` on both.
- `timeZone` city -> UTC offset: `Los_Angeles` -> `UTC-08:00`, `New_York` -> `UTC-05:00`, `Chicago` -> `UTC-06:00`, `London` -> `UTC+00:00`, `Berlin` -> `UTC+01:00`, `Kolkata` -> `UTC+05:30`, `Tokyo` -> `UTC+09:00`, `Sydney` -> `UTC+10:00` (standard time; flag DST-sensitive tests).
- Mobile: regex device names -> TestMu regex or exact names (`Galaxy.*`, `Pixel 8`, `iPhone 15`); `platformVersion` substring (`11`) -> `11` or a version regex (`1[1-3]`). Regex works on App Automation only, not web automation on virtual devices.
- Status: `true`/`false` -> `passed`/`failed`.

## 11. Gotchas

- Sauce has four regional hubs; code often builds the hostname from `SAUCE_REGION`. Delete that logic; TestMu has one web hub.
- `tunnelOwner` (shared tunnels across sub-accounts) has no exact match. Use one shared tunnel under the org account.
- `extendedDebugging` is Chrome-only on Sauce; `network`/`console` work on all TestMu browsers, so the migrated suite may collect more than before.
- `maxDuration`, `commandTimeout` are Sauce-specific job limits; TestMu's `idleTimeout` is the only per-session timer. Keep an eye on long tests.
- saucectl uploads the project to Sauce VMs; the TestMu equivalent is HyperExecute, which changes CI steps (install the `hyperexecute` binary). Make that an explicit decision with the user.
- `appium:deviceName` regexes need TestMu device naming (drop `Samsung `/`Google ` prefixes); `platformVersion` substrings become exact versions or version regexes.
- Sources at research time (26 Oct 2026): docs.saucelabs.com (test-configuration-options, data-center-endpoints, test-annotation, saucectl, playwright/yaml, cypress/yaml/v1, testcafe/yaml, app-storage, appium real-devices, sauce-connect-5), webdriver.io sauce-service, DevExpress testcafe-browser-provider-saucelabs.
