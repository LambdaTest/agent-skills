# WebdriverIO — Advanced Implementation Playbook

## §1 — Production Configuration

```javascript
// wdio.conf.ts
import { join } from 'path';

export const config: WebdriverIO.Config = {
  runner: 'local',
  specs: ['./test/specs/**/*.spec.ts'],
  suites: {
    smoke: ['./test/specs/smoke/**/*.spec.ts'],
    regression: ['./test/specs/regression/**/*.spec.ts'],
    api: ['./test/specs/api/**/*.spec.ts'],
  },
  exclude: ['./test/specs/wip/**'],
  maxInstances: parseInt(process.env.MAX_INSTANCES || '5'),
  capabilities: [{
    browserName: 'chrome',
    'goog:chromeOptions': {
      args: process.env.CI
        ? ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        : [],
    },
  }],
  logLevel: 'warn',
  bail: process.env.CI ? 1 : 0,
  baseUrl: process.env.BASE_URL || 'http://localhost:3000',
  waitforTimeout: 10000,
  connectionRetryTimeout: 120000,
  connectionRetryCount: 3,
  framework: 'mocha',
  reporters: [
    'spec',
    ['allure', {
      outputDir: 'allure-results',
      disableWebdriverStepsReporting: true,
      disableWebdriverScreenshotsReporting: false,
    }],
    ['junit', { outputDir: 'test-results', outputFileFormat: (opts) => `results-${opts.cid}.xml` }],
  ],
  mochaOpts: { ui: 'bdd', timeout: 60000, retries: process.env.CI ? 1 : 0 },

  beforeSession(config, capabilities) {
    // Dynamic capability overrides
  },

  before(capabilities, specs) {
    // Custom commands registration
    browser.addCommand('loginViaApi', async (email: string, password: string) => {
      const response = await browser.call(() =>
        fetch(`${config.baseUrl}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        }).then(r => r.json())
      );
      await browser.setCookies([{ name: 'token', value: response.token }]);
    });
  },

  afterTest: async function(test, context, { error, passed }) {
    if (error) {
      await browser.takeScreenshot();
    }
  },

  onComplete(exitCode, config, capabilities, results) {
    // Generate custom summary
  },
};
```

### Multi-Environment Config

```javascript
// wdio.ci.conf.ts — extends base
import { config as baseConfig } from './wdio.conf';

export const config = {
  ...baseConfig,
  maxInstances: 10,
  capabilities: [{
    browserName: 'chrome',
    'goog:chromeOptions': {
      args: ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage'],
    },
  }],
  bail: 1,
  logLevel: 'error',
};
```

### Multi-Browser Config

```javascript
// wdio.multi.conf.ts
export const config = {
  ...baseConfig,
  capabilities: [
    { browserName: 'chrome', 'goog:chromeOptions': { args: ['--headless=new'] } },
    { browserName: 'firefox', 'moz:firefoxOptions': { args: ['-headless'] } },
    { browserName: 'MicrosoftEdge' },
  ],
};
```

## §2 — Page Object Model

```typescript
// BasePage
export class BasePage {
  open(path: string) {
    return browser.url(path);
  }

  async waitForPageLoad() {
    await browser.waitUntil(
      async () => (await browser.execute(() => document.readyState)) === 'complete',
      { timeout: 30000, timeoutMsg: 'Page did not load within 30s' }
    );
  }

  async getTitle() { return browser.getTitle(); }

  async scrollToElement(selector: string) {
    const elem = await $(selector);
    await elem.scrollIntoView();
    return elem;
  }

  async waitAndClick(selector: string) {
    const elem = await $(selector);
    await elem.waitForClickable({ timeout: 10000 });
    await elem.click();
  }

  async waitAndType(selector: string, text: string) {
    const elem = await $(selector);
    await elem.waitForDisplayed({ timeout: 10000 });
    await elem.clearValue();
    await elem.setValue(text);
  }

  async selectDropdown(selector: string, value: string) {
    const elem = await $(selector);
    await elem.selectByVisibleText(value);
  }

  async isElementPresent(selector: string): Promise<boolean> {
    const elem = await $(selector);
    return elem.isExisting();
  }
}

// LoginPage
export class LoginPage extends BasePage {
  get emailInput() { return $('[data-testid="email"]'); }
  get passwordInput() { return $('[data-testid="password"]'); }
  get submitBtn() { return $('[data-testid="login-submit"]'); }
  get errorMsg() { return $('.error-message'); }
  get rememberMe() { return $('[data-testid="remember-me"]'); }

  async open() { return super.open('/login'); }

  async login(email: string, password: string) {
    await this.emailInput.waitForDisplayed();
    await this.emailInput.setValue(email);
    await this.passwordInput.setValue(password);
    await this.submitBtn.click();
    return new DashboardPage();
  }

  async loginWithRemember(email: string, password: string) {
    await this.emailInput.setValue(email);
    await this.passwordInput.setValue(password);
    await this.rememberMe.click();
    await this.submitBtn.click();
  }

  async getError(): Promise<string> {
    await this.errorMsg.waitForDisplayed({ timeout: 5000 });
    return this.errorMsg.getText();
  }

  async isLoginFormDisplayed(): Promise<boolean> {
    return this.emailInput.isDisplayed();
  }
}

// DashboardPage
export class DashboardPage extends BasePage {
  get welcomeMsg() { return $('[data-testid="welcome-msg"]'); }
  get navMenu() { return $('[data-testid="nav-menu"]'); }
  get logoutBtn() { return $('[data-testid="logout"]'); }

  async isLoaded(): Promise<boolean> {
    await this.welcomeMsg.waitForDisplayed({ timeout: 10000 });
    return true;
  }

  async getWelcomeText(): Promise<string> {
    return this.welcomeMsg.getText();
  }

  async navigateTo(section: string) {
    await this.navMenu.click();
    await $(`[data-testid="nav-${section}"]`).click();
  }
}
```

## §3 — Custom Commands

```typescript
// Type declarations
declare global {
  namespace WebdriverIO {
    interface Browser {
      loginViaApi(email: string, password: string): Promise<void>;
      waitForNetworkIdle(timeout?: number): Promise<void>;
      getLocalStorage(key: string): Promise<string>;
    }
    interface Element {
      clickWhenReady(): Promise<void>;
      safeType(text: string): Promise<void>;
    }
  }
}

// Browser commands
browser.addCommand('waitForNetworkIdle', async (timeout = 5000) => {
  await browser.waitUntil(
    async () => {
      const pending = await browser.execute(() =>
        (performance.getEntriesByType('resource') as any[])
          .filter(r => !r.responseEnd).length
      );
      return pending === 0;
    },
    { timeout, timeoutMsg: 'Network did not become idle' }
  );
});

browser.addCommand('getLocalStorage', async (key: string) => {
  return browser.execute((k) => localStorage.getItem(k), key);
});

// Element commands
browser.addCommand('clickWhenReady', async function(this: WebdriverIO.Element) {
  await this.waitForClickable({ timeout: 10000 });
  await this.click();
}, true);  // true = element command

browser.addCommand('safeType', async function(this: WebdriverIO.Element, text: string) {
  await this.waitForDisplayed({ timeout: 10000 });
  await this.clearValue();
  await this.setValue(text);
}, true);
```

## §4 — Network Mocking (DevTools Protocol)

```typescript
describe('Product Listing', () => {
  it('should display mocked products', async () => {
    const mock = await browser.mock('**/api/products', { method: 'get' });
    mock.respond([
      { id: 1, name: 'Product A', price: 29.99 },
      { id: 2, name: 'Product B', price: 49.99 },
    ], {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
    });

    await browser.url('/products');
    const items = await $$('.product-card');
    expect(items).toHaveLength(2);

    mock.restore();
  });

  it('should handle API errors gracefully', async () => {
    const mock = await browser.mock('**/api/products');
    mock.respond({ error: 'Internal Server Error' }, { statusCode: 500 });

    await browser.url('/products');
    await expect($('.error-banner')).toBeDisplayed();
    expect(await $('.error-banner').getText()).toContain('Something went wrong');
  });

  it('should abort slow requests', async () => {
    const mock = await browser.mock('**/api/slow-endpoint');
    mock.abort('Failed');

    await browser.url('/dashboard');
    await expect($('.timeout-message')).toBeDisplayed();
  });
});
```

## §5 — File Operations

```typescript
// File upload
it('should upload a file', async () => {
  const filePath = join(__dirname, '..', 'fixtures', 'test.pdf');
  const remoteFilePath = await browser.uploadFile(filePath);
  await $('input[type="file"]').setValue(remoteFilePath);
  await $('[data-testid="upload-btn"]').click();
  await expect($('.upload-success')).toBeDisplayed();
});

// File download
it('should download report', async () => {
  const downloadDir = join(__dirname, '..', 'downloads');
  // Configure in capabilities: 'goog:chromeOptions': { prefs: { 'download.default_directory': downloadDir } }
  await $('[data-testid="download-btn"]').click();
  await browser.waitUntil(
    async () => fs.existsSync(join(downloadDir, 'report.pdf')),
    { timeout: 15000, timeoutMsg: 'File not downloaded' }
  );
});

// Drag and drop
it('should reorder items via drag and drop', async () => {
  const source = await $('[data-testid="item-1"]');
  const target = await $('[data-testid="item-3"]');
  await source.dragAndDrop(target);
});
```

## §6 — Multi-Tab, iFrame & Shadow DOM

```typescript
// Multiple windows / tabs
it('should handle new tab', async () => {
  await $('a[target="_blank"]').click();
  const handles = await browser.getWindowHandles();
  await browser.switchToWindow(handles[1]);
  expect(await browser.getUrl()).toContain('/new-page');
  await browser.closeWindow();
  await browser.switchToWindow(handles[0]);
});

// iFrames
it('should interact inside iframe', async () => {
  const iframe = await $('iframe#payment-frame');
  await browser.switchToFrame(iframe);
  await $('[data-testid="card-number"]').setValue('4111111111111111');
  await browser.switchToFrame(null);  // back to parent
});

// Shadow DOM
it('should access shadow DOM element', async () => {
  const host = await $('custom-element');
  const shadowInput = await host.shadow$('input.inner-field');
  await shadowInput.setValue('shadow value');
});

// Nested shadow DOM
const deepElement = await $('outer-component')
  .shadow$('inner-component')
  .shadow$('.deep-element');
```

## §7 — Visual Regression Testing

```typescript
// Using wdio-image-comparison-service
// wdio.conf.ts
import { join } from 'path';

services: [
  ['image-comparison', {
    baselineFolder: join(process.cwd(), './test/baselines/'),
    formatImageName: '{tag}-{browserName}-{width}x{height}',
    screenshotPath: join(process.cwd(), './test/.tmp/'),
    autoSaveBaseline: true,
    blockOutStatusBar: true,
    blockOutToolBar: true,
  }],
],

// Test
it('should match homepage visual baseline', async () => {
  await browser.url('/');
  await browser.waitForPageLoad();
  const result = await browser.checkFullPageScreen('homepage', { /* options */ });
  expect(result).toBeLessThan(0.5);  // 0.5% mismatch threshold
});

it('should match element visual baseline', async () => {
  const header = await $('[data-testid="header"]');
  const result = await browser.checkElement(header, 'header-component');
  expect(result).toBeLessThan(1);
});
```

## §8 — API Testing with WebdriverIO

```typescript
describe('API Tests', () => {
  let token: string;

  before(async () => {
    const response = await browser.call(() =>
      fetch(`${browser.options.baseUrl}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'admin@test.com', password: 'admin123' }),
      }).then(r => r.json())
    );
    token = response.token;
  });

  it('should create a user via API', async () => {
    const response = await browser.call(() =>
      fetch(`${browser.options.baseUrl}/api/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ name: 'Test User', email: 'test@example.com' }),
      })
    );
    expect(response.status).toBe(201);
  });

  it('should combine API setup with UI verification', async () => {
    // Create via API
    await browser.call(() =>
      fetch(`${browser.options.baseUrl}/api/products`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name: 'New Product', price: 99.99 }),
      })
    );
    // Verify in UI
    await browser.url('/products');
    await expect($('text=New Product')).toBeDisplayed();
  });
});
```

## §9 — Mobile Testing (Appium Service)

```javascript
// wdio.mobile.conf.ts
export const config = {
  ...baseConfig,
  services: ['appium'],
  capabilities: [{
    platformName: 'Android',
    'appium:deviceName': 'Pixel_6',
    'appium:automationName': 'UiAutomator2',
    'appium:app': './apps/android-app.apk',
  }],
  // Or for web testing on mobile
  // capabilities: [{
  //   platformName: 'iOS',
  //   browserName: 'Safari',
  //   'appium:deviceName': 'iPhone 15',
  // }],
};
```

## §10 — LambdaTest Integration

```javascript
// wdio.lambdatest.conf.ts
export const config = {
  ...baseConfig,
  user: process.env.LT_USERNAME,
  key: process.env.LT_ACCESS_KEY,
  hostname: 'hub.lambdatest.com',
  path: '/wd/hub',
  capabilities: [{
    browserName: 'Chrome',
    browserVersion: 'latest',
    'LT:Options': {
      platformName: 'Windows 11',
      project: 'My Project',
      build: `Build ${process.env.BUILD_NUMBER || 'local'}`,
      name: 'WebdriverIO Tests',
      video: true,
      console: true,
      network: true,
      tunnel: false,
      w3c: true,
    },
  }],
};
```

## §11 — CI/CD Integration

```yaml
# GitHub Actions
name: WebdriverIO Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        suite: [smoke, regression]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx wdio run wdio.ci.conf.ts --suite ${{ matrix.suite }}
        env:
          CI: true
          BASE_URL: http://localhost:3000
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.suite }}
          path: |
            allure-results/
            test-results/
            screenshots/
```

```yaml
# Docker Compose for local/CI
version: '3'
services:
  chrome:
    image: selenium/standalone-chrome:latest
    ports: ['4444:4444']
    shm_size: 2gb
  tests:
    build: .
    depends_on: [chrome]
    environment:
      - SELENIUM_HOST=chrome
      - BASE_URL=http://app:3000
    command: npx wdio run wdio.docker.conf.ts
```

## §12 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Element not interactable | Hidden or overlapped | `await elem.waitForClickable()` before click |
| Stale element reference | DOM re-rendered | Re-query `await $('selector')` (WDIO auto-retries) |
| `$` returns empty/undefined | Wrong selector or iframe | Check iframe: `browser.switchToFrame()`, verify selector |
| Cookie not set | Set before navigation | Call `browser.setCookies()` after `browser.url()` |
| Mock not intercepting | Wrong URL pattern or method | Use `**/path` glob, verify HTTP method filter |
| Timeout in CI | Slower CI machines | Increase `waitforTimeout`, use `--headless` |
| Upload fails remotely | Path not resolved | Use `browser.uploadFile()` for remote grids |
| Shadow DOM not accessible | Wrong API | Use `elem.shadow$()` not regular `$` |
| Parallel tests interfere | Shared state (cookies, DB) | Isolate with unique test data, clear cookies |
| Visual regression false positive | Dynamic content (dates, ads) | Use `blockOut` regions or `hideElements` option |
| `browser` undefined in hooks | Wrong hook scope | Use `before`/`after` not arrow functions for `this` context |

## §13 — Best Practices Checklist

- ✅ Use `data-testid` attributes for stable selectors
- ✅ Use Page Object Model for 3+ page interactions
- ✅ Register custom commands for reusable actions (API login, waits)
- ✅ Use `browser.mock()` for network mocking via DevTools
- ✅ Use `waitForClickable()` / `waitForDisplayed()` before interactions
- ✅ Login via API for non-auth test scenarios
- ✅ Take screenshots in `afterTest` hook on failure
- ✅ Use suites for organizing test groups (`--suite smoke`)
- ✅ Run headless in CI with `--headless=new`
- ✅ Use Allure reporter for rich HTML reports
- ✅ Use `browser.call()` for async API calls in tests
- ✅ Use image comparison service for visual regression
- ✅ Configure retries in CI: `mochaOpts.retries: 1`
- ✅ Structure: `test/specs/`, `test/pages/`, `test/fixtures/`, `test/helpers/`
