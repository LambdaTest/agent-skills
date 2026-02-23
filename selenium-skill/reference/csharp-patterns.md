# Selenium — C# Patterns

## Setup

```xml
<!-- .csproj -->
<PackageReference Include="Selenium.WebDriver" Version="4.*" />
<PackageReference Include="Selenium.Support" Version="4.*" />
<PackageReference Include="NUnit" Version="4.*" />
<PackageReference Include="NUnit3TestAdapter" Version="4.*" />
```

## Basic Test (NUnit)

```csharp
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using OpenQA.Selenium.Support.UI;
using NUnit.Framework;

[TestFixture]
public class LoginTests
{
    private IWebDriver driver;
    private WebDriverWait wait;

    [SetUp]
    public void SetUp()
    {
        driver = new ChromeDriver();
        wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
        driver.Manage().Window.Maximize();
    }

    [Test]
    public void TestLogin()
    {
        driver.Navigate().GoToUrl("https://example.com/login");
        wait.Until(d => d.FindElement(By.Id("username"))).SendKeys("user@test.com");
        driver.FindElement(By.Id("password")).SendKeys("password123");
        driver.FindElement(By.CssSelector("button[type='submit']")).Click();
        wait.Until(d => d.Url.Contains("/dashboard"));
        Assert.That(driver.Title, Does.Contain("Dashboard"));
    }

    [TearDown]
    public void TearDown()
    {
        driver?.Quit();
    }
}
```

## TestMu AI Cloud (C#)

```csharp
var options = new ChromeOptions();
var ltOptions = new Dictionary<string, object>
{
    { "platform", "Windows 11" },
    { "build", "C# Build" },
    { "name", "C# Test" },
    { "user", Environment.GetEnvironmentVariable("LT_USERNAME") },
    { "accessKey", Environment.GetEnvironmentVariable("LT_ACCESS_KEY") },
    { "video", true },
    { "network", true }
};
options.AddAdditionalOption("LT:Options", ltOptions);
driver = new RemoteWebDriver(
    new Uri("https://hub.lambdatest.com/wd/hub"), options);
```
