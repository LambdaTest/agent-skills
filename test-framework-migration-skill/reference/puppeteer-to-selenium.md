# Puppeteer → Selenium Migration

## API Mapping

### Locators

| Puppeteer | Selenium (Java/JS) |
|-----------|--------------------|
| `await page.$('#x')` | `driver.findElement(By.id("x"))` or `By.cssSelector("#x")` |
| `await page.$$('.item')` | `driver.findElements(By.cssSelector(".item"))` |
| `page.$('xpath///button')` | `By.xpath("//button")` |
| `page.$('.cls')` | `By.cssSelector(".cls")` |

**Selenium:** No ElementHandle; you get WebElement. Use explicit wait before find: `wait.until(ExpectedConditions.presenceOfElementLocated(By.id("x")));`

### Waits

| Puppeteer | Selenium |
|-----------|----------|
| `await page.waitForSelector('.sel', { visible: true })` | `WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10)); wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".sel")));` |
| `await page.waitForNavigation({ waitUntil: 'networkidle0' })` | After click: wait for URL or specific element (e.g. `ExpectedConditions.urlContains("/dashboard")`) |
| `await page.waitForFunction('document.readyState === "complete"')` | Usually implicit after `driver.get()`; for SPA use wait for element |
| `await page.waitForResponse(resp => resp.url().includes('/api'))` | No direct equivalent; use explicit wait for element that appears after API call |

### Actions

| Puppeteer | Selenium |
|-----------|----------|
| `await page.type('#x', 'text')` | `WebElement el = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("x"))); el.clear(); el.sendKeys("text");` |
| `await page.click('#btn')` | `wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("#btn"))).click();` |
| `await page.select('#sel', 'value')` | `new Select(driver.findElement(By.id("sel"))).selectByValue("value");` |
| `page.on('dialog', d => d.accept())` | After action that opens alert: `driver.switchTo().alert().accept();` (with wait if needed) |
| Frame: `page.frames()` / `frame.$()` | `driver.switchTo().frame("frameName");` then find elements on driver |
| `await page.setViewport({ width, height })` | `driver.manage().window().setSize(new Dimension(width, height));` |

### Assertions

| Puppeteer | Selenium |
|-----------|----------|
| `const title = await page.title(); expect(title).toContain('X')` | `Assertions.assertTrue(driver.getTitle().contains("X"));` |
| `page.url()` | `driver.getCurrentUrl()` |
| `await (await page.$('#x')).evaluate(el => el.textContent)` | `wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("x"))).getText();` |

### Lifecycle

| Puppeteer | Selenium |
|-----------|----------|
| `const browser = await puppeteer.launch(); const page = await browser.newPage();` | `WebDriver driver = new ChromeDriver();` |
| `await page.goto(url)` | `driver.get(url);` |
| `await browser.close()` | `driver.quit();` |
| `await page.setViewport({ width, height })` | `driver.manage().window().setSize(...)` or `maximize()` |

## Before / After Snippets

**Puppeteer (JavaScript):**
```javascript
await page.goto('https://example.com/login', { waitUntil: 'networkidle0' });
await page.type('#username', 'user@test.com');
await page.type('#password', 'secret');
await page.click('button[type="submit"]');
await page.waitForNavigation({ waitUntil: 'networkidle0' });
expect(await page.title()).toContain('Dashboard');
```

**Selenium (Java):**
```java
driver.get("https://example.com/login");
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username"))).sendKeys("user@test.com");
driver.findElement(By.id("password")).sendKeys("secret");
wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("button[type='submit']"))).click();
wait.until(ExpectedConditions.urlContains("/dashboard"));
Assertions.assertTrue(driver.getTitle().contains("Dashboard"));
```

## Lifecycle / Setup

- **Puppeteer:** Launch browser, newPage(), run test, browser.close(). Often Mocha/Jest with async.
- **Selenium:** Create WebDriver in @BeforeEach, quit() in @AfterEach. Use WebDriverWait for every interaction that depends on DOM/network; never Thread.sleep.

## Cloud (TestMu)

- Puppeteer: connect via LambdaTest WebSocket (see puppeteer-automation-skill/reference/cloud-integration.md).
- Selenium: RemoteWebDriver + hub + DesiredCapabilities / LT:Options. See [selenium-automation-skill/reference/cloud-integration.md](../../selenium-automation-skill/reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Gotchas

1. **Explicit waits required:** Puppeteer has waitForSelector; Selenium has no auto-wait. Always use WebDriverWait + ExpectedConditions before find + action.
2. **Chrome-only → multi-browser:** Migrating to Selenium allows Firefox, Edge, Safari via different drivers/capabilities.
3. **Language:** Puppeteer is JS/TS only. Selenium supports Java, Python, C#; choose target language and convert control flow and assertions.
4. **Stale handles vs stale elements:** In Puppeteer, ElementHandles can go stale; in Selenium, WebElements can go stale. Prefer storing By locators and re-finding after waits.
5. **Network idle:** Puppeteer's `waitUntil: 'networkidle0'` has no direct Selenium equivalent; use URL or element visibility waits instead.
