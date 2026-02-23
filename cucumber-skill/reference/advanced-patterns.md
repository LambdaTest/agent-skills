# Cucumber — Advanced Patterns & Playbook

## Step Definitions with Transforms (Java)

```java
public class StepDefinitions {
    private final WebDriver driver;
    private final World world;

    public StepDefinitions(World world) {
        this.world = world;
        this.driver = world.getDriver();
    }

    @Given("I am on the {page} page")
    public void navigateToPage(Page page) {
        driver.get(page.getUrl());
    }

    @When("I search for {string}")
    public void searchFor(String query) {
        world.searchPage.searchFor(query);
    }

    @Then("I should see {int} results")
    public void verifyResults(int count) {
        assertEquals(count, world.searchPage.getResultCount());
    }

    // Custom parameter type
    @ParameterType("home|login|dashboard|search")
    public Page page(String pageName) {
        return PageFactory.create(pageName);
    }
}
```

## JavaScript Step Definitions

```javascript
const { Given, When, Then, Before, After, setDefaultTimeout } = require('@cucumber/cucumber');
const { expect } = require('@playwright/test');

setDefaultTimeout(30_000);

Before(async function () {
  this.browser = await chromium.launch();
  this.page = await this.browser.newPage();
});

After(async function ({ result }) {
  if (result.status === 'FAILED') {
    const screenshot = await this.page.screenshot();
    this.attach(screenshot, 'image/png');
  }
  await this.browser?.close();
});

Given('I am logged in as {string}', async function (role) {
  await this.page.goto('/login');
  const creds = this.testData.getCredentials(role);
  await this.page.fill('#email', creds.email);
  await this.page.fill('#password', creds.password);
  await this.page.click('#submit');
  await expect(this.page).toHaveURL(/dashboard/);
});

When('I add {string} to cart', async function (product) {
  await this.page.click(`[data-product="${product}"] .add-to-cart`);
  await expect(this.page.locator('.cart-count')).toHaveText(/[1-9]/);
});

Then('the cart total should be {string}', async function (total) {
  const actual = await this.page.locator('.cart-total').textContent();
  expect(actual).toContain(total);
});
```

## Scenario Outline with Examples

```gherkin
Feature: User Registration
  Background:
    Given the registration page is open

  Scenario Outline: Register with different data
    When I register with name "<name>" and email "<email>"
    Then I should see "<message>"

    Examples: Valid registrations
      | name    | email            | message     |
      | Alice   | alice@test.com   | Welcome     |
      | Bob     | bob@example.org  | Welcome     |

    Examples: Invalid registrations
      | name    | email   | message        |
      |         | a@b.com | Name required  |
      | Charlie | invalid | Invalid email  |

  @wip
  Scenario: Register with existing email
    Given a user with email "existing@test.com" exists
    When I register with name "Eve" and email "existing@test.com"
    Then I should see "Email already taken"

  Rule: Password requirements
    Scenario: Weak password rejected
      When I register with password "123"
      Then I should see "Password too weak"
```

## Hooks & World Object

```java
// Hooks.java
public class Hooks {
    @Before(order = 0)
    public void setupDriver(Scenario scenario) { /* ... */ }

    @Before("@database")
    public void seedDatabase() { testDb.seed(); }

    @After
    public void cleanup(Scenario scenario) {
        if (scenario.isFailed()) {
            byte[] screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);
            scenario.attach(screenshot, "image/png", "failure");
        }
        driver.quit();
    }

    @BeforeStep
    public void logStep() { /* logging */ }
}
```

## Anti-Patterns

- ❌ Implementation details in feature files — keep Gherkin business-readable
- ❌ One step per line that maps to a single WebDriver call — compose higher-level steps
- ❌ `And I wait 5 seconds` — use implicit waits in step definitions
- ❌ Scenario coupling via shared state — each scenario should be independent
- ❌ Too many `Given` steps — use `Background` for shared setup
