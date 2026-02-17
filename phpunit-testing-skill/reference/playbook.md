# PHPUnit — Advanced Playbook

## §1 Project Setup & Configuration

### composer.json (Test Dependencies)
```json
{
    "require-dev": {
        "phpunit/phpunit": "^11.0",
        "mockery/mockery": "^1.6",
        "fakerphp/faker": "^1.23",
        "phpstan/phpstan": "^1.10",
        "squizlabs/php_codesniffer": "^3.8",
        "symfony/http-client": "^7.0",
        "dms/phpunit-arraysubset-asserts": "^0.5"
    },
    "autoload": {
        "psr-4": { "App\\": "src/" }
    },
    "autoload-dev": {
        "psr-4": { "Tests\\": "tests/" }
    },
    "scripts": {
        "test": "phpunit",
        "test:coverage": "XDEBUG_MODE=coverage phpunit --coverage-html coverage",
        "test:filter": "phpunit --filter"
    }
}
```

### phpunit.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<phpunit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="vendor/phpunit/phpunit/phpunit.xsd"
         bootstrap="vendor/autoload.php"
         colors="true"
         failOnWarning="true"
         failOnRisky="true"
         cacheDirectory=".phpunit.cache"
         executionOrder="depends,defects"
         beStrictAboutCoverageMetadata="true"
         requireCoverageMetadata="false">

    <testsuites>
        <testsuite name="Unit">
            <directory>tests/Unit</directory>
        </testsuite>
        <testsuite name="Feature">
            <directory>tests/Feature</directory>
        </testsuite>
        <testsuite name="Integration">
            <directory>tests/Integration</directory>
        </testsuite>
    </testsuites>

    <coverage>
        <report>
            <html outputDirectory="coverage"/>
            <clover outputFile="coverage/clover.xml"/>
            <text outputFile="php://stdout" showOnlySummary="true"/>
        </report>
    </coverage>

    <source>
        <include>
            <directory>src</directory>
        </include>
        <exclude>
            <directory>src/Migrations</directory>
        </exclude>
    </source>

    <php>
        <env name="APP_ENV" value="testing"/>
        <env name="DB_DATABASE" value="testing"/>
        <env name="CACHE_DRIVER" value="array"/>
    </php>
</phpunit>
```

### Project Structure
```
project/
├── phpunit.xml
├── composer.json
├── src/
│   ├── Entity/
│   ├── Repository/
│   ├── Service/
│   └── Controller/
├── tests/
│   ├── Unit/
│   │   ├── Entity/
│   │   ├── Service/
│   │   └── ValueObject/
│   ├── Feature/
│   │   ├── Api/
│   │   └── Controller/
│   ├── Integration/
│   │   ├── Repository/
│   │   └── ExternalApi/
│   ├── Fixtures/
│   │   └── UserFixture.php
│   └── TestCase.php           # Base test case
├── coverage/
└── .phpunit.cache/
```

---

## §2 Test Patterns — Assertions & Data Providers

### Comprehensive Assertions
```php
<?php

declare(strict_types=1);

namespace Tests\Unit\Entity;

use App\Entity\User;
use App\ValueObject\Email;
use PHPUnit\Framework\TestCase;
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\Attributes\CoversClass;
use PHPUnit\Framework\Attributes\DataProvider;

#[CoversClass(User::class)]
class UserTest extends TestCase
{
    #[Test]
    public function createsUserWithValidData(): void
    {
        $user = new User(
            name: 'Alice Smith',
            email: new Email('alice@example.com'),
            age: 30,
        );

        // Strict identity (===)
        $this->assertSame('Alice Smith', $user->getName());
        $this->assertSame(30, $user->getAge());

        // Type checks
        $this->assertInstanceOf(Email::class, $user->getEmail());

        // Boolean
        $this->assertTrue($user->isActive());
        $this->assertFalse($user->isAdmin());

        // Null checks
        $this->assertNull($user->getDeletedAt());
        $this->assertNotNull($user->getCreatedAt());

        // String assertions
        $this->assertStringStartsWith('usr_', $user->getId());
        $this->assertStringEndsWith('@example.com', (string) $user->getEmail());
        $this->assertStringContainsString('Alice', $user->getName());
        $this->assertMatchesRegularExpression('/^usr_[a-f0-9]{12}$/', $user->getId());

        // Numeric
        $this->assertGreaterThan(0, $user->getAge());
        $this->assertLessThanOrEqual(150, $user->getAge());

        // Array/Collection
        $this->assertCount(0, $user->getRoles());
        $this->assertEmpty($user->getRoles());
        $this->assertContains('ROLE_USER', $user->getDefaultRoles());
    }

    #[Test]
    #[DataProvider('invalidEmailProvider')]
    public function rejectsInvalidEmails(string $email, string $reason): void
    {
        $this->expectException(\InvalidArgumentException::class);
        new Email($email);
    }

    public static function invalidEmailProvider(): \Generator
    {
        yield 'empty string' => ['', 'cannot be empty'];
        yield 'no @ symbol' => ['invalid', 'missing @'];
        yield 'no domain' => ['user@', 'missing domain'];
        yield 'no local part' => ['@domain.com', 'missing local part'];
        yield 'spaces' => ['user @domain.com', 'contains spaces'];
        yield 'double dots' => ['user@domain..com', 'consecutive dots'];
    }

    #[Test]
    #[DataProvider('ageValidationProvider')]
    public function validatesAge(int $age, bool $shouldPass): void
    {
        if (!$shouldPass) {
            $this->expectException(\DomainException::class);
        }

        $user = new User(name: 'Test', email: new Email('t@t.com'), age: $age);

        if ($shouldPass) {
            $this->assertSame($age, $user->getAge());
        }
    }

    public static function ageValidationProvider(): array
    {
        return [
            'minimum valid' => [0, true],
            'typical age' => [30, true],
            'maximum valid' => [150, true],
            'negative' => [-1, false],
            'too old' => [151, false],
        ];
    }
}
```

---

## §3 Mocking — createMock, Mockery, Prophecy

### PHPUnit Native Mocks
```php
<?php

namespace Tests\Unit\Service;

use App\Entity\User;
use App\Repository\UserRepositoryInterface;
use App\Service\UserService;
use App\Service\EmailService;
use App\Event\UserCreatedEvent;
use PHPUnit\Framework\TestCase;
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\MockObject\MockObject;

class UserServiceTest extends TestCase
{
    private UserRepositoryInterface&MockObject $repository;
    private EmailService&MockObject $emailService;
    private UserService $service;

    protected function setUp(): void
    {
        $this->repository = $this->createMock(UserRepositoryInterface::class);
        $this->emailService = $this->createMock(EmailService::class);
        $this->service = new UserService($this->repository, $this->emailService);
    }

    #[Test]
    public function createsAndPersistsUser(): void
    {
        // Expect save called once with a User argument
        $this->repository->expects($this->once())
            ->method('save')
            ->with($this->callback(function (User $user): bool {
                return $user->getName() === 'Alice'
                    && $user->getEmail()->toString() === 'alice@test.com';
            }))
            ->willReturnCallback(function (User $user): User {
                // Simulate DB assigning ID
                $reflection = new \ReflectionProperty($user, 'id');
                $reflection->setValue($user, 42);
                return $user;
            });

        // Expect welcome email sent
        $this->emailService->expects($this->once())
            ->method('sendWelcome')
            ->with($this->isInstanceOf(User::class));

        $user = $this->service->createUser('Alice', 'alice@test.com');
        $this->assertSame(42, $user->getId());
    }

    #[Test]
    public function throwsOnDuplicateEmail(): void
    {
        $this->repository->method('findByEmail')
            ->with('existing@test.com')
            ->willReturn(new User(name: 'Existing', email: 'existing@test.com'));

        $this->expectException(\DomainException::class);
        $this->expectExceptionMessage('Email already registered');

        $this->service->createUser('New User', 'existing@test.com');
    }

    #[Test]
    public function retriesOnTransientFailure(): void
    {
        $this->repository->expects($this->exactly(3))
            ->method('save')
            ->willReturnOnConsecutiveCalls(
                $this->throwException(new \RuntimeException('Connection lost')),
                $this->throwException(new \RuntimeException('Timeout')),
                $this->returnArgument(0),  // Third call succeeds
            );

        $user = $this->service->createUser('Alice', 'alice@test.com');
        $this->assertSame('Alice', $user->getName());
    }

    #[Test]
    public function listsUsersWithPagination(): void
    {
        $this->repository->method('findPaginated')
            ->with(
                $this->identicalTo(1),          // page
                $this->identicalTo(10),         // limit
                $this->stringContains('name'),  // sort field
            )
            ->willReturn([
                new User(name: 'Alice', email: 'a@t.com'),
                new User(name: 'Bob', email: 'b@t.com'),
            ]);

        $users = $this->service->listUsers(page: 1, limit: 10, sort: 'name_asc');
        $this->assertCount(2, $users);
    }
}
```

### Mockery Integration
```php
<?php

namespace Tests\Unit\Service;

use App\Service\PaymentGateway;
use App\Service\OrderService;
use Mockery;
use Mockery\Adapter\Phpunit\MockeryPHPUnitIntegration;
use PHPUnit\Framework\TestCase;

class OrderServiceTest extends TestCase
{
    use MockeryPHPUnitIntegration;

    #[Test]
    public function processesPaymentWithRetry(): void
    {
        $gateway = Mockery::mock(PaymentGateway::class);
        $gateway->shouldReceive('charge')
            ->with(Mockery::on(fn($amount) => $amount > 0), Mockery::type('string'))
            ->once()
            ->andReturn(['id' => 'pay_123', 'status' => 'success']);

        $service = new OrderService($gateway);
        $result = $service->processOrder(orderId: 'ord_1', amount: 99.99);

        $this->assertSame('pay_123', $result->paymentId);
    }

    #[Test]
    public function spiesOnMethodCalls(): void
    {
        $logger = Mockery::spy(\Psr\Log\LoggerInterface::class);
        $service = new OrderService(logger: $logger);

        $service->processOrder('ord_1', 50.00);

        $logger->shouldHaveReceived('info')
            ->with(Mockery::pattern('/Order processed/'), Mockery::hasKey('orderId'))
            ->once();
    }
}
```

---

## §4 Test Doubles — Stubs, Fakes & In-Memory Implementations

```php
<?php

namespace Tests\Doubles;

use App\Repository\UserRepositoryInterface;
use App\Entity\User;

/**
 * In-memory fake for integration tests — no database needed.
 */
class InMemoryUserRepository implements UserRepositoryInterface
{
    /** @var array<int, User> */
    private array $users = [];
    private int $nextId = 1;

    public function save(User $user): User
    {
        if ($user->getId() === null) {
            $reflection = new \ReflectionProperty($user, 'id');
            $reflection->setValue($user, $this->nextId++);
        }
        $this->users[$user->getId()] = $user;
        return $user;
    }

    public function findById(int $id): ?User
    {
        return $this->users[$id] ?? null;
    }

    public function findByEmail(string $email): ?User
    {
        foreach ($this->users as $user) {
            if ($user->getEmail()->toString() === $email) {
                return $user;
            }
        }
        return null;
    }

    public function findAll(): array
    {
        return array_values($this->users);
    }

    public function delete(User $user): void
    {
        unset($this->users[$user->getId()]);
    }

    /** Test helper: reset state between tests. */
    public function clear(): void
    {
        $this->users = [];
        $this->nextId = 1;
    }
}
```

### Using Fakes in Tests
```php
<?php

namespace Tests\Integration\Service;

use App\Service\UserService;
use Tests\Doubles\InMemoryUserRepository;
use PHPUnit\Framework\TestCase;

class UserServiceIntegrationTest extends TestCase
{
    private InMemoryUserRepository $repository;
    private UserService $service;

    protected function setUp(): void
    {
        $this->repository = new InMemoryUserRepository();
        $this->service = new UserService($this->repository);
    }

    #[Test]
    public function fullUserLifecycle(): void
    {
        // Create
        $user = $this->service->createUser('Alice', 'alice@test.com');
        $this->assertSame(1, $user->getId());

        // Read
        $found = $this->service->findUser(1);
        $this->assertSame('Alice', $found->getName());

        // Update
        $this->service->updateUser(1, name: 'Alice Smith');
        $updated = $this->service->findUser(1);
        $this->assertSame('Alice Smith', $updated->getName());

        // Delete
        $this->service->deleteUser(1);
        $this->assertNull($this->repository->findById(1));
    }
}
```

---

## §5 Faker & Fixtures — Realistic Test Data

```php
<?php

namespace Tests\Fixtures;

use App\Entity\User;
use App\Entity\Order;
use App\ValueObject\Email;
use App\ValueObject\Money;
use Faker\Factory as FakerFactory;
use Faker\Generator;

class TestDataFactory
{
    private static ?Generator $faker = null;

    private static function faker(): Generator
    {
        return self::$faker ??= FakerFactory::create();
    }

    public static function createUser(array $overrides = []): User
    {
        $faker = self::faker();
        return new User(
            name: $overrides['name'] ?? $faker->name(),
            email: new Email($overrides['email'] ?? $faker->unique()->safeEmail()),
            age: $overrides['age'] ?? $faker->numberBetween(18, 80),
        );
    }

    public static function createOrder(array $overrides = []): Order
    {
        $faker = self::faker();
        return new Order(
            userId: $overrides['userId'] ?? $faker->randomNumber(5),
            items: $overrides['items'] ?? self::createOrderItems(rand(1, 5)),
            total: $overrides['total'] ?? new Money($faker->randomFloat(2, 10, 1000), 'USD'),
            status: $overrides['status'] ?? 'pending',
        );
    }

    /** @return list<OrderItem> */
    public static function createOrderItems(int $count = 3): array
    {
        $faker = self::faker();
        return array_map(fn() => new \App\Entity\OrderItem(
            productId: $faker->randomNumber(5),
            name: $faker->words(3, true),
            price: new Money($faker->randomFloat(2, 5, 500), 'USD'),
            quantity: $faker->numberBetween(1, 10),
        ), range(1, $count));
    }
}
```

### Using Factories in Tests
```php
<?php

namespace Tests\Unit\Service;

use Tests\Fixtures\TestDataFactory;
use PHPUnit\Framework\TestCase;

class OrderProcessingTest extends TestCase
{
    #[Test]
    public function calculatesOrderTotal(): void
    {
        $order = TestDataFactory::createOrder([
            'items' => [
                TestDataFactory::createOrderItem(['price' => new Money(10.00, 'USD'), 'quantity' => 2]),
                TestDataFactory::createOrderItem(['price' => new Money(25.00, 'USD'), 'quantity' => 1]),
            ],
        ]);

        $this->assertEquals(45.00, $order->calculateTotal()->amount());
    }

    #[Test]
    public function bulkUserCreation(): void
    {
        $users = array_map(fn() => TestDataFactory::createUser(), range(1, 50));
        $this->assertCount(50, $users);
        // All emails unique
        $emails = array_map(fn($u) => $u->getEmail()->toString(), $users);
        $this->assertCount(50, array_unique($emails));
    }
}
```

---

## §6 Exception & Error Testing

```php
<?php

namespace Tests\Unit\Service;

use App\Exception\InsufficientFundsException;
use App\Exception\AccountLockedException;
use App\Service\AccountService;
use PHPUnit\Framework\TestCase;

class ExceptionHandlingTest extends TestCase
{
    #[Test]
    public function throwsInsufficientFundsWithDetails(): void
    {
        $service = new AccountService();

        try {
            $service->withdraw(accountId: 1, amount: 1000.00);
            $this->fail('Expected InsufficientFundsException was not thrown');
        } catch (InsufficientFundsException $e) {
            $this->assertSame(1, $e->getAccountId());
            $this->assertSame(1000.00, $e->getRequestedAmount());
            $this->assertSame(500.00, $e->getAvailableBalance());
            $this->assertSame(
                'Insufficient funds: requested $1000.00, available $500.00',
                $e->getMessage()
            );
            $this->assertSame(422, $e->getCode());
        }
    }

    #[Test]
    public function wrapsExternalApiErrors(): void
    {
        $this->expectException(\App\Exception\ExternalServiceException::class);
        $this->expectExceptionMessageMatches('/Payment gateway.*timeout/i');

        $service = new AccountService(gateway: new TimeoutStubGateway());
        $service->processPayment(orderId: 'ord_1', amount: 50.00);
    }

    #[Test]
    public function warningTriggered(): void
    {
        $this->expectWarning();
        $this->expectWarningMessage('Deprecated method');
        $service = new AccountService();
        $service->legacyTransfer(from: 1, to: 2, amount: 100);
    }
}
```

---

## §7 HTTP & API Testing (Symfony / Laravel)

### Symfony WebTestCase
```php
<?php

namespace Tests\Feature\Api;

use Symfony\Bundle\FrameworkBundle\Test\WebTestCase;
use Symfony\Component\HttpFoundation\Response;

class UserApiTest extends WebTestCase
{
    private $client;

    protected function setUp(): void
    {
        $this->client = static::createClient();
        // Reset database
        $this->loadFixtures();
    }

    #[Test]
    public function listUsersRequiresAuth(): void
    {
        $this->client->request('GET', '/api/users');
        $this->assertResponseStatusCodeSame(Response::HTTP_UNAUTHORIZED);
    }

    #[Test]
    public function createsUser(): void
    {
        $this->client->request('POST', '/api/users', [], [], [
            'CONTENT_TYPE' => 'application/json',
            'HTTP_AUTHORIZATION' => 'Bearer ' . $this->getAuthToken(),
        ], json_encode([
            'name' => 'Alice',
            'email' => 'alice@test.com',
            'role' => 'editor',
        ]));

        $this->assertResponseStatusCodeSame(Response::HTTP_CREATED);

        $data = json_decode($this->client->getResponse()->getContent(), true);
        $this->assertArrayHasKey('id', $data);
        $this->assertSame('Alice', $data['name']);
        $this->assertSame('alice@test.com', $data['email']);

        // Verify Location header
        $this->assertResponseHeaderSame(
            'Location',
            '/api/users/' . $data['id']
        );
    }

    #[Test]
    public function validatesRequiredFields(): void
    {
        $this->client->request('POST', '/api/users', [], [], [
            'CONTENT_TYPE' => 'application/json',
            'HTTP_AUTHORIZATION' => 'Bearer ' . $this->getAuthToken(),
        ], json_encode([]));

        $this->assertResponseStatusCodeSame(Response::HTTP_UNPROCESSABLE_ENTITY);
        $errors = json_decode($this->client->getResponse()->getContent(), true);
        $this->assertArrayHasKey('errors', $errors);
        $this->assertArrayHasKey('name', $errors['errors']);
        $this->assertArrayHasKey('email', $errors['errors']);
    }

    #[Test]
    public function paginatesResults(): void
    {
        // Seed 25 users
        $this->seedUsers(25);

        $this->client->request('GET', '/api/users?page=2&limit=10', [], [], [
            'HTTP_AUTHORIZATION' => 'Bearer ' . $this->getAuthToken(),
        ]);

        $this->assertResponseIsSuccessful();
        $data = json_decode($this->client->getResponse()->getContent(), true);
        $this->assertCount(10, $data['data']);
        $this->assertSame(25, $data['meta']['total']);
        $this->assertSame(2, $data['meta']['page']);
    }

    private function getAuthToken(): string
    {
        $this->client->request('POST', '/api/auth/login', [], [], [
            'CONTENT_TYPE' => 'application/json',
        ], json_encode(['email' => 'admin@test.com', 'password' => 'secret']));

        return json_decode($this->client->getResponse()->getContent(), true)['token'];
    }
}
```

---

## §8 Database Testing

### Repository Integration Tests
```php
<?php

namespace Tests\Integration\Repository;

use App\Entity\User;
use App\Repository\UserRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Test\KernelTestCase;

class UserRepositoryTest extends KernelTestCase
{
    private EntityManagerInterface $em;
    private UserRepository $repository;

    protected function setUp(): void
    {
        $kernel = self::bootKernel();
        $this->em = $kernel->getContainer()
            ->get('doctrine')
            ->getManager();

        $this->repository = $this->em->getRepository(User::class);

        // Start transaction — rolled back in tearDown
        $this->em->beginTransaction();
    }

    protected function tearDown(): void
    {
        $this->em->rollback();
        parent::tearDown();
    }

    #[Test]
    public function findsUsersByRole(): void
    {
        $admin = new User(name: 'Admin', email: 'admin@t.com', role: 'admin');
        $editor = new User(name: 'Editor', email: 'ed@t.com', role: 'editor');
        $this->em->persist($admin);
        $this->em->persist($editor);
        $this->em->flush();

        $admins = $this->repository->findByRole('admin');
        $this->assertCount(1, $admins);
        $this->assertSame('Admin', $admins[0]->getName());
    }

    #[Test]
    public function searchesByNameCaseInsensitive(): void
    {
        $this->em->persist(new User(name: 'Alice Smith', email: 'a@t.com'));
        $this->em->persist(new User(name: 'Bob Jones', email: 'b@t.com'));
        $this->em->flush();

        $results = $this->repository->search('alice');
        $this->assertCount(1, $results);
        $this->assertSame('Alice Smith', $results[0]->getName());
    }
}
```

---

## §9 CI/CD Integration

### GitHub Actions
```yaml
name: PHPUnit Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        php-version: ['8.2', '8.3']

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: secret
          MYSQL_DATABASE: testing
        ports: ['3306:3306']
        options: --health-cmd="mysqladmin ping" --health-interval=10s

      redis:
        image: redis:7-alpine
        ports: ['6379:6379']

    steps:
      - uses: actions/checkout@v4

      - uses: shivammathur/setup-php@v2
        with:
          php-version: ${{ matrix.php-version }}
          extensions: mbstring, pdo_mysql, redis
          coverage: xdebug
          tools: composer:v2

      - name: Install Dependencies
        run: composer install --prefer-dist --no-progress

      - name: Run Tests
        run: |
          XDEBUG_MODE=coverage vendor/bin/phpunit \
            --coverage-clover coverage/clover.xml \
            --log-junit reports/junit.xml
        env:
          DB_HOST: 127.0.0.1
          DB_PORT: 3306
          DB_DATABASE: testing
          DB_USERNAME: root
          DB_PASSWORD: secret
          REDIS_HOST: 127.0.0.1

      - name: Check Coverage Threshold
        run: |
          php -r "
            \$xml = simplexml_load_file('coverage/clover.xml');
            \$metrics = \$xml->project->metrics;
            \$covered = (int)\$metrics['coveredstatements'];
            \$total = (int)\$metrics['statements'];
            \$pct = \$total > 0 ? round(\$covered / \$total * 100, 2) : 0;
            echo \"Coverage: {\$pct}%\n\";
            if (\$pct < 80) { echo \"FAIL: Below 80% threshold\n\"; exit(1); }
            echo \"PASS: Above threshold\n\";
          "

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-php${{ matrix.php-version }}
          path: |
            coverage/
            reports/
```

---

## §10 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Tests not discovered | Wrong namespace or file naming | Class must end in `Test.php`; must extend `TestCase`; check `phpunit.xml` directories |
| 2 | `setUp()` not running | Method signature wrong | Must be `protected function setUp(): void` (camelCase, void return) |
| 3 | Mock method not called | `expects()` not verified | Use `$this->once()` or `$this->exactly(N)` — `$this->any()` doesn't verify |
| 4 | `@dataProvider` not found | Method not static | Data providers must be `public static function` in PHPUnit 11+ |
| 5 | Coverage shows 0% | Xdebug not loaded | Set `XDEBUG_MODE=coverage` env var; verify `php -m | grep xdebug` |
| 6 | Test passes when it shouldn't | Missing assertion | Use `failOnRisky="true"` in phpunit.xml; tests without assertions are risky |
| 7 | Tests interfere with each other | Shared state in `static` properties | Reset static state in `tearDown()`; use `--process-isolation` if needed |
| 8 | `createMock()` type error | Intersection types in PHP 8.1+ | Use `UserRepo&MockObject` type hint: `$this->createMock(UserRepo::class)` |
| 9 | Database tests slow | No transaction rollback | Wrap tests in transactions; use `setUp` beginTransaction / `tearDown` rollback |
| 10 | Mockery expectations not checked | Missing trait | Add `use MockeryPHPUnitIntegration;` trait to test class |
| 11 | `expectException` doesn't catch | Exception thrown before `expectException` call | Call `expectException()` BEFORE the code that throws |
| 12 | Parallel tests fail | Shared database or files | Use `--process-isolation` or separate DB per process with `paratest` |

---

## §11 Best Practices Checklist

1. Use `assertSame()` over `assertEquals()` — strict type comparison catches bugs
2. Use `#[DataProvider]` attribute — replace repeated test methods with parameterized data
3. Use `#[CoversClass]` — ensure coverage is accurately attributed to tested classes
4. Use `setUp()` for shared dependencies — avoid duplicating mock setup across tests
5. Use in-memory fakes for integration tests — faster than mocking every method
6. Use Faker for realistic test data — avoid brittle hard-coded values
7. Use `expectException()` BEFORE throwing code — order matters for exception assertions
8. Use transaction rollback for DB tests — `beginTransaction`/`rollback` keeps tests isolated
9. Use `failOnRisky="true"` — catch tests without assertions that silently pass
10. Use separate test suites — Unit/Feature/Integration with different run configurations
11. Run coverage in CI with thresholds — fail builds below 80% coverage
12. Use `--order-by=defects` — run previously failed tests first for faster feedback
13. Avoid testing private methods — test through public API; refactor if needed
14. Use `Mockery::spy()` for verification-only — when you don't need to stub return values
