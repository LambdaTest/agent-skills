# TestCafe — Advanced Patterns & Playbook

## Page Model Pattern

```typescript
import { Selector, t } from 'testcafe';

class LoginPage {
  emailInput = Selector('#email');
  passwordInput = Selector('#password');
  submitBtn = Selector('button').withText('Sign In');
  errorMsg = Selector('.error-message');

  async login(email: string, password: string) {
    await t
      .typeText(this.emailInput, email)
      .typeText(this.passwordInput, password)
      .click(this.submitBtn);
  }
}

class ProductPage {
  products = Selector('.product-card');
  cartCount = Selector('.cart-badge');
  sortDropdown = Selector('#sort');

  product(name: string) { return this.products.withText(name); }

  async addToCart(name: string) {
    await t.click(this.product(name).find('.add-to-cart'));
  }

  async sortBy(option: string) {
    await t.click(this.sortDropdown).click(Selector('option').withText(option));
  }
}

// Test
const login = new LoginPage();
const products = new ProductPage();

fixture('Shopping').page('http://localhost:3000');

test('Add product to cart', async t => {
  await login.login('user@test.com', 'password');
  await products.addToCart('Widget');
  await t.expect(products.cartCount.innerText).eql('1');
});
```

## Roles (Authentication State)

```typescript
import { Role } from 'testcafe';

const adminRole = Role('http://localhost:3000/login', async t => {
  await t.typeText('#email', 'admin@test.com')
         .typeText('#password', 'password')
         .click('#submit');
}, { preserveUrl: true });

test('Admin dashboard', async t => {
  await t.useRole(adminRole);
  await t.expect(Selector('h1').innerText).eql('Admin Dashboard');
});
```

## Request Hooks

```typescript
import { RequestMock, RequestLogger } from 'testcafe';

const mockAPI = RequestMock()
  .onRequestTo('/api/users')
  .respond({ users: [{ id: 1, name: 'Alice' }] }, 200, { 'content-type': 'application/json' });

const logger = RequestLogger('/api/', { logResponseBody: true, logResponseHeaders: true });

fixture('API Tests').page('http://localhost:3000').requestHooks(mockAPI, logger);

test('Uses mocked API', async t => {
  await t.expect(Selector('.user-name').innerText).eql('Alice');
  await t.expect(logger.contains(r => r.response.statusCode === 200)).ok();
});
```

## Client Functions & Custom Selectors

```typescript
import { ClientFunction } from 'testcafe';

const getLocalStorage = ClientFunction(key => localStorage.getItem(key));
const scrollToBottom = ClientFunction(() => window.scrollTo(0, document.body.scrollHeight));

test('Infinite scroll', async t => {
  await scrollToBottom();
  await t.expect(Selector('.item').count).gte(20);
});
```

## Anti-Patterns

- ❌ `await t.wait(5000)` — use smart assertions with auto-retry: `expect(el).ok()`
- ❌ Raw CSS strings in tests — use Page Model with named Selectors
- ❌ Skipping `Role` for auth — duplicated login logic across tests
- ❌ `ClientFunction` for simple assertions — use built-in Selector assertions
