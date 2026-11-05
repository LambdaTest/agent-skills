# AWS Device Farm to TestMu AI

Read this when the source is AWS Device Farm: desktop browser testing via `create_test_grid_url`, or mobile testing via uploaded test packages with a test spec YAML and `DEVICEFARM_*` env vars.

Contents
1. Fingerprints
2. Desktop browser testing (Selenium grid URL)
3. Mobile: server-side Appium runs to client-side cloud runs
4. Test spec YAML to CI / HyperExecute
5. Built-in and framework uploads (Espresso, XCUITest, Appium packages)
6. Device pools to a device matrix
7. Worked example (Python Appium)
8. Gotchas and unverified

## 1. Fingerprints

Grep for: `create_test_grid_url`, `CreateTestGridUrl`, `aws:maxDurationSecs`, `aws:idleTimeoutSecs`, `DEVICEFARM_TEST_PACKAGE_PATH`, `DEVICEFARM_DEVICE_UDID_FOR_APPIUM`, `DEVICEFARM_XCUITESTRUN_FILE`, `DEVICEFARM_TOTAL_JOBS`, `DEVICEFARM_JOB_NUMBER`, `boto3.client('devicefarm')`, `devicefarm`, `projectArn`, `expiresInSeconds`, `aws devicefarm`, `DEVICEFARM_DEVICE_NAME`, `DEVICEFARM_DEVICE_UDID`, `DEVICEFARM_DEVICE_PLATFORM_NAME`, `DEVICEFARM_DEVICE_OS_VERSION`, `DEVICEFARM_APP_PATH`, `DEVICEFARM_LOG_DIR`, `DEVICEFARM_SCREENSHOT_PATH`, `DEVICEFARM_CHROMEDRIVER_EXECUTABLE_DIR`, `DEVICEFARM_APPIUM_WDA_DERIVED_DATA_PATH`, `APPIUM_BASE_PATH`, test spec YAML with `phases:` `install:` `pre_test:` `test:` `post_test:`, `appium --base-path`, `127.0.0.1:4723`, `devicefarm-cli`, `aws devicefarm create-upload`, `schedule-run`.

## 2. Desktop browser testing

Device Farm hands out a signed WebDriver URL:
```python
client = boto3.client('devicefarm', region_name='us-west-2')
url = client.create_test_grid_url(projectArn=ARN, expiresInSeconds=300)['url']
driver = webdriver.Remote(url, options=options)
```
TestMu replacement:
```python
options = webdriver.ChromeOptions()
options.browser_version = "latest"
options.platform_name = "Windows 11"
options.set_capability("LT:Options", {"username": os.getenv("LT_USERNAME"), "accessKey": os.getenv("LT_ACCESS_KEY"),
    "build": os.getenv("BUILD", "local"), "name": "checkout", "video": True, "network": True, "w3c": True})
driver = webdriver.Remote("https://hub.lambdatest.com/wd/hub", options=options)
```

| Device Farm desktop | TestMu |
|---|---|
| `browserName` `chrome`, `firefox`, `MicrosoftEdge` on Windows only | `Chrome`, `Firefox`, `MicrosoftEdge`, `Safari` on Windows and macOS; widen the matrix if useful |
| `browserVersion` `latest`, `latest-1`, `latest-2` | same |
| `aws:idleTimeoutSecs` / `aws:maxDurationSecs` caps | `idleTimeout` in `LT:Options`; drop maxDuration |
| rejected caps: `--headless`, `--user-data-dir`, `--no-sandbox`, `binary`, `w3c: false` | `goog:chromeOptions.args` are accepted on TestMu; keep real flags, drop sandbox flags |
| signed URL expiry / IAM role | static credentials in `LT_USERNAME`/`LT_ACCESS_KEY` CI secrets |
| session artifacts via `list_test_grid_session_artifacts` (video, logs) | `GET https://api.lambdatest.com/automation/api/v1/sessions/{id}/video` and `/log/{selenium|console|network}` |
| `boto3` / AWS SDK dependency for the grid URL | remove |

Status: Device Farm desktop sessions had no pass/fail; send `lambda-status=passed|failed` from the test outcome in teardown (languages.md §3; never a hard-coded `passed`).

## 3. Mobile: server-side runs to client-side cloud runs

Device Farm mobile runs upload your zipped test package and run it on an AWS host next to the device, against a local Appium (`http://127.0.0.1:4723`) with `DEVICEFARM_*` env vars describing the device. TestMu runs the test process from your CI (or HyperExecute) against `mobile-hub.lambdatest.com`.

| Device Farm | TestMu |
|---|---|
| `http://127.0.0.1:4723` (+ `$APPIUM_BASE_PATH`) | `https://{LT_USERNAME}:{LT_ACCESS_KEY}@mobile-hub.lambdatest.com/wd/hub` |
| `$DEVICEFARM_DEVICE_NAME` | `deviceName` (explicit, e.g. `Galaxy S23`) |
| `$DEVICEFARM_DEVICE_UDID` | drop |
| `$DEVICEFARM_DEVICE_PLATFORM_NAME` | `platformName` |
| `$DEVICEFARM_DEVICE_OS_VERSION` | `platformVersion` (major) |
| `$DEVICEFARM_APP_PATH` | `app: "lt://APP..."` after upload |
| `$DEVICEFARM_LOG_DIR`, `$DEVICEFARM_SCREENSHOT_PATH` | TestMu session logs, `visual: true`, `devicelog: true` |
| `$DEVICEFARM_CHROMEDRIVER_EXECUTABLE_DIR` | drop (TestMu manages chromedriver for mobile web) |
| `$DEVICEFARM_APPIUM_WDA_DERIVED_DATA_PATH_V*` | drop |
| `appium --default-capabilities '{...udid...}'` | caps in code |
| `devicefarm-cli use appium 3` | `appiumVersion` (TestMu supports it on real devices: Android 1.21.0 to 3.0.2, iOS 15+ 1.22.3 to 3.0.2, default 2.2.1; check the version is in that list), e.g. `3.0.2` |
| (none) | `isRealMobile: true`, `build`, `name`, `network: true`, `video: true` |

Upload: `aws devicefarm create-upload --type ANDROID_APP` + `curl -T app.apk <presigned url>` -> `curl -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST https://manual-api.lambdatest.com/app/upload/realDevice -F "appFile=@app.apk" -F "name=app"`.

## 4. Test spec YAML to CI / HyperExecute

```yaml
# Device Farm test spec (custom environment)
version: 0.1
phases:
  install:
    commands:
      - devicefarm-cli use appium 2
      - cd $DEVICEFARM_TEST_PACKAGE_PATH && pip install -r requirements.txt
  pre_test:
    commands:
      - appium --base-path=$APPIUM_BASE_PATH --log-timestamp --default-capabilities "{\"deviceName\": \"$DEVICEFARM_DEVICE_NAME\", \"udid\": \"$DEVICEFARM_DEVICE_UDID\", \"app\": \"$DEVICEFARM_APP_PATH\"}" >> $DEVICEFARM_LOG_DIR/appium.log 2>&1 &
      - while ! curl -s http://0.0.0.0:4723${APPIUM_BASE_PATH}/status; do sleep 1; done
  test:
    commands:
      - pytest tests/
  post_test:
    commands: []
artifacts:
  - $DEVICEFARM_LOG_DIR
```
becomes either a plain CI job (`pip install -r requirements.txt && pytest tests/` with `LT_*` secrets; no Appium server, no readiness loop) or `hyperexecute.yaml`:
```yaml
version: 0.1
runson: linux
autosplit: true
concurrency: 3
runtime:
  - language: python
    version: "3.11"
env:
  LT_USERNAME: ${{ .secrets.LT_USERNAME }}       # tests open Real Device Cloud sessions (model A)
  LT_ACCESS_KEY: ${{ .secrets.LT_ACCESS_KEY }}
pre:
  - pip3 install --cache-dir .pip -r requirements.txt
cacheKey: '{{ checksum "requirements.txt" }}'
cacheDirectories:
  - .pip
testDiscovery:
  type: raw
  mode: local
  command: grep -rl "def test_" tests
testRunnerCommand: pytest $test
retryOnFailure: true
maxRetries: 1
```
`artifacts:` -> HyperExecute `uploadArtefacts` / `report`, or TestMu session artifacts.

## 5. Built-in and framework uploads

| Device Farm test type | TestMu |
|---|---|
| `INSTRUMENTATION` (Espresso) with `--test` APK | `POST https://manual-api.lambdatest.com/app/uploadFramework` (`appFile`, `type=espresso-android`) for app and test APK (each response's `app_id` is `lt://APP...`), then `POST https://mobile-api.lambdatest.com/framework/v1/espresso/build` with `{"app","testSuite","device":["Galaxy S23-13"],"build","deviceLog":true,"network":true}`; emulators: `"isVirtualDevice": true` and `"Pixel 6-12.0"` |
| `XCTEST_UI` | `type=xcuit-ios` and `POST https://mobile-api.lambdatest.com/framework/v1/xcui/build` |
| `APPIUM_PYTHON`, `APPIUM_JAVA_TESTNG`, `APPIUM_JAVA_JUNIT`, `APPIUM_NODE`, `APPIUM_RUBY` packages | run from CI/HyperExecute against the mobile hub (§3) |
| `BUILTIN_FUZZ` | no equivalent; KaneAI exploratory is the nearest |
| `APPIUM_WEB_*` | mobile web on TestMu: `browserName` + device caps, no `app` |
| `XCTEST` (non-UI XCTest) | no equivalent beyond XCUITest; list as a gap |

## 6. Device pools to a device matrix

A Device Farm device pool (rules on `PLATFORM`, `OS_VERSION`, `MANUFACTURER`, `FORM_FACTOR`, `MODEL`, `FLEET_TYPE`, `AVAILABILITY` with operators such as `EQUALS`, `IN`, `GREATER_THAN`, `CONTAINS`; or top devices) is a matrix. On TestMu: list devices via `GET https://mobile-api.lambdatest.com/mobile-automation/api/v1/list?region=us`, choose N, and either parametrise the runner (pytest params, TestNG parameters) or use HyperExecute `matrix: { device: ["Galaxy S23-13", "Pixel 8-14"] }` with `testRunnerCommand` reading `${matrix.device}`. TestMu `deviceName` also accepts regular expressions (`Galaxy.*`, `Pixel [6-8]$`) when any matching device is fine. Private device fleets (`FLEET_TYPE PRIVATE`) -> `privateCloud: true`.

## 7. Worked example (Python Appium)

Before (ran inside Device Farm):
```python
caps = {"platformName": os.environ["DEVICEFARM_DEVICE_PLATFORM_NAME"], "appium:deviceName": os.environ["DEVICEFARM_DEVICE_NAME"],
        "appium:udid": os.environ["DEVICEFARM_DEVICE_UDID"], "appium:app": os.environ["DEVICEFARM_APP_PATH"], "appium:automationName": "UiAutomator2"}
driver = webdriver.Remote("http://127.0.0.1:4723" + os.environ.get("APPIUM_BASE_PATH", ""), options=UiAutomator2Options().load_capabilities(caps))
```
After (runs from CI):
```python
caps = {"platformName": "Android", "appium:automationName": "UiAutomator2",
        "LT:Options": {"username": os.getenv("LT_USERNAME"), "accessKey": os.getenv("LT_ACCESS_KEY"),
                       "deviceName": os.getenv("DEVICE_NAME", "Galaxy S23"), "platformVersion": os.getenv("DEVICE_OS", "13"),
                       "isRealMobile": True, "app": "lt://APP1016018741698142800", "build": os.getenv("BUILD", "local"),
                       "name": "Login", "devicelog": True, "network": True, "video": True, "w3c": True}}
driver = webdriver.Remote("https://mobile-hub.lambdatest.com/wd/hub", options=UiAutomator2Options().load_capabilities(caps))
# teardown: status from the real outcome (pytest: conftest hookwrapper, languages.md §3)
driver.execute_script("lambda-status=" + ("failed" if request.node.rep_call.failed else "passed"))
driver.quit()
```

## 8. Gotchas and unverified

- The biggest change is topology: tests leave AWS and run from your CI. Network access to internal backends that was implicit on the AWS host now needs the LT Tunnel (`tunnel: true`, `tunnelName`).
- Device Farm `remote access` sessions (manual) -> TestMu Real Device manual testing in the dashboard.
- TestMu Espresso/XCUITest upload and build endpoints are confirmed in the TestMu getting-started pages; the build response shape and polling are not documented, so CI runs use HyperExecute (`hyperexecute.md` §11b) for a reliable exit code.
- Sources: docs.aws.amazon.com/devicefarm testgrid getting-started-local, API_CreateTestGridUrl, techref-support, custom-test-environment-test-spec, custom-test-environment-variables, test-types-appium; TestMu espresso-supported-capabilities, app-testing-apis.
