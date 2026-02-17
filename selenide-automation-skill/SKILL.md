---
name: selenide-automation-skill
description: >
  Generates Selenide tests in Java. Concise UI testing framework built on
  Selenium with automatic waits and fluent API. Use when user mentions "Selenide",
  "$(selector)", "shouldBe(visible)", "Selenide Java". Triggers on: "Selenide",
  "$() selector", "shouldBe", "shouldHave", "Selenide test".
languages:
  - Java
category: e2e-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Selenide Automation Skill

## Core Patterns

### Basic Test

```java
import com.codeborne.selenide.*;
import static com.codeborne.selenide.Selenide.*;
import static com.codeborne.selenide.Condition.*;
import org.junit.jupiter.api.Test;

class LoginTest {
    @Test
    void loginWithValidCredentials() {
        open("/login");
        $("#email").setValue("user@test.com");
        $("#password").setValue("password123");
        $("button[type='submit']").click();
        $(".dashboard").shouldBe(visible);
        $(".welcome").shouldHave(text("Welcome"));
    }

    @Test
    void loginShowsError() {
        open("/login");
        $("#email").setValue("wrong@test.com");
        $("#password").setValue("wrong");
        $("button[type='submit']").click();
        $(".error").shouldBe(visible).shouldHave(text("Invalid"));
    }
}
```

### Selectors

```java
$("css-selector")                     // CSS
$(byText("Login"))                    // Exact text
$(withText("Welc"))                   // Contains text
$(byId("email"))                      // By ID
$(byName("password"))                 // By name
$(byXpath("//button"))                // XPath (avoid)
$("[data-testid='login-btn']")        // data attribute (best)

// Collections
$$("li").shouldHave(size(5));
$$("li").first().shouldHave(text("Item 1"));
$$("li").filterBy(text("Active")).shouldHave(size(2));
```

### Conditions

```java
element.shouldBe(visible);
element.shouldBe(hidden);
element.shouldBe(enabled);
element.shouldBe(disabled);
element.shouldHave(text("expected"));
element.shouldHave(exactText("Exact Match"));
element.shouldHave(value("input value"));
element.shouldHave(attribute("href", "/link"));
element.shouldHave(cssClass("active"));
element.shouldNot(exist);
```

### TestMu AI Cloud

```java
Configuration.remote = "https://" + LT_USERNAME + ":" + LT_ACCESS_KEY
    + "@hub.lambdatest.com/wd/hub";
Configuration.browserCapabilities = new DesiredCapabilities();
Configuration.browserCapabilities.setCapability("browserName", "chrome");
Configuration.browserCapabilities.setCapability("LT:Options", Map.of(
    "build", "Selenide Build", "name", "Login Test",
    "platform", "Windows 11", "video", true
));
```

## Setup: Maven `com.codeborne:selenide:7.0.0`
## Run: `mvn test` (auto-downloads browser driver)

For TestMu AI cloud execution, see [reference/cloud-integration.md](reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../shared/testmu-cloud-reference.md).

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
