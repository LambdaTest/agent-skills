# Reqnroll — Selenium 3 Patterns (Reqnroll.Actions Plugin)

## Overview

`Reqnroll.SpecFlowCompatibility.Actions.LambdaTest` provides `IBrowserInteractions`,
a high-level abstraction over Selenium that handles driver lifecycle, implicit waits,
and cloud configuration automatically. It is **only compatible with Selenium 3.141**.

Use this approach when migrating from SpecFlow + SpecFlow.Actions.LambdaTest, or when
you prefer plugin-managed driver setup over a manual `DriverFactory`.

---

## Project Structure

```
MyProject/
├── Features/
│   └── search.feature
├── StepDefinitions/
│   └── SearchStepDefinitions.cs
├── reqnroll.actions.json                    # default config
├── reqnroll.actions.windows11.chrome.json  # per-browser capability override
├── reqnroll.cloud.csproj
└── reqnroll.cloud.sln
```

No `Support/Hooks.cs` or `Support/DriverFactory.cs` required — the plugin handles both.

---

## NuGet Packages

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

---

## reqnroll.actions.json

Base configuration file — disables local Selenium, points to LambdaTest:

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

`${LT_USERNAME}` and `${LT_ACCESS_KEY}` are resolved from environment variables at runtime.

---

## Per-Browser Capability Files

The plugin merges capability files matching the pattern
`reqnroll.actions.<os>.<browser>.json`.

### reqnroll.actions.windows11.chrome.json

```json
{
  "selenium": {
    "capabilities": {
      "browserName": "Chrome",
      "browserVersion": "latest",
      "LT:Options": {
        "platformName": "Windows 11",
        "build": "[Selenium 3] Reqnroll Demo",
        "project": "Reqnroll_Selenium3_Demo",
        "w3c": true
      }
    }
  }
}
```

### reqnroll.actions.windows10.firefox.json

```json
{
  "selenium": {
    "capabilities": {
      "browserName": "Firefox",
      "browserVersion": "latest",
      "LT:Options": {
        "platformName": "Windows 10",
        "build": "[Selenium 3] Reqnroll Demo",
        "project": "Reqnroll_Selenium3_Demo",
        "w3c": true
      }
    }
  }
}
```

---

## Step Definitions with IBrowserInteractions

```csharp
using NUnit.Framework;
using OpenQA.Selenium;
using Reqnroll;
using Reqnroll.Actions.Selenium;
using FluentAssertions;

[assembly: Parallelizable(ParallelScope.Fixtures)]
[assembly: LevelOfParallelism(4)]

namespace MyProject.StepDefinitions
{
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
                By.XPath("(//div[@class='dropdown search-category']/button[@type='button'])[1]")
            ).Click();
            _browser.WaitAndReturnElement(
                By.XPath($"(//a[text()='{category}'])[1]")
            ).Click();
        }

        [When(@"I search for (.*)")]
        public void WhenISearchFor(string product)
        {
            _browser.WaitAndReturnElement(
                By.XPath("(//input[@name='search'])[1]")
            ).SendKeys(product);
            _browser.WaitAndReturnElement(
                By.XPath("(//button[normalize-space()='Search'])[1]")
            ).Click();
        }

        [Then(@"I should get (.*) results for (.*)")]
        public void ThenIShouldGetResults(int expected, string product)
        {
            int actual = _browser.WaitAndReturnElements(
                By.XPath(
                    $"//div[@class='row']//div[@class='carousel-item active']/img[@alt='{product}']")
            ).Count();
            Assert.That(actual, Is.EqualTo(expected));
        }
    }
}
```

### IBrowserInteractions key methods

| Method | Description |
|--------|-------------|
| `GoToUrl(string url)` | Navigate to URL |
| `WaitAndReturnElement(By locator)` | Wait and return first matching element |
| `WaitAndReturnElements(By locator)` | Wait and return all matching elements |
| `GetUrl()` | Return current page URL |
| `GetTitle()` | Return current page title |

---

## Migrating from SpecFlow to Reqnroll

The namespace swap is the primary change required:

| SpecFlow | Reqnroll |
|----------|----------|
| `using TechTalk.SpecFlow;` | `using Reqnroll;` |
| `using SpecFlow.Actions.Selenium;` | `using Reqnroll.Actions.Selenium;` |
| `SpecFlow.Actions.LambdaTest` NuGet | `Reqnroll.SpecFlowCompatibility.Actions.LambdaTest` NuGet |

Step definitions, feature files, and `[Binding]` / `[BeforeScenario]` / `[AfterScenario]`
attributes remain identical.
