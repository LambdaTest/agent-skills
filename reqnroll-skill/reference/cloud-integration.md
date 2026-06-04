# Reqnroll — Cloud Integration (TestMu AI / LambdaTest)

## Authentication

Set environment variables before running tests:

```bash
export LT_USERNAME=<your-username>
export LT_ACCESS_KEY=<your-access-key>
```

Credentials are available at https://accounts.lambdatest.com/security.

Read in C# with a safe fallback for local development:
```csharp
string userName  = Environment.GetEnvironmentVariable("LT_USERNAME")   ?? "LT_USERNAME";
string accessKey = Environment.GetEnvironmentVariable("LT_ACCESS_KEY") ?? "LT_ACCESS_KEY";
```

---

## Grid Endpoints

| Target | URL |
|--------|-----|
| Web (Selenium) | `https://{user}:{key}@hub.lambdatest.com/wd/hub` |
| Mobile (Appium) | `https://{user}:{key}@mobile-hub.lambdatest.com/wd/hub` |

---

## LT:Options — Web (Selenium 4)

```csharp
var ltOptions = new Dictionary<string, object>
{
    { "build",            "Build name shown in dashboard" },
    { "project",          "Project name for grouping" },
    { "w3c",              true },
    { "selenium_version", "4.38.0" },
    { "sessionName",      scenarioName },          // per-test session label
    { "platformName",     "Windows 11" },
    { "video",            true },                  // record video (optional)
    { "network",          true },                  // capture network logs (optional)
    { "console",          true },                  // capture browser console (optional)
    { "visual",           true },                  // capture screenshots (optional)
};
var options = new ChromeOptions();
options.BrowserVersion = "latest";
options.AddAdditionalOption("LT:Options", ltOptions);
```

### Supported platformName values
`Windows 11`, `Windows 10`, `macOS Ventura`, `macOS Monterey`, `macOS Big Sur`

### Supported browserVersion values
`latest`, `latest-1`, `latest-2`, or a specific version number (e.g. `"120.0"`)

---

## LT:Options — Mobile (Appium 2)

```csharp
var ltOptions = new Dictionary<string, object>
{
    { "build",                "Build name" },
    { "project",              "Project name" },
    { "w3c",                  true },
    { "app",                  "lt://APP_ID" },           // from LambdaTest App Upload API
    { "platformName",         "android" },               // or "ios"
    { "deviceName",           "Galaxy S23" },            // regex supported: "Galaxy.*"
    { "platformVersion",      "14" },
    { "isRealMobile",         true },
    { "autoAcceptAlerts",     true },
    { "autoGrantPermissions", true },
    { "sessionName",          scenarioName },
    { "video",                true },
    { "devicelog",            true },
    { "network",              true },
};
var options = new AppiumOptions();
options.AddAdditionalAppiumOption("LT:Options", ltOptions);
```

---

## App Upload (Appium)

Upload your APK/IPA to LambdaTest before the test run to get an `lt://` URI:

```bash
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
     -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
     -F "appFile=@/path/to/app.apk" \
     -F "name=MyApp"
```

Response:
```json
{ "app_url": "lt://APP12345678" }
```

Use `lt://APP12345678` as the `"app"` value in `LT:Options`, or register a named alias
(e.g. `"proverbial-android"`) via the LambdaTest dashboard.

---

## Reporting Pass / Fail

LambdaTest requires an explicit status update via JavaScript executor — it cannot infer
pass/fail from driver.Quit() alone.

### Selenium 4

```csharp
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
```

### Appium

```csharp
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
```

---

## Build and Session Naming

Consistent build names allow filtering history in the LambdaTest dashboard:

```csharp
{ "build",       $"[Selenium 4] {Environment.GetEnvironmentVariable("BUILD_NUMBER") ?? "local"}" },
{ "sessionName", scenarioName }   // ScenarioContext.ScenarioInfo.Title
```

`sessionName` maps each Reqnroll scenario to an individual session entry in the dashboard,
making it easy to correlate logs, screenshots, and videos to a specific test.

---

## LambdaTest Tunnel (testing localhost / staging environments)

Start the tunnel binary before the test run:

```bash
./LambdaTestTunnel --user $LT_USERNAME --key $LT_ACCESS_KEY --tunnelName myTunnel
```

Add to `LT:Options`:
```csharp
{ "tunnel",     true },
{ "tunnelName", "myTunnel" }
```

---

## Makefile Targets

```makefile
DOTNET         := dotnet
REQNROLL_PROJECT := reqnroll.cloud.sln

build:
    $(DOTNET) build $(REQNROLL_PROJECT)

reqnroll-automation-test:
    $(DOTNET) test $(REQNROLL_PROJECT) --logger "console;verbosity=detailed"
```

```bash
# Set credentials, then:
make build
make reqnroll-automation-test
```
