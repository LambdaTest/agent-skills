# Cucumber BDD — Advanced Implementation Playbook

## §1 — Project Setup & Configuration

```xml
<!-- pom.xml -->
<dependencies>
    <dependency>
        <groupId>io.cucumber</groupId>
        <artifactId>cucumber-java</artifactId>
        <version>7.15.0</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>io.cucumber</groupId>
        <artifactId>cucumber-testng</artifactId>
        <version>7.15.0</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>io.cucumber</groupId>
        <artifactId>cucumber-picocontainer</artifactId>
        <version>7.15.0</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.seleniumhq.selenium</groupId>
        <artifactId>selenium-java</artifactId>
        <version>4.18.1</version>
    </dependency>
</dependencies>

<build><plugins>
    <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.2.5</version>
        <configuration>
            <properties>
                <property>
                    <name>dataproviderthreadcount</name>
                    <value>4</value>
                </property>
            </properties>
        </configuration>
    </plugin>
</plugins></build>
```

### Runner Configuration

```java
@CucumberOptions(
    features = "src/test/resources/features",
    glue = {"stepdefs", "hooks"},
    plugin = {
        "pretty",
        "html:target/cucumber-reports/cucumber.html",
        "json:target/cucumber-reports/cucumber.json",
        "io.qameta.allure.cucumber7jvm.AllureCucumber7Jvm",
        "rerun:target/rerun.txt"
    },
    tags = "@smoke and not @wip",
    monochrome = true,
    dryRun = false
)
public class TestRunner extends AbstractTestNGCucumberTests {
    @Override
    @DataProvider(parallel = true)
    public Object[][] scenarios() {
        return super.scenarios();
    }
}

// Rerun failed tests runner
@CucumberOptions(
    features = "@target/rerun.txt",
    glue = {"stepdefs", "hooks"},
    plugin = {"pretty", "html:target/rerun-report.html"}
)
public class RerunRunner extends AbstractTestNGCucumberTests {}
```

## §2 — Feature Writing Patterns

```gherkin
@smoke @auth
Feature: User Authentication
  As a registered user
  I want to log into my account
  So that I can access my dashboard

  Background:
    Given the application is running
    And the test database is seeded

  @positive
  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter email "admin@test.com" and password "admin123"
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see welcome message "Hello, Admin"

  @negative
  Scenario Outline: Login validation
    Given I am on the login page
    When I enter email "<email>" and password "<password>"
    And I click the login button
    Then I should see error message "<error>"

    Examples:
      | email            | password | error                |
      | invalid          | pass123  | Invalid email format |
      | admin@test.com   |          | Password is required |
      |                  | pass123  | Email is required    |
      | wrong@test.com   | wrong    | Invalid credentials  |

  @data-driven
  Scenario: Create multiple users
    Given I am logged in as admin
    When I create users with the following details:
      | name    | email             | role   |
      | Alice   | alice@test.com    | editor |
      | Bob     | bob@test.com      | viewer |
      | Charlie | charlie@test.com  | admin  |
    Then all users should be visible in the user list

  @api
  Scenario: API-created data appears in UI
    Given a product "Widget" exists via API
    When I navigate to the products page
    Then I should see "Widget" in the product list
```

## §3 — Step Definitions

```java
public class LoginSteps {
    private final ScenarioContext ctx;
    private LoginPage loginPage;
    private DashboardPage dashboardPage;

    // PicoContainer DI
    public LoginSteps(ScenarioContext ctx) {
        this.ctx = ctx;
    }

    @Given("I am on the login page")
    public void navigateToLogin() {
        loginPage = new LoginPage(ctx.getDriver());
        loginPage.navigate();
    }

    @When("I enter email {string} and password {string}")
    public void enterCredentials(String email, String password) {
        loginPage.enterEmail(email);
        loginPage.enterPassword(password);
    }

    @When("I click the login button")
    public void clickLogin() {
        dashboardPage = loginPage.clickLogin();
    }

    @Then("I should be redirected to the dashboard")
    public void verifyDashboard() {
        assertTrue(dashboardPage.isLoaded(), "Dashboard should be loaded");
    }

    @Then("I should see welcome message {string}")
    public void verifyWelcome(String expectedMessage) {
        assertEquals(expectedMessage, dashboardPage.getWelcomeMessage());
    }

    @Then("I should see error message {string}")
    public void verifyError(String expectedError) {
        assertEquals(expectedError, loginPage.getErrorMessage());
    }
}

// DataTable step
public class UserSteps {
    @When("I create users with the following details:")
    public void createUsers(DataTable dataTable) {
        List<Map<String, String>> users = dataTable.asMaps();
        for (Map<String, String> user : users) {
            adminPage.createUser(user.get("name"), user.get("email"), user.get("role"));
        }
    }
}
```

## §4 — Dependency Injection & Shared State

```java
// ScenarioContext — shared state across steps (PicoContainer)
public class ScenarioContext {
    private static final ThreadLocal<WebDriver> driverThread = new ThreadLocal<>();
    private final Map<String, Object> context = new ConcurrentHashMap<>();

    public WebDriver getDriver() { return driverThread.get(); }
    public void setDriver(WebDriver driver) { driverThread.set(driver); }
    public void removeDriver() { driverThread.remove(); }

    public void set(String key, Object value) { context.put(key, value); }
    @SuppressWarnings("unchecked")
    public <T> T get(String key) { return (T) context.get(key); }
    public void clear() { context.clear(); }
}

// Shared across multiple step definition classes
public class ApiSteps {
    private final ScenarioContext ctx;

    public ApiSteps(ScenarioContext ctx) { this.ctx = ctx; }

    @Given("a product {string} exists via API")
    public void createProductViaApi(String name) {
        String productId = ApiHelper.createProduct(name);
        ctx.set("productId", productId);  // share with UI steps
    }
}
```

## §5 — Hooks (Lifecycle Management)

```java
public class Hooks {
    private final ScenarioContext ctx;

    public Hooks(ScenarioContext ctx) { this.ctx = ctx; }

    @Before(order = 0)
    public void setUp(Scenario scenario) {
        WebDriver driver = DriverFactory.createDriver(
            System.getProperty("browser", "chrome"));
        ctx.setDriver(driver);
        ctx.set("scenario", scenario);
    }

    @Before(value = "@api", order = 1)
    public void setupApiTests() {
        ctx.set("apiToken", ApiHelper.getAuthToken());
    }

    @After(order = 1)
    public void captureOnFailure(Scenario scenario) {
        if (scenario.isFailed() && ctx.getDriver() != null) {
            byte[] screenshot = ((TakesScreenshot) ctx.getDriver())
                .getScreenshotAs(OutputType.BYTES);
            scenario.attach(screenshot, "image/png", "failure-screenshot");

            String pageSource = ctx.getDriver().getPageSource();
            scenario.attach(pageSource.getBytes(), "text/html", "page-source");
        }
    }

    @After(order = 0)
    public void tearDown() {
        WebDriver driver = ctx.getDriver();
        if (driver != null) {
            driver.quit();
            ctx.removeDriver();
        }
        ctx.clear();
    }

    @BeforeStep
    public void beforeStep(Scenario scenario) {
        // Optional: log each step
    }

    @AfterStep
    public void afterStep(Scenario scenario) {
        if (scenario.isFailed()) {
            // Capture intermediate screenshots
        }
    }
}
```

## §6 — Custom Parameter Types & Transformers

```java
// Custom parameter types
@ParameterType("admin|editor|viewer")
public UserRole role(String role) {
    return UserRole.valueOf(role.toUpperCase());
}

@ParameterType("true|false|yes|no")
public boolean booleanValue(String value) {
    return "true".equalsIgnoreCase(value) || "yes".equalsIgnoreCase(value);
}

// Usage in steps
@When("I create a user with role {role}")
public void createUser(UserRole role) {
    // role is already typed
}

@Then("the feature should be {booleanValue}")
public void verifyFeatureState(boolean enabled) {
    assertEquals(enabled, featurePage.isEnabled());
}

// DocString for large text
@When("I submit the following JSON:")
public void submitJson(String docString) {
    apiHelper.post("/api/data", docString);
}
```

## §7 — Parallel Execution

```java
// TestNG parallel DataProvider (in runner)
@Override
@DataProvider(parallel = true)
public Object[][] scenarios() {
    return super.scenarios();
}

// Thread-safe driver via ScenarioContext + ThreadLocal
// Configure thread count in maven-surefire-plugin:
// <dataproviderthreadcount>4</dataproviderthreadcount>
```

```xml
<!-- testng.xml for Cucumber -->
<suite name="BDD Suite" parallel="methods" thread-count="4">
    <test name="Cucumber">
        <classes>
            <class name="runners.TestRunner"/>
        </classes>
    </test>
</suite>
```

## §8 — Reporting

```java
// Cucumber built-in reports
plugin = {
    "pretty",                                               // console
    "html:target/cucumber-reports/cucumber.html",           // HTML
    "json:target/cucumber-reports/cucumber.json",           // JSON
    "junit:target/cucumber-reports/cucumber.xml",           // JUnit XML
    "timeline:target/cucumber-reports/timeline",            // Timeline
    "io.qameta.allure.cucumber7jvm.AllureCucumber7Jvm",   // Allure
}

// Cucumber Reports plugin (masterthought)
// pom.xml
<plugin>
    <groupId>net.masterthought</groupId>
    <artifactId>maven-cucumber-reporting</artifactId>
    <version>5.7.7</version>
    <executions><execution>
        <id>execution</id>
        <phase>verify</phase>
        <goals><goal>generate</goal></goals>
        <configuration>
            <projectName>My Project</projectName>
            <outputDirectory>${project.build.directory}/cucumber-html-reports</outputDirectory>
            <jsonFiles>
                <param>**/cucumber.json</param>
            </jsonFiles>
        </configuration>
    </execution></executions>
</plugin>
```

## §9 — CI/CD Integration

```yaml
# GitHub Actions
name: BDD Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        tags: ['@smoke', '@regression']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - run: |
          mvn test \
            -Dcucumber.filter.tags="${{ matrix.tags }}" \
            -Dbrowser=chrome-headless \
            -Denv=ci
      - run: mvn verify -DskipTests  # Generate reports
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: bdd-results-${{ matrix.tags }}
          path: |
            target/cucumber-reports/
            target/cucumber-html-reports/
            allure-results/
```

## §10 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Step undefined | Glue path wrong or step not matching | Verify `glue` in runner, check regex/expression |
| Ambiguous step | Two steps match same Gherkin line | Make step expressions more specific |
| Scenario Outline fails | Wrong column name in Examples | Match `<placeholder>` exactly to column header |
| PicoContainer error | Missing no-arg constructor | Use constructor injection, add `cucumber-picocontainer` dep |
| Parallel thread interference | Shared mutable state | Use `ThreadLocal` in `ScenarioContext` |
| Hook not executing | Wrong package in `glue` | Ensure hooks class is in package listed in `glue` |
| Tag filter not working | Wrong syntax | Use `@tag and not @wip` (Cucumber 7+ expression) |
| DataTable type mismatch | Wrong DataTable method | Use `asMaps()` for Map, `asList()` for typed objects |
| Rerun file empty | First run passed | `rerun:target/rerun.txt` only populated on failures |
| Screenshot not attached | Driver null or quit | Capture in `@After(order=1)` before quit in `@After(order=0)` |

## §11 — Best Practices Checklist

- ✅ Write features in business language, not technical steps
- ✅ Use `Background` for shared preconditions across scenarios
- ✅ Use `Scenario Outline` + `Examples` for data-driven tests
- ✅ Use tags (`@smoke`, `@regression`, `@wip`) for selective execution
- ✅ Use PicoContainer for dependency injection across step classes
- ✅ Use `ScenarioContext` with `ThreadLocal` for thread-safe shared state
- ✅ Use hook ordering: `@After(order=1)` for screenshots, `@After(order=0)` for cleanup
- ✅ Use custom parameter types for domain objects
- ✅ Attach screenshots and page source on failure
- ✅ Use `rerun:target/rerun.txt` for re-running failed scenarios
- ✅ Use Allure + masterthought for rich reports
- ✅ Keep step definitions thin — delegate to Page Objects
- ✅ Structure: `features/`, `stepdefs/`, `hooks/`, `pages/`, `runners/`, `utils/`
