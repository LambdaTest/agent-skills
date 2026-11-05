# TestMu AI target reference

Everything a migrated suite needs to point at TestMu AI (formerly LambdaTest; rebranded 12 Jan 2026). Hostnames, env vars and capability names did not change in the rebrand, so `lambdatest.com` hosts and `LT_*` variables are still correct. Every doc page has a Markdown twin at `<url>.md`, and a machine index at `https://www.testmuai.com/support/docs/llms.txt`.

Contents
1. Credentials and endpoints
2. Selenium: LT:Options reference and per-language snippets
3. Playwright
4. Cypress
5. Appium (real and virtual devices)
6. Puppeteer, WebdriverIO, TestCafe, Nightwatch, Robot, Espresso, XCUITest
7. Tunnel (localhost testing)
8. Test status and lambda hooks
9. HyperExecute (orchestration)
10. SmartUI (visual) and Accessibility
11. REST API
12. Naming conventions and values
13. Unverified items

## 1. Credentials and endpoints

| Item | Value |
|---|---|
| Env vars | `LT_USERNAME`, `LT_ACCESS_KEY` (dashboard > Credentials, https://accounts.lambdatest.com/security) |
| Selenium hub | `https://hub.lambdatest.com/wd/hub` (or `https://{LT_USERNAME}:{LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub`) |
| Appium hub | `https://mobile-hub.lambdatest.com/wd/hub` |
| Playwright CDP | `wss://cdp.lambdatest.com/playwright?capabilities=<urlencoded JSON>` |
| Puppeteer CDP | `wss://cdp.lambdatest.com/puppeteer?capabilities=<urlencoded JSON>` |
| App upload | `https://manual-api.lambdatest.com/app/upload/realDevice` (also `/virtualDevice`) |
| Automation REST | `https://api.lambdatest.com/automation/api/v1` (EU: `https://eu-api.lambdatest.com/automation/api/v1`) |
| Capabilities generator | https://www.testmuai.com/capabilities-generator/ |
| Docs root | https://www.testmuai.com/support/docs/ |

Capability values are case-insensitive and space-insensitive on the TestMu side (`Windows 11` and `windows11` both work), which is why sloppy source values usually survive a straight copy.

## 2. Selenium

Selenium 4 shape: W3C keys (`browserName`, `browserVersion`, `platformName`) on the browser Options object or top-level, everything TestMu-specific inside the `LT:Options` object.

### LT:Options keys

| Key | Type | Default | Notes |
|---|---|---|---|
| `username` / `user` | string | required | official samples use both spellings; prefer `username` |
| `accessKey` | string | required | |
| `platformName` | string | auto | `Windows 11`, `Windows 10`, `macOS Sonoma` ... (see §12; Linux is not in the documented list) |
| `browserVersion` | string | `latest` | `latest-1`, `latest-2`, or a number |
| `selenium_version` | string | dynamic | e.g. `4.0.0` |
| `driver_version` | string | dynamic | |
| `resolution` | string | `1024x768` | `1280x800`, `1366x768`, `1920x1080`, `2048x1536` |
| `build` | string | `Untitled Build` | < 255 chars |
| `name` | string | | test name, <= 255 chars |
| `project` / `projectName` | string | `Untitled` | both appear in official material |
| `tags` | string[] | | <= 50 chars each |
| `buildTags` | string[] | | |
| `video` | bool | true | |
| `visual` | bool | false | step screenshots |
| `network` | bool | false | HAR capture |
| `console` | bool | false | `true`/`false` (docs also show `"disable"`); log levels are not documented |
| `tunnel` | bool | false | |
| `tunnelName` | string | | pairs with `tunnel: true` |
| `timezone` | string | `UTC+00:00` | format `UTC+HH:MM`, case-sensitive |
| `geoLocation` | string | | ISO country code (`US`, `FR`) |
| `idleTimeout` | int sec | 600 | |
| `queueTimeout` | int sec | 600 | documented for Appium (300 to 900); not documented for web sessions, so leave it out of web caps |
| `w3c` | bool | | samples set `true` |
| `headless` | bool | false | documented; no video for headless sessions |
| `verboseWebDriverLogging` | bool | false | |
| `network.mask`, `network.http2`, `network.debug`, `network.full.har` | bool | false | |
| `commandLog`, `systemLog` | bool | false | |
| `updateBuildStatusOnSuccess` | bool | false | |
| `lambda:loadExtension` | string[] | | uploaded extension zip URLs |
| `lambda:userFiles` | string | | uploaded file name |
| `smartUI.project`, `smartUI.build`, `smartUI.baseline`, `smartUI.options` | | | see §10 |
| `accessibility`, `accessibility.autoscan`, `accessibility.wcagVersion`, `accessibility.bestPractice`, `accessibility.needsReview` | | | see §10 |
| `customData` | object | | arbitrary metadata |
| `plugin` | string | | sample telemetry, e.g. `python-python` |

Selenium 3 / legacy flat keys: `browserName`, `version`, `platform`, `resolution`, `name`, `build`, `projectName`, `tags`, `buildTags`, plus the debugging keys above as flat caps.

### Snippets

Java:
```java
ChromeOptions options = new ChromeOptions();
options.setPlatformName("Windows 11");
options.setBrowserVersion("latest");
HashMap<String, Object> lt = new HashMap<>();
lt.put("username", System.getenv("LT_USERNAME"));
lt.put("accessKey", System.getenv("LT_ACCESS_KEY"));
lt.put("project", "My Project");
lt.put("build", "Build 1");
lt.put("name", "Login test");
lt.put("w3c", true);
lt.put("video", true);
lt.put("network", true);
options.setCapability("LT:Options", lt);
WebDriver driver = new RemoteWebDriver(new URL("https://hub.lambdatest.com/wd/hub"), options);
((JavascriptExecutor) driver).executeScript("lambda-status=passed");
```

Python:
```python
options = webdriver.ChromeOptions()
options.browser_version = "latest"
options.platform_name = "Windows 10"
options.set_capability("LT:Options", {
    "username": os.getenv("LT_USERNAME"), "accessKey": os.getenv("LT_ACCESS_KEY"),
    "build": "Build 1", "name": "Login test", "project": "My Project",
    "video": True, "network": True, "w3c": True,
})
driver = webdriver.Remote(command_executor="https://hub.lambdatest.com/wd/hub", options=options)
driver.execute_script("lambda-status=passed")
```

Node (selenium-webdriver):
```js
const capabilities = {
  browserName: "Chrome", browserVersion: "latest",
  "LT:Options": { platformName: "Windows 11", build: "Build 1", name: "Login test", project: "My Project", w3c: true, video: true },
};
const gridUrl = `https://${process.env.LT_USERNAME}:${process.env.LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub`;
const driver = await new Builder().usingServer(gridUrl).withCapabilities(capabilities).build();
await driver.executeScript("lambda-status=passed");
```

C# (pattern; official page not reachable at research time):
```csharp
var options = new ChromeOptions { BrowserVersion = "latest", PlatformName = "Windows 11" };
var lt = new Dictionary<string, object> {
  {"username", Environment.GetEnvironmentVariable("LT_USERNAME")},
  {"accessKey", Environment.GetEnvironmentVariable("LT_ACCESS_KEY")},
  {"build", "Build 1"}, {"name", "Login test"}, {"w3c", true}
};
options.AddAdditionalOption("LT:Options", lt);
var driver = new RemoteWebDriver(new Uri("https://hub.lambdatest.com/wd/hub"), options);
((IJavaScriptExecutor)driver).ExecuteScript("lambda-status=passed");
```

Ruby:
```ruby
options = Selenium::WebDriver::Options.chrome(browser_version: 'latest', platform_name: 'Windows 11')
options.add_option('LT:Options', { 'username' => ENV['LT_USERNAME'], 'accessKey' => ENV['LT_ACCESS_KEY'], 'build' => 'Build 1', 'name' => 'Login test', 'w3c' => true })
driver = Selenium::WebDriver.for(:remote, url: 'https://hub.lambdatest.com/wd/hub', options: options)
driver.execute_script('lambda-status=passed')
```

PHP (php-webdriver):
```php
$caps = DesiredCapabilities::chrome();
$caps->setCapability('browserVersion', 'latest');
$caps->setCapability('LT:Options', ['username' => getenv('LT_USERNAME'), 'accessKey' => getenv('LT_ACCESS_KEY'), 'platformName' => 'Windows 11', 'build' => 'Build 1', 'name' => 'Login test', 'w3c' => true]);
$driver = RemoteWebDriver::create('https://hub.lambdatest.com/wd/hub', $caps);
$driver->executeScript('lambda-status=passed');
```

Go (tebeka/selenium; no official TestMu page, pattern only):
```go
caps := selenium.Capabilities{"browserName": "chrome", "browserVersion": "latest",
  "LT:Options": map[string]interface{}{"username": os.Getenv("LT_USERNAME"), "accessKey": os.Getenv("LT_ACCESS_KEY"), "platformName": "Windows 11", "build": "Build 1", "name": "Login test", "w3c": true}}
wd, err := selenium.NewRemote(caps, "https://hub.lambdatest.com/wd/hub")
wd.ExecuteScript("lambda-status=passed", nil)
```

## 3. Playwright

Connect: `wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(JSON.stringify(capabilities))}`

Top-level: `browserName` (`Chrome`, `MicrosoftEdge`, `pw-chromium`, `pw-firefox`, `pw-webkit`), `browserVersion` (`latest`; Chrome/Edge 83+), `LT:Options`.

`LT:Options` for Playwright: `platform` (note: `platform`, not `platformName`), `build`, `name`, `projectName`, `tags`, `buildTags`, `user`, `accessKey`, `resolution` (default `1920x1080`), `network`, `console`, `video`, `visual`, `tunnel`, `tunnelName`, `geoLocation`, `idleTimeout` (default 300, max 1800), `lambdaMaskCommands` (`sendType`, `sendFill`, `sendPress`, `setHTTPCredentials`, `setStorageState`, `setGeolocation`), `useSpecificBundleVersion`, `playwrightClientVersion`. Android real devices: connect with `_android.connect(wsEndpoint)` (not `chromium.connect`), then `device.launchBrowser()`; `LT:Options` carries `platformName: "android"`, `deviceName`, `platformVersion`, `isRealMobile: true` and no `browserName` (official sample `playwright-sample/playwright-test-js/lambdatest-setup.js`). iOS real devices: `playwright-ios-real-device.js` in the same repo; iOS always uses webkit.

Status: `page.evaluate("_ => {}", 'lambdatest_action: {"action": "setTestStatus", "arguments": {"status":"passed","remark":"..."}}')`. Without it the session shows "Completed".

Node/TS:
```js
const capabilities = { browserName: "Chrome", browserVersion: "latest",
  "LT:Options": { platform: "Windows 11", build: "Build 1", name: "Login test",
    user: process.env.LT_USERNAME, accessKey: process.env.LT_ACCESS_KEY, network: true, video: true, console: true } };
const browser = await chromium.connect({ wsEndpoint: `wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(JSON.stringify(capabilities))}` });
await page.evaluate(_ => {}, `lambdatest_action: ${JSON.stringify({ action: "setTestStatus", arguments: { status: "passed", remark: "ok" } })}`);
```

Python:
```python
lt_cdp_url = "wss://cdp.lambdatest.com/playwright?capabilities=" + urllib.parse.quote(json.dumps(capabilities))
browser = playwright.chromium.connect(lt_cdp_url)
page.evaluate("_ => {}", 'lambdatest_action: {"action": "setTestStatus", "arguments": {"status":"passed","remark":"ok"}}')
```

Java:
```java
String caps = URLEncoder.encode(capabilities.toString(), "utf-8");
Browser browser = playwright.chromium().connect("wss://cdp.lambdatest.com/playwright?capabilities=" + caps);
```

C#:
```csharp
string cdpUrl = "wss://cdp.lambdatest.com/playwright?capabilities=" + Uri.EscapeDataString(JsonConvert.SerializeObject(capabilities));
await using var browser = await playwright.Chromium.ConnectAsync(cdpUrl);
```

Playwright Test runner: override the test-scoped `page` fixture (never `browser`: it is worker-scoped, so its third argument is WorkerInfo, every test in a worker would share one TestMu session, and per-test names and statuses would be lost). Canonical fixture, adapted from the official sample `github.com/LambdaTest/playwright-sample/playwright-test-js/lambdatest-setup.js`:

```js
// lambdatest-setup.js  (npm i -D @playwright/test playwright)
const base = require('@playwright/test');
const { chromium, _android } = require('playwright');
const { execSync } = require('child_process');
const pwVersion = execSync('npx playwright --version').toString().trim().split(' ')[1];

// Project names encode the target: "Chrome:latest:Windows 11@lambdatest", "pw-webkit:latest:macOS Sonoma@lambdatest", "Pixel 8:14:android@lambdatest"
function capsFor(projectName, testName) {
  const [a, b, c] = projectName.split('@lambdatest')[0].split(':');
  const lt = { build: process.env.LT_BUILD || 'local', name: testName, user: process.env.LT_USERNAME, accessKey: process.env.LT_ACCESS_KEY,
    network: true, video: true, console: true, tunnel: !!process.env.LT_TUNNEL_NAME, tunnelName: process.env.LT_TUNNEL_NAME || '',
    playwrightClientVersion: pwVersion };
  if (/android/i.test(c || '')) return { 'LT:Options': { ...lt, deviceName: a, platformVersion: b, platformName: 'android', isRealMobile: true } };
  return { browserName: a || 'Chrome', browserVersion: b || 'latest', 'LT:Options': { ...lt, platform: c || 'Windows 11' } };
}

exports.test = base.test.extend({
  page: async ({ page }, use, testInfo) => {
    if (!testInfo.project.name.includes('@lambdatest')) { await use(page); return; } // local projects run unchanged
    const caps = capsFor(testInfo.project.name, `${testInfo.title} - ${testInfo.file.split(/[\\/]/).pop()}`);
    const ws = `wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(JSON.stringify(caps))}`;
    let ltPage, close;
    if (caps.browserName) {
      const browser = await chromium.connect(ws);
      ltPage = await browser.newPage(testInfo.project.use); // keeps baseURL, viewport, storageState
      close = () => browser.close();
    } else {
      const device = await _android.connect(ws);
      const context = await device.launchBrowser();
      ltPage = await context.newPage(testInfo.project.use);
      close = async () => { await context.close(); await device.close(); };
    }
    await use(ltPage);
    const status = testInfo.status === testInfo.expectedStatus ? 'passed' : 'failed';
    await ltPage.evaluate(() => {}, `lambdatest_action: ${JSON.stringify({ action: 'setTestStatus', arguments: { status, remark: testInfo.error?.message || 'ok' } })}`);
    await ltPage.close();
    await close();
  },
});
exports.expect = base.expect;
```
Projects in `playwright.config`: `{ name: 'Chrome:latest:Windows 11@lambdatest', use: { baseURL } }`, `{ name: 'pw-webkit:latest:macOS Sonoma@lambdatest' }`, `{ name: 'Pixel 8:14:android@lambdatest' }`; specs import `test`/`expect` from `./lambdatest-setup` instead of `@playwright/test`. Alternative with no spec changes: the Node SDK `npm i -D @lambdatest/playwright-node-sdk`, `npx playwright-node-sdk init` (writes `lambdatest.yml`), `npx playwright-node-sdk playwright test`.

## 4. Cypress

Package `lambdatest-cypress-cli` (bin `lambdatest-cypress`). `npm i -D lambdatest-cypress-cli`; `npx lambdatest-cypress init` writes `lambdatest-config.json`, `base_reporter_config.json`, `custom_support_file.js`; `npx lambdatest-cypress run`; `build-info --id`, `build-stop --id`, `generate-report`. Supports Cypress 9 and below and 10 and above. Node runtime via `run_settings.useNodeVersion` (`18`, `20`, `22`; CLI `--nodeV`).

```json
{
  "browsers": [ { "browser": "Chrome", "platform": "Windows 11", "versions": ["latest"] } ],
  "run_settings": {
    "build_name": "Build 1", "parallels": 2,
    "specs": "./cypress/e2e/**/*.cy.js", "ignore_files": "", "exclude_specs": "",
    "npm_dependencies": { "cypress": "13.13.0" },
    "headless": true, "network": true, "video": true, "geo_location": "", "resolution": "1920x1080",
    "max_duration": 60, "project_name": "", "tags": [], "useNodeVersion": "20",
    "reporter_config_file": "base_reporter_config.json",
    "smart_ui": { "project": "", "build": "", "baseline": false }
  },
  "tunnel_settings": { "tunnel": false, "tunnel_name": null, "autostart": false }
}
```

Notes: `browsers[].platform` is the full OS string (`Windows 11`, `macOS Sonoma`) and `versions` is an array. `run_settings.cypress_config_file` (and `--ccf`) is only for Cypress 9 and below (pointing at `cypress.json`); the CLI rejects it for Cypress 10+, so pass a non-default config with `--cy="--config-file <path>"`. `smart_ui` sits inside `run_settings` (the `cy.screenshot()` capture flow); the SmartUI SDK flow (`@lambdatest/cypress-driver`, `cy.smartuiSnapshot`) runs separately under `npx smartui exec`. Reporters come from `reporter_config_file` (there is no `--reporter` flag). Common run flags: `--bn`, `-p`, `-s`, `--envs` (Cypress env vars; `--env` selects the LambdaTest environment), `--sys-envs`, `--tun=true --tname`, `--brs platform:browser:version`, `--sync=true --eof=true` (without `--eof` a sync run exits 0 on failures), `--headless`, `--net`, `--geo`, `--tz`, `--reg us|eu|ap`, `--accessibility`, `--vip/--vib/--vibase`, `--cy` (pass-through to `cypress run`; `--spec`, `--browser`, `--parallel`, `-p`, `--headed` are blocked).

## 5. Appium

Hub `https://{user}:{key}@mobile-hub.lambdatest.com/wd/hub` for native apps and for mobile browsers on real devices (mobile-web-automation-on-real-devices). Mobile browsers on emulators/simulators for automation are not shown in the docs; migrate those sessions to real devices or test one session first. WebdriverIO: `hostname: "mobile-hub.lambdatest.com", port: 80, path: "/wd/hub"`.

Upload:
```
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" -F "appFile=@app.apk" -F "name=myapp"
# URL upload: -F "url=https://..." -F "name=..." -F "custom_id=..." -F "storage=url"
```
Response `app_url` like `lt://APP1234...`; pass as `app`. Add `-F custom_id=<stable-name>` to the upload and later runs can refer to the app by that id instead of a changing `lt://` URL (`app` accepts the `lt://` id, the bare custom id `app: "<custom_id>"`, or `app: "filename=<file-name>"`, in `LT:Options` or as `appium:app`; test-setup-and-execution. Espresso/XCUI build bodies and HyperExecute YAML document only `lt://` ids). For CI and HyperExecute: upload once in the CI job before the tests (or in HyperExecute `pre`) with a `custom_id`, so test code never needs the fresh `lt://` id passed between processes; `visibility=team` shares the upload across the organisation. Virtual devices use `/app/upload/virtualDevice`. Apps list: `GET https://manual-api.lambdatest.com/app/data?type=android|ios&level=user`. Devices: `GET https://mobile-api.lambdatest.com/mobile-automation/api/v1/list?region=us`.

Capabilities: samples show them flat, but put TestMu keys inside `LT:Options` with `w3c: true` for new code. The Appium Python client 2+ and the Java client 8+ add an `appium:` prefix to unknown flat keys, and `appium:isRealMobile` / `appium:build` are not read as TestMu options; `LT:Options` avoids that. The docs show three styles: legacy flat caps (samples pinned to Python client 1.x / Java client 7.x), everything inside `lt:options` (Python client 2.2 example), and W3C style for current clients (top-level `platformName`, standard caps through the client's options class or `appium:` prefix, TestMu keys `isRealMobile`, `build`, `w3c`, `video` in `LT:Options`; LambdaTest agent-skills appium-skill uses this). Use the W3C style for Appium Python client 2+/3+ and Java client 8+; keep the existing style for older pinned clients.
Required: `user`/`username`, `accessKey` (or credentials in the hub URL `https://USER:KEY@mobile-hub...`; both work, pick one per repo and read both from env), `isRealMobile` (bool; false = emulator/simulator), `deviceName`, `platformName`, `platformVersion`, `app`. When the source gave no OS version, use a regex over recent majors (Android `1[3-5]`, iOS `1[7-8]`) and flag it; legacy device names (models TestMu no longer lists) become a family regex (`Galaxy S2[2-4].*`) after checking the device list API. `deviceName` and `platformVersion` accept regular expressions on App Automation (`Galaxy.*`, `iPhone 1[45].*`, `Pixel [3-6]$`, comma or `|` for alternatives, `1[35]` for versions; see regular-expression-appium). Public sample apps: `lt://proverbial-android`, `lt://proverbial-ios`.
Debug: `video` (true), `devicelog` (false), `network` (false), `console` (false; web sessions only, not native apps), `visual`.
Config: `build`, `name`, `project`, `appiumVersion` (real devices; Android 1.21.0 to 3.0.2, iOS 15+ 1.22.3 to 3.0.2, default 2.2.1; see supported-appium-versions), `queueTimeout` (600, range 300 to 900), `idleTimeout` (120), `deviceOrientation` (docs show `portrait`/`landscape`; samples use `PORTRAIT`), `newCommandTimeout`, `automationName`, `otherApps` (lt:// array, max 3), `region` (`EU`/`US`/`AP`), `privateCloud`, `w3c`, `autoLaunch`.
Android: `appActivity`, `appPackage`, `playStoreLogin`. iOS: `resignApp` (true), `bundleId`, `autoAcceptAlerts` (true), `autoDismissAlerts`, `noReset`.
Conditions: `language`, `locale`, `disableAnimation`, `timezone`, `geoLocation`, `location`, `enableImageInjection`, `media`, `enableBluetooth`, `autoGrantPermissions`, `proxyUrl`, `tunnel`, `tunnelName`, `dedicatedProxy`, `blockDomains`.

Java:
```java
UiAutomator2Options options = new UiAutomator2Options();
options.setCapability("deviceName", "Galaxy S20"); options.setCapability("platformVersion", "11");
options.setCapability("platformName", "Android"); options.setCapability("isRealMobile", true);
options.setCapability("app", "lt://APP123"); options.setCapability("build", "Build 1"); options.setCapability("name", "Login");
options.setCapability("network", true); options.setCapability("devicelog", true);
AndroidDriver driver = new AndroidDriver(new URL("https://" + user + ":" + key + "@mobile-hub.lambdatest.com/wd/hub"), options);
```

## 6. Other frameworks

- TestMu AI SDKs (config-driven, no capability code): Java TestNG Selenium SDK (`io.github.lambdatest:lambdatest-java-selenium-sdk` in the source pom, `lambdatest-selenium-java-sdk` on the docs page; use the one that resolves) as a `-javaagent` + `lambdatest.yml` + listener `com.lambdatest.selenium.testng.TestNgTestListener` (selenium-java-sdk); Node Playwright `@lambdatest/playwright-node-sdk`, run as `npx playwright-node-sdk playwright test` with `lambdatest.yml` (playwright-sdk). Use them when the source was the BrowserStack SDK or the user wants config-only changes.
- Puppeteer: `puppeteer.connect({ browserWSEndpoint: \`wss://cdp.lambdatest.com/puppeteer?capabilities=${encodeURIComponent(JSON.stringify(capabilities))}\` })`; same `LT:Options` keys as Playwright.
- WebdriverIO: `npm i -D wdio-lambdatest-service` (4.x supports wdio 7 to 9); `user: process.env.LT_USERNAME, key: process.env.LT_ACCESS_KEY, hostname: 'hub.lambdatest.com', port: 80, path: '/wd/hub'` (or `protocol: 'https', port: 443`), `services: [['lambdatest', { tunnel: true, lambdatestOpts: { tunnelName } }]]`; caps carry `LT:Options`. Service options: `setSessionName`, `setSessionStatus`, `sessionNameFormat`, `sessionNameOmitTestTitle`, `sessionNamePrependTopLevelSuiteTitle`, `preferScenarioName`, `ignoreTestCountInName`, `app_upload` + `app`.
- TestCafe: `npm i testcafe-browser-provider-lambdatest`; `testcafe "lambdatest:Chrome@latest:Windows 11" tests/`; env `LT_USERNAME`, `LT_ACCESS_KEY`, `LT_BUILD`, `LT_TEST_NAME`, `LT_RESOLUTION`, `LT_TUNNEL_NAME`, `LT_CAPABILITY_PATH`, `LT_CONSOLE`, `LT_NETWORK`, `LT_VIDEO`, `LT_TIMEZONE`, `LT_W3C`, `LT_SELENIUM_VERSION`, `LT_SCREENSHOT`, `LT_VISUAL`, `LT_LOGFILE`, `LT_VERBOSE`, `LT_PROXY_HOST`/`LT_PROXY_PORT`/`LT_PROXY_USER`/`LT_PROXY_PASS`.
- Nightwatch: `selenium.host: "hub.lambdatest.com"`, `port: 80` (or 443 with https), `username`/`access_key` from env, `desiredCapabilities: { "LT:Options": { build, project, w3c, network, visual, console } }`.
- Robot Framework: `Open Browser ${URL} chrome remote_url=https://%{LT_USERNAME}:%{LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub desired_capabilities=...`; Appium: `Open Application https://%{LT_USERNAME}:%{LT_ACCESS_KEY}@mobile-hub.lambdatest.com/wd/hub platformName=ios deviceName=... app=lt://...`.
- Espresso: upload the app APK and the test APK separately to `POST https://manual-api.lambdatest.com/app/uploadFramework` (multipart `appFile`, `type=espresso-android`, optional `name`); each response's `app_id` is an `lt://APP...` id. Run `POST https://mobile-api.lambdatest.com/framework/v1/espresso/build` (Basic auth, JSON) with `{ "app": "lt://APP...", "testSuite": "lt://APP...", "device": ["Galaxy S21 5G-12", "Pixel 6-12"], "build": "...", "deviceLog": true, "network": false, "video": true, "queueTimeout": 10800, "idleTimeout": 150 }`. Device strings are `"<name>-<version>"`, regex allowed (`"Galaxy.*-1[2-4]"`); add `"isVirtualDevice": true` with versions like `"Pixel 6-12.0"` for emulators. Other build keys: `retries` (max 5), `network.har`, `networkProfile` (needs `network: true`), `geoLocation`, `gpsLocation`, `tunnel`/`tunnelName` (not with `geoLocation`), `disableAnimation`, `clearPackageData`, `singleRunnerInvocation`, `testRemarks`, `region`, `uploadMedia`, `enableBluetooth`, `envVariables` (object, read with `InstrumentationRegistry.getArguments()`; espresso-env-variables-settings), `autoGrantPermissions`, `testTimeout` (default 900), `language` + `locale` (pass both, e.g. `"fr"` + `"CA"`). Test filters (speedup-espresso): `package`, `skipPackage`, `class`, `skipClass` (arrays), `annotation`, `skipAnnotation`, `size` (`small|medium|large`); `class`+`package`, `class`+`skipClass` and `package`+`skipPackage` cannot be combined. `queueTimeout` here is total build time (max 10800). Docs examples write `IdleTimeout` and `deviceLog` for Espresso, `idleTimeout` and `devicelog` for XCUI, while both capability tables write camelCase `idleTimeout`/`deviceLog`; copy the examples' spelling per API. The build POST response shape and a status polling endpoint are not documented: documented per-build GETs are `https://mobile-api.lambdatest.com/mobile-automation/api/v1/framework/builds/<build_id>/report/?encoder=false` (JUnit XML) and `.../framework/builds/<build_id>/logs/instrumentation`. For CI gating prefer running Espresso/XCUI through HyperExecute (`framework.name: android/espresso` or `ios/xcui`, hyperexecute.md §11b), whose CLI exits non-zero on failure. Sample artefacts: `https://prod-mobile-artefacts.lambdatest.com/assets/docs/proverbial_android.apk` and `.../proverbial_android_expressotest.apk`.
- XCUITest: same flow with `type=xcuit-ios` and `POST https://mobile-api.lambdatest.com/framework/v1/xcui/build` (body uses `devicelog` lowercase; `"device": ["iPhone 14-16"]`). Filters: `only-testing` / `skip-testing` (arrays of `Class` or `Class/test`, mutually exclusive, not with `xctestplan`); also `resignApp`, `enableResultBundle`, `language` + `locale`. Both the app and the test runner are uploaded as `.ipa`: build with `xcodebuild build-for-testing`, put `<Name>-Runner.app` in a `Payload/` folder, zip it and rename to `.ipa`; app and runner must share the iOS deployment target (ios-ipa-files-xcui page).

## 7. Tunnel

Binary: `https://downloads.lambdatest.com/tunnel/v3/{linux/amd64/LT | linux/arm64/LT | mac/amd64/LT | mac/arm64/LT | windows/amd64/LT.exe}`.
Start: `LT --user $LT_USERNAME --key $LT_ACCESS_KEY --tunnelName my-tunnel`. Config file `.lt.yaml` (`User`, `Key`, `TunnelName`, `Verbose`). Useful flags: `--allowHosts`, `--bypassHosts`, `--dns`, `--egress-only`, `--ingress-only`, `--infoAPIPort`, `--mode ssh|tcp|ws`, `--proxy-host/--proxy-port/--proxy-user/--proxy-pass`, `--pacfile`, `--shared-tunnel`, `--sshConnType over_22|over_443|over_ws`, `--use-private-ip`, `--logFile`, `--verbose`. Env vars `http_proxy`, `https_proxy`, `no_proxy`.
Node binding: `npm i @lambdatest/node-tunnel`; `new lambdaTunnel().start({ user, key, tunnelName, proxyHost, proxyPort, dir, v, logFile })`, `.stop()`.
Caps: `"tunnel": true, "tunnelName": "my-tunnel"` in LT:Options. HyperExecute YAML: `tunnel: true`, `tunnelOpts`, `tunnelNames`.
The v3 paths above (`/tunnel/v3/<os>/<amd64|arm64|386>/LT`, `LT.exe` on Windows) are raw binaries: `chmod +x` and run. The older `/tunnel/.../64bit/LT_<OS>.zip` URLs are zips. The official GitHub Action (LambdaTest/LambdaTest-tunnel-action) runs the `lambdatest/tunnel` Docker image instead, so it needs Docker on the runner (Linux runners).
Readiness: start with `--infoAPIPort 8000` and wait until `curl -s http://127.0.0.1:8000/api/v1.0/info` answers (status SUCCESS) before starting tests (do not `sleep 10`). Stop with `curl -X DELETE http://127.0.0.1:8000/api/v1.0/stop` or kill the process.
CI example (GitHub Actions, Linux):
```yaml
- name: Start TestMu AI tunnel
  env: { LT_USERNAME: ${{ secrets.LT_USERNAME }}, LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }} }
  run: |
    curl -sSLo LT https://downloads.lambdatest.com/tunnel/v3/linux/amd64/LT && chmod +x LT
    ./LT --user "$LT_USERNAME" --key "$LT_ACCESS_KEY" --tunnelName "gh-${GITHUB_RUN_ID}" --infoAPIPort 8000 > tunnel.log 2>&1 &
    for i in $(seq 1 60); do curl -sf http://127.0.0.1:8000/api/v1.0/info && break; sleep 2; done
```
Set `tunnelName` to the same value in the capabilities. Make the name unique per job: in a matrix use `gh-${GITHUB_RUN_ID}-${GITHUB_JOB}-${{ strategy.job-index }}`, otherwise parallel jobs share one name. On macOS runners download `mac/amd64/LT` or `mac/arm64/LT` (Apple Silicon runners such as `macos-14`); on Windows download `windows/amd64/LT.exe` and run it with PowerShell `Start-Process -NoNewWindow .\LT.exe -ArgumentList ...`, then poll the same info URL with `Invoke-WebRequest`. Enable the tunnel only on sessions that need private hosts; public-site tests run faster without it.

## 8. Test status and lambda hooks

Selenium/Appium (JavascriptExecutor string): `lambda-status=passed|failed|skipped|ignored|unknown|error`, `lambda-name=<name>`, `lambda-build=<build>`, `lambda-action=<reason>` (status reason shown with the result; Java also accepts `executeScript("lambda-action", Map.of("status","failed","reason",msg))`), `lambda-test-tags` (args), `lambda-testCase-start=<name>` / `lambda-testCase-end`, `lambda-screenshot=true`, `lambda-breakpoint=true`, `lambda-exceptions` (args), `lambda-throttle-network` (`Regular 4G`), `lambda-file-exists=`, `lambda-file-stats=`, `lambda-file-content=`, `lambda-file-list=`, `lambda-files-delete=`, `lambda-get-clipboard`, `lambda-set-clipboard=`, `lambda-perform-keyboard-events:`, `lambda:network=full.har`, `lambdatest_executor:{"action":"lambda-heal-start"|"lambda-heal-stop"}`, `smartui.takeScreenshot=<name>`.
Appium real-device sessions: `lambda-status=passed|failed` works; to add a reason use `driver.executeScript('lambda-hook: {"action":"setTestStatus","arguments":{"status":"failed","remark":"why"}}')`. `lambda-action`, `lambda-exceptions` and `customData` are documented for web (Selenium) sessions only.
Playwright/Puppeteer (`page.evaluate`): `lambdatest_action: {"action":"setTestStatus"|"smartui.takeScreenshot"|"getTestDetails"|"lambdaSetBrowserPosition","arguments":{...}}`.

## 9. HyperExecute

Runs the entire suite on cloud VMs instead of hub-and-node; replaces a self-managed runner or a competitor's SDK "run everything in parallel" mode. CLI: `https://downloads.lambdatest.com/hyperexecute/{linux/hyperexecute | darwin/hyperexecute | windows/hyperexecute.exe}`; `./hyperexecute --user $LT_USERNAME --key $LT_ACCESS_KEY --config hyperexecute.yaml` (`--download-artifacts`, `--vars k=v`, `--labels`, `--concurrency`). Quiet mode `CI=true`.

Minimal v0.1:
```yaml
version: 0.1
runson: linux
autosplit: true
concurrency: 2
pre:
  - mvn dependency:resolve
testDiscovery:
  type: raw
  mode: local
  command: grep 'test name' testng.xml | awk '{print$2}' | sed 's/name=//g' | sed 's/>//g'
testRunnerCommand: mvn test -DselectedTests=$test
retryOnFailure: true
maxRetries: 1
jobLabel: [selenium, linux]
```
Other keys: `matrix`, `exclusionMatrix`, `parallelism`, `cacheKey`, `cacheDirectories`, `env`, `runtime[{language,version}]`, `report`, `partialReports`, `mergeArtifacts`, `uploadArtefacts`, `globalTimeout`, `failFast`, `tunnel`, `tunnelOpts`, `project`, `cypress: true` + `cypressOps`, `framework{name,...}` (v0.2 replaces testDiscovery/testRunnerCommand).

## 10. SmartUI and Accessibility

SmartUI (visual regression): CLI `npm i -g @lambdatest/smartui-cli`, `export PROJECT_TOKEN=...`, `npx smartui config:create .smartui.json`, `npx smartui --config .smartui.json exec -- <test command>`. SDKs: Java `io.github.lambdatest:lambdatest-java-sdk` (`SmartUISnapshot.smartuiSnapshot(driver, "name")`), Python `lambdatest-selenium-driver` (`smartui_snapshot(driver, "name")`), Playwright `@lambdatest/playwright-driver`, Cypress `@lambdatest/cypress-driver` (`cy.smartuiSnapshot('name')`). Hooks mode on the grid: Selenium caps `smartUI.project`, `smartUI.build`, `smartUI.baseline`; `driver.executeScript("smartui.takeScreenshot=home")`. Playwright/Puppeteer CDP sessions use flat keys `smartUIProjectName`, `smartUIBuildName`, `smartUIBaseline` inside `LT:Options` and `page.evaluate(_ => {}, 'lambdatest_action: {"action":"smartui.takeScreenshot","arguments":{"screenshotName":"home","fullPage":true}}')`.

Accessibility: LT:Options `accessibility: true`, `accessibility.autoscan: true`, `accessibility.wcagVersion: "wcag21aa"`, `accessibility.bestPractice: false`, `accessibility.needsReview: true`; manual scan `driver.executeScript("lambda-accessibility-scan")`; to pause and resume auto-scanning pass a map: Java `executeScript("lambda-accessibility-scan", Map.of("scan", false))`, Python `execute_script("lambda-accessibility-scan", {"scan": True})`; Cypress `--accessibility`. Open-source checkers that run inside the test (axe-core, `@axe-core/playwright`, pa11y, Lighthouse) are test-framework code, not a competing cloud product: keep them unless the user asks to replace them, and add TestMu AI Accessibility alongside when the source used a vendor accessibility product.

## 10a. Selenium 4 features that need a decision

| Source feature | TestMu AI |
|---|---|
| WebDriver BiDi (`webSocketUrl: true`, BiDi event subscriptions) | supported: set `webSocketUrl: true` top-level (run-tests-with-webdriver-bidi; docs examples are WebdriverIO, other BiDi clients use the same capability) |
| Chrome DevTools Protocol from Selenium (`getDevTools()`, `HasDevTools`, `executeCdpCommand`, `execute_cdp_cmd`) through a remote grid | set `seCdp: true` in `LT:Options`, then `driver = new Augmenter().augment(driver); DevTools dt = ((HasDevTools) driver).getDevTools();` (LambdaTest java-selenium-sample). Not in the capability tables and `executeCdpCommand` is not shown anywhere: prefer BiDi for new code, and test one session before relying on CDP. CDP is documented for Puppeteer/Playwright via `wss://cdp.lambdatest.com/...` (run-tests-with-chrome-devtools-protocol) |
| Selenium managed downloads (`se:downloadsEnabled`, `getDownloadableFiles`, `downloadFile`) | `lambda-file-exists=<name>`, `lambda-file-stats=<name>`, `lambda-file-content=<name>` (base64), `lambda-file-list=`, `lambda-files-delete=` (download-files-using-lambdatest-selenium-grid) |
| Edge IE mode (`InternetExplorerOptions` with `attachToEdgeChrome`) | `InternetExplorerOptions`, `platformName: Windows 11`, `browserVersion: 11.0`; Edge attachment is handled server-side (ie-mode-on-edge) |
| macOS before Big Sur (Sierra, High Sierra, Mojave, Catalina), Windows 7/8/8.1 | check `GET https://api.lambdatest.com/automation/api/v1/platforms`; older OSes may be unavailable, so map to the oldest available version and list it |
| vendor-only setup scripts (Sauce `prerun`, Safari "allow downloads" scripts, BrowserStack `browserstack.uploadMedia` pre-steps) | no equivalent; remove and leave `TODO(testmu-migration)` describing the dialog or state the test must now handle |

## 11. REST API

Basic auth `LT_USERNAME:LT_ACCESS_KEY`. Base `https://api.lambdatest.com/automation/api/v1`: `GET /builds`, `GET|PATCH|DELETE /builds/{id}`, `PUT /build/stop`, `GET /sessions`, `GET|PATCH|DELETE /sessions/{id}`, `PUT /sessions/{id}/stop`, `GET /sessions/{id}/screenshots`, `GET /sessions/{id}/video`, `GET /sessions/{id}/log/{command|selenium|console|network|network.har|full-har}`, `GET /platforms`, `GET /tunnels`, `DELETE /tunnels/{id}`. Swagger: https://swagger-api-support.lambdatest.com/index.html. Set status after the fact: web `PATCH https://api.lambdatest.com/automation/api/v1/sessions/{id}`, app `PATCH https://mobile-api.lambdatest.com/mobile-automation/api/v1/sessions/{id}`, body `{"status_ind": "passed|failed", "name": "..."}` (the calls `wdio-lambdatest-service` makes; not on the docs pages).

## 12. Naming conventions and values

- `platformName` (Selenium) / `platform` (Playwright, Cypress, Puppeteer) is one string: `Windows 11`, `Windows 10`, `Windows 8.1`, `macOS Sequoia`, `macOS Sonoma`, `macOS Ventura`, `macOS Monterey`, `macOS Big Sur`. `MacOS Tahoe` appears in samples but not on the capabilities page; Linux is only mentioned in a note. The capabilities page intro says values are case and space insensitive while the table marks `platformName`/`browserName` case-sensitive, so copy the documented spelling.
- `browserName`: `Chrome`, `MicrosoftEdge`, `Firefox`, `Safari`, `Internet Explorer`; Playwright adds `pw-chromium`, `pw-firefox`, `pw-webkit`.
- `browserVersion`: `latest`, `latest-1`, `latest-2`, or `120`, `120.0`.
- Mobile: `platformName` `Android`/`iOS`, `deviceName` like `Galaxy S23`, `Pixel 8`, `iPhone 15`, `platformVersion` `14`, `17`. Device names drop the `Samsung`/`Google` prefix that BrowserStack uses; check the device list API when in doubt.
- Timezone is a UTC offset string (`UTC+05:30`), not a city name.
- Status values are lowercase `passed` / `failed`.

## 13. Unverified at research time

Answered from docs, source and samples on 27 Oct 2026: `MacOS Tahoe` (capital M, as in every sample); Linux is a web platform (Chrome samples; HyperExecute FAQ adds Firefox, Edge); `console` is true/false for Selenium (log levels exist only for KaneAI); Playwright `idleTimeout` default 300, max 1800 (clamped), `lambdaMaskCommands` values `sendType`, `sendFill`, `sendPress`, `setHTTPCredentials`, `setStorageState`, `setGeolocation`, `useSpecificBundleVersion: true` pins the server Playwright version to the requested browserVersion; there is no regional web hub (only `hub`, `mobile-hub`, `beta-hub` `.lambdatest.com`; Appium `region` EU/US/AP); custom ids work as `app`; Espresso filters, env vars and locale keys exist; `ltOptions` YAML overrides are Selenium only.
Still open: official C#, Ruby, PHP, Go LT:Options snippets (pattern-based above); `queueTimeout` for web sessions;  the Espresso/XCUI build POST response and polling; which Java SDK artifactId is published; Cypress component testing (no support in the CLI source). A live-account probe script (`testmu_verify.py`, shipped separately from the skills) answers most of these. Confirm against https://www.testmuai.com/support/docs/llms.txt during a real migration.
