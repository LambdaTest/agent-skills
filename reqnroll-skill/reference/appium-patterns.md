# Reqnroll — Appium 2 Patterns (Android / iOS)

## Overview

Reqnroll + Appium 2 uses the same `[Binding]` / `ScenarioContext` / hooks pattern as
the Selenium 4 path, swapping `IWebDriver` for `AppiumDriver` / `AndroidDriver` and
`RemoteWebDriver` for the Appium-specific driver class. Cloud target is
`mobile-hub.lambdatest.com`.

---

## Project Structure

```
appium/
├── Features/
│   └── proverbial-ops.feature
├── StepDefinitions/
│   └── ProverbialActionsStepDefinitions.cs
├── Support/
│   ├── DriverFactory.cs
│   └── Hooks.cs
├── reqnroll.cloud.csproj
└── reqnroll.cloud.sln
```

---

## NuGet Packages

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.NET.Test.Sdk"           Version="18.0.1" />
  <PackageReference Include="Selenium.WebDriver"               Version="4.38.0" />
  <PackageReference Include="Selenium.Support"                 Version="4.38.0" />
  <PackageReference Include="Appium.WebDriver"                 Version="8.2.0" />
  <PackageReference Include="DotNetSeleniumExtras.WaitHelpers" Version="3.11.0" />
  <PackageReference Include="Reqnroll.NUnit"                   Version="3.3.4" />
  <PackageReference Include="nunit"                            Version="4.5.1" />
  <PackageReference Include="NUnit3TestAdapter"                Version="6.2.0" />
  <PackageReference Include="FluentAssertions"                 Version="8.8.0" />
</ItemGroup>
```

---

## DriverFactory (Android)

```csharp
using OpenQA.Selenium.Appium;
using OpenQA.Selenium.Appium.Android;

namespace appium.Support
{
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
                { "build",                "[Appium 2] Reqnroll Demo" },
                { "project",              "Reqnroll_Appium2_Demo" },
                { "w3c",                  true },
                { "app",                  "proverbial-android" },
                { "platformName",         "android" },
                { "deviceName",           "Galaxy.*" },
                { "platformVersion",      "14" },
                { "isRealMobile",         true },
                { "autoAcceptAlerts",     true },
                { "autoGrantPermissions", true },
                { "sessionName",          scenarioName }
            };

            var options = new AppiumOptions();
            options.AddAdditionalAppiumOption("LT:Options", ltOptions);

            var driver = new AndroidDriver(gridUrl, options);
            driver.Manage().Timeouts().ImplicitWait = TimeSpan.FromSeconds(10);
            return driver;
        }
    }
}
```

---

## Hooks

```csharp
using NUnit.Framework;
using NUnit.Framework.Interfaces;
using OpenQA.Selenium;
using OpenQA.Selenium.Appium.Android;
using Reqnroll;

namespace appium.Support
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

## Feature File

```gherkin
Feature: [Appium 2] Perform actions in Proverbial App

@operations
Scenario: @F1: Validate all UI actions in the Proverbial App
    When I toggle the text color
    And I change the text using the text button
    And I trigger the toast message
    And I tap the notification button
    And I open the geolocation screen
    And I return back to the home screen
    And I open the speed test screen
    And I return back to the home screen
    And I open the in-app browser
    And I enter the url "https://www.lambdatest.com"
    Then the url should be entered successfully
```

---

## Step Definitions

```csharp
using NUnit.Framework;
using OpenQA.Selenium;
using OpenQA.Selenium.Appium;
using OpenQA.Selenium.Appium.Android;
using OpenQA.Selenium.Support.UI;
using Reqnroll;
using SeleniumExtras.WaitHelpers;

namespace appium.StepDefinitions
{
    [Binding]
    public class ProverbialActionsStepDefinitions
    {
        private readonly AppiumDriver _driver;

        public ProverbialActionsStepDefinitions(ScenarioContext scenarioContext)
        {
            _driver = scenarioContext["driver"] as AppiumDriver;
        }

        private IWebElement WaitAndFind(By locator) =>
            new WebDriverWait(_driver, TimeSpan.FromSeconds(10))
                .Until(d => d.FindElement(locator));

        private IWebElement WaitAndClick(By locator, int timeout = 20)
        {
            var element = (IWebElement)new WebDriverWait(_driver, TimeSpan.FromSeconds(timeout))
                .Until(ExpectedConditions.ElementToBeClickable(locator));
            Thread.Sleep(800);
            element.Click();
            return element;
        }

        [When(@"I toggle the text color")]
        public void WhenIToggleTheTextColor()
        {
            var colorButton = WaitAndClick(MobileBy.Id("color"));
            Thread.Sleep(600);
            colorButton.Click();
        }

        [When(@"I change the text using the text button")]
        public void WhenIChangeTheTextUsingTheTextButton()
        {
            WaitAndClick(MobileBy.Id("Text"));
        }

        [When(@"I trigger the toast message")]
        public void WhenITriggerTheToastMessage()
        {
            WaitAndClick(MobileBy.Id("toast"));
        }

        [When(@"I tap the notification button")]
        public void WhenITapTheNotificationButton()
        {
            WaitAndClick(MobileBy.Id("notification"));
            Thread.Sleep(1500);
        }

        [When(@"I open the geolocation screen")]
        public void WhenIOpenTheGeolocationScreen()
        {
            WaitAndClick(MobileBy.Id("geoLocation"));
            Thread.Sleep(3000);
        }

        [When(@"I return back to the home screen")]
        public void WhenIReturnBackToTheHomeScreen()
        {
            // KEYCODE_BACK (0x4) via lambda-adb executor
            _driver.ExecuteScript("lambda-adb", new Dictionary<string, object>
            {
                { "command", "keyevent" },
                { "keycode", 0x4 }
            });
            Thread.Sleep(800);
        }

        [When(@"I open the speed test screen")]
        public void WhenIOpenTheSpeedTestScreen()
        {
            WaitAndClick(MobileBy.Id("speedTest"));
            Thread.Sleep(4000);
        }

        [When(@"I open the in-app browser")]
        public void WhenIOpenTheInAppBrowser()
        {
            WaitAndClick(
                MobileBy.XPath(
                    "//android.widget.FrameLayout[@content-desc='Browser']" +
                    "/android.widget.FrameLayout/android.widget.ImageView"),
                timeout: 30);
        }

        [When(@"I enter the url ""(.*)""")]
        public void WhenIEnterTheUrl(string urlText)
        {
            var urlField = WaitAndClick(MobileBy.Id("url"));
            urlField.SendKeys(urlText);
            Thread.Sleep(800);
            WaitAndClick(MobileBy.XPath("//*[@resource-id='com.lambdatest.proverbial:id/find']"))
                .Click();
            Thread.Sleep(10000);
        }

        [Then(@"the url should be entered successfully")]
        public void ThenTheUrlShouldBeEnteredSuccessfully()
        {
            Console.WriteLine("URL entry verified");
        }
    }
}
```

---

## Locator Strategy

| Priority | Locator | Example |
|----------|---------|---------|
| 1 | `MobileBy.AccessibilityId` | `MobileBy.AccessibilityId("login_button")` |
| 2 | `MobileBy.Id` (resource-id) | `MobileBy.Id("com.pkg:id/btn")` or short form `MobileBy.Id("btn")` |
| 3 | `MobileBy.AndroidUIAutomator` | `MobileBy.AndroidUIAutomator("new UiSelector().text(\"Login\")")` |
| 4 | `MobileBy.XPath` | Use sparingly; 10x slower than id/accessibilityId |

---

## LambdaTest ADB Execution

Send ADB key events via `lambda-adb` executor without shell access:

```csharp
_driver.ExecuteScript("lambda-adb", new Dictionary<string, object>
{
    { "command", "keyevent" },
    { "keycode", 0x4 }   // KEYCODE_BACK
});
```

Common keycodes:
| Key | Code |
|-----|------|
| Back | `0x4` |
| Home | `0x3` |
| Enter | `0x42` |
| Menu | `0x52` |

---

## iOS Support

For iOS, replace `AndroidDriver` with `IOSDriver` and adjust `LT:Options`:

```csharp
var ltOptions = new Dictionary<string, object>
{
    { "app",             "lt://YOUR_IOS_APP_ID" },
    { "platformName",    "ios" },
    { "deviceName",      "iPhone 15" },
    { "platformVersion", "17" },
    { "isRealMobile",    true },
    { "autoAcceptAlerts", true },
    { "sessionName",     scenarioName }
};
var options = new AppiumOptions();
options.AddAdditionalAppiumOption("LT:Options", ltOptions);
var driver = new IOSDriver(gridUrl, options);
```

iOS locators use `MobileBy.IosNSPredicate` or `MobileBy.AccessibilityId`:
```csharp
MobileBy.IosNSPredicate("type == 'XCUIElementTypeButton' AND label == 'Login'")
MobileBy.AccessibilityId("login_button")
```
