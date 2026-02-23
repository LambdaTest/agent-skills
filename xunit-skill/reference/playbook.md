# xUnit — Advanced Implementation Playbook

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
    <PackageReference Include="xunit" Version="2.7.0" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.7" />
    <PackageReference Include="FluentAssertions" Version="6.12.0" />
    <PackageReference Include="Moq" Version="4.20.70" />
    <PackageReference Include="NSubstitute" Version="5.1.0" />
    <PackageReference Include="Bogus" Version="35.4.0" />
    <PackageReference Include="coverlet.collector" Version="6.0.0" />
    <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.0" />
    <PackageReference Include="Testcontainers" Version="3.7.0" />
    <PackageReference Include="Testcontainers.PostgreSql" Version="3.7.0" />
  </ItemGroup>
</Project>
```

### xunit.runner.json
```json
{
  "$schema": "https://xunit.net/schema/current/xunit.runner.schema.json",
  "parallelizeAssembly": true,
  "parallelizeTestCollections": true,
  "maxParallelThreads": 0,
  "diagnosticMessages": true,
  "longRunningTestSeconds": 30
}
```

---

## §2 Test Patterns — Fact & Theory

### Constructor Setup / IDisposable Teardown
```csharp
public class UserServiceTests : IDisposable
{
    private readonly Mock<IUserRepository> _mockRepo;
    private readonly Mock<IEmailService> _mockEmail;
    private readonly UserService _service;

    public UserServiceTests()
    {
        _mockRepo = new Mock<IUserRepository>();
        _mockEmail = new Mock<IEmailService>();
        _service = new UserService(_mockRepo.Object, _mockEmail.Object);
    }

    public void Dispose()
    {
        // cleanup if needed
    }

    [Fact]
    public void CreateUser_ValidData_ReturnsUserAndSendsWelcomeEmail()
    {
        // Arrange
        _mockRepo.Setup(r => r.Save(It.IsAny<User>()))
            .Returns(new User { Id = 1, Name = "Alice", Email = "alice@test.com" });

        // Act
        var user = _service.Create("Alice", "alice@test.com");

        // Assert
        user.Should().NotBeNull();
        user.Name.Should().Be("Alice");
        _mockEmail.Verify(e => e.SendWelcome(It.Is<string>(s => s == "alice@test.com")),
            Times.Once);
    }

    [Fact]
    public void CreateUser_DuplicateEmail_ThrowsConflictException()
    {
        _mockRepo.Setup(r => r.FindByEmail("alice@test.com"))
            .Returns(new User { Id = 1 });

        var act = () => _service.Create("Alice", "alice@test.com");

        act.Should().Throw<ConflictException>()
            .WithMessage("*already exists*");
    }
}
```

### Theory with InlineData / MemberData / ClassData
```csharp
public class EmailValidatorTests
{
    [Theory]
    [InlineData("user@test.com", true)]
    [InlineData("user@sub.domain.com", true)]
    [InlineData("invalid", false)]
    [InlineData("", false)]
    [InlineData("@missing.com", false)]
    public void IsValid_ReturnsExpected(string email, bool expected)
    {
        EmailValidator.IsValid(email).Should().Be(expected);
    }

    [Theory]
    [MemberData(nameof(GetUserTestData))]
    public void CreateUser_Parameterized(string name, string email, bool shouldSucceed)
    {
        if (shouldSucceed)
            _service.Create(name, email).Should().NotBeNull();
        else
            FluentActions.Invoking(() => _service.Create(name, email))
                .Should().Throw<ValidationException>();
    }

    public static IEnumerable<object[]> GetUserTestData()
    {
        yield return new object[] { "Alice", "alice@test.com", true };
        yield return new object[] { "", "bad", false };
        yield return new object[] { "Bob", "", false };
    }

    // ClassData for reusable data across test classes
    [Theory]
    [ClassData(typeof(PasswordStrengthData))]
    public void PasswordStrength_ReturnsCorrectLevel(string password, PasswordLevel expected)
    {
        PasswordChecker.GetLevel(password).Should().Be(expected);
    }
}

public class PasswordStrengthData : IEnumerable<object[]>
{
    public IEnumerator<object[]> GetEnumerator()
    {
        yield return new object[] { "weak", PasswordLevel.Weak };
        yield return new object[] { "Str0ng!Pass", PasswordLevel.Strong };
    }
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}
```

---

## §3 Shared Context — IClassFixture & ICollectionFixture

### IClassFixture (shared within one test class)
```csharp
public class DatabaseFixture : IAsyncLifetime
{
    public string ConnectionString { get; private set; } = "";

    public async Task InitializeAsync()
    {
        var container = new PostgreSqlBuilder()
            .WithImage("postgres:16")
            .Build();
        await container.StartAsync();
        ConnectionString = container.GetConnectionString();
        await ApplyMigrations(ConnectionString);
    }

    public async Task DisposeAsync()
    {
        // container auto-disposes
    }
}

public class UserRepositoryTests : IClassFixture<DatabaseFixture>
{
    private readonly DatabaseFixture _db;
    private readonly UserRepository _repo;

    public UserRepositoryTests(DatabaseFixture db)
    {
        _db = db;
        _repo = new UserRepository(db.ConnectionString);
    }

    [Fact]
    public async Task Save_PersistsUser()
    {
        var user = new User { Name = "Alice", Email = $"alice-{Guid.NewGuid()}@test.com" };
        var saved = await _repo.SaveAsync(user);
        saved.Id.Should().BeGreaterThan(0);
    }
}
```

### ICollectionFixture (shared across multiple test classes)
```csharp
[CollectionDefinition("Database")]
public class DatabaseCollection : ICollectionFixture<DatabaseFixture> { }

[Collection("Database")]
public class OrderRepositoryTests
{
    private readonly DatabaseFixture _db;
    public OrderRepositoryTests(DatabaseFixture db) { _db = db; }
}

[Collection("Database")]
public class ProductRepositoryTests
{
    private readonly DatabaseFixture _db;
    public ProductRepositoryTests(DatabaseFixture db) { _db = db; }
}
```

---

## §4 Async Testing & Custom Assertions

### Async Tests
```csharp
[Fact]
public async Task GetUserAsync_ReturnsUser()
{
    _mockRepo.Setup(r => r.FindByIdAsync(1))
        .ReturnsAsync(new User { Id = 1, Name = "Alice" });

    var user = await _service.GetUserAsync(1);

    user.Should().NotBeNull();
    user!.Name.Should().Be("Alice");
}

[Fact]
public async Task GetUserAsync_NotFound_ThrowsWithin5Seconds()
{
    _mockRepo.Setup(r => r.FindByIdAsync(99))
        .ReturnsAsync((User?)null);

    Func<Task> act = async () => await _service.GetUserAsync(99);

    await act.Should().ThrowAsync<NotFoundException>()
        .WithMessage("*not found*")
        .Where(e => e.StatusCode == 404);
}
```

### Assert.Multiple (Grouped Assertions)
```csharp
[Fact]
public void UserProfile_HasAllFields()
{
    var profile = _service.GetProfile(1);

    // All assertions run even if earlier ones fail
    using (new AssertionScope())
    {
        profile.Name.Should().NotBeNullOrEmpty();
        profile.Email.Should().Contain("@");
        profile.CreatedAt.Should().BeBefore(DateTime.UtcNow);
        profile.Role.Should().BeOneOf("admin", "user", "viewer");
    }
}
```

---

## §5 Test Data Generation with Bogus

```csharp
using Bogus;

public class UserTestDataFactory
{
    private static readonly Faker<CreateUserRequest> _faker = new Faker<CreateUserRequest>()
        .RuleFor(u => u.Name, f => f.Name.FullName())
        .RuleFor(u => u.Email, f => f.Internet.Email())
        .RuleFor(u => u.Age, f => f.Random.Int(18, 80))
        .RuleFor(u => u.Address, f => f.Address.FullAddress());

    public static CreateUserRequest Generate() => _faker.Generate();
    public static List<CreateUserRequest> GenerateMany(int count) => _faker.Generate(count);
}

[Fact]
public void CreateUser_RandomValidData_Succeeds()
{
    var request = UserTestDataFactory.Generate();
    _mockRepo.Setup(r => r.Save(It.IsAny<User>()))
        .Returns(new User { Id = 1, Name = request.Name });

    var user = _service.Create(request);

    user.Should().NotBeNull();
    user.Name.Should().Be(request.Name);
}
```

---

## §6 Integration Testing with WebApplicationFactory

```csharp
public class ApiIntegrationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public ApiIntegrationTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Replace real DB with in-memory
                services.RemoveAll<DbContext>();
                services.AddDbContext<AppDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb"));
            });
        }).CreateClient();
    }

    [Fact]
    public async Task GetUsers_ReturnsOkWithList()
    {
        var response = await _client.GetAsync("/api/users");

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var users = await response.Content.ReadFromJsonAsync<List<UserDto>>();
        users.Should().NotBeNull();
    }

    [Fact]
    public async Task CreateUser_ValidPayload_Returns201()
    {
        var payload = new { Name = "Alice", Email = "alice@test.com" };
        var response = await _client.PostAsJsonAsync("/api/users", payload);

        response.StatusCode.Should().Be(HttpStatusCode.Created);
        response.Headers.Location.Should().NotBeNull();
    }

    [Fact]
    public async Task CreateUser_InvalidEmail_Returns400()
    {
        var payload = new { Name = "Alice", Email = "invalid" };
        var response = await _client.PostAsJsonAsync("/api/users", payload);

        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }
}
```

---

## §7 Logging & Output

```csharp
public class DiagnosticTests : ITestOutputHelper
{
    private readonly ITestOutputHelper _output;

    public DiagnosticTests(ITestOutputHelper output) { _output = output; }

    [Fact]
    public void LongRunningOperation_LogsProgress()
    {
        _output.WriteLine("Starting test at {0}", DateTime.UtcNow);

        var result = _service.ProcessBatch(1000);

        _output.WriteLine("Processed {0} items in {1}ms", result.Count, result.ElapsedMs);
        result.Count.Should().Be(1000);
    }
}
```

---

## §8 CI/CD Integration

### GitHub Actions
```yaml
name: .NET Tests
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

      - name: Run tests with coverage
        run: |
          dotnet test \
            --configuration Release \
            --logger "trx;LogFileName=results.trx" \
            --collect:"XPlat Code Coverage" \
            --results-directory TestResults

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: TestResults/

      - name: Coverage report
        uses: danielpalme/ReportGenerator-GitHub-Action@5
        with:
          reports: 'TestResults/**/coverage.cobertura.xml'
          targetdir: 'CoverageReport'

      - uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: CoverageReport/
```

---

## §9 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Tests not discovered | Missing `[Fact]`/`[Theory]` attribute | Ensure every test method has an attribute; check class is `public` |
| 2 | Constructor runs for every test | xUnit design — constructor = per-test setup | Use `IClassFixture<T>` for shared expensive setup |
| 3 | Parallel tests interfere | Shared static state or database | Use `[Collection("name")]` to serialize; use unique data per test |
| 4 | `MemberData` throws `InvalidCast` | Wrong types in `object[]` | Match exact types; use `TheoryData<T>` for type safety |
| 5 | `IAsyncLifetime` not called | Class doesn't implement interface | Implement both `InitializeAsync()` and `DisposeAsync()` |
| 6 | FluentAssertions scope not working | Missing `using` block | Use `using (new AssertionScope()) { ... }` |
| 7 | Mock `ReturnsAsync` not found | Missing `Moq` extension | Use `using Moq;` and ensure `ReturnsAsync()` is on `Setup()` |
| 8 | Test hangs indefinitely | Deadlock in async code | Use `ConfigureAwait(false)` in library code; avoid `.Result`/`.Wait()` |
| 9 | Coverage report empty | Missing `coverlet.collector` | Add `coverlet.collector` package; use `--collect:"XPlat Code Coverage"` |
| 10 | `WebApplicationFactory` startup fails | Missing `Program` class | Add `public partial class Program { }` to API project |

---

## §10 Best Practices Checklist

1. ✅ Use `[Fact]` for single tests, `[Theory]` + `[InlineData]` for parameterized
2. ✅ Constructor = per-test setup, `IDisposable` = teardown — no attributes needed
3. ✅ Use `IClassFixture<T>` for expensive shared setup (DB, containers)
4. ✅ Use `ICollectionFixture<T>` for sharing across test classes
5. ✅ Use FluentAssertions: `result.Should().Be(expected)` — readable & informative
6. ✅ Use Moq or NSubstitute for mocking — never mock concrete classes
7. ✅ Use `Bogus` for random but realistic test data generation
8. ✅ Use `AssertionScope` for grouped assertions (all run even if one fails)
9. ✅ Use `WebApplicationFactory` for ASP.NET Core integration tests
10. ✅ Use `Testcontainers` for real database integration tests
11. ✅ Use `ITestOutputHelper` for diagnostic logging in tests
12. ✅ Avoid test order dependencies — each test should be fully independent
13. ✅ Use `[Collection]` to control parallelism for tests with shared resources
14. ✅ Set `longRunningTestSeconds` in `xunit.runner.json` to detect slow tests
