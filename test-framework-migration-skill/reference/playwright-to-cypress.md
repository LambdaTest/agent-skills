# Playwright → Cypress Migration

## API Mapping

### Locators

| Playwright | Cypress |
|------------|---------|
| `page.locator('#x')` | `cy.get('#x')` |
| `page.getByRole('button', { name: 'Submit' })` | `cy.contains('button', 'Submit')` or `cy.get('button').contains('Submit')` |
| `page.getByLabel('Email')` | `cy.get('label').contains('Email').parent().find('input')` or `cy.get('input[name=email]')` / data-cy |
| `page.getByTestId('btn')` | `cy.get('[data-testid="btn"]')` or `cy.get('[data-cy="btn"]')` (Cypress recommends data-cy) |
| `page.getByText('Welcome')` | `cy.contains('Welcome')` |
| `page.locator('.item').all()` | `cy.get('.item')` (returns chainable; use .each or assertions) |

**Cypress:** Prefer `data-cy` or `data-testid` selectors. No getByRole; use `cy.contains()` or `cy.get(selector)`.

### Waits / Assertions

| Playwright | Cypress |
|------------|---------|
| `await expect(locator).toBeVisible()` | `cy.get(selector).should('be.visible')` |
| `await expect(locator).toHaveText('x')` | `cy.get(selector).should('have.text', 'x')` |
| `await expect(page).toHaveURL(/\/dashboard/)` | `cy.url().should('include', '/dashboard')` |
| `await expect(page).toHaveTitle(/X/)` | `cy.title().should('include', 'X')` |
| Auto-wait on actions | Cypress has built-in retry-ability on cy.get and .should; no explicit wait needed for visibility |
| `page.waitForTimeout(ms)` | `cy.wait(ms)` (avoid; use .should instead) |

### Actions

| Playwright | Cypress |
|------------|---------|
| `await page.goto('/login')` | `cy.visit('/login')` (uses baseURL if set in config) |
| `await locator.fill('text')` | `cy.get(selector).type('text')` (or .clear() then .type) |
| `await locator.click()` | `cy.get(selector).click()` |
| `await page.locator('#sel').selectOption('v')` | `cy.get('#sel').select('v')` |
| `page.on('dialog', d => d.accept())` | `cy.on('window:alert', (text) => { ... })` or stub; for confirm use stub |
| `page.route(...)` for mocking | `cy.intercept('GET', '/api/**', { fixture: 'data.json' })` |
| `await request.post(...)` (APIRequestContext) | `cy.request('POST', '/api/...', body)` |

### Lifecycle

| Playwright | Cypress |
|------------|---------|
| `test.beforeEach(async ({ page }) => { await page.goto('/'); });` | `beforeEach(() => { cy.visit('/'); });` |
| Fixture-provided `page` | No page object; use `cy` in each test |
| `await browser.close()` | Cypress runner manages browser; no explicit close in test |
| `context.storageState()` for auth | `cy.session()` (Cypress 8+) or preserve cookies/localStorage |

## Before / After Snippets

**Playwright (TypeScript):**
```typescript
await page.goto('/login');
await page.getByLabel('Email').fill('user@test.com');
await page.getByRole('button', { name: 'Sign in' }).click();
await expect(page).toHaveURL(/\/dashboard/);
```

**Cypress (JavaScript):**
```javascript
cy.visit('/login');
cy.get('input[type="email"]').type('user@test.com');
cy.get('input[type="password"]').type('secret');
cy.get('button[type="submit"]').click();
cy.url().should('include', '/dashboard');
```

## Lifecycle / Setup

- **Playwright:** Async/await; config in playwright.config.ts; fixtures provide page.
- **Cypress:** No async/await with cy commands; config in cypress.config.js; use beforeEach for setup. Do not assign cy.get() to a variable for later use (commands are queued).

## Cloud (TestMu)

- Playwright: CDP to LambdaTest.
- Cypress: LambdaTest Cypress CLI. See [cypress-skill/reference/cloud-integration.md](../../cypress-skill/reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Gotchas

1. **No async/await with cy:** Never use async/await with Cypress commands. Write synchronous-looking code; Cypress queues commands.
2. **Do not store cy.get() for later:** Commands run asynchronously; use the chain or re-call cy.get() in the same flow. Avoid `const btn = cy.get('button');` then later `btn.click()`.
3. **getByRole/getByLabel:** Cypress has no equivalent; use cy.get(selector) or cy.contains(). Prefer data-cy or data-testid for stability.
4. **Multiple tabs:** Cypress does not support multiple browser tabs. If the Playwright test uses multiple pages/tabs, simplify to single tab or skip that part and document the limitation.
5. **Request mocking:** Playwright uses page.route(); Cypress uses cy.intercept(). Map intercept patterns and fixtures accordingly.
