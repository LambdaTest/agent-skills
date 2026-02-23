# PHPUnit — Advanced Patterns & Playbook

## Data Providers & Mocking

```php
class UserServiceTest extends TestCase
{
    #[DataProvider('userDataProvider')]
    public function testCreateUser(string $name, string $email, bool $valid): void
    {
        if (!$valid) {
            $this->expectException(ValidationException::class);
        }
        $user = $this->service->create($name, $email);
        $this->assertEquals($name, $user->getName());
    }

    public static function userDataProvider(): array
    {
        return [
            'valid user' => ['Alice', 'alice@test.com', true],
            'empty name' => ['', 'test@test.com', false],
            'invalid email' => ['Bob', 'invalid', false],
        ];
    }

    // Mock with Prophecy
    public function testSendsNotification(): void
    {
        $repo = $this->createMock(UserRepository::class);
        $repo->expects($this->once())
            ->method('save')
            ->with($this->callback(fn(User $u) => $u->getName() === 'Alice'))
            ->willReturn(new User(1, 'Alice'));

        $mailer = $this->createMock(MailerInterface::class);
        $mailer->expects($this->once())
            ->method('send')
            ->with($this->stringContains('Welcome'));

        $service = new UserService($repo, $mailer);
        $service->register('Alice', 'alice@test.com');
    }

    // Consecutive returns
    public function testRetries(): void
    {
        $client = $this->createMock(HttpClient::class);
        $client->method('get')
            ->willReturnOnConsecutiveCalls(
                $this->throwException(new TimeoutException()),
                new Response(200, '{"ok":true}')
            );
        $result = (new ApiClient($client))->fetchWithRetry('/data');
        $this->assertTrue($result['ok']);
    }
}
```

## Database Testing

```php
class DatabaseTest extends TestCase
{
    use DatabaseTransactions;   // Laravel: auto-rollback
    // use RefreshDatabase;     // Laravel: full migration

    protected function setUp(): void
    {
        parent::setUp();
        $this->seed(UserSeeder::class);
    }

    public function testCreatesRecord(): void
    {
        $user = User::factory()->create(['name' => 'Alice']);
        $this->assertDatabaseHas('users', ['name' => 'Alice']);
        $user->delete();
        $this->assertDatabaseMissing('users', ['id' => $user->id]);
    }
}
```

## Custom Assertions

```php
trait ApiAssertions
{
    public function assertJsonStructure(array $structure, array $data): void
    {
        foreach ($structure as $key => $value) {
            if (is_array($value)) {
                $this->assertArrayHasKey(is_string($key) ? $key : $value, $data);
            } else {
                $this->assertArrayHasKey($value, $data);
            }
        }
    }

    public function assertApiSuccess($response): void
    {
        $this->assertEquals(200, $response->getStatusCode());
        $body = json_decode($response->getBody(), true);
        $this->assertTrue($body['success'] ?? false);
    }
}
```

## Configuration

```xml
<!-- phpunit.xml -->
<phpunit bootstrap="vendor/autoload.php" colors="true"
    stopOnFailure="false" cacheResult="true">
    <testsuites>
        <testsuite name="Unit"><directory>tests/Unit</directory></testsuite>
        <testsuite name="Integration"><directory>tests/Integration</directory></testsuite>
    </testsuites>
    <coverage>
        <include><directory suffix=".php">src</directory></include>
        <report><html outputDirectory="coverage"/><text outputFile="coverage.txt"/></report>
    </coverage>
    <php>
        <env name="APP_ENV" value="testing"/>
        <env name="DB_DATABASE" value="test_db"/>
    </php>
</phpunit>
```

## Anti-Patterns

- ❌ `$this->assertTrue($a === $b)` → use `$this->assertSame($a, $b)`
- ❌ `@depends` chains longer than 2 — fragile, hard to debug
- ❌ Mocking concrete classes — mock interfaces instead
- ❌ `echo` for debugging — use `$this->addWarning()` or assertions
