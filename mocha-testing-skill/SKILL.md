---
name: mocha-testing-skill
description: >
  Generates Mocha tests in JavaScript with Chai assertions and Sinon mocking.
  Use when user mentions "Mocha", "Chai", "sinon", "describe/it (not Jest)".
  Triggers on: "Mocha", "Chai", "sinon", "mocha test".
languages:
  - JavaScript
  - TypeScript
category: unit-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Mocha Testing Skill

## Core Patterns

### Basic Test with Chai

```javascript
const { expect } = require('chai');

describe('Calculator', () => {
  let calc;
  beforeEach(() => { calc = new Calculator(); });

  it('should add two numbers', () => {
    expect(calc.add(2, 3)).to.equal(5);
  });

  it('should throw on divide by zero', () => {
    expect(() => calc.divide(10, 0)).to.throw('Division by zero');
  });
});
```

### Chai Assertions

```javascript
expect(value).to.equal(5);
expect(arr).to.have.lengthOf(3);
expect(obj).to.have.property('name');
expect(str).to.include('hello');
expect(fn).to.throw(Error);
expect(arr).to.deep.equal([1, 2, 3]);
expect(obj).to.deep.include({ name: 'Alice' });
```

### Sinon Mocking

```javascript
const sinon = require('sinon');

describe('UserService', () => {
  let sandbox;
  beforeEach(() => { sandbox = sinon.createSandbox(); });
  afterEach(() => { sandbox.restore(); });

  it('fetches user from API', async () => {
    const stub = sandbox.stub(api, 'get').resolves({ name: 'Alice' });
    const user = await userService.getUser(1);
    expect(user.name).to.equal('Alice');
    expect(stub.calledOnce).to.be.true;
  });
});
```

### Async Testing

```javascript
it('should fetch data', async () => {
  const data = await fetchData();
  expect(data).to.have.property('id');
});

it('callback style', (done) => {
  fetchData((err, data) => {
    expect(err).to.be.null;
    done();
  });
});
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| Missing `done()` | Use async/await | Hanging tests |
| No sandbox | `sinon.createSandbox()` | Stubs leak |
| Arrow in `describe` | Regular function for `this.timeout()` | Context |

## Quick Reference

| Task | Command |
|------|---------|
| Run all | `npx mocha` |
| Watch | `npx mocha --watch` |
| Grep | `npx mocha --grep "login"` |
| Timeout | `npx mocha --timeout 10000` |
| Recursive | `npx mocha --recursive` |

## Setup: `npm install mocha chai sinon --save-dev`

## Deep Patterns → `reference/playbook.md`

| § | Section | Lines |
|---|---------|-------|
| 1 | Production Configuration | mocharc, NYC coverage, TypeScript |
| 2 | Testing with Chai + Sinon | Stubs, spies, assertions |
| 3 | Advanced Sinon Patterns | Fake timers, nock HTTP, sequential |
| 4 | Async Patterns | Promise, await, callback, events |
| 5 | Hooks & Test Organization | Lifecycle, nesting, grep tags |
| 6 | Custom Reporters & Plugins | Reporter class, root hooks |
| 7 | Express/API Testing | Supertest integration |
| 8 | CI/CD Integration | GitHub Actions, services |
| 9 | Debugging Quick-Reference | 10 common problems |
| 10 | Best Practices Checklist | 13 items |
