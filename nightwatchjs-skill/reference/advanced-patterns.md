# NightwatchJS — Advanced Patterns & Playbook

## Page Objects

```javascript
// pages/loginPage.js
module.exports = {
  url: '/login',
  elements: {
    emailInput: { selector: '#email' },
    passwordInput: { selector: '#password' },
    submitBtn: { selector: 'button[type="submit"]' },
    errorMsg: { selector: '.error-message' }
  },
  commands: [{
    login(email, password) {
      return this
        .setValue('@emailInput', email)
        .setValue('@passwordInput', password)
        .click('@submitBtn')
        .waitForElementVisible('.dashboard', 5000);
    },
    assertError(message) {
      return this.assert.containsText('@errorMsg', message);
    }
  }]
};

// Test using page object
module.exports = {
  'Login test': (browser) => {
    const login = browser.page.loginPage();
    login.navigate()
      .login('admin@test.com', 'password123')
      .assert.urlContains('/dashboard');
  }
};
```

## Custom Commands & Assertions

```javascript
// custom-commands/dragAndDrop.js
module.exports.command = function(source, target) {
  this.moveToElement(source, 10, 10)
    .mouseButtonDown(0)
    .moveToElement(target, 10, 10)
    .mouseButtonUp(0);
  return this;
};

// custom-assertions/hasMinLength.js
exports.assertion = function(selector, minLength, msg) {
  this.formatMessage = () => msg || `Element ${selector} has min length ${minLength}`;
  this.expected = () => `>= ${minLength} characters`;
  this.evaluate = (value) => value.length >= minLength;
  this.value = (result) => result.value;
  this.command = (callback) => this.api.getValue(selector, callback);
};

// Usage: browser.assert.hasMinLength('#password', 8)
```

## API Testing

```javascript
module.exports = {
  'API: Create user': async (browser) => {
    const response = await new Promise((resolve) => {
      browser.perform(() => {
        const http = require('http');
        const req = http.request({ hostname: 'localhost', port: 3000,
          path: '/api/users', method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        }, (res) => {
          let data = '';
          res.on('data', (c) => data += c);
          res.on('end', () => resolve({ status: res.statusCode, body: JSON.parse(data) }));
        });
        req.write(JSON.stringify({ name: 'Alice' }));
        req.end();
      });
    });
    browser.assert.equal(response.status, 201);
  }
};
```

## Configuration

```javascript
// nightwatch.conf.js
module.exports = {
  src_folders: ['tests'],
  page_objects_path: ['pages'],
  custom_commands_path: ['custom-commands'],
  custom_assertions_path: ['custom-assertions'],
  test_settings: {
    default: {
      launch_url: 'http://localhost:3000',
      desiredCapabilities: { browserName: 'chrome' },
      screenshots: { enabled: true, on_failure: true, path: 'screenshots' },
      globals: { waitForConditionTimeout: 10000, retryAssertionTimeout: 5000 }
    }
  }
};
```

## Anti-Patterns

- ❌ `browser.pause(5000)` — use `waitForElementVisible` or `waitForConditionTimeout`
- ❌ Raw selectors in test files — use page objects with `@element` syntax
- ❌ Callback hell — use `async/await` with Nightwatch 2+
- ❌ Missing `after` hook for browser cleanup
