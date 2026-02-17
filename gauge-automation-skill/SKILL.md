---
name: gauge-automation-skill
description: >
  Generates Gauge test specifications in Markdown with step implementations
  in Java, Python, JS, or Ruby. ThoughtWorks' test automation framework.
  Use when user mentions "Gauge", "spec file", "## Scenario", "step
  implementation". Triggers on: "Gauge", "Gauge spec", "Gauge framework",
  "ThoughtWorks test".
languages:
  - Java
  - Python
  - JavaScript
  - Ruby
  - C#
category: bdd-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Gauge Automation Skill

## Core Patterns

### Specification (specs/login.spec)

```markdown
# Login Feature

## Successful Login
* Navigate to login page
* Enter email "user@test.com"
* Enter password "password123"
* Click login button
* Verify dashboard is displayed
* Verify welcome message contains "Welcome"

## Invalid Credentials
* Navigate to login page
* Enter email "wrong@test.com"
* Enter password "wrong"
* Click login button
* Verify error message "Invalid credentials" is shown

## Login with multiple users
|email             |password |expected  |
|-----------------|---------|----------|
|admin@test.com   |admin123 |Dashboard |
|user@test.com    |pass123  |Dashboard |
|bad@test.com     |wrong    |Error     |

* Login as <email> with <password>
* Verify <expected> page is shown
```

### Step Implementation — Java

```java
import com.thoughtworks.gauge.Step;
import com.thoughtworks.gauge.Table;

public class LoginSteps {
    WebDriver driver;

    @Step("Navigate to login page")
    public void navigateToLogin() {
        driver.get("http://localhost:3000/login");
    }

    @Step("Enter email <email>")
    public void enterEmail(String email) {
        driver.findElement(By.id("email")).sendKeys(email);
    }

    @Step("Enter password <password>")
    public void enterPassword(String password) {
        driver.findElement(By.id("password")).sendKeys(password);
    }

    @Step("Click login button")
    public void clickLogin() {
        driver.findElement(By.cssSelector("button[type='submit']")).click();
    }

    @Step("Verify dashboard is displayed")
    public void verifyDashboard() {
        assertTrue(driver.getCurrentUrl().contains("/dashboard"));
    }
}
```

### Step Implementation — Python

```python
from getgauge.python import step
from selenium import webdriver

@step("Navigate to login page")
def navigate_to_login():
    driver.get("http://localhost:3000/login")

@step("Enter email <email>")
def enter_email(email):
    driver.find_element_by_id("email").send_keys(email)

@step("Click login button")
def click_login():
    driver.find_element_by_css_selector("button[type='submit']").click()
```

### Concepts (Reusable Step Groups — specs/concepts/login.cpt)

```markdown
# Login as <email> with <password>
* Navigate to login page
* Enter email <email>
* Enter password <password>
* Click login button
```

## Setup: `gauge install java` (or `python`, `js`, `ruby`)
## Init: `gauge init java`
## Run: `gauge run specs/` or `gauge run specs/login.spec`

### Cloud Execution on TestMu AI

Set environment variables: `LT_USERNAME`, `LT_ACCESS_KEY`

```java
// StepImplementation.java
ChromeOptions browserOptions = new ChromeOptions();
HashMap<String, Object> ltOptions = new HashMap<>();
ltOptions.put("user", System.getenv("LT_USERNAME"));
ltOptions.put("accessKey", System.getenv("LT_ACCESS_KEY"));
ltOptions.put("build", "Gauge Build");
ltOptions.put("platformName", "Windows 11");
ltOptions.put("video", true);
ltOptions.put("console", true);
browserOptions.setCapability("LT:Options", ltOptions);
Driver.setWebDriver(new RemoteWebDriver(
    new URL("https://hub.lambdatest.com/wd/hub"), browserOptions));
```
## Tags: `gauge run --tags "smoke"` (use `Tags: smoke` in spec)

## Deep Patterns

See `reference/playbook.md` for production-grade patterns:

| Section | What You Get |
|---------|-------------|
| §1 Project Setup | Installation, project structure, environment properties |
| §2 Spec Files | Markdown scenarios, data tables, concepts (.cpt) |
| §3 Step Implementations | Java steps, table-driven steps, assertions |
| §4 Hooks & Execution | BeforeSuite/Scenario/Step, screenshots, browser logs |
| §5 Page Objects | BasePage, concrete pages, usage in steps |
| §6 Data Management | ScenarioDataStore, SpecDataStore, CSV data |
| §7 LambdaTest Integration | Remote driver factory with LT:Options |
| §8 CI/CD Integration | GitHub Actions with parallel execution, XML reports |
| §9 Debugging Table | 12 common problems with causes and fixes |
| §10 Best Practices | 14-item Gauge testing checklist |
