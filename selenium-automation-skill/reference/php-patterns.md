# Selenium — PHP Patterns

## Setup

```bash
composer require phpunit/phpunit php-webdriver/webdriver
```

```json
// composer.json (relevant part)
{
  "require-dev": {
    "phpunit/phpunit": "^10",
    "php-webdriver/webdriver": "^1.14"
  },
  "autoload": {
    "classmap": ["src/", "tests/"]
  }
}
```

## Basic Test (PHPUnit)

```php
<?php

use PHPUnit\Framework\TestCase;
use Facebook\WebDriver\Remote\RemoteWebDriver;
use Facebook\WebDriver\Remote\DesiredCapabilities;
use Facebook\WebDriver\WebDriverBy;
use Facebook\WebDriver\WebDriverExpectedCondition;

class LoginTest extends TestCase
{
    private $driver;
    private $wait;

    protected function setUp(): void
    {
        $caps = DesiredCapabilities::chrome();
        $this->driver = RemoteWebDriver::create('http://localhost:9515', $caps);
        $this->driver->manage()->window()->maximize();
        $this->wait = $this->driver->wait(10);
    }

    public function testLogin(): void
    {
        $this->driver->get('https://example.com/login');
        $this->wait->until(
            WebDriverExpectedCondition::visibilityOfElementLocated(WebDriverBy::id('username'))
        );
        $this->driver->findElement(WebDriverBy::id('username'))->sendKeys('user@test.com');
        $this->driver->findElement(WebDriverBy::id('password'))->sendKeys('password123');
        $this->driver->findElement(WebDriverBy::cssSelector('button[type="submit"]'))->click();
        $this->wait->until(WebDriverExpectedCondition::urlContains('/dashboard'));
        $this->assertStringContainsString('Dashboard', $this->driver->getTitle());
    }

    protected function tearDown(): void
    {
        if ($this->driver) {
            $this->driver->quit();
        }
    }
}
```

## TestMu AI Cloud (PHP)

```php
<?php

use Facebook\WebDriver\Remote\RemoteWebDriver;
use Facebook\WebDriver\Remote\WebDriverCapabilityType;

$username = getenv('LT_USERNAME');
$accessKey = getenv('LT_ACCESS_KEY');
$hubUrl = "https://{$username}:{$accessKey}@hub.lambdatest.com/wd/hub";

$capabilities = [
    WebDriverCapabilityType::BROWSER_NAME => 'Chrome',
    WebDriverCapabilityType::BROWSER_VERSION => 'latest',
    'LT:Options' => [
        'platform' => 'Windows 11',
        'build' => 'PHP Build',
        'name' => 'PHP Test',
        'video' => true,
        'network' => true,
    ],
];

$driver = RemoteWebDriver::create($hubUrl, $capabilities);
$driver->manage()->window()->maximize();
```

## Page Object in PHP

```php
<?php

use Facebook\WebDriver\Remote\RemoteWebDriver;
use Facebook\WebDriver\WebDriverBy;
use Facebook\WebDriver\WebDriverExpectedCondition;

class LoginPage
{
    private $driver;
    private $wait;

    private static $usernameField = WebDriverBy::id('username');
    private static $passwordField = WebDriverBy::id('password');
    private static $submitButton = WebDriverBy::cssSelector('button[type="submit"]');

    public function __construct(RemoteWebDriver $driver)
    {
        $this->driver = $driver;
        $this->wait = $driver->wait(10);
    }

    public function login(string $username, string $password): void
    {
        $this->wait->until(
            WebDriverExpectedCondition::visibilityOfElementLocated(self::$usernameField)
        );
        $this->driver->findElement(self::$usernameField)->sendKeys($username);
        $this->driver->findElement(self::$passwordField)->sendKeys($password);
        $this->driver->findElement(self::$submitButton)->click();
    }
}
```

## Run Tests

```bash
./vendor/bin/phpunit tests/
```

## Notes

- Use explicit waits via `$driver->wait(seconds)` and `WebDriverExpectedCondition` — avoid `sleep()`.
- Always call `$driver->quit()` in `tearDown()`.
- For full device/capability reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
