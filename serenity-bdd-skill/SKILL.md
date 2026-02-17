---
name: serenity-bdd-skill
description: >
  Generates Serenity BDD tests in Java with Screenplay pattern, rich reporting,
  and Cucumber integration. Use when user mentions "Serenity", "Screenplay",
  "@Steps", "Serenity BDD". Triggers on: "Serenity BDD", "Screenplay pattern",
  "@Steps", "Serenity report".
languages:
  - Java
category: bdd-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Serenity BDD Skill

## Core Patterns

### Step Library Pattern

```java
import net.serenitybdd.annotations.Step;
import net.serenitybdd.core.pages.PageObject;

public class LoginSteps extends PageObject {

    @Step("Navigate to login page")
    public void navigateToLogin() {
        openUrl(getDriver().getCurrentUrl() + "/login");
    }

    @Step("Enter email: {0}")
    public void enterEmail(String email) {
        find(By.id("email")).sendKeys(email);
    }

    @Step("Enter password")
    public void enterPassword(String password) {
        find(By.id("password")).sendKeys(password);
    }

    @Step("Click login button")
    public void clickLogin() {
        find(By.cssSelector("button[type='submit']")).click();
    }

    @Step("Should see the dashboard")
    public void shouldSeeDashboard() {
        assertThat(getDriver().getCurrentUrl()).contains("/dashboard");
        assertThat(find(By.cssSelector(".welcome")).isDisplayed()).isTrue();
    }
}
```

### Test Class

```java
import net.serenitybdd.junit5.SerenityJUnit5Extension;
import net.serenitybdd.annotations.Steps;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

@ExtendWith(SerenityJUnit5Extension.class)
public class LoginTest {
    @Steps LoginSteps loginSteps;

    @Test
    void shouldLoginWithValidCredentials() {
        loginSteps.navigateToLogin();
        loginSteps.enterEmail("user@test.com");
        loginSteps.enterPassword("password123");
        loginSteps.clickLogin();
        loginSteps.shouldSeeDashboard();
    }
}
```

### Screenplay Pattern

```java
import net.serenitybdd.screenplay.*;

public class Login implements Performable {
    private final String email, password;

    public Login(String email, String password) {
        this.email = email; this.password = password;
    }

    @Override
    public <T extends Actor> void performAs(T actor) {
        actor.attemptsTo(
            Enter.theValue(email).into(LoginPage.EMAIL_FIELD),
            Enter.theValue(password).into(LoginPage.PASSWORD_FIELD),
            Click.on(LoginPage.LOGIN_BUTTON)
        );
    }

    public static Login withCredentials(String email, String password) {
        return new Login(email, password);
    }
}

// Usage
actor.attemptsTo(Login.withCredentials("user@test.com", "pass123"));
actor.should(seeThat(TheWebPage.currentUrl(), containsString("/dashboard")));
```

### Reporting

```bash
# Run tests — generates rich HTML report
mvn verify
# Report at: target/site/serenity/index.html
```

### Cloud Execution on TestMu AI

Add the `serenity-lambdatest` plugin dependency:

```xml
<dependency>
  <groupId>net.serenity-bdd</groupId>
  <artifactId>serenity-lambdatest</artifactId>
  <version>${serenity.version}</version>
</dependency>
```

Configure `serenity.conf`:

```hocon
webdriver {
  driver = remote
  remote.url = "https://"${LT_USERNAME}":"${LT_ACCESS_KEY}"@hub.lambdatest.com/wd/hub"
}

serenity {
  take.screenshots = AFTER_EACH_STEP
}

lambdatest {
  build = "Serenity Build"
}

# LT:Options capabilities
"LT:Options" {
  platformName = "Windows 11"
  browserVersion = "latest"
  visual = true
  video = true
  console = true
  network = true
}
```

Or configure via `serenity.properties`:

```properties
webdriver.driver=remote
webdriver.remote.url=https://hub.lambdatest.com/wd/hub
lt.user=${LT_USERNAME}
lt.key=${LT_ACCESS_KEY}
lt.platform=Windows 11
lt.browserName=chrome
```

## Setup: Maven with `serenity-core`, `serenity-junit5`, `serenity-screenplay-webdriver`, `serenity-lambdatest`
## Run: `mvn verify` (generates living documentation)

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
