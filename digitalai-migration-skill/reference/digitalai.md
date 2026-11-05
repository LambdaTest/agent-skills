# Digital.ai Continuous Testing (Experitest / SeeTest) to TestMu AI

Read this when the source is Digital.ai Continuous Testing, formerly Experitest / SeeTest: `cloud.seetest.io`, `<company>.experitest.com`, `digitalai:options`, `deviceQuery`, `cloud:` app references, `seetest:client.*` commands.

Contents
1. Fingerprints
2. Credentials and endpoints
3. Capabilities
4. deviceQuery translation
5. App upload and `cloud:` references
6. SeeTest extension commands to lambda hooks
7. Frameworks (Java, C#, Python, WebdriverIO)
8. Worked example (C# NUnit Appium)
9. Gotchas and unverified

## 1. Fingerprints

Grep for: `cloud.seetest.io`, `experitest.com`, `seetest`, `SEETEST_IO_ACCESS_KEY`, `digitalai:options`, `digital.ai:options`, `otherApps`, `commandScreenshot`, `selfHealing`, `appiumPlugins`, `accessKey` cap without a username, `deviceQuery`, `testName` cap, `reportDisable`, `releaseDevice`, `reservationDuration`, `devicePool`, `cloud:com.` app values, `seetest:client.`, `client:client.`, `reportUrl`, `/api/v1/applications/new`, `Cloud Agent`, `uniqueName`.

## 2. Credentials and endpoints

| Digital.ai | TestMu AI |
|---|---|
| `accessKey` capability (project access key, env `SEETEST_IO_ACCESS_KEY`) | `LT:Options.username` + `accessKey` |
| `http://:<accessKey>@<host>:<port>/wd/hub/` (empty user) | `https://<LT_USERNAME>:<LT_ACCESS_KEY>@mobile-hub.lambdatest.com/wd/hub` |
| `https://cloud.seetest.io/wd/hub/`, `https://<company>.experitest.com/wd/hub/`, on-prem `https://<host>/wd/hub` | `https://mobile-hub.lambdatest.com/wd/hub` (mobile), `https://hub.lambdatest.com/wd/hub` (web) |
| `Authorization: Bearer <accessKey>` on REST | Basic auth |
| `POST https://cloud.seetest.io/api/v1/applications/new` | `POST https://manual-api.lambdatest.com/app/upload/realDevice` |
| `reportUrl` capability read after session | `GET https://api.lambdatest.com/automation/api/v1/sessions/{id}` |

## 3. Capabilities

Appium 2 form puts Digital.ai keys in `digitalai:options` and standard keys under `appium:`; older code uses flat keys. Both map the same way.

| Digital.ai | TestMu | Notes |
|---|---|---|
| `accessKey` | `username` + `accessKey` | |
| `testName` | `name` | |
| `deviceQuery` | `platformName` + `deviceName` + `platformVersion` | see §4 |
| `deviceManufacturer`, `deviceModel`, `deviceCategory` (`PHONE`/`TABLET`) | fold into `deviceName` | |
| `platformVersion` | `platformVersion` | |
| `udid` | drop | |
| `app` (`cloud:com.example/.MainActivity`, `cloud:com.example`) | `app` (`lt://...`) | re-upload |
| `appPackage`, `appActivity`, `bundleId` | same | keep; TestMu uses them for launch |
| `releaseVersion`, `buildVersion`, `appVersion`, `uniqueName`, `installOnlyForUpdate` | drop | upload the exact build you want |
| `instrumentApp` | drop | |
| `appiumVersion` | `appiumVersion` (TestMu supports it on real devices: Android 1.21.0 to 3.0.2, iOS 15+ 1.22.3 to 3.0.2, default 2.2.1; check the version is in that list) | |
| `reportDisable` / `report.disable` | drop | |
| `releaseDevice` (default true) | drop | TestMu releases on `quit()` |
| `reservationDuration` | drop | |
| `devicePool` (`shared`/`dedicated`/`any`) | `dedicated` -> `privateCloud: true` | |
| `deviceCleanup`, `onlyAvailable` | drop | |
| `deviceWithAudio` | drop | |
| `orientation` | `deviceOrientation` | |
| `configurationProfile`, `setPasscode`, `dontGoHomeOnQuit` | drop | |
| `noReset`, `fullReset`, `newCommandTimeout` | same | |
| `otherApps` | `otherApps` (lt:// ids, max 3) | re-upload |
| `commandScreenshot`, `AudioReport`, `selfHealing`, `appiumPlugins`, `removeConfigurationProfile` | drop (`visual: true` covers screenshots) | |
| `acceptInsecureCerts` | `acceptInsecureCerts` | |
| (none) | `isRealMobile: true` | |
| (none) | `devicelog: true`, `network: true`, `video: true`, `build` | Digital.ai reports captured these by default |

## 4. deviceQuery translation

`deviceQuery` is an XPath over device attributes. Translate each predicate:

| Predicate | TestMu |
|---|---|
| `@os='android'` | `platformName: "Android"` |
| `@os='ios'` | `platformName: "iOS"` |
| `@category='PHONE'` / `'TABLET'` | choose a phone/tablet `deviceName` |
| `@manufacture='samsung'` | `deviceName` starting with `Galaxy` |
| `contains(@model, 'iphone')` | `deviceName: "iPhone 15"` (pick one) |
| `@version='13'` / `starts-with(@version,'13')` | `platformVersion: "13"` |
| `@dedicated='true'` | `privateCloud: true` |
| `@uniqueName='...'` | drop |

Example: `"@os='android' and @category='PHONE' and @manufacture='samsung'"` -> `{"platformName": "Android", "deviceName": "Galaxy S23", "platformVersion": "13", "isRealMobile": true}`. Confirm the device exists via `GET https://mobile-api.lambdatest.com/mobile-automation/api/v1/list`. A query that matched many devices was a matrix; offer the user a matrix (HyperExecute `matrix` or a parametrised runner).

## 5. App upload and `cloud:` references

```
# Digital.ai
curl -X POST "https://cloud.seetest.io/api/v1/applications/new" -H "Authorization: Bearer $SEETEST_IO_ACCESS_KEY" -F "file=@app.apk"
# TestMu
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" -F "appFile=@app.apk" -F "name=app"
```
`cloud:com.example/.MainActivity` -> `app: "lt://APP..."` plus `appPackage: "com.example"`, `appActivity: ".MainActivity"`. iOS `cloud:com.example` -> `app: "lt://APP..."` plus `bundleId: "com.example"`. `camera`/`touchId` upload flags -> TestMu `enableImageInjection` cap (camera) and flag biometrics.

## 6. SeeTest extension commands to lambda hooks

| Digital.ai (`driver.executeScript(...)`) | TestMu |
|---|---|
| `seetest:client.report("step", "true")` | `lambda-testCase-start=step` then `lambda-testCase-end` |
| `seetest:client.report("step", "false")` | web: `lambda-exceptions` with the message; real-device app sessions: `lambda-hook: {"action":"setTestStatus","arguments":{"status":"failed","remark":"step"}}` |
| `seetest:client.startStepsGroup("g")` / `stopStepsGroup()` | `lambda-testCase-start=g` / `lambda-testCase-end` |
| `seetest:client.setGroupStatus("g", "true")` | drop |
| `client:client.setTestStatus(true, "msg")` (forum-documented form) | `lambda-status=passed|failed`; with a message on app sessions use `lambda-hook: {"action":"setTestStatus","arguments":{"status":"passed","remark":"msg"}}` (`lambda-action` is documented for Selenium only) |
| `seetest:client.addTestProperty("k", "v")` | web sessions: `customData` cap; app sessions: no equivalent yet (docs: coming soon), drop and list |
| SeeTestClient Java `seetest.setReportStatus(status, message, stacktrace)` | app sessions: `lambda-hook` setTestStatus with the message as `remark` (no stacktrace field) |
| `driver.getCapabilities().getCapability("reportUrl")` | REST session lookup |
| `driver.installApp("cloud:...")`, `seetest:client.launch`, `seetest:client.applicationClearData` | standard Appium `installApp` (lt:// or path), `activateApp`, `terminateApp`/`removeApp` |
| `seetest:client.setLocationPlaybackFile`, `seetest:client.clearLocation`, `stopLocationPlayback` | `location` cap / Appium `setLocation` (single point; playback files have no equivalent) |
| `seetest:client.setNetworkConditions(...)` | `lambda-throttle-network` hook |

## 7. Frameworks

- Java (TestNG/JUnit): `DesiredCapabilities dc; dc.setCapability("accessKey", ...); dc.setCapability("deviceQuery", ...); dc.setCapability("digitalai:options", options); new AndroidDriver(new URL(server + "/wd/hub/"), dc)` -> `UiAutomator2Options` + `LT:Options` + `mobile-hub.lambdatest.com`. Hook in `@AfterMethod`/`TestWatcher`.
- C# (NUnit/MSTest): `AppiumOptions options; options.AddAdditionalAppiumOption("accessKey", ...)` -> `options.AddAdditionalAppiumOption("LT:Options", dict)`. Hook in `[TearDown]`.
- Python: `desired_caps['accessKey']` -> `UiAutomator2Options().load_capabilities({... "LT:Options": {...}})`. Hook in pytest fixture teardown.
- WebdriverIO: `hostname: '<cloud>', protocol: 'https', port: 443, path: '/wd/hub'`, caps `'digitalai:options': { testName, accessKey, appiumVersion }`, `'appium:options': { udid, app }` -> `user`/`key`, `hostname: 'mobile-hub.lambdatest.com'`, `port: 80`, `'LT:Options': {...}`, `wdio-lambdatest-service`.
- Cloud Agent / on-prem device hosting has no equivalent; private devices on TestMu are `privateCloud: true` through TestMu's own private cloud.

## 8. Worked example (C# NUnit Appium)

Before:
```csharp
var options = new AppiumOptions();
options.AddAdditionalAppiumOption("accessKey", Environment.GetEnvironmentVariable("SEETEST_IO_ACCESS_KEY"));
options.AddAdditionalAppiumOption("testName", "Login");
options.AddAdditionalAppiumOption("deviceQuery", "@os='android' and @category='PHONE'");
options.AddAdditionalAppiumOption("app", "cloud:com.acme/.MainActivity");
options.AddAdditionalAppiumOption("appPackage", "com.acme");
options.AddAdditionalAppiumOption("appActivity", ".MainActivity");
driver = new AndroidDriver(new Uri("https://acme.experitest.com/wd/hub/"), options);
// ...
driver.ExecuteScript("seetest:client.report", "Login passed", "true");
```
After:
```csharp
var options = new AppiumOptions { PlatformName = "Android" };
options.AddAdditionalAppiumOption("LT:Options", new Dictionary<string, object> {
  {"username", Environment.GetEnvironmentVariable("LT_USERNAME")},
  {"accessKey", Environment.GetEnvironmentVariable("LT_ACCESS_KEY")},
  {"name", "Login"}, {"build", Environment.GetEnvironmentVariable("BUILD") ?? "local"},
  {"deviceName", "Galaxy S23"}, {"platformVersion", "13"}, {"isRealMobile", true},
  {"app", "lt://APP1016018741698142800"}, {"devicelog", true}, {"network", true}, {"w3c", true}
});
options.AddAdditionalAppiumOption("appium:appPackage", "com.acme");
options.AddAdditionalAppiumOption("appium:appActivity", ".MainActivity");
driver = new AndroidDriver(new Uri("https://mobile-hub.lambdatest.com/wd/hub"), options);
// ...
((IJavaScriptExecutor)driver).ExecuteScript("lambda-status=passed");
```

## 9. Gotchas and unverified

- The access key alone authenticated on Digital.ai; TestMu needs both username and key. Add `LT_USERNAME` to CI secrets.
- `releaseDevice: false` patterns (keeping a device reserved across tests) have no equivalent; each TestMu session is one device reservation.
- Unverified at research time (27 Oct 2026): `reportStatus` capability (not in current docs; the `dw:options` key also does not exist, `digitalai:options` is documented); `deviceQuery` attributes `@dedicated` and `@uniqueName`; `customData` on TestMu Appium sessions; a Sauce-Connect-style developer tunnel for Digital.ai (none found; LT Tunnel is needed for localhost apps on TestMu).
- Sources: docs.digital.ai continuous-testing appium code examples (java, c#, python), appium-server-supported-capabilities, additional-appium-capabilities-using-digitalaioptions-appium-2, webdriverio-integration-appium, uploading-applications-to-your-project, Appium OSS supported commands.
