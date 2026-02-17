# Gauge — Advanced Playbook

## §1 — Project Setup

### Installation
```bash
# Install Gauge
curl -SsL https://downloads.gauge.org/stable | sh
# Or via npm
npm install -g @getgauge/cli

# Install language runners
gauge install java   # Java runner
gauge install js     # JavaScript runner
gauge install python # Python runner

# Install plugins
gauge install html-report
gauge install xml-report
gauge install screenshot

# Initialize project (Java)
gauge init java
```

### Project Structure
```
project/
├── specs/
│   ├── login.spec
│   ├── checkout.spec
│   └── concepts/
│       └── login_actions.cpt
├── src/test/java/
│   ├── steps/
│   │   ├── LoginSteps.java
│   │   ├── CheckoutSteps.java
│   │   └── CommonSteps.java
│   ├── pages/
│   │   ├── BasePage.java
│   │   ├── LoginPage.java
│   │   └── DashboardPage.java
│   └── utils/
│       ├── DriverFactory.java
│       └── TestDataManager.java
├── env/
│   ├── default/
│   │   └── default.properties
│   └── staging/
│       └── staging.properties
├── resources/
│   └── testdata/
│       └── users.csv
└── manifest.json
```

### Environment Configuration
```properties
# env/default/default.properties
base_url = http://localhost:3000
browser = chrome
headless = false
screenshot_on_failure = true
gauge_clear_state_level = scenario
# Parallel execution
gauge_parallel_streams = 4

# env/staging/staging.properties
base_url = https://staging.example.com
headless = true
```

---

## §2 — Spec Files (Markdown Scenarios)

### Basic Spec
```markdown
# User Authentication

Tags: auth, smoke

## Successful login with valid credentials
Tags: positive

* Navigate to "/login"
* Enter "user@test.com" in "email" field
* Enter "SecurePass123" in "password" field
* Click "Sign In" button
* Verify user is on "/dashboard"
* Verify page contains "Welcome back"

## Login fails with invalid password
Tags: negative

* Navigate to "/login"
* Enter "user@test.com" in "email" field
* Enter "wrongpassword" in "password" field
* Click "Sign In" button
* Verify error message "Invalid email or password"
```

### Data-Driven Specs (Table Parameters)
```markdown
# Product Search

## Search returns matching results

* Search for products with criteria

  |category |min_price |max_price |expected_count |
  |---------|----------|----------|---------------|
  |laptops  |500       |1500      |12             |
  |phones   |200       |800       |25             |
  |tablets  |150       |600       |8              |

## User registration with multiple roles

* Register user with role <role> and verify access to <section>

  |role    |section          |
  |--------|-----------------|
  |admin   |/admin/dashboard |
  |editor  |/content/manage  |
  |viewer  |/reports/view    |
```

### Concepts (Reusable Step Groups)
```markdown
# concepts/login_actions.cpt

# Log in as user <email> with password <password>
* Navigate to "/login"
* Enter <email> in "email" field
* Enter <password> in "password" field
* Click "Sign In" button
* Wait for page load

# Add product <n> to cart with quantity <qty>
* Search for product <n>
* Click first search result
* Set quantity to <qty>
* Click "Add to Cart" button
* Verify cart badge shows <qty>
```

### Using Concepts in Specs
```markdown
# Checkout Flow

## Complete purchase as registered user

* Log in as user "buyer@test.com" with password "pass123"
* Add product "Wireless Mouse" to cart with quantity "2"
* Navigate to "/cart"
* Click "Proceed to Checkout"
* Enter shipping address
* Select "Credit Card" payment method
* Confirm order
* Verify order confirmation displayed
```

---

## §3 — Step Implementations (Java)

### Basic Steps
```java
import com.thoughtworks.gauge.Step;
import com.thoughtworks.gauge.Table;
import com.thoughtworks.gauge.TableRow;
import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.*;

public class CommonSteps {

    private WebDriver driver;
    private WebDriverWait wait;

    public CommonSteps() {
        driver = DriverFactory.getDriver();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Step("Navigate to <url>")
    public void navigateTo(String url) {
        String baseUrl = System.getenv("base_url");
        driver.get(baseUrl + url);
    }

    @Step("Enter <value> in <field> field")
    public void enterText(String value, String field) {
        WebElement element = wait.until(
            ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("[data-testid='" + field + "']")
            )
        );
        element.clear();
        element.sendKeys(value);
    }

    @Step("Click <buttonText> button")
    public void clickButton(String buttonText) {
        wait.until(ExpectedConditions.elementToBeClickable(
            By.xpath("//button[normalize-space()='" + buttonText + "']")
        )).click();
    }

    @Step("Verify user is on <path>")
    public void verifyPath(String path) {
        wait.until(ExpectedConditions.urlContains(path));
        assertTrue(driver.getCurrentUrl().contains(path));
    }

    @Step("Verify page contains <text>")
    public void verifyText(String text) {
        wait.until(ExpectedConditions.textToBePresentInElementLocated(
            By.tagName("body"), text
        ));
    }

    @Step("Verify error message <message>")
    public void verifyError(String message) {
        WebElement alert = wait.until(
            ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("[role='alert'], .error-message")
            )
        );
        assertEquals(message, alert.getText());
    }
}
```

### Table-Driven Steps
```java
import com.thoughtworks.gauge.Step;
import com.thoughtworks.gauge.Table;
import com.thoughtworks.gauge.TableRow;

public class SearchSteps {

    @Step("Search for products with criteria <table>")
    public void searchWithCriteria(Table table) {
        for (TableRow row : table.getTableRows()) {
            String category = row.getCell("category");
            String minPrice = row.getCell("min_price");
            String maxPrice = row.getCell("max_price");
            int expectedCount = Integer.parseInt(row.getCell("expected_count"));

            navigateTo("/products?category=" + category);
            applyPriceFilter(minPrice, maxPrice);

            int actual = getResultCount();
            assertTrue(
                "Expected " + expectedCount + " for " + category + ", got " + actual,
                actual >= expectedCount
            );
        }
    }

    @Step("Register user with role <role> and verify access to <section>")
    public void registerWithRole(String role, String section) {
        String email = "test_" + role + "_" + System.currentTimeMillis() + "@test.com";
        registerUser(email, role);
        loginAs(email);
        navigateTo(section);
        verifyPageLoaded(section);
    }
}
```

---

## §4 — Hooks & Execution Control

### Execution Hooks
```java
import com.thoughtworks.gauge.*;

public class ExecutionHooks {

    @BeforeSuite
    public void setupSuite() {
        TestDataManager.seedDatabase();
        System.out.println("Suite started: " + java.time.LocalDateTime.now());
    }

    @AfterSuite
    public void teardownSuite() {
        TestDataManager.cleanDatabase();
        DriverFactory.quitAllDrivers();
    }

    @BeforeScenario
    public void setupScenario(ExecutionContext context) {
        DriverFactory.createDriver();
        System.out.println("Running: " + context.getCurrentScenario().getName());
    }

    @AfterScenario
    public void teardownScenario(ExecutionContext context) {
        if (context.getCurrentScenario().getIsFailing()) {
            captureScreenshot(context.getCurrentScenario().getName());
            capturePageSource(context.getCurrentScenario().getName());
            captureBrowserLogs();
        }
        DriverFactory.quitDriver();
    }

    @BeforeStep
    public void beforeStep(ExecutionContext context) {
        // Log step for debugging
    }

    @AfterStep
    public void afterStep(ExecutionContext context) {
        if (context.getCurrentStep().getIsFailing()) {
            Gauge.writeMessage("Step failed: " + context.getCurrentStep().getText());
        }
    }

    private void captureScreenshot(String scenarioName) {
        try {
            TakesScreenshot ts = (TakesScreenshot) DriverFactory.getDriver();
            byte[] screenshot = ts.getScreenshotAs(OutputType.BYTES);
            Gauge.captureScreenshot(); // Attaches to report
        } catch (Exception e) {
            Gauge.writeMessage("Screenshot capture failed: " + e.getMessage());
        }
    }

    private void captureBrowserLogs() {
        try {
            LogEntries logs = DriverFactory.getDriver()
                .manage().logs().get(LogType.BROWSER);
            for (LogEntry entry : logs) {
                Gauge.writeMessage("[BROWSER] " + entry.getMessage());
            }
        } catch (Exception e) {
            // Browser log capture not supported
        }
    }
}
```

---

## §5 — Page Object Pattern

### Base Page
```java
public abstract class BasePage {
    protected WebDriver driver;
    protected WebDriverWait wait;

    public BasePage() {
        this.driver = DriverFactory.getDriver();
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    protected WebElement find(By locator) {
        return wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
    }

    protected void click(By locator) {
        wait.until(ExpectedConditions.elementToBeClickable(locator)).click();
    }

    protected void type(By locator, String text) {
        WebElement el = find(locator);
        el.clear();
        el.sendKeys(text);
    }

    protected void selectByText(By locator, String visibleText) {
        new Select(find(locator)).selectByVisibleText(visibleText);
    }

    protected boolean isVisible(By locator) {
        try {
            return find(locator).isDisplayed();
        } catch (TimeoutException e) {
            return false;
        }
    }

    protected void waitForUrl(String partialUrl) {
        wait.until(ExpectedConditions.urlContains(partialUrl));
    }
}
```

### Concrete Page Objects
```java
public class LoginPage extends BasePage {
    private final By emailInput = By.cssSelector("[data-testid='email']");
    private final By passwordInput = By.cssSelector("[data-testid='password']");
    private final By submitBtn = By.cssSelector("[data-testid='login-submit']");
    private final By errorMsg = By.cssSelector("[role='alert']");

    public LoginPage open() {
        driver.get(System.getenv("base_url") + "/login");
        return this;
    }

    public DashboardPage loginAs(String email, String password) {
        type(emailInput, email);
        type(passwordInput, password);
        click(submitBtn);
        return new DashboardPage();
    }

    public String getErrorMessage() {
        return find(errorMsg).getText();
    }
}

public class DashboardPage extends BasePage {
    private final By welcomeText = By.cssSelector("[data-testid='welcome']");
    private final By navMenu = By.cssSelector("[data-testid='nav-menu']");

    public DashboardPage verifyLoaded() {
        waitForUrl("/dashboard");
        find(welcomeText);
        return this;
    }

    public String getWelcomeMessage() {
        return find(welcomeText).getText();
    }

    public void navigateTo(String menuItem) {
        click(navMenu);
        click(By.linkText(menuItem));
    }
}
```

### Using Page Objects in Steps
```java
public class LoginSteps {
    private LoginPage loginPage = new LoginPage();
    private DashboardPage dashboardPage;

    @Step("Open login page")
    public void openLogin() {
        loginPage.open();
    }

    @Step("Log in as <email> with password <password>")
    public void login(String email, String password) {
        dashboardPage = loginPage.open().loginAs(email, password);
    }

    @Step("Verify dashboard welcome message contains <text>")
    public void verifyWelcome(String text) {
        dashboardPage.verifyLoaded();
        assertTrue(dashboardPage.getWelcomeMessage().contains(text));
    }
}
```

---

## §6 — Data Management & Custom Data Stores

### Data Store (Scenario/Spec/Suite Level)
```java
import com.thoughtworks.gauge.datastore.*;

public class DataStoreSteps {

    @Step("Create user and store details")
    public void createAndStoreUser() {
        String email = "user_" + System.currentTimeMillis() + "@test.com";
        String userId = UserApi.createUser(email, "Test User");

        // Available for current scenario only
        ScenarioDataStore.put("userEmail", email);
        ScenarioDataStore.put("userId", userId);
    }

    @Step("Verify created user is displayed")
    public void verifyUser() {
        String email = (String) ScenarioDataStore.get("userEmail");
        verifyText(email);
    }

    @Step("Set up shared test data for spec")
    public void specLevelData() {
        // Available across all scenarios in one spec
        SpecDataStore.put("apiToken", AuthHelper.getAdminToken());
    }

    @Step("Initialize suite-level config")
    public void suiteLevelData() {
        // Available for entire suite
        SuiteDataStore.put("environment", System.getenv("GAUGE_ENV"));
    }
}
```

### CSV Data Files
```java
@Step("Load users from CSV and verify accounts")
public void loadFromCsv() throws Exception {
    try (CSVReader reader = new CSVReader(
            new FileReader("resources/testdata/users.csv"))) {
        String[] headers = reader.readNext();
        String[] line;
        while ((line = reader.readNext()) != null) {
            String email = line[0];
            String role = line[1];
            verifyUserAccount(email, role);
        }
    }
}
```

---

## §7 — LambdaTest Integration

### Driver Factory with LambdaTest
```java
public class DriverFactory {
    private static ThreadLocal<WebDriver> drivers = new ThreadLocal<>();

    public static WebDriver createDriver() {
        String browser = System.getenv("browser");
        boolean isCloud = "true".equals(System.getenv("use_lambdatest"));

        WebDriver driver;
        if (isCloud) {
            driver = createLambdaTestDriver();
        } else {
            driver = createLocalDriver(browser);
        }
        drivers.set(driver);
        return driver;
    }

    private static WebDriver createLambdaTestDriver() {
        String username = System.getenv("LT_USERNAME");
        String accessKey = System.getenv("LT_ACCESS_KEY");

        ChromeOptions options = new ChromeOptions();
        options.setPlatformName("Windows 11");
        options.setBrowserVersion("latest");

        HashMap<String, Object> ltOptions = new HashMap<>();
        ltOptions.put("project", "Gauge Tests");
        ltOptions.put("build", "gauge-" + System.getenv("BUILD_NUMBER"));
        ltOptions.put("name", Thread.currentThread().getName());
        ltOptions.put("console", true);
        ltOptions.put("network", true);
        ltOptions.put("visual", true);
        ltOptions.put("w3c", true);
        options.setCapability("LT:Options", ltOptions);

        try {
            return new RemoteWebDriver(
                new URL("https://" + username + ":" + accessKey +
                    "@hub.lambdatest.com/wd/hub"),
                options
            );
        } catch (MalformedURLException e) {
            throw new RuntimeException("Invalid LambdaTest hub URL", e);
        }
    }

    private static WebDriver createLocalDriver(String browser) {
        return switch (browser != null ? browser : "chrome") {
            case "firefox" -> new FirefoxDriver();
            case "edge" -> new EdgeDriver();
            default -> {
                ChromeOptions opts = new ChromeOptions();
                if ("true".equals(System.getenv("headless"))) {
                    opts.addArguments("--headless=new");
                }
                yield new ChromeDriver(opts);
            }
        };
    }

    public static WebDriver getDriver() {
        return drivers.get();
    }

    public static void quitDriver() {
        WebDriver driver = drivers.get();
        if (driver != null) {
            driver.quit();
            drivers.remove();
        }
    }
}
```

### LambdaTest Environment Properties
```properties
# env/lambdatest/lambdatest.properties
use_lambdatest = true
browser = chrome
headless = false
LT_USERNAME = ${LT_USERNAME}
LT_ACCESS_KEY = ${LT_ACCESS_KEY}
```

---

## §8 — CI/CD Integration

### GitHub Actions
```yaml
name: Gauge Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  gauge-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: testdb
          POSTGRES_PASSWORD: postgres
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Install Gauge
        uses: getgauge/setup-gauge@master
        with:
          gauge-version: master
          gauge-plugins: java, html-report, xml-report

      - name: Run Gauge specs
        run: gauge run specs/ --env ci
        env:
          base_url: http://localhost:3000
          headless: true
          GAUGE_PARALLEL_STREAMS: 4

      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: gauge-reports
          path: |
            reports/html-report/
            reports/xml-report/

      - name: Publish test results
        if: always()
        uses: dorny/test-reporter@v1
        with:
          name: Gauge Results
          path: reports/xml-report/*.xml
          reporter: java-junit
```

### Running with Tags
```bash
# Run smoke tests only
gauge run specs/ --tags "smoke"

# Run auth tests except negative
gauge run specs/ --tags "auth & !negative"

# Run in parallel
gauge run specs/ --parallel -n 4

# Run specific spec
gauge run specs/login.spec

# Run with specific environment
gauge run specs/ --env staging

# Run with verbose output
gauge run specs/ --verbose
```

---

## §9 — Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `Step implementation not found` | Step text in spec doesn't match `@Step` annotation exactly | Compare spec step text character-by-character with annotation; check parameter placeholders `<param>` match |
| 2 | `Could not get a driver` | DriverFactory not returning ThreadLocal driver | Ensure `createDriver()` is called in `@BeforeScenario`; check `drivers.set(driver)` is called |
| 3 | `Scenario data store returns null` | Storing in one step, reading in different scenario | Use `ScenarioDataStore` only within same scenario; use `SpecDataStore` for cross-scenario sharing |
| 4 | Concept step not resolved | Concept file has wrong extension or location | Concepts must be `.cpt` files in `specs/` or `concepts/` directory; verify Markdown heading format |
| 5 | Parallel tests interfere with each other | Shared mutable state between threads | Use `ThreadLocal` for all driver/state references; isolate test data per thread with timestamps |
| 6 | Table parameters not passed to step | Step signature doesn't accept `Table` type | Add `com.thoughtworks.gauge.Table` as last parameter in step method |
| 7 | Tags filter not working | Wrong tag operator syntax | Use `&` for AND, `|` for OR; quote complex expressions: `--tags "smoke & !slow"` |
| 8 | Screenshots not in report | `Gauge.captureScreenshot()` not called | Call `Gauge.captureScreenshot()` in `@AfterScenario` when `context.getCurrentScenario().getIsFailing()` |
| 9 | Environment properties not loaded | Wrong directory structure under `env/` | Each environment needs its own subdirectory: `env/staging/staging.properties` |
| 10 | `gauge run` hangs | Browser window opened in CI without headless | Set `headless = true` in CI environment properties |
| 11 | Step with same text in multiple classes | Ambiguous step implementation | Gauge doesn't allow duplicate step text; consolidate into one class or use different step wording |
| 12 | HTML report missing scenarios | `gauge_clear_state_level` misconfigured | Set to `scenario` in properties; ensure `xml-report` plugin is installed for CI artifact upload |

---

## §10 — Best Practices Checklist

1. Write specs in business language — non-technical stakeholders should understand them
2. Use concepts (`.cpt`) for reusable step sequences — reduces duplication across specs
3. Keep step implementations thin — delegate to page objects and helpers
4. Use `ScenarioDataStore` / `SpecDataStore` for passing data between steps
5. Implement `ThreadLocal` drivers for safe parallel execution
6. Use environment directories (`env/staging/`, `env/ci/`) for configuration per environment
7. Tag specs and scenarios for selective execution (`smoke`, `regression`, `slow`)
8. Capture screenshots and browser logs on failure in `@AfterScenario`
9. Use table parameters for data-driven testing instead of duplicating scenarios
10. Run `gauge validate` before pushing to catch unimplemented steps early
11. Keep specs focused — one feature per spec file, one flow per scenario
12. Use `Gauge.writeMessage()` to add contextual debug info to reports
13. Configure `gauge_clear_state_level = scenario` for test isolation
14. Set up CI with `--parallel -n N` and XML reports for test result publishing
