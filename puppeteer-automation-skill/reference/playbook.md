# Puppeteer — Advanced Implementation Playbook

## §1 — Production Setup & Configuration

```typescript
// puppeteer.config.ts
import puppeteer, { Browser, Page, LaunchOptions } from 'puppeteer';

const defaultLaunchOptions: LaunchOptions = {
  headless: process.env.CI ? 'new' : false,
  args: [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--window-size=1920,1080',
    '--force-device-scale-factor=1',
  ],
  defaultViewport: { width: 1920, height: 1080 },
  slowMo: parseInt(process.env.SLOW_MO || '0'),
  timeout: 30000,
};

export async function createBrowser(overrides: Partial<LaunchOptions> = {}): Promise<Browser> {
  return puppeteer.launch({ ...defaultLaunchOptions, ...overrides });
}

export async function createPage(browser: Browser): Promise<Page> {
  const page = await browser.newPage();

  // Console & error logging
  page.on('console', msg => {
    if (msg.type() === 'error') console.error('[PAGE ERROR]', msg.text());
  });
  page.on('pageerror', err => console.error('[UNCAUGHT]', err.message));
  page.on('requestfailed', req =>
    console.error('[REQUEST FAILED]', req.url(), req.failure()?.errorText));

  // Default timeouts
  await page.setDefaultNavigationTimeout(30000);
  await page.setDefaultTimeout(15000);

  // Block unnecessary resources in CI
  if (process.env.CI) {
    await page.setRequestInterception(true);
    page.on('request', req => {
      const type = req.resourceType();
      if (['image', 'font', 'media'].includes(type)) req.abort();
      else req.continue();
    });
  }

  return page;
}
```

### Jest + Puppeteer Integration

```javascript
// jest-puppeteer.config.js
module.exports = {
  launch: {
    headless: process.env.CI ? 'new' : false,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1920, height: 1080 },
  },
  server: {
    command: 'npm start',
    port: 3000,
    launchTimeout: 30000,
    debug: true,
  },
};

// jest.config.js
module.exports = {
  preset: 'jest-puppeteer',
  testMatch: ['**/tests/**/*.test.ts'],
  transform: { '^.+\\.tsx?$': 'ts-jest' },
  testTimeout: 60000,
};
```

## §2 — Page Object Pattern

```typescript
class BasePage {
  constructor(protected page: Page) {}

  async goto(path: string) {
    await this.page.goto(`${process.env.BASE_URL || 'http://localhost:3000'}${path}`, {
      waitUntil: 'networkidle0',
    });
  }

  async waitAndClick(selector: string) {
    await this.page.waitForSelector(selector, { visible: true });
    await this.page.click(selector);
  }

  async waitAndType(selector: string, text: string) {
    await this.page.waitForSelector(selector, { visible: true });
    await this.page.click(selector, { clickCount: 3 });  // select all
    await this.page.type(selector, text);
  }

  async getText(selector: string): Promise<string> {
    await this.page.waitForSelector(selector);
    return this.page.$eval(selector, el => el.textContent?.trim() || '');
  }

  async isVisible(selector: string): Promise<boolean> {
    try {
      await this.page.waitForSelector(selector, { visible: true, timeout: 3000 });
      return true;
    } catch { return false; }
  }

  async screenshot(name: string) {
    await this.page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
  }

  async waitForNetworkIdle() {
    await this.page.waitForNetworkIdle({ idleTime: 500, timeout: 15000 });
  }
}

class LoginPage extends BasePage {
  async open() { await this.goto('/login'); }

  async login(email: string, password: string) {
    await this.waitAndType('[data-testid="email"]', email);
    await this.waitAndType('[data-testid="password"]', password);
    await this.waitAndClick('[data-testid="submit"]');
    await this.page.waitForNavigation({ waitUntil: 'networkidle0' });
    return new DashboardPage(this.page);
  }

  async getError(): Promise<string> {
    return this.getText('.error-message');
  }
}

class DashboardPage extends BasePage {
  async isLoaded(): Promise<boolean> {
    return this.isVisible('[data-testid="dashboard"]');
  }

  async getWelcomeText(): Promise<string> {
    return this.getText('[data-testid="welcome-msg"]');
  }
}
```

## §3 — Network Interception & Mocking

```typescript
// Full request interception
async function setupMocks(page: Page) {
  await page.setRequestInterception(true);

  const mocks: Map<string, any> = new Map([
    ['/api/products', { status: 200, data: [{ id: 1, name: 'Mock Product' }] }],
    ['/api/user', { status: 200, data: { name: 'Test User', role: 'admin' } }],
  ]);

  page.on('request', req => {
    const mockEntry = [...mocks.entries()].find(([url]) => req.url().includes(url));
    if (mockEntry) {
      req.respond({
        status: mockEntry[1].status,
        contentType: 'application/json',
        body: JSON.stringify(mockEntry[1].data),
      });
    } else if (req.resourceType() === 'image') {
      req.abort();
    } else {
      req.continue();
    }
  });
}

// Capture API responses
async function captureApiResponse(page: Page, urlPattern: string): Promise<any> {
  const response = await page.waitForResponse(
    r => r.url().includes(urlPattern) && r.status() === 200
  );
  return response.json();
}

// Block specific domains
page.on('request', req => {
  const blockedDomains = ['analytics.google.com', 'ads.example.com', 'tracking.io'];
  if (blockedDomains.some(d => req.url().includes(d))) req.abort();
  else req.continue();
});
```

## §4 — Wait Strategies

```typescript
// Wait for DOM element
await page.waitForSelector('.loaded', { visible: true, timeout: 15000 });

// Wait for element to disappear
await page.waitForSelector('.loading-spinner', { hidden: true });

// Wait for custom condition
await page.waitForFunction(
  () => document.querySelectorAll('.item').length > 5,
  { timeout: 10000 }
);

// Wait for network idle after action
await Promise.all([
  page.waitForNetworkIdle({ idleTime: 500 }),
  page.click('#load-more'),
]);

// Wait for navigation after click
await Promise.all([
  page.waitForNavigation({ waitUntil: 'networkidle0' }),
  page.click('a.next-page'),
]);

// Wait for specific API response
const [response] = await Promise.all([
  page.waitForResponse(r => r.url().includes('/api/data') && r.status() === 200),
  page.click('#fetch-data'),
]);
const data = await response.json();

// Wait for frame
const frame = await page.waitForFrame(f => f.url().includes('payment'));

// Retry with polling
async function waitForCondition(page: Page, fn: () => Promise<boolean>, timeout = 10000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    if (await fn()) return;
    await new Promise(r => setTimeout(r, 250));
  }
  throw new Error('Condition not met within timeout');
}
```

## §5 — Screenshots, PDF & Media

```typescript
// Full page screenshot
await page.screenshot({ path: 'full.png', fullPage: true });

// Element screenshot
const element = await page.$('[data-testid="chart"]');
await element?.screenshot({ path: 'chart.png' });

// Clip region
await page.screenshot({
  path: 'region.png',
  clip: { x: 0, y: 0, width: 800, height: 600 },
});

// PDF generation
await page.pdf({
  path: 'report.pdf',
  format: 'A4',
  printBackground: true,
  margin: { top: '1cm', bottom: '1cm', left: '1cm', right: '1cm' },
  displayHeaderFooter: true,
  headerTemplate: '<span style="font-size:10px">Report</span>',
  footerTemplate: '<span style="font-size:10px">Page <span class="pageNumber"></span>/<span class="totalPages"></span></span>',
});

// Video recording (via screen capture)
const recorder = await page.screencast({ path: 'recording.webm' });
// ... run test actions ...
await recorder.stop();

// Emulate devices
const iPhone = puppeteer.KnownDevices['iPhone 15'];
await page.emulate(iPhone);
```

## §6 — Authentication & Cookies

```typescript
// Cookie-based auth
async function loginViaApi(page: Page, email: string, password: string) {
  const response = await fetch(`${BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const { token } = await response.json();

  await page.setCookie({
    name: 'auth_token',
    value: token,
    domain: 'localhost',
    path: '/',
    httpOnly: true,
    secure: false,
  });
}

// Save and restore session
async function saveSession(page: Page, path: string) {
  const cookies = await page.cookies();
  const localStorage = await page.evaluate(() => JSON.stringify(window.localStorage));
  fs.writeFileSync(path, JSON.stringify({ cookies, localStorage }));
}

async function restoreSession(page: Page, path: string) {
  const { cookies, localStorage } = JSON.parse(fs.readFileSync(path, 'utf8'));
  await page.setCookie(...cookies);
  await page.evaluate(data => {
    Object.entries(JSON.parse(data)).forEach(([k, v]) =>
      window.localStorage.setItem(k, v as string));
  }, localStorage);
}
```

## §7 — iFrame, Dialog & File Operations

```typescript
// iFrame interaction
const frameElement = await page.waitForSelector('iframe#payment');
const frame = await frameElement?.contentFrame();
if (frame) {
  await frame.type('#card-number', '4111111111111111');
  await frame.type('#expiry', '12/28');
  await frame.click('#pay-btn');
}

// Dialog handling (alert, confirm, prompt)
page.on('dialog', async dialog => {
  console.log('Dialog:', dialog.type(), dialog.message());
  if (dialog.type() === 'confirm') await dialog.accept();
  else if (dialog.type() === 'prompt') await dialog.accept('user input');
  else await dialog.dismiss();
});

// File upload
const [fileChooser] = await Promise.all([
  page.waitForFileChooser(),
  page.click('#upload-btn'),
]);
await fileChooser.accept(['./fixtures/test.pdf']);

// File download
const client = await page.target().createCDPSession();
await client.send('Page.setDownloadBehavior', {
  behavior: 'allow',
  downloadPath: './downloads',
});
await page.click('#download-btn');
```

## §8 — Performance & Metrics

```typescript
// Core Web Vitals
const metrics = await page.metrics();
console.log('JSHeapUsed:', metrics.JSHeapUsedSize);

const timing = await page.evaluate(() => {
  const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  return {
    domContentLoaded: nav.domContentLoadedEventEnd - nav.startTime,
    load: nav.loadEventEnd - nav.startTime,
    ttfb: nav.responseStart - nav.requestStart,
    fcp: performance.getEntriesByName('first-contentful-paint')[0]?.startTime,
  };
});

// Lighthouse via puppeteer
const { startFlow } = require('lighthouse');
const flow = await startFlow(page, { name: 'User Flow' });
await flow.navigate(url);
await flow.snapshot({ stepName: 'Homepage loaded' });
const report = await flow.generateReport();

// Coverage (CSS/JS)
await page.coverage.startCSSCoverage();
await page.coverage.startJSCoverage();
await page.goto(url);
const [cssCoverage, jsCoverage] = await Promise.all([
  page.coverage.stopCSSCoverage(),
  page.coverage.stopJSCoverage(),
]);
const unusedCSS = cssCoverage.reduce((acc, entry) => {
  const unused = entry.ranges.reduce((s, r) => s + r.end - r.start, 0);
  return acc + (entry.text.length - unused);
}, 0);
```

## §9 — Accessibility Testing

```typescript
import { AxePuppeteer } from '@axe-core/puppeteer';

it('should have no accessibility violations', async () => {
  await page.goto('/');
  const results = await new AxePuppeteer(page)
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze();
  expect(results.violations).toEqual([]);
});
```

## §10 — CI/CD Integration

```yaml
# GitHub Actions
name: Puppeteer Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx jest --runInBand
        env: { CI: true, BASE_URL: 'http://localhost:3000' }
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: screenshots
          path: screenshots/
```

```yaml
# Docker for consistent environment
FROM node:20-slim
RUN apt-get update && apt-get install -y chromium
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npx", "jest", "--runInBand"]
```

## §11 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| `page.click()` fails | Element hidden or overlapped | Use JS click: `page.evaluate(el => el.click(), elem)` |
| Navigation timeout | SPA doesn't trigger navigation | Use `waitForSelector` instead of `waitForNavigation` |
| Element not found | DOM not ready | `await page.waitForSelector()` before interaction |
| Memory leak | Unclosed pages or browsers | Close pages: `page.close()`, browser: `browser.close()` |
| Headless rendering differs | Missing GPU/fonts | Use `--force-device-scale-factor=1`, fixed viewport |
| Request interception errors | Multiple handlers conflict | Use single interception handler with routing |
| iFrame content not accessible | Wrong frame reference | Use `frame.waitForSelector()`, not `page.waitForSelector()` |
| File upload fails | No file chooser triggered | Use `page.waitForFileChooser()` before click |
| Dialog not handled | Event listener not set | Register `page.on('dialog')` before triggering action |
| Slow in CI | Resource loading | Block images/fonts, use `networkidle0` |
| Screenshot blank | Page not loaded | Wait for `networkidle0` or specific selector |

## §12 — Best Practices Checklist

- ✅ Always close browser in `finally` or `afterAll` block
- ✅ Use `page.waitForNetworkIdle()` over arbitrary `setTimeout`
- ✅ Use `page.setRequestInterception()` to mock APIs and block resources
- ✅ Set `defaultViewport` for consistent screenshots
- ✅ Limit concurrent pages to control memory
- ✅ Use `page.on('console')` and `page.on('pageerror')` for error capture
- ✅ Use Page Object pattern for maintainable tests
- ✅ Use `Promise.all([waitFor..., click()])` for navigation + action
- ✅ Save/restore cookies for faster auth across tests
- ✅ Use `data-testid` attributes for stable selectors
- ✅ Run headless in CI with `headless: 'new'`
- ✅ Use `@axe-core/puppeteer` for accessibility testing
- ✅ Structure: `tests/`, `pages/`, `fixtures/`, `helpers/`, `screenshots/`
