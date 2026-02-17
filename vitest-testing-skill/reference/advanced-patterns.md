# Vitest — Advanced Patterns & Playbook

## In-Source Testing

```typescript
// src/utils.ts — tests live alongside code
export function sum(a: number, b: number) { return a + b; }

if (import.meta.vitest) {
  const { it, expect } = import.meta.vitest;
  it('adds numbers', () => expect(sum(1, 2)).toBe(3));
}
```

## Advanced Mocking

```typescript
import { vi, describe, it, expect, beforeEach } from 'vitest';

// Auto-mock entire module
vi.mock('./api', () => ({
  fetchUser: vi.fn().mockResolvedValue({ id: 1, name: 'Alice' }),
  updateUser: vi.fn()
}));

// Partial mock — keep real implementations
vi.mock('./utils', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./utils')>();
  return { ...actual, formatDate: vi.fn(() => '2025-01-01') };
});

// Mock globals
vi.stubGlobal('fetch', vi.fn());
vi.stubGlobal('IntersectionObserver', vi.fn(() => ({
  observe: vi.fn(), unobserve: vi.fn(), disconnect: vi.fn()
})));

// Timer control
describe('Debounce', () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => { vi.useRealTimers(); });

  it('debounces calls', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 300);
    debounced(); debounced(); debounced();
    vi.advanceTimersByTime(300);
    expect(fn).toHaveBeenCalledOnce();
  });
});

// Spy on class methods
const spy = vi.spyOn(UserService.prototype, 'save');
spy.mockResolvedValue({ id: 1 });
```

## Concurrent & Parallel Testing

```typescript
// Run tests concurrently within a suite
describe.concurrent('independent API tests', () => {
  it('fetches users', async () => { /* ... */ });
  it('fetches products', async () => { /* ... */ });
  it('fetches orders', async () => { /* ... */ });
});

// Pool configuration in vitest.config.ts
export default defineConfig({
  test: {
    pool: 'threads',        // or 'forks', 'vmThreads'
    poolOptions: { threads: { maxThreads: 8, minThreads: 2 } },
    isolate: true,           // true = full isolation per test file
    fileParallelism: true
  }
});
```

## Snapshot Testing

```typescript
// Inline snapshot
it('creates user shape', () => {
  expect(createUser('Alice')).toMatchInlineSnapshot(`
    { "id": StringMatching /^[a-f0-9-]+$/, "name": "Alice" }
  `);
});

// File snapshot (saved to __snapshots__)
it('renders component', () => {
  const html = render(<Button variant="primary">Click</Button>);
  expect(html).toMatchSnapshot();
});

// Custom serializer
expect.addSnapshotSerializer({
  serialize: (val) => `MyType(${val.name})`,
  test: (val) => val?.__type === 'MyType'
});
```

## Vue/React Component Testing

```typescript
import { mount } from '@vue/test-utils';
// or: import { render, screen } from '@testing-library/react';

describe('Counter Component', () => {
  it('increments on click', async () => {
    const wrapper = mount(Counter, { props: { initial: 0 } });
    await wrapper.find('button').trigger('click');
    expect(wrapper.text()).toContain('1');
  });

  it('emits update event', async () => {
    const wrapper = mount(Counter);
    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('update')).toHaveLength(1);
    expect(wrapper.emitted('update')[0]).toEqual([1]);
  });
});
```

## Coverage & Configuration

```typescript
// vitest.config.ts — production-grade
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./test/setup.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: ['node_modules/', 'test/', '**/*.d.ts', '**/*.config.*'],
      thresholds: { branches: 80, functions: 80, lines: 80, statements: 80 }
    },
    alias: { '@': path.resolve(__dirname, './src') },
    reporters: ['default', 'junit'],
    outputFile: { junit: './reports/junit.xml' },
    typecheck: { enabled: true }
  }
});
```

## Workspace Configuration (Monorepo)

```typescript
// vitest.workspace.ts
export default ['packages/*', 'apps/*'];

// Each package gets its own vitest.config.ts
// Run: vitest --workspace
```

## Anti-Patterns

- ❌ Using `jest.fn()` instead of `vi.fn()` — Vitest has its own API
- ❌ `import.meta.env` in tests without `vi.stubEnv` — env vars leak between tests
- ❌ `vi.mock()` inside `it()` — must be at file scope (hoisted automatically)
- ❌ Missing `vi.useRealTimers()` cleanup — fake timers leak to next test
- ❌ Not using `pool: 'forks'` for CPU-bound tests — threads share memory
