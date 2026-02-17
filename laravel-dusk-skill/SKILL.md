---
name: laravel-dusk-skill
description: >
  Generates Laravel Dusk browser tests in PHP. Chrome-based E2E testing for
  Laravel apps. Use when user mentions "Dusk", "Laravel Dusk", "$browser->visit",
  "DuskTestCase". Triggers on: "Laravel Dusk", "Dusk test", "$browser->visit",
  "DuskTestCase".
languages:
  - PHP
category: e2e-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Laravel Dusk Skill

For TestMu AI cloud execution, see [reference/cloud-integration.md](reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../shared/testmu-cloud-reference.md).

## Core Patterns

### Basic Test

```php
<?php
namespace Tests\Browser;

use Laravel\Dusk\Browser;
use Tests\DuskTestCase;

class LoginTest extends DuskTestCase
{
    public function testLoginWithValidCredentials(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/login')
                ->type('email', 'user@test.com')
                ->type('password', 'password123')
                ->press('Login')
                ->assertPathIs('/dashboard')
                ->assertSee('Welcome');
        });
    }

    public function testLoginWithInvalidCredentials(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/login')
                ->type('email', 'wrong@test.com')
                ->type('password', 'wrong')
                ->press('Login')
                ->assertPathIs('/login')
                ->assertSee('Invalid credentials');
        });
    }
}
```

### Browser Methods

```php
// Navigation
$browser->visit('/path');
$browser->back();
$browser->forward();
$browser->refresh();

// Forms
$browser->type('name', 'value');
$browser->clear('name');
$browser->select('select', 'option');
$browser->check('checkbox');
$browser->uncheck('checkbox');
$browser->radio('radio', 'value');
$browser->attach('file', '/path/to/file');
$browser->press('Button Text');
$browser->click('.selector');

// Assertions
$browser->assertSee('text');
$browser->assertDontSee('text');
$browser->assertPathIs('/expected');
$browser->assertUrlIs('http://full-url');
$browser->assertInputValue('name', 'value');
$browser->assertChecked('checkbox');
$browser->assertVisible('.element');
$browser->assertMissing('.element');
$browser->assertTitle('Page Title');
$browser->assertPresent('.selector');

// Waiting
$browser->waitFor('.element');
$browser->waitFor('.element', 10); // 10 seconds
$browser->waitUntilMissing('.loading');
$browser->waitForText('Loaded');
$browser->waitForLink('Click Me');
$browser->pause(1000); // milliseconds
```

### Page Objects

```php
<?php
namespace Tests\Browser\Pages;

use Laravel\Dusk\Page;

class LoginPage extends Page
{
    public function url(): string { return '/login'; }

    public function assert(Browser $browser): void
    {
        $browser->assertPathIs($this->url());
    }

    public function login(Browser $browser, string $email, string $password): void
    {
        $browser->type('email', $email)
            ->type('password', $password)
            ->press('Login');
    }
}

// Usage
$browser->visit(new LoginPage)
    ->login($browser, 'user@test.com', 'password123');
```

### Cloud: Override `DuskTestCase::driver()` to return `RemoteWebDriver` with LT caps

## Setup: `composer require --dev laravel/dusk && php artisan dusk:install`

### Cloud Execution on TestMu AI

Set `.env` variables: `LT_USERNAME`, `LT_ACCESS_KEY`

```php
// tests/DuskTestCase.php
protected function driver()
{
    $options = (new ChromeOptions)->addArguments(['--disable-gpu', '--no-sandbox']);
    $ltOptions = [
        'user' => env('LT_USERNAME'),
        'accessKey' => env('LT_ACCESS_KEY'),
        'build' => 'Laravel Dusk Build',
        'name' => $this->getName(),
        'platformName' => 'Windows 11',
        'video' => true,
        'console' => true,
    ];
    $options->setExperimentalOption('LT:Options', $ltOptions);
    return RemoteWebDriver::create(
        'https://hub.lambdatest.com/wd/hub', $options
    );
}
```
## Run: `php artisan dusk` or `php artisan dusk tests/Browser/LoginTest.php`

## Deep Patterns

See `reference/playbook.md` for production-grade patterns:

| Section | What You Get |
|---------|-------------|
| §1 Project Setup | Installation, DuskTestCase, .env.dusk configuration |
| §2 Browser Tests | Login flows, forms, multi-step wizards, multiple browsers |
| §3 Page Objects | Page class with elements, custom methods, assertions |
| §4 Components | DatePicker, Modal, reusable component pattern |
| §5 Advanced Interactions | JavaScript, scrolling, drag-and-drop, waiting strategies |
| §6 Database & Data | DatabaseMigrations, factories, screenshots, console logs |
| §7 LambdaTest Integration | Remote WebDriver with LT:Options capabilities |
| §8 CI/CD Integration | GitHub Actions with MySQL, ChromeDriver, artifact upload |
| §9 Debugging Table | 12 common problems with causes and fixes |
| §10 Best Practices | 14-item Laravel Dusk testing checklist |
