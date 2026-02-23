# Java Patterns — Playwright

## Table of Contents
- Setup (Maven / Gradle)
- Basic Test Structure
- JUnit 5 Integration
- POM in Java
- Cloud Integration (Java)

## Setup (Maven)

```xml
<!-- pom.xml -->
<dependencies>
  <dependency>
    <groupId>com.microsoft.playwright</groupId>
    <artifactId>playwright</artifactId>
    <version>1.49.0</version>
  </dependency>
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>
  </dependency>
</dependencies>
```

Install browsers: `mvn exec:java -e -D exec.mainClass=com.microsoft.playwright.CLI -D exec.args="install"`

## Setup (Gradle)

```kotlin
// build.gradle.kts
dependencies {
    implementation("com.microsoft.playwright:playwright:1.49.0")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
}
```

## Basic Test Structure

```java
import com.microsoft.playwright.*;
import org.junit.jupiter.api.*;
import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

public class LoginTest {
    static Playwright playwright;
    static Browser browser;
    BrowserContext context;
    Page page;

    @BeforeAll
    static void setup() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch(
            new BrowserType.LaunchOptions().setHeadless(false)
        );
    }

    @BeforeEach
    void createContext() {
        context = browser.newContext();
        page = context.newPage();
    }

    @AfterEach
    void closeContext() {
        context.close();
    }

    @AfterAll
    static void teardown() {
        browser.close();
        playwright.close();
    }

    @Test
    void shouldLoginSuccessfully() {
        page.navigate("http://localhost:3000/login");
        page.getByLabel("Email").fill("user@example.com");
        page.getByLabel("Password").fill("password123");
        page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Sign in")).click();
        assertThat(page.getByRole(AriaRole.HEADING)).containsText("Dashboard");
    }
}
```

## POM in Java

```java
// pages/LoginPage.java
import com.microsoft.playwright.*;

public class LoginPage {
    private final Page page;
    private final Locator emailInput;
    private final Locator passwordInput;
    private final Locator submitButton;
    private final Locator errorMessage;

    public LoginPage(Page page) {
        this.page = page;
        this.emailInput = page.getByLabel("Email");
        this.passwordInput = page.getByLabel("Password");
        this.submitButton = page.getByRole(AriaRole.BUTTON,
            new Page.GetByRoleOptions().setName("Sign in"));
        this.errorMessage = page.getByRole(AriaRole.ALERT);
    }

    public void navigate() {
        page.navigate("/login");
    }

    public void login(String email, String password) {
        emailInput.fill(email);
        passwordInput.fill(password);
        submitButton.click();
    }

    public Locator getErrorMessage() {
        return errorMessage;
    }
}
```

## Cloud Integration (Java)

```java
import com.microsoft.playwright.*;
import com.google.gson.Gson;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class CloudTest {
    public static void main(String[] args) throws Exception {
        Map<String, Object> ltOptions = new HashMap<>();
        ltOptions.put("platform", "Windows 11");
        ltOptions.put("build", "Java Build");
        ltOptions.put("name", "Java Test");
        ltOptions.put("user", System.getenv("LT_USERNAME"));
        ltOptions.put("accessKey", System.getenv("LT_ACCESS_KEY"));
        ltOptions.put("network", true);
        ltOptions.put("video", true);

        Map<String, Object> capabilities = new HashMap<>();
        capabilities.put("browserName", "Chrome");
        capabilities.put("browserVersion", "latest");
        capabilities.put("LT:Options", ltOptions);

        String capsJson = new Gson().toJson(capabilities);
        String encoded = URLEncoder.encode(capsJson, StandardCharsets.UTF_8);
        String wsEndpoint = "wss://cdp.lambdatest.com/playwright?capabilities=" + encoded;

        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().connect(wsEndpoint);
            Page page = browser.newContext().newPage();

            try {
                page.navigate("https://example.com");
                // test logic...
                setTestStatus(page, "passed", "OK");
            } catch (Exception e) {
                setTestStatus(page, "failed", e.getMessage());
                throw e;
            } finally {
                browser.close();
            }
        }
    }

    static void setTestStatus(Page page, String status, String remark) {
        String action = String.format(
            "lambdatest_action: {\"action\":\"setTestStatus\",\"arguments\":{\"status\":\"%s\",\"remark\":\"%s\"}}",
            status, remark.replace("\"", "\\\"")
        );
        page.evaluate("_ => {}", action);
    }
}
```
