# Jest — Advanced Patterns & Playbook

## Custom Matchers

```javascript
expect.extend({
  toBeWithinRange(received, floor, ceiling) {
    const pass = received >= floor && received <= ceiling;
    return {
      pass,
      message: () => `expected ${received} to be within range ${floor} - ${ceiling}`
    };
  },
  toContainObject(received, argument) {
    const pass = this.equals(received, expect.arrayContaining([expect.objectContaining(argument)]));
    return { pass, message: () => `expected array to contain object ${JSON.stringify(argument)}` };
  }
});

test('value in range', () => expect(100).toBeWithinRange(90, 110));
```

## Advanced Mocking Patterns

```javascript
// Module factory mock with partial implementation
jest.mock('./api', () => ({
  ...jest.requireActual('./api'),
  fetchUser: jest.fn(),
  deleteUser: jest.fn()
}));

// Mock class with auto-mocked methods
jest.mock('./services/UserService');
const { UserService } = require('./services/UserService');
UserService.prototype.getUser.mockResolvedValue({ id: 1, name: 'Alice' });

// Spy on module method while keeping implementation
const utils = require('./utils');
jest.spyOn(utils, 'formatDate').mockReturnValue('2025-01-01');

// Manual mock with __mocks__ directory
// __mocks__/axios.js
module.exports = {
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  create: jest.fn(function () { return this; }),
  interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } }
};

// Timer mocking
jest.useFakeTimers();
test('debounced function', () => {
  const fn = jest.fn();
  const debounced = debounce(fn, 500);
  debounced(); debounced(); debounced();
  expect(fn).not.toHaveBeenCalled();
  jest.advanceTimersByTime(500);
  expect(fn).toHaveBeenCalledTimes(1);
});

// Mock date
jest.useFakeTimers({ now: new Date('2025-06-15T12:00:00Z') });
test('formats today', () => expect(getToday()).toBe('2025-06-15'));
```

## Async Testing Patterns

```javascript
// Async/await with error handling
test('rejects on network error', async () => {
  fetchUser.mockRejectedValueOnce(new Error('Network Error'));
  await expect(getUserProfile(1)).rejects.toThrow('Network Error');
});

// Testing streams/events
test('emits data events', (done) => {
  const stream = createReadStream('test.txt');
  const chunks = [];
  stream.on('data', chunk => chunks.push(chunk));
  stream.on('end', () => { expect(chunks.length).toBeGreaterThan(0); done(); });
});

// Retry logic testing
test('retries failed requests', async () => {
  fetchUser
    .mockRejectedValueOnce(new Error('timeout'))
    .mockRejectedValueOnce(new Error('timeout'))
    .mockResolvedValueOnce({ id: 1 });
  const result = await fetchWithRetry(fetchUser, 3);
  expect(result).toEqual({ id: 1 });
  expect(fetchUser).toHaveBeenCalledTimes(3);
});

// waitFor pattern with polling
const waitFor = (fn, { timeout = 5000, interval = 50 } = {}) =>
  new Promise((resolve, reject) => {
    const start = Date.now();
    const check = async () => {
      try { resolve(await fn()); }
      catch (e) {
        if (Date.now() - start >= timeout) reject(e);
        else setTimeout(check, interval);
      }
    };
    check();
  });
```

## Snapshot Testing

```javascript
// Inline snapshots (auto-filled by Jest)
test('user object shape', () => {
  expect(createUser('Alice')).toMatchInlineSnapshot(`
    { "id": Any<String>, "name": "Alice", "createdAt": Any<Date> }
  `);
});

// Property matchers for dynamic values
test('user with dynamic fields', () => {
  expect(createUser('Bob')).toMatchSnapshot({
    id: expect.any(String),
    createdAt: expect.any(Date)
  });
});

// Serializer for custom types
expect.addSnapshotSerializer({
  test: val => val && val.type === 'Component',
  serialize: (val) => `<${val.name} props={${JSON.stringify(val.props)}} />`
});
```

## React Testing with Testing Library

```javascript
import { render, screen, waitFor, within, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Complete component test
describe('TodoList', () => {
  const user = userEvent.setup();

  it('adds and removes todo items', async () => {
    render(<TodoList />);
    const input = screen.getByPlaceholderText('Add a todo');
    await user.type(input, 'Buy milk');
    await user.click(screen.getByRole('button', { name: /add/i }));
    expect(screen.getByText('Buy milk')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /delete/i }));
    expect(screen.queryByText('Buy milk')).not.toBeInTheDocument();
  });

  it('shows loading state', async () => {
    render(<TodoList />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByRole('progressbar')).not.toBeInTheDocument());
  });

  it('handles form validation', async () => {
    render(<TodoList />);
    await user.click(screen.getByRole('button', { name: /add/i }));
    expect(screen.getByRole('alert')).toHaveTextContent('Todo cannot be empty');
  });
});

// Context/Provider testing
const renderWithProviders = (ui, { initialState, ...options } = {}) => {
  const store = createStore(initialState);
  const Wrapper = ({ children }) => (
    <ThemeProvider><StoreProvider store={store}>{children}</StoreProvider></ThemeProvider>
  );
  return { ...render(ui, { wrapper: Wrapper, ...options }), store };
};

// Hook testing
import { renderHook, act } from '@testing-library/react';
test('useCounter', () => {
  const { result } = renderHook(() => useCounter(0));
  act(() => result.current.increment());
  expect(result.current.count).toBe(1);
});
```

## Performance Testing with Jest

```javascript
test('processes 10k items under 100ms', () => {
  const items = Array.from({ length: 10000 }, (_, i) => ({ id: i }));
  const start = performance.now();
  processItems(items);
  expect(performance.now() - start).toBeLessThan(100);
});
```

## Configuration Best Practices

```javascript
// jest.config.js — production-grade
module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  collectCoverageFrom: ['src/**/*.{js,jsx,ts,tsx}', '!src/**/*.d.ts', '!src/index.{js,ts}'],
  coverageThresholds: { global: { branches: 80, functions: 80, lines: 80, statements: 80 } },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|svg)$': '<rootDir>/__mocks__/fileMock.js'
  },
  setupFilesAfterSetup: ['<rootDir>/jest.setup.js'],
  transform: { '^.+\\.(ts|tsx)$': 'ts-jest' },
  testMatch: ['**/__tests__/**/*.(spec|test).[jt]s?(x)'],
  watchPlugins: ['jest-watch-typeahead/filename', 'jest-watch-typeahead/testname']
};
```

## Anti-Patterns

- ❌ `test('works', () => { myFunction(); })` — assertion-free tests prove nothing
- ❌ Testing implementation details (internal state, private methods)
- ❌ Snapshot overuse — large snapshots become meaningless; prefer targeted assertions
- ❌ `jest.mock()` at file level when only one test needs it — use `jest.spyOn` per-test instead
- ❌ `setTimeout` in tests — use `jest.useFakeTimers()` and `advanceTimersByTime`
- ❌ Shared mutable state between tests — always reset in `beforeEach`
