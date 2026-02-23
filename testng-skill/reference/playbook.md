# TestNG — Advanced Implementation Playbook

## §1 — Project Setup & Configuration

```xml
<!-- pom.xml -->
<dependencies>
    <dependency>
        <groupId>org.testng</groupId>
        <artifactId>testng</artifactId>
        <version>7.9.0</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.seleniumhq.selenium</groupId>
        <artifactId>selenium-java</artifactId>
        <version>4.18.1</version>
    </dependency>
    <dependency>
        <groupId>io.github.bonigarcia</groupId>
        <artifactId>webdrivermanager</artifactId>
        <version>5.7.0</version>
    </dependency>
    <dependency>
        <groupId>io.qameta.allure</groupId>
        <artifactId>allure-testng</artifactId>
        <version>2.25.0</version>
    </dependency>
</dependencies>

<build><plugins>
    <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.2.5</version>
        <configuration>
            <suiteXmlFiles><suiteXmlFile>testng.xml</suiteXmlFile></suiteXmlFiles>
            <parallel>classes</parallel>
            <threadCount>4</threadCount>
            <argLine>-Denv=${env:qa}</argLine>
        </configuration>
    </plugin>
</plugins></build>
```

## §2 — Suite XML Configuration

```xml
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Regression" parallel="classes" thread-count="4" verbose="1">
    <listeners>
        <listener class-name="listeners.RetryListener"/>
        <listener class-name="listeners.AllureListener"/>
        <listener class-name="listeners.ScreenshotListener"/>
    </listeners>

    <parameter name="browser" value="chrome"/>
    <parameter name="env" value="qa"/>

    <test name="Smoke">
        <groups>
            <run><include name="smoke"/></run>
        </groups>
        <classes>
            <class name="tests.LoginTest"/>
            <class name="tests.DashboardTest"/>
        </classes>
    </test>

    <test name="Regression">
        <groups>
            <run>
                <include name="regression"/>
                <exclude name="wip"/>
                <exclude name="flaky"/>
            </run>
        </groups>
        <packages><package name="tests.*"/></packages>
    </test>

    <test name="API" parallel="methods" thread-count="8">
        <classes><class name="tests.api.UserApiTest"/></classes>
    </test>
</suite>
```

### Multi-Environment Suites

```xml
<!-- testng-staging.xml -->
<suite name="Staging">
    <parameter name="env" value="staging"/>
    <parameter name="browser" value="chrome"/>
    <suite-files>
        <suite-file path="testng-smoke.xml"/>
    </suite-files>
</suite>
```

## §3 — BaseTest & Thread-Safe Driver

```java
public class BaseTest {
    private static final ThreadLocal<WebDriver> driverThread = new ThreadLocal<>();
    protected WebDriver driver;

    @Parameters({"browser", "env"})
    @BeforeMethod(alwaysRun = true)
    public void setUp(@Optional("chrome") String browser, @Optional("qa") String env) {
        WebDriver d;
        switch (browser.toLowerCase()) {
            case "firefox":
                WebDriverManager.firefoxdriver().setup();
                d = new FirefoxDriver();
                break;
            case "edge":
                WebDriverManager.edgedriver().setup();
                d = new EdgeDriver();
                break;
            default:
                ChromeOptions opts = new ChromeOptions();
                if ("ci".equals(System.getenv("CI"))) {
                    opts.addArguments("--headless=new", "--no-sandbox", "--disable-gpu");
                }
                WebDriverManager.chromedriver().setup();
                d = new ChromeDriver(opts);
        }
        d.manage().window().maximize();
        d.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        d.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));
        driverThread.set(d);
        driver = d;

        String baseUrl = ConfigReader.get(env + ".base.url");
        driver.get(baseUrl);
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown(ITestResult result) {
        if (result.getStatus() == ITestResult.FAILURE) {
            captureScreenshot(result.getName());
        }
        WebDriver d = driverThread.get();
        if (d != null) { d.quit(); driverThread.remove(); }
    }

    public WebDriver getDriver() { return driverThread.get(); }

    private void captureScreenshot(String testName) {
        try {
            File src = ((TakesScreenshot) getDriver()).getScreenshotAs(OutputType.FILE);
            String path = "screenshots/" + testName + "_" + System.currentTimeMillis() + ".png";
            FileUtils.copyFile(src, new File(path));
            Allure.addAttachment("Screenshot", new FileInputStream(new File(path)));
        } catch (Exception e) { /* log */ }
    }
}
```

### Configuration Reader

```java
public class ConfigReader {
    private static final Properties props = new Properties();

    static {
        String env = System.getProperty("env", "qa");
        try {
            props.load(ConfigReader.class.getResourceAsStream("/config-" + env + ".properties"));
        } catch (IOException e) { throw new RuntimeException(e); }
    }

    public static String get(String key) {
        return System.getProperty(key, props.getProperty(key));
    }
}
```

## §4 — Data Providers (Advanced)

```java
// Parallel DataProvider
@DataProvider(name = "loginData", parallel = true)
public Object[][] loginData() {
    return new Object[][] {
        {"admin@test.com", "admin123", true},
        {"user@test.com", "wrong", false},
        {"", "", false},
        {"sql@inject.com", "' OR 1=1 --", false},
    };
}

@Test(dataProvider = "loginData", groups = "smoke")
public void testLogin(String email, String password, boolean expected) {
    assertEquals(loginService.authenticate(email, password), expected);
}

// Excel DataProvider
@DataProvider(name = "excelData")
public Object[][] excelData() throws Exception {
    return ExcelReader.getData("testdata/users.xlsx", "Sheet1");
}

// JSON DataProvider
@DataProvider(name = "jsonData")
public Object[][] jsonData() throws Exception {
    List<Map<String, String>> data = JsonReader.readArray("testdata/cases.json");
    return data.stream().map(m -> new Object[]{m}).toArray(Object[][]::new);
}

// CSV DataProvider with Iterator (memory efficient)
@DataProvider(name = "csvData")
public Iterator<Object[]> csvData() throws Exception {
    CSVReader reader = new CSVReader(new FileReader("testdata/large-dataset.csv"));
    return reader.readAll().stream()
        .skip(1)  // skip header
        .map(row -> (Object[]) row)
        .iterator();
}

// Cross-class DataProvider
public class TestDataProviders {
    @DataProvider(name = "sharedData")
    public static Object[][] sharedData() {
        return new Object[][] { {"data1"}, {"data2"} };
    }
}

@Test(dataProvider = "sharedData", dataProviderClass = TestDataProviders.class)
public void testWithSharedData(String data) { /* ... */ }
```

## §5 — Factory Pattern

```java
public class DynamicLoginTest extends BaseTest {
    private String browser;
    private String resolution;

    @Factory(dataProvider = "browserMatrix")
    public DynamicLoginTest(String browser, String resolution) {
        this.browser = browser;
        this.resolution = resolution;
    }

    @DataProvider(name = "browserMatrix")
    public static Object[][] browserMatrix() {
        return new Object[][] {
            {"chrome", "1920x1080"},
            {"chrome", "1366x768"},
            {"firefox", "1920x1080"},
            {"edge", "1920x1080"},
        };
    }

    @Test(groups = "crossBrowser")
    public void testLoginRendering() {
        // each Factory instance runs as independent test
        driver.manage().window().setSize(parseDimension(resolution));
        // ... assert login page renders correctly
    }
}
```

## §6 — Listeners (Production Suite)

```java
// Retry Analyzer — configurable
public class RetryAnalyzer implements IRetryAnalyzer {
    private int count = 0;
    private static final int MAX = Integer.parseInt(
        System.getProperty("retry.max", "2"));

    @Override
    public boolean retry(ITestResult result) {
        if (count < MAX) { count++; return true; }
        return false;
    }
}

// Global retry via transformer
public class RetryListener implements IAnnotationTransformer {
    @Override
    public void transform(ITestAnnotation annotation, Class testClass,
                          Constructor ctor, Method method) {
        if (annotation.getRetryAnalyzerClass() == null) {
            annotation.setRetryAnalyzer(RetryAnalyzer.class);
        }
    }
}

// Screenshot + Allure on failure
public class ScreenshotListener implements ITestListener {
    @Override
    public void onTestFailure(ITestResult result) {
        Object instance = result.getInstance();
        if (instance instanceof BaseTest) {
            WebDriver driver = ((BaseTest) instance).getDriver();
            if (driver != null) {
                byte[] screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);
                Allure.addAttachment("Failure Screenshot", "image/png",
                    new ByteArrayInputStream(screenshot), "png");
            }
        }
    }

    @Override
    public void onTestStart(ITestResult result) {
        Log.info("Starting: " + result.getMethod().getMethodName());
    }

    @Override
    public void onTestSuccess(ITestResult result) {
        Log.info("Passed: " + result.getMethod().getMethodName() +
                 " in " + (result.getEndMillis() - result.getStartMillis()) + "ms");
    }
}

// Execution timing listener
public class TimingListener implements ISuiteListener {
    @Override
    public void onStart(ISuite suite) {
        suite.setAttribute("startTime", System.currentTimeMillis());
    }

    @Override
    public void onFinish(ISuite suite) {
        long start = (long) suite.getAttribute("startTime");
        long duration = System.currentTimeMillis() - start;
        Log.info("Suite completed in " + duration + "ms");
        Log.info("Passed: " + suite.getAllMethods().stream()
            .filter(m -> m.getCurrentInvocationCount() > 0).count());
    }
}
```

## §7 — Soft Assertions & Dependencies

```java
// Soft assertions — report ALL failures
@Test
public void testUserProfile() {
    SoftAssert soft = new SoftAssert();
    User user = userService.getUser(1);
    soft.assertEquals(user.getName(), "Alice", "Name mismatch");
    soft.assertEquals(user.getEmail(), "alice@test.com", "Email mismatch");
    soft.assertTrue(user.isActive(), "User should be active");
    soft.assertNotNull(user.getCreatedAt(), "Created date missing");
    soft.assertAll();
}

// Method dependencies
@Test(priority = 1, groups = "crud")
public void createUser() { userId = userService.create(testUser); }

@Test(priority = 2, dependsOnMethods = "createUser", groups = "crud")
public void verifyUser() { assertNotNull(userService.get(userId)); }

@Test(priority = 3, dependsOnMethods = "createUser", groups = "crud")
public void deleteUser() { userService.delete(userId); }

// Group dependencies
@Test(groups = "setup")
public void seedDatabase() { /* ... */ }

@Test(dependsOnGroups = "setup", groups = "regression")
public void testWithSeededData() { /* ... */ }
```

## §8 — Page Object Integration

```java
public class LoginPage {
    private final WebDriver driver;
    private final WebDriverWait wait;

    @FindBy(id = "email") private WebElement emailInput;
    @FindBy(id = "password") private WebElement passwordInput;
    @FindBy(css = "[data-testid='login-btn']") private WebElement loginButton;
    @FindBy(css = ".error-message") private WebElement errorMessage;

    public LoginPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        PageFactory.initElements(driver, this);
    }

    public DashboardPage loginAs(String email, String password) {
        emailInput.clear();
        emailInput.sendKeys(email);
        passwordInput.clear();
        passwordInput.sendKeys(password);
        loginButton.click();
        return new DashboardPage(driver);
    }

    public String getErrorMessage() {
        wait.until(ExpectedConditions.visibilityOf(errorMessage));
        return errorMessage.getText();
    }
}

// Test using Page Object
public class LoginTest extends BaseTest {
    @Test(groups = "smoke", dataProvider = "validLogins")
    public void testSuccessfulLogin(String email, String password) {
        LoginPage loginPage = new LoginPage(driver);
        DashboardPage dashboard = loginPage.loginAs(email, password);
        assertTrue(dashboard.isLoaded(), "Dashboard should load after login");
    }
}
```

## §9 — Parallel Execution Strategies

```xml
<!-- Method-level: fastest, requires thread-safe tests -->
<suite parallel="methods" thread-count="8">

<!-- Class-level: each class in its own thread (recommended) -->
<suite parallel="classes" thread-count="4">

<!-- Test-level: each <test> block in its own thread -->
<suite parallel="tests" thread-count="3">

<!-- Instance-level: with @Factory -->
<suite parallel="instances" thread-count="4">

<!-- Mixed: different parallelism per test block -->
<suite parallel="tests" thread-count="3">
    <test name="UITests" parallel="classes" thread-count="2">
        <classes>...</classes>
    </test>
    <test name="APITests" parallel="methods" thread-count="8">
        <classes>...</classes>
    </test>
</suite>
```

### Thread-Safe Guidelines

```java
// Thread-safe: Use ThreadLocal for shared resources
private static final ThreadLocal<WebDriver> driver = new ThreadLocal<>();
private static final ThreadLocal<SoftAssert> softAssert = new ThreadLocal<>();

@BeforeMethod
public void init() {
    driver.set(new ChromeDriver());
    softAssert.set(new SoftAssert());
}
```

## §10 — Reporting Integration

```java
// Allure annotations
@Epic("User Management")
@Feature("Login")
@Story("Successful Login")
@Severity(SeverityLevel.CRITICAL)
@Description("Verifies that valid credentials allow login")
@Test(groups = "smoke")
public void testSuccessfulLogin() {
    Allure.step("Navigate to login page", () -> driver.get(baseUrl + "/login"));
    Allure.step("Enter credentials", () -> {
        loginPage.enterEmail("admin@test.com");
        loginPage.enterPassword("admin123");
    });
    Allure.step("Submit and verify", () -> {
        loginPage.clickLogin();
        assertTrue(dashboard.isLoaded());
    });
}

// ExtentReports listener
public class ExtentListener implements ITestListener {
    private static ExtentReports extent;
    private static ThreadLocal<ExtentTest> test = new ThreadLocal<>();

    @Override
    public void onStart(ITestContext context) {
        extent = new ExtentReports();
        extent.attachReporter(new ExtentSparkReporter("reports/extent-report.html"));
    }

    @Override
    public void onTestStart(ITestResult result) {
        test.set(extent.createTest(result.getMethod().getMethodName()));
    }

    @Override
    public void onTestSuccess(ITestResult result) {
        test.get().pass("Passed");
    }

    @Override
    public void onTestFailure(ITestResult result) {
        test.get().fail(result.getThrowable());
    }

    @Override
    public void onFinish(ITestContext context) { extent.flush(); }
}
```

## §11 — CI/CD Integration

```yaml
# GitHub Actions
name: TestNG Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        suite: [testng-smoke.xml, testng-regression.xml]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - run: mvn test -DsuiteXmlFile=${{ matrix.suite }} -Denv=ci
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.suite }}
          path: |
            test-output/
            target/surefire-reports/
            allure-results/
```

```yaml
# Jenkins Pipeline
pipeline {
    agent any
    parameters {
        choice(name: 'SUITE', choices: ['smoke', 'regression', 'full'], description: 'Test suite')
        choice(name: 'ENV', choices: ['qa', 'staging', 'prod'], description: 'Environment')
    }
    stages {
        stage('Test') {
            steps {
                sh "mvn test -DsuiteXmlFile=testng-${params.SUITE}.xml -Denv=${params.ENV}"
            }
            post {
                always {
                    testNG(reportFilenamePattern: '**/testng-results.xml')
                    allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
                }
            }
        }
    }
}
```

## §12 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Test not found/running | Missing `@Test` or wrong suite XML path | Verify annotations, check `<classes>` in XML |
| `NullPointerException` in parallel | Shared mutable state across threads | Use `ThreadLocal` for driver and data |
| `DependencyException` | Dependent method failed or not found | Check method name spelling, ensure dependency runs first |
| DataProvider returns 0 rows | File path wrong or empty dataset | Verify file path relative to resources, check data format |
| `@BeforeMethod` not running | Missing `alwaysRun = true` | Add `alwaysRun = true` for grouped tests |
| Retry runs infinitely | Counter not per-instance | Ensure `count` resets per test (instance variable) |
| Groups not filtering | Wrong group name or XML config | Check `<include>` names match `@Test(groups = ...)` |
| Listener not triggered | Not registered in XML or `@Listeners` | Add to `<listeners>` in testng.xml |
| Flaky parallel tests | Race conditions on shared resources | Use ThreadLocal, avoid static mutable state |
| Screenshots missing | Driver already quit in `@AfterMethod` | Capture screenshot before `driver.quit()` |
| `@Factory` tests not independent | Shared state between factory instances | Each Factory instance should be fully independent |
| Allure report empty | Missing `allure-testng` dependency or listener | Add dependency + register `AllureTestNg` listener |

## §13 — Best Practices Checklist

- ✅ Use `ThreadLocal<WebDriver>` for parallel-safe driver management
- ✅ Use `@DataProvider(parallel = true)` for data-driven parallelism
- ✅ Use `alwaysRun = true` on setup/teardown with groups
- ✅ Use `SoftAssert` when multiple independent checks needed
- ✅ Use groups (`smoke`, `regression`, `wip`) for selective execution
- ✅ Use listeners (not base classes) for cross-cutting concerns
- ✅ Use `@Factory` for cross-browser / cross-config matrix tests
- ✅ Use Allure or ExtentReports for rich HTML reports
- ✅ Configure retry analyzer with env-configurable max count
- ✅ Keep `dependsOnMethods` minimal — prefer independent tests
- ✅ Use `@Parameters` for suite-level config (browser, env)
- ✅ Use `ConfigReader` pattern for multi-environment properties
- ✅ Store screenshots and logs as Allure attachments
- ✅ Structure: `tests/`, `pages/`, `listeners/`, `utils/`, `testdata/`
