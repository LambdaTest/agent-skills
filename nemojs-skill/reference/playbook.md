# Nemo.js — Advanced Implementation Playbook

## §1 — JSON Locator Files (View Pattern)

Nemo's View pattern separates locators from test logic via JSON files.

```
test/
├── functional/
│   ├── login.test.js
│   └── dashboard.test.js
└── locators/
    ├── login.json
    └── dashboard.json
```

### login.json
```json
{
  "emailInput": { "locator": "#email", "type": "css" },
  "passwordInput": { "locator": "#password", "type": "css" },
  "submitBtn": { "locator": "button[type='submit']", "type": "css" },
  "errorMessage": { "locator": ".error-message", "type": "css" },
  "googleLogin": { "locator": "[data-testid='google-oauth']", "type": "css" },
  "rememberMe": { "locator": "#remember-checkbox", "type": "css" }
}
```

### Using Named Locators in Tests
```javascript
describe('Login', function() {
  let nemo;

  before(async () => {
    nemo = await Nemo();
  });
  after(async () => { await nemo.driver.quit(); });

  it('should login using named locators', async () => {
    await nemo.driver.get(nemo.data.baseUrl + '/login');
    // Uses locators from login.json automatically
    await nemo.view.login.emailInput().sendKeys('user@test.com');
    await nemo.view.login.passwordInput().sendKeys('password123');
    await nemo.view.login.submitBtn().click();
    await nemo.view.dashboard.welcomeMsg.waitVisible(10000);
  });

  it('shows error for invalid credentials', async () => {
    await nemo.driver.get(nemo.data.baseUrl + '/login');
    await nemo.view.login.emailInput().sendKeys('bad@test.com');
    await nemo.view.login.passwordInput().sendKeys('wrong');
    await nemo.view.login.submitBtn().click();
    await nemo.view.login.errorMessage.waitVisible(5000);
    const text = await nemo.view.login.errorMessage().getText();
    expect(text).to.include('Invalid credentials');
  });
});
```

## §2 — Profile-Based Configuration

```json
{
  "profiles": {
    "base": {
      "driver": { "browser": "chrome" },
      "data": { "baseUrl": "http://localhost:3000" },
      "plugins": {
        "view": {
          "module": "nemo-view",
          "arguments": ["path:locators"]
        }
      }
    },
    "ci": {
      "driver": {
        "browser": "chrome",
        "chromeOptions": ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage"]
      },
      "data": {
        "baseUrl": "http://localhost:3000"
      }
    },
    "staging": {
      "data": {
        "baseUrl": "https://staging.example.com"
      }
    }
  }
}
```

Usage:
```bash
# Local development
NEMO_PROFILE=base npx mocha test/**/*.test.js

# CI pipeline
NEMO_PROFILE=ci npx mocha test/**/*.test.js

# Staging
NEMO_PROFILE=staging npx mocha test/**/*.test.js
```

## §3 — Custom View Methods

```javascript
// views/custom-login-view.js
module.exports = {
  /**
   * Complete login action
   * @param {string} email
   * @param {string} password
   */
  async login(email, password) {
    const nemo = this.nemo;
    await nemo.view.login.emailInput().clear();
    await nemo.view.login.emailInput().sendKeys(email);
    await nemo.view.login.passwordInput().clear();
    await nemo.view.login.passwordInput().sendKeys(password);
    await nemo.view.login.submitBtn().click();
  },

  /**
   * Login and verify success
   */
  async loginAndVerify(email, password) {
    await this.login(email, password);
    await nemo.view.dashboard.welcomeMsg.waitVisible(10000);
    return nemo.driver.getCurrentUrl();
  },

  /**
   * Get error message text
   */
  async getErrorText() {
    await this.nemo.view.login.errorMessage.waitVisible(5000);
    return this.nemo.view.login.errorMessage().getText();
  }
};
```

## §4 — Screenshot on Failure

```javascript
// test/helpers/screenshot-hook.js
const fs = require('fs');
const path = require('path');

function setupScreenshotHook(nemo, testContext) {
  afterEach(async function() {
    if (this.currentTest.state === 'failed' && nemo && nemo.driver) {
      const dir = 'screenshots';
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

      const name = this.currentTest.title.replace(/[^a-zA-Z0-9]/g, '_');
      const ts = Date.now();
      const filepath = path.join(dir, `${name}_${ts}.png`);

      const screenshot = await nemo.driver.takeScreenshot();
      fs.writeFileSync(filepath, screenshot, 'base64');
      console.log(`  Screenshot: ${filepath}`);
    }
  });
}

module.exports = { setupScreenshotHook };
```

Usage in test:
```javascript
const { setupScreenshotHook } = require('./helpers/screenshot-hook');

describe('Login', function() {
  let nemo;
  before(async () => { nemo = await Nemo(); });
  after(async () => { await nemo.driver.quit(); });
  setupScreenshotHook(() => nemo);

  it('test...', async () => { /* ... */ });
});
```

## §5 — Nemo Plugins

```json
{
  "plugins": {
    "view": { "module": "nemo-view", "arguments": ["path:locators"] },
    "drivex": { "module": "nemo-drivex" },
    "mocha": { "module": "nemo-mocha-factory" }
  }
}
```

Common plugins:
- `nemo-view` — JSON-based locator management
- `nemo-drivex` — Extended WebDriver methods (waitForElement, anyVisible)
- `nemo-mocha-factory` — Auto test generation from Mocha
- `nemo-accessibility` — Accessibility testing integration

## §6 — Debugging & Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `Nemo is not a function` | Wrong import | Use `const Nemo = require('nemo')` |
| Locator not found | Missing view JSON | Verify JSON file in locators dir, check `arguments` path |
| Profile not loading | Wrong env var | Set `NEMO_PROFILE=profileName` |
| Timeout on element | Page not loaded | Use `_waitVisible(locator, timeout)` with longer timeout |
| Chrome not starting | Missing chromedriver | `npm install chromedriver` or use `webdriver-manager` |
| Stale element | DOM changed | Re-find element: `await nemo.view._find(locator)` again |

## §7 — CI/CD Integration

```yaml
name: Nemo Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 18 }
      - run: npm ci
      - run: NEMO_PROFILE=ci npx mocha test/**/*.test.js --timeout 60000 --reporter mochawesome
        env: { CI: true }
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-report
          path: |
            mochawesome-report/
            screenshots/
```

## §8 — Best Practices

- Use JSON locator files for all elements — separates test logic from selectors
- Use profiles for environment switching (local/CI/staging)
- Use `_waitVisible()` instead of implicit waits
- Take screenshots on failure for debugging
- Keep nemo instance setup in `before()`, cleanup in `after()`
- Use named views (`nemo.view.login.emailInput()`) over raw CSS in tests
- Install nemo-drivex for extended wait/find utilities
- Run with `--timeout 60000` for E2E tests
- Use mochawesome reporter for HTML reports
