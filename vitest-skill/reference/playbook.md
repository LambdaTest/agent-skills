# Vitest — Advanced Implementation Playbook

## §1 — Production Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': resolve(__dirname, 'src') },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.test.ts', 'tests/**/*.test.tsx'],
    exclude: ['tests/e2e/**', 'node_modules/**'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov', 'json-summary'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.d.ts', 'src/**/index.ts', 'src/**/*.stories.tsx'],
      thresholds: { lines: 80, branches: 75, functions: 80, statements: 80 },
    },
    pool: 'threads',
    poolOptions: { threads: { maxThreads: 4, minThreads: 1 } },
    reporters: ['default', 'json', 'junit'],
    outputFile: {
      json: './test-results/results.json',
      junit: './test-results/junit.xml',
    },
    typecheck: { enabled: true },
  },
});
```

### Workspace Config (Monorepo)

```typescript
// vitest.workspace.ts
import { defineWorkspace } from 'vitest/config';

export default defineWorkspace([
  { extends: './vitest.config.ts', test: { name: 'unit', include: ['tests/unit/**/*.test.ts'] } },
  { extends: './vitest.config.ts', test: { name: 'integration', include: ['tests/integration/**/*.test.ts'], environment: 'node' } },
  { extends: './vitest.config.ts', test: { name: 'components', include: ['tests/components/**/*.test.tsx'], environment: 'jsdom' } },
]);
```

### Setup File

```typescript
// tests/setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  vi.restoreAllMocks();
});

// Global mocks
vi.stubGlobal('ResizeObserver', vi.fn().mockImplementation(() => ({
  observe: vi.fn(), unobserve: vi.fn(), disconnect: vi.fn(),
})));

vi.stubGlobal('IntersectionObserver', vi.fn().mockImplementation(() => ({
  observe: vi.fn(), unobserve: vi.fn(), disconnect: vi.fn(),
})));

Object.defineProperty(window, 'matchMedia', {
  value: vi.fn().mockImplementation(query => ({
    matches: false, media: query,
    addEventListener: vi.fn(), removeEventListener: vi.fn(),
  })),
});
```

## §2 — Mocking Patterns

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Module mock
vi.mock('@/services/api', () => ({
  fetchUser: vi.fn(),
  fetchProducts: vi.fn(),
}));

import { fetchUser, fetchProducts } from '@/services/api';
const mockFetchUser = vi.mocked(fetchUser);

describe('UserService', () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it('should fetch and transform user', async () => {
    mockFetchUser.mockResolvedValue({ id: 1, name: 'Alice', email: 'a@test.com' });
    const result = await userService.getUser(1);
    expect(result).toEqual({ id: 1, displayName: 'Alice', email: 'a@test.com' });
    expect(mockFetchUser).toHaveBeenCalledWith(1);
  });

  it('should handle errors', async () => {
    mockFetchUser.mockRejectedValue(new Error('Network error'));
    await expect(userService.getUser(1)).rejects.toThrow('Network error');
  });
});

// Partial module mock (keep original exports)
vi.mock('@/utils/helpers', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/utils/helpers')>();
  return { ...actual, formatDate: vi.fn().mockReturnValue('2024-01-01') };
});

// Spy on object methods
const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

// Fetch mock
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

mockFetch.mockResolvedValueOnce({
  ok: true,
  json: () => Promise.resolve({ data: [1, 2, 3] }),
  status: 200,
});

// Timer mocking
describe('Debounce', () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => { vi.useRealTimers(); });

  it('should debounce calls', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 300);
    debounced(); debounced(); debounced();
    expect(fn).not.toHaveBeenCalled();
    vi.advanceTimersByTime(300);
    expect(fn).toHaveBeenCalledOnce();
  });
});

// Date mocking
vi.setSystemTime(new Date('2024-06-15T12:00:00Z'));
expect(new Date().toISOString()).toContain('2024-06-15');
vi.useRealTimers();
```

## §3 — React Testing Library Integration

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

describe('LoginForm', () => {
  it('should submit form with valid credentials', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();

    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'alice@test.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /login/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'alice@test.com',
      password: 'password123',
    });
  });

  it('should show validation errors', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: /login/i }));

    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
  });
});

// Custom hook testing
import { renderHook, act } from '@testing-library/react';

describe('useCounter', () => {
  it('should increment', () => {
    const { result } = renderHook(() => useCounter(0));
    act(() => { result.current.increment(); });
    expect(result.current.count).toBe(1);
  });
});

// Testing with context providers
function renderWithProviders(ui: React.ReactElement, options = {}) {
  return render(ui, {
    wrapper: ({ children }) => (
      <AuthProvider><ThemeProvider>{children}</ThemeProvider></AuthProvider>
    ),
    ...options,
  });
}
```

## §4 — Snapshot & Inline Snapshots

```typescript
// File snapshot
it('should match component snapshot', () => {
  const { container } = render(<UserCard user={mockUser} />);
  expect(container.firstChild).toMatchSnapshot();
});

// Inline snapshot (auto-updated by vitest)
it('should format user display', () => {
  expect(formatUser({ name: 'Alice', role: 'admin' }))
    .toMatchInlineSnapshot(`"Alice (admin)"`);
});

// Snapshot with custom serializer
expect.addSnapshotSerializer({
  serialize(val) { return `User: ${val.name}`; },
  test(val) { return val && val.hasOwnProperty('name'); },
});
```

## §5 — Table-Driven & Parameterized Tests

```typescript
// test.each with array
it.each([
  [1, 1, 2],
  [2, 3, 5],
  [0, 0, 0],
  [-1, 1, 0],
])('add(%i, %i) = %i', (a, b, expected) => {
  expect(add(a, b)).toBe(expected);
});

// test.each with objects
it.each([
  { input: 'hello', expected: 'HELLO' },
  { input: 'world', expected: 'WORLD' },
  { input: '', expected: '' },
])('toUpper("$input") → "$expected"', ({ input, expected }) => {
  expect(input.toUpperCase()).toBe(expected);
});

// describe.each
describe.each([
  { role: 'admin', canDelete: true, canEdit: true },
  { role: 'editor', canDelete: false, canEdit: true },
  { role: 'viewer', canDelete: false, canEdit: false },
])('Role: $role', ({ role, canDelete, canEdit }) => {
  it(`canDelete: ${canDelete}`, () => {
    expect(permissions(role).canDelete).toBe(canDelete);
  });
  it(`canEdit: ${canEdit}`, () => {
    expect(permissions(role).canEdit).toBe(canEdit);
  });
});
```

## §6 — In-Source Testing

```typescript
// src/utils/math.ts
export function add(a: number, b: number): number { return a + b; }
export function multiply(a: number, b: number): number { return a * b; }

// Tests co-located in source file
if (import.meta.vitest) {
  const { it, expect, describe } = import.meta.vitest;

  describe('math utils', () => {
    it('add', () => { expect(add(1, 2)).toBe(3); });
    it('multiply', () => { expect(multiply(3, 4)).toBe(12); });
  });
}

// Enable in config:
// defineConfig({ test: { includeSource: ['src/**/*.ts'] } })
// For production build, tree-shake with:
// define: { 'import.meta.vitest': 'undefined' }
```

## §7 — API / Integration Testing

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';

describe('API Integration', () => {
  let server: any;
  let baseUrl: string;

  beforeAll(async () => {
    server = await startTestServer();
    baseUrl = `http://localhost:${server.port}`;
  });

  afterAll(async () => { await server.close(); });

  it('should create and fetch user', async () => {
    // Create
    const createRes = await fetch(`${baseUrl}/api/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'Alice', email: 'alice@test.com' }),
    });
    expect(createRes.status).toBe(201);
    const { id } = await createRes.json();

    // Fetch
    const getRes = await fetch(`${baseUrl}/api/users/${id}`);
    expect(getRes.status).toBe(200);
    const user = await getRes.json();
    expect(user.name).toBe('Alice');
  });
});
```

## §8 — CI/CD Integration

```yaml
# GitHub Actions
name: Vitest
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx vitest run --coverage --reporter=junit
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: |
            test-results/
            coverage/
```

```json
// package.json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:watch": "vitest --watch",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",
    "test:ci": "vitest run --coverage --reporter=junit --reporter=default"
  }
}
```

## §9 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Mock not working | Module cached before mock | Move `vi.mock()` to top of file (hoisted) |
| `vi.mocked()` type error | Missing type assertion | Use `vi.mocked(fn)` with proper import |
| Timer test fails | Forgot `vi.useRealTimers()` | Add in `afterEach`, use `vi.useFakeTimers()` per test |
| Snapshot outdated | Code changed | Run `vitest -u` to update snapshots |
| jsdom missing APIs | `ResizeObserver`, `matchMedia` | Mock in setup file with `vi.stubGlobal()` |
| Act warning in React tests | State update outside act | Use `userEvent.setup()` and `waitFor()` |
| Module resolution fails | Missing alias | Add `resolve.alias` in vitest config |
| Coverage too low | Untested files | Set `coverage.all: true` to include all files |
| Tests slow | Large test suite | Use `pool: 'threads'`, parallel by default |
| In-source tests not found | Not enabled in config | Add `includeSource` to test config |

## §10 — Best Practices Checklist

- ✅ Use `vi.fn()` / `vi.mock()` — Jest-compatible API
- ✅ Use `vi.clearAllMocks()` in `afterEach` for clean state
- ✅ Use `vi.mocked()` for type-safe mock access
- ✅ Use `pool: 'threads'` for parallel execution (default)
- ✅ Use `@testing-library/react` with `userEvent.setup()` for React tests
- ✅ Use inline snapshots for small, readable assertions
- ✅ Use `test.each` / `describe.each` for parameterized tests
- ✅ Use workspace config for monorepo projects
- ✅ Use in-source testing for utility functions
- ✅ Use `--ui` flag for interactive test explorer
- ✅ Use `vi.stubGlobal()` for browser API mocks in setup
- ✅ Configure coverage thresholds in `vitest.config.ts`
- ✅ Structure: `tests/unit/`, `tests/components/`, `tests/integration/`, `tests/setup.ts`
