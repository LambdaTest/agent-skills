# Debugging Flaky Tests — Playwright

## Table of Contents
- Flaky Test Checklist
- Debugging Tools
- Common Fixes with Code

## Flaky Test Checklist

Work through in order. Stop at the first match:

| # | Check | Fix |
|---|-------|-----|
| 1 | `waitForTimeout` anywhere? | Replace with `await expect(locator).toBeVisible()` or `waitForResponse` |
| 2 | `expect(await locator.isVisible())` pattern? | Switch to `await expect(locator).toBeVisible()` — enables auto-retry |
| 3 | `page.$(selector)` or `page.$$(selector)`? | Switch to `page.getByRole()` / `page.locator()` with web-first assertions |
| 4 | Shared state between tests? | Make each test independent with `test.beforeEach` setup |
| 5 | Fragile CSS/XPath selectors? | Switch to role-based: `getByRole`, `getByLabel`, `getByTestId` |
| 6 | Navigation without `waitForURL`? | Add `await page.waitForURL('**/dashboard')` after clicks that navigate |
| 7 | Dialog/alert not handled? | Register handler BEFORE the action that triggers it |
| 8 | Animation interference? | Add `animations: 'disabled'` to config or screenshot options |
| 9 | Network race condition? | Use `page.waitForResponse()` or mock the API |
| 10 | Test depends on time/date? | Mock `Date.now()` via `page.addInitScript` |

## Debugging Tools

### UI Mode (Best for investigation)

```bash
npx playwright test --ui
```

Interactive timeline with DOM snapshots at every action. Best for understanding what happened.

### Debug Mode (Step through)

```bash
npx playwright test --debug
```

Opens browser with Playwright Inspector. Set breakpoints with `await page.pause()`.

### Trace Viewer (Post-mortem)

```typescript
// playwright.config.ts
use: {
  trace: 'on-first-retry',  // Only captures on retry = only flaky tests
}
```

```bash
npx playwright show-trace trace.zip
```

### Video Recording

```typescript
use: {
  video: 'on-first-retry',
}
```

## Common Fixes with Code

### Fix 1: Dialog Race Condition

```typescript
// ❌ Dialog appears before handler is registered
await page.getByRole('button', { name: 'Delete' }).click();
page.on('dialog', (d) => d.accept()); // TOO LATE

// ✅ Register handler BEFORE triggering action
page.on('dialog', (d) => d.accept());
await page.getByRole('button', { name: 'Delete' }).click();
```

### Fix 2: Navigation Race

```typescript
// ❌ Click and immediately assert — page may not have loaded
await page.getByRole('link', { name: 'Dashboard' }).click();
await expect(page.getByRole('heading')).toHaveText('Dashboard'); // FLAKY

// ✅ Wait for URL first
await page.getByRole('link', { name: 'Dashboard' }).click();
await page.waitForURL('**/dashboard');
await expect(page.getByRole('heading')).toHaveText('Dashboard');
```

### Fix 3: Network-Dependent Assertions

```typescript
// ❌ Assert before API response arrives
await page.getByRole('button', { name: 'Save' }).click();
await expect(page.getByText('Saved')).toBeVisible(); // Might be too early

// ✅ Wait for the API response
const responsePromise = page.waitForResponse('**/api/save');
await page.getByRole('button', { name: 'Save' }).click();
await responsePromise;
await expect(page.getByText('Saved')).toBeVisible();
```

### Fix 4: Animation Interference

```typescript
// In playwright.config.ts or per-test
use: {
  // Disable CSS animations, transitions, and web animations
  contextOptions: {
    reducedMotion: 'reduce',
  },
}

// Or per screenshot
await expect(page).toHaveScreenshot({ animations: 'disabled' });
```

### Fix 5: Stale Element After Reload

```typescript
// ❌ Element reference becomes stale after page reload
const heading = page.getByRole('heading');
await page.reload();
await expect(heading).toBeVisible(); // May reference old DOM

// ✅ Playwright locators auto-resolve — this actually works fine
// But if using raw ElementHandle, re-query after reload
```

### Fix 6: Time-Dependent Tests

```typescript
// Mock the current date
await page.addInitScript(() => {
  const fixedDate = new Date('2025-01-15T10:00:00Z');
  const OrigDate = Date;
  // @ts-ignore
  Date = class extends OrigDate {
    constructor(...args: any[]) {
      if (args.length === 0) super(fixedDate.getTime());
      else super(...args);
    }
    static now() { return fixedDate.getTime(); }
  };
});
```
