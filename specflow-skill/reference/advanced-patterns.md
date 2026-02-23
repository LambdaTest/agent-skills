# SpecFlow (.NET BDD) — Advanced Patterns & Playbook

## Step Definitions with DI

```csharp
[Binding]
public class UserSteps
{
    private readonly ScenarioContext _ctx;
    private readonly IUserService _service;
    private readonly IWebDriver _driver;

    public UserSteps(ScenarioContext ctx, IUserService service, WebDriverContext driverCtx)
    {
        _ctx = ctx;
        _service = service;
        _driver = driverCtx.Driver;
    }

    [Given(@"a user named ""(.*)""")]
    public void GivenUserNamed(string name)
    {
        var user = _service.Create(name, $"{name.ToLower()}@test.com");
        _ctx.Set(user, "currentUser");
    }

    [When(@"I navigate to the (.*) page")]
    public void WhenNavigate(string page)
    {
        _driver.Navigate().GoToUrl($"{Config.BaseUrl}/{page}");
    }

    [Then(@"I should see ""(.*)""")]
    public void ThenShouldSee(string text)
    {
        Assert.That(_driver.PageSource, Does.Contain(text));
    }
}
```

## Table Arguments & Transforms

```gherkin
Scenario: Create multiple users
  Given the following users exist:
    | Name    | Email            | Role   |
    | Alice   | alice@test.com   | admin  |
    | Bob     | bob@test.com     | user   |
  When I query all users
  Then I should find 2 users
```

```csharp
[Given(@"the following users exist:")]
public void GivenUsersExist(Table table)
{
    var users = table.CreateSet<UserDto>();
    foreach (var u in users) _service.Create(u);
}

// StepArgumentTransformation
[StepArgumentTransformation]
public UserDto TransformUser(Table table) => table.CreateInstance<UserDto>();

[StepArgumentTransformation(@"(\d+) days? ago")]
public DateTime DaysAgo(int days) => DateTime.Now.AddDays(-days);
```

## Hooks

```csharp
[Binding]
public class Hooks
{
    [BeforeScenario("@ui")]
    public void SetupBrowser(WebDriverContext ctx) { ctx.Init(); }

    [AfterScenario("@ui")]
    public void TakeScreenshotOnFail(ScenarioContext ctx, WebDriverContext driver)
    {
        if (ctx.TestError != null)
        {
            var ss = ((ITakesScreenshot)driver.Driver).GetScreenshot();
            ss.SaveAsFile($"screenshots/{ctx.ScenarioInfo.Title}.png");
        }
        driver.Dispose();
    }

    [BeforeTestRun]
    public static void GlobalSetup() { Database.Migrate(); }
}
```

## Anti-Patterns

- ❌ Step definitions referencing UI elements directly — use Page Objects
- ❌ `ScenarioContext` as a dumping ground — use typed context classes
- ❌ Long Gherkin scenarios (>10 steps) — break into focused scenarios
- ❌ Missing `[AfterScenario]` cleanup — resource leaks in parallel execution
