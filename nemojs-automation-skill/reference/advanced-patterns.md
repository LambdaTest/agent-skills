# NemoJS — Advanced Patterns & Playbook

## Locator Strategies with JSON

```json
// locators/login.json
{
  "emailField": { "locator": "#email", "type": "css" },
  "passwordField": { "locator": "#password", "type": "css" },
  "submitBtn": { "locator": "button[type='submit']", "type": "css" },
  "errorMsg": { "locator": ".error-message", "type": "css" }
}
```

## View (Page Object)

```javascript
// views/login.js
module.exports = {
  locator: 'body.login-page',
  login: async function(nemo, email, password) {
    await nemo.view.login.emailField().sendKeys(email);
    await nemo.view.login.passwordField().sendKeys(password);
    await nemo.view.login.submitBtn().click();
    await nemo.driver.wait(until.urlContains('/dashboard'), 10000);
  },
  getError: async function(nemo) {
    return nemo.view.login.errorMsg().getText();
  }
};
```

## Test with Mocha Integration

```javascript
describe('Login @login', function() {
  let nemo;

  before(async function() {
    nemo = await Nemo();
  });

  after(async function() {
    await nemo?.driver?.quit();
  });

  it('should login with valid credentials', async function() {
    await nemo.driver.get(nemo.data.baseUrl + '/login');
    await nemo.view.login.login(nemo, 'admin@test.com', 'password');
    const url = await nemo.driver.getCurrentUrl();
    assert(url.includes('/dashboard'));
  });

  it('should show error for invalid login', async function() {
    await nemo.driver.get(nemo.data.baseUrl + '/login');
    await nemo.view.login.login(nemo, 'wrong@test.com', 'invalid');
    const error = await nemo.view.login.getError(nemo);
    assert.equal(error, 'Invalid credentials');
  });
});
```

## Configuration

```javascript
// config/nemo.js
module.exports = {
  driver: {
    browser: process.env.BROWSER || 'chrome',
  },
  data: {
    baseUrl: process.env.APP_URL || 'http://localhost:3000'
  },
  plugins: {
    view: { module: 'nemo-view', arguments: ['path:locators', 'path:views'] }
  }
};
```

## Anti-Patterns

- ❌ Hardcoded locators in test files — use JSON locator files
- ❌ `driver.sleep()` — use `driver.wait(until.elementLocated(...))` with explicit conditions
- ❌ Skipping nemo.view patterns for raw driver calls
- ❌ Missing error screenshots in `after()` hooks
