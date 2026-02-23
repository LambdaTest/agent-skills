# TestCafe — Advanced Implementation Playbook

## §1 Production Configuration

### .testcaferc.json
```json
{
  "browsers": ["chrome:headless"],
  "src": ["tests/**/*.test.ts"],
  "screenshots": {
    "path": "screenshots",
    "takeOnFails": true,
    "fullPage": true,
    "pathPattern": "${DATE}_${TIME}/${FIXTURE}/${TEST}/${RUN_ID}.png"
  },
  "reporter": [
    { "name": "spec" },
    { "name": "html", "output": "reports/report.html" },
    { "name": "xunit", "output": "reports/junit.xml" }
  ],
  "concurrency": 3,
  "selectorTimeout": 10000,
  "assertionTimeout": 5000,
  "pageLoadTimeout": 30000,
  "pageRequestTimeout": 8000,
  "ajaxRequestTimeout": 40000,
  "quarantineMode": {
    "successThreshold": 1,
    "attemptLimit": 3
  },
  "stopOnFirstFail": false,
  "skipJsErrors": false,
  "cache": true,
  "compilerOptions": {
    "typescript": {
      "configPath": "tsconfig.testcafe.json"
    }
  }
}
```

### tsconfig.testcafe.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true,
    "baseUrl": ".",
    "paths": {
      "@pages/*": ["tests/pages/*"],
      "@helpers/*": ["tests/helpers/*"]
    }
  }
}
```

---

## §2 Page Model Pattern with Roles

### Roles (Authentication)
```typescript
import { Role } from 'testcafe';

export const adminRole = Role('http://localhost:3000/login', async t => {
  await t
    .typeText('[data-testid="email"]', 'admin@test.com')
    .typeText('[data-testid="password"]', 'admin-pass')
    .click('[data-testid="submit"]');
}, { preserveUrl: true });

export const userRole = Role('http://localhost:3000/login', async t => {
  await t
    .typeText('[data-testid="email"]', 'user@test.com')
    .typeText('[data-testid="password"]', 'user-pass')
    .click('[data-testid="submit"]');
}, { preserveUrl: true });

// API-based role (faster — no UI interaction)
export const apiRole = Role('http://localhost:3000', async t => {
  const response = await t.request('http://localhost:3000/api/login', {
    method: 'POST',
    body: { email: 'user@test.com', password: 'password' },
  });
  await t.setCookies({ name: 'token', value: response.body.token });
});
```

### BasePage
```typescript
import { Selector, t } from 'testcafe';

export class BasePage {
  protected async waitForVisible(selector: Selector, timeout = 10000) {
    await t.expect(selector.visible).ok({ timeout });
  }

  protected async getText(selector: Selector): Promise<string> {
    return selector.innerText;
  }

  protected async selectDropdownOption(dropdown: Selector, option: string) {
    await t.click(dropdown).click(Selector('option').withText(option));
  }
}
```

### DashboardPage
```typescript
import { Selector, t } from 'testcafe';
import { BasePage } from './BasePage';

export class DashboardPage extends BasePage {
  welcomeMsg = Selector('[data-testid="welcome"]');
  navItems = Selector('.nav-item');
  searchInput = Selector('[data-testid="search"]');
  productCards = Selector('[data-testid="product-card"]');
  logoutBtn = Selector('[data-testid="logout"]');

  async getWelcomeText() { return this.welcomeMsg.innerText; }

  async searchProducts(query: string) {
    await t
      .selectText(this.searchInput)
      .pressKey('delete')
      .typeText(this.searchInput, query);
    await t.expect(this.productCards.count).gt(0, { timeout: 5000 });
  }

  async getProductCount() { return this.productCards.count; }

  async clickProduct(index: number) {
    await t.click(this.productCards.nth(index));
  }
}
```

---

## §3 Request Mocking & Logging

### Request Mocks
```typescript
import { RequestMock, RequestLogger } from 'testcafe';

const productsMock = RequestMock()
  .onRequestTo('/api/products')
  .respond([
    { id: 1, name: 'Mock Widget', price: 9.99 },
    { id: 2, name: 'Mock Gadget', price: 19.99 },
  ], 200, { 'content-type': 'application/json' });

const errorMock = RequestMock()
  .onRequestTo('/api/products')
  .respond({ error: 'Internal Server Error' }, 500);

// Conditional mock based on request
const conditionalMock = RequestMock()
  .onRequestTo({ url: /\/api\/users\/\d+/, method: 'GET' })
  .respond((req, res) => {
    const id = req.url.match(/\/users\/(\d+)/)[1];
    res.statusCode = 200;
    res.headers['content-type'] = 'application/json';
    res.body = JSON.stringify({ id: Number(id), name: `User ${id}` });
  });
```

### Request Logger
```typescript
const apiLogger = RequestLogger(/\/api\//, {
  logRequestHeaders: true,
  logRequestBody: true,
  logResponseHeaders: true,
  logResponseBody: true,
});

fixture`API Monitoring`.requestHooks(apiLogger);

test('tracks API calls during workflow', async t => {
  await t.navigateTo('/dashboard');

  // Verify specific API call was made
  await t.expect(apiLogger.contains(r =>
    r.request.url.includes('/api/products') &&
    r.response.statusCode === 200
  )).ok({ timeout: 10000 });

  // Check request count
  await t.expect(apiLogger.count(r =>
    r.request.method === 'GET'
  )).gte(1);
});
```

---

## §4 Client Functions & Browser Interaction

```typescript
import { ClientFunction, Selector } from 'testcafe';

// Access browser APIs
const getWindowLocation = ClientFunction(() => window.location.href);
const getLocalStorage = ClientFunction((key: string) => localStorage.getItem(key));
const setLocalStorage = ClientFunction((key: string, value: string) =>
  localStorage.setItem(key, value));
const scrollToBottom = ClientFunction(() =>
  window.scrollTo(0, document.body.scrollHeight));
const getComputedStyle = ClientFunction((selector: string, prop: string) => {
  const el = document.querySelector(selector);
  return el ? window.getComputedStyle(el).getPropertyValue(prop) : null;
});

test('verifies client-side state', async t => {
  await t.navigateTo('/login');
  await t.typeText('#email', 'user@test.com');
  await t.typeText('#password', 'password');
  await t.click('#submit');

  const url = await getWindowLocation();
  await t.expect(url).contains('/dashboard');

  const token = await getLocalStorage('auth_token');
  await t.expect(token).ok('Auth token should be stored');
});
```

### File Operations
```typescript
test('file upload and download', async t => {
  // Upload
  await t.setFilesToUpload('[data-testid="file-input"]', [
    './fixtures/test-document.pdf',
    './fixtures/test-image.png',
  ]);
  await t.expect(Selector('.uploaded-file').count).eql(2);

  // Clear upload
  await t.clearUpload('[data-testid="file-input"]');
});
```

### iFrame Interaction
```typescript
test('fills payment iframe', async t => {
  await t
    .switchToIframe('#payment-iframe')
    .typeText('#card-number', '4242424242424242')
    .typeText('#expiry', '12/25')
    .typeText('#cvc', '123')
    .switchToMainWindow()
    .click('#submit-payment');
});
```

---

## §5 Advanced Test Patterns

### Fixture-Level Configuration
```typescript
fixture`Dashboard Tests`
  .page`http://localhost:3000/dashboard`
  .requestHooks(productsMock, apiLogger)
  .beforeEach(async t => {
    await t.useRole(userRole);
  })
  .afterEach(async t => {
    await t.takeScreenshot();
  })
  .meta({ priority: 'high', suite: 'smoke' });
```

### Filtering Tests by Meta
```bash
testcafe chrome tests/ --test-meta priority=high
testcafe chrome tests/ --fixture-meta suite=smoke
```

### Multiple Browser Windows
```typescript
test('OAuth popup flow', async t => {
  await t.click('#oauth-login');

  // Switch to popup window
  await t.switchToWindow(w => w.url.host === 'accounts.google.com');
  await t.typeText('#email', 'user@gmail.com');
  await t.click('#next');

  // Switch back to main window
  await t.switchToParentWindow();
  await t.expect(Selector('#welcome').visible).ok();
});
```

### Custom Test Speed & Debug
```typescript
test('debug this test', async t => {
  await t.setTestSpeed(0.5);  // slow down for visibility
  await t.debug();             // pause and open debug panel

  // Continue test
  await t.click('#submit');
});
```

---

## §6 LambdaTest Integration

```json
{
  "browsers": ["lambdatest:chrome@latest:Windows 11"],
  "hostname": "hub.lambdatest.com",
  "port": 80,
  "path": "/wd/hub",
  "concurrency": 5,
  "src": ["tests/**/*.test.ts"]
}
```

```bash
export LT_USERNAME=your_username
export LT_ACCESS_KEY=your_access_key
testcafe "lambdatest:Chrome@latest:Windows 11" tests/
```

---

## §7 CI/CD Integration

### GitHub Actions
```yaml
name: TestCafe E2E
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  e2e:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chrome:headless, firefox:headless]

    services:
      app:
        image: myapp:latest
        ports: ['3000:3000']

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }

      - run: npm ci

      - name: Run TestCafe
        run: npx testcafe ${{ matrix.browser }} tests/ --reporter spec,xunit:reports/junit.xml

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: testcafe-results-${{ matrix.browser }}
          path: |
            screenshots/
            reports/
```

### Docker
```dockerfile
FROM testcafe/testcafe:latest
COPY tests/ /tests/
COPY .testcaferc.json /
CMD ["chromium:headless", "/tests/", "--reporter", "spec,html:reports/report.html"]
```

---

## §8 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Selector not found | Element not rendered or wrong selector | Use `t.debug()` to inspect; verify `data-testid` in DOM |
| 2 | Role login fails | Login page changed or redirect issue | Check Role URL and selectors; use `preserveUrl: false` if redirect needed |
| 3 | Request mock not intercepting | URL pattern mismatch | Use regex: `.onRequestTo(/\/api\/products/)` for flexible matching |
| 4 | `quarantineMode` retries forever | Test has non-deterministic failure | Fix root cause; adjust `attemptLimit` and `successThreshold` |
| 5 | `ClientFunction` returns undefined | Accessing variables from test scope | Pass values as arguments: `ClientFunction((val) => ..., { dependencies: { val } })` |
| 6 | Timeout in CI but passes locally | Slower CI environment | Increase `selectorTimeout` and `assertionTimeout` in `.testcaferc.json` |
| 7 | File upload fails | Incorrect file path | Use relative path from project root; verify file exists in repo |
| 8 | iFrame content not accessible | Wrong iframe selector | Verify iframe `id`/`name`; ensure `switchToIframe` completes |
| 9 | Concurrent tests interfere | Shared state between tests | Use `beforeEach` to reset state; avoid shared database records |
| 10 | Screenshots not saved | Path pattern issue | Check `screenshots.pathPattern` in config; ensure directory exists |
| 11 | Browser window switch fails | Popup blocked | Disable popup blocker: use `--disable-popup-blocking` Chrome flag |
| 12 | `skipJsErrors` hides real bugs | All JS errors silenced | Use `t.skipJsErrors(opts)` per-test with specific error filtering |

---

## §9 Best Practices Checklist

1. ✅ Use Roles for auth state — faster than re-logging in each test
2. ✅ Use `data-testid` attributes for stable selectors
3. ✅ Use RequestMock for API mocking — eliminate external API dependency
4. ✅ Use RequestLogger for API call assertions in integration tests
5. ✅ TestCafe auto-waits — avoid manual `wait()` calls; increase timeout configs instead
6. ✅ Use `quarantineMode` for flaky test management with bounded retries
7. ✅ Use `concurrency` for parallel browser instances to reduce execution time
8. ✅ Use `Selector().filterVisible()` for dynamic content
9. ✅ Use `t.debug()` during development to pause and inspect state
10. ✅ Use fixture-level `requestHooks` for mock/logger scope management
11. ✅ Use `--test-meta` for filtering tests by priority/suite in CI
12. ✅ Configure `screenshots.takeOnFails: true` for automatic failure evidence
13. ✅ Use Docker image `testcafe/testcafe` for consistent CI environments
