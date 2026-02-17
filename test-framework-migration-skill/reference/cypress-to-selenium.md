# Cypress → Selenium Migration

## API Mapping

### Locators

| Cypress | Selenium (Java example) |
|---------|-------------------------|
| `cy.get('#x')` | `By.id("x")` or `By.cssSelector("#x")` |
| `cy.get('[data-cy="btn"]')` | `By.cssSelector("[data-cy='btn']")` |
| `cy.get('[data-testid="btn"]')` | `By.cssSelector("[data-testid='btn']")` |
| `cy.contains('Submit')` | `By.xpath("//*[contains(text(),'Submit')]")` or more specific |
| `cy.contains('button', 'Submit')` | `By.xpath("//button[contains(.,'Submit')]")` |
| `cy.get('.cls')` | `By.cssSelector(".cls")` |

**Selenium:** Use explicit wait before every find. Store `By` locators, not WebElement, to avoid stale references.

### Waits / Assertions

| Cypress | Selenium |
|---------|----------|
| `cy.get(sel).should('be.visible')` | `WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10)); wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(sel)));` |
| `cy.get(sel).should('have.text', 'x')` | Wait for visible, then `Assertions.assertEquals("x", driver.findElement(By.cssSelector(sel)).getText());` |
| `cy.url().should('include', '/dashboard')` | `wait.until(ExpectedConditions.urlContains("/dashboard"));` |
| `cy.title().should('include', 'X')` | `wait.until(ExpectedConditions.titleContains("X"));` or getTitle() and assert |
| Cypress retry-ability | Selenium has no retry; always use WebDriverWait before get + action/assert. |

### Actions

| Cypress | Selenium |
|---------|----------|
| `cy.visit('/login')` | `driver.get(baseURL + "/login");` |
| `cy.get(sel).type('text')` | `WebElement el = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(sel))); el.clear(); el.sendKeys("text");` |
| `cy.get(sel).click()` | `wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(sel))).click();` |
| `cy.get('#sel').select('value')` | `new Select(driver.findElement(By.id("sel"))).selectByValue("value");` |
| `cy.intercept(...)` | No direct equivalent; use driver for network only if needed (e.g. DevTools). For mocking, consider test double at app/network layer. |
| `cy.request('POST', url, body)` | Use HttpClient/OkHttp in Java, or JS fetch in Node, outside Selenium. |

### Lifecycle

| Cypress | Selenium |
|---------|----------|
| `beforeEach(() => cy.visit('/'))` | `@BeforeEach` create driver and optionally `driver.get(baseURL);` |
| No explicit close | `@AfterEach` call `driver.quit();` |
| Viewport in config or `cy.viewport()` | `driver.manage().window().setSize(...)` or `maximize()` |

## Before / After Snippets

**Cypress (JavaScript):**
```javascript
cy.visit('/login');
cy.get('[data-cy="email"]').type('user@test.com');
cy.get('[data-cy="password"]').type('secret');
cy.get('button[type="submit"]').click();
cy.url().should('include', '/dashboard');
```

**Selenium (Java):**
```java
driver.get(baseURL + "/login");
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector("[data-cy='email']"))).sendKeys("user@test.com");
driver.findElement(By.cssSelector("[data-cy='password']")).sendKeys("secret");
wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("button[type='submit']"))).click();
wait.until(ExpectedConditions.urlContains("/dashboard"));
```

## Lifecycle / Setup

- **Cypress:** No driver; cy commands queued. Config in cypress.config.js.
- **Selenium:** Create WebDriver in setup, quit in teardown. Use WebDriverWait for every interaction that depends on DOM/visibility. Choose language (Java, Python, JS, C#) and test runner (JUnit, pytest, Mocha, NUnit).

## Cloud (TestMu)

- Cypress: LambdaTest Cypress CLI.
- Selenium: RemoteWebDriver + hub + DesiredCapabilities / LT:Options. See [selenium-automation-skill/reference/cloud-integration.md](../../selenium-automation-skill/reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Gotchas

1. **Explicit waits required:** Cypress retries; Selenium does not. Add WebDriverWait + ExpectedConditions before every findElement + action or assertion.
2. **No cy.intercept in Selenium:** Network mocking is not built into Selenium. Use application-level mocks or test against a mocked backend.
3. **cy.request:** In Selenium you typically do API calls via the same language's HTTP client (e.g. Java HttpClient) if needed; not part of WebDriver.
4. **Language:** Cypress is JS/TS; Selenium supports Java, Python, C#, etc. Pick target language and convert syntax and lifecycle (e.g. JUnit @BeforeEach/@AfterEach).
5. **Stale elements:** Do not hold WebElement across navigations or DOM updates; re-find using By locators after wait.
