# Codeception — Advanced Patterns & Playbook

## API Testing Module

```php
// tests/Api/UserCest.php
class UserCest
{
    public function _before(ApiTester $I)
    {
        $I->haveHttpHeader('Content-Type', 'application/json');
        $I->haveHttpHeader('Authorization', 'Bearer ' . $I->getToken());
    }

    public function createUser(ApiTester $I)
    {
        $I->sendPost('/api/users', ['name' => 'Alice', 'email' => 'alice@test.com']);
        $I->seeResponseCodeIs(201);
        $I->seeResponseIsJson();
        $I->seeResponseContainsJson(['name' => 'Alice']);
        $I->seeResponseMatchesJsonType([
            'id' => 'integer',
            'name' => 'string',
            'email' => 'string:email',
            'created_at' => 'string:date'
        ]);
    }

    public function listUsers(ApiTester $I)
    {
        $I->sendGet('/api/users', ['page' => 1, 'limit' => 10]);
        $I->seeResponseCodeIs(200);
        $I->seeResponseJsonMatchesJsonPath('$.data[*].id');
    }
}
```

## Page Object Pattern

```php
// tests/_support/Page/Login.php
class LoginPage
{
    public static $url = '/login';
    public static $usernameField = '#username';
    public static $passwordField = '#password';
    public static $submitBtn = '#login-btn';
    public static $errorMsg = '.error-message';

    public static function route($param) { return static::$url . '/' . $param; }
}

// Usage in Cest
class LoginCest
{
    public function loginSuccessfully(AcceptanceTester $I)
    {
        $I->amOnPage(LoginPage::$url);
        $I->fillField(LoginPage::$usernameField, 'admin');
        $I->fillField(LoginPage::$passwordField, 'secret');
        $I->click(LoginPage::$submitBtn);
        $I->see('Dashboard');
    }
}
```

## Data Factories

```php
// tests/_support/Helper/DataFactory.php
class DataFactory extends Module
{
    public function createUser(array $overrides = []): array
    {
        $defaults = ['name' => 'Test User', 'email' => uniqid() . '@test.com'];
        $data = array_merge($defaults, $overrides);
        return $this->getModule('REST')->_request('POST', '/api/users', $data);
    }
}
```

## Anti-Patterns

- ❌ Acceptance tests for unit-testable logic — use proper test levels
- ❌ `$I->wait(5)` — use `$I->waitForElement()` or `$I->waitForText()`
- ❌ Hardcoded selectors in Cest files — use Page Objects
- ❌ Missing `_before`/`_after` cleanup — state leaks between scenarios
