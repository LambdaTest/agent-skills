# Karma — Advanced Patterns & Playbook

## Configuration for Angular

```javascript
// karma.conf.js — production-grade
module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine', '@angular-devkit/build-angular'],
    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-launcher'),
      require('karma-coverage'),
      require('karma-junit-reporter'),
      require('@angular-devkit/build-angular/plugins/karma')
    ],
    client: { clearContext: false, jasmine: { random: true, seed: '' } },
    coverageReporter: {
      dir: require('path').join(__dirname, './coverage'),
      subdir: '.',
      reporters: [{ type: 'html' }, { type: 'text-summary' }, { type: 'lcov' }],
      check: { global: { statements: 80, branches: 75, functions: 80, lines: 80 } }
    },
    reporters: ['progress', 'coverage', 'junit'],
    junitReporter: { outputDir: 'reports', outputFile: 'junit.xml' },
    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: true,
    browsers: ['ChromeHeadless'],
    customLaunchers: {
      ChromeHeadlessCI: { base: 'ChromeHeadless', flags: ['--no-sandbox', '--disable-gpu'] }
    },
    singleRun: true,
    restartOnFileChange: true,
    concurrency: Infinity
  });
};
```

## Angular Component Testing

```typescript
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

describe('UserComponent', () => {
  let component: UserComponent;
  let fixture: ComponentFixture<UserComponent>;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      declarations: [UserComponent],
      providers: [{ provide: UserService, useClass: MockUserService }]
    }).compileComponents();

    fixture = TestBed.createComponent(UserComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => httpMock.verify());

  it('loads user on init', () => {
    const req = httpMock.expectOne('/api/users/1');
    req.flush({ id: 1, name: 'Alice' });
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.name').textContent).toContain('Alice');
  });

  it('handles async with fakeAsync', fakeAsync(() => {
    component.search('test');
    tick(300); // debounce
    fixture.detectChanges();
    expect(component.results.length).toBeGreaterThan(0);
  }));
});
```

## Multi-Browser Testing

```javascript
// karma.conf.js additions for cross-browser
browsers: ['Chrome', 'Firefox', 'Safari'],
customLaunchers: {
  ChromeDebug: { base: 'Chrome', flags: ['--remote-debugging-port=9333'] },
  FirefoxHeadless: { base: 'Firefox', flags: ['-headless'] }
}
```

## Anti-Patterns

- ❌ `singleRun: false` in CI — tests never exit
- ❌ Testing with real HTTP calls — always use `HttpTestingController`
- ❌ Missing `fixture.detectChanges()` after state changes
- ❌ `PhantomJS` launcher — deprecated, use ChromeHeadless
