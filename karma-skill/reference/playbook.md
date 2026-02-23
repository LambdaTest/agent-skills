# Karma — Advanced Playbook

## §1 Production Configuration

### karma.conf.js — Full Setup
```javascript
// karma.conf.js
module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine', '@angular-devkit/build-angular'],

    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-launcher'),
      require('karma-firefox-launcher'),
      require('karma-coverage'),
      require('karma-junit-reporter'),
      require('karma-spec-reporter'),
      require('@angular-devkit/build-angular/plugins/karma'),
    ],

    client: {
      jasmine: {
        random: true,
        seed: '',
        stopOnSpecFailure: false,
        failSpecWithNoExpectations: true,
        forbidDuplicateNames: true,
        timeoutInterval: 10000,
      },
      clearContext: false,
    },

    coverageReporter: {
      dir: require('path').join(__dirname, './coverage'),
      subdir: '.',
      reporters: [
        { type: 'html' },
        { type: 'text-summary' },
        { type: 'lcov' },
        { type: 'cobertura' },
      ],
      check: {
        global: {
          statements: 80,
          branches: 75,
          functions: 80,
          lines: 80,
        },
        each: {
          statements: 50,
          branches: 50,
          functions: 50,
          lines: 50,
        },
      },
    },

    reporters: ['spec', 'coverage', 'junit'],
    junitReporter: {
      outputDir: 'test-results',
      outputFile: 'karma-results.xml',
      useBrowserName: false,
    },

    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: true,
    restartOnFileChange: true,

    browsers: [process.env.CI ? 'ChromeHeadlessNoSandbox' : 'Chrome'],
    customLaunchers: {
      ChromeHeadlessNoSandbox: {
        base: 'ChromeHeadless',
        flags: [
          '--no-sandbox',
          '--disable-gpu',
          '--disable-translate',
          '--disable-extensions',
        ],
      },
    },

    singleRun: !!process.env.CI,
    browserDisconnectTolerance: 3,
    browserDisconnectTimeout: 30000,
    browserNoActivityTimeout: 60000,
    captureTimeout: 60000,
    concurrency: Infinity,
  });
};
```

### tsconfig.spec.json (Angular)
```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/spec",
    "types": ["jasmine"]
  },
  "files": ["src/test.ts", "src/polyfills.ts"],
  "include": ["src/**/*.spec.ts", "src/**/*.d.ts"]
}
```

---

## §2 Angular Component Testing — Production Patterns

### Service Mocking with createSpyObj
```typescript
import { ComponentFixture, TestBed, fakeAsync, tick, flush } from '@angular/core/testing';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { of, throwError, BehaviorSubject } from 'rxjs';
import { LoginComponent } from './login.component';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let notifyService: jasmine.SpyObj<NotificationService>;

  beforeEach(async () => {
    authService = jasmine.createSpyObj('AuthService', ['login', 'logout', 'isAuthenticated'], {
      currentUser$: new BehaviorSubject(null),
    });
    router = jasmine.createSpyObj('Router', ['navigate']);
    notifyService = jasmine.createSpyObj('NotificationService', ['success', 'error']);

    await TestBed.configureTestingModule({
      imports: [ReactiveFormsModule, FormsModule],
      declarations: [LoginComponent],
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: Router, useValue: router },
        { provide: NotificationService, useValue: notifyService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('form validation', () => {
    it('should be invalid when empty', () => {
      expect(component.loginForm.valid).toBeFalse();
    });

    it('should validate email format', () => {
      component.loginForm.patchValue({ email: 'invalid', password: 'pass123' });
      expect(component.loginForm.get('email')!.errors?.['email']).toBeTruthy();
    });

    it('should be valid with correct data', () => {
      component.loginForm.patchValue({
        email: 'user@example.com',
        password: 'password123',
      });
      expect(component.loginForm.valid).toBeTrue();
    });
  });

  describe('login submission', () => {
    beforeEach(() => {
      component.loginForm.patchValue({
        email: 'user@example.com',
        password: 'password123',
      });
    });

    it('should call auth service and navigate on success', fakeAsync(() => {
      authService.login.and.returnValue(of({ token: 'abc', user: { id: 1 } }));
      component.onSubmit();
      tick();
      expect(authService.login).toHaveBeenCalledWith('user@example.com', 'password123');
      expect(router.navigate).toHaveBeenCalledWith(['/dashboard']);
      expect(notifyService.success).toHaveBeenCalledWith('Login successful');
    }));

    it('should show error message on failure', fakeAsync(() => {
      authService.login.and.returnValue(
        throwError(() => ({ status: 401, error: { message: 'Invalid credentials' } }))
      );
      component.onSubmit();
      tick();
      fixture.detectChanges();

      const errorEl = fixture.nativeElement.querySelector('[data-testid="error-message"]');
      expect(errorEl.textContent).toContain('Invalid credentials');
      expect(component.isLoading).toBeFalse();
    }));

    it('should disable submit button while loading', fakeAsync(() => {
      authService.login.and.returnValue(of({ token: 'abc' }).pipe());
      component.onSubmit();
      fixture.detectChanges();

      const button = fixture.nativeElement.querySelector('button[type="submit"]');
      expect(button.disabled).toBeTrue();
      expect(component.isLoading).toBeTrue();
      tick();
    }));
  });
});
```

### DOM Interaction Patterns
```typescript
describe('ProductListComponent', () => {
  let component: ProductListComponent;
  let fixture: ComponentFixture<ProductListComponent>;
  let productService: jasmine.SpyObj<ProductService>;

  const mockProducts = [
    { id: 1, name: 'Widget', price: 9.99, inStock: true },
    { id: 2, name: 'Gadget', price: 19.99, inStock: false },
    { id: 3, name: 'Doohickey', price: 4.99, inStock: true },
  ];

  beforeEach(async () => {
    productService = jasmine.createSpyObj('ProductService', ['getAll', 'delete']);
    productService.getAll.and.returnValue(of(mockProducts));

    await TestBed.configureTestingModule({
      declarations: [ProductListComponent],
      providers: [{ provide: ProductService, useValue: productService }],
    }).compileComponents();

    fixture = TestBed.createComponent(ProductListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should render product cards', () => {
    const cards = fixture.nativeElement.querySelectorAll('[data-testid="product-card"]');
    expect(cards.length).toBe(3);
  });

  it('should show out-of-stock badge', () => {
    const badges = fixture.nativeElement.querySelectorAll('.out-of-stock-badge');
    expect(badges.length).toBe(1);
    expect(badges[0].textContent.trim()).toBe('Out of Stock');
  });

  it('should sort products by price', () => {
    const sortButton = fixture.nativeElement.querySelector('[data-testid="sort-price"]');
    sortButton.click();
    fixture.detectChanges();

    const prices = Array.from(
      fixture.nativeElement.querySelectorAll('[data-testid="product-price"]')
    ).map((el: any) => parseFloat(el.textContent.replace('$', '')));

    expect(prices).toEqual([4.99, 9.99, 19.99]);
  });

  it('should confirm before deleting', fakeAsync(() => {
    spyOn(window, 'confirm').and.returnValue(true);
    productService.delete.and.returnValue(of(void 0));

    const deleteBtn = fixture.nativeElement.querySelector('[data-testid="delete-btn-1"]');
    deleteBtn.click();
    tick();

    expect(window.confirm).toHaveBeenCalled();
    expect(productService.delete).toHaveBeenCalledWith(1);
  }));
});
```

---

## §3 Service Testing with HTTP

### HttpClient Testing
```typescript
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { UserService } from './user.service';

describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [UserService],
    });
    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify(); // Ensure no outstanding requests
  });

  it('should fetch users with pagination', () => {
    const mockResponse = {
      data: [{ id: 1, name: 'Alice' }],
      total: 50,
      page: 1,
    };

    service.getUsers(1, 10).subscribe((response) => {
      expect(response.data.length).toBe(1);
      expect(response.total).toBe(50);
    });

    const req = httpMock.expectOne('/api/users?page=1&limit=10');
    expect(req.request.method).toBe('GET');
    expect(req.request.headers.get('Accept')).toBe('application/json');
    req.flush(mockResponse);
  });

  it('should handle 404 errors', () => {
    service.getUser(999).subscribe({
      error: (err) => {
        expect(err.status).toBe(404);
        expect(err.statusText).toBe('Not Found');
      },
    });

    const req = httpMock.expectOne('/api/users/999');
    req.flush('Not found', { status: 404, statusText: 'Not Found' });
  });

  it('should retry failed requests', () => {
    service.getUsersWithRetry().subscribe((users) => {
      expect(users.length).toBe(1);
    });

    // First attempt fails
    const req1 = httpMock.expectOne('/api/users');
    req1.error(new ProgressEvent('Network error'));

    // Retry succeeds
    const req2 = httpMock.expectOne('/api/users');
    req2.flush([{ id: 1, name: 'Alice' }]);
  });

  it('should send POST with correct body', () => {
    const newUser = { name: 'Bob', email: 'bob@test.com' };

    service.createUser(newUser).subscribe((user) => {
      expect(user.id).toBeDefined();
    });

    const req = httpMock.expectOne('/api/users');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(newUser);
    req.flush({ id: 2, ...newUser });
  });
});
```

---

## §4 Directive & Pipe Testing

### Custom Directive
```typescript
import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HighlightDirective } from './highlight.directive';

@Component({
  template: `
    <p appHighlight="yellow" data-testid="highlighted">Highlighted text</p>
    <p data-testid="plain">Plain text</p>
  `,
})
class TestHostComponent {}

describe('HighlightDirective', () => {
  let fixture: ComponentFixture<TestHostComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TestHostComponent, HighlightDirective],
    });
    fixture = TestBed.createComponent(TestHostComponent);
    fixture.detectChanges();
  });

  it('should apply background color', () => {
    const el = fixture.nativeElement.querySelector('[data-testid="highlighted"]');
    expect(el.style.backgroundColor).toBe('yellow');
  });

  it('should change color on hover', () => {
    const el = fixture.nativeElement.querySelector('[data-testid="highlighted"]');
    el.dispatchEvent(new Event('mouseenter'));
    fixture.detectChanges();
    expect(el.style.backgroundColor).toBe('gold');
  });
});
```

### Custom Pipe
```typescript
import { TruncatePipe } from './truncate.pipe';

describe('TruncatePipe', () => {
  const pipe = new TruncatePipe();

  it('should truncate long strings', () => {
    expect(pipe.transform('Hello World!', 5)).toBe('Hello...');
  });

  it('should return short strings unchanged', () => {
    expect(pipe.transform('Hi', 10)).toBe('Hi');
  });

  it('should handle null/undefined', () => {
    expect(pipe.transform(null as any)).toBe('');
    expect(pipe.transform(undefined as any)).toBe('');
  });

  it('should use custom suffix', () => {
    expect(pipe.transform('Hello World!', 5, ' [more]')).toBe('Hello [more]');
  });
});
```

---

## §5 RxJS & Async Patterns

### Testing Observables
```typescript
import { fakeAsync, tick, flush, discardPeriodicTimers } from '@angular/core/testing';
import { of, interval, Subject, timer } from 'rxjs';
import { debounceTime, switchMap, take, delay } from 'rxjs/operators';

describe('SearchComponent', () => {
  let component: SearchComponent;
  let fixture: ComponentFixture<SearchComponent>;
  let searchService: jasmine.SpyObj<SearchService>;

  beforeEach(async () => {
    searchService = jasmine.createSpyObj('SearchService', ['search']);
    await TestBed.configureTestingModule({
      declarations: [SearchComponent],
      providers: [{ provide: SearchService, useValue: searchService }],
    }).compileComponents();

    fixture = TestBed.createComponent(SearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should debounce search input', fakeAsync(() => {
    searchService.search.and.returnValue(of([{ id: 1, name: 'Result' }]));

    component.searchControl.setValue('hel');
    tick(100);
    component.searchControl.setValue('hello');
    tick(300); // debounceTime(300)

    expect(searchService.search).toHaveBeenCalledTimes(1);
    expect(searchService.search).toHaveBeenCalledWith('hello');

    discardPeriodicTimers();
  }));

  it('should cancel previous search on new input', fakeAsync(() => {
    const slow$ = of([{ id: 1 }]).pipe(delay(500));
    const fast$ = of([{ id: 2 }]);
    searchService.search.and.returnValues(slow$, fast$);

    component.searchControl.setValue('first');
    tick(300);
    component.searchControl.setValue('second');
    tick(300);
    tick(500);

    expect(component.results.length).toBe(1);
    expect(component.results[0].id).toBe(2);

    discardPeriodicTimers();
  }));

  it('should unsubscribe on destroy', () => {
    const subject = new Subject();
    spyOn(subject, 'unsubscribe');
    component['subscription'] = subject.subscribe();
    component.ngOnDestroy();
    expect(component['subscription'].closed).toBeTrue();
  });
});
```

---

## §6 Router & NgRx Testing

### Router Testing
```typescript
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';
import { Location } from '@angular/common';

describe('AppComponent routing', () => {
  let router: Router;
  let location: Location;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        RouterTestingModule.withRoutes([
          { path: '', component: HomeComponent },
          { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
          { path: '**', component: NotFoundComponent },
        ]),
      ],
      declarations: [AppComponent, HomeComponent, DashboardComponent, NotFoundComponent],
      providers: [{ provide: AuthGuard, useValue: { canActivate: () => true } }],
    }).compileComponents();

    router = TestBed.inject(Router);
    location = TestBed.inject(Location);
    router.initialNavigation();
  });

  it('should navigate to dashboard', fakeAsync(() => {
    router.navigate(['/dashboard']);
    tick();
    expect(location.path()).toBe('/dashboard');
  }));

  it('should redirect unknown routes to 404', fakeAsync(() => {
    router.navigate(['/nonexistent']);
    tick();
    expect(location.path()).toBe('/nonexistent');
  }));
});
```

### NgRx Store Testing
```typescript
import { provideMockStore, MockStore } from '@ngrx/store/testing';
import { Store } from '@ngrx/store';
import * as UserActions from '../store/user.actions';
import * as UserSelectors from '../store/user.selectors';

describe('UserListComponent with NgRx', () => {
  let store: MockStore;
  let fixture: ComponentFixture<UserListComponent>;

  const initialState = {
    users: {
      list: [],
      loading: false,
      error: null,
    },
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [UserListComponent],
      providers: [
        provideMockStore({
          initialState,
          selectors: [
            { selector: UserSelectors.selectAllUsers, value: [] },
            { selector: UserSelectors.selectLoading, value: false },
          ],
        }),
      ],
    }).compileComponents();

    store = TestBed.inject(Store) as MockStore;
    spyOn(store, 'dispatch');
    fixture = TestBed.createComponent(UserListComponent);
    fixture.detectChanges();
  });

  it('should dispatch loadUsers on init', () => {
    expect(store.dispatch).toHaveBeenCalledWith(UserActions.loadUsers());
  });

  it('should show loading spinner', () => {
    store.overrideSelector(UserSelectors.selectLoading, true);
    store.refreshState();
    fixture.detectChanges();

    const spinner = fixture.nativeElement.querySelector('[data-testid="loading"]');
    expect(spinner).toBeTruthy();
  });

  it('should render users from store', () => {
    store.overrideSelector(UserSelectors.selectAllUsers, [
      { id: 1, name: 'Alice' },
      { id: 2, name: 'Bob' },
    ]);
    store.refreshState();
    fixture.detectChanges();

    const rows = fixture.nativeElement.querySelectorAll('[data-testid="user-row"]');
    expect(rows.length).toBe(2);
  });
});
```

---

## §7 LambdaTest Cloud Integration

```javascript
// karma.conf.js — LambdaTest cloud browsers
module.exports = function (config) {
  const customLaunchers = {
    lt_chrome_win: {
      base: 'WebDriver',
      config: { hostname: 'hub.lambdatest.com', port: 80 },
      browserName: 'Chrome',
      version: 'latest',
      platform: 'Windows 11',
      name: 'Karma Chrome Win',
      tunnel: true,
      tunnelName: 'karma-tunnel',
      user: process.env.LT_USERNAME,
      accessKey: process.env.LT_ACCESS_KEY,
      video: true,
      console: true,
    },
    lt_firefox_mac: {
      base: 'WebDriver',
      config: { hostname: 'hub.lambdatest.com', port: 80 },
      browserName: 'Firefox',
      version: 'latest',
      platform: 'macOS Sonoma',
      name: 'Karma Firefox Mac',
      tunnel: true,
      user: process.env.LT_USERNAME,
      accessKey: process.env.LT_ACCESS_KEY,
    },
  };

  config.set({
    browsers: Object.keys(customLaunchers),
    customLaunchers,
    concurrency: 2,
    browserDisconnectTimeout: 60000,
    browserNoActivityTimeout: 120000,
  });
};
```

---

## §8 CI/CD Integration

### GitHub Actions
```yaml
name: Angular Tests
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

      - run: npx ng test --watch=false --code-coverage --browsers=ChromeHeadlessNoSandbox
        env:
          CI: true

      - name: Upload Coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage/

      - name: Check Coverage Threshold
        run: |
          COVERAGE=$(cat coverage/text-summary.txt | grep 'Lines' | grep -oP '[\d.]+%' | head -1)
          echo "Line coverage: $COVERAGE"

      - name: Publish Test Results
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: Karma Test Results
          path: test-results/karma-results.xml
          reporter: java-junit
```

---

## §9 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `No captured browser` | Browser fails to launch in CI | Use `ChromeHeadlessNoSandbox` with `--no-sandbox --disable-gpu` flags |
| 2 | `Disconnected: no message in 60000 ms` | Tests take too long or browser hangs | Increase `browserNoActivityTimeout` and `browserDisconnectTimeout` |
| 3 | `Expected spy to have been called` | Async code not flushed | Wrap in `fakeAsync` + `tick()` or `flush()` |
| 4 | `Cannot read properties of null` | DOM element not rendered | Call `fixture.detectChanges()` before querying DOM |
| 5 | `NullInjectorError: No provider for X` | Dependency not provided in TestBed | Add missing `providers` or `imports` in `TestBed.configureTestingModule()` |
| 6 | `1 periodic timer(s) still in queue` | Interval/timer not cleaned up | Call `discardPeriodicTimers()` at end of `fakeAsync` test |
| 7 | `HttpTestingController: Unflushed requests` | HTTP mock not responded | Call `req.flush()` for every expected request; `httpMock.verify()` in `afterEach` |
| 8 | Coverage shows 0% on all files | Preprocessor misconfigured | Ensure `coverage` preprocessor is in `karma.conf.js` and files match patterns |
| 9 | Tests pass locally, fail in CI | Browser difference or timing | Use `ChromeHeadless` in CI; add explicit waits; check `fakeAsync` usage |
| 10 | `ExpressionChangedAfterItHasBeenCheckedError` | Change detection triggered after check | Call `fixture.detectChanges()` after changing component state |
| 11 | `Cannot configure TestBed after initialized` | TestBed not reset | Ensure each `describe` has its own `beforeEach` with `TestBed.configureTestingModule` |
| 12 | Spies not resetting between tests | Spy created outside beforeEach | Create all `jasmine.createSpyObj` inside `beforeEach`; Jasmine auto-resets per test |

---

## §10 Best Practices Checklist

1. Use `ChromeHeadlessNoSandbox` for CI — never run headed Chrome in pipelines
2. Use `fakeAsync`/`tick` for all async Angular tests — never use `done()` callback
3. Call `fixture.detectChanges()` after every state change before asserting DOM
4. Call `httpMock.verify()` in `afterEach` — catch unhandled HTTP requests
5. Use `data-testid` attributes for DOM queries — not CSS classes or tag names
6. Create spies in `beforeEach` — let Jasmine auto-reset them per test
7. Set `failSpecWithNoExpectations: true` — catch tests with missing assertions
8. Use `discardPeriodicTimers()` — clean up intervals in fakeAsync tests
9. Set coverage thresholds in `karma.conf.js` — fail build on coverage drops
10. Use `RouterTestingModule` — never import real routing module in tests
11. Use `provideMockStore` for NgRx — isolate component from store side effects
12. Keep tests under 50 lines — extract helpers for common setup patterns
13. Use `jasmine.objectContaining()` for partial assertion matching
14. Run with `--random-order` — catch test interdependencies early
