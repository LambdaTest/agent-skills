# Jasmine — Advanced Playbook

## §1 Project Setup & Configuration

### Package Installation
```bash
npm install --save-dev jasmine jasmine-ts ts-node typescript @types/jasmine
npm install --save-dev jasmine-spec-reporter jasmine-console-reporter
npm install --save-dev c8  # Coverage
npx jasmine init
```

### jasmine.json (spec/support/)
```json
{
  "spec_dir": "spec",
  "spec_files": ["**/*[sS]pec.?(m)ts"],
  "helpers": ["helpers/**/*.?(m)ts"],
  "env": {
    "stopSpecOnExpectationFailure": false,
    "random": true,
    "forbidDuplicateNames": true,
    "failSpecWithNoExpectations": true
  }
}
```

### TypeScript Support
```json
// tsconfig.spec.json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/spec",
    "types": ["jasmine", "node"],
    "module": "commonjs"
  },
  "include": ["spec/**/*.ts", "src/**/*.ts"]
}
```

### Custom Reporter (spec/helpers/reporter.ts)
```typescript
import { SpecReporter, StacktraceOption } from 'jasmine-spec-reporter';

jasmine.getEnv().clearReporters();
jasmine.getEnv().addReporter(
  new SpecReporter({
    spec: {
      displayPending: true,
      displayDuration: true,
      displayStacktrace: StacktraceOption.PRETTY,
    },
    summary: {
      displayDuration: true,
      displaySuccessful: false,
      displayFailed: true,
      displayPending: true,
    },
  })
);
```

---

## §2 Spies — Complete API

### Spy Creation Patterns
```typescript
describe('Spy Patterns', () => {
  let userService: UserService;
  let logger: Logger;

  beforeEach(() => {
    userService = new UserService();
    logger = new Logger();
  });

  it('spyOn — track calls to existing method', () => {
    spyOn(userService, 'save').and.returnValue(Promise.resolve({ id: 1 }));

    userService.save({ name: 'Alice' });

    expect(userService.save).toHaveBeenCalledWith(
      jasmine.objectContaining({ name: 'Alice' })
    );
    expect(userService.save).toHaveBeenCalledTimes(1);
  });

  it('and.callThrough — spy + execute real implementation', () => {
    spyOn(logger, 'info').and.callThrough();
    logger.info('test message');
    expect(logger.info).toHaveBeenCalled();
    // Real method also executed
  });

  it('and.callFake — replace with custom logic', () => {
    spyOn(userService, 'getById').and.callFake((id: number) => {
      if (id === 1) return { id: 1, name: 'Alice' };
      throw new Error('Not found');
    });

    expect(userService.getById(1)).toEqual({ id: 1, name: 'Alice' });
    expect(() => userService.getById(999)).toThrowError('Not found');
  });

  it('and.returnValues — different values per call', () => {
    spyOn(userService, 'getNext')
      .and.returnValues('first', 'second', 'third');

    expect(userService.getNext()).toBe('first');
    expect(userService.getNext()).toBe('second');
    expect(userService.getNext()).toBe('third');
  });

  it('and.throwError — simulate failures', () => {
    spyOn(userService, 'save').and.throwError('Database connection failed');
    expect(() => userService.save({})).toThrowError('Database connection failed');
  });
});
```

### createSpyObj — Mock Objects
```typescript
describe('createSpyObj Patterns', () => {
  it('creates mock with methods and properties', () => {
    const httpClient = jasmine.createSpyObj('HttpClient',
      ['get', 'post', 'put', 'delete'],  // methods
      { baseUrl: 'http://api.test.com' }   // properties
    );

    httpClient.get.and.returnValue(Promise.resolve({ data: [] }));
    httpClient.post.and.returnValue(Promise.resolve({ id: 1 }));

    const service = new ApiService(httpClient);
    expect(httpClient.baseUrl).toBe('http://api.test.com');
  });

  it('tracks all call details', () => {
    const spy = jasmine.createSpyObj('Notifier', ['send']);
    spy.send('hello', { urgent: true });
    spy.send('world');

    expect(spy.send.calls.count()).toBe(2);
    expect(spy.send.calls.argsFor(0)).toEqual(['hello', { urgent: true }]);
    expect(spy.send.calls.argsFor(1)).toEqual(['world']);
    expect(spy.send.calls.mostRecent().args).toEqual(['world']);
    expect(spy.send.calls.allArgs()).toEqual([
      ['hello', { urgent: true }],
      ['world'],
    ]);
  });

  it('resets spy tracking', () => {
    const spy = jasmine.createSpy('callback');
    spy('first');
    spy.calls.reset();
    expect(spy).not.toHaveBeenCalled();
  });
});
```

---

## §3 Async Testing Patterns

### Async/Await
```typescript
describe('Async Patterns', () => {
  let apiService: ApiService;

  beforeEach(() => {
    apiService = new ApiService();
  });

  it('async/await — preferred pattern', async () => {
    spyOn(apiService, 'fetchUsers').and.resolveTo([
      { id: 1, name: 'Alice' },
    ]);

    const users = await apiService.fetchUsers();
    expect(users).toHaveSize(1);
    expect(users[0].name).toBe('Alice');
  });

  it('async rejection', async () => {
    spyOn(apiService, 'fetchUsers').and.rejectWith(new Error('Network error'));

    await expectAsync(apiService.fetchUsers()).toBeRejectedWithError('Network error');
  });

  it('expectAsync matchers', async () => {
    const promise = apiService.fetchUsers();

    await expectAsync(promise).toBeResolved();
    await expectAsync(promise).toBeResolvedTo([]);
    // or
    await expectAsync(failingPromise).toBeRejected();
    await expectAsync(failingPromise).toBeRejectedWith(jasmine.objectContaining({ code: 500 }));
  });
});
```

### Clock Control
```typescript
describe('Timer-based code', () => {
  beforeEach(() => {
    jasmine.clock().install();
  });

  afterEach(() => {
    jasmine.clock().uninstall();
  });

  it('controls setTimeout', () => {
    const callback = jasmine.createSpy('timeout');
    setTimeout(callback, 1000);

    jasmine.clock().tick(999);
    expect(callback).not.toHaveBeenCalled();

    jasmine.clock().tick(1);
    expect(callback).toHaveBeenCalled();
  });

  it('controls setInterval', () => {
    const callback = jasmine.createSpy('interval');
    setInterval(callback, 500);

    jasmine.clock().tick(1500);
    expect(callback).toHaveBeenCalledTimes(3);
  });

  it('mocks Date', () => {
    const baseDate = new Date(2025, 0, 1);
    jasmine.clock().mockDate(baseDate);

    expect(new Date().getFullYear()).toBe(2025);

    jasmine.clock().tick(86400000); // 1 day
    expect(new Date().getDate()).toBe(2);
  });

  it('debounce testing', () => {
    const search = jasmine.createSpy('search');
    const debounced = debounce(search, 300);

    debounced('hel');
    debounced('hell');
    debounced('hello');

    jasmine.clock().tick(300);
    expect(search).toHaveBeenCalledTimes(1);
    expect(search).toHaveBeenCalledWith('hello');
  });
});
```

---

## §4 Custom Matchers

### Creating Domain-Specific Matchers
```typescript
// spec/helpers/custom-matchers.ts
const customMatchers: jasmine.CustomMatcherFactories = {
  toBeValidEmail(): jasmine.CustomMatcher {
    return {
      compare(actual: string): jasmine.CustomMatcherResult {
        const pass = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(actual);
        return {
          pass,
          message: pass
            ? `Expected "${actual}" not to be a valid email`
            : `Expected "${actual}" to be a valid email`,
        };
      },
    };
  },

  toBeWithinRange(): jasmine.CustomMatcher {
    return {
      compare(actual: number, floor: number, ceiling: number) {
        const pass = actual >= floor && actual <= ceiling;
        return {
          pass,
          message: `Expected ${actual} to be within [${floor}, ${ceiling}]`,
        };
      },
    };
  },

  toHaveBeenCalledWithObject(): jasmine.CustomMatcher {
    return {
      compare(actual: jasmine.Spy, expected: object) {
        const calls = actual.calls.allArgs();
        const pass = calls.some((args: any[]) =>
          args.some((arg: any) => jasmine.matchersUtil.equals(arg, jasmine.objectContaining(expected)))
        );
        return {
          pass,
          message: pass
            ? `Expected spy not to have been called with object containing ${JSON.stringify(expected)}`
            : `Expected spy to have been called with object containing ${JSON.stringify(expected)}`,
        };
      },
    };
  },
};

beforeEach(() => {
  jasmine.addMatchers(customMatchers);
});

// Usage
describe('Custom Matchers', () => {
  it('validates email', () => {
    expect('user@example.com').toBeValidEmail();
    expect('invalid').not.toBeValidEmail();
  });

  it('checks range', () => {
    expect(5).toBeWithinRange(1, 10);
    expect(15).not.toBeWithinRange(1, 10);
  });
});
```

### Asymmetric Matchers
```typescript
describe('Asymmetric Matchers', () => {
  it('partial object matching', () => {
    const user = { id: 1, name: 'Alice', createdAt: new Date(), token: 'abc123' };

    expect(user).toEqual(jasmine.objectContaining({
      name: 'Alice',
      id: jasmine.any(Number),
    }));
  });

  it('array containing', () => {
    const tags = ['javascript', 'testing', 'jasmine'];
    expect(tags).toEqual(jasmine.arrayContaining(['testing', 'jasmine']));
  });

  it('string matching', () => {
    expect('Hello World').toEqual(jasmine.stringMatching(/^Hello/));
  });

  it('nested matching', () => {
    const response = {
      data: { users: [{ name: 'Alice' }, { name: 'Bob' }] },
      meta: { total: 2 },
    };

    expect(response).toEqual({
      data: jasmine.objectContaining({
        users: jasmine.arrayContaining([
          jasmine.objectContaining({ name: 'Alice' }),
        ]),
      }),
      meta: jasmine.any(Object),
    });
  });
});
```

---

## §5 Test Organization — Suites & Context

### Nested Describe with Shared State
```typescript
describe('ShoppingCart', () => {
  let cart: ShoppingCart;

  beforeEach(() => {
    cart = new ShoppingCart();
  });

  describe('when empty', () => {
    it('has zero items', () => {
      expect(cart.itemCount).toBe(0);
    });

    it('has zero total', () => {
      expect(cart.total).toBe(0);
    });

    it('returns empty array for items', () => {
      expect(cart.items).toEqual([]);
    });
  });

  describe('with items', () => {
    beforeEach(() => {
      cart.add({ id: 'A', name: 'Widget', price: 9.99, quantity: 2 });
      cart.add({ id: 'B', name: 'Gadget', price: 19.99, quantity: 1 });
    });

    it('calculates correct total', () => {
      expect(cart.total).toBeCloseTo(39.97, 2);
    });

    it('tracks item count', () => {
      expect(cart.itemCount).toBe(3);
    });

    describe('applying discount', () => {
      it('reduces total by percentage', () => {
        cart.applyDiscount(10); // 10%
        expect(cart.total).toBeCloseTo(35.97, 2);
      });

      it('rejects invalid discount', () => {
        expect(() => cart.applyDiscount(-5)).toThrowError();
        expect(() => cart.applyDiscount(101)).toThrowError();
      });
    });

    describe('removing items', () => {
      it('removes by id', () => {
        cart.remove('A');
        expect(cart.itemCount).toBe(1);
        expect(cart.total).toBeCloseTo(19.99, 2);
      });

      it('throws for unknown id', () => {
        expect(() => cart.remove('Z')).toThrowError('Item not found');
      });
    });
  });
});
```

### Focused & Excluded Tests
```typescript
// Focus: only run this suite (remove before commit!)
fdescribe('Debugging suite', () => {
  fit('only this test runs', () => { });
});

// Exclude: skip this
xdescribe('Broken suite', () => {
  xit('skipped test', () => { });
});

// Pending: no function body
it('TODO: implement this');
```

---

## §6 Mocking Fetch & Modules

### Fetch Mocking
```typescript
describe('API Client', () => {
  let client: ApiClient;

  beforeEach(() => {
    client = new ApiClient('https://api.test.com');
  });

  it('fetches and parses JSON', async () => {
    const mockResponse = { id: 1, name: 'Alice' };
    spyOn(globalThis, 'fetch').and.resolveTo(
      new Response(JSON.stringify(mockResponse), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    const result = await client.getUser(1);

    expect(fetch).toHaveBeenCalledWith(
      'https://api.test.com/users/1',
      jasmine.objectContaining({ method: 'GET' })
    );
    expect(result).toEqual(mockResponse);
  });

  it('handles network errors', async () => {
    spyOn(globalThis, 'fetch').and.rejectWith(new TypeError('Failed to fetch'));

    await expectAsync(client.getUser(1))
      .toBeRejectedWithError('Failed to fetch');
  });

  it('handles HTTP errors', async () => {
    spyOn(globalThis, 'fetch').and.resolveTo(
      new Response('Not Found', { status: 404 })
    );

    await expectAsync(client.getUser(999))
      .toBeRejectedWithError(/404/);
  });

  it('sends POST with body', async () => {
    spyOn(globalThis, 'fetch').and.resolveTo(
      new Response(JSON.stringify({ id: 2 }), { status: 201 })
    );

    await client.createUser({ name: 'Bob' });

    expect(fetch).toHaveBeenCalledWith(
      'https://api.test.com/users',
      jasmine.objectContaining({
        method: 'POST',
        body: JSON.stringify({ name: 'Bob' }),
      })
    );
  });
});
```

---

## §7 Browser Testing with Karma

### Karma + Jasmine for DOM Testing
```typescript
describe('Modal Component (Browser)', () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.removeChild(container);
  });

  it('shows modal on trigger', () => {
    const modal = new Modal(container);
    modal.open();

    const overlay = container.querySelector('.modal-overlay');
    expect(overlay).not.toBeNull();
    expect(overlay!.classList.contains('visible')).toBeTrue();
  });

  it('closes on escape key', () => {
    const modal = new Modal(container);
    modal.open();

    const event = new KeyboardEvent('keydown', { key: 'Escape' });
    document.dispatchEvent(event);

    const overlay = container.querySelector('.modal-overlay');
    expect(overlay!.classList.contains('visible')).toBeFalse();
  });

  it('traps focus inside modal', () => {
    const modal = new Modal(container);
    modal.open();

    const focusable = container.querySelectorAll('button, input, [tabindex]');
    expect(document.activeElement).toBe(focusable[0]);
  });
});
```

---

## §8 CI/CD Integration

### GitHub Actions
```yaml
name: Jasmine Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - run: npm ci

      - name: Run Jasmine Tests
        run: npx c8 --reporter=lcov --reporter=text npx jasmine --config=spec/support/jasmine.json

      - name: Check Coverage
        run: |
          npx c8 check-coverage --lines 80 --functions 80 --branches 75

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage
          path: coverage/

  browser-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }
      - run: npm ci
      - run: npx karma start karma.conf.js --single-run --browsers ChromeHeadless
        env:
          CI: true
```

### package.json Scripts
```json
{
  "scripts": {
    "test": "jasmine --config=spec/support/jasmine.json",
    "test:watch": "nodemon --exec 'npm test' --ext ts,js",
    "test:coverage": "c8 --reporter=lcov --reporter=text npm test",
    "test:browser": "karma start --single-run",
    "test:ci": "c8 --check-coverage --lines 80 npm test"
  }
}
```

---

## §9 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `No specs found` | Spec files don't match pattern | Check `spec_files` glob in jasmine.json; ensure files end in `.spec.ts` |
| 2 | `fdescribe`/`fit` left in code | Focused test committed accidentally | Add lint rule or git hook to block focused tests |
| 3 | Spy not called as expected | Method called before spy attached | Attach `spyOn` before invoking the code under test |
| 4 | `jasmine.clock()` leaks between tests | Missing `uninstall()` | Always pair `install()` in `beforeEach` with `uninstall()` in `afterEach` |
| 5 | Async test timeout | Promise never resolves or rejects | Check `and.resolveTo`/`and.rejectWith`; increase `DEFAULT_TIMEOUT_INTERVAL` |
| 6 | `Expected spy to have been called with` fails | Object reference mismatch | Use `jasmine.objectContaining()` for partial matching |
| 7 | Random test failures | Tests depend on execution order | Enable `random: true` in config; fix shared state in `beforeEach` |
| 8 | Custom matcher not found | Matcher not registered in `beforeEach` | Call `jasmine.addMatchers()` in a `beforeEach` block or helper file |
| 9 | `calls.reset()` doesn't clear return value | Reset only clears call tracking | Re-configure `and.returnValue` after reset if needed |
| 10 | TypeScript types missing for custom matchers | No type declarations | Create `jasmine.d.ts` with `declare namespace jasmine` extending Matchers |
| 11 | `createSpyObj` method not stubbed | Method called but no `and.returnValue` | Configure return values for all methods that will be called |
| 12 | Tests pass alone, fail together | Shared mutable state between suites | Use `beforeEach` for fresh instances; avoid module-level variables |

---

## §10 Best Practices Checklist

1. Set `random: true` — catch test ordering dependencies early
2. Set `failSpecWithNoExpectations: true` — prevent empty tests from passing
3. Use `createSpyObj` for mock objects — cleaner than manual spyOn
4. Use `jasmine.objectContaining` — avoid brittle exact-match assertions
5. Always pair `clock().install()` with `uninstall()` — prevent timer leaks
6. Use `async`/`await` over `done()` callback — cleaner, better error messages
7. Use `expectAsync()` for promise assertions — native Jasmine 3.x+ support
8. Create custom matchers for domain logic — makes tests more readable
9. Use nested `describe` blocks — organize tests by state/context
10. Clean up DOM in `afterEach` — prevent element leaks in browser tests
11. Use `and.returnValues` for sequential calls — test multi-step flows
12. Keep spies in `beforeEach` — Jasmine auto-resets between specs
13. Use spec reporter for CI — better output than default progress reporter
14. Never commit `fdescribe`/`fit` — add pre-commit hook to catch focused tests
