# Language-specific mechanics

How to express the same migration in each language binding: where vendor options go, how to URL-encode the CDP capabilities, where to hook test status, and what to uninstall. Read the row for the language in play; the vendor files say what the values are, this file says how to write them.

Contents
1. Vendor option object per binding
2. CDP URL encoding (Playwright / Puppeteer)
3. Status hook placement per test framework
4. Credential loading
5. Dependency changes
6. Kotlin, Scala, Groovy, Swift, Dart and other less common hosts

## 1. Vendor option object per binding (Selenium / Appium)

| Language / binding | Set vendor block | Set W3C platform/browser |
|---|---|---|
| Java (selenium 4) | `options.setCapability("LT:Options", Map<String,Object>)` or `MutableCapabilities ltOptions; options.setCapability("LT:Options", ltOptions)` | `options.setPlatformName("Windows 11"); options.setBrowserVersion("latest")` |
| Java Appium | `UiAutomator2Options`/`XCUITestOptions`: `options.setCapability("LT:Options", map)` or flat `options.setCapability("deviceName", ...)` with `w3c: false` | |
| Python (selenium 4) | `options.set_capability("LT:Options", dict)` | `options.platform_name = "Windows 11"; options.browser_version = "latest"` |
| Python Appium | `UiAutomator2Options().load_capabilities({...})` or `options.set_capability(...)` | |
| JavaScript (selenium-webdriver) | plain object `{ browserName, browserVersion, "LT:Options": {...} }` passed to `.withCapabilities()` | top-level keys |
| WebdriverIO | `capabilities: [{ browserName, browserVersion, "LT:Options": {...} }]` in `wdio.conf` | |
| C# | `options.AddAdditionalOption("LT:Options", Dictionary<string, object>)` | `options.PlatformName = "Windows 11"; options.BrowserVersion = "latest"` |
| Ruby | `options.add_option('LT:Options', hash)` | `Selenium::WebDriver::Options.chrome(platform_name:, browser_version:)` |
| PHP (php-webdriver) | `$caps->setCapability('LT:Options', array)` | `$caps->setCapability('platformName', ...)`; `DesiredCapabilities::chrome()` |
| Go (tebeka/selenium) | `selenium.Capabilities{"LT:Options": map[string]interface{}{...}}` | top-level keys in the same map |
| Kotlin | same as Java (`mapOf(...)`, `hashMapOf`) | |
| Robot Framework | `&{lt}= Create Dictionary username=%{LT_USERNAME} ...` then `options.set_capability("LT:Options", ${lt})` via `Open Browser ... options=...` or `desired_capabilities` on older SeleniumLibrary | |

Nested keys like `smartUI.project` or `accessibility.wcagVersion` are literal dotted strings, not nested objects: `lt.put("smartUI.project", "x")`.

Booleans: TestMu accepts real booleans; BrowserStack/Sauce suites often carry `"true"` strings. Convert to the language's boolean (`true`, `True`, `$true`) when rewriting.

## 2. CDP URL encoding (Playwright / Puppeteer)

| Language | Encoding |
|---|---|
| Node/TS | `encodeURIComponent(JSON.stringify(capabilities))` |
| Python | `urllib.parse.quote(json.dumps(capabilities))` |
| Java | `URLEncoder.encode(gson.toJson(capabilities), StandardCharsets.UTF_8)` (Gson or Jackson) |
| C# | `Uri.EscapeDataString(JsonConvert.SerializeObject(capabilities))` or `JsonSerializer.Serialize` |
| Ruby | `URI.encode_www_form_component(JSON.generate(capabilities))` |
| PHP | `rawurlencode(json_encode($capabilities))` |
| Go | `url.QueryEscape(string(jsonBytes))` |

URL: `wss://cdp.lambdatest.com/playwright?capabilities=<encoded>` (Puppeteer: `/puppeteer?capabilities=`). BrowserStack used `caps=`; Moon used path segments; Azure used a service config. Only Node has an official TestMu SDK (`@lambdatest/playwright-node-sdk`); other languages connect manually.

## 3. Status hook placement

The session shows "Completed" unless the test reports `passed`/`failed`. Put the hook where the test outcome is known.

| Framework | Hook | Status call |
|---|---|---|
| JUnit 5 | `TestWatcher` (`testSuccessful`/`testFailed`) or `@AfterEach` reading an outcome flag | `((JavascriptExecutor) driver).executeScript("lambda-status=" + status)` |
| JUnit 4 | `@Rule TestWatcher`; the rule wraps `@Before`/`@After`, so if `@After` calls `driver.quit()` the watcher runs on a closed session. Send the status and quit inside the watcher's `succeeded`/`failed` + `finished`, or record the outcome in the watcher and send it from an outer `RuleChain` | same |
| TestNG | `ITestListener.onTestSuccess/onTestFailure` or `@AfterMethod(alwaysRun=true)` with `ITestResult result` (`result.getStatus() == ITestResult.SUCCESS`) | same |
| Cucumber JVM | `@After(Scenario scenario)` -> `scenario.isFailed()` | same, plus `lambda-name=` + `scenario.getName()` in `@Before` |
| pytest | `conftest.py` `pytest_runtest_makereport` hookwrapper sets `item.rep_call`; fixture teardown reads it | `driver.execute_script("lambda-status=" + ("failed" if failed else "passed"))` |
| unittest (run by `python -m unittest`) | `tearDown` checks `self._outcome.errors` (3.4 to 3.10) or `self._outcome.result.failures` (3.11+) | same |
| unittest classes run by pytest | `self._outcome` does not reflect failures under pytest (every test reads as passed); use the pytest `conftest.py` hookwrapper row above and reach the driver through `item.instance.driver` | same |
| Robot Framework | `Run Keyword If Test Failed` / `Test Teardown` with `${TEST STATUS}` | `Execute Javascript lambda-status=${status}` |
| Behave | `after_scenario(context, scenario)` -> `scenario.status` | same |
| Mocha / Jest (selenium-webdriver, wdio) | `afterEach(function(){ this.currentTest.state })` (Mocha) ; Jest: wrap in `try/catch` or use `jest-circus` `handleTestEvent` | `await driver.executeScript("lambda-status=" + status)` |
| WebdriverIO | nothing; `wdio-lambdatest-service` sets name and status | |
| Nightwatch | `globals.js` `afterEach(browser, done)`: read `browser.currentTest.results` (`failed`/`errors` > 0), send the status, then `browser.end(done)`. Nightwatch closes the session on failure (`end_session_on_fail`, default true) and tests often call `browser.end()` themselves: set `end_session_on_fail: false` and move `browser.end()` into the hook so the status call still has a session; assertions stay untouched | `browser.execute('lambda-status=' + status)` |
| Playwright Test | fixture teardown (`testInfo.status === testInfo.expectedStatus`) | `page.evaluate(_ => {}, 'lambdatest_action: {"action":"setTestStatus","arguments":{"status":"passed","remark":"ok"}}')` |
| Playwright (pytest-playwright / Java / C#) | same pattern in the language's fixture/teardown | same `lambdatest_action` string |
| Cypress | nothing; `lambdatest-cypress-cli` reports per spec | |
| NUnit | `[TearDown]` with `TestContext.CurrentContext.Result.Outcome.Status == TestStatus.Passed` | `((IJavaScriptExecutor)driver).ExecuteScript("lambda-status=" + status)` |
| xUnit | implement `IDisposable` + a test outcome via `ITestOutputHelper`/custom `BeforeAfterTestAttribute`; or set `failed` in catch | same |
| MSTest | `[TestCleanup]` with `TestContext.CurrentTestOutcome == UnitTestOutcome.Passed` | same |
| SpecFlow / Reqnroll | `[AfterScenario]` with `ScenarioContext.TestError == null` | same |
| RSpec | `after(:each) do |example| example.exception.nil?` | `driver.execute_script("lambda-status=#{status}")` |
| Cucumber Ruby | `After do |scenario| scenario.failed?` | same |
| Minitest | `teardown` with `passed?` | same |
| PHPUnit | `tearDown()` with `$this->status()` / `hasFailed()` (PHPUnit 9/10) | `$driver->executeScript("lambda-status=$status")` |
| Codeception | `_after(\Codeception\TestInterface $test)` + `$test->getMetadata()` or a `Codeception\Event` subscriber | same |
| Go testing | `t.Cleanup(func(){ if t.Failed() {...} })` | `wd.ExecuteScript("lambda-status="+status, nil)` |
| Appium (any) | same as the host framework; executor string identical | |

Plain scripts with no test framework (a `main()` or a top-level Python script, common in vendor samples): wrap the body in try/except/finally (try/catch/finally), set `status = "passed"` at the end of `try`, `"failed"` in `except`/`catch`, re-raise so the process still exits non-zero exactly as before, and in `finally` send `lambda-status=` then `driver.quit()`. Where the script checks a condition and only prints the result (no exception), send `failed` for the same condition it prints as a failure; do not add new assertions.

Also send `lambda-name=<test name>` at session start (or set `name` in caps per test) so the dashboard is searchable. Replace `browserstack_executor ... setSessionName`, `sauce:job-name=`, `reportiumClient.testStart` with this.

## 4. Credential loading

Replace `BROWSERSTACK_USERNAME`/`BROWSERSTACK_ACCESS_KEY`, `SAUCE_USERNAME`/`SAUCE_ACCESS_KEY`, `KOBITON_USERNAME`/`KOBITON_API_KEY`, `SEETEST_IO_ACCESS_KEY`, `HEADSPIN_API_TOKEN`, `PLAYWRIGHT_SERVICE_ACCESS_TOKEN` with `LT_USERNAME`/`LT_ACCESS_KEY` everywhere: code, `.env`, `.env.example`, CI secrets (GitHub Actions `${{ secrets.LT_USERNAME }}`, GitLab variables, Jenkins credentials ids, Azure Pipelines variable groups), Docker compose `environment:`, `Makefile`, `package.json` scripts, `pom.xml` `<systemPropertyVariables>`, `pytest.ini`/`tox.ini` `passenv`, `appsettings.json`.

Read: Java `System.getenv("LT_USERNAME")`; Python `os.getenv`; Node `process.env`; C# `Environment.GetEnvironmentVariable`; Ruby `ENV[]`; PHP `getenv()`; Go `os.Getenv`; Robot `%{LT_USERNAME}`; shell `$LT_USERNAME`.

Do not embed credentials in the hub URL inside committed code when the suite previously used a vendor block; keep them in `LT:Options` read from env.

## 5. Dependency changes

| Language | Remove | Add |
|---|---|---|
| Node | `browserstack-node-sdk`, `browserstack-local`, `browserstack-cypress-cli`, `@wdio/browserstack-service`, `testcafe-browser-provider-browserstack`, `@nightwatch/browserstack`, `@percy/*`, `@wdio/sauce-service`, `saucectl`, `@saucelabs/playwright-reporter`, `testcafe-browser-provider-saucelabs`, `@azure/playwright`, `@azure/microsoft-playwright-testing`, `@aerokube/cypress-moon` | `lambdatest-cypress-cli`, `wdio-lambdatest-service`, `testcafe-browser-provider-lambdatest`, `@lambdatest/node-tunnel`, `@lambdatest/playwright-node-sdk`, `@lambdatest/playwright-driver`, `@lambdatest/cypress-driver`, `@lambdatest/smartui-cli` as needed |
| Python | `browserstack-sdk`, `browserstack-local`, `percy-selenium`, `saucebindings` | `lambdatest-selenium-driver` (SmartUI) if visual; otherwise nothing (plain `selenium`/`Appium-Python-Client`) |
| Java | `com.browserstack:browserstack-java-sdk` (+ surefire `-javaagent` argLine, `maven-dependency-plugin` `getClasspathFilenames`), `com.browserstack:browserstack-local-java`, `io.percy:percy-java-selenium`, `com.saucelabs:sauce_bindings`, `com.perfecto.reporting-sdk:reportium-java` | `io.github.lambdatest:lambdatest-java-sdk` (SmartUI) if visual |
| C# | `BrowserStack.TestAdapter`, `BrowserStackLocal`, `PercyIO.Selenium`, `Sauce.Bindings` | none required |
| Ruby | `browserstack-local`, `percy-selenium`, `sauce_bindings` | none required |
| PHP | `browserstack/local` | none required |
| Go | none typical | none |
| Any | `browserstack.yml`, `browserstack.json`, `.sauce/config.yml`, `credentials.yml`, `playwright.service.config.ts`, test spec YAML (Device Farm), `browsers.json` (Selenoid) | `lambdatest-config.json` (Cypress), `hyperexecute.yaml` (if orchestrating), `.smartui.json` (if visual), `.lt.yaml` (tunnel) |

## 6. Less common hosts

- Kotlin / Scala / Groovy (Spock, Geb): identical to Java bindings. Geb: `GebConfig.groovy` `driver = { new RemoteWebDriver(new URL("https://hub.lambdatest.com/wd/hub"), options) }`.
- Swift (XCUITest on device): no client-side hub; upload via `uploadFramework` and the `xcui/build` API.
- Dart / Flutter: Flutter integration tests run as Espresso/XCUITest wrappers or via `appium-flutter-driver` (`automationName: Flutter` is supported on TestMu per the Appium caps page).
- Rust (thirtyfour), Elixir (Hound/Wallaby), Clojure (etaoin): all speak W3C; pass `LT:Options` as an extra capability map and swap the hub URL. Status hook via `execute_script` equivalents.
- Karate: `configure driver = { type: 'chrome', webDriverUrl: 'https://USER:KEY@hub.lambdatest.com/wd/hub', webDriverSession: { capabilities: { browserName: 'chrome', 'LT:Options': {...} } } }`.
- Katalon: run via HyperExecute (`runtime: [{language: katalon}]`) or Remote Web Testing settings with the hub URL.
