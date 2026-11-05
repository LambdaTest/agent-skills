# Migrating to HyperExecute

Read this when the user chose HyperExecute as the target (or "grid now, HyperExecute later"). HyperExecute is TestMu AI's test orchestration platform: the CLI uploads the repo, HyperExecute discovers tests, splits them across cloud VMs, runs them, retries, collects reports and artifacts. Tests either open sessions on the TestMu AI grid from the VMs (`hub.lambdatest.com`, `mobile-hub.lambdatest.com`, `cdp.lambdatest.com`; the grid migration in the vendor reference applies first), launch browsers on the VMs themselves, or keep local Selenium drivers that HyperExecute routes via `platformConfig`; §2a says which model fits.

Source: TestMu AI docs (`deep-dive-into-hyperexecute-yaml`, `hyperexecute-yaml-parameters`, `hyperexecute-yaml-version0.2`, `hyperexecute-yaml-capability-overrides`, `hyperexecute-cli-run-tests-on-hyperexecute-grid`, `saucelabs-to-hyperexecute-migrate`), read from the docs repo on 27 Oct 2026.

Contents
1. Grid or HyperExecute: what changes in each
2. What HyperExecute replaces, per source
2a. Execution models: grid sessions, browsers on the VM, platformConfig
3. Steps
4. hyperexecute.yaml: v0.1 (discovery + runner command) and v0.2 (framework block)
5. Key reference
6. Splitting strategies: autosplit, matrix, hybrid
7. Capabilities on HyperExecute: HYPEREXECUTE_PLATFORM and ltOptions overrides
7a. BrowserStack SDK repos: platformConfig
8. Secrets, env and tunnel
9. CLI
10. CI integration
11. Per-framework starting YAMLs
11a. Mapping vendor run settings (build id, timeouts, resolution, macOS, CI actions)
11b. Espresso and XCUITest on HyperExecute
12. Gotchas

## 1. Grid or HyperExecute

| | Grid (Browser Cloud / Real Device Cloud) | HyperExecute |
|---|---|---|
| Where the test process runs | your CI runner or laptop | HyperExecute VMs (linux, win, mac) |
| Code change | endpoints, `LT:Options`, hooks, tunnel | same as grid, plus `hyperexecute.yaml` |
| CI change | swap secrets | replace the test step with the `hyperexecute` CLI |
| Parallelism | your runner (`workers`, xdist, TestNG `parallel`, Cypress `parallels`) | `concurrency` + `autosplit`/`matrix`, no CI machine fan-out |
| Retries, fail-fast, test ordering | your runner | `retryOnFailure`/`maxRetries`, `failFast`, smart ordering |
| Reports, artifacts | your CI | `report`, `partialReports`, `uploadArtefacts`, job dashboard, RCA |
| Good fit | small change, quick win | replacing saucectl, BrowserStack SDK parallel runs, Device Farm server-side runs, Cypress Cloud parallelisation, CI sharding |

Ask the user which one before editing (the SKILL.md workflow says how). "Grid now, HyperExecute later" is a valid answer: do the grid migration, then add the YAML as a second PR.

## 2. What HyperExecute replaces

| Source construct | HyperExecute equivalent |
|---|---|
| BrowserStack SDK `platforms[]` + `parallelsPerPlatform` | `platformConfig.platform` + `parallelism` (§7a), or `matrix` (one combination per platform); `concurrency` |
| BrowserStack `browserstack-cypress-cli` `parallels` | `cypress: true` + `cypressOps`, `concurrency`, `autosplit` |
| BrowserStack Local in CI | `tunnel: true` (spawned by the CLI) or `tunnelNames` |
| Sauce `saucectl` (`.sauce/config.yml` suites, `concurrency`, `retries`, `shard`) | `hyperexecute.yaml` (`matrix`/`testSuites` for suites, `concurrency`, `retryOnFailure`/`maxRetries`, `autosplit`) |
| Sauce Orchestrate (container runs) | HyperExecute VMs with `runtime` + `pre` (no customer container image) |
| AWS Device Farm test spec phases (`install`, `pre_test`, `test`, `post_test`) | `pre`, `testRunnerCommand`, `post`, `uploadArtefacts` |
| Cypress Cloud `--parallel --group --ci-build-id` | `autosplit` + `concurrency`; job = build |
| Azure Playwright Workspaces `--workers=N` | `concurrency` + `autosplit` over spec files |
| CI sharding: Playwright `--shard=x/y`, GitHub Actions matrix, CircleCI `tests split --split-by=timings`, Knapsack Pro queue mode | `autosplit: true` (uses previous run timings) or `dynamicAllocation: true` |
| Self-hosted grid as the parallel runner (compose `replicas`, `SE_NODE_MAX_SESSIONS`) | `concurrency` |
| Retry plugins (`pytest-rerunfailures`, TestNG `IRetryAnalyzer`, Playwright `retries`) | keep, or move to `retryOnFailure`/`maxRetries` (1 to 5) |
| JUnit/Allure/HTML report upload steps | `report: true` + `partialReports`, `uploadArtefacts`, `mergeArtifacts` |

## 2a. Two execution models on HyperExecute (pick per suite)

| Model | Test code | When |
|---|---|---|
| A. Grid sessions from HyperExecute | tests open remote sessions on `hub.lambdatest.com` / `mobile-hub.lambdatest.com` / `cdp.lambdatest.com` with `LT:Options`; status hooks apply | source was a cloud grid (BrowserStack, Sauce Selenium/Appium, Perfecto...) and the code already has (or now has) a remote-driver factory |
| B. Browsers on the HyperExecute VM | tests launch browsers locally (`chromium.launch`, `new ChromeDriver()`); the VM OS is `runson` and is exported as `HYPEREXECUTE_PLATFORM`; no grid session, so no `lambda-status`/`setTestStatus` hook | source ran the whole project on vendor VMs (saucectl, Device Farm server-side, Cypress Cloud CI machines) |
| B'. Local Selenium driver with `platformConfig` | tests keep `new ChromeDriver()`; HyperExecute intercepts Selenium commands and routes them to the platforms listed in YAML | BrowserStack SDK repos whose code never had a remote driver (the SDK swapped it at runtime); see §7a |

Model A is the default for grid sources and for every native-app suite (Appium, including Device Farm Appium; a HyperExecute VM has no phone, so the app must run on the Real Device Cloud); model B is the default for saucectl web suites and Device Farm desktop-browser (test grid) suites; offer B' when the repo is a BrowserStack SDK (Java/TestNG documented) repo and the user wants no driver-code changes. For the grid (not HyperExecute), the config-driven equivalent of the BrowserStack SDK is the TestMu AI SDK (`lambdatest.yml`; Java TestNG and Node Playwright; see browserstack.md §5 path A).

## 3. Steps

1. Model A: finish the grid migration in code (endpoints, `LT:Options`, hooks) and run one test against the grid from a laptop first. Model B: make sure the suite runs locally with locally launched browsers. Model B': keep the local driver and write `platformConfig` (§7a).
2. Add `hyperexecute.yaml` at the repo root (start from §11).
3. Model A: set the platform per task through a `matrix` value passed to the tests (env var or system property) or override caps with `ltOptions` (§7). `HYPEREXECUTE_PLATFORM` is the VM's own OS, which only matters for model B or when the session should match the VM OS.
4. Download the CLI and run locally: `./hyperexecute --user $LT_USERNAME --key $LT_ACCESS_KEY --config hyperexecute.yaml`.
5. Replace the CI test step (§10). Remove the old vendor's orchestration (saucectl, BrowserStack SDK runner scripts, Cypress Cloud record flags, shard matrices).
6. Verify in the HyperExecute dashboard: tasks split, sessions visible under the build, retries, artifacts.

## 4. hyperexecute.yaml

Version rule: `version: 0.1` uses `testDiscovery` + `testRunnerCommand` (any language). `version: 0.2` replaces both with a `framework` block and only supports Java (Maven/Gradle TestNG, JUnit 4/5, Spock) and WebdriverIO (mocha, jasmine). Never combine `version: 0.2` with `testDiscovery`. Discovery `mode` is `local` (discovery runs where the CLI runs, needs dependencies there) or `remote` (discovery on a HyperExecute VM; needed for matrix-based distribution); older samples show `static` and `dynamic`, which are superseded.

v0.1, generic (any language): discovery command lists test entities, runner command runs one (`$test`).
```yaml
---
version: 0.1
runson: linux
autosplit: true
concurrency: 4
retryOnFailure: true
maxRetries: 1
pre:
  - pip3 install -r requirements.txt
cacheKey: '{{ checksum "requirements.txt" }}'
cacheDirectories:
  - CacheDir
testDiscovery:
  type: raw
  mode: local          # local | remote (the old "dynamic" is deprecated)
  command: grep -rl "def test_" tests
testRunnerCommand: pytest $test -v
jobLabel: [migration, pytest]
```

v0.2, Java and WebdriverIO: a `framework` block replaces discovery and the runner command; caching is automatic.
```yaml
---
version: 0.2
runson: win
autosplit: true
concurrency: 4
retryOnFailure: true
maxRetries: 1
globalTimeout: 150
testSuiteTimeout: 150
testSuiteStep: 150
framework:
  name: maven/testng           # maven|gradle + testng|junit4|junit5|spock, wdio/mocha, wdio/jasmine
  discoveryType: method        # testng: method|class|xmltest; junit: method|class; wdio: test|spec|suite|wdiosuite
  flags:
    - "-Dplatname=win"
  defaultReports: false
report: true
partialReports:
  location: target/surefire-reports/html
  type: html
  frameworkName: extent
uploadArtefacts:
  - name: Reports
    path:
      - target/surefire-reports/**
jobLabel: [selenium-testng, migration]
```
For Appium with a v0.2 Java runner add `appium: true` above `framework`; `framework.args.region: us|eu|ap` picks the device region.

## 5. Key reference

Core: `version` (0.1 | 0.2), `runson` (linux | win | mac, or `${matrix.os}`), `pre`, `post`, `concurrency`, `autosplit`, `testDiscovery` (`type: raw|automatic`, `mode: local|remote`, `command`), `testRunnerCommand` (plus `linuxTestRunnerCommand`, `winTestRunnerCommand`, `macTestRunnerCommand` in hybrid mode), `framework` (v0.2: `name`, `flags`, `discoveryFlags`, `runnerFlags`, `discoveryType`, `discoveryMode`, `defaultReports`, `workingDirectory`, `args`).
Matrix: `matrix`, `exclusionMatrix`, `combineTasksInMatrixMode`, `testSuites`, `matrixEnvPrefix`.
Hybrid: `parallelism`, `linuxParallelism`, `winParallelism`, `macParallelism`.
Dependencies: `runtime` (`- language: python|java|node|dotnet|ruby|maven ... version: "x"`), `cacheKey`, `cacheDirectories`, `env`, `vars`, `shell`, `workingDirectory`, `codeDirectory`, `preDirectives`, `postDirectives`, `globalPre`, `globalPost`, `background` (long-running app servers), `hostsOverride`.
Reliability: `retryOnFailure`, `maxRetries` (1 to 5, default 2 when enabled), `retryOptions`, `failFast`, `dynamicAllocation`, `syncStart`, `globalTimeout` (1 to 150 min, default 90), `testSuiteTimeout`, `testSuiteStep`.
Reports and artifacts: `report`, `partialReports` (`location`, `type`, `frameworkName`, `email`), `errorCategorizedReport`, `errorCategorizedOnFailureOnly`, `mergeArtifacts`, `uploadArtefacts`, `stripParentDirectory`, `linkValidity`, `captureScreenRecordingForScenarios`, `captureCSVResult`.
Network: `tunnel`, `tunnelOpts`, `tunnelNames`.
Source and project: `sourcePayload` (fetch code from git), `differentialUpload`, `base` (inherit a base YAML), `project`, `jobLabel`, `slackChannel`, `callbackURL`, `collectLocalGitData`.
Frameworks: `cypress: true` + `cypressOps`, `smartGrid` (Windows browser setup speed-up), `dataJsonPath`, `dataJsonBuilder`.

## 6. Splitting strategies

Different values per platform (devices that differ between Android and iOS): HyperExecute matrices are cartesian, so either list `platform:device` pairs as one matrix key (`target: ["android:Galaxy S23:13", "ios:iPhone 15:17"]`, split the string in the test or in a wrapper script) or use one `testSuites` entry per pair. `$key` is substituted textually into `testSuites` commands before the shell runs them, so `DEVICE="$target" python3 run.py` works; matrix values are also exported as env vars (`$target`), or as `HE_ENV_target` with `matrixEnvPrefix: true`. Env vars exported inside `pre` commands are not documented to persist into test commands; put values in the YAML `env:` map instead.

Python example with `runtime` and caching (model A, app uploaded once with a `custom_id`):
```yaml
version: 0.1
runson: linux
concurrency: 4
runtime:
  - language: python
    version: "3.11"
env:
  LT_USERNAME: ${{ .secrets.LT_USERNAME }}
  LT_ACCESS_KEY: ${{ .secrets.LT_ACCESS_KEY }}
cacheKey: '{{ checksum "requirements.txt" }}'
cacheDirectories:
  - .pip-cache
pre:
  - pip3 install --cache-dir .pip-cache -r requirements.txt
matrix:
  target: ["android:Galaxy S23:13", "ios:iPhone 15:17"]
testSuites:
  - TESTMU_TARGET="$target" python3 -m pytest tests -v
retryOnFailure: true
maxRetries: 1
```
Upload the app in the CI job before the CLI runs (`curl ... -F custom_id=myapp`), then tests use `app: "myapp"` (testmu-target.md §5), so no id has to travel from `pre` to the test process.

Matrix example (each combination becomes a task; user-defined keys are opaque to HyperExecute and are substituted as `$key` in `testSuites` and as `${matrix.key}` elsewhere):
```yaml
version: 0.1
runson: ${matrix.os}
matrix:
  os: [win, mac]
  project: [chromium, firefox, webkit]
exclusionMatrix:
  - os: [mac]
    project: [firefox]
pre:
  - npm ci
  - npx playwright install --with-deps
testSuites:
  - npx playwright test --project=$project
concurrency: 5
```
`exclusionMatrix` is a list of maps whose values are lists (deep-dive-into-hyperexecute-yaml). Matrix keys are also exported as env vars in each task; set `matrixEnvPrefix: true` to name them `HE_ENV_<key>` (e.g. `HE_ENV_os`) when a key such as `os` clashes with a tool's own variable.


- Autosplit (`autosplit: true`): HyperExecute discovers tests once and spreads them over `concurrency` VMs using previous run timings. Default choice for one OS.
- Matrix: `matrix: { os: [win, mac], browser: [chrome, edge] }` multiplies tasks; reference values as `${matrix.os}` in `runson` and commands; use for BrowserStack SDK `platforms[]` or saucectl `suites[]` that differ only by browser or OS.
- Hybrid: autosplit across several OSes with `parallelism` or per-OS `*Parallelism` and per-OS runner commands.

## 7. Capabilities on HyperExecute

- The VM exports `HYPEREXECUTE_PLATFORM`; driver factories read it for the OS: `platform: process.env.HYPEREXECUTE_PLATFORM || 'Windows 11'`. Its exact values are not documented; samples fall back to `Windows 10`, `Windows 11`, `MacOS Monterey`, `LINUX`, matching `runson` `win` (Windows 10), `win11`, `mac` (macOS Monterey), `mac13` (macOS Ventura), `linux`. Treat it as a grid platform string and log it in the first run.
- YAML capability overrides (Selenium only): an `ltOptions` map in `hyperexecute.yaml` is merged into every session's capabilities, and YAML wins over the script. Use it to set `build`, `video`, `network`, `console`, `selenium_version`, browser and version without touching code.
```yaml
ltOptions:
  build: checkout-regression
  network: true
  console: true
  video: true
```
- Test code keeps pointing at `https://hub.lambdatest.com/wd/hub` (or the mobile hub / CDP URL); HyperExecute routes it.

## 7a. BrowserStack SDK repos: `platformConfig` (local Selenium driver)

BrowserStack SDK repos create a local driver (`new ChromeDriver()`, `webdriver.Chrome()`) and the SDK redirects it to the cloud using `browserstack.yml` `platforms[]`. HyperExecute's local-driver support does the same with `platformConfig` (doc: hyperexecute-how-to-run-tests-using-local-selenium-drivers; sample is Java TestNG):
```yaml
version: 0.1
runson: win
autosplit: true
parallelism: 1            # browserstack.yml parallelsPerPlatform
concurrency: 3
testDiscovery:
  type: raw
  mode: remote
  command: grep 'test name' testng.xml | awk '{print$2}' | sed 's/name=//g' | sed 's/\x3e//g'
testRunnerCommand: mvn test
platformConfig:
  platform:                 # browserstack.yml platforms[]
    - os: mac               # OS X + any version -> mac (exact macOS version selection is not documented here)
      browserName: chrome
      browserVersion: latest
    - os: win10             # Windows + 10 -> win10; Windows + 11 -> win11
      browserName: edge
    - os: android
      deviceName: Galaxy S22 Ultra
      browserName: chrome
  config:                   # common keys from browserstack.yml (buildName, networkLogs, consoleLogs...)
    build: my-build
    network: true
    console: true
```
Tasks = platforms x `parallelism`. Documented `os` values: `win10`, `win11`, `mac`, `linux`, `android`, `ios` (no versioned mac). `platformConfig` covers browsers (desktop, and Android/iOS mobile browsers through `deviceName` + `browserName`); the doc says "Support for AndroidDriver is not yet available", so Appium native-app suites use model A with an explicit driver factory. IEDriver runs only on Windows 10; SafariDriver is not supported. Precedence: script capabilities < YAML `config` < YAML `platform` entry. For `android`/`ios`, `os` and `deviceName` are mandatory (regex allowed, `.*` for any). Unverified: support outside Java, and exact macOS version selection; when unsure, use model A with an explicit driver factory.

## 8. Secrets, env and tunnel

- Secrets live in the HyperExecute secrets vault and are referenced as `${{ .secrets.KeyName }}` inside `env`; CLI `--job-secret-file` passes a file of secrets for one job.
- `env:` sets VM environment variables; `vars:` defines YAML variables used as `${name}`.
- `tunnel: true` makes the CLI start a tunnel from the machine running the CLI (your CI runner or laptop) to the VMs and their browser sessions, so tests reach hosts that only that machine can reach (staging behind VPN, a server started in CI). It does not reach services started on the HyperExecute VM itself; start those with `background:` and use `localhost` from the VM. `tunnelNames: [name]` uses already-running named tunnels; `tunnelOpts` holds tunnel settings; CLI `--tests-per-tunnel` caps load per tunnel.
- `tunnel: true` in the YAML makes the CLI start the tunnel as a subprocess; do not also set a tunnel in the session capabilities, because the troubleshooting guide says a tunnel configured in both places may disconnect (hyperexecute-scenario-steps-error). Remove `tunnel`/`tunnelName` from `LT:Options` when the YAML owns the tunnel.
- Credentials on the VM: tests that open grid sessions (model A) need `LT_USERNAME`/`LT_ACCESS_KEY` on the VM. Store them in the HyperExecute secrets vault and map them in `env:` (`LT_USERNAME: ${{ .secrets.LT_USERNAME }}`); do not commit them to the YAML.
- `.hyperexecuteignore` (gitignore syntax) excludes files from the uploaded archive; if `.gitignore` also exists, `.gitignore` takes precedence.

## 9. CLI

Download: `https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute`, `.../darwin/hyperexecute`, `.../windows/hyperexecute.exe`; `chmod u+x hyperexecute` on macOS/Linux.
Run: `./hyperexecute --user $LT_USERNAME --key $LT_ACCESS_KEY --config hyperexecute.yaml`.
Common flags: `--concurrency`, `--runson`, `--labels`, `--vars`, `--job-secret-file`, `--download-artifacts`, `--download-artifacts-path`, `--download-artifacts-zip`, `--download-report`, `--download-logs`, `--force-clean-artifacts`, `--target-directory`, `--target-path`, `--use-zip`, `--tests-per-tunnel`, `--validate` (check YAML), `--no-track`, `--preserve-payload`, `--verbose`, `--version`, `--disable-updates`, `--auto-proxy`. Set `CI=true` for quiet CI output.

## 10. CI integration

GitHub Actions:
```yaml
- name: Run on HyperExecute
  env:
    LT_USERNAME: ${{ secrets.LT_USERNAME }}
    LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
  run: |
    curl -sSL https://downloads.lambdatest.com/hyperexecute/linux/hyperexecute -o hyperexecute
    chmod u+x hyperexecute
    ./hyperexecute --user "$LT_USERNAME" --key "$LT_ACCESS_KEY" --config hyperexecute.yaml --download-artifacts --download-report
```
The same three lines work in GitLab, Jenkins, Azure DevOps, CircleCI, Bitbucket, Bamboo, TeamCity, Travis, Semaphore, GoCD and AWS CodePipeline (TestMu docs have a page per CI tool). The CLI exit code reflects the job result. Remove the CI matrix or shard jobs that the old setup used only for parallelism; keep matrices over language or OS versions that build and unit-test the code itself (SKILL.md step 5).

## 11. Per-framework starting YAMLs

| Framework | Discovery / framework | Runner |
|---|---|---|
| Java TestNG / JUnit (Maven/Gradle) | v0.2 `framework.name: maven/testng` etc. | built in |
| WebdriverIO | v0.2 `framework.name: wdio/mocha` or `wdio/jasmine` | built in |
| pytest | `grep -rl "def test_" tests` | `pytest $test` |
| Playwright Test (Node) | `npx playwright test --list` piped to file names, or `find tests -name "*.spec.ts"` | `npx playwright test $test` |
| Cypress | `cypress: true`, `cypressOps`, discovery over `cypress/e2e/**/*.cy.*` | `npx cypress run --spec $test` |
| NUnit / xUnit / MSTest | `dotnet test --list-tests` or grep on `[Test]` | `dotnet test --filter "FullyQualifiedName~$test"` |
| Ruby RSpec / Cucumber | `find spec -name "*_spec.rb"` / grep `Scenario:` | `bundle exec rspec $test` / `cucumber $test` |
| Robot Framework | grep test names in `*.robot` | `robot --test "$test" tests/` |
| Behave / Cucumber JVM / SpecFlow / Reqnroll | feature files or tags | per framework |
| Appium (any language) | as above, with `appium: true` for v0.2 Java | as above |
| Espresso / XCUITest | `framework.name: android/espresso` or `ios/xcui` (§11b) | built in |
| Plain programs with no test framework (a console app or script per scenario) | no discovery: list each run as a `testSuites` entry, or a matrix key (`scenario: [single, local, parallel]` with `testSuites: - dotnet run -- $scenario`) | the program's own command; it must exit non-zero on failure |
| JMeter / k6 / Gatling | HyperExecute performance pages | built in |

## 11b. Espresso and XCUITest on HyperExecute

```yaml
version: "0.2"
runson: android
autosplit: true
concurrency: 2
framework:
  name: "android/espresso"
  args:
    buildName: "espresso-${GITHUB_RUN_ID}"
    video: true
    deviceLog: true
    appPath: app/build/outputs/apk/debug/app-debug.apk          # or appId: lt://APP...
    testSuitePath: app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk   # or testSuiteAppId
    deviceSelectionStrategy: any                                 # any | all
    devices: ["Galaxy.*", "Pixel.*"]
    # isVirtualDevice: true                                      # emulators
    # filters: { attributes: [ { type: class, values: [com.acme.LoginTest] } ] }   # class | package | annotation
env:
  STAGE: stg1                                                    # instrumentation env vars
```
XCUI: `runson: ios`, `framework.name: "ios/xcui"`, same `appPath`/`testSuitePath` (the `.ipa` files), filters `type: className|testName`; manual shards with `autosplit: false` and `shards.mappings: [{name, strategy: only-testing|skip-testing, values}]` (Espresso strategies: `class`, `package`, `skipClass`, ...). Samples: github.com/LambdaTest/hyp-real-device-espresso, github.com/LambdaTest/hyperexecute-xcui-sample.

TestMu publishes a sample repo per framework under `github.com/LambdaTest/*-hyperexecute-sample` (for example `testng-selenium-hyperexecute-sample`); copy the closest one's YAML.

## 11a. Mapping vendor run settings

- Build name / build id: `--labels "build-${RUN_ID}"` on the CLI or `jobLabel`; for grid sessions also set `LT:Options.build`.
- Per-suite timeouts (saucectl `suites[].timeout`): `testSuiteTimeout` (all scenario stages in a task, max 150 min); per-test: `testSuiteStep`; whole job: `globalTimeout`.
- `screenResolution` for model B: set the window size in the test framework (`viewport` in Playwright config); for model A use `LT:Options.resolution`.
- macOS versions: `runson: mac` (CLI `--runson` also documents `mac13`); a specific macOS minor version is not selectable in the documented YAML.
- saucectl GitHub Action / CircleCI orb / `.gitpod.yml` steps -> the three-line CLI download and run (§10).

## 12. Gotchas

- HyperExecute VMs run the test process; anything the old CI runner provided (Docker services, local DB, OS packages) must move to `pre`, `background` or `runtime`.
- `mode: local` discovery needs the framework installed where the CLI runs; use `mode: remote` (or v0.2) when the CI runner is bare.
- Hard-coded `platform` in caps overrides the matrix intent; read `HYPEREXECUTE_PLATFORM` or use `ltOptions`.
- `globalTimeout` caps the whole job at 150 minutes; split long suites with higher `concurrency`.
- `ltOptions` overrides are Selenium only (hyperexecute-yaml-capability-overrides: "only supported for Selenium-based tests at the moment"); Appium and Playwright sessions take their platform from code (env var or matrix value).
