# Perfecto (Perforce) to TestMu AI

Read this when the source is Perfecto: Perfecto Mobile/Web cloud, Reportium reporting SDK, Quantum framework, Perfecto Connect tunnel.

Contents
1. Fingerprints
2. Credentials and endpoints
3. Capabilities (mobile)
4. Capabilities (desktop web)
5. App repository and upload
6. Reportium lifecycle to lambda hooks
7. Quantum framework
8. Perfecto Connect to LT Tunnel
9. Worked example (Java Appium)
10. Gotchas and unverified

## 1. Fingerprints

Grep for: `perfectomobile.com`, `nexperience/perfectomobile/wd/hub`, `/wd/hub/fast`, `perfectoDriver`, `perfectoRemoteDriver`, `securityToken`, `perfecto:options`, `perfecto:`, `Perfecto-Authorization`, `PerfectoExecutionContext`, `ReportiumClient`, `ReportiumClientFactory`, `TestResultFactory`, `reportium`, `com.perfecto.reporting-sdk`, `perfectoconnect`, `tunnelId`, `PRIVATE:`, `GROUP:`, `PUBLIC:` app locators, `report.projectName`, `report.jobName`, `driver.capabilities.model`, `remote.server` (Quantum), `waitForAvailableLicense`, `enableAppiumBehavior`.

## 2. Credentials and endpoints

| Perfecto | TestMu AI |
|---|---|
| `securityToken` capability (or `perfecto:options.securityToken`); REST header `Perfecto-Authorization: <token>` | `LT_USERNAME` + `LT_ACCESS_KEY` as `LT:Options.username` / `accessKey`, or embedded in the hub URL; REST Basic auth |
| `https://<cloud>.perfectomobile.com/nexperience/perfectomobile/wd/hub` (mobile and web) | `https://mobile-hub.lambdatest.com/wd/hub` (Appium) and `https://hub.lambdatest.com/wd/hub` (desktop web) |
| `https://<cloud>.app.perfectomobile.com/repository/api/v1/artifacts` | `https://manual-api.lambdatest.com/app/upload/realDevice` |
| Reportium report URL from `reportiumClient.getReportUrl()` | session URL from `GET https://api.lambdatest.com/automation/api/v1/sessions/{id}` or the dashboard |

Perfecto's region-aware host `<cloud>.hub.perfectomobile.com` is the same thing. Quantum course material uses the `/nexperience/perfectomobile/wd/hub/fast` suffix; treat it as the same hub.

## 3. Capabilities (mobile)

With Appium 2 Perfecto wants its keys inside `perfecto:options` (or `perfecto:` prefixed) and standard keys under `appium:`. TestMu wants its keys inside `LT:Options` (or flat with `w3c: false`).

| Perfecto | TestMu | Notes |
|---|---|---|
| `securityToken` | `username` + `accessKey` | |
| `deviceName` (Perfecto device id) | `deviceName` (model name, e.g. `Galaxy S23`) | pick from `GET https://mobile-api.lambdatest.com/mobile-automation/api/v1/list` |
| `model` (regex `iPhone.*`, `Galaxy S23`) | `deviceName` (regex allowed on TestMu App Automation, e.g. `iPhone.*`) | |
| `manufacturer` | fold into `deviceName` | |
| `platformName`, `platformVersion` | same | TestMu wants major version (`13`, `17`) |
| `location`, `network`, `description`, `deviceType`, `audioPlayback`, `automationInfrastructure`, `deviceLanguage` | drop | pick the device explicitly; `language`/`locale` caps exist on TestMu |
| `openDeviceTimeout` (min, max 9) | `queueTimeout` (sec, 300 to 900) | |
| `app` (`PRIVATE:MyApp.apk`, `GROUP:x.apk`) | `app` (`lt://APP...`) | re-upload |
| `bundleId`, `appPackage`, `appActivity`, `fullReset`, `noReset`, `autoLaunch`, `automationName` | same names | `automationName: PerfectoMobile` -> `UiAutomator2`/`XCUITest` |
| `autoInstrument`, `sensorInstrument`, `enableAppiumBehavior`, `useAppiumForWeb` | drop | TestMu runs standard Appium; `resignApp` (iOS, default true) covers resigning |
| `appiumVersion` | `appiumVersion` (TestMu supports it on real devices: Android 1.21.0 to 3.0.2, iOS 15+ 1.22.3 to 3.0.2, default 2.2.1; check the version is in that list) | |
| `perfecto:espressoServerApp` | drop | |
| `waitForAvailableLicense` | drop | |
| `scriptName` | drop | |
| `takesScreenshot`, `screenshotOnError`, `screenshotFormat` | `visual: true` | |
| `report.projectName` / `report.projectVersion` | `project` | |
| `report.jobName` / `report.jobNumber` / `report.jobBranch` | `build` (join as `jobName-jobNumber-branch` or use CI vars) | |
| `report.tags` | `tags` or `buildTags` | |
| `report.customFields` | `customData` | |
| `tunnelId` | `tunnel: true`, `tunnelName` | |
| (none) | add `isRealMobile: true` | Perfecto is all real devices |
| (none) | `devicelog: true`, `network: true`, `video: true` | Perfecto captured these by default in the report |

## 4. Capabilities (desktop web)

| Perfecto | TestMu |
|---|---|
| `platformName: Windows` + `platformVersion: 11` | `platformName: "Windows 11"` (one string) |
| `platformName: Mac` + `platformVersion: 14` | `platformName: "macOS Sonoma"` (codename) |
| `browserName`, `browserVersion` | same (`latest` works on both) |
| `resolution` (default 1024x768) | `resolution` (default 1024x768) |
| `location` | drop |
| `addHostsRecord` | LT tunnel `--dns` / flag |
| `ie-mode` | TestMu IE mode on Edge caps; flag |
| `installCertificates`, `uploadFileFromRepo` | `lambda:userFiles` for files; certificates: `acceptInsecureCerts` |
| `takesScreenshot`, `screenshotOnError` | `visual` |
| `securityToken` | `username`/`accessKey` |
| hub `https://<cloud>.perfectomobile.com/nexperience/perfectomobile/wd/hub` | `https://hub.lambdatest.com/wd/hub` |

## 5. App repository and upload

```
# Perfecto
curl --location 'https://<cloud>.app.perfectomobile.com/repository/api/v1/artifacts' \
  --header 'Perfecto-Authorization: <token>' \
  --form 'inputStream=@"/path/app.apk"' \
  --form 'requestPart="{\"artifactLocator\":\"PRIVATE:app.apk\",\"artifactType\":\"ANDROID\",\"override\":true}"'
# TestMu
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@/path/app.apk" -F "name=app"
```
The `artifactLocator` string in the `app` cap becomes the `lt://` id from the TestMu response. `artifactType IOS`/`ANDROID` is inferred by TestMu from the file. Perfecto media/image artifacts (`IMAGE`, `AUDIO`) map to TestMu `media` uploads for image injection; flag.

## 5a. Perfecto `mobile:*` commands

Perfecto extensions run as `driver.executeScript("mobile:<area>:<action>", params)`. Plain Appium `mobile:` commands (`mobile: activateApp`, `mobile: shell`) are a different family; leave those as they are.

| Perfecto | TestMu AI |
|---|---|
| `mobile:application:open` / `close` / `install` / `uninstall` / `clean` | Appium `driver.activateApp(id)` / `terminateApp(id)` / `installApp(path)` / `removeApp(id)`; clean -> `noReset: false` / `fullReset` caps or reinstall |
| `mobile:handset:ready`, `mobile:device:open`/`close` | drop (devices are allocated per session) |
| `mobile:device:info`, `mobile:handset:info` | `driver.getCapabilities()` / session details API |
| `mobile:screen:image`, `mobile:screenshot` | `getScreenshotAs` or `lambda-screenshot=true` |
| `mobile:checkpoint:text`, `mobile:text:find`, `mobile:text:select`, `mobile:checkpoint:image`, `mobile:image:find`, `mobile:image:select` (visual OCR/image analysis) | no equivalent: replace with element locators where possible, SmartUI hooks for visual checks, otherwise `TODO(testmu-migration)` |
| `mobile:browser:open` / `clean` / `goto` | `driver.get(url)`; clean -> new session |
| `mobile:location:set` / `reset` | `geoLocation` / `gpsLocation` capability, or Appium `setLocation` |
| `mobile:network:settings`, `mobile:vnetwork:start`/`stop` | `networkProfile` capability or `lambda-throttle-network` hook |
| `mobile:presskey`, `mobile:button-text:click`, `mobile:touch:tap`, `mobile:touch:swipe` | Appium `pressKey`, W3C actions / `mobile: clickGesture`, `mobile: swipeGesture` (UiAutomator2) or XCUITest `mobile: tap`/`swipe` |
| `mobile:keyboard:display` | `driver.hideKeyboard()` |
| `mobile:audio:*`, `mobile:sensorInstrument:*`, `mobile:image.injection:*` | image injection via `enableImageInjection` + `lambda-image-injection`; others: gap |

Add `"mobile:` (with the colon right after `mobile`) to the leftover grep.

## 5b. Mobile web on real devices

Perfecto mobile browser sessions (`browserName: "mobileOS"`/`Chrome`/`Safari` with `deviceName`/`model`) -> `https://mobile-hub.lambdatest.com/wd/hub` with `browserName` (`Chrome` on Android, `Safari` on iOS), `platformName`, `deviceName`, `platformVersion` and `isRealMobile: true` in `LT:Options` (mobile-web-automation-on-real-devices). Desktop browsers stay on `hub.lambdatest.com`.

## 6. Reportium lifecycle to lambda hooks

| Reportium (Java) | TestMu |
|---|---|
| `new PerfectoExecutionContext.PerfectoExecutionContextBuilder().withProject(new Project("name","1.0")).withJob(new Job("job", 45).withBranch("b")).withContextTags("Regression").withWebDriver(driver).build()` | caps: `project`, `build`, `tags`, `buildTags` |
| `reportiumClient.testStart("myTest", new TestContext("Sanity"))` | `executeScript("lambda-name=myTest")` and `executeScript("lambda-test-tags", "Sanity")` (or `name`/`tags` caps per test) |
| `reportiumClient.stepStart("Login")` / `stepEnd()` | `executeScript("lambda-testCase-start=Login")` / `executeScript("lambda-testCase-end")` |
| `reportiumClient.reportiumAssert("msg", bool)` | it is a soft assertion (records a failed step, the test continues): keep that behaviour with the framework's soft assert (TestNG `SoftAssert` + `assertAll()` in teardown, AssertJ `SoftAssertions`), and send `lambda-hook` setTestStatus with the message on failure; do not turn it into a hard assert |
| `reportiumClient.testStop(TestResultFactory.createSuccess())` | `executeScript("lambda-status=passed")` |
| `reportiumClient.testStop(TestResultFactory.createFailure(msg, throwable, reason))` | `executeScript("lambda-status=failed")`, `executeScript("lambda-action=" + msg)`, `executeScript("lambda-exceptions", msg)` |
| `reportiumClient.getReportUrl()` | `((RemoteWebDriver) driver).getSessionId()` then dashboard/REST |

Remove `com.perfecto.reporting-sdk:reportium-java` from `pom.xml`. The same classes exist for C# (NuGet `Perfecto-Reporting`), Python (`perfecto-py3`) and JavaScript (`perfecto-reporting`); the hook strings are identical across languages.

## 7. Quantum framework

Quantum (QAF + Cucumber + TestNG) reads `resources/application.properties` (`remote.server`, `perfecto.capabilities.securityToken`, `driver.name=perfectoDriver|perfectoRemoteDriver`) and TestNG XML `<parameter>` entries (`driver.capabilities.*`):
- `remote.server=https://<cloud>.perfectomobile.com/nexperience/perfectomobile/wd/hub` -> `https://mobile-hub.lambdatest.com/wd/hub` (or web hub).
- `perfecto.capabilities.securityToken=...` -> put `username:accessKey` in the URL: `remote.server=https://${LT_USERNAME}:${LT_ACCESS_KEY}@mobile-hub.lambdatest.com/wd/hub`.
- `driver.capabilities.model=iPhone.*` -> `driver.capabilities.deviceName=iPhone 15`; add `driver.capabilities.isRealMobile=true`, `driver.capabilities.platformVersion=17`.
- `driver.capabilities.app=PRIVATE:app.ipa` -> `driver.capabilities.app=lt://APP...`.
- QAF property syntax has no nested object, so use flat caps with `driver.capabilities.w3c=false`, `driver.capabilities.build=...`, `driver.capabilities.name=...`.
- Quantum's built-in Reportium listener: replace with a QAF listener that runs the status hook in `onTestSuccess`/`onTestFailure`.

## 8. Perfecto Connect to LT Tunnel

`./perfectoconnect start -c <cloud>.perfectomobile.com -s <token>` (returns a Tunnel ID used in `tunnelId` cap) -> `./LT --user $LT_USERNAME --key $LT_ACCESS_KEY --tunnelName perfecto-migrated` and caps `tunnel: true`, `tunnelName: "perfecto-migrated"`. `perfectoconnect stop` -> kill the LT process (or `curl -X DELETE http://127.0.0.1:8000/api/v1.0/stop` with `--infoAPIPort 8000`).

## 9. Worked example (Java Appium)

Before:
```java
DesiredCapabilities caps = new DesiredCapabilities();
Map<String, Object> perfectoOptions = new HashMap<>();
perfectoOptions.put("securityToken", System.getenv("PERFECTO_TOKEN"));
perfectoOptions.put("model", "Galaxy S2.*");
perfectoOptions.put("report.projectName", "Banking");
perfectoOptions.put("report.jobName", "nightly");
caps.setCapability("perfecto:options", perfectoOptions);
caps.setCapability("platformName", "Android");
caps.setCapability("appium:app", "PRIVATE:bank.apk");
caps.setCapability("appium:appPackage", "com.bank");
caps.setCapability("appium:appActivity", ".MainActivity");
driver = new AndroidDriver(new URL("https://acme.perfectomobile.com/nexperience/perfectomobile/wd/hub"), caps);
ReportiumClient reportiumClient = new ReportiumClientFactory().createPerfectoReportiumClient(
    new PerfectoExecutionContext.PerfectoExecutionContextBuilder().withProject(new Project("Banking", "1.0")).withWebDriver(driver).build());
reportiumClient.testStart("Login", new TestContext("Sanity"));
// ... steps ...
reportiumClient.testStop(TestResultFactory.createSuccess());
```
After:
```java
UiAutomator2Options options = new UiAutomator2Options();
Map<String, Object> lt = new HashMap<>();
lt.put("username", System.getenv("LT_USERNAME"));
lt.put("accessKey", System.getenv("LT_ACCESS_KEY"));
lt.put("deviceName", "Galaxy S23");
lt.put("platformVersion", "13");
lt.put("isRealMobile", true);
lt.put("project", "Banking");
lt.put("build", "nightly");
lt.put("name", "Login");
lt.put("tags", new String[] {"Sanity"});
lt.put("devicelog", true);
lt.put("network", true);
lt.put("w3c", true);
options.setCapability("LT:Options", lt);
options.setPlatformName("Android");
options.setApp("lt://APP1016018741698142800");
options.setAppPackage("com.bank");
options.setAppActivity(".MainActivity");
driver = new AndroidDriver(new URL("https://mobile-hub.lambdatest.com/wd/hub"), options);
// ... steps ...
((JavascriptExecutor) driver).executeScript("lambda-status=passed");
```

## 9a. Dependencies to remove

Maven/Gradle: `com.perfectomobile:pm-webdriver`, `com.perfectomobile:http-client`, `com.perfecto.reporting-sdk:reportium-java`, `reportium-testng`, `reportium-junit`, `com.perfecto:quantum-*`, and the Perfecto Maven repository (`repository.perfectomobile.com`). These often brought `commons-lang3`, `commons-io`, `gson` and Selenium/Appium in transitively; add back any the tests import, at the versions the old dependency tree used. If the build cannot run, take the versions from the old lockfile/pom of the removed artifact and list them as unverified.

A single session shared by several TestNG methods (driver created in `@BeforeClass`): record each method's result in `@AfterMethod`, and send one `lambda-status` in `@AfterClass` (`failed` if any method failed) before `quit()`; use `lambda-testCase-start`/`lambda-testCase-end` around each method so the dashboard still shows them separately.

## 10. Gotchas and unverified

- Perfecto's report is the only place pass/fail lived; after removing Reportium, every test must call `lambda-status=` or the dashboard shows "Completed".
- `model` regexes usually hide a device matrix; ask which devices matter rather than picking the first match.
- Perfecto desktop web and mobile share one hub; on TestMu they are two hubs, so a shared driver factory needs a branch.
- Unverified at research time (26 Oct 2026): `driver.capabilities.app` as a Quantum parameter name; whether TestMu accepts `tags` as an array in Appium caps (documented for Selenium); the LT tunnel info API stop call.
- Sources: help.perfecto.io define_capabilities, supported_appium_capabilities, upload_item_to_repository, java reporting (test-analysis/java), work_with_perfecto_connect, quantum_framework_introduction; github.com/Project-Quantum/Quantum-Starter-Kit.
