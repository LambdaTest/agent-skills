# C# Patterns — Playwright

## Table of Contents
- Setup (.NET)
- NUnit Integration
- MSTest Integration
- POM in C#
- Cloud Integration (C#)

## Setup (.NET)

```bash
dotnet new nunit -n PlaywrightTests
cd PlaywrightTests
dotnet add package Microsoft.Playwright
dotnet add package Microsoft.Playwright.NUnit
dotnet build
pwsh bin/Debug/net8.0/playwright.ps1 install
```

## NUnit Integration (Recommended)

```csharp
// Tests/LoginTests.cs
using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;

[Parallelizable(ParallelScope.Self)]
[TestFixture]
public class LoginTests : PageTest
{
    [SetUp]
    public async Task Setup()
    {
        await Page.GotoAsync("http://localhost:3000/login");
    }

    [Test]
    public async Task ShouldLoginSuccessfully()
    {
        await Page.GetByLabel("Email").FillAsync("user@example.com");
        await Page.GetByLabel("Password").FillAsync("password123");
        await Page.GetByRole(AriaRole.Button, new() { Name = "Sign in" }).ClickAsync();
        await Expect(Page.GetByRole(AriaRole.Heading)).ToContainTextAsync("Dashboard");
    }

    [Test]
    public async Task ShouldShowErrorOnInvalidCredentials()
    {
        await Page.GetByLabel("Email").FillAsync("bad@example.com");
        await Page.GetByLabel("Password").FillAsync("wrong");
        await Page.GetByRole(AriaRole.Button, new() { Name = "Sign in" }).ClickAsync();
        await Expect(Page.GetByRole(AriaRole.Alert)).ToHaveTextAsync("Invalid credentials");
    }
}
```

### .runsettings

```xml
<?xml version="1.0" encoding="utf-8"?>
<RunSettings>
  <Playwright>
    <BrowserName>chromium</BrowserName>
    <LaunchOptions>
      <Headless>false</Headless>
    </LaunchOptions>
  </Playwright>
</RunSettings>
```

Run: `dotnet test --settings .runsettings`

## MSTest Integration

```csharp
using Microsoft.Playwright;
using Microsoft.Playwright.MSTest;

[TestClass]
public class LoginTests : PageTest
{
    [TestMethod]
    public async Task ShouldLoginSuccessfully()
    {
        await Page.GotoAsync("http://localhost:3000/login");
        await Page.GetByLabel("Email").FillAsync("user@example.com");
        await Page.GetByLabel("Password").FillAsync("password123");
        await Page.GetByRole(AriaRole.Button, new() { Name = "Sign in" }).ClickAsync();
        await Expect(Page.GetByRole(AriaRole.Heading)).ToContainTextAsync("Dashboard");
    }
}
```

## POM in C#

```csharp
// Pages/LoginPage.cs
using Microsoft.Playwright;

public class LoginPage
{
    private readonly IPage _page;
    public ILocator EmailInput => _page.GetByLabel("Email");
    public ILocator PasswordInput => _page.GetByLabel("Password");
    public ILocator SubmitButton => _page.GetByRole(AriaRole.Button, new() { Name = "Sign in" });
    public ILocator ErrorMessage => _page.GetByRole(AriaRole.Alert);

    public LoginPage(IPage page) => _page = page;

    public async Task GotoAsync() => await _page.GotoAsync("/login");

    public async Task LoginAsync(string email, string password)
    {
        await EmailInput.FillAsync(email);
        await PasswordInput.FillAsync(password);
        await SubmitButton.ClickAsync();
    }
}
```

## Cloud Integration (C#)

```csharp
using System.Text.Json;
using System.Web;
using Microsoft.Playwright;

var capabilities = new Dictionary<string, object>
{
    ["browserName"] = "Chrome",
    ["browserVersion"] = "latest",
    ["LT:Options"] = new Dictionary<string, object>
    {
        ["platform"] = "Windows 11",
        ["build"] = "C# Build",
        ["name"] = "C# Test",
        ["user"] = Environment.GetEnvironmentVariable("LT_USERNAME")!,
        ["accessKey"] = Environment.GetEnvironmentVariable("LT_ACCESS_KEY")!,
        ["network"] = true,
        ["video"] = true,
    }
};

var capsJson = JsonSerializer.Serialize(capabilities);
var encoded = HttpUtility.UrlEncode(capsJson);
var wsEndpoint = $"wss://cdp.lambdatest.com/playwright?capabilities={encoded}";

using var playwright = await Playwright.CreateAsync();
var browser = await playwright.Chromium.ConnectAsync(wsEndpoint);
var page = await (await browser.NewContextAsync()).NewPageAsync();

try
{
    await page.GotoAsync("https://example.com");
    // test logic...
    await SetTestStatusAsync(page, "passed", "OK");
}
catch (Exception ex)
{
    await SetTestStatusAsync(page, "failed", ex.Message);
    throw;
}
finally
{
    await browser.CloseAsync();
}

static async Task SetTestStatusAsync(IPage page, string status, string remark)
{
    var action = JsonSerializer.Serialize(new
    {
        action = "setTestStatus",
        arguments = new { status, remark }
    });
    await page.EvaluateAsync("_ => {}", $"lambdatest_action: {action}");
}
```
