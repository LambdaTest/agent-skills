---
name: reqnroll-skill
description: >
  Generates production-grade Reqnroll BDD automation scripts for web (Selenium 3/4)
  and mobile (Appium 2) testing in C#. Supports parallel NUnit execution locally and
  on TestMu AI cloud. Use when the user asks to write BDD tests, automate with Reqnroll,
  create .feature files, write Gherkin scenarios, write step definitions, migrate from
  SpecFlow, or test on browsers/Android/iOS. Triggers on: "Reqnroll", "BDD", "Gherkin",
  ".feature file", "step definition", "SpecFlow migration", "Selenium C#", "Appium C#",
  "TestMu", "LambdaTest", "NUnit BDD", "reqnroll.actions.json".
languages:
  - C#
category: bdd-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

## Overview

This skill guides QA engineers and test architects in writing production-grade Reqnroll
BDD tests for web and mobile automation in C#. It covers three execution paths — Selenium 4
with manual driver management, Selenium 3 via the `Reqnroll.Actions` plugin, and Appium 2
for Android mobile — all targeting TestMu AI (LambdaTest) cloud infrastructure.

Reqnroll is the actively maintained open-source successor to SpecFlow. Existing SpecFlow
projects can migrate by swapping the NuGet package and namespace — no step definition
rewrites required.

## Key Execution Pathways

**Framework Selection:** Distinguishes between Selenium 4 (manual `DriverFactory`),
Selenium 3 (`Reqnroll.SpecFlowCompatibility.Actions.LambdaTest` plugin with
`IBrowserInteractions`), and Appium 2 (`Appium.WebDriver`, `AndroidDriver`).

**Cloud vs Local:** Reads `LT_USERNAME` and `LT_ACCESS_KEY` environment variables;
routes to `hub.lambdatest.com` (web) or `mobile-hub.lambdatest.com` (mobile).
Reports pass/fail to LambdaTest via `lambda-status` JavaScript executor calls in
`[AfterScenario]`.

**Parallelism:** Uses `[assembly: Parallelizable(ParallelScope.Fixtures)]` with
`[assembly: LevelOfParallelism(N)]` (NUnit). State is shared between step definition
classes via `ScenarioContext` (injected by Reqnroll's DI container), not static fields.

## Core Technical Patterns

### Feature Files (Gherkin)
Each `.feature` file maps to one test class. Scenarios are tagged (`@tagName`) for
selective filtering with `dotnet test --filter "Category=tagName"`. Background steps
run before every scenario in the file; Scenario Outlines drive data-driven testing via
`Examples` tables.

### Step Definitions
Classes are decorated with `[Binding]`. Constructor injection (via Reqnroll's built-in
DI) receives `ScenarioContext` or shared context objects. One `[Binding]` class per
concern keeps files small. Regex-based step patterns use `(.*)` or typed captures
(`(\d+)`) — no attribute-level type converters needed for primitives.

### Hooks
`[BeforeScenario]` initialises the driver (stored in `ScenarioContext["driver"]`) and
navigates to the base URL. `[AfterScenario]` reads `_scenarioContext.TestError` (web) or
`TestContext.CurrentContext.Result.Outcome.Status` (mobile) to emit
`lambda-status=passed/failed` before `driver.Quit()`.

### ScenarioContext Driver Sharing
Drivers are stored as `_scenarioContext["driver"] = driver` and retrieved with
`scenarioContext["driver"] as IWebDriver`. This is required for parallel execution —
`static` driver fields cause race conditions.

### Explicit Waits
`WebDriverWait` with `Until(d => d.FindElement(locator))` replaces `ImplicitWait`
for dynamic content. A `WaitAndFind(By)` helper method encapsulates the 10-second
default; a `WaitAndClick(By, int timeout)` variant handles clickability.

## Cloud Integration (TestMu / LambdaTest)

### Web (Selenium 4)
```csharp
var ltOptions = new Dictionary<string, object>
{
    { "build", "Build Name" },
    { "project", "Project Name" },
    { "w3c", true },
    { "selenium_version", "4.38.0" },
    { "sessionName", scenarioName },
    { "platformName", "Windows 11" }
};
var options = new ChromeOptions();
options.BrowserVersion = "latest";
options.AddAdditionalOption("LT:Options", ltOptions);
var driver = new RemoteWebDriver(
    new Uri($"https://{userName}:{accessKey}@hub.lambdatest.com/wd/hub"), options);
```

### Mobile (Appium 2)
```csharp
var ltOptions = new Dictionary<string, object>
{
    { "build", "Build Name" },
    { "project", "Project Name" },
    { "w3c", true },
    { "app", "proverbial-android" },         // lt:// URI or pre-uploaded alias
    { "platformName", "android" },
    { "deviceName", "Galaxy.*" },
    { "platformVersion", "14" },
    { "isRealMobile", true },
    { "autoAcceptAlerts", true },
    { "autoGrantPermissions", true },
    { "sessionName", scenarioName }
};
var appiumOptions = new AppiumOptions();
appiumOptions.AddAdditionalAppiumOption("LT:Options", ltOptions);
var driver = new AndroidDriver(
    new Uri($"https://{userName}:{accessKey}@mobile-hub.lambdatest.com/wd/hub"),
    appiumOptions);
```

### Reporting Pass/Fail
```csharp
// Web (AfterScenario)
if (_scenarioContext.TestError == null)
    ((IJavaScriptExecutor)driver).ExecuteScript("lambda-status=passed");
else
    ((IJavaScriptExecutor)driver).ExecuteScript("lambda-status=failed");

// Mobile (AfterScenario)
bool passed = TestContext.CurrentContext.Result.Outcome.Status == TestStatus.Passed;
((IJavaScriptExecutor)driver).ExecuteScript("lambda-status=" + (passed ? "passed" : "failed"));
```

## Quality Checkpoints

- Feature files use descriptive scenario names that double as the LambdaTest session name
- `ScenarioContext` used for driver sharing — never static fields in parallel runs
- `[assembly: Parallelizable(ParallelScope.Fixtures)]` declared once in any `.cs` file
- `LT_USERNAME` and `LT_ACCESS_KEY` read from environment — never hardcoded
- `lambda-status=passed/failed` emitted in every `[AfterScenario]` for cloud runs
- `WebDriverWait` used throughout — no unconditional `Thread.Sleep` except transient Appium delays
- Appium locators use `MobileBy.Id` (resource-id) or `MobileBy.AccessibilityId` before XPath
- `driver.Quit()` always called in `[AfterScenario]` to free cloud device slots
- `dotnet test --logger "console;verbosity=detailed"` surfaces per-scenario pass/fail

## Reference Structure

The `reference/` directory contains detailed playbook sections:

| File | Contents |
|------|----------|
| `playbook.md` | Full implementation guide: project setup, all three driver modes, parallel execution, CI/CD, debugging table, best practices checklist |
| `cloud-integration.md` | LambdaTest capability reference, `LT:Options` fields, tunnel setup, build/session naming, test observability |
| `selenium-4-patterns.md` | Selenium 4 patterns: `DriverFactory`, multi-browser, `ChromeOptions`/`FirefoxOptions`/`EdgeOptions`, screenshot on failure |
| `selenium-3-patterns.md` | Selenium 3 patterns: `Reqnroll.SpecFlowCompatibility.Actions.LambdaTest`, `IBrowserInteractions`, `reqnroll.actions.json` config |
| `appium-patterns.md` | Appium 2 patterns: `AndroidDriver`, `AppiumOptions`, gesture helpers, `MobileBy` locators, app lifecycle |
