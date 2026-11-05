# BrowserStack to TestMu AI

Read this when the source is BrowserStack (Automate, App Automate, SDK, Percy, Local). Tables map every BrowserStack construct to its TestMu AI equivalent. "Same" means copy the value through unchanged.

Contents
1. Fingerprints (how to recognise BrowserStack in a repo)
2. Credentials and endpoints
3. Selenium: bstack:options to LT:Options
4. Legacy flat capabilities (Selenium 3 / JSON Wire)
5. BrowserStack SDK (browserstack.yml) to TestMu
6. Playwright
7. Cypress (browserstack.json to lambdatest-config.json)
8. App Automate (Appium) and app upload
9. Espresso / XCUITest
10. BrowserStack Local to LT Tunnel
11. browserstack_executor to lambda hooks
12. WebdriverIO, Puppeteer, TestCafe, Nightwatch, Robot, Protractor, Capybara
13. Percy, Accessibility, Test Observability
14. REST API
15. Value translation (os/osVersion, device names, timezone)
16. Gotchas

## 1. Fingerprints

Grep for any of: `hub.browserstack.com`, `hub-cloud.browserstack.com`, `cdp.browserstack.com`, `api.browserstack.com`, `api-cloud.browserstack.com`, `bstack:options`, `browserstack.user`, `browserstack.key`, `browserstack.local`, `browserstack_executor`, `BROWSERSTACK_USERNAME`, `BROWSERSTACK_ACCESS_KEY`, `browserstack.yml`, `browserstack.json`, `browserstack-node-sdk`, `browserstack-sdk`, `browserstack-java-sdk`, `BrowserStack.TestAdapter`, `browserstack-cypress-cli`, `browserstack-local`, `BrowserStackLocal`, `@wdio/browserstack-service`, `testcafe-browser-provider-browserstack`, `@nightwatch/browserstack`, `@percy/`, `percySnapshot`, `bs://`, `media://`, `bs-local.com`, `browserstackLocal`, `browserStackLocalOptions`, `buildIdentifier`.

## 2. Credentials and endpoints

| BrowserStack | TestMu AI |
|---|---|
| `BROWSERSTACK_USERNAME` | `LT_USERNAME` |
| `BROWSERSTACK_ACCESS_KEY` | `LT_ACCESS_KEY` |
| `https://hub.browserstack.com/wd/hub`, `https://hub-cloud.browserstack.com/wd/hub` | `https://hub.lambdatest.com/wd/hub` |
| `https://USER:KEY@hub.browserstack.com/wd/hub` | `https://USER:KEY@hub.lambdatest.com/wd/hub` |
| App Automate hub (same hosts) | `https://mobile-hub.lambdatest.com/wd/hub` |
| `wss://cdp.browserstack.com/playwright?caps=` | `wss://cdp.lambdatest.com/playwright?capabilities=` |
| `wss://cdp.browserstack.com/puppeteer?caps=` | `wss://cdp.lambdatest.com/puppeteer?capabilities=` |
| `https://api.browserstack.com/automate/...` | `https://api.lambdatest.com/automation/api/v1/...` |
| `https://api-cloud.browserstack.com/app-automate/upload` | `https://manual-api.lambdatest.com/app/upload/realDevice` |

Note the query parameter rename for CDP: `caps` becomes `capabilities`. Both are URL-encoded JSON.

## 3. Selenium: bstack:options to LT:Options

W3C keys outside the vendor object (`browserName`, `browserVersion`, `acceptInsecureCerts`) stay where they are. `bstack:options.os` + `osVersion` collapse into one `platformName` string (see §15).

| bstack:options key | LT:Options key | Transform |
|---|---|---|
| `userName` | `username` | same value, env var rename |
| `accessKey` | `accessKey` | same |
| `os` + `osVersion` | `platformName` | join: `Windows`+`11` -> `Windows 11`; `OS X`+`Sonoma` -> `macOS Sonoma` |
| `browserVersion` (inside bstack:options) | top-level `browserVersion` | move out; `latest`, `latest-1` are the same |
| `projectName` | `project` | same value |
| `buildName` | `build` | same |
| `sessionName` | `name` | same |
| `buildTag` | `buildTags` | wrap in array |
| `local` | `tunnel` | boolean; `"true"` string -> `true` |
| `localIdentifier` | `tunnelName` | same value |
| `debug` | `visual` | boolean (step screenshots) |
| `networkLogs` | `network` | boolean |
| `networkLogsOptions.captureContent` (yml/Playwright key) | `network.full.har` | boolean |
| `consoleLogs` (`disable|errors|warnings|info|verbose`) | `console` | `disable` -> `false`; any level -> `true` (TestMu captures full console) |
| `video` | `video` | same (default true on both) |
| `seleniumLogs` | `verboseWebDriverLogging` | approximate; TestMu always keeps selenium logs |
| `telemetryLogs` | drop | no equivalent |
| `seleniumVersion` | `selenium_version` | same value |
| `resolution` | `resolution` | same value; check TestMu supports it (`1024x768`, `1280x800`, `1366x768`, `1600x1200`, `1920x1080`, `2048x1536`) |
| `geoLocation` | `geoLocation` | same ISO code |
| `timezone` (city, `New_York`) | `timezone` (`UTC-05:00`) | convert city to UTC offset (see §15) |
| `idleTimeout` (0 to 300) | `idleTimeout` | same number; TestMu allows larger |
| `maskCommands` (`setValues,getValues,...`) | `lambdaMaskCommands` | Playwright only on TestMu; for Selenium drop and flag |
| `maskBasicAuth` | drop | flag to user |
| `autoWait` | drop | TestMu has SmartWait; flag |
| `hosts` | tunnel `--dns` or `/etc/hosts` on runner | flag |
| `wsLocalSupport` | drop | tunnel handles websockets |
| `disableCorsRestrictions` | drop | flag |
| `interactiveDebugging` | drop | |
| `deviceName` + `osVersion` (mobile web) | `deviceName` + `platformVersion` + `isRealMobile: true` + `platformName` | Appium hub for real devices |
| `appiumVersion` | `appiumVersion` (TestMu supports it on real devices: Android 1.21.0 to 3.0.2, iOS 15+ 1.22.3 to 3.0.2, default 2.2.1; check the version is in that list) | same value if supported |
| `deviceOrientation` | `deviceOrientation` | same value (docs show lowercase, samples uppercase) |
| `customNetwork`, `networkProfile` | `lambda-throttle-network` hook at runtime | flag |
| `httpProxy`, `httpsProxy` | tunnel `--proxy-host/--proxy-port` | |
| `selfHeal` | `lambda-heal-start` hook | flag |
| `chrome.driver`, `firefox.driver`, `safari.driver`, `ie.driver` | `driver_version` | one key on TestMu |
| `safari.enablePopups`, `edge.enablePopups`, `ie.*`, `bfcache`, `browserstack.sendKeys` | drop | flag |
| `percy`, `percyCaptureMode` (yml keys) | SmartUI (`smartUI.project`) | see §13 |
| `accessibility`, `accessibilityOptions.*` | `accessibility`, `accessibility.wcagVersion`, `accessibility.bestPractice`, `accessibility.needsReview`, `accessibility.autoscan` | see §13 |
| `testObservability`, `testContextOptions` | drop | dashboard features on TestMu are on by default |

Always add `w3c: true` to LT:Options for Selenium 4 code.

Java before:
```java
HashMap<String, Object> bs = new HashMap<>();
bs.put("os", "Windows"); bs.put("osVersion", "11"); bs.put("buildName", "Release 42"); bs.put("sessionName", "Login"); bs.put("local", "true"); bs.put("localIdentifier", "ci-1");
options.setCapability("bstack:options", bs);
driver = new RemoteWebDriver(new URL("https://" + USER + ":" + KEY + "@hub.browserstack.com/wd/hub"), options);
```
Java after:
```java
HashMap<String, Object> lt = new HashMap<>();
lt.put("username", System.getenv("LT_USERNAME")); lt.put("accessKey", System.getenv("LT_ACCESS_KEY"));
lt.put("platformName", "Windows 11"); lt.put("build", "Release 42"); lt.put("name", "Login"); lt.put("tunnel", true); lt.put("tunnelName", "ci-1"); lt.put("w3c", true);
options.setCapability("LT:Options", lt);
driver = new RemoteWebDriver(new URL("https://hub.lambdatest.com/wd/hub"), options);
```

Python before / after:
```python
options.set_capability('bstack:options', {"os": "Windows", "osVersion": "10", "buildName": "b1", "sessionName": "t1", "networkLogs": "true", "consoleLogs": "info"})
driver = webdriver.Remote(command_executor="https://{}:{}@hub.browserstack.com/wd/hub".format(U, K), options=options)
# ->
options.set_capability("LT:Options", {"username": os.getenv("LT_USERNAME"), "accessKey": os.getenv("LT_ACCESS_KEY"), "platformName": "Windows 10", "build": "b1", "name": "t1", "network": True, "console": True, "w3c": True})
driver = webdriver.Remote(command_executor="https://hub.lambdatest.com/wd/hub", options=options)
```

## 4. Legacy flat capabilities

| BrowserStack flat key | TestMu |
|---|---|
| `browserstack.user` / `browserstack.key` | `LT:Options.username` / `accessKey` (or URL-embedded) |
| `os` + `os_version` | `platformName` (joined, see §15); legacy TestMu flat key `platform` |
| `browser` | `browserName` |
| `browser_version` | `browserVersion` (legacy flat: `version`) |
| `device` + `os_version` + `real_mobile` | `deviceName` + `platformVersion` + `isRealMobile` |
| `name` / `build` / `project` | `name` / `build` / `project` |
| `browserstack.local` / `browserstack.localIdentifier` | `tunnel` / `tunnelName` |
| `browserstack.debug` | `visual` |
| `browserstack.networkLogs` | `network` |
| `browserstack.consoleLogs` / `browserstack.console` | `console` |
| `browserstack.video` | `video` |
| `browserstack.selenium_version` | `selenium_version` |
| `browserstack.idleTimeout` | `idleTimeout` |
| `browserstack.geoLocation` | `geoLocation` |
| `browserstack.timezone` | `timezone` (UTC offset) |
| `browserstack.maskCommands`, `browserstack.sendKeys`, `browserstack.appium_version`, `browserstack.gpsLocation`, `browserstack.resignApp` | see §3 and §8 |
| `acceptSslCerts` | `acceptInsecureCerts` (W3C) |

String booleans (`"true"`) become real booleans. If the suite is still on Selenium 3 flat caps, the cleanest migration is to Selenium 4 + `LT:Options`; keep flat keys only when the user wants a minimal diff.

## 5. BrowserStack SDK (browserstack.yml)

The BrowserStack SDK reads `browserstack.yml` and injects capabilities and the hub at runtime, so SDK repos often contain no remote-driver code (a bare `new RemoteWebDriver(new URL(HUB), new MutableCapabilities())`, or even `new ChromeDriver()` / `webdriver.Chrome()` that the SDK redirects). Run `python3 scripts/convert_caps.py --from browserstack browserstack.yml` first: it prints the TestMu capabilities for every `platforms[]` entry. Then pick one path (ask the user if it is not obvious; the first that fits is the default):

| Path | Fits | What changes |
|---|---|---|
| A. TestMu AI SDK (config-driven, closest 1:1) | Java + TestNG (TestMu Selenium Java SDK, doc selenium-java-sdk); Node Playwright Test (`@lambdatest/playwright-node-sdk`, doc playwright-sdk) | `browserstack.yml` -> `lambdatest.yml` (table below); swap the BrowserStack agent for the TestMu one; driver code untouched except the hub URL |
| B. HyperExecute `platformConfig` | user chose HyperExecute; Selenium suites whose code creates local drivers (`hyperexecute.md` §7a; documented sample is Java TestNG) | add `hyperexecute.yaml` with `platformConfig.platform` = `platforms[]`; no driver-code change |
| C. Explicit driver factory | every other language/framework (Python, C#, Ruby, JUnit, Cucumber, WebdriverIO) and every Appium native-app SDK repo in any language (`platformConfig` is documented for browsers only, and the Java SDK for web only); with HyperExecute this is model A | add a small factory that reads the platform (env var, TestNG suite parameter, pytest parametrize) and builds `LT:Options`; `platforms[]` becomes runner parallelism (TestNG `<test>` per platform with `parallel="tests"`, `pytest -n` + parametrize, a thread pool for plain scripts) or a HyperExecute matrix |

Path A details (Java, TestNG only; behaviour below is read from the SDK source, github.com/LambdaTest/lambdatest-java-selenium-sdk):
- Coordinates: the docs page shows `io.github.lambdatest:lambdatest-selenium-java-sdk:1.0.1`; the source `pom.xml` publishes `io.github.lambdatest:lambdatest-java-selenium-sdk:1.0.2`. Use whichever resolves (`mvn dependency:get -Dartifact=io.github.lambdatest:<artifactId>:<version>` or search mvnrepository.com); if neither can be checked here, write the source coordinates and list the check as the first open item.
- pom: remove `com.browserstack:browserstack-java-sdk` and its `-javaagent`; add the SDK dependency, a `maven-dependency-plugin` `copy` execution placing it at `${project.build.directory}/agents/lambdatest-agent.jar`, and surefire `<argLine>-javaagent:${project.build.directory}/agents/lambdatest-agent.jar</argLine>`. The agent class is `com.lambdatest.selenium.agent.LambdaTestAgent`.
- `testng.xml`: add `<listener class-name="com.lambdatest.selenium.testng.TestNgTestListener"/>` (sets pass/fail; remove any `browserstack_executor setSessionStatus` calls). JUnit and Cucumber are not supported by the SDK yet: those repos use path C.
- What the agent intercepts: only `new RemoteWebDriver(URL, Capabilities)` whose URL contains `lambdatest.com`. It does not touch `new ChromeDriver()`, `RemoteWebDriver.builder()`, or other hosts. So change every local driver line (which the BrowserStack agent used to redirect) to `new RemoteWebDriver(new URL("https://hub.lambdatest.com/wd/hub"), options)`, and point BrowserStack hub constants there. Keep the options object if the code builds one; `ChromeOptions` args such as `start-maximized` only apply when the platform's browser is Chrome, so pass a neutral `MutableCapabilities` when `platforms[]` mixes browsers. YAML `lt:options` values overwrite the ones in code.
- `lambdatest.yml` keys the SDK reads: `username`, `accesskey`, `platforms[]` (`browserName`, `browserVersion`, `platformName`), and `build`, `project`, `name`, `video`, `network`, `console`, `visual`, `resolution`, `tunnel`, `tunnelName`. There are no mobile/device keys: mobile web entries go through path C. There is no `${VAR}` substitution; the docs' `username: ${LT_USERNAME}` works only because the SDK reads the `LT_USERNAME`/`LT_ACCESS_KEY` env vars first. So leave credentials out of the file and set the env vars. For per-run build names generate the file in CI (`envsubst < lambdatest.tmpl.yml > lambdatest.yml`).
- Tunnel: with `tunnel: true` the SDK starts one tunnel per suite; its name comes from the `LT_TUNNEL_NAME` env var or is generated. The tunnel applies to every session in the run, so if only a few tests need it, give them their own suite/config or use path C.
- Gradle (the SDK repo itself builds with Gradle; the docs show Maven only):
  ```groovy
  configurations { ltAgent }
  dependencies {
      testImplementation 'io.github.lambdatest:lambdatest-java-selenium-sdk:1.0.2'   // or the docs coordinates, whichever resolves
      ltAgent 'io.github.lambdatest:lambdatest-java-selenium-sdk:1.0.2'
  }
  test { useTestNG(); jvmArgs "-javaagent:${configurations.ltAgent.singleFile}" }
  ```
- `python3 scripts/convert_caps.py --from browserstack browserstack.yml --emit lambdatest-yml` prints a starting `lambdatest.yml` (Java SDK format, or Playwright SDK format when `framework: playwright`).

Path A details (Node Playwright Test):
- `npm uninstall browserstack-node-sdk`; `npm i -D @lambdatest/playwright-node-sdk`; `npx playwright-node-sdk init` creates `lambdatest.yml`.
- Credentials: leave `user`/`accessKey` out of the file; the SDK reads `LT_USERNAME`/`LT_ACCESS_KEY` env vars, which take precedence. `${VAR}` in the file is not substituted.
- Projects: by default the SDK replaces the `projects` in `playwright.config` with one project per `lambdatest.yml` platform. If the repo relies on setup projects, `dependencies` or `storageState`, set `preserveProjects: true` (keep one browser project; the platform decides the browser; write `storageState` per platform). Source: package README of `@lambdatest/playwright-node-sdk` 1.0.5.
- Keys: `build`, `name`, `projectName`, `buildTags`, `tags`, `parallelsPerPlatform`, `network`, `console`, `video`, `visual`, `tunnel`, `tunnelSettings` (`tunnel`, `autostart`, `tunnelName`; the SDK 1.0.5 code reads only `tunnelSettings`, the `tunnel_settings` spelling on the docs page and in the playwright-bdd sample is stale), `timezone`, `idleTimeout`, `resolution`, `headless`, `playwrightConfigOptions` (`testDir`, `testMatch`, `testIgnore`, `use`, `setup`/`teardown`), `platforms[]` (`platform`, `browserName` chrome/pw-firefox/pw-webkit, `browserVersion`, mobile `deviceName`/`platformVersion`/`isRealMobile`, per-platform `ltOptions` and `playwrightConfigOptions`).
- Scripts: `npx browserstack-node-sdk playwright test` -> `npx playwright-node-sdk playwright test`. A non-default file is selected with the env var `LAMBDATEST_YML_FILE=other.yml`; do not pass `--config` (it goes to Playwright). Remove the BrowserStack `postinstall` hook. A BrowserStack-only fixture file that no spec imports is deleted, not converted.
- `buildIdentifier` (`#${BUILD_NUMBER}`, `${DATE_TIME}`): no equivalent key; set `build` to the plain name and, for per-run builds, generate the yml in CI (`envsubst`).
- Sample: github.com/LambdaTest/playwright-sample/tree/main/playwright-node-sdk.
- If the user prefers no SDK, use the canonical fixture in testmu-target.md §3 (path C for Playwright).

`browserstack.yml` -> `lambdatest.yml` / `LT:Options`:

| browserstack.yml | TestMu |
|---|---|
| `userName`, `accessKey` | `LT_USERNAME`, `LT_ACCESS_KEY` |
| `framework` | drop |
| `platforms[]` (os, osVersion, browserName, browserVersion) | per-platform `LT:Options` entries, or HyperExecute `matrix` |
| `parallelsPerPlatform` | runner parallelism, or HyperExecute `concurrency` |
| `buildName`, `projectName`, `buildIdentifier` | `build`, `project`; `buildIdentifier` becomes a CI var appended to `build` |
| `browserstackLocal`, `browserStackLocalOptions` (capital S; camelCase keys `localIdentifier`, `forceLocal`, `proxyHost`/`proxyPort`/`proxyUser`/`proxyPass`, `pacFile`) | `tunnel`, `tunnelName`; LT binary flags `--proxy-host`, `--pacfile` |
| `debug`, `networkLogs`, `consoleLogs`, `video`, `seleniumLogs` | `visual`, `network`, `console`, `video`, `verboseWebDriverLogging` |
| `geoLocation`, `timezone`, `resolution`, `idleTimeout` | same names (timezone converted) |
| `app` (App Automate) | `app` = `lt://` id after re-upload |
| `percy`, `percyCaptureMode` | SmartUI SDK + `npx smartui exec` |
| `accessibility`, `accessibilityOptions` | `accessibility.*` caps |
| `testObservability` | drop |
| `CUSTOM_TAG_N` | `buildTags` |

Uninstall per language: Node `npm uninstall browserstack-node-sdk` and remove the `*-browserstack` scripts from package.json; Python `pip uninstall browserstack-sdk`, replace `browserstack-sdk pytest` with `pytest`; Java remove `com.browserstack:browserstack-java-sdk` dependency, the `maven-dependency-plugin` `getClasspathFilenames` execution and the surefire `-javaagent` argLine; C# `dotnet remove package BrowserStack.TestAdapter`, run plain `dotnet test`.

## 6. Playwright

BrowserStack uses flat legacy-style caps in the CDP URL; TestMu uses `LT:Options`.

| BrowserStack cap | TestMu |
|---|---|
| `browser` (`chrome`, `edge`, `playwright-chromium`, `playwright-firefox`, `playwright-webkit`) | `browserName` (`Chrome`, `MicrosoftEdge`, `pw-chromium`, `pw-firefox`, `pw-webkit`) |
| `browser_version` | `browserVersion` |
| `os` + `os_version` | `LT:Options.platform` (joined) |
| `browserstack.username` / `browserstack.accessKey` | `LT:Options.user` / `accessKey` |
| `project`, `build`, `name`, `buildTag` | `LT:Options.projectName`, `build`, `name`, `buildTags` |
| `resolution` | `LT:Options.resolution` |
| `browserstack.local` / `localIdentifier` | `tunnel` / `tunnelName` |
| `browserstack.playwrightVersion`, `client.playwrightVersion` | `playwrightClientVersion` (set from installed version) |
| `browserstack.geoLocation` | `geoLocation` |
| `browserstack.networkLogs` | `network` |
| `browserstack.console` | `console` |
| `browserstack.video` | `video` |
| `browserstack.debug` | `visual` |
| `browserstack.maskCommands` | `lambdaMaskCommands` (array) |
| `browserstack.interactiveDebugging` | drop |

Endpoint: `wss://cdp.browserstack.com/playwright?caps=${encodeURIComponent(JSON.stringify(caps))}` -> `wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(JSON.stringify(capabilities))}`.

Status: `page.evaluate(_ => {}, \`browserstack_executor: ${JSON.stringify({action: 'setSessionStatus', arguments: {status: 'passed', reason: 'x'}})}\`)` -> `page.evaluate(_ => {}, \`lambdatest_action: ${JSON.stringify({action: 'setTestStatus', arguments: {status: 'passed', remark: 'x'}})}\`)`. Rename `reason` to `remark`. Python uses `urllib.parse.quote`, Java `URLEncoder.encode`, C# `Uri.EscapeDataString` on both sides, so only the host and key names change.

Playwright Test with the BrowserStack SDK (`browserstack.yml`, `browserstack-node-sdk playwright test`): replace with `@lambdatest/playwright-node-sdk` (`npx playwright-node-sdk init`, `npx playwright-node-sdk playwright test`) or a fixture that calls `chromium.connect` per project.

## 7. Cypress

| browserstack.json | lambdatest-config.json |
|---|---|
| `auth.username` / `auth.access_key` | `lambdatest_auth.username` / `access_key` |
| `browsers[].browser` | `browsers[].browser` (capitalise: `chrome` -> `Chrome`) |
| `browsers[].os` (`Windows 10`, `OS X Mojave`) | `browsers[].platform` (`Windows 10`, `macOS Mojave`) |
| `browsers[].versions` | `browsers[].versions` |
| `run_settings.cypress_config_file` | `run_settings.cypress_config_file` |
| `run_settings.cypress_version` | `run_settings.npm_dependencies.cypress` |
| `run_settings.project_name` | `run_settings.project_name` |
| `run_settings.build_name` | `run_settings.build_name` |
| `run_settings.build_tag` | `run_settings.tags` |
| `run_settings.parallels` | `run_settings.parallels` |
| `run_settings.specs` | `run_settings.specs` (glob string) |
| `run_settings.exclude` | `run_settings.ignore_files` |
| `run_settings.npm_dependencies` | `run_settings.npm_dependencies` |
| `run_settings.headless` | `run_settings.headless` |
| `run_settings.nodeVersion` (`18.17.0`) | `run_settings.useNodeVersion` (`18`) |
| `run_settings.network_logs` | `run_settings.network` |
| `run_settings.geolocation` / `timezone` | `run_settings.geo_location` / `--tz` flag |
| `run_settings.record`, `record-key`, `projectId` | keep in cypress config if Cypress Cloud stays; otherwise drop |
| `run_settings.spec_timeout` | `run_settings.max_duration` (minutes) |
| `connection_settings.local` / `local_identifier` / `local_mode` | `tunnel_settings.tunnel` / `tunnel_name` / `autostart` |
| `disable_usage_reporting` | drop |
| `run_settings.enforce_settings`, `home_directory`, `system_env_vars`, `package_config_options`, `interactiveDebugging` | `system_env_vars` -> `--sys-envs`; others drop |
| `run_settings.networkLogsOptions.captureContent` | `run_settings.network: true` |
| `connection_settings.local_config_file` | LT tunnel `--config` file |

CLI: `browserstack-cypress init|run|build-info|build-stop` -> `lambdatest-cypress init|run|build-info --id|build-stop --id`. `npm uninstall browserstack-cypress-cli && npm i -D lambdatest-cypress-cli`. Percy snapshots (`cy.percySnapshot`) become `cy.smartuiSnapshot` with `@lambdatest/cypress-driver`.

## 8. App Automate (Appium)

Re-upload every app: `bs://<hash>` ids do not transfer.
```
# BrowserStack
curl -u "U:K" -X POST "https://api-cloud.browserstack.com/app-automate/upload" -F "file=@app.apk" -F "custom_id=MyApp"
# TestMu
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" -F "appFile=@app.apk" -F "name=MyApp"
```
Form field `file` -> `appFile`; `custom_id` -> `name` (and `custom_id` also exists on TestMu for URL uploads). Response `app_url: bs://...` -> `app_url: lt://...`.

| BrowserStack (W3C) | TestMu |
|---|---|
| `platformName` (`android`/`ios`) | `platformName` (`Android`/`iOS`) |
| `deviceName` (`Samsung Galaxy S23`, `Google Pixel 7`) | `deviceName` (`Galaxy S23`, `Pixel 7`); verify against device list API |
| `platformVersion` | `platformVersion` |
| `app` (`bs://...` or custom_id) | `app` (`lt://...`) |
| `automationName` | `automationName` |
| `otherApps` | `otherApps` (lt:// ids) |
| `autoGrantPermissions`, `autoAcceptAlerts`, `autoDismissAlerts`, `language`, `locale` | same names |
| `disableAnimations` | `disableAnimation` (singular) |
| `bstack:options.appiumVersion` | `appiumVersion` (TestMu supports it on real devices: Android 1.21.0 to 3.0.2, iOS 15+ 1.22.3 to 3.0.2, default 2.2.1; check the version is in that list) |
| `bstack:options.projectName`, `buildName`, `sessionName`, `buildTag` | `project`, `build`, `name`, `buildTags` |
| `bstack:options.local` / `localIdentifier` | `tunnel` / `tunnelName` |
| `bstack:options.debug` | `visual` |
| `bstack:options.deviceLogs` | `devicelog` (lowercase l) |
| `bstack:options.appiumLogs` | drop (always on) |
| `bstack:options.networkLogs` | `network` |
| `bstack:options.video` | `video` |
| `bstack:options.gpsLocation` (`lat,long`) | `location` (flag; verify format) |
| `bstack:options.geoLocation` | `geoLocation` |
| `bstack:options.networkProfile` / `customNetwork` | `lambda-throttle-network` hook |
| `bstack:options.resignApp` | `resignApp` |
| `bstack:options.timezone` | `timezone` (UTC offset) |
| `bstack:options.enablePasscode` | drop |
| `bstack:options.deviceOrientation` | `deviceOrientation` |
| `bstack:options.idleTimeout` | `idleTimeout` |
| `bstack:options.maskCommands` | `lambdaMaskCommands` |
| `bstack:options.uploadMedia` (`media://`) | `media` (re-upload media) |
| `bstack:options.midSessionInstallApps` | `otherApps` |
| `bstack:options.acceptInsecureCerts` | `acceptInsecureCerts` |
| `bstack:options.interactiveDebugging`, `appProfiling` | drop |
| (no equivalent) | add `isRealMobile: true` for real devices, `false` for emulator/simulator |

Hub `hub.browserstack.com/wd/hub` -> `mobile-hub.lambdatest.com/wd/hub`. Java `UiAutomator2Options`/`XCUITestOptions` + `AndroidDriver`/`IOSDriver` stay identical; only caps and URL change.

## 9. Espresso / XCUITest

| BrowserStack | TestMu |
|---|---|
| `POST /app-automate/espresso/v2/app` (`file`) | `POST https://manual-api.lambdatest.com/app/uploadFramework` (`appFile`, `type=espresso-android`) |
| `POST /app-automate/espresso/v2/test-suite` | same endpoint for the test APK |
| `POST /app-automate/espresso/v2/build` `{"app","testSuite","devices":["Google Pixel 7-13.0"]}` | `POST https://mobile-api.lambdatest.com/framework/v1/espresso/build` `{"app","testSuite","device":["Pixel 7-13"],"build","deviceLog","network","queueTimeout"}` |
| XCUITest `/xcuitest/v2/*` | `type=xcuit-ios`, `POST .../framework/v1/xcui/build` |

Key rename: `devices` -> `device`. Device string format stays `<name>-<version>`, but names drop the vendor prefix.

## 10. BrowserStack Local to LT Tunnel

| BrowserStack Local | LT Tunnel |
|---|---|
| `./BrowserStackLocal --key KEY --local-identifier ID` | `./LT --user $LT_USERNAME --key $LT_ACCESS_KEY --tunnelName ID` |
| `--force-local` | `--ingress-only` is the closest (routes all traffic through tunnel); otherwise drop |
| `--only-automate` | drop |
| `--proxy-host/--proxy-port/--proxy-user/--proxy-pass` | `--proxy-host/--proxy-port/--proxy-user/--proxy-pass` |
| `--pac-file` | `--pacfile` |
| `--folder` | `--dir` |
| `--verbose N` | `--verbose` |
| `--log-file` | `--logFile` |
| `--daemon start` | run in background; `--infoAPIPort` to check |
| `--config-file file.yml` | `--config .lt.yaml` |
| `--use-ca-certificate` | `--clientCert` / `--mitm` |
| `--parallel-runs N` | `--maxSSHConnections` |
| npm `browserstack-local` `new Local().start({key, localIdentifier, ...})` | `@lambdatest/node-tunnel` `new lambdaTunnel().start({user, key, tunnelName, ...})` |
| pip `browserstack-local` `Local().start(...)` | run the LT binary via subprocess (no official pip package verified) |
| Maven `browserstack-local-java` (`com.browserstack.local.Local`) | Maven `com.github.lambdatest:lambdatest-tunnel-binary` (4.0.2 in the docs): `import com.lambdatest.tunnel.Tunnel; Tunnel t = new Tunnel(); HashMap<String,String> args = new HashMap<>(); args.put("user", ...); args.put("key", ...); args.put("tunnelName", ...); t.start(args); ... t.stop();` (maven-tunnel-for-locally-hosted-web-applications) |
| NuGet `BrowserStackLocal` (C#, `new Local().start(...)`) | no TestMu NuGet package is documented: start the LT binary with `System.Diagnostics.Process` (`LT.exe --user ... --key ... --tunnelName X --infoAPIPort 8000`), poll `http://127.0.0.1:8000/api/v1.0/info` until it answers, stop with `DELETE /api/v1.0/stop`; or start the tunnel in CI before `dotnet test` and drop the in-process code |
| wdio `browserstackLocal: true, opts: {localIdentifier}` | `services: [['lambdatest', { tunnel: true, lambdatestOpts: { tunnelName: 'X', logFile: 'tunnel.log' } }]]`; the service starts the tunnel and sets `tunnel`/`tunnelName` in every capability itself (wdio-lambdatest-service launcher source) |

Caps: `local: true, localIdentifier: X` -> `tunnel: true, tunnelName: X`. The `bs-local.com` hostname trick for websocket/local domains is not needed; use `localhost` through the tunnel.
- BrowserStack samples test `http://bs-local.com:45454/`, a page served by the BrowserStackLocal binary itself. The LT tunnel serves no such page. Change only the URL (to a server the team runs, read from an env var such as `LOCAL_TEST_URL`); leave the assertion as it is and add `TODO(testmu-migration): assertion checks the BrowserStack Local test page title; update it for the real local page`. Do not rewrite assertions yourself.
- Apps built to call BrowserStack Local endpoints (sample apps with "Test BrowserStack Local" buttons that hit `bs-local.com`) still need a reachable host through the tunnel; flag them rather than renaming accessibility ids.
- Enable `tunnel` only on sessions that need private hosts; the sample repos often set `browserstackLocal: true` globally.

## 11. browserstack_executor to lambda hooks

Selenium/Appium (JS executor string):

| BrowserStack | TestMu |
|---|---|
| `browserstack_executor: {"action":"setSessionStatus","arguments":{"status":"passed","reason":"r"}}` | `lambda-status=passed` and optionally `lambda-action=r` |
| `setSessionStatus` `failed` | `lambda-status=failed` |
| `setSessionName` `{"name":"n"}` | `lambda-name=n` |
| `annotate` `{"data":"d","level":"info"}` | `lambda-testCase-start=d` / `lambda-testCase-end` (step markers), or `lambda-exceptions` for errors |
| `fileExists` `{"fileName":"f"}` | `lambda-file-exists=f` |
| `getFileProperties` | `lambda-file-stats=f` |
| `getFileContent` | `lambda-file-content=f` |
| `LocalFileDetector` + sendKeys upload | same Selenium mechanism works; or `lambda:userFiles` cap |

Playwright/Puppeteer: `browserstack_executor: {"action":"setSessionStatus",...}` -> `lambdatest_action: {"action":"setTestStatus","arguments":{"status":"passed","remark":"..."}}`.

REST fallback: `PUT https://api.browserstack.com/automate/sessions/{id}.json {"status":"passed"}` -> `PATCH https://api.lambdatest.com/automation/api/v1/sessions/{id}` (confirm body field in Swagger).

## 12. Other frameworks

WebdriverIO: `services: [['browserstack', {...}]]`, `hostname: 'hub.browserstack.com'`, `user: BROWSERSTACK_USERNAME`, `key: BROWSERSTACK_ACCESS_KEY` -> `npm uninstall @wdio/browserstack-service && npm i -D wdio-lambdatest-service`; `services: [['lambdatest', { tunnel: true }]]`, `hostname: 'hub.lambdatest.com'`, `port: 80`, `path: '/wd/hub'`, `user: LT_USERNAME`, `key: LT_ACCESS_KEY`. Capabilities `'bstack:options': {...}` -> `'LT:Options': {...}` using §3. Service options `buildIdentifier`, `testObservability*`/`testReporting*`, `percy*`, `turboScale`, `sessionNameFormat`, `preferScenarioName` drop; `opts` (BrowserStack Local options) -> `lambdatestOpts` (passed to `@lambdatest/node-tunnel`); `app` (auto-upload) -> the lambdatest service uploads too: `app_upload: true, app: { app_name, app_path | app_url, custom_id, enableCapability: true }` sets `app` in the capabilities, or upload in CI and set `app: lt://...`. Use `wdio-lambdatest-service` 4.x (peer range covers WebdriverIO 7, 8 and 9). Mixed desktop and real-device capabilities in one config: WebdriverIO accepts `hostname`/`port`/`path`/`protocol` inside an individual capability entry, so give the device entries `hostname: 'mobile-hub.lambdatest.com'`; if that is awkward, split into `wdio.web.conf.js` and `wdio.mobile.conf.js`. Port 80 with `protocol: 'http'` is what the docs show; `protocol: 'https', port: 443` keeps credentials off plain HTTP and is the safer default where corporate proxies allow it. `setSessionName`/`setSessionStatus` are handled by the lambdatest service.

Puppeteer: `wss://cdp.browserstack.com/puppeteer?caps=` -> `wss://cdp.lambdatest.com/puppeteer?capabilities=`; caps per §6 table.

TestCafe: `testcafe "browserstack:Chrome@120:Windows 11"` -> `testcafe "lambdatest:Chrome@120:Windows 11"`; provider `testcafe-browser-provider-browserstack` -> `testcafe-browser-provider-lambdatest`. Env: `BROWSERSTACK_USERNAME` -> `LT_USERNAME`, `BROWSERSTACK_ACCESS_KEY` -> `LT_ACCESS_KEY`, `BROWSERSTACK_BUILD_ID` or `BROWSERSTACK_BUILD_NAME` -> `LT_BUILD`, `BROWSERSTACK_LOGFILE` -> `LT_LOGFILE`, `BROWSERSTACK_VERBOSE` -> `LT_VERBOSE`, `BROWSERSTACK_PROXY` -> `LT_PROXY_HOST`/`LT_PROXY_PORT`, `BROWSERSTACK_TEST_RUN_NAME` -> `LT_TEST_NAME`, `BROWSERSTACK_DISPLAY_RESOLUTION` -> `LT_RESOLUTION`, `BROWSERSTACK_LOCAL_IDENTIFIER` -> `LT_TUNNEL_NAME`, `BROWSERSTACK_CAPABILITIES_CONFIG_PATH` -> `LT_CAPABILITY_PATH`, `BROWSERSTACK_CONSOLE` -> `LT_CONSOLE`, `BROWSERSTACK_NETWORK_LOGS` -> `LT_NETWORK`, `BROWSERSTACK_VIDEO` -> `LT_VIDEO`, `BROWSERSTACK_TIMEZONE` -> `LT_TIMEZONE`, `BROWSERSTACK_DEBUG` -> `LT_VISUAL` (or `LT_SCREENSHOT`). `BROWSERSTACK_USE_AUTOMATE`, `BROWSERSTACK_PROJECT_NAME`, `BROWSERSTACK_GEO_LOCATION`, `BROWSERSTACK_CUSTOM_NETWORK` have no TestCafe-provider equivalent on TestMu; pass via `LT_CAPABILITY_PATH` JSON.

Nightwatch: `plugins: ['@nightwatch/browserstack']` -> remove; `selenium.host: 'hub.browserstack.com', port: 443` -> `host: 'hub.lambdatest.com', port: 80` (or 443 with `use_ssl`); `desiredCapabilities['bstack:options']` -> `['LT:Options']`.

Robot Framework: SDK (`browserstack-sdk robot`) -> plain `robot` with `remote_url=https://%{LT_USERNAME}:%{LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub` and `desired_capabilities` built per §3.

Protractor: `browserstackUser`/`browserstackKey` -> `seleniumAddress: 'https://' + LT_USERNAME + ':' + LT_ACCESS_KEY + '@hub.lambdatest.com/wd/hub'`; `commonCapabilities['browserstack.debug']` -> `'LT:Options': { visual: true }`.

Capybara: `server: hub-cloud.browserstack.com` -> `hub.lambdatest.com`; YAML `common_caps` keys per §3.

## 13. Percy, Accessibility, Test Observability

Percy -> SmartUI: use the `percy-migration-skill` skill for the full mapping (CLI, `.percy.yml`, every SDK, App Percy, Storybook, baselines). Quick reference: `percySnapshot(driver, 'name')` -> Java `SmartUISnapshot.smartuiSnapshot(driver, "name")`, Python `smartui_snapshot(driver, "name")`, Node Playwright `smartuiSnapshot(page, "name")`, Cypress `cy.smartuiSnapshot('name')`; wrap the run in `npx smartui --config .smartui.json exec -- <cmd>` with `PROJECT_TOKEN`. Percy on Automate (caps-driven, `percyScreenshot`) -> SmartUI hooks mode: caps `smartUI.project`, `smartUI.build`, `smartUI.baseline`, and `driver.executeScript("smartui.takeScreenshot=name")`. Baselines must be rebuilt on SmartUI; schedule a baseline run first.

Accessibility: yml `accessibility: true`, `accessibilityOptions.wcagVersion: wcag21aa`, `includeIssueType.bestPractice/needsReview`, `autoScanning` -> LT:Options `accessibility: true`, `accessibility.wcagVersion: "wcag21aa"`, `accessibility.bestPractice`, `accessibility.needsReview`, `accessibility.autoscan`. Manual scan `driver.executeScript("lambda-accessibility-scan")`.

Test Observability / Test Reporting & Analytics: no config to migrate; TestMu dashboard and Test Manager cover builds, sessions, logs, video. If the team used Observability for tests run outside BrowserStack, flag that as a gap.

## 14. REST API

| BrowserStack | TestMu |
|---|---|
| `GET /automate/builds.json` | `GET /automation/api/v1/builds` |
| `GET /automate/builds/{id}.json` | `GET /automation/api/v1/builds/{id}` |
| `GET /automate/builds/{id}/sessions.json` | `GET /automation/api/v1/sessions?build_id={id}` |
| `GET /automate/sessions/{id}.json` | `GET /automation/api/v1/sessions/{id}` |
| `PUT /automate/sessions/{id}.json {"status","reason","name"}` | `PATCH /automation/api/v1/sessions/{id}` |
| `GET /automate/sessions/{id}/networklogs` | `GET /automation/api/v1/sessions/{id}/log/network.har` |
| `GET /automate/sessions/{id}/consolelogs` | `.../log/console` |
| `GET /automate/sessions/{id}/seleniumlogs` | `.../log/selenium` |
| `video_url` field | `GET /automation/api/v1/sessions/{id}/video` |
| `GET /automate/browsers.json` | `GET /automation/api/v1/platforms` |
| `GET /app-automate/recent_apps` | `GET https://manual-api.lambdatest.com/app/data` |
| `DELETE /app-automate/app/delete/{id}` | `DELETE https://manual-api.lambdatest.com/app/delete` |

Base host `api.browserstack.com` -> `api.lambdatest.com`; `.json` suffixes go away; Basic auth stays.

## 15. Value translation

os + osVersion to platformName:
- `Windows` + `11|10|8.1|8|7` -> `Windows 11|10|8.1|8|7`
- `OS X` + codename -> `macOS <codename>` (`Sonoma`, `Ventura`, `Monterey`, `Big Sur`, `Catalina`, `Mojave`, `Sequoia`); `Tahoe` -> `MacOS Tahoe` (seen in samples, not on the capabilities page). Pre-Mojave codenames: check TestMu platform list; fall back to nearest supported.
- Cypress strings `Windows 10` stay; `OS X Mojave` -> `macOS Mojave`.

Browser names: `Chrome`/`chrome` -> `Chrome`; `Edge`/`edge` -> `MicrosoftEdge`; `Firefox` -> `Firefox`; `Safari` -> `Safari`; `IE` -> `Internet Explorer`; `chromefortesting` -> flag.

Device names: strip vendor prefix. `Samsung Galaxy S23` -> `Galaxy S23`; `Google Pixel 7` -> `Pixel 7`; `iPhone 14` -> `iPhone 14`; `iPad Air 6` -> `iPad Air 6`. Android versions `13.0` -> `13`; iOS `17` -> `17`. Always confirm with `GET https://mobile-api.lambdatest.com/mobile-automation/api/v1/list`.

Timezone: BrowserStack city names -> TestMu UTC offsets. `New_York` -> `UTC-05:00` (or `UTC-04:00` in DST), `London` -> `UTC+00:00`, `Kolkata` -> `UTC+05:30`, `Tokyo` -> `UTC+09:00`, `Los_Angeles` -> `UTC-08:00`, `Berlin` -> `UTC+01:00`, `Sydney` -> `UTC+10:00`. Flag DST-sensitive tests.

Status values: `passed`/`failed` are identical.

## 16. Gotchas

- `bstack:options` left anywhere in the caps is ignored by TestMu, so a half-migrated file fails silently with default Chrome on default OS. Grep for leftovers after editing.
- BrowserStack defaults `video: true` and `consoleLogs: errors`; TestMu defaults `video: true`, `console: false`, `network: false`. Set `network: true` and `console: true` explicitly if the team relied on those logs.
- `timezone` format differs completely (city vs UTC offset).
- `debug` means screenshots, not verbose logging; map it to `visual`.
- The SDK hid the hub URL and caps from the code. After removing it, every driver factory must build caps explicitly, and `sessionName` auto-population is gone; use `lambda-name=` in a `@BeforeEach`/fixture.
- Percy baselines and BrowserStack app ids (`bs://`) do not transfer. Re-upload apps and re-baseline SmartUI.
- Cypress `browsers[].os` becomes `browsers[].platform` and `exclude` becomes `ignore_files` in lambdatest-config.json.
- Playwright CDP param is `capabilities=`, not `caps=`; the JSON shape also changes from flat to `LT:Options`.
- Sources at research time (26 Oct 2026): browserstack.com/docs, browserstack.com/automate/capabilities, browserstack/app-automate/capabilities, github.com/browserstack sample repos. Many BrowserStack doc pages block automated fetches; the GitHub samples are the reliable fallback.
