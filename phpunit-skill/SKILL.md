---
name: phpunit-skill
description: >
  Generates PHPUnit tests in PHP. Covers assertions, data providers, mocking,
  and test doubles. Use when user mentions "PHPUnit", "TestCase", "assertEquals",
  "PHP test". Triggers on: "PHPUnit", "TestCase PHP", "assertEquals PHP",
  "PHP unit test".
languages:
  - PHP
category: unit-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# PHPUnit Testing Skill

## Core Patterns

### Basic Test

```php
<?php
use PHPUnit\Framework\TestCase;

class CalculatorTest extends TestCase
{
    private Calculator $calculator;

    protected function setUp(): void
    {
        $this->calculator = new Calculator();
    }

    public function testAddition(): void
    {
        $this->assertEquals(5, $this->calculator->add(2, 3));
    }

    public function testDivideByZero(): void
    {
        $this->expectException(\DivisionByZeroError::class);
        $this->calculator->divide(10, 0);
    }

    public function testMultipleAssertions(): void
    {
        $this->assertSame(4, $this->calculator->add(2, 2));
        $this->assertSame(0, $this->calculator->subtract(2, 2));
        $this->assertSame(6, $this->calculator->multiply(2, 3));
    }
}
```

### Data Providers

```php
/**
 * @dataProvider additionProvider
 */
public function testAdd(int $a, int $b, int $expected): void
{
    $this->assertEquals($expected, $this->calculator->add($a, $b));
}

public static function additionProvider(): array
{
    return [
        'positive numbers' => [2, 3, 5],
        'negative numbers' => [-1, -1, -2],
        'zeros'            => [0, 0, 0],
        'mixed'            => [10, -5, 5],
    ];
}
```

### Assertions

```php
$this->assertEquals($expected, $actual);
$this->assertSame($expected, $actual);          // Strict type
$this->assertNotEquals($unexpected, $actual);
$this->assertTrue($condition);
$this->assertFalse($condition);
$this->assertNull($value);
$this->assertNotNull($value);
$this->assertCount(3, $array);
$this->assertContains('item', $array);
$this->assertArrayHasKey('key', $array);
$this->assertInstanceOf(MyClass::class, $obj);
$this->assertStringContainsString('sub', $string);
$this->assertMatchesRegularExpression('/\d+/', $string);
$this->assertEmpty($collection);
$this->assertGreaterThan(5, $value);
$this->assertJsonStringEqualsJsonString($expected, $actual);
```

### Mocking

```php
public function testCreateUser(): void
{
    $mockRepo = $this->createMock(UserRepository::class);
    $mockRepo->expects($this->once())
        ->method('save')
        ->with($this->isInstanceOf(User::class))
        ->willReturn(new User(1, 'Alice'));

    $mockEmail = $this->createMock(EmailService::class);
    $mockEmail->expects($this->once())
        ->method('sendWelcome')
        ->with('alice@test.com');

    $service = new UserService($mockRepo, $mockEmail);
    $result = $service->createUser('alice@test.com', 'Alice');

    $this->assertEquals(1, $result->getId());
}
```

### Lifecycle

```php
public static function setUpBeforeClass(): void { }   // Once before all
protected function setUp(): void { }                    // Before each test
protected function tearDown(): void { }                 // After each test
public static function tearDownAfterClass(): void { }  // Once after all
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| `assertEquals` for strict | `assertSame` for type+value | Type coercion |
| No data providers | `@dataProvider` | DRY |
| Global state | `setUp()`/`tearDown()` | Isolation |
| No groups | `@group smoke` | Run subsets |

## Setup: `composer require --dev phpunit/phpunit`
## Run: `./vendor/bin/phpunit` or `./vendor/bin/phpunit --group smoke`
## Config: `phpunit.xml` with testsuites and coverage

## Deep Patterns

See `reference/playbook.md` for production-grade patterns:

| Section | What You Get |
|---------|-------------|
| §1 Project Setup | composer.json, phpunit.xml with suites, coverage config, project structure |
| §2 Test Patterns | Assertions, #[DataProvider], Generator yields, strict comparisons |
| §3 Mocking | createMock with callbacks, Mockery spies, consecutive returns |
| §4 Test Doubles | In-memory fakes, repository pattern, test helpers |
| §5 Faker & Fixtures | TestDataFactory with overrides, bulk generation |
| §6 Exception Testing | Detailed exception assertions, warning testing |
| §7 HTTP & API Testing | Symfony WebTestCase, auth, validation, pagination |
| §8 Database Testing | Transaction rollback, repository integration, Doctrine |
| §9 CI/CD Integration | GitHub Actions with MySQL/Redis, coverage thresholds |
| §10 Debugging Table | 12 common problems with causes and fixes |
| §11 Best Practices | 14-item production PHP testing checklist |
