# Kobiton to TestMu AI

Read this when the source is Kobiton: real-device Appium cloud, Kobiton App Repository (`kobiton-store:`), NOVA Scriptless exports.

Contents
1. Fingerprints
2. Credentials and endpoints
3. Capabilities
4. App upload
5. Scriptless (NOVA) test cases
6. Frameworks
7. Worked example (Python Appium)
8. Gotchas and unverified

## 1. Fingerprints

Grep for: `api.kobiton.com/wd/hub`, `api.kobiton.com`, `:3000/wd/hub` (on-prem), `appium:username` with `appium:accessKey`, `kobiton:`, `kobiton-store:`, `deviceGroup`, `sessionName`, `sessionDescription`, `captureScreenshots`, `useConfiguration`, `groupId`, `KOBITON_USERNAME`, `KOBITON_API_KEY`, `/v2/apps/upload-url`, `/v1/apps/uploadUrl`, `kobiton:runtime`, `kobiton:sessionTags`, `app-install`, `KOBITON_ACCESS_KEY`, `kobitonSessionId`, `kobiton:tcm`, `externalCaseId`, `scriptlessEnable`, `allowMobileShell`.

## 2. Credentials and endpoints

| Kobiton | TestMu AI |
|---|---|
| `https://<username>:<apikey>@api.kobiton.com/wd/hub` (or `appium:username` + `appium:accessKey` caps; on-prem `https://<host>:3000/wd/hub`) | `https://<LT_USERNAME>:<LT_ACCESS_KEY>@mobile-hub.lambdatest.com/wd/hub` |
| WebdriverIO `protocol: 'https', hostname: 'api.kobiton.com', port: 443, path: '/wd/hub', user, key` | `hostname: 'mobile-hub.lambdatest.com', port: 80, path: '/wd/hub', user: process.env.LT_USERNAME, key: process.env.LT_ACCESS_KEY` with `wdio-lambdatest-service` |
| `KOBITON_USERNAME` / `KOBITON_API_KEY` | `LT_USERNAME` / `LT_ACCESS_KEY` |
| App upload `POST https://api.kobiton.com/v2/apps/upload-url` + S3 PUT + `POST /v2/apps` | `POST https://manual-api.lambdatest.com/app/upload/realDevice` |
| Session REST `https://api.kobiton.com/v1/sessions/{id}` | `https://api.lambdatest.com/automation/api/v1/sessions/{id}` |

## 3. Capabilities

Kobiton with Appium 2 prefixes its keys `kobiton:`; older samples are unprefixed. Both forms map the same way.

| Kobiton | TestMu | Notes |
|---|---|---|
| `kobiton:sessionName` / `sessionName` | `name` | |
| `kobiton:sessionDescription` | no equivalent for app sessions (`customData` is Web Automation only); put it in `name` or `build`, or drop | |
| `kobiton:deviceGroup` `KOBITON` | default public cloud | |
| `kobiton:deviceGroup` `ORGANIZATION` (private devices) | `privateCloud: true` | |
| `deviceName` with wildcards (`iPhone 11*`, `*Pro`) | `deviceName` regex (`iPhone 11.*`, `.*Pro$`) or an exact name | TestMu App Automation supports regex |
| `platformName` (`Android`/`iOS`) | same | |
| `platformVersion` (wildcard `14.*`) | `platformVersion` major (`14`) | |
| `app` / `kobiton:app` (`kobiton-store:12345`, `kobiton-store:v657531`, or URL) | `app` (`lt://APP...`) | re-upload; URL form works on TestMu via `-F url=` upload |
| `browserName` (`safari`, `chrome`) for mobile web | `browserName` | mobile web on TestMu uses the same hub with `browserName` and no `app` |
| `kobiton:captureScreenshots` (web sessions only on Kobiton) | `visual: true` | |
| `appium:deviceOrientation` (`portrait`/`landscape`) | `deviceOrientation` | |
| `kobiton:groupId` | drop | |
| `kobiton:useConfiguration` (network payload capture) | `network: true` | |
| `kobiton:sessionTags` / `kobiton:tags` | `tags` | |
| `kobiton:runtime` (`xium`/`appium`) | drop | TestMu is standard Appium |
| `kobiton:app-install` (`always`/`never`) | `noReset` / `fullReset` semantics | |
| `kobiton:waitForIdle`, `kobiton:includeSystemWindows`, `kobiton:xpath2` | drop | |
| `appium:noReset`, `appium:fullReset` | `noReset`, `fullReset` | |
| `appium:waitForIdleTimeout` | pass through unchanged as an `appium:` driver cap | not an LT:Options key |
| `appium:udid` (pinning one physical device) | no documented udid capability: use the exact `deviceName` + `platformVersion`, and `privateCloud: true` for dedicated devices on a private cloud plan | |
| `kobiton:tcmServerUrl`, `kobiton:tcmUsername`, `kobiton:tcmApiKey`, `kobiton:tcm*`, `externalCaseId` (TestRail reporting) | no session capability: import the TestRail cases into TestMu AI Test Manager with the one-click TestRail importer, and leave `TODO(testmu-migration)` where results were pushed to TestRail | |
| `scriptlessEnable` (record for scriptless/NOVA) | drop; recorded flows are re-created in KaneAI (§5) | |
| `allowMobileShell` | drop; Appium `mobile: shell` is not documented on the Real Device Cloud, so flag any `mobile: shell` calls | |
| `appium:enforceAppInstall` | drop | |
| `appium:newCommandTimeout` | `newCommandTimeout` | |
| (none) | `isRealMobile: true` | Kobiton is real devices |
| (none) | `devicelog: true`, `video: true` | Kobiton recorded these by default |

Status: Kobiton marks sessions from the Appium session end (a REST state update exists in third-party API specs but is not on docs.kobiton.com). On TestMu send `lambda-status=passed|failed` through `execute_script` before `quit()`.

## 4. App upload

```
# Kobiton v2 (three steps)
curl -X POST https://api.kobiton.com/v2/apps/upload-url -H "Authorization: Basic <b64 user:apikey>" -H "Content-Type: application/json" -d '{"file_name":"app.apk"}'
curl -X PUT "<url from step 1>" -H "Content-Type: application/octet-stream" -H "x-amz-tagging: unsaved=true" -T app.apk
curl -X POST https://api.kobiton.com/v2/apps -H "Authorization: Basic ..." -d '{"file_name":"app.apk","app_path":"<app_path>"}'
# if app_id is N/A: poll GET https://api.kobiton.com/v2/apps/parsing-status?appVersionId=<version_id>
# TestMu (one step)
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" -F "appFile=@app.apk" -F "name=app"
```
`kobiton-store:<app_id>` / `kobiton-store:v<version_id>` -> `lt://APP...` from the response. Kobiton `app_id` vs `version_id` distinction: TestMu `app` always points at one uploaded build; use `custom_id` on URL uploads if the team wants a stable alias.

## 5. Scriptless (NOVA) test cases

Scriptless test cases (Kobiton's generate-an-Appium-script flow) are recorded sessions, not code. Export from Kobiton first (Appium script export: Java TestNG/JUnit, Node Mocha, C# NUnit, Python pytest), then migrate the exported code with §3. If the team wants to stay script-free, KaneAI (natural-language web and mobile tests) and Kane CLI `kane-cli generate` are the TestMu offers; the recorded steps translate to plain-English `*_test.md` steps.

## 6. Frameworks

Kobiton samples cover Java (TestNG/JUnit), Node (Mocha + webdriverio/wd), C# (NUnit), Python (pytest). The host framework does not change; only the hub URL, caps and status hook. Hook placement per framework: see languages.md §3.

## 7. Worked example (Python Appium)

Before:
```python
caps = {
    "platformName": "Android",
    "kobiton:sessionName": "Login smoke",
    "kobiton:deviceGroup": "ORGANIZATION",
    "deviceName": "Galaxy S2*",
    "platformVersion": "13*",
    "kobiton:app": "kobiton-store:98765",
    "appium:appPackage": "com.acme",
    "appium:appActivity": ".MainActivity",
    "kobiton:captureScreenshots": True,
}
driver = webdriver.Remote(f"https://{os.getenv('KOBITON_USERNAME')}:{os.getenv('KOBITON_API_KEY')}@api.kobiton.com/wd/hub", options=UiAutomator2Options().load_capabilities(caps))
```
After:
```python
caps = {
    "platformName": "Android",
    "LT:Options": {
        "username": os.getenv("LT_USERNAME"),
        "accessKey": os.getenv("LT_ACCESS_KEY"),
        "name": "Login smoke",
        "build": os.getenv("CI_BUILD", "local"),
        "deviceName": "Galaxy S23",
        "platformVersion": "13",
        "isRealMobile": True,
        "privateCloud": True,
        "app": "lt://APP1016018741698142800",
        "visual": True,
        "devicelog": True,
        "network": True,
        "w3c": True,
    },
    "appium:appPackage": "com.acme",
    "appium:appActivity": ".MainActivity",
}
driver = webdriver.Remote("https://mobile-hub.lambdatest.com/wd/hub", options=UiAutomator2Options().load_capabilities(caps))
# teardown:
driver.execute_script("lambda-status=passed")
driver.quit()
```

## 8. Gotchas and unverified

- Wildcard device names hide a matrix; resolve with the user.
- `deviceGroup`: current docs show `ORGANIZATION`; `KOBITON` appears in Kobiton's official sample packages; `CLOUD` was not found anywhere.
- Kobiton network payload capture (`useConfiguration`) produced HAR-like data; TestMu `network: true` gives HAR via `lambda:network=full.har` and the session log API.
- Unverified at research time (26 Oct 2026): a REST call to set session pass/fail; `retainDurationInSeconds`, `flowDriver` (not in current docs). `kobiton-store:v<id>` is in official docs.
- Sources: docs.kobiton.com automation-testing/capabilities/available-capabilities, apps/upload-an-app/using-the-kobiton-api, automation-testing/basic-appium-server/launch-a-basic-appium-2-session, test-management/generate-appium.
