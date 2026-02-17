---
name: codeception-testing-skill
description: >
  Generates Codeception tests in PHP covering acceptance, functional, and unit
  testing. BDD-style with Actor pattern. Use when user mentions "Codeception",
  "$I->amOnPage", "$I->see", "Cest". Triggers on: "Codeception", "$I->amOnPage",
  "AcceptanceTester", "Codeception PHP", "Cest".
languages:
  - PHP
category: e2e-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Codeception Testing Skill

## Core Patterns

### Acceptance Test (Cest)

```php
<?php
// tests/Acceptance/LoginCest.php

class LoginCest
{
    public function _before(AcceptanceTester $I)
    {
        $I->amOnPage('/login');
    }

    public function loginWithValidCredentials(AcceptanceTester $I)
    {
        $I->fillField('email', 'user@test.com');
        $I->fillField('password', 'password123');
        $I->click('Login');
        $I->see('Dashboard');
        $I->seeInCurrentUrl('/dashboard');
        $I->seeElement('.welcome-message');
    }

    public function loginWithInvalidCredentials(AcceptanceTester $I)
    {
        $I->fillField('email', 'wrong@test.com');
        $I->fillField('password', 'wrong');
        $I->click('Login');
        $I->see('Invalid credentials');
        $I->seeInCurrentUrl('/login');
    }
}
```

### Actor Methods (AcceptanceTester $I)

```php
// Navigation
$I->amOnPage('/path');
$I->click('Button Text');
$I->click('#id');
$I->click(['xpath' => '//button']);

// Forms
$I->fillField('Name or Label', 'value');
$I->selectOption('Select', 'Option');
$I->checkOption('Checkbox');
$I->uncheckOption('Checkbox');
$I->attachFile('Upload', 'file.txt');
$I->submitForm('#form', ['email' => 'test@x.com']);

// Assertions
$I->see('Text');
$I->dontSee('Text');
$I->seeElement('#id');
$I->dontSeeElement('.error');
$I->seeInField('email', 'expected@value.com');
$I->seeInCurrentUrl('/dashboard');
$I->seeInTitle('Page Title');
$I->seeCheckboxIsChecked('#agree');
$I->seeNumberOfElements('li', 5);

// Grabbers
$text = $I->grabTextFrom('.element');
$attr = $I->grabAttributeFrom('#link', 'href');
$value = $I->grabValueFrom('#input');
```

### Page Objects (Step Objects)

```php
<?php
// tests/_support/Page/Login.php
namespace Page;

class Login
{
    public static $url = '/login';
    public static $emailField = '#email';
    public static $passwordField = '#password';
    public static $loginButton = 'button[type="submit"]';

    protected $I;
    public function __construct(\AcceptanceTester $I) { $this->I = $I; }

    public function login(string $email, string $password): void
    {
        $this->I->amOnPage(self::$url);
        $this->I->fillField(self::$emailField, $email);
        $this->I->fillField(self::$passwordField, $password);
        $this->I->click(self::$loginButton);
    }
}
```

### Cloud (TestMu AI)

Full setup: [reference/cloud-integration.md](reference/cloud-integration.md). Capabilities reference: [shared/testmu-cloud-reference.md](../shared/testmu-cloud-reference.md).

### Cloud Config (acceptance.suite.yml)

```yaml
actor: AcceptanceTester
modules:
  enabled:
    - WebDriver:
        url: 'http://localhost:3000'
        host: 'hub.lambdatest.com'
        port: 80
        browser: chrome
        capabilities:
          'LT:Options':
            user: '%LT_USERNAME%'
            accessKey: '%LT_ACCESS_KEY%'
            build: 'Codeception Build'
            video: true
```

## Setup: `composer require --dev codeception/codeception codeception/module-webdriver`
## Init: `php vendor/bin/codecept bootstrap`
## Run: `php vendor/bin/codecept run acceptance`

## Deep Patterns

See `reference/playbook.md` for production-grade patterns:

| Section | What You Get |
|---------|-------------|
| §1 Project Setup | Installation, codeception.yml, suite configurations |
| §2 Acceptance Tests | Cest pattern, @dataProvider, WebDriver interactions |
| §3 API Tests | REST module, CRUD operations, @depends, HttpCode |
| §4 Page Objects | Page class with static selectors, reusable methods |
| §5 Database Testing | haveInDatabase, seeInDatabase, updateInDatabase |
| §6 Custom Helpers | Custom module extending Codeception Module |
| §7 CI/CD Integration | GitHub Actions with MySQL, Selenium, coverage |
| §8 Debugging Table | 12 common problems with causes and fixes |
| §9 Best Practices | 14-item Codeception testing checklist |
