---
name: jasmine-testing-skill
description: >
  Generates Jasmine tests in JavaScript. BDD-style framework with spies and
  async support. Use when user mentions "Jasmine", "jasmine.createSpy",
  "toHaveBeenCalled". Triggers on: "Jasmine", "jasmine test", "createSpy",
  "Jasmine spec".
languages:
  - JavaScript
  - TypeScript
category: unit-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Jasmine Testing Skill

## Core Patterns

### Basic Test

```javascript
describe('Calculator', () => {
  let calc;

  beforeEach(() => { calc = new Calculator(); });

  it('should add two numbers', () => {
    expect(calc.add(2, 3)).toBe(5);
  });

  it('should throw on divide by zero', () => {
    expect(() => calc.divide(10, 0)).toThrowError('Division by zero');
  });
});
```

### Matchers

```javascript
expect(value).toBe(exact);              // === strict
expect(value).toEqual(object);           // Deep equality
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();
expect(value).toBeNaN();
expect(value).toBeGreaterThan(3);
expect(value).toBeCloseTo(0.3, 5);
expect(str).toContain('sub');
expect(str).toMatch(/pattern/);
expect(arr).toContain(item);
expect(fn).toThrow();
expect(fn).toThrowError('message');

// Negation
expect(value).not.toBe(other);
```

### Spies

```javascript
describe('UserService', () => {
  let service, api;

  beforeEach(() => {
    api = jasmine.createSpyObj('api', ['get', 'post']);
    service = new UserService(api);
  });

  it('fetches user from API', async () => {
    api.get.and.returnValue(Promise.resolve({ name: 'Alice' }));
    const user = await service.getUser(1);
    expect(user.name).toBe('Alice');
    expect(api.get).toHaveBeenCalledWith('/users/1');
    expect(api.get).toHaveBeenCalledTimes(1);
  });
});

// Spy on existing method
spyOn(obj, 'method').and.returnValue(42);
spyOn(obj, 'method').and.callThrough();    // Call original
spyOn(obj, 'method').and.throwError('err');
```

### Async Testing

```javascript
it('fetches data', async () => {
  const data = await fetchData();
  expect(data).toBeDefined();
});

// With done callback
it('fetches data', (done) => {
  fetchData().then(data => {
    expect(data).toBeDefined();
    done();
  });
});

// Clock control
beforeEach(() => { jasmine.clock().install(); });
afterEach(() => { jasmine.clock().uninstall(); });

it('handles timeout', () => {
  const callback = jasmine.createSpy();
  setTimeout(callback, 1000);
  jasmine.clock().tick(1001);
  expect(callback).toHaveBeenCalled();
});
```

## Setup: `npm install jasmine --save-dev && npx jasmine init`
## Run: `npx jasmine` or `npx jasmine spec/calculatorSpec.js`

## Deep Patterns

See `reference/playbook.md` for production-grade patterns:

| Section | What You Get |
|---------|-------------|
| §1 Project Setup | jasmine.json, TypeScript, spec reporter config |
| §2 Spies — Complete API | spyOn, createSpyObj, callFake, returnValues, call tracking |
| §3 Async Testing | async/await, expectAsync, promise matchers |
| §4 Custom Matchers | Domain-specific matchers, asymmetric matchers |
| §5 Test Organization | Nested describe, shared state, focused/excluded |
| §6 Fetch & Module Mocking | globalThis.fetch spy, HTTP error handling |
| §7 Browser Testing | DOM creation, keyboard events, focus trapping with Karma |
| §8 CI/CD Integration | GitHub Actions with coverage, browser testing |
| §9 Debugging Table | 12 common problems with causes and fixes |
| §10 Best Practices | 14-item checklist for production Jasmine testing |
