# Jasmine — Advanced Patterns & Playbook

## Custom Matchers

```javascript
beforeEach(() => {
  jasmine.addMatchers({
    toBeValidEmail: () => ({
      compare: (actual) => {
        const pass = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(actual);
        return { pass, message: `Expected "${actual}" ${pass ? 'not ' : ''}to be a valid email` };
      }
    }),
    toHaveBeenCalledWithMatch: () => ({
      compare: (spy, ...matchers) => {
        const calls = spy.calls.allArgs();
        const pass = calls.some(args => matchers.every((m, i) =>
          jasmine.matchersUtil.equals(args[i], m)));
        return { pass, message: `Expected spy to have been called with matching args` };
      }
    })
  });
});
```

## Spy Patterns

```javascript
describe('SpyPatterns', () => {
  it('tracks calls and arguments', () => {
    const obj = { process: (x) => x * 2 };
    spyOn(obj, 'process').and.callThrough();
    obj.process(5);
    expect(obj.process).toHaveBeenCalledWith(5);
    expect(obj.process).toHaveReturnedWith(10);
    expect(obj.process.calls.count()).toBe(1);
  });

  it('stubs return values', () => {
    const api = { fetch: () => {} };
    spyOn(api, 'fetch').and.returnValues(
      Promise.resolve({ id: 1 }),  // first call
      Promise.resolve({ id: 2 })   // second call
    );
  });

  it('creates standalone spy', () => {
    const callback = jasmine.createSpy('callback').and.callFake((x) => x + 1);
    [1, 2, 3].forEach(callback);
    expect(callback).toHaveBeenCalledTimes(3);
    expect(callback.calls.argsFor(0)).toEqual([1, 0, [1, 2, 3]]);
  });

  it('spies on property', () => {
    const obj = { get value() { return 42; } };
    spyOnProperty(obj, 'value', 'get').and.returnValue(100);
    expect(obj.value).toBe(100);
  });
});
```

## Async Testing

```javascript
describe('Async', () => {
  it('resolves promise', async () => {
    const result = await fetchData();
    expect(result).toBeDefined();
  });

  it('uses done callback', (done) => {
    fetchData().then(result => {
      expect(result.status).toBe('ok');
      done();
    }).catch(done.fail);
  });

  // Clock for timers
  beforeEach(() => jasmine.clock().install());
  afterEach(() => jasmine.clock().uninstall());

  it('debounces', () => {
    const spy = jasmine.createSpy();
    const d = debounce(spy, 500);
    d(); d();
    jasmine.clock().tick(500);
    expect(spy).toHaveBeenCalledTimes(1);
  });
});
```

## Configuration

```javascript
// jasmine.json
{
  "spec_dir": "test",
  "spec_files": ["**/*[sS]pec.?(m)js"],
  "helpers": ["helpers/**/*.?(m)js"],
  "random": true,
  "seed": null,
  "stopSpecOnExpectationFailure": false,
  "failSpecWithNoExpectations": true
}
```

## Anti-Patterns

- ❌ `fit()`/`fdescribe()` committed to source — skips other tests in CI
- ❌ Shared state via closure without `beforeEach` reset
- ❌ `jasmine.clock().install()` without corresponding `uninstall()` in `afterEach`
- ❌ Nested `describe` blocks more than 3 levels deep — flatten test structure
