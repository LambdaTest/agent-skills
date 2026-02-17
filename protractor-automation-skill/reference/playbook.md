# Protractor — Advanced Playbook

> **⚠ Protractor is officially deprecated** (end-of-life since 2023). Angular recommends migrating to Playwright, Cypress, or WebDriverIO. This playbook covers both maintaining existing Protractor codebases and migration strategies.

## §1 — Project Setup (Legacy Maintenance)

### Configuration
```javascript
// protractor.conf.js
exports.config = {
    directConnect: true,
    framework: 'jasmine',
    specs: ['spec/**/*.spec.ts'],
    suites: {
        smoke: 'spec/smoke/**/*.spec.ts',
        regression: 'spec/regression/**/*.spec.ts',
        auth: 'spec/auth/**/*.spec.ts',
    },
    capabilities: {
        browserName: 'chrome',
        chromeOptions: {
            args: [
                '--headless=new',
                '--no-sandbox',
                '--disable-gpu',
                '--window-size=1920,1080',
            ],
        },
    },
    multiCapabilities: [
        { browserName: 'chrome', shardTestFiles: true, maxInstances: 4 },
    ],
    baseUrl: process.env.BASE_URL || 'http://localhost:4200',
    jasmineNodeOpts: {
        defaultTimeoutInterval: 30000,
        showColors: true,
        print: function() {},
    },
    onPrepare: async () => {
        await browser.waitForAngularEnabled(true);
        const SpecReporter = require('jasmine-spec-reporter').SpecReporter;
        jasmine.getEnv().addReporter(new SpecReporter({
            spec: { displayStacktrace: 'pretty' }
        }));

        // Global implicit wait
        browser.manage().timeouts().implicitlyWait(5000);
    },
    params: {
        login: {
            email: 'admin@test.com',
            password: 'password123',
        },
    },
};
```

### Project Structure
```
project/
├── spec/
│   ├── smoke/
│   │   └── login.spec.ts
│   ├── regression/
│   │   ├── dashboard.spec.ts
│   │   └── checkout.spec.ts
│   └── auth/
│       └── permissions.spec.ts
├── pages/
│   ├── login.page.ts
│   ├── dashboard.page.ts
│   └── base.page.ts
├── helpers/
│   ├── wait.helper.ts
│   └── data.helper.ts
├── protractor.conf.js
└── tsconfig.e2e.json
```

---

## §2 — Page Objects

### Base Page
```typescript
import { browser, by, element, ElementFinder, ExpectedConditions as EC } from 'protractor';

export class BasePage {
    private timeout = 10000;

    async navigateTo(path: string): Promise<void> {
        await browser.get(path);
    }

    async waitForVisible(el: ElementFinder): Promise<void> {
        await browser.wait(EC.visibilityOf(el), this.timeout);
    }

    async waitForClickable(el: ElementFinder): Promise<void> {
        await browser.wait(EC.elementToBeClickable(el), this.timeout);
    }

    async safeClick(el: ElementFinder): Promise<void> {
        await this.waitForClickable(el);
        await el.click();
    }

    async safeType(el: ElementFinder, text: string): Promise<void> {
        await this.waitForVisible(el);
        await el.clear();
        await el.sendKeys(text);
    }

    async getText(el: ElementFinder): Promise<string> {
        await this.waitForVisible(el);
        return el.getText();
    }

    async isPresent(el: ElementFinder): Promise<boolean> {
        try {
            await browser.wait(EC.presenceOf(el), 3000);
            return true;
        } catch {
            return false;
        }
    }

    async getCurrentUrl(): Promise<string> {
        return browser.getCurrentUrl();
    }

    async takeScreenshot(name: string): Promise<void> {
        const png = await browser.takeScreenshot();
        const fs = require('fs');
        fs.writeFileSync(`screenshots/${name}.png`, png, 'base64');
    }
}
```

### Login Page Object
```typescript
import { by, element } from 'protractor';
import { BasePage } from './base.page';

export class LoginPage extends BasePage {
    private emailInput = element(by.css('[data-testid="email"]'));
    private passwordInput = element(by.css('[data-testid="password"]'));
    private submitBtn = element(by.css('[data-testid="login-submit"]'));
    private errorMsg = element(by.css('[role="alert"]'));
    private rememberMe = element(by.css('input[name="remember"]'));

    async open(): Promise<void> {
        await this.navigateTo('/login');
        await this.waitForVisible(this.emailInput);
    }

    async login(email: string, password: string): Promise<void> {
        await this.safeType(this.emailInput, email);
        await this.safeType(this.passwordInput, password);
        await this.safeClick(this.submitBtn);
    }

    async getErrorMessage(): Promise<string> {
        await this.waitForVisible(this.errorMsg);
        return this.errorMsg.getText();
    }

    async toggleRememberMe(): Promise<void> {
        await this.safeClick(this.rememberMe);
    }
}
```

---

## §3 — Test Specs

### Basic Specs
```typescript
import { browser, ExpectedConditions as EC } from 'protractor';
import { LoginPage } from '../pages/login.page';
import { DashboardPage } from '../pages/dashboard.page';

describe('Login', () => {
    const loginPage = new LoginPage();
    const dashboardPage = new DashboardPage();

    beforeEach(async () => {
        await loginPage.open();
    });

    it('should login with valid credentials', async () => {
        await loginPage.login('admin@test.com', 'password123');
        await browser.wait(EC.urlContains('/dashboard'), 10000);
        expect(await dashboardPage.getWelcomeText()).toContain('Welcome');
    });

    it('should show error for invalid credentials', async () => {
        await loginPage.login('admin@test.com', 'wrongpassword');
        expect(await loginPage.getErrorMessage()).toBe('Invalid credentials');
    });

    it('should redirect unauthenticated users to login', async () => {
        await browser.get('/dashboard');
        expect(await browser.getCurrentUrl()).toContain('/login');
    });
});
```

### Non-Angular Pages
```typescript
describe('External page', () => {
    beforeAll(async () => {
        await browser.waitForAngularEnabled(false);
    });

    afterAll(async () => {
        await browser.waitForAngularEnabled(true);
    });

    it('should handle non-Angular page', async () => {
        await browser.get('https://external-site.com');
        const heading = element(by.css('h1'));
        await browser.wait(EC.visibilityOf(heading), 10000);
        expect(await heading.getText()).toBeTruthy();
    });
});
```

---

## §4 — Angular-Specific Features

### Angular Locators
```typescript
// By model (AngularJS only)
element(by.model('user.name'));

// By binding (AngularJS only)
element(by.binding('user.email'));

// By repeater (AngularJS only)
element.all(by.repeater('item in items'));

// CSS (works for all Angular versions)
element(by.css('[data-testid="user-name"]'));

// By Angular component tag
element(by.css('app-user-list'));

// Deep CSS (piercing shadow DOM)
element(by.deepCss('.shadow-element'));
```

### Wait for Angular
```typescript
// Wait for Angular to stabilize (default behavior)
await browser.waitForAngularEnabled(true);

// For hybrid apps: disable and use explicit waits
await browser.waitForAngularEnabled(false);
await browser.wait(EC.presenceOf(element(by.css('.loaded'))), 10000);
```

---

## §5 — Migration to Playwright

### Migration Mapping
```
PROTRACTOR                              PLAYWRIGHT
─────────────────────────────────────── ─────────────────────────────
browser.get(url)                     →  page.goto(url)
element(by.css('.btn'))              →  page.locator('.btn')
element(by.id('name'))               →  page.locator('#name')
element(by.buttonText('Submit'))     →  page.getByRole('button', { name: 'Submit' })
element(by.xpath('//div'))           →  page.locator('//div')
element.all(by.css('.item'))         →  page.locator('.item').all()
el.click()                           →  locator.click()
el.sendKeys('text')                  →  locator.fill('text')
el.getText()                         →  locator.textContent()
el.getAttribute('href')              →  locator.getAttribute('href')
el.isDisplayed()                     →  locator.isVisible()
el.isPresent()                       →  locator.count() > 0
browser.wait(EC.visibilityOf(el))    →  locator.waitFor({ state: 'visible' })
browser.wait(EC.elementToBeClickable)→  locator.waitFor({ state: 'visible' })
browser.takeScreenshot()             →  page.screenshot()
browser.getCurrentUrl()              →  page.url()
browser.sleep(ms)                    →  page.waitForTimeout(ms)
ExpectedConditions.urlContains(str)  →  expect(page).toHaveURL(/str/)
expect(el.getText()).toBe('x')       →  expect(locator).toHaveText('x')
```

### Migration Strategy
```typescript
// Step 1: Install Playwright alongside Protractor
// npm install -D @playwright/test

// Step 2: Convert page objects
// BEFORE (Protractor)
class LoginPage extends BasePage {
    emailInput = element(by.css('[data-testid="email"]'));
    login(email, pass) {
        this.emailInput.sendKeys(email);
    }
}

// AFTER (Playwright)
class LoginPage {
    constructor(private page: Page) {}
    get emailInput() { return this.page.locator('[data-testid="email"]'); }
    async login(email: string, pass: string) {
        await this.emailInput.fill(email);
    }
}

// Step 3: Convert specs one suite at a time
// Step 4: Run both in parallel during migration
// Step 5: Remove Protractor once all specs are converted
```

---

## §6 — LambdaTest Integration

### Remote Configuration
```javascript
// protractor.conf.js — LambdaTest
exports.config = {
    seleniumAddress: `https://${process.env.LT_USERNAME}:${process.env.LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub`,
    capabilities: {
        browserName: 'chrome',
        browserVersion: 'latest',
        platformName: 'Windows 11',
        'LT:Options': {
            project: 'Protractor Tests',
            build: `protractor-${process.env.BUILD_NUMBER || 'local'}`,
            name: 'E2E Suite',
            console: true,
            network: true,
            visual: true,
            w3c: true,
        },
    },
    onPrepare: async () => {
        await browser.waitForAngularEnabled(true);
    },
};
```

---

## §7 — CI/CD Integration

### GitHub Actions
```yaml
name: Protractor E2E Tests
on:
  push:
    branches: [main]
  pull_request:

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Update WebDriver
        run: npx webdriver-manager update --chrome

      - name: Start application
        run: |
          npm run build
          npm run serve &
          npx wait-on http://localhost:4200

      - name: Run Protractor tests
        run: npx protractor protractor.conf.js --suite smoke
        env:
          BASE_URL: http://localhost:4200

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: protractor-screenshots
          path: screenshots/
```

---

## §8 — Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `Angular could not be found on the page` | Non-Angular app or Angular not bootstrapped | Use `browser.waitForAngularEnabled(false)` for non-Angular pages; add explicit waits |
| 2 | `ScriptTimeoutError` | Angular HTTP requests or zone.js tasks never complete | Check for long-polling, WebSocket connections; use `browser.waitForAngularEnabled(false)` + explicit waits |
| 3 | `StaleElementReferenceException` | Element removed from DOM between find and interaction | Re-locate element; use `ExpectedConditions` before interaction; avoid storing element references |
| 4 | `WebDriverError: chrome not reachable` | ChromeDriver version mismatch | Run `npx webdriver-manager update --chrome`; pin ChromeDriver version matching installed Chrome |
| 5 | Tests pass locally, fail in CI | No display for headless mode or timing differences | Add `--headless=new` to Chrome args; increase timeouts; add explicit waits |
| 6 | `ElementNotVisibleError` | Element exists in DOM but hidden by CSS | Use `browser.wait(EC.visibilityOf(el))` before interaction; check CSS display/visibility |
| 7 | `browser.params` undefined | Params not in config or overridden | Verify `params` object in protractor.conf.js; access as `browser.params.login.email` |
| 8 | Parallel tests interfere | Shared state or same test data | Use `shardTestFiles: true` in capabilities; isolate test data per instance |
| 9 | `by.model` / `by.binding` not found | Using AngularJS locators with Angular 2+ | Switch to `by.css('[data-testid="..."]')` for Angular 2+; these locators only work with AngularJS |
| 10 | Screenshots blank | Page not rendered when screenshot taken | Add `await browser.sleep(500)` or wait for specific element before screenshot |
| 11 | `NoSuchElementError` in `element.all` | Empty collection accessed by index | Check `.count()` before accessing by index; use `.filter()` to narrow results |
| 12 | Tests extremely slow | `browser.sleep()` everywhere | Replace `browser.sleep()` with `browser.wait(EC.visibilityOf(el))`; use explicit conditions |

---

## §9 — Best Practices Checklist

1. **Plan migration to Playwright or Cypress** — Protractor is deprecated with no security patches
2. Use `data-testid` attributes for stable selectors — avoid CSS classes and XPath
3. Use `browser.wait(EC.*)` instead of `browser.sleep()` — deterministic over fixed delays
4. Use page objects for all page interactions — keeps specs readable and maintainable
5. Use `waitForAngularEnabled(false)` for non-Angular pages — prevents timeouts
6. Run in headless mode in CI — `--headless=new` Chrome flag
7. Use `shardTestFiles: true` for parallel execution across spec files
8. Use suites for organizing tests — smoke, regression, auth
9. Pin ChromeDriver version to match CI Chrome — prevents version mismatch failures
10. Capture screenshots on failure — invaluable for debugging CI issues
11. Use `browser.params` for configurable test data — not hardcoded values
12. Use Jasmine `SpecReporter` for readable console output in CI
13. Migrate incrementally — convert one suite at a time to Playwright while keeping Protractor running
14. Track migration progress — count specs converted vs remaining to measure completion
