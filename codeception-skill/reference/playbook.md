# Codeception — Advanced Playbook

## §1 Project Setup & Configuration

### Installation
```bash
composer require codeception/codeception --dev
composer require codeception/module-webdriver --dev
composer require codeception/module-phpbrowser --dev
composer require codeception/module-asserts --dev
composer require codeception/module-rest --dev
composer require codeception/module-db --dev
php vendor/bin/codecept bootstrap
```

### codeception.yml
```yaml
namespace: Tests
support_namespace: Support
paths:
  tests: tests
  output: tests/_output
  data: tests/_data
  support: tests/_support
  envs: tests/_envs
actor_suffix: Tester

settings:
  colors: true
  memory_limit: 1024M
  log: true

coverage:
  enabled: true
  include:
    - app/*
  exclude:
    - app/Console/*

extensions:
  enabled:
    - Codeception\Extension\RunFailed
    - Codeception\Extension\Recorder
  config:
    Codeception\Extension\Recorder:
      delete_successful: true
```

### Suite Configuration — Acceptance
```yaml
# tests/Acceptance.suite.yml
actor: AcceptanceTester
modules:
  enabled:
    - WebDriver:
        url: https://staging.example.com
        browser: chrome
        capabilities:
          goog:chromeOptions:
            args: ["--headless", "--no-sandbox", "--disable-dev-shm-usage"]
    - \Tests\Support\Helper\Acceptance
  step_decorators:
    - \Codeception\Step\Retry
```

### Suite Configuration — API
```yaml
# tests/Api.suite.yml
actor: ApiTester
modules:
  enabled:
    - REST:
        url: https://staging.example.com/api
        depends: PhpBrowser
    - \Tests\Support\Helper\Api
```

---

## §2 Acceptance Tests (UI)

### Cest Pattern (Recommended)
```php
<?php
// tests/Acceptance/LoginCest.php
namespace Tests\Acceptance;

use Tests\Support\AcceptanceTester;
use Tests\Support\Page\LoginPage;

class LoginCest
{
    public function _before(AcceptanceTester $I): void
    {
        $I->amOnPage('/login');
    }

    public function loginWithValidCredentials(AcceptanceTester $I): void
    {
        $I->wantTo('login with valid credentials');
        $I->fillField('#email', 'user@test.com');
        $I->fillField('#password', 'ValidPass123');
        $I->click('#login-submit');
        $I->waitForText('Dashboard', 10);
        $I->seeInCurrentUrl('/dashboard');
        $I->see('Welcome back');
    }

    public function loginFailsWithInvalidPassword(AcceptanceTester $I): void
    {
        $I->wantTo('see error on invalid password');
        $I->fillField('#email', 'user@test.com');
        $I->fillField('#password', 'wrong');
        $I->click('#login-submit');
        $I->waitForElement('.error-message', 5);
        $I->see('Invalid email or password', '.error-message');
        $I->seeInCurrentUrl('/login');
    }

    /** @dataProvider loginDataProvider */
    public function loginWithDataProvider(AcceptanceTester $I, \Codeception\Example $example): void
    {
        $I->fillField('#email', $example['email']);
        $I->fillField('#password', $example['password']);
        $I->click('#login-submit');
        if ($example['success']) {
            $I->seeInCurrentUrl('/dashboard');
        } else {
            $I->see($example['error'], '.error-message');
        }
    }

    protected function loginDataProvider(): array
    {
        return [
            ['email' => 'user@test.com', 'password' => 'ValidPass123', 'success' => true, 'error' => ''],
            ['email' => 'wrong@test.com', 'password' => 'pass', 'success' => false, 'error' => 'Invalid'],
            ['email' => '', 'password' => 'pass', 'success' => false, 'error' => 'Email is required'],
        ];
    }
}
```

---

## §3 API Tests

```php
<?php
// tests/Api/UsersCest.php
namespace Tests\Api;

use Tests\Support\ApiTester;
use Codeception\Util\HttpCode;

class UsersCest
{
    private string $token = '';
    private int $userId = 0;

    public function _before(ApiTester $I): void
    {
        $I->haveHttpHeader('Content-Type', 'application/json');
        $I->sendPost('/auth/login', [
            'email' => 'admin@test.com',
            'password' => 'AdminPass123',
        ]);
        $this->token = $I->grabDataFromResponseByJsonPath('$.token')[0];
        $I->amBearerAuthenticated($this->token);
    }

    public function createUser(ApiTester $I): void
    {
        $I->wantTo('create a new user');
        $I->sendPost('/users', [
            'name' => 'Test User',
            'email' => 'new-user@test.com',
            'role' => 'viewer',
        ]);
        $I->seeResponseCodeIs(HttpCode::CREATED);
        $I->seeResponseIsJson();
        $I->seeResponseContainsJson(['name' => 'Test User']);
        $this->userId = $I->grabDataFromResponseByJsonPath('$.id')[0];
    }

    /** @depends createUser */
    public function getUser(ApiTester $I): void
    {
        $I->sendGet("/users/{$this->userId}");
        $I->seeResponseCodeIs(HttpCode::OK);
        $I->seeResponseContainsJson(['name' => 'Test User', 'role' => 'viewer']);
    }

    /** @depends createUser */
    public function updateUser(ApiTester $I): void
    {
        $I->sendPut("/users/{$this->userId}", [
            'name' => 'Updated User',
            'role' => 'editor',
        ]);
        $I->seeResponseCodeIs(HttpCode::OK);
        $I->seeResponseContainsJson(['name' => 'Updated User']);
    }

    /** @depends createUser */
    public function deleteUser(ApiTester $I): void
    {
        $I->sendDelete("/users/{$this->userId}");
        $I->seeResponseCodeIs(HttpCode::NO_CONTENT);
    }

    public function createUserValidation(ApiTester $I): void
    {
        $I->sendPost('/users', ['name' => '']);
        $I->seeResponseCodeIs(HttpCode::UNPROCESSABLE_ENTITY);
        $I->seeResponseContainsJson(['field' => 'email']);
    }

    public function unauthorizedAccess(ApiTester $I): void
    {
        $I->deleteHeader('Authorization');
        $I->sendGet('/users');
        $I->seeResponseCodeIs(HttpCode::UNAUTHORIZED);
    }
}
```

---

## §4 Page Objects

```php
<?php
// tests/Support/Page/LoginPage.php
namespace Tests\Support\Page;

use Tests\Support\AcceptanceTester;

class LoginPage
{
    public static string $URL = '/login';
    public static string $emailField = '#email';
    public static string $passwordField = '#password';
    public static string $submitButton = '#login-submit';
    public static string $errorMessage = '.error-message';

    protected AcceptanceTester $tester;

    public function __construct(AcceptanceTester $I)
    {
        $this->tester = $I;
    }

    public function login(string $email, string $password): void
    {
        $this->tester->amOnPage(self::$URL);
        $this->tester->fillField(self::$emailField, $email);
        $this->tester->fillField(self::$passwordField, $password);
        $this->tester->click(self::$submitButton);
    }

    public function seeError(string $message): void
    {
        $this->tester->waitForElement(self::$errorMessage, 5);
        $this->tester->see($message, self::$errorMessage);
    }
}
```

---

## §5 Database Testing

```php
<?php
// tests/Functional/DatabaseCest.php
namespace Tests\Functional;

use Tests\Support\FunctionalTester;

class DatabaseCest
{
    public function _before(FunctionalTester $I): void
    {
        $I->haveInDatabase('users', [
            'name' => 'Test User',
            'email' => 'db-test@test.com',
            'role' => 'viewer',
        ]);
    }

    public function seeUserInDatabase(FunctionalTester $I): void
    {
        $I->seeInDatabase('users', ['email' => 'db-test@test.com']);
    }

    public function updateUser(FunctionalTester $I): void
    {
        $I->updateInDatabase('users',
            ['role' => 'admin'],
            ['email' => 'db-test@test.com']
        );
        $I->seeInDatabase('users', ['email' => 'db-test@test.com', 'role' => 'admin']);
    }

    public function _after(FunctionalTester $I): void
    {
        $I->dontSeeInDatabase('users', ['email' => 'db-test@test.com']);
    }
}
```

---

## §6 Custom Helpers & Extensions

```php
<?php
// tests/Support/Helper/Acceptance.php
namespace Tests\Support\Helper;

use Codeception\Module;

class Acceptance extends Module
{
    public function loginAs(string $email, string $password = 'TestPass123'): void
    {
        $I = $this->getModule('WebDriver');
        $I->amOnPage('/login');
        $I->fillField('#email', $email);
        $I->fillField('#password', $password);
        $I->click('#login-submit');
        $I->waitForText('Dashboard', 10);
    }

    public function seeFlashMessage(string $message): void
    {
        $I = $this->getModule('WebDriver');
        $I->waitForElement('.flash-message', 5);
        $I->see($message, '.flash-message');
    }
}
```

---

## §7 CI/CD Integration

### GitHub Actions
```yaml
name: Codeception Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  codeception:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: testdb
        ports: ['3306:3306']
      selenium:
        image: selenium/standalone-chrome:latest
        ports: ['4444:4444']

    steps:
      - uses: actions/checkout@v4
      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.3'
          extensions: pdo_mysql, mbstring
      - run: composer install --no-interaction

      - name: Run Codeception
        run: |
          php vendor/bin/codecept run \
            --steps \
            --xml reports/junit.xml \
            --html reports/report.html \
            --coverage --coverage-xml reports/coverage.xml
        env:
          APP_ENV: testing
          DB_HOST: 127.0.0.1

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: codeception-results
          path: tests/_output/
```

---

## §8 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `ElementNotFound` in acceptance test | Element not visible or page not loaded | Use `waitForElement` before interaction; increase timeout |
| 2 | `_before` runs before every test method | Expected behavior for Cest | Use `_passed` / `_failed` for conditional cleanup |
| 3 | API test sees wrong response | Previous test left state | Use `_before` to re-authenticate; clean database per test |
| 4 | `grabDataFromResponseByJsonPath` returns empty | Wrong JSONPath expression | Test JSONPath against response body manually; use `$` root |
| 5 | `@depends` test skipped | Dependency test failed | Fix dependency first; avoid tight coupling between tests |
| 6 | WebDriver not connecting | Selenium not running or wrong host | Check `url` in suite config; verify Selenium is accessible |
| 7 | Database module conflicts | Module not enabled in suite config | Add `Db` module to suite YAML; configure DSN |
| 8 | Coverage report empty | Xdebug/pcov not installed | Install pcov: `pecl install pcov`; add to php.ini |
| 9 | Parallel tests interfere | Shared database state | Use separate databases per process or transaction isolation |
| 10 | Custom helper methods not found | Helper not enabled in suite | Add helper class path to suite `modules.enabled` |
| 11 | `amBearerAuthenticated` not working | Token format wrong | Use raw token without "Bearer " prefix; module adds it |
| 12 | Screenshots not generated | Output directory not writable | Check `tests/_output` permissions; create directory if missing |

---

## §9 Best Practices Checklist

1. Use Cest format over Cept — object-oriented, reusable, supports dependencies
2. Use `@dataProvider` for parameterized tests — avoid duplicating test methods
3. Use Page Objects — centralize selectors and page interactions
4. Use `amBearerAuthenticated` for API auth — cleaner than manual headers
5. Use `waitForElement` / `waitForText` — never use `sleep()` or `wait()`
6. Use `grabDataFromResponseByJsonPath` — chain API responses between steps
7. Use database module for fixtures — `haveInDatabase` / `seeInDatabase`
8. Use environments for config switching — `--env staging` or `--env ci`
9. Use `wantTo` for test documentation — generates readable reports
10. Use `RunFailed` extension — re-run only failed tests in CI
11. Use Recorder extension — visual debugging with screenshots per step
12. Use `@depends` sparingly — prefer independent tests over chains
13. Use coverage with pcov — faster than Xdebug for coverage collection
14. Use groups for selective execution — `--group smoke`, `--group api`
