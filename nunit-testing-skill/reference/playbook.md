# NUnit — Advanced Implementation Playbook

## §1 Project Setup & Configuration

### .csproj — Test Dependencies
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.9.0" />
    <PackageReference Include="NUnit" Version="4.0.1" />
    <PackageReference Include="NUnit3TestAdapter" Version="4.5.0" />
    <PackageReference Include="NUnit.Analyzers" Version="4.0.1" />
    <PackageReference Include="FluentAssertions" Version="6.12.0" />
    <PackageReference Include="Moq" Version="4.20.70" />
    <PackageReference Include="NSubstitute" Version="5.1.0" />
    <PackageReference Include="Bogus" Version="35.4.0" />
    <PackageReference Include="coverlet.collector" Version="6.0.0" />
  </ItemGroup>
</Project>
```

### .runsettings
```xml
<?xml version="1.0" encoding="utf-8"?>
<RunSettings>
  <NUnit>
    <NumberOfTestWorkers>4</NumberOfTestWorkers>
    <DefaultTimeout>30000</DefaultTimeout>
    <StopOnError>false</StopOnError>
    <WorkDirectory>%temp%\nunit-work</WorkDirectory>
  </NUnit>
  <DataCollectionRunSettings>
    <DataCollectors>
      <DataCollector friendlyName="XPlat Code Coverage">
        <Configuration>
          <Format>cobertura</Format>
          <ExcludeByAttribute>GeneratedCodeAttribute,ObsoleteAttribute</ExcludeByAttribute>
        </Configuration>
      </DataCollector>
    </DataCollectors>
  </DataCollectionRunSettings>
</RunSettings>
```

---

## §2 Test Patterns — Test & TestCase

### SetUp / TearDown Lifecycle
```csharp
[TestFixture]
public class UserServiceTests
{
    private Mock<IUserRepository> _mockRepo;
    private Mock<IEmailService> _mockEmail;
    private UserService _service;

    [SetUp]
    public void Setup()
    {
        _mockRepo = new Mock<IUserRepository>();
        _mockEmail = new Mock<IEmailService>();
        _service = new UserService(_mockRepo.Object, _mockEmail.Object);
    }

    [TearDown]
    public void TearDown()
    {
        // cleanup if needed
    }

    [Test]
    public void CreateUser_ValidData_ReturnsUserAndSendsEmail()
    {
        _mockRepo.Setup(r => r.Save(It.IsAny<User>()))
            .Returns(new User { Id = 1, Name = "Alice", Email = "alice@test.com" });

        var user = _service.Create("Alice", "alice@test.com");

        Assert.That(user, Is.Not.Null);
        Assert.That(user.Name, Is.EqualTo("Alice"));
        _mockEmail.Verify(e => e.SendWelcome("alice@test.com"), Times.Once);
    }

    [Test]
    public void CreateUser_DuplicateEmail_ThrowsConflict()
    {
        _mockRepo.Setup(r => r.FindByEmail("alice@test.com"))
            .Returns(new User { Id = 1 });

        Assert.That(
            () => _service.Create("Alice", "alice@test.com"),
            Throws.TypeOf<ConflictException>()
                .With.Message.Contains("already exists"));
    }
}
```

### TestCase & TestCaseSource
```csharp
[TestFixture]
public class ValidationTests
{
    [TestCase("user@test.com", true)]
    [TestCase("user@sub.domain.com", true)]
    [TestCase("invalid", false)]
    [TestCase("", false)]
    [TestCase("@missing.com", false)]
    public void ValidateEmail(string email, bool expected)
    {
        Assert.That(EmailValidator.IsValid(email), Is.EqualTo(expected));
    }

    [TestCaseSource(nameof(PasswordStrengthCases))]
    public void PasswordStrength(string password, PasswordLevel expected)
    {
        Assert.That(PasswordChecker.GetLevel(password), Is.EqualTo(expected));
    }

    private static IEnumerable<TestCaseData> PasswordStrengthCases()
    {
        yield return new TestCaseData("weak", PasswordLevel.Weak).SetName("Weak password");
        yield return new TestCaseData("Str0ng!Pass", PasswordLevel.Strong).SetName("Strong password");
        yield return new TestCaseData("m3d1um", PasswordLevel.Medium).SetName("Medium password");
    }

    [TestCase(12, 3, ExpectedResult = 4)]
    [TestCase(20, 4, ExpectedResult = 5)]
    [TestCase(100, 10, ExpectedResult = 10)]
    public int Divide_ReturnsCorrectResult(int a, int b)
    {
        return Calculator.Divide(a, b);
    }

    [Test]
    public void Divide_ByZero_Throws()
    {
        Assert.That(() => Calculator.Divide(10, 0),
            Throws.TypeOf<DivideByZeroException>());
    }
}
```

---

## §3 Constraint Model (Assert.That)

```csharp
[TestFixture]
public class ConstraintExamples
{
    [Test]
    public void StringConstraints()
    {
        var name = "Alice Smith";
        Assert.That(name, Is.Not.Null.And.Not.Empty);
        Assert.That(name, Does.StartWith("Alice"));
        Assert.That(name, Does.Contain("Smith"));
        Assert.That(name, Does.Match("^[A-Z][a-z]+ [A-Z][a-z]+$"));
        Assert.That(name, Has.Length.EqualTo(11));
    }

    [Test]
    public void CollectionConstraints()
    {
        var items = new[] { 1, 2, 3, 4, 5 };
        Assert.That(items, Has.Exactly(5).Items);
        Assert.That(items, Is.Ordered);
        Assert.That(items, Does.Contain(3));
        Assert.That(items, Has.All.GreaterThan(0));
        Assert.That(items, Is.Unique);
        Assert.That(items, Has.Some.GreaterThan(4));
        Assert.That(items, Has.None.LessThan(0));
    }

    [Test]
    public void ObjectConstraints()
    {
        var user = new User { Id = 1, Name = "Alice", Active = true };
        Assert.That(user, Has.Property("Name").EqualTo("Alice"));
        Assert.That(user, Has.Property("Active").True);
        Assert.That(user, Is.InstanceOf<User>());
    }

    [Test]
    public void MultipleAssertions()
    {
        var user = _service.GetProfile(1);

        Assert.Multiple(() =>
        {
            Assert.That(user.Name, Is.Not.Null);
            Assert.That(user.Email, Does.Contain("@"));
            Assert.That(user.CreatedAt, Is.LessThan(DateTime.UtcNow));
            Assert.That(user.Role, Is.AnyOf("admin", "user", "viewer"));
        });
    }
}
```

---

## §4 OneTimeSetUp, Fixtures & Parallel Execution

### OneTimeSetUp (shared across tests in fixture)
```csharp
[TestFixture]
public class DatabaseTests
{
    private static TestDatabase _db;

    [OneTimeSetUp]
    public async Task GlobalSetup()
    {
        _db = await TestDatabase.Create();
        await _db.Migrate();
    }

    [OneTimeTearDown]
    public async Task GlobalTeardown()
    {
        await _db.DisposeAsync();
    }

    [SetUp]
    public async Task PerTestSetup()
    {
        await _db.BeginTransaction();
    }

    [TearDown]
    public async Task PerTestTeardown()
    {
        await _db.RollbackTransaction();
    }

    [Test]
    public async Task SaveUser_PersistsToDb()
    {
        var repo = new UserRepository(_db.ConnectionString);
        var user = await repo.SaveAsync(new User { Name = "Alice" });
        Assert.That(user.Id, Is.GreaterThan(0));
    }
}
```

### Parallel Execution
```csharp
// All tests in this fixture run in parallel
[TestFixture]
[Parallelizable(ParallelScope.All)]
public class IndependentTests
{
    [Test] public void Test1() { /* runs concurrently */ }
    [Test] public void Test2() { /* runs concurrently */ }
}

// Tests across fixtures run in parallel (default)
[TestFixture]
[Parallelizable(ParallelScope.Fixtures)]
public class FixtureA { }

// Disable parallelism for tests with shared state
[TestFixture]
[NonParallelizable]
public class SequentialDatabaseTests { }
```

### SetUpFixture (assembly-level setup)
```csharp
[SetUpFixture]
public class GlobalSetup
{
    [OneTimeSetUp]
    public void AssemblyInit()
    {
        // Runs once before all tests in the assembly
        TestEnvironment.Initialize();
    }

    [OneTimeTearDown]
    public void AssemblyCleanup()
    {
        TestEnvironment.Cleanup();
    }
}
```

---

## §5 Async Testing

```csharp
[TestFixture]
public class AsyncServiceTests
{
    [Test]
    public async Task GetUserAsync_ReturnsUser()
    {
        _mockRepo.Setup(r => r.FindByIdAsync(1))
            .ReturnsAsync(new User { Id = 1, Name = "Alice" });

        var user = await _service.GetUserAsync(1);

        Assert.That(user, Is.Not.Null);
        Assert.That(user!.Name, Is.EqualTo("Alice"));
    }

    [Test]
    public void GetUserAsync_NotFound_ThrowsAsync()
    {
        _mockRepo.Setup(r => r.FindByIdAsync(99))
            .ReturnsAsync((User?)null);

        Assert.That(
            async () => await _service.GetUserAsync(99),
            Throws.TypeOf<NotFoundException>()
                .With.Property("StatusCode").EqualTo(404));
    }

    [Test]
    public async Task ProcessBatchAsync_CompletesWithinTimeout()
    {
        var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
        var result = await _service.ProcessBatchAsync(100, cts.Token);
        Assert.That(result.ProcessedCount, Is.EqualTo(100));
    }

    [Test]
    [Timeout(5000)]
    public async Task SlowOperation_RespectsTimeout()
    {
        // NUnit will fail this test if it takes > 5 seconds
        var result = await _service.SlowOperation();
        Assert.That(result, Is.Not.Null);
    }
}
```

---

## §6 Test Data with Bogus

```csharp
using Bogus;

public static class TestDataFactory
{
    private static readonly Faker<CreateUserRequest> UserFaker = new Faker<CreateUserRequest>()
        .RuleFor(u => u.Name, f => f.Name.FullName())
        .RuleFor(u => u.Email, f => f.Internet.Email())
        .RuleFor(u => u.Age, f => f.Random.Int(18, 80));

    public static CreateUserRequest ValidUser() => UserFaker.Generate();
    public static List<CreateUserRequest> ValidUsers(int count) => UserFaker.Generate(count);
}

[Test]
public void CreateUser_WithRandomData_Succeeds()
{
    var request = TestDataFactory.ValidUser();
    _mockRepo.Setup(r => r.Save(It.IsAny<User>()))
        .Returns(new User { Id = 1, Name = request.Name });

    var result = _service.Create(request);
    Assert.That(result.Name, Is.EqualTo(request.Name));
}
```

---

## §7 Categories & Filtering

```csharp
[TestFixture]
[Category("Integration")]
public class IntegrationTests
{
    [Test]
    [Category("Database")]
    public void DbConnection_Works() { }

    [Test]
    [Category("API")]
    public void ApiEndpoint_Returns200() { }
}
```

```bash
# Run by category
dotnet test --filter "TestCategory=Integration"
dotnet test --filter "TestCategory!=Slow"
dotnet test --filter "TestCategory=API|TestCategory=Database"
```

---

## §8 CI/CD Integration

```yaml
name: NUnit CI
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '8.0.x' }

      - run: dotnet restore
      - name: Run tests
        run: |
          dotnet test \
            --configuration Release \
            --logger "trx;LogFileName=results.trx" \
            --logger "console;verbosity=detailed" \
            --collect:"XPlat Code Coverage" \
            --results-directory TestResults \
            --settings .runsettings

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: TestResults/

      - name: Publish Test Report
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: NUnit Results
          path: TestResults/*.trx
          reporter: dotnet-trx
```

---

## §9 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Tests not discovered | Missing `[Test]`/`[TestCase]` attribute | Ensure attribute present; class must be `public` and non-static |
| 2 | `SetUp` runs before every test | NUnit design — `[SetUp]` is per-test | Use `[OneTimeSetUp]` for fixture-level initialization |
| 3 | Parallel tests fail intermittently | Shared mutable state | Use `[NonParallelizable]` or isolate state per test |
| 4 | `TestCaseSource` not found | Method not `static` | Make data source method `static` and return `IEnumerable` |
| 5 | `Assert.Multiple` reports only first failure | Not using `Assert.Multiple()` | Wrap all assertions in `Assert.Multiple(() => { ... })` |
| 6 | Async test hangs | `.Result` or `.Wait()` causing deadlock | Use `async Task` return type; avoid blocking on async code |
| 7 | `ExpectedResult` doesn't match | Wrong return type | `[TestCase]` with `ExpectedResult` requires the test method to return a value |
| 8 | Mock `Verify` fails | Method not called | Check the code path; ensure mock setup matches actual call parameters |
| 9 | `Timeout` attribute ignored | Test not marked `[Test]` | `[Timeout]` only works on methods with `[Test]` or `[TestCase]` |
| 10 | Coverage shows 0% | Missing `coverlet.collector` | Add package; use `--collect:"XPlat Code Coverage"` |

---

## §10 Best Practices Checklist

1. ✅ Use `Assert.That()` with constraint model — readable and extensible
2. ✅ Use `[TestCase]` for inline data, `[TestCaseSource]` for complex parameterized tests
3. ✅ Use `[SetUp]`/`[TearDown]` per-test; `[OneTimeSetUp]`/`[OneTimeTearDown]` per-fixture
4. ✅ Use Moq or NSubstitute for mocking — never mock concrete classes
5. ✅ Use `[Parallelizable]` for independent tests; `[NonParallelizable]` for shared state
6. ✅ Use `Assert.Multiple()` for grouped assertions — all run even if one fails
7. ✅ Use `[Category]` for test organization and selective CI execution
8. ✅ Use Bogus for realistic random test data generation
9. ✅ Use `async Task` for async tests — never block with `.Result`
10. ✅ Use `.runsettings` for configuring workers, timeout, and coverage
11. ✅ Use `[SetUpFixture]` for assembly-level initialization (once for all tests)
12. ✅ Use FluentAssertions alongside NUnit constraints for readability
13. ✅ Set `DefaultTimeout` in `.runsettings` to catch hanging tests
