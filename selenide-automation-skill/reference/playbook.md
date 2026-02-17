# Selenide — Advanced Playbook

## §1 — Project Setup

### Maven Configuration
```xml
<!-- pom.xml -->
<project>
    <properties>
        <selenide.version>7.2.3</selenide.version>
        <junit.version>5.10.2</junit.version>
        <allure.version>2.25.0</allure.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
    </properties>

    <dependencies>
        <dependency>
            <groupId>com.codeborne</groupId>
            <artifactId>selenide</artifactId>
            <version>${selenide.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.qameta.allure</groupId>
            <artifactId>allure-selenide</artifactId>
            <version>${allure.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.qameta.allure</groupId>
            <artifactId>allure-junit5</artifactId>
            <version>${allure.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.5</version>
                <configuration>
                    <systemPropertyVariables>
                        <selenide.headless>${headless}</selenide.headless>
                        <selenide.browser>${browser}</selenide.browser>
                    </systemPropertyVariables>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### Project Structure
```
src/test/java/
├── config/
│   └── TestConfig.java
├── pages/
│   ├── BasePage.java
│   ├── LoginPage.java
│   └── DashboardPage.java
├── components/
│   ├── NavBar.java
│   └── DataTable.java
├── tests/
│   ├── BaseTest.java
│   ├── LoginTest.java
│   └── DashboardTest.java
└── utils/
    ├── TestDataFactory.java
    └── AllureListener.java
src/test/resources/
├── selenide.properties
└── testdata/
    └── users.json
```

### selenide.properties
```properties
selenide.browser=chrome
selenide.baseUrl=http://localhost:3000
selenide.timeout=10000
selenide.pageLoadTimeout=30000
selenide.screenshots=true
selenide.savePageSource=false
selenide.reportsFolder=build/reports/selenide
selenide.headless=false
selenide.browserSize=1920x1080
```

---

## §2 — Fluent API & Selectors

### Element Operations
```java
import static com.codeborne.selenide.Selenide.*;
import static com.codeborne.selenide.Condition.*;
import static com.codeborne.selenide.CollectionCondition.*;
import static com.codeborne.selenide.Selectors.*;

class FluentApiExamplesTest {

    @Test
    void singleElementOperations() {
        open("/login");

        // CSS selectors
        $("[data-testid='email']").setValue("user@test.com");
        $("button[type='submit']").click();

        // By selectors
        $(byText("Welcome")).shouldBe(visible);
        $(byAttribute("role", "alert")).shouldHave(text("Success"));
        $(byXpath("//div[@class='card']//h2")).shouldHave(text("Dashboard"));

        // Chained conditions
        $(".notification")
            .shouldBe(visible)
            .shouldHave(text("Saved"))
            .shouldHave(cssClass("success"));

        // Value operations
        $("input#email").shouldHave(value("user@test.com"));
        $("select#role").shouldHave(selectedText("Admin"));
        $("input#agree").shouldBe(checked);

        // Hover and actions
        $(".dropdown-trigger").hover();
        $(".dropdown-menu").shouldBe(visible);

        // Inner element search
        $(".card").find("h2").shouldHave(text("Title"));
        $(".card").$("p.description").shouldHave(text("Details"));
    }

    @Test
    void collectionOperations() {
        open("/products");

        // Size assertions
        $$(".product-card").shouldHave(size(10));
        $$(".product-card").shouldHave(sizeGreaterThan(0));
        $$(".product-card").shouldHave(sizeLessThanOrEqual(20));

        // Content assertions
        $$("ul.nav li").shouldHave(texts("Home", "Products", "About", "Contact"));
        $$(".tag").shouldHave(exactTexts("New", "Sale", "Featured"));

        // Filtering and finding
        $$(".product-card").filterBy(text("Sale")).shouldHave(sizeGreaterThan(0));
        $$(".product-card").excludeWith(cssClass("sold-out")).shouldHave(size(8));
        SelenideElement first = $$(".product-card").first();
        SelenideElement last = $$(".product-card").last();
        SelenideElement third = $$(".product-card").get(2);

        // Iterate
        $$(".product-card").forEach(card -> {
            card.$(".price").shouldBe(visible);
            card.$(".title").shouldNotBe(empty);
        });

        // Snapshot for performance
        List<String> titles = $$(".product-card").snapshot()
            .stream()
            .map(el -> el.$(".title").getText())
            .collect(Collectors.toList());
    }

    @Test
    void formInteractions() {
        open("/form");

        // Text input
        $("input#name").setValue("John Doe");
        $("input#name").clear();
        $("input#name").append(" Jr.");

        // Select dropdown
        $("select#country").selectOption("India");
        $("select#country").selectOptionByValue("IN");
        $("select#country").selectOptionContainingText("Ind");

        // Radio buttons and checkboxes
        $("input[value='premium']").click();
        $("input#terms").setSelected(true);

        // File upload
        $("input[type='file']").uploadFromClasspath("testdata/avatar.png");
        $("input[type='file']").uploadFile(new File("/tmp/report.pdf"));

        // Date inputs
        $("input[type='date']").setValue("2025-01-15");
    }
}
```

---

## §3 — Page Objects

### BasePage
```java
public abstract class BasePage {
    public abstract String getUrl();
    public abstract SelenideElement getPageIdentifier();

    public void openPage() {
        open(getUrl());
        getPageIdentifier().shouldBe(visible);
    }

    public boolean isLoaded() {
        return getPageIdentifier().isDisplayed();
    }

    protected void waitForSpinner() {
        $(".loading-spinner").shouldNotBe(visible);
    }

    protected void clearAndType(SelenideElement input, String text) {
        input.shouldBe(visible).clear();
        input.setValue(text);
    }
}
```

### Login Page
```java
public class LoginPage extends BasePage {
    private final SelenideElement emailInput = $("[data-testid='email']");
    private final SelenideElement passwordInput = $("[data-testid='password']");
    private final SelenideElement loginButton = $("button[type='submit']");
    private final SelenideElement errorMessage = $("[data-testid='error-message']");
    private final SelenideElement rememberMe = $("input#remember");

    @Override public String getUrl() { return "/login"; }
    @Override public SelenideElement getPageIdentifier() { return loginButton; }

    public DashboardPage loginAs(String email, String password) {
        clearAndType(emailInput, email);
        clearAndType(passwordInput, password);
        loginButton.click();
        return page(DashboardPage.class);
    }

    public LoginPage loginExpectingError(String email, String password) {
        clearAndType(emailInput, email);
        clearAndType(passwordInput, password);
        loginButton.click();
        errorMessage.shouldBe(visible);
        return this;
    }

    public LoginPage setRememberMe(boolean checked) {
        rememberMe.setSelected(checked);
        return this;
    }

    public String getErrorText() {
        return errorMessage.shouldBe(visible).getText();
    }
}
```

### Dashboard Page with Reusable Components
```java
public class DashboardPage extends BasePage {
    private final SelenideElement welcomeMessage = $("[data-testid='welcome']");
    private final NavBar navBar = new NavBar();
    private final DataTable usersTable = new DataTable($("[data-testid='users-table']"));

    @Override public String getUrl() { return "/dashboard"; }
    @Override public SelenideElement getPageIdentifier() { return welcomeMessage; }

    public String getWelcomeText() {
        return welcomeMessage.getText();
    }

    public NavBar getNavBar() { return navBar; }
    public DataTable getUsersTable() { return usersTable; }
}

// Reusable Component
public class DataTable {
    private final SelenideElement root;

    public DataTable(SelenideElement root) { this.root = root; }

    public ElementsCollection getRows() {
        return root.$$("tbody tr");
    }

    public int getRowCount() {
        return getRows().size();
    }

    public SelenideElement getCell(int row, int col) {
        return getRows().get(row).$$("td").get(col);
    }

    public DataTable sortBy(String column) {
        root.$("th[data-column='" + column + "']").click();
        return this;
    }

    public DataTable searchFor(String query) {
        root.$("input[type='search']").setValue(query);
        root.$(".loading").shouldNotBe(visible);
        return this;
    }
}
```

### Using Page Objects in Tests
```java
class LoginTest extends BaseTest {
    LoginPage loginPage = new LoginPage();

    @Test
    void successfulLogin() {
        loginPage.openPage();
        DashboardPage dashboard = loginPage.loginAs("admin@test.com", "password");
        dashboard.getPageIdentifier().shouldBe(visible);
        assertThat(dashboard.getWelcomeText()).contains("Welcome");
    }

    @Test
    void invalidCredentialsShowError() {
        loginPage.openPage();
        loginPage.loginExpectingError("wrong@test.com", "bad");
        assertThat(loginPage.getErrorText()).contains("Invalid credentials");
    }

    @Test
    void dashboardTableOperations() {
        loginPage.openPage();
        DashboardPage dashboard = loginPage.loginAs("admin@test.com", "password");

        DataTable table = dashboard.getUsersTable();
        table.searchFor("John");
        table.getRows().shouldHave(sizeGreaterThan(0));
        table.getCell(0, 0).shouldHave(text("John"));
    }
}
```

---

## §4 — Waiting & Async

### Custom Conditions
```java
import com.codeborne.selenide.Condition;
import org.openqa.selenium.WebElement;

public class CustomConditions {

    public static Condition attributeValue(String attr, String expected) {
        return new Condition("attribute " + attr + "=" + expected) {
            @Override
            public boolean apply(Driver driver, WebElement element) {
                return expected.equals(element.getAttribute(attr));
            }
        };
    }

    public static Condition textMatches(String regex) {
        return new Condition("text matches " + regex) {
            @Override
            public boolean apply(Driver driver, WebElement element) {
                return element.getText().matches(regex);
            }
        };
    }
}

// Usage
$(".status").shouldHave(CustomConditions.attributeValue("data-state", "complete"), Duration.ofSeconds(15));
$(".price").shouldHave(CustomConditions.textMatches("\\$\\d+\\.\\d{2}"));
```

### JavaScript Execution
```java
@Test
void javascriptInteraction() {
    open("/spa-app");

    // Execute JS and get result
    String title = executeJavaScript("return document.title;");
    long scrollHeight = executeJavaScript("return document.body.scrollHeight;");

    // Scroll to element
    $(".footer").scrollIntoView("{behavior: 'smooth', block: 'center'}");

    // Wait for SPA framework
    executeJavaScript("return window.__APP_READY__ === true;");

    // Trigger events
    executeJavaScript("arguments[0].dispatchEvent(new Event('change'))", $("input#search"));

    // Remove interfering elements
    executeJavaScript("document.querySelector('.cookie-banner').remove()");
}
```

### Waiting Strategies
```java
@Test
void waitingPatterns() {
    open("/async-page");

    // Built-in implicit waits (default 4s, configurable)
    $(".loaded-content").shouldBe(visible);

    // Custom timeout for specific assertion
    $(".slow-load").shouldBe(visible, Duration.ofSeconds(30));

    // Wait for condition with Selenide.Wait()
    Selenide.Wait()
        .withTimeout(Duration.ofSeconds(10))
        .pollingEvery(Duration.ofMillis(500))
        .until(driver -> $$(".result-item").size() > 5);

    // Wait for page URL/title
    Selenide.webdriver().shouldHave(url(containsString("/dashboard")));
    Selenide.webdriver().shouldHave(title("Dashboard"));

    // Wait for download
    Configuration.downloadsFolder = "build/downloads";
    File pdf = $("a.download-link").download();
    assertThat(pdf.getName()).endsWith(".pdf");
}
```

---

## §5 — Advanced Patterns

### Multi-Window and Frames
```java
@Test
void windowAndFrameHandling() {
    open("/multi-window");

    // Switch to new window
    $("a#open-new").click();
    switchTo().window(1);
    $("h1").shouldHave(text("New Window Content"));
    closeWindow();
    switchTo().window(0);

    // Frames
    switchTo().frame("editor-frame");
    $(".editor-content").shouldBe(visible);
    switchTo().defaultContent();

    // iFrames by element
    switchTo().frame($("iframe.payment-frame"));
    $("input#card-number").setValue("4242424242424242");
    switchTo().defaultContent();
}

@Test
void alertHandling() {
    open("/alerts");

    $("button#alert").click();
    switchTo().alert().accept();

    $("button#confirm").click();
    switchTo().alert().dismiss();

    $("button#prompt").click();
    switchTo().alert().sendKeys("Test Input");
    switchTo().alert().accept();
}
```

### Drag-and-Drop & Advanced Actions
```java
@Test
void advancedActions() {
    open("/interactions");

    // Drag and drop
    $(".draggable").dragAndDrop(DragAndDropOptions.to($(".droppable")));

    // Keyboard actions
    actions()
        .keyDown(Keys.CONTROL)
        .click($(".item-1"))
        .click($(".item-2"))
        .click($(".item-3"))
        .keyUp(Keys.CONTROL)
        .perform();

    // Double-click and right-click
    $(".editable").doubleClick();
    $(".context-target").contextClick();

    // Hover chain
    $(".menu-item").hover();
    $(".submenu-item").shouldBe(visible).click();
}
```

### File Downloads
```java
@Test
void fileDownloadStrategies() {
    // HTTPGET mode (default) — follows href
    Configuration.fileDownload = FileDownloadMode.HTTPGET;
    File csv = $("a.export-csv").download();
    assertThat(csv).hasExtension("csv");

    // PROXY mode — intercepts network
    Configuration.proxyEnabled = true;
    Configuration.fileDownload = FileDownloadMode.PROXY;
    File pdf = $("button.generate-report").download(
        using(FileDownloadMode.PROXY)
            .withFilter(urlContaining("/api/reports/"))
            .withTimeout(30_000)
    );
    assertThat(pdf.length()).isGreaterThan(0);

    // FOLDER mode — watches download directory
    Configuration.fileDownload = FileDownloadMode.FOLDER;
    File file = $("a.download").download();
}
```

---

## §6 — LambdaTest Integration

### Remote Configuration
```java
public class LambdaTestConfig {

    public static void configureLambdaTest() {
        String username = System.getenv("LT_USERNAME");
        String accessKey = System.getenv("LT_ACCESS_KEY");
        String gridUrl = "https://" + username + ":" + accessKey + "@hub.lambdatest.com/wd/hub";

        Configuration.remote = gridUrl;
        Configuration.browser = "chrome";
        Configuration.browserVersion = "latest";

        Map<String, Object> ltOptions = new HashMap<>();
        ltOptions.put("build", "selenide-" + System.getenv("BUILD_ID"));
        ltOptions.put("name", "Selenide Tests");
        ltOptions.put("platform", "Windows 11");
        ltOptions.put("resolution", "1920x1080");
        ltOptions.put("console", "true");
        ltOptions.put("network", "true");
        ltOptions.put("video", "true");
        ltOptions.put("visual", "true");
        ltOptions.put("selenium_version", "4.0.0");

        Configuration.browserCapabilities.setCapability("LT:Options", ltOptions);
    }
}
```

### Base Test with LambdaTest
```java
public class BaseTest {

    @BeforeAll
    static void globalSetup() {
        if (System.getenv("LT_USERNAME") != null) {
            LambdaTestConfig.configureLambdaTest();
        } else {
            Configuration.browser = "chrome";
            Configuration.headless = Boolean.parseBoolean(
                System.getProperty("selenide.headless", "false"));
        }
        Configuration.baseUrl = System.getProperty("selenide.baseUrl", "http://localhost:3000");
        Configuration.timeout = 10000;
        Configuration.browserSize = "1920x1080";
        Configuration.screenshots = true;

        SelenideLogger.addListener("allure", new AllureSelenide()
            .screenshots(true).savePageSource(false));
    }

    @AfterEach
    void updateStatus(TestInfo testInfo) {
        if (System.getenv("LT_USERNAME") != null) {
            try {
                executeJavaScript("lambda-status=passed");
            } catch (Exception ignored) {}
        }
    }

    @AfterAll
    static void globalTeardown() {
        SelenideLogger.removeListener("allure");
    }
}
```

---

## §7 — CI/CD Integration

### GitHub Actions
```yaml
name: Selenide Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 17
          cache: maven

      - name: Run Selenide tests
        run: mvn test -Dheadless=true -Dbrowser=chrome
        env:
          LT_USERNAME: ${{ secrets.LT_USERNAME }}
          LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}

      - name: Generate Allure report
        if: always()
        run: mvn allure:report

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: selenide-reports
          path: |
            build/reports/selenide/
            target/site/allure-maven-plugin/
```

### Parallel Execution
```xml
<!-- pom.xml surefire for parallel -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <configuration>
        <parallel>methods</parallel>
        <threadCount>4</threadCount>
        <perCoreThreadCount>true</perCoreThreadCount>
        <systemPropertyVariables>
            <selenide.headless>true</selenide.headless>
        </systemPropertyVariables>
    </configuration>
</plugin>
```

---

## §8 — Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `ElementNotFound` after page load | Element rendered asynchronously | Use `shouldBe(visible)` — Selenide auto-waits up to `Configuration.timeout` |
| 2 | `StaleElementReferenceException` | DOM re-rendered between find and action | Selenide handles this automatically; if persists, re-query element |
| 3 | `$` returns wrong element | Multiple matches for CSS selector | Use more specific selectors: `$("[data-testid='email']")` or `$(byXpath(...))` |
| 4 | Collections empty `$$(...)` | Elements loaded via AJAX after query | Add `shouldHave(sizeGreaterThan(0))` to wait for elements |
| 5 | Screenshots not generated | `Configuration.screenshots` is false | Set `selenide.screenshots=true` in properties or Configuration |
| 6 | `InvalidStateError` on setValue | Input is readonly or disabled | Assert `shouldBe(enabled)` first; use JS: `executeJavaScript("arguments[0].value='x'", el)` |
| 7 | Download fails | Proxy not enabled or wrong mode | Set `Configuration.proxyEnabled=true` and `fileDownload=PROXY` |
| 8 | Tests interfere in parallel | Shared browser state or static data | Use `@Isolated` annotation or ensure test independence with setup/teardown |
| 9 | `Configuration.remote` ignored | Set after browser already opened | Configure remote URL in `@BeforeAll` before any `open()` calls |
| 10 | Allure report empty | Listener not registered | Add `SelenideLogger.addListener("allure", new AllureSelenide())` in setup |
| 11 | `$.click()` intercepted | Overlay or modal covering element | Use `$.click(ClickOptions.usingJavaScript())` to bypass interception |
| 12 | CI tests pass locally but fail headless | Viewport size differs | Set `Configuration.browserSize="1920x1080"` explicitly |

---

## §9 — Best Practices Checklist

1. **Let Selenide auto-wait** — never use `Thread.sleep()` or explicit WebDriver waits; use `shouldBe()`/`shouldHave()` assertions
2. **Use `$` for single, `$$` for collections** — consistent fluent API across all tests
3. **Page Objects return page types** — `loginPage.loginAs()` returns `DashboardPage` for fluent chaining
4. **Data-testid selectors first** — prefer `[data-testid='x']` over brittle CSS class selectors
5. **Custom Conditions for domain logic** — extend `Condition` class for reusable app-specific waits
6. **Configure via selenide.properties** — externalize browser, timeout, URL settings from code
7. **Allure integration for reports** — add `AllureSelenide` listener for screenshots, steps, and attachments
8. **Snapshot collections for performance** — use `$$.snapshot()` when iterating large collections
9. **Component pattern for reusable widgets** — DataTable, NavBar as composable objects taking root element
10. **Parallel-safe test design** — no shared mutable state; each test creates its own data
11. **Screenshot on failure is automatic** — Selenide captures on assertion failure by default
12. **Use `$$.filterBy()` over loops** — collection filtering is more readable and auto-waits
13. **Set browser size for CI** — explicit `browserSize` prevents responsive layout surprises
14. **LambdaTest for cross-browser** — configure `Configuration.remote` with LT:Options for cloud grid
