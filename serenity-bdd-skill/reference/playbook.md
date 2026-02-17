# Serenity BDD — Advanced Playbook

## §1 — Project Setup

### Maven Configuration
```xml
<!-- pom.xml -->
<project>
    <properties>
        <serenity.version>4.1.4</serenity.version>
        <serenity.maven.version>4.1.4</serenity.maven.version>
        <junit.version>5.10.2</junit.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
    </properties>

    <dependencies>
        <dependency>
            <groupId>net.serenity-bdd</groupId>
            <artifactId>serenity-core</artifactId>
            <version>${serenity.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>net.serenity-bdd</groupId>
            <artifactId>serenity-junit5</artifactId>
            <version>${serenity.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>net.serenity-bdd</groupId>
            <artifactId>serenity-screenplay</artifactId>
            <version>${serenity.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>net.serenity-bdd</groupId>
            <artifactId>serenity-screenplay-webdriver</artifactId>
            <version>${serenity.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>net.serenity-bdd</groupId>
            <artifactId>serenity-ensure</artifactId>
            <version>${serenity.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>net.serenity-bdd</groupId>
            <artifactId>serenity-rest-assured</artifactId>
            <version>${serenity.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>net.serenity-bdd</groupId>
            <artifactId>serenity-cucumber</artifactId>
            <version>${serenity.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>net.serenity-bdd.maven.plugins</groupId>
                <artifactId>serenity-maven-plugin</artifactId>
                <version>${serenity.maven.version}</version>
                <executions>
                    <execution>
                        <id>serenity-reports</id>
                        <phase>post-integration-test</phase>
                        <goals><goal>aggregate</goal></goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

### Project Structure
```
src/test/java/
├── features/
│   ├── login/
│   │   ├── LoginTest.java
│   │   └── LoginWithCucumber.java
│   └── search/
│       └── SearchTest.java
├── screenplay/
│   ├── abilities/
│   │   └── AuthenticateWithAPI.java
│   ├── actions/
│   │   ├── LoginActions.java
│   │   ├── NavigateTo.java
│   │   └── Search.java
│   ├── questions/
│   │   ├── DashboardInfo.java
│   │   └── SearchResults.java
│   └── tasks/
│       ├── Login.java
│       ├── PlaceOrder.java
│       └── SearchForProduct.java
├── pages/
│   ├── LoginPage.java
│   ├── DashboardPage.java
│   └── SearchResultsPage.java
├── steps/
│   ├── LoginSteps.java
│   ├── NavigationSteps.java
│   └── SearchSteps.java
└── stepdefs/
    └── LoginStepDefinitions.java
src/test/resources/
├── serenity.conf
└── features/
    └── login.feature
```

### serenity.conf
```hocon
serenity {
    project.name = "My Project Tests"
    test.root = "features"
    tag.failures = "true"
    take.screenshots = FOR_FAILURES
    browser.maximized = true
    restart.browser.for.each = SCENARIO
}

headless.mode = false

webdriver {
    driver = chrome
    autodownload = true

    capabilities {
        browserName = "chrome"
        "goog:chromeOptions" {
            args = ["--remote-allow-origins=*", "--disable-gpu", "--no-sandbox",
                    "--disable-dev-shm-usage", "--window-size=1920,1080"]
        }
    }
}

environments {
    default {
        webdriver.base.url = "http://localhost:3000"
        api.base.url = "http://localhost:3000/api"
    }
    staging {
        webdriver.base.url = "https://staging.example.com"
        api.base.url = "https://staging.example.com/api"
    }
    lambdatest {
        webdriver {
            driver = remote
            remote.url = "https://"${LT_USERNAME}":"${LT_ACCESS_KEY}"@hub.lambdatest.com/wd/hub"
            capabilities {
                browserName = "chrome"
                "LT:Options" {
                    build = "serenity-"${BUILD_ID}
                    name = "Serenity BDD Tests"
                    platform = "Windows 11"
                    resolution = "1920x1080"
                    network = true
                    video = true
                    console = true
                    visual = true
                }
            }
        }
    }
}
```

---

## §2 — Step Libraries Pattern

### Step Library Classes
```java
public class LoginSteps extends ScenarioSteps {
    LoginPage loginPage;

    @Step("Navigate to the login page")
    public void navigateToLogin() {
        loginPage.open();
    }

    @Step("Enter credentials for {0}")
    public void enterCredentials(String email, String password) {
        loginPage.enterEmail(email);
        loginPage.enterPassword(password);
    }

    @Step("Click the login button")
    public void clickLogin() {
        loginPage.clickLogin();
    }

    @Step("Login as {0}")
    public void loginAs(String email, String password) {
        navigateToLogin();
        enterCredentials(email, password);
        clickLogin();
    }

    @Step("Verify error message contains '{0}'")
    public void verifyErrorMessage(String expected) {
        assertThat(loginPage.getErrorMessage()).containsIgnoringCase(expected);
    }
}

public class NavigationSteps extends ScenarioSteps {
    DashboardPage dashboardPage;

    @Step("Verify dashboard is displayed")
    public void verifyDashboard() {
        dashboardPage.shouldBeDisplayed();
    }

    @Step("Verify welcome message for '{0}'")
    public void verifyWelcomeMessage(String name) {
        assertThat(dashboardPage.getWelcomeMessage()).contains(name);
    }

    @Step("Navigate to {0} from sidebar")
    public void navigateToSection(String section) {
        dashboardPage.clickSidebarLink(section);
    }
}
```

### Page Objects
```java
@DefaultUrl("/login")
public class LoginPage extends PageObject {

    @FindBy(css = "[data-testid='email']")
    private WebElementFacade emailInput;

    @FindBy(css = "[data-testid='password']")
    private WebElementFacade passwordInput;

    @FindBy(css = "button[type='submit']")
    private WebElementFacade loginButton;

    @FindBy(css = "[data-testid='error-message']")
    private WebElementFacade errorMessage;

    public void enterEmail(String email) {
        emailInput.waitUntilVisible().clear();
        emailInput.type(email);
    }

    public void enterPassword(String password) {
        passwordInput.waitUntilVisible().clear();
        passwordInput.type(password);
    }

    public void clickLogin() {
        loginButton.waitUntilClickable().click();
    }

    public String getErrorMessage() {
        return errorMessage.waitUntilVisible().getText();
    }

    public boolean isErrorDisplayed() {
        return errorMessage.isCurrentlyVisible();
    }
}

@DefaultUrl("/dashboard")
public class DashboardPage extends PageObject {

    @FindBy(css = "[data-testid='welcome']")
    private WebElementFacade welcomeMessage;

    @FindBy(css = ".sidebar-nav a")
    private List<WebElementFacade> sidebarLinks;

    public void shouldBeDisplayed() {
        welcomeMessage.shouldBeVisible();
    }

    public String getWelcomeMessage() {
        return welcomeMessage.waitUntilVisible().getText();
    }

    public void clickSidebarLink(String text) {
        sidebarLinks.stream()
            .filter(link -> link.getText().equalsIgnoreCase(text))
            .findFirst()
            .orElseThrow(() -> new NoSuchElementException("Link not found: " + text))
            .click();
    }
}
```

### Tests Using Step Libraries
```java
@ExtendWith(SerenityJUnit5Extension.class)
@Tag("smoke")
class LoginTest {
    @Steps LoginSteps loginSteps;
    @Steps NavigationSteps navigationSteps;

    @Test
    @Title("Successful login with valid credentials")
    void successfulLogin() {
        loginSteps.loginAs("admin@test.com", "password");
        navigationSteps.verifyDashboard();
        navigationSteps.verifyWelcomeMessage("Admin");
    }

    @Test
    @Title("Login fails with invalid credentials")
    void loginWithInvalidCredentials() {
        loginSteps.loginAs("wrong@test.com", "bad");
        loginSteps.verifyErrorMessage("Invalid credentials");
    }

    @Test
    @Title("Login with empty fields shows validation")
    void loginWithEmptyFields() {
        loginSteps.navigateToLogin();
        loginSteps.clickLogin();
        loginSteps.verifyErrorMessage("required");
    }
}
```

---

## §3 — Screenplay Pattern

### Tasks
```java
public class Login implements Task {
    private final String email;
    private final String password;

    public Login(String email, String password) {
        this.email = email;
        this.password = password;
    }

    public static Login withCredentials(String email, String password) {
        return new Login(email, password);
    }

    @Override
    @Step("{0} logs in with #email")
    public <T extends Actor> void performAs(T actor) {
        actor.attemptsTo(
            NavigateTo.theLoginPage(),
            Enter.theValue(email).into(LoginPageElements.EMAIL_FIELD),
            Enter.theValue(password).into(LoginPageElements.PASSWORD_FIELD),
            Click.on(LoginPageElements.LOGIN_BUTTON)
        );
    }
}

public class NavigateTo {
    public static Performable theLoginPage() {
        return Task.where("{0} navigates to the login page",
            Open.url("/login")
        );
    }

    public static Performable theSearchPage() {
        return Task.where("{0} navigates to search",
            Open.url("/search")
        );
    }
}

public class SearchForProduct implements Task {
    private final String query;

    public SearchForProduct(String query) { this.query = query; }

    public static SearchForProduct called(String query) {
        return new SearchForProduct(query);
    }

    @Override
    @Step("{0} searches for '#query'")
    public <T extends Actor> void performAs(T actor) {
        actor.attemptsTo(
            Enter.theValue(query).into(SearchPageElements.SEARCH_INPUT).thenHit(Keys.ENTER),
            WaitUntil.the(SearchPageElements.RESULTS_CONTAINER, isVisible())
                .forNoMoreThan(10).seconds()
        );
    }
}
```

### Questions
```java
public class SearchResults {

    public static Question<Integer> count() {
        return actor -> {
            return SearchPageElements.RESULT_ITEMS
                .resolveAllFor(actor)
                .size();
        };
    }

    public static Question<List<String>> titles() {
        return actor -> {
            return SearchPageElements.RESULT_TITLES
                .resolveAllFor(actor)
                .stream()
                .map(WebElementFacade::getText)
                .collect(Collectors.toList());
        };
    }

    public static Question<String> firstResultTitle() {
        return actor -> {
            return SearchPageElements.RESULT_TITLES
                .resolveAllFor(actor)
                .get(0)
                .getText();
        };
    }
}

public class DashboardInfo {

    public static Question<String> welcomeMessage() {
        return actor -> DashboardPageElements.WELCOME_MESSAGE
            .resolveFor(actor)
            .getText();
    }

    public static Question<Boolean> isDisplayed() {
        return actor -> DashboardPageElements.WELCOME_MESSAGE
            .resolveFor(actor)
            .isCurrentlyVisible();
    }
}
```

### Page Elements (Targets)
```java
public class LoginPageElements {
    public static final Target EMAIL_FIELD =
        Target.the("email field").locatedBy("[data-testid='email']");
    public static final Target PASSWORD_FIELD =
        Target.the("password field").locatedBy("[data-testid='password']");
    public static final Target LOGIN_BUTTON =
        Target.the("login button").locatedBy("button[type='submit']");
    public static final Target ERROR_MESSAGE =
        Target.the("error message").locatedBy("[data-testid='error-message']");
}

public class SearchPageElements {
    public static final Target SEARCH_INPUT =
        Target.the("search input").locatedBy("input#search");
    public static final Target RESULTS_CONTAINER =
        Target.the("results container").locatedBy(".search-results");
    public static final Target RESULT_ITEMS =
        Target.the("result items").locatedBy(".search-result-item");
    public static final Target RESULT_TITLES =
        Target.the("result titles").locatedBy(".search-result-item h3");
}
```

### Screenplay Tests
```java
@ExtendWith(SerenityJUnit5Extension.class)
class SearchScreenplayTest {

    Actor alice = Actor.named("Alice");

    @BeforeEach
    void setup() {
        alice.can(BrowseTheWeb.with(getDriver()));
    }

    @Test
    @Title("Search returns matching results")
    void searchReturnsResults() {
        alice.attemptsTo(
            NavigateTo.theSearchPage(),
            SearchForProduct.called("laptop")
        );

        alice.should(
            seeThat(SearchResults.count(), greaterThan(0)),
            seeThat(SearchResults.firstResultTitle(), containsString("Laptop"))
        );
    }

    @Test
    @Title("Login and verify dashboard")
    void loginAndVerifyDashboard() {
        alice.attemptsTo(
            Login.withCredentials("admin@test.com", "password")
        );

        alice.should(
            seeThat(DashboardInfo.isDisplayed(), is(true)),
            seeThat(DashboardInfo.welcomeMessage(), containsString("Admin"))
        );
    }
}
```

---

## §4 — Cucumber Integration

### Feature Files
```gherkin
# src/test/resources/features/login.feature
@login
Feature: User Login
  As a registered user
  I want to log into the application
  So that I can access my dashboard

  Background:
    Given I am on the login page

  @smoke @critical
  Scenario: Successful login with valid credentials
    When I login with "admin@test.com" and "password"
    Then I should see the dashboard
    And the welcome message should contain "Admin"

  @negative
  Scenario Outline: Login with invalid credentials
    When I login with "<email>" and "<password>"
    Then I should see an error message containing "<error>"

    Examples:
      | email            | password | error               |
      | wrong@test.com   | bad      | Invalid credentials |
      | admin@test.com   | wrong    | Invalid credentials |
      |                  |          | required            |
```

### Step Definitions
```java
public class LoginStepDefinitions {

    @Steps LoginSteps loginSteps;
    @Steps NavigationSteps navigationSteps;

    @Given("I am on the login page")
    public void iAmOnTheLoginPage() {
        loginSteps.navigateToLogin();
    }

    @When("I login with {string} and {string}")
    public void iLoginWith(String email, String password) {
        loginSteps.enterCredentials(email, password);
        loginSteps.clickLogin();
    }

    @Then("I should see the dashboard")
    public void iShouldSeeTheDashboard() {
        navigationSteps.verifyDashboard();
    }

    @Then("the welcome message should contain {string}")
    public void welcomeMessageContains(String expected) {
        navigationSteps.verifyWelcomeMessage(expected);
    }

    @Then("I should see an error message containing {string}")
    public void errorMessageContaining(String expected) {
        loginSteps.verifyErrorMessage(expected);
    }
}
```

### Cucumber Runner
```java
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("/features")
@ConfigurationParameter(key = PLUGIN_PROPERTY_NAME,
    value = "io.cucumber.core.plugin.SerenityReporterParallelPlugin,pretty")
@ConfigurationParameter(key = GLUE_PROPERTY_NAME,
    value = "stepdefs")
public class CucumberTestRunner {}
```

---

## §5 — REST API Testing

### Serenity REST Integration
```java
@ExtendWith(SerenityJUnit5Extension.class)
class ApiTest {
    @Steps ApiSteps apiSteps;

    @Test
    @Title("Create user via API")
    void createUser() {
        apiSteps.createUser("John", "john@test.com");
        apiSteps.verifyStatusCode(201);
        apiSteps.verifyResponseContains("id");
    }

    @Test
    @Title("List users returns paginated results")
    void listUsers() {
        apiSteps.getUsers(1, 10);
        apiSteps.verifyStatusCode(200);
        apiSteps.verifyUserCount(10);
    }
}

public class ApiSteps extends ScenarioSteps {
    private final String baseUrl = EnvironmentVariables
        .from(ConfiguredEnvironment.getEnvironmentVariables())
        .getProperty("api.base.url");

    @Step("Create user with name '{0}' and email '{1}'")
    public void createUser(String name, String email) {
        SerenityRest.given()
            .baseUri(baseUrl)
            .contentType(ContentType.JSON)
            .body(Map.of("name", name, "email", email))
        .when()
            .post("/users")
        .then()
            .log().ifError();
    }

    @Step("GET users page {0}, size {1}")
    public void getUsers(int page, int size) {
        SerenityRest.given()
            .baseUri(baseUrl)
            .queryParam("page", page)
            .queryParam("size", size)
        .when()
            .get("/users");
    }

    @Step("Verify status code is {0}")
    public void verifyStatusCode(int expected) {
        SerenityRest.then().statusCode(expected);
    }

    @Step("Verify response contains field '{0}'")
    public void verifyResponseContains(String field) {
        SerenityRest.then().body(field, notNullValue());
    }

    @Step("Verify {0} users returned")
    public void verifyUserCount(int count) {
        SerenityRest.then().body("data.size()", equalTo(count));
    }
}
```

---

## §6 — Reporting & Tags

### Custom Tags and Reporting
```java
@ExtendWith(SerenityJUnit5Extension.class)
class TaggedTests {

    @Test
    @Title("Critical checkout flow")
    @WithTag("type:smoke")
    @WithTags({
        @WithTag("feature:checkout"),
        @WithTag("priority:critical"),
        @WithTag("sprint:24")
    })
    void criticalCheckout() {
        // test implementation
    }

    @Test
    @Title("User profile update")
    @WithTag("feature:profile")
    @Narrative(text = {
        "As a logged-in user",
        "I want to update my profile",
        "So that my information is current"
    })
    void updateProfile() {
        // test implementation
    }

    @Test
    @Pending
    @Title("Feature not yet implemented")
    void pendingFeature() {
        // Will appear as pending in reports
    }

    @Test
    @Manual
    @Title("Manual verification required")
    void manualTest() {
        // Tracked in reports but not automated
    }
}
```

### Running by Tags
```bash
# Run only smoke tests
mvn verify -Dtags="type:smoke"

# Run specific feature
mvn verify -Dtags="feature:checkout"

# Exclude pending
mvn verify -Dtags="not @Pending"

# Combine tags
mvn verify -Dtags="type:smoke and priority:critical"
```

---

## §7 — LambdaTest Integration

### Environment-Based Configuration
```hocon
# In serenity.conf - environments section
environments {
    lambdatest {
        webdriver {
            driver = remote
            remote.url = "https://"${LT_USERNAME}":"${LT_ACCESS_KEY}"@hub.lambdatest.com/wd/hub"
            capabilities {
                browserName = "chrome"
                browserVersion = "latest"
                "LT:Options" {
                    build = "serenity-"${BUILD_ID}
                    name = "Serenity BDD Tests"
                    platform = "Windows 11"
                    resolution = "1920x1080"
                    network = true
                    video = true
                    console = true
                    visual = true
                    selenium_version = "4.0.0"
                }
            }
        }
    }
    lambdatest-firefox {
        webdriver {
            driver = remote
            remote.url = "https://"${LT_USERNAME}":"${LT_ACCESS_KEY}"@hub.lambdatest.com/wd/hub"
            capabilities {
                browserName = "firefox"
                browserVersion = "latest"
                "LT:Options" {
                    build = "serenity-firefox-"${BUILD_ID}
                    platform = "Windows 11"
                }
            }
        }
    }
}
```

### Running on LambdaTest
```bash
# Run with LambdaTest environment
mvn verify -Denvironment=lambdatest

# Cross-browser
mvn verify -Denvironment=lambdatest-firefox
```

### Status Update Hook
```java
@ExtendWith(SerenityJUnit5Extension.class)
class BaseTest {

    @AfterEach
    void updateLambdaTestStatus(TestInfo testInfo) {
        if (System.getenv("LT_USERNAME") != null) {
            String status = "passed"; // Serenity manages pass/fail
            try {
                ((JavascriptExecutor) getDriver())
                    .executeScript("lambda-status=" + status);
            } catch (Exception ignored) {}
        }
    }
}
```

---

## §8 — CI/CD Integration

### GitHub Actions
```yaml
name: Serenity BDD Tests
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

      - name: Run Serenity tests
        run: mvn clean verify -Dheadless.mode=true
        env:
          LT_USERNAME: ${{ secrets.LT_USERNAME }}
          LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}
          BUILD_ID: ${{ github.run_id }}

      - name: Generate Serenity report
        if: always()
        run: mvn serenity:aggregate

      - name: Upload Serenity report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: serenity-report
          path: target/site/serenity/

      - name: Publish report summary
        if: always()
        run: |
          echo "## Serenity Test Results" >> $GITHUB_STEP_SUMMARY
          if [ -f target/site/serenity/serenity-summary.html ]; then
            echo "Report generated. See artifacts." >> $GITHUB_STEP_SUMMARY
          fi
```

### Parallel Execution
```xml
<!-- pom.xml failsafe for parallel -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-failsafe-plugin</artifactId>
    <configuration>
        <parallel>classes</parallel>
        <threadCount>4</threadCount>
        <forkCount>4</forkCount>
        <reuseForks>true</reuseForks>
    </configuration>
</plugin>
```

---

## §9 — Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `@Steps` fields are null | Missing `@ExtendWith(SerenityJUnit5Extension.class)` | Add Serenity JUnit5 extension to test class |
| 2 | Page objects not injected | PageObject not extending `PageObject` base class | Ensure pages extend `net.serenity_bdd.core.pages.PageObject` |
| 3 | Report empty after run | `serenity:aggregate` not executed | Add `mvn serenity:aggregate` or configure maven plugin execution phase |
| 4 | `@Step` annotations not recording | Method not in `@Steps`-annotated class | Steps must be in classes injected via `@Steps`; direct instantiation bypasses recording |
| 5 | WebDriver null in page | Driver not initialized before page access | Use `@Managed` annotation or ensure actor has `BrowseTheWeb` ability |
| 6 | Screenplay `seeThat` fails silently | Wrong import for matchers | Use `net.serenity_bdd.screenplay.ensure.Ensure` or Hamcrest matchers with `seeThat` |
| 7 | Cucumber steps not found | Glue path mismatch | Verify `@ConfigurationParameter(key=GLUE_PROPERTY_NAME)` matches step definition package |
| 8 | Screenshots missing in report | `take.screenshots` set to DISABLED | Set `serenity.take.screenshots=FOR_FAILURES` or `FOR_EACH_ACTION` in serenity.conf |
| 9 | Environment config not loading | Wrong environment key or missing env vars | Check `mvn -Denvironment=xxx` matches `environments.xxx` block in serenity.conf |
| 10 | REST API tests show no steps | Not using `SerenityRest` wrapper | Replace RestAssured with `SerenityRest.given()` for step recording |
| 11 | Tags filter not working | Incorrect tag syntax | Use `type:value` format; run with `-Dtags="type:smoke"` |
| 12 | Parallel tests share driver | Driver scope misconfigured | Set `serenity.restart.browser.for.each=SCENARIO` in serenity.conf |

---

## §10 — Best Practices Checklist

1. **Use Step Libraries for reuse** — `@Steps` classes centralize UI interactions with automatic reporting
2. **Screenplay for complex flows** — Tasks, Questions, and Abilities decouple test intent from implementation
3. **Targets over raw locators** — `Target.the("name").locatedBy(css)` provides readable failure messages
4. **serenity.conf for all config** — HOCON configuration with environment-specific overrides
5. **Tag everything** — `@WithTag` for features, priorities, sprints enables selective execution
6. **Living documentation** — Serenity reports are stakeholder-readable; use `@Narrative` and `@Title`
7. **REST + UI in same suite** — Use `SerenityRest` for API setup/validation alongside WebDriver tests
8. **Cucumber for business specs** — Feature files for stakeholder-facing scenarios; step defs delegate to Steps
9. **Environment-based execution** — `-Denvironment=lambdatest` switches entire WebDriver config
10. **Aggregate reports always** — Run `serenity:aggregate` in CI even on failure for full results
11. **WebElementFacade over WebElement** — Serenity's facade adds waiting, visibility checks, and logging
12. **Page Object `@DefaultUrl`** — Auto-navigation with `page.open()` using annotation URL
13. **`@Pending` for tracking** — Mark unimplemented tests rather than skipping; they appear in reports
14. **Parallel-safe with scenario restarts** — `restart.browser.for.each=SCENARIO` prevents state leakage
