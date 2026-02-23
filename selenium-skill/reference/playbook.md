# Selenium WebDriver — Advanced Implementation Playbook

## §1 — Thread-Safe DriverFactory

```java
public class DriverFactory {
    private static ThreadLocal<WebDriver> driver = new ThreadLocal<>();

    public static WebDriver getDriver() { return driver.get(); }

    public static void initDriver(String browser) {
        WebDriver d;
        switch (browser.toLowerCase()) {
            case "firefox":
                WebDriverManager.firefoxdriver().setup();
                d = new FirefoxDriver(firefoxOptions());
                break;
            case "edge":
                WebDriverManager.edgedriver().setup();
                d = new EdgeDriver(edgeOptions());
                break;
            case "safari":
                d = new SafariDriver();
                break;
            default:
                WebDriverManager.chromedriver().setup();
                d = new ChromeDriver(chromeOptions());
        }
        d.manage().window().maximize();
        d.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
        d.manage().timeouts().scriptTimeout(Duration.ofSeconds(30));
        driver.set(d);
    }

    public static void initRemoteDriver(String browser, String hubUrl) {
        MutableCapabilities caps;
        switch (browser.toLowerCase()) {
            case "firefox": caps = firefoxOptions(); break;
            case "edge":    caps = edgeOptions(); break;
            default:        caps = chromeOptions();
        }
        try {
            WebDriver d = new RemoteWebDriver(new URL(hubUrl), caps);
            d.manage().window().maximize();
            driver.set(d);
        } catch (MalformedURLException e) { throw new RuntimeException(e); }
    }

    private static ChromeOptions chromeOptions() {
        ChromeOptions opts = new ChromeOptions();
        opts.addArguments("--disable-notifications", "--disable-popup-blocking");
        if (Boolean.parseBoolean(System.getProperty("headless", "false"))
                || System.getenv("CI") != null) {
            opts.addArguments("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                "--disable-gpu", "--window-size=1920,1080");
        }
        return opts;
    }

    private static FirefoxOptions firefoxOptions() {
        FirefoxOptions opts = new FirefoxOptions();
        if (Boolean.parseBoolean(System.getProperty("headless", "false"))
                || System.getenv("CI") != null) {
            opts.addArguments("-headless");
        }
        return opts;
    }

    private static EdgeOptions edgeOptions() {
        EdgeOptions opts = new EdgeOptions();
        if (Boolean.parseBoolean(System.getProperty("headless", "false"))
                || System.getenv("CI") != null) {
            opts.addArguments("--headless=new");
        }
        return opts;
    }

    public static void quitDriver() {
        if (driver.get() != null) { driver.get().quit(); driver.remove(); }
    }
}
```

## §2 — Configuration Management

```java
// config.properties → src/test/resources/
// base.url=https://staging.example.com
// browser=chrome
// timeout.explicit=10
// timeout.pageload=30
// headless=false
// screenshot.on.failure=true
// retry.count=2

public class Config {
    private static final Properties props = new Properties();

    static {
        try (InputStream is = Config.class.getClassLoader()
                .getResourceAsStream("config.properties")) {
            props.load(is);
        } catch (IOException e) { throw new RuntimeException(e); }
        // System properties override file (for CI: -Dbase.url=https://prod.example.com)
        System.getProperties().forEach((k, v) -> props.setProperty(k.toString(), v.toString()));
    }

    public static String get(String key) { return props.getProperty(key); }
    public static String get(String key, String def) { return props.getProperty(key, def); }
    public static int getInt(String key, int def) {
        String v = props.getProperty(key);
        return v != null ? Integer.parseInt(v) : def;
    }
    public static boolean getBool(String key, boolean def) {
        String v = props.getProperty(key);
        return v != null ? Boolean.parseBoolean(v) : def;
    }

    public static String baseUrl()       { return get("base.url", "https://localhost:3000"); }
    public static String browser()       { return get("browser", "chrome"); }
    public static int explicitTimeout()  { return getInt("timeout.explicit", 10); }
    public static int retryCount()       { return getInt("retry.count", 2); }
}
```

## §3 — Production BasePage

```java
public abstract class BasePage {
    protected WebDriver driver;
    protected WebDriverWait wait;
    protected Actions actions;

    public BasePage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(Config.explicitTimeout()));
        this.actions = new Actions(driver);
    }

    // --- Core interactions ---
    protected WebElement find(By locator) {
        return wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
    }

    protected List<WebElement> findAll(By locator) {
        return wait.until(ExpectedConditions.presenceOfAllElementsLocatedBy(locator));
    }

    protected void click(By locator) {
        wait.until(ExpectedConditions.elementToBeClickable(locator)).click();
    }

    protected void clickJS(By locator) {
        WebElement el = find(locator);
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", el);
    }

    protected void type(By locator, String text) {
        WebElement el = find(locator);
        el.clear();
        el.sendKeys(text);
    }

    protected String getText(By locator) { return find(locator).getText(); }

    protected boolean isDisplayed(By locator) {
        try { return driver.findElement(locator).isDisplayed(); }
        catch (NoSuchElementException e) { return false; }
    }

    // --- Advanced interactions ---
    protected void selectByVisibleText(By locator, String text) {
        new Select(find(locator)).selectByVisibleText(text);
    }

    protected void hover(By locator) {
        actions.moveToElement(find(locator)).perform();
    }

    protected void dragAndDrop(By source, By target) {
        actions.dragAndDrop(find(source), find(target)).perform();
    }

    protected void scrollToElement(By locator) {
        ((JavascriptExecutor) driver).executeScript(
            "arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", find(locator));
    }

    protected void switchToFrame(By locator) { driver.switchTo().frame(find(locator)); }
    protected void switchToDefault() { driver.switchTo().defaultContent(); }

    protected void handleAlert(boolean accept) {
        wait.until(ExpectedConditions.alertIsPresent());
        Alert alert = driver.switchTo().alert();
        if (accept) alert.accept(); else alert.dismiss();
    }

    // --- Shadow DOM ---
    protected WebElement findInShadow(By hostLocator, String cssSelector) {
        SearchContext shadow = find(hostLocator).getShadowRoot();
        return shadow.findElement(By.cssSelector(cssSelector));
    }

    // --- Waits ---
    protected void waitForUrlContains(String text) {
        wait.until(ExpectedConditions.urlContains(text));
    }

    protected void waitForTextPresent(By locator, String text) {
        wait.until(ExpectedConditions.textToBePresentInElementLocated(locator, text));
    }

    protected void waitForPageLoad() {
        wait.until(d -> ((JavascriptExecutor) d)
            .executeScript("return document.readyState").equals("complete"));
    }

    protected void waitForAjax() {
        wait.until(d -> (Boolean) ((JavascriptExecutor) d)
            .executeScript("return typeof jQuery !== 'undefined' ? jQuery.active == 0 : true"));
    }

    protected void waitForAngular() {
        wait.until(d -> (Boolean) ((JavascriptExecutor) d).executeScript(
            "return window.getAllAngularTestabilities?.().every(t => t.isStable()) ?? true"));
    }
}
```

## §4 — Page Object Example with BasePage

```java
public class LoginPage extends BasePage {
    private final By usernameField = By.id("username");
    private final By passwordField = By.id("password");
    private final By submitButton  = By.cssSelector("button[type='submit']");
    private final By errorMessage  = By.cssSelector(".error-message");

    public LoginPage(WebDriver driver) { super(driver); }

    public LoginPage open() {
        driver.get(Config.baseUrl() + "/login");
        waitForPageLoad();
        return this;
    }

    public DashboardPage loginAs(String user, String pass) {
        type(usernameField, user);
        type(passwordField, pass);
        click(submitButton);
        return new DashboardPage(driver);
    }

    public LoginPage loginExpectingError(String user, String pass) {
        type(usernameField, user);
        type(passwordField, pass);
        click(submitButton);
        return this;
    }

    public String getErrorText() { return getText(errorMessage); }
    public boolean isErrorDisplayed() { return isDisplayed(errorMessage); }
}
```

## §5 — Smart Wait Strategies

```java
public class WaitUtils {
    private WebDriverWait wait;
    private WebDriver driver;

    public WaitUtils(WebDriver driver, int timeout) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(timeout));
    }

    /** Click with StaleElement retry */
    public void clickWithRetry(By locator, int maxRetries) {
        for (int i = 0; i < maxRetries; i++) {
            try {
                wait.until(ExpectedConditions.elementToBeClickable(locator)).click();
                return;
            } catch (StaleElementReferenceException e) {
                if (i == maxRetries - 1) throw e;
            }
        }
    }

    /** FluentWait with custom polling */
    public WebElement fluentWait(By locator) {
        return new FluentWait<>(driver)
            .withTimeout(Duration.ofSeconds(30))
            .pollingEvery(Duration.ofMillis(500))
            .ignoring(NoSuchElementException.class)
            .ignoring(StaleElementReferenceException.class)
            .until(d -> d.findElement(locator));
    }

    /** Wait for element count to stabilize (dynamic lists) */
    public List<WebElement> waitForStableList(By locator) {
        wait.until(d -> {
            int first = d.findElements(locator).size();
            try { Thread.sleep(300); } catch (InterruptedException e) {}
            int second = d.findElements(locator).size();
            return first == second && first > 0;
        });
        return driver.findElements(locator);
    }

    /** Custom ExpectedCondition — element has attribute value */
    public static ExpectedCondition<Boolean> attributeContains(By locator, String attr, String value) {
        return d -> {
            try { return d.findElement(locator).getAttribute(attr).contains(value); }
            catch (Exception e) { return false; }
        };
    }
}
```

## §6 — Data-Driven Testing

```java
// JUnit 5 — CSV file
@ParameterizedTest(name = "Login: {0}/{2}")
@CsvFileSource(resources = "/testdata/login.csv", numLinesToSkip = 1)
void testLoginScenarios(String email, String password, String expected) {
    LoginPage loginPage = new LoginPage(driver).open();
    if ("success".equals(expected)) {
        loginPage.loginAs(email, password);
        assertTrue(driver.getCurrentUrl().contains("/dashboard"));
    } else {
        loginPage.loginExpectingError(email, password);
        assertTrue(loginPage.getErrorText().contains(expected));
    }
}

// JUnit 5 — Method source for complex objects
@ParameterizedTest
@MethodSource("registrationData")
void testRegistration(String name, String email, int age, boolean expected) {
    RegisterPage page = new RegisterPage(driver).open();
    page.fillForm(name, email, age);
    assertEquals(expected, page.isSubmitEnabled());
}

static Stream<Arguments> registrationData() {
    return Stream.of(
        Arguments.of("John", "john@test.com", 25, true),
        Arguments.of("", "invalid", -1, false),
        Arguments.of("Jane", "jane@test.com", 17, false)
    );
}

// TestNG — DataProvider with Excel (Apache POI)
@DataProvider(name = "excelData")
public Object[][] excelData() throws Exception {
    FileInputStream fis = new FileInputStream("src/test/resources/testdata.xlsx");
    Workbook wb = new XSSFWorkbook(fis);
    Sheet sheet = wb.getSheetAt(0);
    int rows = sheet.getPhysicalNumberOfRows();
    int cols = sheet.getRow(0).getPhysicalNumberOfCells();
    Object[][] data = new Object[rows - 1][cols];
    for (int i = 1; i < rows; i++)
        for (int j = 0; j < cols; j++)
            data[i - 1][j] = sheet.getRow(i).getCell(j).toString();
    wb.close();
    return data;
}
```

## §7 — Screenshot & Reporting on Failure

```java
// JUnit 5 Extension
public class ScreenshotExtension implements TestWatcher {
    @Override
    public void testFailed(ExtensionContext ctx, Throwable cause) {
        WebDriver driver = DriverFactory.getDriver();
        if (driver == null) return;
        File src = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
        String name = ctx.getDisplayName().replaceAll("[^a-zA-Z0-9]", "_");
        Path dest = Path.of("target/screenshots", name + "_" + System.currentTimeMillis() + ".png");
        try {
            Files.createDirectories(dest.getParent());
            Files.copy(src.toPath(), dest);
            Allure.addAttachment("Screenshot", "image/png", Files.newInputStream(dest), ".png");
        } catch (IOException e) { e.printStackTrace(); }
    }
}

// TestNG Listener
public class TestListener implements ITestListener {
    @Override
    public void onTestFailure(ITestResult result) {
        WebDriver driver = ((BaseTest) result.getInstance()).getDriver();
        if (driver == null) return;
        String path = "target/screenshots/" + result.getName() + "_" + System.currentTimeMillis() + ".png";
        File src = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
        try { FileUtils.copyFile(src, new File(path)); } catch (IOException e) {}
    }
}
```

## §8 — Allure Reporting

```java
@Epic("Authentication")
@Feature("Login")
@Story("Valid Credentials")
@Severity(SeverityLevel.CRITICAL)
@Test
void testValidLogin() {
    Allure.step("Navigate to login", () -> driver.get(Config.baseUrl() + "/login"));
    Allure.step("Enter credentials", () -> new LoginPage(driver).loginAs("admin", "pass"));
    Allure.step("Verify dashboard", () -> assertTrue(driver.getCurrentUrl().contains("/dashboard")));
}
```

```xml
<!-- pom.xml -->
<dependency>
  <groupId>io.qameta.allure</groupId>
  <artifactId>allure-junit5</artifactId>
  <version>2.25.0</version>
  <scope>test</scope>
</dependency>
```

## §9 — CI/CD Integration

```yaml
# GitHub Actions
name: Selenium Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        browser: [chrome, firefox, edge]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - name: Cache Maven
        uses: actions/cache@v4
        with:
          path: ~/.m2/repository
          key: ${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}
      - name: Run tests
        run: mvn test -Dbrowser=${{ matrix.browser }} -Dheadless=true
        env:
          LT_USERNAME: ${{ secrets.LT_USERNAME }}
          LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
      - name: Allure report
        run: mvn allure:report
        if: always()
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: results-${{ matrix.browser }}
          path: |
            target/surefire-reports/
            target/site/allure-maven-plugin/
            target/screenshots/
```

```yaml
# GitLab CI
selenium-tests:
  image: maven:3.9-eclipse-temurin-17
  stage: test
  services:
    - selenium/standalone-chrome:latest
  variables:
    SELENIUM_REMOTE_URL: http://selenium__standalone-chrome:4444/wd/hub
  script:
    - mvn test -Dbrowser=chrome -Dheadless=true -Dgrid.url=$SELENIUM_REMOTE_URL
  artifacts:
    when: always
    paths: [target/surefire-reports/, target/screenshots/]
    reports:
      junit: target/surefire-reports/TEST-*.xml
```

## §10 — Parallel Execution

```xml
<!-- testng.xml -->
<suite name="Parallel" parallel="tests" thread-count="4">
  <test name="Chrome Tests">
    <parameter name="browser" value="chrome"/>
    <classes><class name="tests.LoginTest"/><class name="tests.SearchTest"/></classes>
  </test>
  <test name="Firefox Tests">
    <parameter name="browser" value="firefox"/>
    <classes><class name="tests.LoginTest"/><class name="tests.SearchTest"/></classes>
  </test>
</suite>
```

```properties
# JUnit 5 parallel — junit-platform.properties
junit.jupiter.execution.parallel.enabled=true
junit.jupiter.execution.parallel.mode.default=concurrent
junit.jupiter.execution.parallel.config.fixed.parallelism=4
```

## §11 — Advanced Element Interactions

```java
// File Download — configure Chrome download directory
public static ChromeOptions downloadOptions(String downloadDir) {
    ChromeOptions opts = chromeOptions();
    HashMap<String, Object> prefs = new HashMap<>();
    prefs.put("download.default_directory", downloadDir);
    prefs.put("download.prompt_for_download", false);
    prefs.put("plugins.always_open_pdf_externally", true);
    opts.setExperimentalOption("prefs", prefs);
    return opts;
}

// Wait for download to complete
public static File waitForDownload(String downloadDir, String filePattern, int timeoutSec) {
    return new FluentWait<>(new File(downloadDir))
        .withTimeout(Duration.ofSeconds(timeoutSec))
        .pollingEvery(Duration.ofSeconds(1))
        .until(dir -> {
            File[] files = dir.listFiles((d, name) -> name.matches(filePattern)
                && !name.endsWith(".crdownload") && !name.endsWith(".tmp"));
            return (files != null && files.length > 0) ? files[0] : null;
        });
}

// Multiple windows / tabs
public void switchToNewWindow() {
    String originalHandle = driver.getWindowHandle();
    for (String handle : driver.getWindowHandles()) {
        if (!handle.equals(originalHandle)) { driver.switchTo().window(handle); break; }
    }
}

// Network logs (Chrome DevTools Protocol)
public List<LogEntry> getNetworkLogs() {
    return driver.manage().logs().get(LogType.PERFORMANCE).getAll();
}
```

## §12 — Retry Mechanism for Flaky Tests

```java
// TestNG — IRetryAnalyzer
public class RetryAnalyzer implements IRetryAnalyzer {
    private int count = 0;
    private static final int MAX = Config.retryCount();

    @Override
    public boolean retry(ITestResult result) {
        if (count < MAX) { count++; return true; }
        return false;
    }
}
// Usage: @Test(retryAnalyzer = RetryAnalyzer.class)
```

## §13 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| `StaleElementReferenceException` | DOM re-rendered after find | Re-locate with `wait.until(elementToBeClickable(...))` |
| `NoSuchElementException` | Element not yet in DOM | Use `wait.until(presenceOfElementLocated(...))` |
| `ElementClickInterceptedException` | Overlay/modal covers element | `scrollIntoView()` then click, or JS click |
| `TimeoutException` | Element never appeared | Check locator, increase timeout, verify page loaded |
| `SessionNotCreatedException` | Driver/browser version mismatch | Use WebDriverManager auto-setup |
| `InvalidSelectorException` | Bad CSS/XPath syntax | Validate selector in browser DevTools |
| `UnhandledAlertException` | Unexpected alert/confirm dialog | Add `wait.until(alertIsPresent())` handler |
| `MoveTargetOutOfBoundsException` | Element outside viewport | `scrollIntoView()` before Actions API |
| Tests pass locally, fail in CI | Display/timing differences | Run headless, increase waits, add `--window-size=1920,1080` |
| Flaky `.click()` | Race condition | Use `elementToBeClickable` + retry pattern |
| iframe elements not found | Wrong browsing context | `switchTo().frame()` before interacting |

## §14 — Best Practices Checklist

- ✅ Use explicit waits — NEVER `Thread.sleep()`
- ✅ Prefer `By.cssSelector` or `By.id` over `By.xpath`
- ✅ Implement Page Object Model for 3+ page interactions
- ✅ Use WebDriverManager for automatic driver management
- ✅ Use `ThreadLocal<WebDriver>` for parallel safety
- ✅ Run headless in CI: `--headless=new --no-sandbox --disable-dev-shm-usage`
- ✅ Take screenshots on failure automatically
- ✅ Set page load and script timeouts explicitly
- ✅ Clean up with `@AfterEach` / `driver.quit()` always
- ✅ Use data-driven approach for repetitive scenarios
- ✅ Never mix implicit and explicit waits
- ✅ Externalize config (properties files) — override with system properties for CI
- ✅ Use Allure or ExtentReports for rich HTML reporting
- ✅ Use retry mechanism for known-flaky tests (max 2 retries)
- ✅ Structure: `pages/`, `tests/`, `utils/`, `config/`, `testdata/`
- ✅ Assert one logical concept per test
- ✅ Cache Maven/Gradle dependencies in CI
