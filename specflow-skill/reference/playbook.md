# SpecFlow — Advanced Playbook

## §1 — Project Setup

### .csproj Configuration
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="SpecFlow" Version="3.9.74" />
    <PackageReference Include="SpecFlow.NUnit" Version="3.9.74" />
    <PackageReference Include="SpecFlow.Plus.LivingDocPlugin" Version="3.9.57" />
    <PackageReference Include="NUnit" Version="4.1.0" />
    <PackageReference Include="NUnit3TestAdapter" Version="4.5.0" />
    <PackageReference Include="Selenium.WebDriver" Version="4.18.1" />
    <PackageReference Include="Selenium.Support" Version="4.18.1" />
    <PackageReference Include="WebDriverManager" Version="2.17.2" />
    <PackageReference Include="FluentAssertions" Version="6.12.0" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.9.0" />
  </ItemGroup>
</Project>
```

### Project Structure
```
SpecFlowProject/
├── Features/
│   ├── Login.feature
│   ├── Search.feature
│   └── Checkout.feature
├── StepDefinitions/
│   ├── LoginSteps.cs
│   ├── SearchSteps.cs
│   └── SharedSteps.cs
├── Pages/
│   ├── BasePage.cs
│   ├── LoginPage.cs
│   ├── DashboardPage.cs
│   └── SearchPage.cs
├── Hooks/
│   ├── WebDriverHooks.cs
│   └── ReportingHooks.cs
├── Drivers/
│   ├── DriverFactory.cs
│   └── LambdaTestDriver.cs
├── Support/
│   ├── TestConfig.cs
│   └── TestDataHelper.cs
└── specflow.json
```

### specflow.json
```json
{
  "language": {
    "feature": "en"
  },
  "bindingCulture": {
    "name": "en-US"
  },
  "generator": {
    "addNonParallelizableMarkerForTags": ["sequential"]
  },
  "stepAssemblies": [
    { "assembly": "SpecFlowProject" }
  ]
}
```

---

## §2 — Feature Files

### Login Feature
```gherkin
@login
Feature: User Authentication
  As a registered user
  I want to log into the application
  So that I can access protected features

  Background:
    Given I am on the login page

  @smoke @critical
  Scenario: Successful login with valid credentials
    When I enter email "admin@test.com"
    And I enter password "password123"
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see a welcome message containing "Admin"

  @negative
  Scenario Outline: Login with invalid credentials
    When I enter email "<email>"
    And I enter password "<password>"
    And I click the login button
    Then I should see an error message "<error>"

    Examples:
      | email            | password | error               |
      | wrong@test.com   | bad      | Invalid credentials |
      | admin@test.com   | wrong    | Invalid credentials |
      |                  |          | Email is required   |

  @security
  Scenario: Account lockout after failed attempts
    When I attempt to login 5 times with wrong credentials
    Then the account should be locked
    And I should see "Account locked. Try again in 15 minutes."
```

### Search Feature with Data Tables
```gherkin
@search
Feature: Product Search
  As a customer
  I want to search for products
  So that I can find what I need

  @smoke
  Scenario: Search returns matching products
    Given I am on the search page
    When I search for "laptop"
    Then I should see at least 1 result
    And the first result should contain "laptop"

  Scenario: Filter search results
    Given I am on the search page
    And I search for "shoes"
    When I apply the following filters:
      | Filter   | Value     |
      | Brand    | Nike      |
      | Size     | 10        |
      | Color    | Black     |
      | PriceMax | 150       |
    Then all results should match the applied filters

  Scenario: Compare multiple products
    Given I am on the search page
    And I search for "phone"
    When I add the following products to comparison:
      | Product     |
      | iPhone 15   |
      | Galaxy S24  |
      | Pixel 8     |
    Then the comparison table should show 3 products
    And each product should display price, rating, and specs
```

---

## §3 — Step Definitions

### Login Steps
```csharp
[Binding]
public class LoginSteps
{
    private readonly ScenarioContext _scenarioContext;
    private readonly LoginPage _loginPage;
    private readonly DashboardPage _dashboardPage;

    public LoginSteps(ScenarioContext scenarioContext, LoginPage loginPage, DashboardPage dashboardPage)
    {
        _scenarioContext = scenarioContext;
        _loginPage = loginPage;
        _dashboardPage = dashboardPage;
    }

    [Given(@"I am on the login page")]
    public void GivenIAmOnTheLoginPage()
    {
        _loginPage.NavigateTo();
        _loginPage.WaitForPageLoad();
    }

    [When(@"I enter email ""(.*)""")]
    public void WhenIEnterEmail(string email)
    {
        _loginPage.EnterEmail(email);
    }

    [When(@"I enter password ""(.*)""")]
    public void WhenIEnterPassword(string password)
    {
        _loginPage.EnterPassword(password);
    }

    [When(@"I click the login button")]
    public void WhenIClickTheLoginButton()
    {
        _loginPage.ClickLogin();
    }

    [Then(@"I should be redirected to the dashboard")]
    public void ThenIShouldBeRedirectedToDashboard()
    {
        _dashboardPage.WaitForPageLoad();
        _dashboardPage.IsDisplayed().Should().BeTrue();
    }

    [Then(@"I should see a welcome message containing ""(.*)""")]
    public void ThenWelcomeMessageContaining(string expected)
    {
        _dashboardPage.GetWelcomeMessage().Should().Contain(expected);
    }

    [Then(@"I should see an error message ""(.*)""")]
    public void ThenIShouldSeeAnErrorMessage(string expected)
    {
        _loginPage.GetErrorMessage().Should().Contain(expected);
    }

    [When(@"I attempt to login (\d+) times with wrong credentials")]
    public void WhenIAttemptToLoginMultipleTimes(int times)
    {
        for (int i = 0; i < times; i++)
        {
            _loginPage.EnterEmail("wrong@test.com");
            _loginPage.EnterPassword("wrongpassword");
            _loginPage.ClickLogin();
        }
    }

    [Then(@"the account should be locked")]
    public void ThenTheAccountShouldBeLocked()
    {
        _loginPage.IsAccountLocked().Should().BeTrue();
    }
}
```

### Search Steps with Table Arguments
```csharp
[Binding]
public class SearchSteps
{
    private readonly SearchPage _searchPage;

    public SearchSteps(SearchPage searchPage)
    {
        _searchPage = searchPage;
    }

    [Given(@"I am on the search page")]
    public void GivenIAmOnTheSearchPage()
    {
        _searchPage.NavigateTo();
    }

    [When(@"I search for ""(.*)""")]
    [Given(@"I search for ""(.*)""")]
    public void WhenISearchFor(string query)
    {
        _searchPage.Search(query);
    }

    [When(@"I apply the following filters:")]
    public void WhenIApplyFilters(Table table)
    {
        foreach (var row in table.Rows)
        {
            _searchPage.ApplyFilter(row["Filter"], row["Value"]);
        }
        _searchPage.WaitForResults();
    }

    [When(@"I add the following products to comparison:")]
    public void WhenIAddProductsToComparison(Table table)
    {
        foreach (var row in table.Rows)
        {
            _searchPage.AddToComparison(row["Product"]);
        }
    }

    [Then(@"I should see at least (\d+) result")]
    public void ThenIShouldSeeResults(int minCount)
    {
        _searchPage.GetResultCount().Should().BeGreaterThanOrEqualTo(minCount);
    }

    [Then(@"the first result should contain ""(.*)""")]
    public void ThenFirstResultContains(string expected)
    {
        _searchPage.GetFirstResultTitle().Should()
            .ContainEquivalentOf(expected);
    }

    [Then(@"all results should match the applied filters")]
    public void ThenAllResultsMatchFilters()
    {
        _searchPage.AreAllResultsFiltered().Should().BeTrue();
    }

    [Then(@"the comparison table should show (\d+) products")]
    public void ThenComparisonTableShows(int count)
    {
        _searchPage.GetComparisonCount().Should().Be(count);
    }
}
```

---

## §4 — Page Objects

### BasePage
```csharp
public abstract class BasePage
{
    protected readonly IWebDriver Driver;
    protected readonly WebDriverWait Wait;

    protected BasePage(IWebDriver driver)
    {
        Driver = driver;
        Wait = new WebDriverWait(driver, TimeSpan.FromSeconds(10));
    }

    protected abstract string PageUrl { get; }
    protected abstract By PageIdentifier { get; }

    public void NavigateTo()
    {
        var baseUrl = TestConfig.BaseUrl;
        Driver.Navigate().GoToUrl($"{baseUrl}{PageUrl}");
    }

    public void WaitForPageLoad()
    {
        Wait.Until(d => d.FindElement(PageIdentifier).Displayed);
    }

    public bool IsDisplayed()
    {
        try { return Driver.FindElement(PageIdentifier).Displayed; }
        catch (NoSuchElementException) { return false; }
    }

    protected IWebElement FindElement(By by) =>
        Wait.Until(d => d.FindElement(by));

    protected IReadOnlyCollection<IWebElement> FindElements(By by) =>
        Driver.FindElements(by);

    protected void ClearAndType(By by, string text)
    {
        var element = FindElement(by);
        element.Clear();
        element.SendKeys(text);
    }

    protected void Click(By by) =>
        Wait.Until(ExpectedConditions.ElementToBeClickable(by)).Click();

    protected string GetText(By by) =>
        FindElement(by).Text;

    protected void TakeScreenshot(string name)
    {
        var screenshot = ((ITakesScreenshot)Driver).GetScreenshot();
        var path = Path.Combine("screenshots", $"{name}_{DateTime.Now:yyyyMMdd_HHmmss}.png");
        Directory.CreateDirectory("screenshots");
        screenshot.SaveAsFile(path);
    }
}
```

### LoginPage
```csharp
public class LoginPage : BasePage
{
    private static readonly By EmailInput = By.CssSelector("[data-testid='email']");
    private static readonly By PasswordInput = By.CssSelector("[data-testid='password']");
    private static readonly By LoginButton = By.CssSelector("button[type='submit']");
    private static readonly By ErrorMessage = By.CssSelector("[data-testid='error-message']");
    private static readonly By LockoutMessage = By.CssSelector("[data-testid='lockout']");

    public LoginPage(IWebDriver driver) : base(driver) { }

    protected override string PageUrl => "/login";
    protected override By PageIdentifier => LoginButton;

    public void EnterEmail(string email) => ClearAndType(EmailInput, email);
    public void EnterPassword(string password) => ClearAndType(PasswordInput, password);
    public void ClickLogin() => Click(LoginButton);

    public string GetErrorMessage() => GetText(ErrorMessage);

    public bool IsAccountLocked()
    {
        try { return FindElement(LockoutMessage).Displayed; }
        catch { return false; }
    }

    public DashboardPage LoginAs(string email, string password)
    {
        EnterEmail(email);
        EnterPassword(password);
        ClickLogin();
        return new DashboardPage(Driver);
    }
}
```

---

## §5 — Hooks & Dependency Injection

### WebDriver Hooks
```csharp
[Binding]
public class WebDriverHooks
{
    private readonly IObjectContainer _container;
    private readonly ScenarioContext _scenarioContext;
    private IWebDriver? _driver;

    public WebDriverHooks(IObjectContainer container, ScenarioContext scenarioContext)
    {
        _container = container;
        _scenarioContext = scenarioContext;
    }

    [BeforeScenario(Order = 0)]
    public void InitializeWebDriver()
    {
        _driver = DriverFactory.CreateDriver();
        _container.RegisterInstanceAs(_driver);

        // Register page objects
        _container.RegisterInstanceAs(new LoginPage(_driver));
        _container.RegisterInstanceAs(new DashboardPage(_driver));
        _container.RegisterInstanceAs(new SearchPage(_driver));
    }

    [AfterScenario(Order = 999)]
    public void CleanupWebDriver()
    {
        if (_scenarioContext.TestError != null && _driver != null)
        {
            var screenshot = ((ITakesScreenshot)_driver).GetScreenshot();
            var title = _scenarioContext.ScenarioInfo.Title.Replace(" ", "_");
            var path = $"screenshots/{title}_{DateTime.Now:yyyyMMdd_HHmmss}.png";
            Directory.CreateDirectory("screenshots");
            screenshot.SaveAsFile(path);
            Console.WriteLine($"Screenshot saved: {path}");
        }
        _driver?.Quit();
        _driver?.Dispose();
    }
}
```

### Driver Factory
```csharp
public static class DriverFactory
{
    public static IWebDriver CreateDriver()
    {
        var environment = TestConfig.Environment;

        return environment switch
        {
            "lambdatest" => CreateLambdaTestDriver(),
            "headless" => CreateHeadlessChromeDriver(),
            _ => CreateLocalChromeDriver()
        };
    }

    private static IWebDriver CreateLocalChromeDriver()
    {
        new WebDriverManager.DriverManager().SetUpDriver(new ChromeConfig());
        var options = new ChromeOptions();
        options.AddArguments("--window-size=1920,1080", "--disable-gpu", "--no-sandbox");
        return new ChromeDriver(options);
    }

    private static IWebDriver CreateHeadlessChromeDriver()
    {
        new WebDriverManager.DriverManager().SetUpDriver(new ChromeConfig());
        var options = new ChromeOptions();
        options.AddArguments("--headless=new", "--window-size=1920,1080",
            "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage");
        return new ChromeDriver(options);
    }

    private static IWebDriver CreateLambdaTestDriver()
    {
        var username = Environment.GetEnvironmentVariable("LT_USERNAME");
        var accessKey = Environment.GetEnvironmentVariable("LT_ACCESS_KEY");

        var options = new ChromeOptions();
        options.PlatformName = "Windows 11";
        options.BrowserVersion = "latest";

        var ltOptions = new Dictionary<string, object>
        {
            ["build"] = $"specflow-{Environment.GetEnvironmentVariable("BUILD_ID") ?? "local"}",
            ["name"] = "SpecFlow Tests",
            ["resolution"] = "1920x1080",
            ["console"] = "true",
            ["network"] = "true",
            ["video"] = "true",
            ["visual"] = "true",
            ["selenium_version"] = "4.0.0"
        };
        options.AddAdditionalOption("LT:Options", ltOptions);

        return new RemoteWebDriver(
            new Uri($"https://{username}:{accessKey}@hub.lambdatest.com/wd/hub"),
            options
        );
    }
}
```

### Configuration
```csharp
public static class TestConfig
{
    public static string BaseUrl =>
        Environment.GetEnvironmentVariable("BASE_URL") ?? "http://localhost:3000";

    public static string Environment =>
        System.Environment.GetEnvironmentVariable("TEST_ENV") ?? "local";

    public static int DefaultTimeout =>
        int.Parse(System.Environment.GetEnvironmentVariable("TIMEOUT") ?? "10");
}
```

---

## §6 — Scoped Bindings & Transforms

### Scoped Step Definitions
```csharp
// Steps only available for scenarios tagged @admin
[Binding]
[Scope(Tag = "admin")]
public class AdminSteps
{
    [Given(@"I am logged in as admin")]
    public void GivenLoggedInAsAdmin()
    {
        // Admin-specific login flow
    }

    [Then(@"I should see the admin panel")]
    public void ThenIShouldSeeAdminPanel()
    {
        // Admin-specific assertion
    }
}

// Steps scoped to a specific feature
[Binding]
[Scope(Feature = "User Authentication")]
public class AuthenticationSteps
{
    [When(@"I submit the form")]
    public void WhenISubmitTheForm()
    {
        // Auth-specific submit behavior
    }
}
```

### Step Argument Transformations
```csharp
[Binding]
public class Transforms
{
    [StepArgumentTransformation(@"(\d+) days? from now")]
    public DateTime DaysFromNow(int days) => DateTime.Now.AddDays(days);

    [StepArgumentTransformation(@"(\d+) hours? ago")]
    public DateTime HoursAgo(int hours) => DateTime.Now.AddHours(-hours);

    [StepArgumentTransformation]
    public User UserFromTable(Table table)
    {
        return new User
        {
            Name = table.Rows[0]["Name"],
            Email = table.Rows[0]["Email"],
            Role = table.Rows[0]["Role"]
        };
    }

    [StepArgumentTransformation]
    public List<string> StringListFromTable(Table table)
    {
        return table.Rows.Select(r => r[0]).ToList();
    }
}

// Usage in feature:
// When the order was placed 2 days from now
// And the notification was sent 3 hours ago
```

---

## §7 — CI/CD Integration

### GitHub Actions
```yaml
name: SpecFlow Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: 8.0.x

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore

      - name: Run SpecFlow tests
        run: dotnet test --no-build --logger "trx;LogFileName=results.trx"
        env:
          TEST_ENV: headless
          LT_USERNAME: ${{ secrets.LT_USERNAME }}
          LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
          BUILD_ID: ${{ github.run_id }}

      - name: Generate Living Doc
        if: always()
        run: |
          dotnet tool install --global SpecFlow.Plus.LivingDoc.CLI
          livingdoc test-assembly bin/Debug/net8.0/SpecFlowProject.dll \
            -t bin/Debug/net8.0/TestExecution.json \
            -o LivingDoc.html

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: specflow-results
          path: |
            TestResults/
            LivingDoc.html
            screenshots/
```

### Parallel Execution
```json
// In .runsettings
{
  "RunConfiguration": {
    "MaxCpuCount": 4,
    "TestSessionTimeout": 600000
  }
}
```

```bash
# Run with parallel settings
dotnet test --settings .runsettings --logger "trx"
```

---

## §8 — Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Step definition not found | Missing `[Binding]` attribute or assembly not scanned | Add `[Binding]` to class; verify `specflow.json` stepAssemblies |
| 2 | DI injection fails for page objects | Type not registered in container | Register in `[BeforeScenario]`: `_container.RegisterInstanceAs(new LoginPage(driver))` |
| 3 | `ScenarioContext` not injected | Not requesting via constructor | Add `ScenarioContext` parameter to step class constructor |
| 4 | Parallel tests share WebDriver | Driver registered as singleton | Use `[BeforeScenario]` hook per scenario for fresh driver instance |
| 5 | Feature file not generating code | SpecFlow extension not installed | Install SpecFlow VS extension; ensure NuGet packages match |
| 6 | `AmbiguousStepException` | Multiple step defs match same pattern | Use `[Scope]` attribute or make regex patterns more specific |
| 7 | Scoped binding not triggered | Wrong tag or feature name in `[Scope]` | Verify `[Scope(Tag="x")]` matches feature file `@x` tag exactly |
| 8 | Screenshots not captured on failure | AfterScenario hook order too early | Set `[AfterScenario(Order = 999)]` to run last |
| 9 | Table argument transform fails | Constructor params don't match table headers | Verify `table.Rows[0]["ColumnName"]` matches exact feature file column |
| 10 | Living Doc shows no results | TestExecution.json not generated | Build before running `livingdoc`; verify test-assembly path |
| 11 | CI tests slower than local | No headless mode in CI | Set `TEST_ENV=headless` in CI environment; use `--headless=new` |
| 12 | `Hooks` not executing | Class missing `[Binding]` attribute | Add `[Binding]` to hooks class |

---

## §9 — Best Practices Checklist

1. **BoDi container for DI** — inject WebDriver, pages, and services via constructor, not static fields
2. **ScenarioContext for state** — pass data between steps using `_scenarioContext["key"]`
3. **Scoped bindings for specificity** — `[Scope(Tag="admin")]` prevents step ambiguity
4. **Step argument transforms** — convert table data to domain objects automatically
5. **Feature files for stakeholders** — write Gherkin at business level, not implementation
6. **Screenshot on failure** — capture in `[AfterScenario]` when `TestError != null`
7. **Living Documentation** — generate with `SpecFlow.Plus.LivingDoc` for stakeholder reports
8. **Tag-based execution** — `@smoke`, `@critical`, `@wip` for selective test runs
9. **Background for shared setup** — DRY common Given steps across scenarios
10. **Scenario Outline for data-driven** — use Examples table instead of duplicating scenarios
11. **Page Object per page** — encapsulate locators and actions, extend `BasePage`
12. **Driver factory pattern** — abstract driver creation for local, headless, LambdaTest
13. **FluentAssertions for readability** — `.Should().Contain()` over `Assert.Contains()`
14. **Parallel-safe hooks** — each scenario gets fresh driver; no shared state between tests
