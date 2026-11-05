# HeadSpin to TestMu AI

Read this when the source is HeadSpin: per-device Appium/Selenium endpoints with the API token in the URL, `headspin:` capabilities, User Flows, `hs connect browser` for Playwright/Puppeteer.

Contents
1. Fingerprints
2. Credentials and endpoints
3. Capabilities (Appium)
4. Capabilities (Selenium desktop)
5. Status and session metadata
6. App upload
7. Playwright and Puppeteer
8. Worked example (Node WebdriverIO Appium)
9. Gotchas and unverified

## 1. Fingerprints

Grep for: `headspin.io`, `/v0/` followed by a token and `/wd/hub`, `api-dev.headspin.io`, `appium-dev.headspin.io`, `headspin:options` (bundles every HeadSpin cap unprefixed), `automation-config`, `driver_url`, `headspin:capture`, `headspin:controlLock`, `headspin:testName`, `headspin:session.name`, `headspin:sessionTags`, `headspin:selector`, `headspin:quitSession`, `headspin:appId`, `HEADSPIN_API_TOKEN`, `HS_API_TOKEN`, `hs connect browser`, `localhost:9222`, `/json/version`, `/devtools/browser/`, `/v1/app/upload`.

## 2. Credentials and endpoints

| HeadSpin | TestMu AI |
|---|---|
| API token in URL: `https://{host}:{port}/v0/{api_token}/wd/hub` | `https://{LT_USERNAME}:{LT_ACCESS_KEY}@mobile-hub.lambdatest.com/wd/hub` (Appium) or `hub.lambdatest.com` (desktop) |
| Per-device `driver_url` from `GET https://<token>@api-dev.headspin.io/v0/devices/automation-config` | one hub; device chosen by `deviceName` + `platformVersion` |
| Load-balanced driver URL (AppiumLB) `https://appium-dev.headspin.io/v0/{token}/wd/hub` | same single hub |
| `Authorization: Bearer <token>` on v1 REST; token in the URL userinfo on v0 REST | Basic auth `LT_USERNAME:LT_ACCESS_KEY` |
| `https://api-dev.headspin.io/v1/app/upload` | `https://manual-api.lambdatest.com/app/upload/realDevice` |
| `https://{host}:{port}/v0/{token}/wd/hub/versions` (browser versions) | `GET https://api.lambdatest.com/automation/api/v1/platforms` |

Delete any code that calls the automation-config API to discover a device host; it has no equivalent and is the biggest structural change.

## 3. Capabilities (Appium)

| HeadSpin | TestMu | Notes |
|---|---|---|
| `udid` (device id) | `deviceName` + `platformVersion` | look up the model behind the udid in HeadSpin UI |
| blank `deviceName` + `udid` | `deviceName` (exact or regex) | |
| `headspin:selector` (`'os_version:>9 city:"Mountain View, US" device_skus:...'`; keys os_version, city, sku, device_skus, carrier, udid, device_id, model) | `deviceName`/`platformVersion` | a selector is a matrix; ask which devices matter |
| `headspin:capture` (video + network + function call) | `video: true`, `network: true` | function-call capture has no equivalent |
| `headspin:capture.video` | `video` | |
| `headspin:capture.network` | `network` | |
| `headspin:capture.functionCall` | drop | |
| `headspin:capture.ignoreHosts` | drop (filter HAR after download) | |
| `headspin:capture.networkConfig.shaping` (numeric `{down, up, rtt, loss}`) | `lambda-throttle-network` hook (named presets like `Regular 4G`) | approximate; preset nearest to the numbers |
| `headspin:capture.networkConfig.redirectRules/spoofRules/headerRules` | no TestMu AI equivalent: list as a gap with `TODO(testmu-migration)` | |
| `headspin:controlLock` | drop | |
| `headspin:testName` (User Flow) | `name` | |
| `headspin:session.name` / `headspin:session.description` | `name`; description has no app-session equivalent (`customData` is Web Automation only) | |
| `headspin:sessionTags` (`[{"k": "v"}]`) | `tags` (flat strings `k:v`) | |
| `headspin:autoLabel` | drop | |
| `headspin:appiumVersion` | `appiumVersion` (TestMu supports it on real devices: Android 1.21.0 to 3.0.2, iOS 15+ 1.22.3 to 3.0.2, default 2.2.1; check the version is in that list) | |
| `headspin:newCommandTimeout` | `newCommandTimeout` | |
| `headspin:requestTimeout`, `headspin:waitForAvailableTimeout` (and the older `waitForDeviceOnlineTimeout`, `ignoreFailedDevice`) | `queueTimeout` (300 to 900 s) | |
| `headspin:app.resign` / `headspin:appId.resignIpa` | `resignApp` | |
| `headspin:appId` / `headspin:app.id` | `app` (`lt://...`) | |
| `headspin:otherApps.ids` | `otherApps` (lt:// ids, max 3) | re-upload |
| `headspin:network.regionalRouting` | drop | |
| `headspin:testData` | no app-session equivalent (`customData` is Web Automation only); drop and list | |
| `headspin:quitOnDisconnect`, `restartDeviceOnSessionStart`, `useAppiumUnlock`, `removeAppPackages`, `resetUiAutomator2`, `useMjpegScreenshotUrl`, `logPath`, `initialScreenSize`, `driverLogLevel`, `enableJSConsoleLog` | drop | `console: true` covers JS console for mobile web |
| standard `appium:*` (`app`, `appPackage`, `appActivity`, `bundleId`, `noReset`, `automationName`) | same names | |
| (none) | `isRealMobile: true` | |

## 4. Capabilities (Selenium desktop)

HeadSpin desktop browsers (`chrome`, `MicrosoftEdge`/`msedge`, `chromium`, `brave`, `firefox`, `safari`) via the same token URL -> `https://hub.lambdatest.com/wd/hub` with `LT:Options { platformName, build, name, video, network, console }`. `brave` and `chromium` have no TestMu equivalent; use `Chrome`. `headspin:capture*` -> `video`/`network`; `headspin:testName` -> `name`.

## 5. Status and session metadata

| HeadSpin | TestMu |
|---|---|
| `driver.execute_script("headspin:quitSession", {"status": "passed"})` (needs `headspin:testName`) | `driver.execute_script("lambda-status=passed")` then `driver.quit()` |
| `status: "failed"` / `"excluded"` / `"not_set"` | `lambda-status=failed` / `skipped` / omit |
| Performance Monitoring API `PATCH /v0/userflows/{user_flow_id}/sessions/{session_id}` `{"status": "Passed|Failed|Excluded"}` | `PATCH https://mobile-api.lambdatest.com/mobile-automation/api/v1/sessions/{id}` with `{"name": "...", "status_ind": "passed|failed"}` for app sessions (web sessions: `PATCH https://api.lambdatest.com/automation/api/v1/sessions/{id}`); this is what `wdio-lambdatest-service` calls |
| Session Annotation API (labels, time ranges) | `lambda-testCase-start=` / `lambda-testCase-end` markers during the run |

## 6. App upload

```
# HeadSpin
curl -X POST -H "Authorization: Bearer $HS_API_TOKEN" https://api-dev.headspin.io/v1/app/upload -F app="@app.ipa"
# -> {"app_id": "..."}; install with /v1/app/{app_id}/install/{device_id}
# TestMu
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" -F "appFile=@app.ipa" -F "name=app"
# -> {"app_url": "lt://APP..."}; pass as the app capability, no separate install step
```
Legacy `/v0/apps/apk/upload` and `/v0/apps/ipa/upload` (`apk_id`/`ipa_id`) map the same way.

## 7. Playwright and Puppeteer

HeadSpin exposes a local CDP endpoint through `hs connect browser --api-token <token> <browser-device-id@host>` (default `localhost:9222`). HeadSpin's own Playwright sample reads `webSocketDebuggerUrl` from `http://localhost:9222/json/version` and calls `chromium.connect({ wsEndpoint: 'ws://localhost:9222/devtools/browser/<id>' })`; some teams use `connectOverCDP('http://localhost:9222')`. Puppeteer uses `puppeteer.connect({ browserURL: 'http://localhost:9222' })`.

On TestMu: remove the `hs connect` step from CI; replace with
```js
const capabilities = { browserName: 'Chrome', browserVersion: 'latest',
  'LT:Options': { platform: 'Windows 11', build: process.env.BUILD, name: 'checkout', user: process.env.LT_USERNAME, accessKey: process.env.LT_ACCESS_KEY, network: true, video: true } };
const browser = await chromium.connect({ wsEndpoint: `wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(JSON.stringify(capabilities))}` });
```
(Puppeteer: `puppeteer.connect({ browserWSEndpoint: \`wss://cdp.lambdatest.com/puppeteer?capabilities=...\` })`). The call stays `chromium.connect`; what changes is the endpoint (no `/json/version` lookup, capabilities in the query string) and, for code that used `connectOverCDP`, a switch to `connect`. Mobile browsers via Playwright on TestMu: `LT:Options.platform: 'android'`, `deviceName`, `platformVersion`.

## 8. Worked example (Node WebdriverIO Appium)

Before (`wdio.conf.js`):
```js
exports.config = {
  protocol: 'https', hostname: 'proxy-us-nyc-4.headspin.io', port: 7001,
  path: `/v0/${process.env.HS_API_TOKEN}/wd/hub`,
  capabilities: [{
    platformName: 'Android', 'appium:udid': 'ce0917194392a140017e', 'appium:automationName': 'UiAutomator2',
    'appium:app': 'https://.../app.apk', 'headspin:capture': true, 'headspin:testName': 'Login', 'headspin:controlLock': true,
  }],
};
```
After:
```js
exports.config = {
  user: process.env.LT_USERNAME, key: process.env.LT_ACCESS_KEY,
  hostname: 'mobile-hub.lambdatest.com', port: 80, path: '/wd/hub',
  services: [['lambdatest', {}]],
  capabilities: [{
    platformName: 'Android',
    'LT:Options': { deviceName: 'Galaxy S23', platformVersion: '13', isRealMobile: true, app: 'lt://APP1016018741698142800',
      build: process.env.BUILD || 'local', name: 'Login', video: true, network: true, devicelog: true, w3c: true },
    'appium:automationName': 'UiAutomator2',
  }],
};
```
`npm i -D wdio-lambdatest-service`; the service can set session name and pass/fail (check its `setSessionName`/`setSessionStatus` options are on); otherwise add `lambda-status=` in an `afterTest` hook.

## 9. Gotchas and unverified

- HeadSpin device hosts are geographic (`proxy-us-nyc-4`); teams sometimes rely on that for geo-specific testing. TestMu equivalent is `geoLocation: "US"` (web) or the `region` cap plus real-device `geoLocation`.
- `headspin:capture.functionCall` and the performance (Waterfall/Session Analysis) UI have no equivalent; say so in the plan.
- Unverified at research time (26 Oct 2026): `headspin:waitForDeviceOnlineTimeout`, `headspin:ignoreFailedDevice`, `headspin:initialScreenSize`, `headspin:driverLogLevel` (absent from current docs); `headspin:sessionName` camelCase does not exist (docs use `headspin:session.name`).
- Sources: headspin.io/docs appium-capabilities, selenium-capabilities, automation-configuration-api, appiumlb, annotating-your-session, app-management, app-api, chrome-devtools; info.headspin.io Appium Capabilities PDF.
