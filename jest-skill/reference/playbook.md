# Jest — Advanced Implementation Playbook

## §1 — Production Config

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: ['**/*.test.{js,ts}'],
  transform: { '^.+\\.tsx?$': 'ts-jest' },
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'json-summary'],
  coverageThreshold: { global: { branches: 80, functions: 80, lines: 80, statements: 80 } },
  coveragePathIgnorePatterns: ['/node_modules/', '/tests/', '/dist/'],
  setupFilesAfterSetup: ['<rootDir>/tests/setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss)$': 'identity-obj-proxy',
  },
  verbose: true,
  testTimeout: 10000,
  maxWorkers: '50%',  // Use half CPU cores
};
```

```javascript
// jest.config.js — for React projects
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterSetup: ['@testing-library/jest-dom', '<rootDir>/tests/setup.ts'],
  transform: { '^.+\\.(t|j)sx?$': ['@swc/jest'] },  // Faster than ts-jest
  moduleNameMapper: {
    '\\.(css|scss)$': 'identity-obj-proxy',
    '\\.(jpg|png|svg)$': '<rootDir>/tests/__mocks__/fileMock.js',
  },
};
```

## §2 — Mocking Deep Dive

```javascript
// Full module mock
jest.mock('./database', () => ({
  query: jest.fn(),
  connect: jest.fn().mockResolvedValue(true),
}));

// Partial mock (keep real implementations for some functions)
jest.mock('./utils', () => ({
  ...jest.requireActual('./utils'),
  fetchData: jest.fn(),
}));

// Manual mock — __mocks__/axios.js
module.exports = {
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  create: jest.fn(function() { return this; }),
};

// Spy with chained responses
const spy = jest.spyOn(userService, 'findById')
  .mockResolvedValueOnce({ id: 1, name: 'Alice' })
  .mockResolvedValueOnce(null);

expect(await userService.findById(1)).toEqual({ id: 1, name: 'Alice' });
expect(await userService.findById(999)).toBeNull();
spy.mockRestore();

// Timer mocking
jest.useFakeTimers();
const callback = jest.fn();
setTimeout(callback, 5000);
jest.advanceTimersByTime(5000);
expect(callback).toHaveBeenCalledTimes(1);
jest.useRealTimers();

// Mock Date
jest.useFakeTimers({ now: new Date('2024-12-25T00:00:00Z') });
expect(new Date().toISOString()).toBe('2024-12-25T00:00:00.000Z');

// Mock environment variables
const originalEnv = process.env;
beforeEach(() => { process.env = { ...originalEnv, API_KEY: 'test-key' }; });
afterEach(() => { process.env = originalEnv; });

// Mock console
const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
afterEach(() => consoleSpy.mockRestore());
```

## §3 — Async Patterns

```javascript
// Async/await
test('fetches user', async () => {
  const user = await fetchUser(1);
  expect(user.name).toBe('Alice');
});

// Rejection
test('rejects on not found', async () => {
  await expect(fetchUser(999)).rejects.toThrow('Not found');
});

// Resolves/rejects matchers
test('resolves with data', () => {
  return expect(fetchUser(1)).resolves.toMatchObject({ name: 'Alice' });
});

// Testing event emitters
test('emits data event', (done) => {
  const emitter = createDataStream();
  emitter.on('data', (data) => {
    expect(data).toBeDefined();
    done();
  });
  emitter.start();
});

// Testing streams / callbacks with timeout
test('stream completes', async () => {
  const result = await new Promise((resolve, reject) => {
    const chunks = [];
    stream.on('data', chunk => chunks.push(chunk));
    stream.on('end', () => resolve(Buffer.concat(chunks)));
    stream.on('error', reject);
  });
  expect(result.length).toBeGreaterThan(0);
});
```

## §4 — Table-Driven Tests (test.each)

```javascript
// Array format
test.each([
  ['admin@test.com', 'pass123', true],
  ['user@test.com', 'wrong', false],
  ['', '', false],
  ['invalid-email', 'pass', false],
])('login(%s, %s) => %s', async (email, password, expected) => {
  const result = await authService.login(email, password);
  expect(result.success).toBe(expected);
});

// Tagged template literal
test.each`
  input         | expected
  ${1}          | ${'1'}
  ${null}       | ${''}
  ${undefined}  | ${''}
  ${'hello'}    | ${'hello'}
`('toString($input) => $expected', ({ input, expected }) => {
  expect(toString(input)).toBe(expected);
});

// describe.each for grouped tests
describe.each([
  { role: 'admin', canDelete: true, canEdit: true },
  { role: 'editor', canDelete: false, canEdit: true },
  { role: 'viewer', canDelete: false, canEdit: false },
])('$role permissions', ({ role, canDelete, canEdit }) => {
  test(`canDelete is ${canDelete}`, () => {
    expect(getPermissions(role).canDelete).toBe(canDelete);
  });
  test(`canEdit is ${canEdit}`, () => {
    expect(getPermissions(role).canEdit).toBe(canEdit);
  });
});
```

## §5 — Custom Matchers

```javascript
// tests/setup.ts
expect.extend({
  toBeWithinRange(received, floor, ceiling) {
    const pass = received >= floor && received <= ceiling;
    return {
      message: () => `expected ${received} to be within [${floor}, ${ceiling}]`,
      pass,
    };
  },
  toBeValidEmail(received) {
    const pass = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(received);
    return {
      message: () => `expected ${received} to be a valid email`,
      pass,
    };
  },
  toContainObject(received, argument) {
    const pass = received.some(item =>
      Object.keys(argument).every(key => item[key] === argument[key])
    );
    return {
      message: () => `expected array to contain object ${JSON.stringify(argument)}`,
      pass,
    };
  },
});

// TypeScript declaration
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeWithinRange(floor: number, ceiling: number): R;
      toBeValidEmail(): R;
      toContainObject(obj: Record<string, unknown>): R;
    }
  }
}

// Usage
expect(response.status).toBeWithinRange(200, 299);
expect(user.email).toBeValidEmail();
expect(users).toContainObject({ name: 'Alice', role: 'admin' });
```

## §6 — React Testing (Testing Library)

```javascript
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('submits login form', async () => {
  const user = userEvent.setup();
  const onSubmit = jest.fn();
  render(<LoginForm onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText('Email'), 'user@test.com');
  await user.type(screen.getByLabelText('Password'), 'pass');
  await user.click(screen.getByRole('button', { name: 'Sign In' }));

  await waitFor(() => {
    expect(onSubmit).toHaveBeenCalledWith({ email: 'user@test.com', password: 'pass' });
  });
});

test('shows validation error', async () => {
  const user = userEvent.setup();
  render(<LoginForm onSubmit={jest.fn()} />);
  await user.click(screen.getByRole('button', { name: 'Sign In' }));
  expect(screen.getByText('Email is required')).toBeInTheDocument();
});

// Testing custom hooks
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

test('useCounter increments', () => {
  const { result } = renderHook(() => useCounter(0));
  act(() => { result.current.increment(); });
  expect(result.current.count).toBe(1);
});

// Testing with context providers
const AllProviders = ({ children }) => (
  <ThemeProvider theme="dark">
    <AuthProvider user={mockUser}>
      {children}
    </AuthProvider>
  </ThemeProvider>
);

test('renders with providers', () => {
  render(<Dashboard />, { wrapper: AllProviders });
  expect(screen.getByText('Welcome, Alice')).toBeInTheDocument();
});
```

## §7 — Snapshot Testing

```javascript
import renderer from 'react-test-renderer';

test('Header matches snapshot', () => {
  const tree = renderer.create(<Header title="Hello" user={mockUser} />).toJSON();
  expect(tree).toMatchSnapshot();
});

// Inline snapshot (no file)
test('formats date', () => {
  expect(formatDate('2024-01-15')).toMatchInlineSnapshot(`"January 15, 2024"`);
});

// Property matchers (ignore dynamic fields)
test('user snapshot with dynamic id', () => {
  expect(createUser('Alice')).toMatchSnapshot({
    id: expect.any(String),
    createdAt: expect.any(Date),
  });
});

// Update: jest --updateSnapshot
```

## §8 — Testing API Services

```javascript
import axios from 'axios';
import { UserService } from './UserService';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('UserService', () => {
  const service = new UserService();

  afterEach(() => jest.clearAllMocks());

  test('getUser returns user data', async () => {
    mockedAxios.get.mockResolvedValue({ data: { id: 1, name: 'Alice' } });
    const user = await service.getUser(1);
    expect(user).toEqual({ id: 1, name: 'Alice' });
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/users/1');
  });

  test('getUser throws on 404', async () => {
    mockedAxios.get.mockRejectedValue({ response: { status: 404 } });
    await expect(service.getUser(999)).rejects.toThrow('User not found');
  });

  test('createUser sends POST', async () => {
    mockedAxios.post.mockResolvedValue({ data: { id: 2, name: 'Bob' } });
    const user = await service.createUser({ name: 'Bob' });
    expect(user.id).toBe(2);
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/users', { name: 'Bob' });
  });
});
```

## §9 — Global Setup/Teardown & Projects

```javascript
// jest.config.js — multi-project setup
module.exports = {
  projects: [
    {
      displayName: 'unit',
      testMatch: ['<rootDir>/tests/unit/**/*.test.ts'],
      testEnvironment: 'node',
    },
    {
      displayName: 'integration',
      testMatch: ['<rootDir>/tests/integration/**/*.test.ts'],
      testEnvironment: 'node',
      globalSetup: '<rootDir>/tests/integration/globalSetup.ts',
      globalTeardown: '<rootDir>/tests/integration/globalTeardown.ts',
    },
    {
      displayName: 'react',
      testMatch: ['<rootDir>/src/**/*.test.tsx'],
      testEnvironment: 'jsdom',
      setupFilesAfterSetup: ['@testing-library/jest-dom'],
    },
  ],
};

// tests/integration/globalSetup.ts
export default async function globalSetup() {
  // Start test database, seed data, etc.
  process.env.DATABASE_URL = 'postgresql://localhost:5432/test';
}

// tests/integration/globalTeardown.ts
export default async function globalTeardown() {
  // Clean up test database
}
```

## §10 — CI/CD Integration

```yaml
# GitHub Actions
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm test -- --ci --coverage --maxWorkers=2
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage/lcov.info
      - name: Check thresholds
        run: |
          COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage $COVERAGE% is below 80%"
            exit 1
          fi
```

## §11 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Mock not working | Mock path doesn't match import | Verify `jest.mock()` path matches exactly |
| Async test timeout | Unresolved promise or missing await | Add `await`, increase `testTimeout` |
| State leaking between tests | Shared mutable state | Use `beforeEach` + `jest.clearAllMocks()` |
| `act()` warnings | State update not wrapped | Use `waitFor()` or `await act(async () => ...)` |
| Snapshot too large | Entire component tree serialized | Use `toMatchInlineSnapshot()` or target subcomponents |
| ESM imports fail | node_modules not transformed | Add package to `transformIgnorePatterns` |
| `Cannot find module` | Path alias not configured | Add to `moduleNameMapper` in config |
| Slow test suite | Too many workers / no cache | Use `--maxWorkers=50%`, enable `cacheDirectory` |
| `ReferenceError: fetch` | Node < 18 or jsdom env | Use `undici` or mock `global.fetch` |
| Mock doesn't reset | Missing cleanup | Add `jest.restoreAllMocks()` in `afterEach` |

## §12 — Best Practices Checklist

- ✅ Use `beforeEach` + `jest.clearAllMocks()` to prevent leaks
- ✅ Mock external dependencies, never internal logic
- ✅ Use `toMatchObject` for partial object matching
- ✅ Use `expect.any(Type)` and `expect.stringContaining()` for flexible assertions
- ✅ Use `--watch` during development for fast feedback
- ✅ Set coverage thresholds in config as quality gates
- ✅ Use `jest.spyOn` over manual mocks when possible
- ✅ Test behavior, not implementation details
- ✅ Use `test.each` for parameterized/table-driven tests
- ✅ Use `userEvent` over `fireEvent` for realistic user interactions
- ✅ Use `renderHook` for testing custom React hooks
- ✅ Use multi-project config to separate unit/integration/component
- ✅ Use `@swc/jest` instead of `ts-jest` for 2-5x faster transforms
- ✅ Use `--ci` flag in CI (disables interactive watch mode)
- ✅ Structure: `tests/unit/`, `tests/integration/`, `src/**/*.test.tsx`
