# WebdriverIO — Advanced Patterns

## Custom Commands

```javascript
browser.addCommand('loginAs', async function(email, password) {
    await browser.url('/login');
    await $('[data-testid="email"]').setValue(email);
    await $('[data-testid="password"]').setValue(password);
    await $('[data-testid="submit"]').click();
    await browser.waitUntil(async () =>
        (await browser.getUrl()).includes('/dashboard')
    );
});
```

## Network Mocking

```javascript
const mock = await browser.mock('**/api/users');
mock.respond([{ id: 1, name: 'Test User' }]);

// After test
expect(mock).toBeRequestedTimes(1);
```

## Visual Regression

```bash
npm install @wdio/visual-service --save-dev
```

```javascript
await expect(browser).toMatchScreenshot('login-page', { /* options */ });
await expect($('[data-testid="header"]')).toMatchElementSnapshot('header');
```
