# Firebase Test Lab to TestMu AI

Read this when the source is Firebase Test Lab (`gcloud firebase test android|ios run`), including Fastlane, Bitrise, Codemagic and GitHub Actions steps that wrap it. Test Lab is deprecated and shuts down on 30 September 2027, so this migration also has a deadline. The TestMu AI target is the Real Device Cloud (real and virtual devices) through its Espresso and XCUITest framework APIs, or HyperExecute for Espresso/XCUI suites run as jobs.

Contents
1. Fingerprints
2. What transfers and what does not
3. Instrumentation (Espresso) to TestMu AI Espresso
4. XCTest (XCUITest) to TestMu AI XCUITest
5. Device strings, API levels and emulators
6. Robo and Game Loop
7. CI wrappers
8. Worked example (GitHub Actions)
9. Gotchas and unverified

## 1. Fingerprints

Grep for: `gcloud firebase test android run`, `gcloud firebase test ios run`, `gcloud beta firebase test`, `--type instrumentation`, `--type robo`, `--type game-loop`, `--type xctest`, `--device model=`, `--device-ids`, `--os-version-ids`, `--results-bucket`, `--results-dir`, `--test-targets`, `--num-flaky-test-attempts`, `--num-uniform-shards`, `--environment-variables`, `--directories-to-pull`, Fastlane actions `firebase_test_lab_ios_xctest` and `run_tests_firebase_testlab`, Bitrise step "Virtual Device Testing for Android/iOS", Codemagic workflows with a `firebase_credentials` group calling gcloud, `google-github-actions/auth` next to `gcloud firebase test`, `GOOGLE_APPLICATION_CREDENTIALS`.

## 2. What transfers and what does not

| Test Lab | TestMu AI |
|---|---|
| Instrumentation (Espresso / AndroidJUnitRunner) on physical devices | Espresso build on real devices |
| Instrumentation on virtual devices (`MediumPhone.arm`, older `Pixel2.arm`) | Espresso build with `"isVirtualDevice": true` and an emulator string such as `"Pixel 6-12.0"` |
| XCTest (XCUITest) | XCUITest build (real devices; `isVirtualDevice` for simulators) |
| Robo crawl (Android and iOS) | no equivalent; KaneAI app tests are the nearest TestMu AI product (§6) |
| Game Loop | no equivalent |
| Results in a Cloud Storage bucket (`--results-bucket`), Firebase console | TestMu AI dashboard, build and session APIs |
| Service account auth | `LT_USERNAME` / `LT_ACCESS_KEY` Basic auth |
| `--num-flaky-test-attempts` (max 10) | `retries` (max 5) |
| `--timeout` (default 15m) | `testTimeout` (default 900 s) per test; `queueTimeout` is total build time (max 10800 s) |
| `--test-targets "class com.acme.LoginTest"` / `package` / `annotation` / `size` | build body `class`, `package` (arrays), `annotation`, `size`, plus `skipClass`/`skipPackage`/`skipAnnotation`; XCUI `only-testing`/`skip-testing` (speedup-espresso, speedup-xcui) |
| `--environment-variables k=v` | `envVariables` in the build body (`{"STAGE":"stg1"}`, read via `InstrumentationRegistry.getArguments()`; espresso-env-variables-settings) |
| `--directories-to-pull` | no equivalent; device logs and video come from the build artifacts |
| `--network-profile` | `networkProfile` (needs `"network": true`; TestMu profile names differ, e.g. `2g-gprs-good`) |
| `--locales`, `--orientations` (deprecated legacy flags) | `language` + `locale` in the build body (pass both); `deviceOrientation` |
| `--num-uniform-shards` (beta) | several builds, or more devices in `device[]` |

## 3. Instrumentation (Espresso) to TestMu AI Espresso

Test Lab:
```
gcloud firebase test android run --type instrumentation \
  --app app-debug.apk --test app-debug-androidTest.apk \
  --device model=oriole,version=33 --timeout 15m --num-flaky-test-attempts 1
```
TestMu AI (official flow: getting-started-with-espresso-testing):
```
# 1. upload the app APK and the test APK (same endpoint, separate calls); each response has "app_id": "lt://APP..."
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST "https://manual-api.lambdatest.com/app/uploadFramework" -F "appFile=@app-debug.apk" -F "type=espresso-android"
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST "https://manual-api.lambdatest.com/app/uploadFramework" -F "appFile=@app-debug-androidTest.apk" -F "type=espresso-android"
# 2. start the build
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST "https://mobile-api.lambdatest.com/framework/v1/espresso/build" -H "Content-Type: application/json" \
  -d '{"app":"lt://APP_ID","testSuite":"lt://TEST_ID","device":["Pixel 6-13"],"build":"nightly","deviceLog":true,"network":false,"video":true,"queueTimeout":10800,"idleTimeout":150,"retries":1}'
# 3. results: the response/polling shape is not documented; fetch the JUnit report when done
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" "https://mobile-api.lambdatest.com/mobile-automation/api/v1/framework/builds/<build_id>/report/?encoder=false"
# for CI gating use HyperExecute (hyperexecute.md §11b): its CLI exit code reflects the result
```
Other build keys: `isVirtualDevice`, `network.har`, `networkProfile`, `geoLocation`, `gpsLocation`, `tunnel`/`tunnelName` (not with `geoLocation`), `disableAnimation`, `clearPackageData`, `singleRunnerInvocation`, `testRemarks`, `region` (`us`/`eu`/`ap`), `uploadMedia`, `autoGrantPermissions`, `testTimeout`. Use `idleTimeout` (one docs example writes `IdleTimeout`). Set `disableAnimation: true` and `clearPackageData: true` to match Test Lab's clean-device behaviour.

## 4. XCTest to TestMu AI XCUITest

Test Lab: `gcloud firebase test ios run --type xctest --test MyTests.zip --device model=iphone13pro,version=16.6` (the zip holds `Debug-iphoneos` and the `.xctestrun`).
TestMu AI wants the app and the UI test runner as two separate `.ipa` uploads:
1. `xcodebuild build-for-testing` for a device destination.
2. App: put `<App>.app` in a `Payload/` folder, zip it, rename to `.ipa`. Runner: same for `<App>UITests-Runner.app`. App and runner must share the iOS deployment target (ios-ipa-files-xcui).
3. Upload both with `type=xcuit-ios` to `uploadFramework`; each response gives `app_id`.
4. `POST https://mobile-api.lambdatest.com/framework/v1/xcui/build` with `{"app","testSuite","device":["iPhone 13 Pro-16"],"video":true,"devicelog":true,"network":false,"build":"nightly","queueTimeout":10800}` (XCUI uses lowercase `devicelog`).

## 5. Device strings, API levels and emulators

TestMu AI device strings are `"<device name>-<OS version>"`, regex allowed (`"Galaxy.*-1[3-4]"`, `"iPhone 1[45].*-17"`). Confirm names with `GET https://mobile-api.lambdatest.com/mobile-automation/api/v1/list?region=us`.

| Test Lab | TestMu AI |
|---|---|
| `model=oriole,version=33` (Pixel 6, physical) | `Pixel 6-13` |
| `model=redfin,version=30` (Pixel 5) | `Pixel 5-11` |
| `model=b0q` (Galaxy S22 Ultra) | `Galaxy S22 Ultra-<version>` |
| `model=iphone13pro,version=16.6` | `iPhone 13 Pro-16` |
| `model=MediumPhone.arm,version=33` (virtual) | `"Pixel 6-13.0"` with `"isVirtualDevice": true` |
| `model=Pixel2.arm` (virtual, removed by Test Lab in Nov 2025) | a current virtual device, e.g. `"Pixel 6-12.0"` with `isVirtualDevice` |

Android API level to version: 26 -> 8, 27 -> 8.1, 28 -> 9, 29 -> 10, 30 -> 11, 31 -> 12, 32 -> 12L, 33 -> 13, 34 -> 14, 35 -> 15, 36 -> 16. Resolve Test Lab model ids to marketing names with `gcloud firebase test android models list`.

## 6. Robo and Game Loop

No TestMu AI equivalent. State this as a gap. For teams that used Robo for smoke coverage, the TestMu AI path is KaneAI app tests: upload the APK/IPA, write the smoke journey in natural language ("open the app, sign in, add an item to the cart"), and run it on real devices through a KaneAI test run on HyperExecute; Kane CLI (`kane-cli generate`) can scaffold the scenarios.

## 7. CI wrappers

- GitHub Actions (`google-github-actions/auth` + `gcloud firebase test ...`): replace with the upload and build calls (§8); swap the service-account secret for `LT_USERNAME`/`LT_ACCESS_KEY`.
- Fastlane: `run_tests_firebase_testlab` (pink-room plugin) and `firebase_test_lab_ios_xctest` (official plugin, archived) -> a `sh` action running the curl calls, or `Net::HTTP` in the Fastfile.
- Bitrise "Virtual Device Testing for Android/iOS" step -> a Script step with the curl calls.
- Codemagic (gcloud scripts with a `firebase_credentials` group) -> replace the gcloud script with the curl calls; drop the credentials group.
- To run Espresso/XCUI as HyperExecute jobs instead, see `hyperexecute.md` and the HyperExecute Espresso/XCUI docs pages.

## 8. Worked example (GitHub Actions)

Before:
```yaml
- uses: google-github-actions/auth@v2
  with: { credentials_json: ${{ secrets.GCP_SA }} }
- run: gcloud firebase test android run --type instrumentation --app app/build/outputs/apk/debug/app-debug.apk --test app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk --device model=oriole,version=33
```
After:
```yaml
- name: Espresso on TestMu AI
  env: { LT_USERNAME: ${{ secrets.LT_USERNAME }}, LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }} }
  run: |
    APP=$(curl -s -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST https://manual-api.lambdatest.com/app/uploadFramework -F "appFile=@app/build/outputs/apk/debug/app-debug.apk" -F "type=espresso-android" | jq -r .app_id)
    SUITE=$(curl -s -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST https://manual-api.lambdatest.com/app/uploadFramework -F "appFile=@app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk" -F "type=espresso-android" | jq -r .app_id)
    test "$APP" != "null" && test "$SUITE" != "null"
    curl -s -u "$LT_USERNAME:$LT_ACCESS_KEY" -X POST https://mobile-api.lambdatest.com/framework/v1/espresso/build -H "Content-Type: application/json" \
      -d "{\"app\":\"$APP\",\"testSuite\":\"$SUITE\",\"device\":[\"Pixel 6-13\"],\"build\":\"${GITHUB_RUN_ID}\",\"deviceLog\":true,\"network\":false,\"retries\":1}" | tee build.json
```
The build POST response shape and a polling endpoint are not documented, so this curl form cannot gate CI reliably. Prefer the HyperExecute form for CI (same uploads, then `./hyperexecute --user $LT_USERNAME --key $LT_ACCESS_KEY --config hyperexecute.yaml` with the `android/espresso` YAML from `hyperexecute.md` §11b); the job fails when tests fail.

## 9. Gotchas and unverified

- Physical TestMu AI devices behave differently from Test Lab emulators (permission dialogs, animations, network); keep `isVirtualDevice` for suites that were emulator-only, or budget a stabilisation pass.
- Not documented (27 Oct 2026): the `/framework/v1/espresso/build` response shape and a status polling endpoint. For CI that must fail on test failures, run Espresso/XCUI through HyperExecute (`hyperexecute.md` §11b), whose CLI exit code reflects the result. Casing: Espresso examples use `IdleTimeout`/`deviceLog`, XCUI examples `idleTimeout`/`devicelog`.
- Sources: firebase.google.com/docs/test-lab (android/command-line, ios/command-line, available-testing-devices, migrate); cloud.google.com gcloud firebase test android/ios run reference; TestMu AI docs getting-started-with-espresso-testing, espresso-supported-capabilities, getting-started-with-xcuitest, ios-ipa-files-xcui, regular-expression-espresso, app-automation build API reference; OpenAPI (App Automation uploadFramework response `app_id`).
