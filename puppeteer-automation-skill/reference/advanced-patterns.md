# Puppeteer — Advanced Patterns & Playbook

## Page Object Pattern

```javascript
class LoginPage {
  constructor(page) { this.page = page; }

  async navigate() { await this.page.goto('/login', { waitUntil: 'networkidle0' }); }

  async login(email, password) {
    await this.page.type('#email', email);
    await this.page.type('#password', password);
    await Promise.all([
      this.page.waitForNavigation({ waitUntil: 'networkidle0' }),
      this.page.click('#submit')
    ]);
  }

  async getError() {
    await this.page.waitForSelector('.error', { visible: true });
    return this.page.$eval('.error', el => el.textContent);
  }
}
```

## Network Interception

```javascript
// Mock API responses
await page.setRequestInterception(true);
page.on('request', request => {
  if (request.url().includes('/api/users')) {
    request.respond({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 1, name: 'Alice' }])
    });
  } else {
    request.continue();
  }
});

// Log network requests
const requests = [];
page.on('request', req => requests.push({ url: req.url(), method: req.method() }));
page.on('response', res => {
  const match = requests.find(r => r.url === res.url());
  if (match) match.status = res.status();
});
```

## Performance & Tracing

```javascript
// Performance metrics
await page.goto(url);
const metrics = await page.metrics();
console.log(`JS Heap: ${(metrics.JSHeapUsedSize / 1024 / 1024).toFixed(1)} MB`);
console.log(`DOM Nodes: ${metrics.Nodes}`);

// Chrome DevTools Protocol tracing
await page.tracing.start({ path: 'trace.json', categories: ['devtools.timeline'] });
await page.goto(url);
await page.tracing.stop();

// Coverage
await page.coverage.startJSCoverage();
await page.goto(url);
const coverage = await page.coverage.stopJSCoverage();
const usedBytes = coverage.reduce((acc, entry) => {
  return acc + entry.ranges.reduce((sum, range) => sum + range.end - range.start, 0);
}, 0);
```

## PDF & Screenshot Generation

```javascript
// Full page screenshot
await page.screenshot({ path: 'full-page.png', fullPage: true });

// Element screenshot
const element = await page.$('.hero-section');
await element.screenshot({ path: 'hero.png' });

// PDF generation
await page.pdf({
  path: 'report.pdf', format: 'A4',
  margin: { top: '1cm', bottom: '1cm' },
  printBackground: true
});
```

## Anti-Patterns

- ❌ `page.waitForTimeout(5000)` — use `waitForSelector`, `waitForNavigation`, or `waitForFunction`
- ❌ `page.click()` without waiting for navigation — use `Promise.all([waitForNav, click])`
- ❌ Forgetting `await` on async operations — leads to race conditions
- ❌ Not closing browser in `afterAll` — memory leaks in test suites
- ❌ `page.evaluate()` for simple text checks — use `page.$eval` or `page.textContent`
