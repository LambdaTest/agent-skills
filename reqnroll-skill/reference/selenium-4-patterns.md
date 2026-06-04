# Reqnroll — Selenium 4 Patterns

## Overview

Selenium 4 with Reqnroll uses a manual `DriverFactory` + `ScenarioContext` pattern.
The Actions plugin (`Reqnroll.SpecFlowCompatibility.Actions.LambdaTest`) is **not**
compatible with Selenium 4; use this approach instead.

---

## Project Structure

```
MyProject/
├── Features/
│   ├── search.feature
│   └── checkout.feature
├── StepDefinitions/
│   └── SearchStepDefinitions.cs
├── Support/
│   ├── DriverFactory.cs
│   └── Hooks.cs
├── reqnroll.cloud.csproj
└── reqnroll.cloud.sln
```

---

## DriverFactory

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
        public static IWebDriver CreateDriver(string scenarioName) =>
            CreateCloudDriver(scenarioName);

        private static IWebDriver CreateCloudDriver(string scenarioName)
        {
            string userName  = Environment.GetEnvironmentVariable("LT_USERNAME")   ?? "LT_USERNAME";
            string accessKey = Environment.GetEnvironmentVariable("LT_ACCESS_KEY") ?? "LT_ACCESS_KEY";
            string browser   = Environment.GetEnvironmentVariable("BROWSER")?.ToLower() ?? "chrome";
            string os        = Environment.GetEnvironmentVariable("PLATFORM") ?? "Windows 11";

            var ltOptions = new Dictionary<string, object>
            {
                { "build",            "[Selenium 4] Reqnroll Demo" },
                { "project",          "Reqnroll_Selenium4_Demo" },
                { "w3c",              true },
                { "selenium_version", "4.38.0" },
                { "sessionName",      scenarioName },
                { "platformName",     os }
            };

            var gridUrl = new Uri($"https://{userName}:{accessKey}@hub.lambdatest.com/wd/hub");

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

## Hooks

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

---

## Step Definitions

```csharp
using NUnit.Framework;
using OpenQA.Selenium;
using OpenQA.Selenium.Support.UI;
using Reqnroll;

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
            WaitAndFind(
                By.XPath("(//div[@class='dropdown search-category']/button[@type='button'])[1]")
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
                By.XPath(
                    $"//div[@class='row']//div[@class='carousel-item active']/img[@alt='{product}']")
            ).Count;
            Assert.That(actual, Is.EqualTo(expected));
        }
    }
}
```

---

## Screenshot on Failure

Add to `[AfterScenario]` in Hooks:

```csharp
[AfterScenario]
public void TearDown()
{
    if (_scenarioContext.TryGetValue("driver", out IWebDriver driver))
    {
        if (_scenarioContext.TestError != null)
        {
            var screenshot = ((ITakesScreenshot)driver).GetScreenshot();
            string path = Path.Combine("screenshots", $"{_scenarioContext.ScenarioInfo.Title}.png");
            Directory.CreateDirectory("screenshots");
            screenshot.SaveAsFile(path);
        }
        driver.Quit();
    }
}
```

---

## Multiple Feature Files + Parallel Execution

With `ParallelScope.Fixtures`, each `[Binding]` class runs in its own thread. Each
scenario in each feature file gets an isolated `ScenarioContext`, so multiple features
execute concurrently without shared state conflicts.

```
Feature file 1 (Scenario A, B) ──► Thread 1
Feature file 2 (Scenario C, D) ──► Thread 2
Feature file 3 (Scenario E)    ──► Thread 3
Feature file 4 (Scenario F, G) ──► Thread 4
```

Set `LevelOfParallelism` to the number of parallel cloud browser sessions available
on your LambdaTest plan.
