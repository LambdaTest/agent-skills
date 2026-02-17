# Mocha — Advanced Implementation Playbook

## §1 — Production Configuration

```yaml
# .mocharc.yml
spec: 'tests/**/*.test.ts'
timeout: 10000
recursive: true
reporter: spec
require:
  - ts-node/register
  - tests/setup.ts
exit: true
parallel: false
retries: 0
slow: 200
```

```json
// package.json scripts
{
  "scripts": {
    "test": "mocha",
    "test:watch": "mocha --watch",
    "test:smoke": "mocha --grep @smoke",
    "test:coverage": "nyc mocha",
    "test:ci": "mocha --reporter mocha-junit-reporter --retries 1"
  }
}
```

### NYC (Istanbul) Coverage Config

```json
// .nycrc.json
{
  "extends": "@istanbuljs/nyc-config-typescript",
  "all": true,
  "include": ["src/**/*.ts"],
  "exclude": ["**/*.test.ts", "**/*.d.ts"],
  "reporter": ["text", "lcov", "html"],
  "branches": 80,
  "lines": 85,
  "functions": 85,
  "statements": 85,
  "check-coverage": true
}
```

### TypeScript Setup

```typescript
// tests/setup.ts
import chai from 'chai';
import chaiAsPromised from 'chai-as-promised';
import sinonChai from 'sinon-chai';

chai.use(chaiAsPromised);
chai.use(sinonChai);

// Global test timeout
process.env.NODE_ENV = 'test';
```

## §2 — Testing with Chai + Sinon

```typescript
import { expect } from 'chai';
import sinon, { SinonSandbox, SinonStub } from 'sinon';
import { UserService } from '../src/services/UserService';

describe('UserService', () => {
  let sandbox: SinonSandbox;
  let service: UserService;
  let mockDb: { query: SinonStub; connect: SinonStub };

  beforeEach(() => {
    sandbox = sinon.createSandbox();
    mockDb = {
      query: sandbox.stub(),
      connect: sandbox.stub().resolves(true),
    };
    service = new UserService(mockDb);
  });

  afterEach(() => sandbox.restore());

  describe('create()', () => {
    it('should create user with valid data', async () => {
      mockDb.query.resolves({ id: '1', name: 'Alice', email: 'alice@test.com' });

      const user = await service.create({ name: 'Alice', email: 'alice@test.com' });

      expect(user).to.have.property('id', '1');
      expect(user).to.have.property('name', 'Alice');
      expect(mockDb.query).to.have.been.calledOnce;
      expect(mockDb.query).to.have.been.calledWith(
        sinon.match.string,
        sinon.match.has('name', 'Alice')
      );
    });

    it('should reject invalid email', async () => {
      await expect(service.create({ name: 'Alice', email: 'bad' }))
        .to.be.rejectedWith('Invalid email');
    });

    it('should handle database errors', async () => {
      mockDb.query.rejects(new Error('Connection lost'));
      await expect(service.create({ name: 'Alice', email: 'a@test.com' }))
        .to.be.rejectedWith('Connection lost');
    });
  });

  describe('findById()', () => {
    it('should return null for non-existent user', async () => {
      mockDb.query.resolves(null);
      const user = await service.findById('999');
      expect(user).to.be.null;
    });
  });
});
```

## §3 — Advanced Sinon Patterns

```typescript
// Stubs with sequential returns
const stub = sandbox.stub();
stub.onFirstCall().resolves({ page: 1, data: [1, 2] });
stub.onSecondCall().resolves({ page: 2, data: [3, 4] });
stub.onThirdCall().resolves({ page: 3, data: [] });

// Fake timers
describe('Token Expiry', () => {
  let clock: sinon.SinonFakeTimers;

  beforeEach(() => { clock = sinon.useFakeTimers(); });
  afterEach(() => { clock.restore(); });

  it('should expire token after 1 hour', async () => {
    const token = await auth.createToken('user');
    expect(auth.isValid(token)).to.be.true;
    clock.tick(3600 * 1000 + 1);  // advance 1 hour + 1ms
    expect(auth.isValid(token)).to.be.false;
  });
});

// Spy on existing methods
it('should log on error', async () => {
  const logSpy = sandbox.spy(logger, 'error');
  mockDb.query.rejects(new Error('fail'));
  try { await service.create(validData); } catch {}
  expect(logSpy).to.have.been.calledOnce;
  expect(logSpy).to.have.been.calledWith(sinon.match('fail'));
});

// Fake server (HTTP)
import nock from 'nock';

describe('API Client', () => {
  afterEach(() => nock.cleanAll());

  it('should fetch users', async () => {
    nock('https://api.example.com')
      .get('/users')
      .reply(200, [{ id: 1, name: 'Alice' }]);

    const users = await apiClient.getUsers();
    expect(users).to.have.lengthOf(1);
    expect(users[0].name).to.equal('Alice');
  });

  it('should handle 500 errors', async () => {
    nock('https://api.example.com')
      .get('/users')
      .reply(500, { error: 'Internal Server Error' });

    await expect(apiClient.getUsers()).to.be.rejectedWith('Server error');
  });
});
```

## §4 — Async Patterns

```typescript
// Promises
it('should resolve with data', () => {
  return fetchData().then(data => expect(data).to.exist);
});

// Async/await
it('should resolve with data', async () => {
  const data = await fetchData();
  expect(data).to.exist;
});

// Callbacks (done)
it('should callback with data', (done) => {
  fetchDataCallback((err, data) => {
    if (err) return done(err);
    expect(data).to.exist;
    done();
  });
});

// Event emitters
it('should emit "data" event', (done) => {
  const emitter = createStream();
  emitter.on('data', (chunk) => {
    expect(chunk).to.be.a('string');
    done();
  });
  emitter.start();
});

// Timeout override per test
it('should complete long operation', async function() {
  this.timeout(30000);
  const result = await longRunningOperation();
  expect(result).to.equal('complete');
});
```

## §5 — Hooks & Test Organization

```typescript
// Lifecycle hooks
describe('Database Tests', () => {
  let connection: DbConnection;

  before(async () => {
    // Runs once before all tests in this describe
    connection = await Database.connect(TEST_DB_URL);
  });

  after(async () => {
    // Runs once after all tests
    await connection.close();
  });

  beforeEach(async () => {
    // Runs before each test
    await connection.truncateAll();
    await connection.seed('users', testUsers);
  });

  afterEach(async () => {
    // Runs after each test
    await connection.rollback();
  });

  // Tests...
});

// Nested describes
describe('Cart', () => {
  describe('when empty', () => {
    it('should have zero total', () => { /* ... */ });
    it('should show empty message', () => { /* ... */ });
  });

  describe('with items', () => {
    beforeEach(() => { cart.add(item1); cart.add(item2); });

    it('should calculate total', () => { /* ... */ });
    it('should apply discount', () => { /* ... */ });

    describe('at checkout', () => {
      it('should validate stock', () => { /* ... */ });
    });
  });
});

// Skip and only
describe.skip('WIP Feature', () => { /* skipped */ });
it.only('debug this test', () => { /* only this runs */ });

// Grep tags in test names
it('should login @smoke', () => { /* run with --grep @smoke */ });
it('should process order @regression', () => { /* ... */ });
```

## §6 — Custom Reporters & Plugins

```typescript
// Custom reporter
class CustomReporter {
  constructor(runner: Mocha.Runner) {
    let passes = 0, failures = 0;

    runner.on('pass', (test) => {
      passes++;
      console.log(`✓ ${test.fullTitle()} (${test.duration}ms)`);
    });

    runner.on('fail', (test, err) => {
      failures++;
      console.log(`✗ ${test.fullTitle()}: ${err.message}`);
    });

    runner.on('end', () => {
      console.log(`\n${passes} passing, ${failures} failing`);
    });
  }
}

// Root-level hooks (runs for all test files)
// tests/hooks.ts
export const mochaHooks = {
  beforeAll() { console.log('Suite starting'); },
  afterAll() { console.log('Suite complete'); },
  beforeEach() { /* ... */ },
  afterEach() { /* ... */ },
};
```

## §7 — Express/API Testing with Supertest

```typescript
import request from 'supertest';
import { expect } from 'chai';
import app from '../src/app';

describe('User API', () => {
  let token: string;

  before(async () => {
    const res = await request(app)
      .post('/api/auth/login')
      .send({ email: 'admin@test.com', password: 'admin123' });
    token = res.body.token;
  });

  describe('GET /api/users', () => {
    it('should return users list', async () => {
      const res = await request(app)
        .get('/api/users')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);

      expect(res.body).to.be.an('array');
      expect(res.body[0]).to.have.property('name');
    });

    it('should reject without auth', async () => {
      await request(app).get('/api/users').expect(401);
    });
  });

  describe('POST /api/users', () => {
    it('should create user', async () => {
      const res = await request(app)
        .post('/api/users')
        .set('Authorization', `Bearer ${token}`)
        .send({ name: 'New User', email: 'new@test.com' })
        .expect(201);

      expect(res.body).to.have.property('id');
    });

    it('should validate required fields', async () => {
      const res = await request(app)
        .post('/api/users')
        .set('Authorization', `Bearer ${token}`)
        .send({})
        .expect(400);

      expect(res.body.errors).to.have.lengthOf.at.least(1);
    });
  });
});
```

## §8 — CI/CD Integration

```yaml
# GitHub Actions
name: Mocha Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20]
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_DB: test, POSTGRES_PASSWORD: test }
        ports: ['5432:5432']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: ${{ matrix.node-version }} }
      - run: npm ci
      - run: npm run test:ci
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/test
          CI: true
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-node${{ matrix.node-version }}
          path: |
            test-results/
            coverage/
```

## §9 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Tests hang (no exit) | Open DB connections or timers | Use `--exit` flag or cleanup in `after()` hooks |
| Timeout exceeded | Slow async ops | Increase: `this.timeout(30000)` per test |
| Stub not working | Wrong import or module caching | Use `sinon.stub(object, 'method')`, check import path |
| `afterEach` not restoring | Missing `sandbox.restore()` | Always call in `afterEach`, use sandbox pattern |
| Async error swallowed | Missing `await` or `return` | Always `return` promise or use `async/await` |
| Test order dependency | Shared mutable state | Reset in `beforeEach`, use separate describes |
| `--watch` not rerunning | File not matching spec pattern | Check `.mocharc.yml` spec glob |
| Coverage shows 0% | Source not instrumented | Use `nyc` wrapper: `nyc mocha` |
| Nock not intercepting | URL mismatch or https vs http | Match exact URL including protocol |
| `describe.only` left in code | Forgotten debugging flag | Use lint rule: `no-only-tests` |

## §10 — Best Practices Checklist

- ✅ Use `sinon.createSandbox()` + `sandbox.restore()` in `afterEach`
- ✅ Use Chai's `expect` style for readable assertions
- ✅ Use `chai-as-promised` for async assertion chains
- ✅ Use `--exit` flag to prevent hanging from open handles
- ✅ Use `nock` for HTTP mocking (not sinon for fetch/axios)
- ✅ Use `nyc` for coverage with threshold enforcement
- ✅ Use grep tags (`@smoke`, `@regression`) for selective runs
- ✅ Use root-level hooks (`mochaHooks`) for global setup/teardown
- ✅ Use nested `describe` blocks for logical grouping
- ✅ Clean up all stubs, mocks, and connections in `afterEach`/`after`
- ✅ Use `supertest` for Express API testing
- ✅ Use TypeScript with `ts-node/register` for type safety
- ✅ Structure: `tests/unit/`, `tests/integration/`, `tests/fixtures/`, `tests/setup.ts`
