# Nightwatch.js — Advanced Implementation Playbook

## §1 — Production Configuration

```javascript
// nightwatch.conf.js
module.exports = {
  src_folders: ['tests'],
  page_objects_path: ['pages'],
  custom_commands_path: ['commands'],
  custom_assertions_path: ['assertions'],
  globals_path: 'globals.js',
  output_folder: 'reports',

  webdriver: { start_process: true, port: 9515 },

  test_settings: {
    default: {
      launch_url: process.env.BASE_URL || 'http://localhost:3000',
      desiredCapabilities: {
        browserName: 'chrome',
        'goog:chromeOptions': {
          args: process.env.CI ? ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage'] : [],
          w3c: true,
        },
      },
      screenshots: { enabled: true, on_failure: true, on_error: true, path: 'screenshots' },
      end_session_on_fail: true,
      skip_testcases_on_fail: false,
    },

    firefox: {
      desiredCapabilities: {
        browserName: 'firefox',
        'moz:firefoxOptions': { args: process.env.CI ? ['-headless'] : [] },
      },
    },

    selenium: {
      selenium: {
        start_process: true,
        host: 'localhost',
        port: 4444,
        server_path: require('selenium-server').path,
      },
    },
  },

  test_workers: { enabled: true, workers: 'auto' },
};
```

### Globals File

```javascript
// globals.js
module.exports = {
  waitForConditionTimeout: 10000,
  retryAssertionTimeout: 5000,
  asyncHookTimeout: 30000,

  before(done) { console.log('Global setup'); done(); },
  after(done) { console.log('Global teardown'); done(); },
  beforeEach(browser, done) { done(); },
  afterEach(browser, done) {
    if (browser.currentTest.results.failed > 0) {
      browser.saveScreenshot(`screenshots/failure-${Date.now()}.png`);
    }
    done();
  },
};
```

## §2 — Page Objects

```javascript
// pages/loginPage.js
module.exports = {
  url() { return `${this.api.launchUrl}/login`; },

  elements: {
    emailInput: { selector: '[data-testid="email"]' },
    passwordInput: { selector: '[data-testid="password"]' },
    submitBtn: { selector: '[data-testid="login-btn"]' },
    errorMsg: { selector: '.error-message' },
    rememberMe: { selector: '[data-testid="remember-me"]' },
  },

  commands: [{
    login(email, password) {
      return this
        .waitForElementVisible('@emailInput')
        .clearValue('@emailInput').setValue('@emailInput', email)
        .clearValue('@passwordInput').setValue('@passwordInput', password)
        .click('@submitBtn');
    },

    getError() {
      this.waitForElementVisible('@errorMsg');
      return this.getText('@errorMsg');
    },

    assertLoggedIn() {
      return this.waitForElementNotPresent('@emailInput');
    },
  }],
};

// pages/dashboardPage.js
module.exports = {
  elements: {
    welcomeMsg: { selector: '[data-testid="welcome"]' },
    navMenu: { selector: '[data-testid="nav"]' },
    logoutBtn: { selector: '[data-testid="logout"]' },
  },

  commands: [{
    assertLoaded() {
      return this.waitForElementVisible('@welcomeMsg');
    },
    getWelcomeText(callback) {
      return this.getText('@welcomeMsg', callback);
    },
  }],
};
```

## §3 — Test Patterns

```javascript
// tests/login.test.js
describe('Login @smoke', function() {
  let loginPage, dashboard;

  before(function(browser) {
    loginPage = browser.page.loginPage();
    dashboard = browser.page.dashboardPage();
    loginPage.navigate();
  });

  it('should login with valid credentials', function(browser) {
    loginPage.login('admin@test.com', 'admin123');
    dashboard.assertLoaded();
    dashboard.getWelcomeText(function(result) {
      browser.assert.ok(result.value.includes('Welcome'));
    });
  });

  it('should show error for invalid credentials', function() {
    loginPage.navigate();
    loginPage.login('wrong@test.com', 'wrong');
    loginPage.assert.visible('@errorMsg');
    loginPage.expect.element('@errorMsg').text.to.contain('Invalid');
  });

  after(function(browser) {
    browser.end();
  });
});

// BDD-style with expect
describe('Search Feature @regression', function() {
  it('should return results', function(browser) {
    browser
      .url(`${browser.launch_url}/search`)
      .waitForElementVisible('[data-testid="search-input"]')
      .setValue('[data-testid="search-input"]', 'testing')
      .click('[data-testid="search-btn"]')
      .waitForElementVisible('.results');

    browser.expect.elements('.result-item').count.to.be.above(0);
    browser.expect.element('.result-item:first-child').text.to.contain('testing');
  });
});
```

## §4 — Custom Commands

```javascript
// commands/loginViaApi.js
module.exports = {
  command: async function(email, password) {
    const response = await fetch(`${this.launchUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }).then(r => r.json());

    this.setCookie({ name: 'token', value: response.token, path: '/' });
    return this;
  },
};

// commands/waitForNetworkIdle.js
module.exports = {
  command: function(timeout = 5000) {
    this.execute(function() {
      return performance.getEntriesByType('resource')
        .filter(r => !r.responseEnd).length;
    }, [], function(result) {
      this.assert.equal(result.value, 0, 'Network is idle');
    });
    return this;
  },
};

// Usage in tests
browser.loginViaApi('admin@test.com', 'admin123');
browser.url('/dashboard');
```

## §5 — Custom Assertions

```javascript
// assertions/elementCount.js
exports.assertion = function(selector, expectedCount) {
  this.message = `Testing if element <${selector}> count is ${expectedCount}`;
  this.expected = expectedCount;

  this.evaluate = function(value) { return value === expectedCount; };

  this.value = function(result) { return result.value.length; };

  this.command = function(callback) {
    return this.api.elements('css selector', selector, callback);
  };
};

// Usage: browser.assert.elementCount('.item', 5);
```

## §6 — API Testing (Built-in)

```javascript
describe('API Tests', function() {
  it('should create a user', async function(browser) {
    const response = await browser.request('POST', '/api/users', {
      body: { name: 'Alice', email: 'alice@test.com' },
      headers: { 'Content-Type': 'application/json' },
    });

    browser.assert.equal(response.status, 201);
    browser.assert.ok(response.body.id);
  });

  it('should verify API + UI integration', async function(browser) {
    // Create via API
    await browser.request('POST', '/api/products', {
      body: { name: 'Widget', price: 9.99 },
    });

    // Verify in UI
    browser.url('/products');
    browser.waitForElementVisible('[data-testid="product-list"]');
    browser.assert.textContains('.product-name', 'Widget');
  });
});
```

## §7 — Component Testing (React/Vue)

```javascript
// Nightwatch component testing
describe('Button Component', function() {
  it('should render with label', async function(browser) {
    const button = await browser.mountComponent('/src/components/Button.jsx', {
      props: { label: 'Click Me', variant: 'primary' },
    });

    browser.expect.element(button).text.to.equal('Click Me');
    browser.expect.element(button).to.have.css('background-color');
  });
});
```

## §8 — CI/CD Integration

```yaml
# GitHub Actions
name: Nightwatch Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        env: [default, firefox]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx nightwatch --env ${{ matrix.env }} --tag smoke
        env: { CI: true }
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: nightwatch-results-${{ matrix.env }}
          path: |
            reports/
            screenshots/
```

## §9 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Element not found | Selector wrong or not visible | Use `waitForElementVisible` before interaction |
| Page object command fails | Missing `return this` | Always return `this` for chaining |
| Timeout on waitFor | Element never appears | Increase `waitForConditionTimeout` in globals |
| Screenshots not saving | Wrong path config | Check `screenshots.path` in config |
| Workers causing conflicts | Shared state between tests | Use `test_workers: { enabled: false }` to debug |
| Custom command not found | Wrong folder path | Verify `custom_commands_path` in config |
| Element stale after navigation | Page re-rendered | Re-query element after navigation |
| `@` selector not working | Not using page object | `@` prefix only works in page object context |

## §10 — Best Practices Checklist

- ✅ Use Page Objects for all page interactions
- ✅ Use custom commands for reusable actions (API login, waits)
- ✅ Use `data-testid` selectors for stability
- ✅ Use `waitForElementVisible` before every interaction
- ✅ Return `this` in all page object commands for chaining
- ✅ Use globals file for shared hooks and timeouts
- ✅ Use `test_workers` for parallel execution
- ✅ Use tags (`@smoke`, `@regression`) for selective runs
- ✅ Capture screenshots on failure in `afterEach` hook
- ✅ Use built-in API testing for backend verification
- ✅ Run headless in CI with `--headless=new`
- ✅ Structure: `tests/`, `pages/`, `commands/`, `assertions/`, `globals.js`
