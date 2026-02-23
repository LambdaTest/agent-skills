# Mocha — Advanced Patterns & Playbook

## Async Patterns

```javascript
const { expect } = require('chai');
const sinon = require('sinon');

describe('Async Operations', () => {
  // Promise-based
  it('fetches user data', () => {
    return fetchUser(1).then(user => {
      expect(user).to.have.property('name');
      expect(user.name).to.be.a('string');
    });
  });

  // Async/await
  it('creates and retrieves user', async () => {
    const created = await createUser({ name: 'Alice' });
    const fetched = await fetchUser(created.id);
    expect(fetched).to.deep.include({ name: 'Alice' });
  });

  // Callback (done)
  it('emits event', (done) => {
    const emitter = new EventEmitter();
    emitter.on('data', (val) => {
      expect(val).to.equal('hello');
      done();
    });
    emitter.emit('data', 'hello');
  });

  // Retry flaky tests
  it('handles intermittent failures', async function () {
    this.retries(3);
    const result = await unreliableService.call();
    expect(result.status).to.equal('ok');
  });
});
```

## Sinon Mocking & Stubbing

```javascript
describe('Service Layer', () => {
  let sandbox;
  beforeEach(() => { sandbox = sinon.createSandbox(); });
  afterEach(() => sandbox.restore());

  it('calls API with correct params', async () => {
    const stub = sandbox.stub(http, 'get').resolves({ data: { id: 1 } });
    await userService.getUser(1);
    expect(stub).to.have.been.calledOnceWith('/api/users/1');
  });

  it('handles API errors gracefully', async () => {
    sandbox.stub(http, 'get').rejects(new Error('500'));
    const result = await userService.getUser(1);
    expect(result).to.be.null;
  });

  // Fake timers
  it('debounces calls', () => {
    const clock = sandbox.useFakeTimers();
    const spy = sandbox.spy();
    const debounced = debounce(spy, 300);
    debounced(); debounced(); debounced();
    clock.tick(300);
    expect(spy).to.have.been.calledOnce;
  });

  // Spy on prototype
  it('logs on error', async () => {
    const logSpy = sandbox.spy(Logger.prototype, 'error');
    sandbox.stub(http, 'get').rejects(new Error('fail'));
    await userService.getUser(1);
    expect(logSpy).to.have.been.calledOnce;
  });
});
```

## Chai Assertion Patterns

```javascript
// Deep equality
expect({ a: { b: [1, 2] } }).to.deep.equal({ a: { b: [1, 2] } });

// Partial matching
expect(user).to.include({ name: 'Alice' });
expect(users).to.deep.include.members([{ id: 1 }, { id: 2 }]);

// Type checking
expect(result).to.be.an('array').that.has.lengthOf(3);
expect(fn).to.be.a('function');

// chai-as-promised
const chaiAsPromised = require('chai-as-promised');
chai.use(chaiAsPromised);
await expect(fetchUser(-1)).to.be.rejectedWith(Error, /not found/);

// chai-http for API testing
const chaiHttp = require('chai-http');
chai.use(chaiHttp);
const res = await chai.request(app).get('/api/users').set('Authorization', 'Bearer token');
expect(res).to.have.status(200);
expect(res.body).to.be.an('array');
```

## Hooks & Lifecycle

```javascript
describe('Database Tests', () => {
  before(async () => { await db.connect(); await db.migrate(); });       // Once before all
  after(async () => { await db.disconnect(); });                          // Once after all
  beforeEach(async () => { await db.seed(); });                           // Before each test
  afterEach(async () => { await db.truncate(); });                        // After each test

  it('inserts record', async () => { /* ... */ });
});

// Root hooks plugin (.mocharc.yml: require: ./test/hooks.js)
module.exports = {
  mochaHooks: {
    beforeAll() { console.log('Global setup'); },
    afterAll() { console.log('Global teardown'); },
    beforeEach() { /* per-test setup */ },
    afterEach() { /* per-test cleanup */ }
  }
};
```

## Configuration

```yaml
# .mocharc.yml — production-grade
spec: 'test/**/*.spec.{js,ts}'
require:
  - ts-node/register
  - test/hooks.js
timeout: 10000
retries: 1
recursive: true
reporter: mochawesome
reporter-options:
  reportDir: reports
  reportFilename: test-report
  charts: true
  inline: true
parallel: true
jobs: 4
exit: true
```

## Custom Reporter

```javascript
class CustomReporter {
  constructor(runner) {
    const stats = runner.stats;
    runner.on('pass', test => console.log(`✅ ${test.fullTitle()} (${test.duration}ms)`));
    runner.on('fail', (test, err) => console.log(`❌ ${test.fullTitle()}: ${err.message}`));
    runner.on('end', () => console.log(`\n${stats.passes} passing, ${stats.failures} failing`));
  }
}
module.exports = CustomReporter;
```

## Anti-Patterns

- ❌ Arrow functions in `describe`/`it` — loses `this` context for `this.timeout()`, `this.retries()`
- ❌ Missing `afterEach` cleanup — leads to leaky state between tests
- ❌ `done()` with promises — pick one async style per test, not both
- ❌ Hardcoded timeouts in tests — use `.timeout()` or config, not `setTimeout`
- ❌ Tests dependent on execution order — each test must be independently runnable
