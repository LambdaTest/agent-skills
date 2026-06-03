# Reqnroll — Advanced Implementation Playbook

## §1 — Project Setup

### Selenium 4 (manual driver, recommended for new projects)

```xml
<!-- reqnroll.cloud.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk"  Version="18.0.1" />
    <PackageReference Include="Selenium.WebDriver"      Version="4.38.0" />
    <PackageReference Include="Reqnroll.NUnit"           Version="2.4.1" />
    <PackageReference Include="nunit"                    Version="4.4.0" />
    <PackageReference Include="NUnit3TestAdapter"        Version="5.2.0" />
    <PackageReference Include="FluentAssertions"         Version="8.8.0" />
  </ItemGroup>
</Project>
```

### Selenium 3 (Reqnroll.Actions plugin — IBrowserInteractions abstraction)

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.NET.Test.Sdk"                           Version="18.0.1" />
  <PackageReference Include="Selenium.WebDriver"                               Version="3.141.0" />
  <PackageReference Include="Reqnroll.SpecFlowCompatibility.Actions.LambdaTest" Version="0.2.6" />
  <PackageReference Include="Reqnroll.NUnit"                                   Version="2.4.1" />
  <PackageReference Include="nunit"                                             Version="4.4.0" />
  <PackageReference Include="NUnit3TestAdapter"                                 Version="5.2.0" />
  <PackageReference Include="FluentAssertions"                                 Version="8.8.0" />
</ItemGroup>
```

> **Note:** `Reqnroll.SpecFlowCompatibility.Actions.LambdaTest` is only compatible with
> Selenium 3.141. For Selenium 4, use manual `DriverFactory` instead.

### Appium 2 (Android / iOS mobile)

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.NET.Test.Sdk"         Version="18.0.1" />
  <PackageReference Include="Selenium.WebDriver"             Version="4.38.0" />
  <PackageReference Include="Selenium.Support"               Version="4.38.0" />
  <PackageReference Include="Appium.WebDriver"               Version="8.2.0" />
  <PackageReference Include="DotNetSeleniumExtras.WaitHelpers" Version="3.11.0" />
  <PackageReference Include="Reqnroll.NUnit"                 Version="3.3.4" />
  <PackageReference Include="nunit"                          Version="4.5.1" />
  <PackageReference Include="NUnit3TestAdapter"              Version="6.2.0" />
  <PackageReference Include="FluentAssertions"               Version="8.8.0" />
</ItemGroup>
```

---

## §2 — Feature File Structure

```gherkin
Feature: ECommerce Playground Search

@searchItems
Scenario: Search for iPod Nano
    Given I select the Software category
    When I search for iPod Nano
    Then I should get 4 results for iPod Nano

@searchItems
Scenario Outline: Search for multiple products
    Given I select the <category> category
    When I search for <product>
    Then I should get <count> results for <product>

    Examples:
      | category | product       | count |
      | Tablets  | HTC Touch HD  | 8     |
      | Software | iPod Nano     | 4     |
```

**Conventions:**
- One `Feature:` per file; file name mirrors the feature name (kebab-case)
- Tag scenarios with `@tagName` to filter: `dotnet test --filter "Category=tagName"`
- Use `Background:` for steps that repeat in every scenario of the file
- Keep scenario titles unique — they become the LambdaTest session name

---

## §3 — Step Definitions

```csharp
using NUnit.Framework;
using OpenQA.Selenium;
using Reqnroll;
using OpenQA.Selenium.Support.UI;

[assembly: Parallelizable(ParallelScope.Fixtures)]
[assembly: LevelOfParallelism(4)]

namespace MyProject.StepDefinitions
{
    [Binding]
    public class SearchStepDefinitions
    {
        private readonly IWebDriver _driver;

        public SearchStepDefinitions(ScenarioContext scenarioContext)
        {
            _driver = scenarioContext["driver"] as IWebDriver;
        }

        private IWebElement WaitAndFind(By locator) =>
            new WebDriverWait(_driver, TimeSpan.FromSeconds(10))
                .Until(d => d.FindElement(locator));

        private IReadOnlyCollection<IWebElement> WaitAndFindAll(By locator) =>
            new WebDriverWait(_driver, TimeSpan.FromSeconds(10))
                .Until(d => d.FindElements(locator));

        [Given(@"I select the (.*) category")]
        public void GivenISelectTheCategory(string category)
        {
            WaitAndFind(By.XPath(
                "(//div[@class='dropdown search-category']/button[@type='button'])[1]")
            ).Click();
            WaitAndFind(By.XPath($"(//a[text()='{category}'])[1]")).Click();
        }

        [When(@"I search for (.*)")]
        public void WhenISearchFor(string product)
        {
            WaitAndFind(By.XPath("(//input[@name='search'])[1]")).SendKeys(product);
            WaitAndFind(By.XPath("(//button[normalize-space()='Search'])[1]")).Click();
        }

        [Then(@"I should get (.*) results for (.*)")]
        public void ThenIShouldGetResults(int expected, string product)
        {
            int actual = WaitAndFindAll(
                By.XPath($"//div[@class='row']//div[@class='carousel-item active']/img[@alt='{product}']")
            ).Count;
            Assert.That(actual, Is.EqualTo(expected));
        }
    }
}
```

---

## §4 — Hooks (BeforeScenario / AfterScenario)

### Selenium 4 Hooks

```csharp
using OpenQA.Selenium;
using Reqnroll;

namespace MyProject.Support
{
    [Binding]
    public sealed class Hooks
    {
        private readonly ScenarioContext _scenarioContext;

        public Hooks(ScenarioContext scenarioContext)
        {
            _scenarioContext = scenarioContext;
        }

        [BeforeScenario]
        public void SetUp()
        {
            string scenarioName = _scenarioContext.ScenarioInfo.Title;
            var driver = DriverFactory.CreateDriver(scenarioName);
            _scenarioContext["driver"] = driver;
            driver.Navigate().GoToUrl("https://ecommerce-playground.lambdatest.io/");
        }

        [AfterScenario]
        public void TearDown()
        {
            var platform = Environment.GetEnvironmentVariable("EXEC_PLATFORM")?.ToLower() ?? "local";
            if (_scenarioContext.TryGetValue("driver", out IWebDriver driver))
            {
                if (platform == "cloud")
                {
                    var status = _scenarioContext.TestError == null ? "passed" : "failed";
                    ((IJavaScriptExecutor)driver).ExecuteScript($"lambda-status={status}");
                }
                driver.Quit();
            }
        }
    }
}
```

### Appium Hooks

```csharp
using NUnit.Framework;
using NUnit.Framework.Interfaces;
using OpenQA.Selenium;
using OpenQA.Selenium.Appium.Android;
using Reqnroll;

namespace MyProject.Support
{
    [Binding]
    public sealed class Hooks
    {
        private readonly ScenarioContext _scenarioContext;

        public Hooks(ScenarioContext scenarioContext)
        {
            _scenarioContext = scenarioContext;
        }

        [BeforeScenario]
        public void SetUp()
        {
            string scenarioName = _scenarioContext.ScenarioInfo.Title;
            var driver = DriverFactory.CreateCloudAppiumDriver(scenarioName);
            _scenarioContext["driver"] = driver;
        }

        [AfterScenario]
        public void TearDown()
        {
            bool passed = TestContext.CurrentContext.Result.Outcome.Status == TestStatus.Passed;
            if (_scenarioContext.TryGetValue("driver", out AndroidDriver driver))
            {
                ((IJavaScriptExecutor)driver).ExecuteScript(
                    "lambda-status=" + (passed ? "passed" : "failed"));
                driver.Quit();
            }
        }
    }
}
```

---

## §5 — DriverFactory (Selenium 4 — LambdaTest Cloud)

```csharp
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using OpenQA.Selenium.Firefox;
using OpenQA.Selenium.Edge;
using OpenQA.Selenium.Remote;

namespace MyProject.Support
{
    public static class DriverFactory
    {
        public static IWebDriver CreateDriver(string scenarioName)
        {
            return CreateCloudDriver(scenarioName);
        }

        private static IWebDriver CreateCloudDriver(string scenarioName)
        {
            string userName  = Environment.GetEnvironmentVariable("LT_USERNAME")   ?? "LT_USERNAME";
            string accessKey = Environment.GetEnvironmentVariable("LT_ACCESS_KEY") ?? "LT_ACCESS_KEY";
            string browser   = Environment.GetEnvironmentVariable("BROWSER")?.ToLower() ?? "chrome";
            string os        = Environment.GetEnvironmentVariable("PLATFORM") ?? "Windows 11";

            var gridUrl = new Uri($"https://{userName}:{accessKey}@hub.lambdatest.com/wd/hub");

            var ltOptions = new Dictionary<string, object>
            {
                { "build",            "Reqnroll Cloud Build" },
                { "project",          "Reqnroll_Selenium4_Demo" },
                { "w3c",              true },
                { "selenium_version", "4.38.0" },
                { "sessionName",      scenarioName },
                { "platformName",     os }
            };

            DriverOptions options = browser switch
            {
                "firefox" => BuildFirefox(ltOptions),
                "edge"    => BuildEdge(ltOptions),
                _         => BuildChrome(ltOptions)
            };

            var driver = new RemoteWebDriver(gridUrl, options);
            driver.Manage().Timeouts().ImplicitWait = TimeSpan.FromSeconds(10);
            return driver;
        }

        private static ChromeOptions BuildChrome(Dictionary<string, object> lt)
        {
            var o = new ChromeOptions { BrowserVersion = "latest" };
            o.AddAdditionalOption("LT:Options", lt);
            return o;
        }

        private static FirefoxOptions BuildFirefox(Dictionary<string, object> lt)
        {
            var o = new FirefoxOptions { BrowserVersion = "latest" };
            o.AddAdditionalOption("LT:Options", lt);
            return o;
        }

        private static EdgeOptions BuildEdge(Dictionary<string, object> lt)
        {
            var o = new EdgeOptions { BrowserVersion = "latest" };
            o.AddAdditionalOption("LT:Options", lt);
            return o;
        }
    }
}
```

---

## §6 — Parallel Execution

NUnit parallel attributes control concurrency at the assembly level. Declare once in any
`.cs` file in the project (typically the step definitions file):

```csharp
[assembly: Parallelizable(ParallelScope.Fixtures)]
[assembly: LevelOfParallelism(4)]
```

`ParallelScope.Fixtures` runs each `[Binding]` class (scenario group) concurrently.
Each scenario gets its own `ScenarioContext` instance from Reqnroll's DI container,
so `_scenarioContext["driver"]` is always scenario-scoped — no locking required.

Run with:
```bash
dotnet test reqnroll.cloud.sln --logger "console;verbosity=detailed"
```

---

## §7 — Selenium 3 with Reqnroll.Actions (IBrowserInteractions)

`Reqnroll.SpecFlowCompatibility.Actions.LambdaTest` injects `IBrowserInteractions`
automatically. No `DriverFactory` or `Hooks` class needed for basic use.

```csharp
[Binding]
public class SearchStepDefinitions
{
    private readonly IBrowserInteractions _browser;

    public SearchStepDefinitions(IBrowserInteractions browser)
    {
        _browser = browser;
    }

    [BeforeScenario]
    public void SetUp()
    {
        _browser.GoToUrl("https://ecommerce-playground.lambdatest.io/");
    }

    [Given(@"I select the (.*) category")]
    public void GivenISelectTheCategory(string category)
    {
        _browser.WaitAndReturnElement(
            By.XPath("(//div[@class='dropdown search-category']/button)[1]")).Click();
        _browser.WaitAndReturnElement(
            By.XPath($"(//a[text()='{category}'])[1]")).Click();
    }
}
```

### reqnroll.actions.json (browser and cloud config)

```json
{
  "selenium": {
    "disabled": true,
    "defaultTimeout": 60,
    "pollingInterval": 5,
    "lambdatest": {
      "url": "https://${LT_USERNAME}:${LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub"
    }
  }
}
```

Per-browser overrides live in separate files, e.g.
`reqnroll.actions.windows11.chrome.json`:
```json
{
  "selenium": {
    "capabilities": {
      "browserName": "Chrome",
      "browserVersion": "latest",
      "LT:Options": {
        "platformName": "Windows 11",
        "build": "Selenium3 Build",
        "w3c": true
      }
    }
  }
}
```

---

## §8 — Appium 2 DriverFactory (Android)

```csharp
using OpenQA.Selenium.Appium;
using OpenQA.Selenium.Appium.Android;

public static class DriverFactory
{
    public static AndroidDriver CreateCloudAppiumDriver(string scenarioName)
    {
        string userName  = Environment.GetEnvironmentVariable("LT_USERNAME")   ?? "LT_USERNAME";
        string accessKey = Environment.GetEnvironmentVariable("LT_ACCESS_KEY") ?? "LT_ACCESS_KEY";

        var gridUrl = new Uri(
            $"https://{userName}:{accessKey}@mobile-hub.lambdatest.com/wd/hub");

        var ltOptions = new Dictionary<string, object>
        {
            { "build",              "[Appium 2] Reqnroll Demo" },
            { "project",            "Reqnroll_Appium2_Demo" },
            { "w3c",                true },
            { "app",                "proverbial-android" },
            { "platformName",       "android" },
            { "deviceName",         "Galaxy.*" },
            { "platformVersion",    "14" },
            { "isRealMobile",       true },
            { "autoAcceptAlerts",   true },
            { "autoGrantPermissions", true },
            { "sessionName",        scenarioName }
        };

        var options = new AppiumOptions();
        options.AddAdditionalAppiumOption("LT:Options", ltOptions);

        var driver = new AndroidDriver(gridUrl, options);
        driver.Manage().Timeouts().ImplicitWait = TimeSpan.FromSeconds(10);
        return driver;
    }
}
```

---

## §9 — CI/CD Integration (GitHub Actions)

```yaml
name: Reqnroll Tests
on: [push, pull_request]

jobs:
  selenium4-cloud:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
      - name: Restore dependencies
        run: dotnet restore selenium_4/reqnroll.cloud.sln
      - name: Build
        run: dotnet build selenium_4/reqnroll.cloud.sln
      - name: Run tests
        run: dotnet test selenium_4/reqnroll.cloud.sln --logger "console;verbosity=detailed"
        env:
          LT_USERNAME:  ${{ secrets.LT_USERNAME }}
          LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
          EXEC_PLATFORM: cloud

  appium-cloud:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
      - name: Run Appium tests
        run: dotnet test appium/reqnroll.cloud.sln --logger "console;verbosity=detailed"
        env:
          LT_USERNAME:  ${{ secrets.LT_USERNAME }}
          LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
```

---

## §10 — Debugging Quick Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Step not found | Pattern mismatch | Check regex captures; run `dotnet test --list-tests` |
| NullRef on `_driver` | ScenarioContext key wrong | Use exact same key string in `[BeforeScenario]` and step ctor |
| Tests run serially | Missing `Parallelizable` attribute | Add `[assembly: Parallelizable(ParallelScope.Fixtures)]` |
| Cloud session not marked | `lambda-status` not called | Check `EXEC_PLATFORM=cloud` env var in `[AfterScenario]` |
| `IBrowserInteractions` null | Using Selenium 4 with Actions plugin | Actions plugin only supports Selenium 3.141; use `DriverFactory` for Selenium 4 |
| `RemoteWebDriver` connection refused | Wrong grid URL | Verify `LT_USERNAME`/`LT_ACCESS_KEY` env vars are set |
| Appium element not found | Wrong resource-id prefix | Include full package prefix: `com.packagename:id/element_id` |
| App not installed on device | Invalid app alias | Pre-upload app to LambdaTest and use the returned `lt://` URI |
| Parallel race on driver | Static driver field | Replace with `ScenarioContext["driver"]` instance field |
| Feature not discovered | Wrong namespace/assembly | Ensure `[Binding]` attribute on step definition class |
| Scenario title in session name shows blank | `ScenarioInfo.Title` called too early | Access inside `[BeforeScenario]`, not constructor |

---

## §11 — Best Practices Checklist

- Use `ScenarioContext["driver"]` for driver sharing — never static fields in parallel runs
- Declare `[assembly: Parallelizable(ParallelScope.Fixtures)]` at the assembly level once
- Set `LT_USERNAME` and `LT_ACCESS_KEY` from environment — never commit credentials
- Emit `lambda-status=passed/failed` in every `[AfterScenario]` hook when running on cloud
- Use `WebDriverWait` for all element interactions — no unconditional `Thread.Sleep` in web tests
- Use `MobileBy.Id` / `MobileBy.AccessibilityId` before XPath in Appium tests
- Name scenarios descriptively — titles appear as LambdaTest session names
- Tag scenarios with `@tagName` to enable selective test runs in CI
- Always call `driver.Quit()` in `[AfterScenario]` to release cloud device/browser slots
- One `[Binding]` class per feature area keeps step files focused and maintainable
- Use `dotnet test --logger "console;verbosity=detailed"` to see per-scenario results locally
- Structure: `Features/`, `StepDefinitions/`, `Support/` (Hooks, DriverFactory)
