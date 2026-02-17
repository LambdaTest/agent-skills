# Selenium → Puppeteer Migration

## API Mapping

### Locators

| Selenium (Java/JS) | Puppeteer |
|--------------------|-----------|
| `By.id("x")` | `await page.$('#x')` or `page.$('#x')` (returns ElementHandle) |
| `By.cssSelector(".cls")` | `await page.$('.cls')` |
| `By.xpath("//button")` | `await page.$('xpath///button')` or use CSS equivalent |
| `driver.findElement(By.id("x"))` | `await page.$('#x')` (then use handle for actions) |
| `driver.findElements(By.cssSelector(".item"))` | `await page.$$('.item')` |

**Note:** Puppeteer uses CSS by default; for XPath use `page.$('xpath///...')`. Prefer `page.$` for single element, `page.$$` for array.

### Waits

| Selenium | Puppeteer |
|----------|-----------|
| `WebDriverWait` + `ExpectedConditions.visibilityOfElementLocated(...)` | `await page.waitForSelector('.selector', { visible: true, timeout: 10000 })` |
| `wait.until(ExpectedConditions.elementToBeClickable(...))` | `await page.waitForSelector('button', { visible: true }); await page.click('button');` |
| `Thread.sleep(ms)` | **Avoid.** Use `await page.waitForSelector(...)` or `await page.waitForFunction(...)` |
| Wait for navigation | `await Promise.all([page.waitForNavigation({ waitUntil: 'networkidle0' }), page.click('a')]);` |

### Actions

| Selenium | Puppeteer |
|----------|-----------|
| `element.sendKeys("text")` | `await page.type('#selector', 'text')` or `await element.type('text')` (deprecated: use `element.type` on handle) — prefer `await page.$('#x')` then `await (await page.$('#x')).type('text')` or `page.evaluate` for complex cases. For modern Puppeteer use `await page.evaluate(el => { el.value = 'text'; })` or `await (await page.$('#x')).type('text', { delay: 0 });` |
| `element.click()` | `await page.click('#selector')` or `await (await page.$('#selector')).click()` |
| `element.clear()` | `await page.evaluate(sel => { document.querySelector(sel).value = ''; }, '#x')` or type empty after select all |
| Select dropdown | `await page.select('#sel', 'value')` |
| Alert accept | `page.on('dialog', d => d.accept());` before triggering action |
| Switch to frame | `const frame = page.frames().find(f => f.name() === 'name');` then use `frame.$`, `frame.click`, etc. |

### Assertions

| Selenium | Puppeteer |
|----------|-----------|
| `driver.getTitle().contains("X")` | `const title = await page.title();` then assert in test (e.g. `expect(title).toContain('X')`) |
| `driver.getCurrentUrl().includes("/dashboard")` | `page.url()` or `page.url()` then assert |
| `element.getText()` | `await page.evaluate(el => el.textContent, await page.$('#x'))` or `await (await page.$('#x')).evaluate(el => el.textContent)` |

### Lifecycle

| Selenium | Puppeteer |
|----------|-----------|
| `WebDriver driver = new ChromeDriver();` | `const browser = await puppeteer.launch(); const page = await browser.newPage();` |
| `driver.get("https://...")` | `await page.goto('https://...', { waitUntil: 'networkidle0' });` |
| `driver.quit()` | `await browser.close();` |
| `driver.manage().window().maximize()` | `await page.setViewport({ width: 1920, height: 1080 });` |

## Before / After Snippets

**Selenium (Java):**
```java
driver.get("https://example.com/login");
wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username"))).sendKeys("user@test.com");
driver.findElement(By.id("password")).sendKeys("secret");
driver.findElement(By.cssSelector("button[type='submit']")).click();
```

**Puppeteer (JavaScript):**
```javascript
await page.goto('https://example.com/login', { waitUntil: 'networkidle0' });
await page.type('#username', 'user@test.com');
await page.type('#password', 'secret');
await page.click('button[type="submit"]');
await page.waitForNavigation({ waitUntil: 'networkidle0' });
```

## Lifecycle / Setup

- **Selenium:** One WebDriver per test; teardown with `driver.quit()`.
- **Puppeteer:** `puppeteer.launch()` once (or per test); create `page` with `browser.newPage()`. Always `browser.close()` in finally/teardown. Typically no test runner; wrap in async IIFE or use Mocha/Jest with async tests.

## Cloud (TestMu)

- Selenium on TestMu: RemoteWebDriver + hub + capabilities.
- Puppeteer on TestMu: Connect via WebSocket endpoint (LambdaTest Puppeteer integration). See [puppeteer-automation-skill/reference/cloud-integration.md](../../puppeteer-automation-skill/reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Gotchas

1. **Chrome/Chromium only:** Puppeteer does not drive Firefox or Safari; migration implies Chrome-only.
2. **Language:** Selenium may be Java/Python/C#; Puppeteer is JS/TS only. Migration usually means rewriting to JavaScript/TypeScript.
3. **No auto-wait:** Unlike Playwright, Puppeteer does not auto-wait. Use `waitForSelector`, `waitForNavigation`, or `waitForFunction` explicitly.
4. **page.type vs fill:** `page.type()` sends key events; for clearing + typing use `page.evaluate` to set value or type with delay. Newer patterns prefer `page.evaluate` for large text or `elementHandle.type()`.
5. **ElementHandle can go stale:** After navigation or DOM change, re-query with `page.$()`; do not reuse old handles.
