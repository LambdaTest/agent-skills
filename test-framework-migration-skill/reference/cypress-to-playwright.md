# Cypress → Playwright Migration

## API Mapping

### Locators

| Cypress | Playwright |
|---------|------------|
| `cy.get('[data-cy="x"]')` | `page.getByTestId('x')` (requires `data-testid="x"`) or `page.locator('[data-cy="x"]')` |
| `cy.get('[data-testid="btn"]')` | `page.getByTestId('btn')` |
| `cy.contains('Submit')` | `page.getByText('Submit')` or `page.getByRole('button', { name: 'Submit' })` |
| `cy.get('#id')` | `page.locator('#id')` |
| `cy.get('.class')` | `page.locator('.class')` |
| `cy.get('button').contains('Save')` | `page.locator('button').filter({ hasText: 'Save' })` or `page.getByRole('button', { name: 'Save' })` |

**Playwright:** Prefer getByRole, getByLabel, getByText, getByTestId. Cypress chains are synchronous-looking but async under the hood; Playwright is explicitly async/await.

### Waits / Assertions (Cypress retry-ability → Playwright auto-wait)

| Cypress | Playwright |
|---------|------------|
| `cy.get('.msg').should('be.visible')` | `await expect(page.locator('.msg')).toBeVisible()` |
| `cy.get('.msg').should('have.text', 'Saved')` | `await expect(page.locator('.msg')).toHaveText('Saved')` |
| `cy.url().should('include', '/dashboard')` | `await expect(page).toHaveURL(/\/dashboard/)` |
| `cy.get('h1').should('contain', 'Welcome')` | `await expect(page.locator('h1')).toContainText('Welcome')` |
| `cy.wait(3000)` | **Avoid.** Use `await expect(locator).toBeVisible()` or action that implies wait |
| Implicit retry on cy.get/cy.should | Playwright auto-waits on assertions and actions |

### Actions

| Cypress | Playwright |
|---------|------------|
| `cy.visit('/login')` | `await page.goto(baseURL + '/login')` or `await page.goto('/login')` with baseURL in config |
| `cy.get('#email').type('user@test.com')` | `await page.locator('#email').fill('user@test.com')` |
| `cy.get('button').click()` | `await page.getByRole('button').click()` or `await page.locator('button').click()` |
| `cy.get('#sel').select('value')` | `await page.locator('#sel').selectOption('value')` |
| `cy.intercept('GET', '/api/users').as('users')` then `cy.wait('@users')` | `await page.waitForResponse(resp => resp.url().includes('/api/users') && resp.request().method() === 'GET')` or `page.route()` for mocking |
| `cy.request('POST', '/api/login', body)` | `await request.post(baseURL + '/api/login', { data: body })` (request from @playwright/test) |

### Lifecycle

| Cypress | Playwright |
|---------|------------|
| `beforeEach(() => { cy.visit('/') })` | `test.beforeEach(async ({ page }) => { await page.goto('/'); });` or set baseURL in config and goto in test |
| No explicit "close"; Cypress manages browser | Test runner provides page; browser/context closed after test |
| `cy.clearCookies()`, `cy.clearLocalStorage()` | `await context.clearCookies()`; `await page.evaluate(() => localStorage.clear())` |
| `cy.fixture('data.json')` | `import data from './fixtures/data.json'` or `require` / fs read in beforeAll |

## Before / After Snippets

**Cypress (JavaScript):**
```javascript
cy.visit('/login');
cy.get('[data-cy="email"]').type('user@test.com');
cy.get('[data-cy="password"]').type('secret');
cy.get('button[type="submit"]').click();
cy.url().should('include', '/dashboard');
cy.get('h1').should('contain', 'Dashboard');
```

**Playwright (TypeScript):**
```typescript
await page.goto('/login');
await page.getByTestId('email').fill('user@test.com');
await page.getByTestId('password').fill('secret');
await page.locator('button[type="submit"]').click();
await expect(page).toHaveURL(/\/dashboard/);
await expect(page.locator('h1')).toContainText('Dashboard');
```

## Lifecycle / Setup

- **Cypress:** Cypress runner; `cy` commands are queued and run asynchronously but written without async/await. Config in `cypress.config.js`.
- **Playwright:** Async/await throughout. Config in `playwright.config.ts`; use `baseURL` for relative URLs. Tests use `test('...', async ({ page }) => { ... })`.

## Cloud (TestMu)

- Cypress on TestMu: LambdaTest Cypress CLI / plugin.
- Playwright on TestMu: CDP connection. See [playwright-skill/reference/cloud-integration.md](../../playwright-skill/reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Gotchas

1. **Async/await required:** Cypress uses chain style (no await on cy); Playwright is async/await. Every action and assertion must be awaited.
2. **baseURL:** Cypress has baseURL in config; Playwright has the same. Use `page.goto('/path')` with config baseURL so relative paths work.
3. **No cy.wrap / aliases:** Cypress aliases (`.as()`) become variables or repeated locators in Playwright. Store locators in variables if reused.
4. **cy.intercept → page.route:** For mocking, use `await page.route('**/api/*', route => route.fulfill({ ... }))` or similar. For waiting on requests use `page.waitForResponse()`.
5. **Multiple tabs:** Cypress does not support multiple tabs well; Playwright does. If migrating tests that avoided multiple tabs, you can now use `context.waitForEvent('page')` or similar.
