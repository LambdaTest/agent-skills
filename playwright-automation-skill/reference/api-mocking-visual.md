# API Mocking & Visual Regression — Playwright

## Table of Contents
- API Mocking Patterns
- Visual Regression Patterns

---

## API Mocking Patterns

### Mock an Endpoint

```typescript
await page.route('**/api/users', (route) =>
  route.fulfill({
    status: 200,
    json: [{ id: 1, name: 'Mock User', email: 'mock@test.com' }],
  })
);
```

### Modify Real Response (Pass-Through)

```typescript
await page.route('**/api/products', async (route) => {
  const response = await route.fetch(); // Call real API
  const data = await response.json();
  // Inject test data
  data.push({ id: 999, name: 'Test Product', price: 0 });
  await route.fulfill({ json: data });
});
```

### Block Resources (Faster Tests)

```typescript
// Block images, fonts, analytics
await page.route('**/*.{png,jpg,jpeg,gif,svg,woff,woff2}', (route) => route.abort());
await page.route('**/analytics/**', (route) => route.abort());
await page.route('**/ads/**', (route) => route.abort());
```

### Wait for Network After Action

```typescript
const responsePromise = page.waitForResponse('**/api/save');
await page.getByRole('button', { name: 'Save' }).click();
const response = await responsePromise;
expect(response.status()).toBe(200);
```

### Simulate Errors

```typescript
// Server error
await page.route('**/api/checkout', (route) =>
  route.fulfill({ status: 500, json: { error: 'Internal server error' } })
);

// Network failure
await page.route('**/api/checkout', (route) => route.abort('connectionrefused'));

// Slow response
await page.route('**/api/data', async (route) => {
  await new Promise((r) => setTimeout(r, 5000)); // 5s delay
  await route.fulfill({ json: { data: 'slow' } });
});
```

### Mock GraphQL

```typescript
await page.route('**/graphql', async (route) => {
  const body = JSON.parse(route.request().postData() || '{}');

  if (body.operationName === 'GetUser') {
    await route.fulfill({
      json: { data: { user: { id: '1', name: 'Test User' } } },
    });
  } else {
    await route.fallback(); // Let other operations pass through
  }
});
```

---

## Visual Regression Patterns

### Page-Level Screenshot

```typescript
await expect(page).toHaveScreenshot('homepage.png', {
  maxDiffPixelRatio: 0.01, // Allow 1% pixel difference
  animations: 'disabled',
});
```

### Component-Level Screenshot

```typescript
const card = page.getByTestId('product-card').first();
await expect(card).toHaveScreenshot('product-card.png');
```

### Mask Dynamic Content

```typescript
await expect(page).toHaveScreenshot('dashboard.png', {
  mask: [
    page.locator('.timestamp'),
    page.locator('.avatar'),
    page.locator('[data-testid="random-banner"]'),
  ],
  animations: 'disabled',
});
```

### Full Page Screenshot

```typescript
await expect(page).toHaveScreenshot('full-page.png', {
  fullPage: true,
  animations: 'disabled',
});
```

### Update Baselines

```bash
# Regenerate all baseline screenshots
npx playwright test --update-snapshots

# Update for specific test file only
npx playwright test tests/visual.spec.ts --update-snapshots
```

### Cross-Browser Visual Testing

Screenshots differ between browsers. Playwright stores baselines per project:

```
tests/
  visual.spec.ts-snapshots/
    homepage-chromium.png
    homepage-firefox.png
    homepage-webkit.png
```

Each project gets its own baseline automatically.
