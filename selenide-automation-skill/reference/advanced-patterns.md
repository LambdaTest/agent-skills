# Selenide — Advanced Patterns & Playbook

## Fluent Page Objects

```java
public class LoginPage {
    private final SelenideElement emailField = $("#email");
    private final SelenideElement passwordField = $("#password");
    private final SelenideElement submitBtn = $("button[type='submit']");
    private final SelenideElement error = $(".error-message");

    public DashboardPage loginAs(String email, String password) {
        emailField.setValue(email);
        passwordField.setValue(password);
        submitBtn.click();
        return page(DashboardPage.class);
    }

    public LoginPage loginShouldFail(String email, String password) {
        emailField.setValue(email);
        passwordField.setValue(password);
        submitBtn.click();
        error.shouldBe(visible);
        return this;
    }

    public LoginPage errorShouldHaveText(String text) {
        error.shouldHave(text(text));
        return this;
    }
}
```

## Collection Assertions

```java
@Test
void testProductList() {
    open("/products");
    $$(".product-card")
        .shouldHave(size(10))
        .filter(text("Sale"))
        .shouldHave(sizeGreaterThan(0));

    $$(".product-card").first().shouldHave(text("Widget"));
    $$(".product-card").last().$(".price").shouldHave(text("$"));

    // Snapshot for later comparison
    ElementsCollection products = $$(".product-card").snapshot();
    $(".sort-by-price").click();
    $$(".product-card").shouldNotBe(texts(products.texts()));
}
```

## File Operations & Downloads

```java
@Test
void testFileDownload() {
    File report = $("a.download-report").download();
    assertThat(report.getName()).endsWith(".pdf");
    assertThat(report.length()).isGreaterThan(0);
}

@Test
void testFileUpload() {
    $("input[type='file']").uploadFile(new File("test-data/document.pdf"));
    $(".upload-success").shouldBe(visible);
}
```

## Custom Conditions

```java
public class CustomConditions {
    public static Condition cssValue(String prop, String expected) {
        return new Condition("css " + prop + "=" + expected) {
            @Override
            public boolean apply(Driver driver, WebElement element) {
                return element.getCssValue(prop).equals(expected);
            }
        };
    }
}

// Usage
$(".highlight").shouldHave(cssValue("background-color", "rgba(255, 255, 0, 1)"));
```

## Configuration

```java
// src/test/java/BaseTest.java
@BeforeAll
static void setup() {
    Configuration.browser = "chrome";
    Configuration.baseUrl = "http://localhost:3000";
    Configuration.timeout = 10_000;
    Configuration.pageLoadTimeout = 30_000;
    Configuration.screenshots = true;
    Configuration.savePageSource = false;
    Configuration.reportsFolder = "build/reports/selenide";
    Configuration.headless = Boolean.parseBoolean(System.getenv("CI"));
}
```

## Anti-Patterns

- ❌ `Thread.sleep()` — Selenide auto-waits; use `shouldBe(visible)` conditions
- ❌ `Selenide.sleep(ms)` in production tests — indicates missing conditions
- ❌ `$(By.xpath("//div[@class='...']"))` — prefer `$(".class")` CSS selectors
- ❌ Ignoring collection size — always assert expected count before iterating
