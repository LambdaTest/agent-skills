# Selenium → Cypress Migration

## API Mapping

### Locators

| Selenium (Java/JS) | Cypress |
|--------------------|---------|
| `By.id("x")` | `cy.get('#x')` |
| `By.cssSelector(".cls")` | `cy.get('.cls')` |
| `By.xpath("//button[text()='Submit']")` | `cy.contains('button', 'Submit')` or `cy.get('button').contains('Submit')` |
| `By.name("q")` | `cy.get('input[name="q"]')` |
| `driver.findElement(By.id("x"))` | `cy.get('#x')` (then chain .click(), .type(), .should()) |

**Cypress:** Prefer `data-cy` or `data-testid`; use `cy.get('[data-cy="x"]')`. No By objects; use selector strings.

### Waits

| Selenium | Cypress |
|----------|---------|
| `WebDriverWait` + `ExpectedConditions.visibilityOfElementLocated(...)` | Not needed; `cy.get(selector).should('be.visible')` or just `cy.get(selector).click()` (Cypress retries) |
| `Thread.sleep(ms)` | **Avoid.** Use `cy.get(...).should(...)` or `cy.wait(alias)` for intercepts |
| Wait for URL | `wait.until(ExpectedConditions.urlContains("/dashboard"))` → `cy.url().should('include', '/dashboard')` |

### Actions

| Selenium | Cypress |
|----------|---------|
| `element.sendKeys("text")` | `cy.get(selector).type('text')` |
| `element.clear()` | `cy.get(selector).clear()` |
| `element.click()` | `cy.get(selector).click()` |
| `new Select(...).selectByValue("v")` | `cy.get('#sel').select('v')` |
| `driver.switchTo().alert().accept()` | `cy.on('window:confirm', () => true)` or stub before action |
| `driver.get(url)` | `cy.visit(url)` or `cy.visit('/path')` with baseURL |

### Assertions

| Selenium | Cypress |
|----------|---------|
| `Assertions.assertTrue(driver.getTitle().contains("X"))` | `cy.title().should('include', 'X')` |
| `Assertions.assertTrue(driver.getCurrentUrl().contains("/dashboard"))` | `cy.url().should('include', '/dashboard')` |
| `Assertions.assertEquals("text", element.getText())` | `cy.get(selector).should('have.text', 'text')` |
| `element.isDisplayed()` | `cy.get(selector).should('be.visible')` |

### Lifecycle

| Selenium | Cypress |
|----------|---------|
| `WebDriver driver = new ChromeDriver();` | No driver in test; Cypress provides `cy` |
| `@BeforeEach` create driver | `beforeEach(() => { cy.visit('/'); });` or similar |
| `driver.quit()` in @AfterEach | No teardown; Cypress manages browser |
| `driver.manage().window().maximize()` | Viewport in cypress.config.js or `cy.viewport(width, height)` |

## Before / After Snippets

**Selenium (Java):**
```java
driver.get("https://example.com/login");
wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username"))).sendKeys("user@test.com");
driver.findElement(By.id("password")).sendKeys("secret");
driver.findElement(By.cssSelector("button[type='submit']")).click();
wait.until(ExpectedConditions.urlContains("/dashboard"));
```

**Cypress (JavaScript):**
```javascript
cy.visit('https://example.com/login');
cy.get('#username').type('user@test.com');
cy.get('#password').type('secret');
cy.get('button[type="submit"]').click();
cy.url().should('include', '/dashboard');
```

## Lifecycle / Setup

- **Selenium:** Create WebDriver, run test, quit. Often JUnit/TestNG with @BeforeEach/@AfterEach.
- **Cypress:** No driver creation; use `cy.visit()`, `cy.get()`, etc. in tests. Config in cypress.config.js. Tests are written without async/await (Cypress queues commands).

## Cloud (TestMu)

- Selenium: RemoteWebDriver + hub + capabilities.
- Cypress: LambdaTest Cypress CLI. See [cypress-skill/reference/cloud-integration.md](../../cypress-skill/reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Gotchas

1. **Language:** Selenium may be Java/Python/C#; Cypress is JS/TS only. Migration means rewriting to JavaScript/TypeScript.
2. **No async/await with cy:** Do not use async/await with Cypress commands. Write linear cy chains.
3. **Do not store cy.get() result for later:** Commands are queued and run asynchronously; chain or repeat cy.get() in the same flow.
4. **Explicit waits → retry-ability:** Replace WebDriverWait with Cypress .should(); Cypress automatically retries assertions and get until timeout.
5. **Multiple tabs/windows:** Cypress does not support multiple tabs. If Selenium tests switch windows, consolidate to single tab or document the limitation.
