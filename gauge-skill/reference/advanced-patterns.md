# Gauge — Advanced Patterns & Playbook

## Data-Driven Specs

```markdown
# User Registration

|name   |email            |expected|
|-------|-----------------|--------|
|Alice  |alice@test.com   |success |
|       |invalid          |error   |
|Bob    |bob@existing.com |error   |

## Register user with <name> and <email>
* Navigate to registration page
* Enter name <name> and email <email>
* Submit registration
* Verify result is <expected>
```

## Step Implementation with Hooks

```java
public class RegistrationSteps {
    private WebDriver driver;

    @BeforeScenario
    public void setup() {
        driver = new ChromeDriver();
    }

    @AfterScenario
    public void teardown() {
        if (driver != null) driver.quit();
    }

    @Step("Navigate to registration page")
    public void navigateToRegistration() {
        driver.get(System.getenv("APP_URL") + "/register");
    }

    @Step("Enter name <name> and email <email>")
    public void enterDetails(String name, String email) {
        driver.findElement(By.id("name")).sendKeys(name);
        driver.findElement(By.id("email")).sendKeys(email);
    }

    @Step("Submit registration")
    public void submit() {
        driver.findElement(By.id("submit")).click();
    }

    @Step("Verify result is <expected>")
    public void verify(String expected) {
        if ("success".equals(expected)) {
            assertTrue(driver.findElement(By.css(".success")).isDisplayed());
        } else {
            assertTrue(driver.findElement(By.css(".error")).isDisplayed());
        }
    }
}
```

## Concepts (Reusable Step Groups)

```markdown
# Login as <role>
* Navigate to login page
* Enter credentials for <role>
* Click login button
* Verify dashboard is visible
```

## Custom Report Plugin

```java
// Implement GaugeListener
public class CustomReporter implements GaugeListener {
    @Override
    public void scenarioEnd(ScenarioInfo info) {
        logger.info("Scenario: {} - {}", info.getName(),
            info.isFailing() ? "FAIL" : "PASS");
    }
}
```

## Anti-Patterns

- ❌ Steps with UI details in spec files — specs should be business-readable
- ❌ Duplicate step implementations — use Concepts for reuse
- ❌ Hardcoded data in steps — use table-driven specs or env variables
- ❌ Missing `@AfterScenario` cleanup — browser/state leaks
