# MSTest — Advanced Playbook

## §1 Project Setup & Configuration

### .csproj Dependencies
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.9.0" />
    <PackageReference Include="MSTest.TestAdapter" Version="3.2.0" />
    <PackageReference Include="MSTest.TestFramework" Version="3.2.0" />
    <PackageReference Include="FluentAssertions" Version="6.12.0" />
    <PackageReference Include="Moq" Version="4.20.70" />
    <PackageReference Include="NSubstitute" Version="5.1.0" />
    <PackageReference Include="Bogus" Version="35.4.0" />
    <PackageReference Include="Testcontainers" Version="3.7.0" />
    <PackageReference Include="Testcontainers.PostgreSql" Version="3.7.0" />
    <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.0" />
    <PackageReference Include="coverlet.collector" Version="6.0.1" />
  </ItemGroup>
</Project>
```

### .runsettings
```xml
<?xml version="1.0" encoding="utf-8"?>
<RunSettings>
  <MSTest>
    <Parallelize>
      <Workers>4</Workers>
      <Scope>ClassLevel</Scope>
    </Parallelize>
    <MapInconclusiveToFailed>true</MapInconclusiveToFailed>
    <TreatDiscoveryWarningsAsErrors>true</TreatDiscoveryWarningsAsErrors>
  </MSTest>
  <DataCollectionRunSettings>
    <DataCollectors>
      <DataCollector friendlyName="XPlat code coverage">
        <Configuration>
          <Format>cobertura</Format>
          <Exclude>[*]*.Migrations.*</Exclude>
          <ExcludeByAttribute>Obsolete,GeneratedCodeAttribute</ExcludeByAttribute>
          <SingleHit>false</SingleHit>
          <IncludeTestAssembly>false</IncludeTestAssembly>
        </Configuration>
      </DataCollector>
    </DataCollectors>
  </DataCollectionRunSettings>
</RunSettings>
```

---

## §2 Test Patterns — TestMethod & DataTestMethod

### Basic Test Structure
```csharp
[TestClass]
public class OrderServiceTests
{
    private Mock<IOrderRepository> _mockRepo = null!;
    private Mock<IPaymentGateway> _mockPayment = null!;
    private Mock<IEmailService> _mockEmail = null!;
    private OrderService _service = null!;

    [TestInitialize]
    public void Setup()
    {
        _mockRepo = new Mock<IOrderRepository>();
        _mockPayment = new Mock<IPaymentGateway>();
        _mockEmail = new Mock<IEmailService>();
        _service = new OrderService(
            _mockRepo.Object,
            _mockPayment.Object,
            _mockEmail.Object
        );
    }

    [TestCleanup]
    public void Cleanup()
    {
        // Verify no unexpected calls
        _mockRepo.VerifyNoOtherCalls();
    }

    [TestMethod]
    public async Task PlaceOrder_ValidOrder_ReturnsOrderId()
    {
        // Arrange
        var items = new List<OrderItem>
        {
            new("SKU-001", 2, 29.99m),
            new("SKU-002", 1, 49.99m)
        };
        _mockPayment.Setup(p => p.ChargeAsync(It.IsAny<decimal>(), It.IsAny<string>()))
            .ReturnsAsync(new PaymentResult { Success = true, TransactionId = "TXN-123" });
        _mockRepo.Setup(r => r.SaveAsync(It.IsAny<Order>()))
            .ReturnsAsync(new Order { Id = 42 });

        // Act
        var result = await _service.PlaceOrderAsync(items, "card_abc");

        // Assert
        Assert.IsNotNull(result);
        Assert.AreEqual(42, result.Id);
        Assert.AreEqual("TXN-123", result.TransactionId);
        _mockPayment.Verify(p => p.ChargeAsync(109.97m, "card_abc"), Times.Once);
        _mockEmail.Verify(e => e.SendOrderConfirmationAsync(42), Times.Once);
    }

    [TestMethod]
    [ExpectedException(typeof(InsufficientStockException))]
    public async Task PlaceOrder_OutOfStock_ThrowsException()
    {
        _mockRepo.Setup(r => r.CheckStockAsync("SKU-001"))
            .ReturnsAsync(0);

        var items = new List<OrderItem> { new("SKU-001", 5, 10m) };
        await _service.PlaceOrderAsync(items, "card_abc");
    }

    [TestMethod]
    public async Task PlaceOrder_PaymentFails_DoesNotSaveOrder()
    {
        _mockPayment.Setup(p => p.ChargeAsync(It.IsAny<decimal>(), It.IsAny<string>()))
            .ReturnsAsync(new PaymentResult { Success = false, Error = "Declined" });

        var items = new List<OrderItem> { new("SKU-001", 1, 10m) };

        await Assert.ThrowsExceptionAsync<PaymentFailedException>(
            () => _service.PlaceOrderAsync(items, "card_abc"));

        _mockRepo.Verify(r => r.SaveAsync(It.IsAny<Order>()), Times.Never);
    }
}
```

### DataTestMethod with DataRow
```csharp
[TestClass]
public class PricingCalculatorTests
{
    private readonly PricingCalculator _calculator = new();

    [DataTestMethod]
    [DataRow(100.0, 0.0, 100.0, DisplayName = "No discount")]
    [DataRow(100.0, 10.0, 90.0, DisplayName = "10% discount")]
    [DataRow(100.0, 100.0, 0.0, DisplayName = "100% discount")]
    [DataRow(0.0, 50.0, 0.0, DisplayName = "Zero price")]
    public void CalculateDiscount_ReturnsCorrectPrice(
        double price, double discountPercent, double expected)
    {
        var result = _calculator.ApplyDiscount((decimal)price, (decimal)discountPercent);
        Assert.AreEqual((decimal)expected, result);
    }

    [DataTestMethod]
    [DataRow(-1.0, DisplayName = "Negative price")]
    [DataRow(double.NaN, DisplayName = "NaN price")]
    public void CalculateDiscount_InvalidPrice_Throws(double price)
    {
        Assert.ThrowsException<ArgumentException>(
            () => _calculator.ApplyDiscount((decimal)price, 10m));
    }
}
```

### DynamicData for Complex Test Data
```csharp
[TestClass]
public class ValidationTests
{
    public static IEnumerable<object[]> InvalidUserData =>
        new List<object[]>
        {
            new object[] { "", "alice@test.com", "Name is required" },
            new object[] { "Alice", "", "Email is required" },
            new object[] { "Alice", "not-an-email", "Invalid email format" },
            new object[] { new string('A', 256), "a@b.com", "Name exceeds max length" },
        };

    [DataTestMethod]
    [DynamicData(nameof(InvalidUserData))]
    public void Validate_InvalidInput_ReturnsError(
        string name, string email, string expectedError)
    {
        var validator = new UserValidator();
        var result = validator.Validate(new UserDto { Name = name, Email = email });

        Assert.IsFalse(result.IsValid);
        CollectionAssert.Contains(result.Errors.Select(e => e.Message).ToList(), expectedError);
    }
}
```

---

## §3 FluentAssertions Integration

```csharp
using FluentAssertions;
using FluentAssertions.Execution;

[TestClass]
public class UserServiceFluentTests
{
    [TestMethod]
    public async Task GetUser_ReturnsFullProfile()
    {
        var user = await _service.GetByIdAsync(1);

        user.Should().NotBeNull();
        user!.Name.Should().Be("Alice");
        user.Email.Should().EndWith("@example.com");
        user.CreatedAt.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromSeconds(5));
        user.Roles.Should().Contain("admin").And.HaveCount(2);
    }

    [TestMethod]
    public void GetUsers_ReturnsSortedByName()
    {
        var users = _service.GetAll();

        users.Should().BeInAscendingOrder(u => u.Name);
        users.Should().OnlyContain(u => u.IsActive);
        users.Should().HaveCountGreaterThanOrEqualTo(1);
    }

    [TestMethod]
    public async Task CreateUser_ShouldThrowWithDetails()
    {
        var act = () => _service.CreateAsync(new UserDto { Name = "" });

        await act.Should().ThrowAsync<ValidationException>()
            .WithMessage("*Name*required*")
            .Where(e => e.Errors.Count > 0);
    }

    [TestMethod]
    public void AssertMultipleProperties()
    {
        var order = _service.GetOrder(1);

        using (new AssertionScope())
        {
            order.Status.Should().Be("Completed");
            order.Total.Should().BeGreaterThan(0);
            order.Items.Should().NotBeEmpty();
            order.ShippedAt.Should().NotBeNull();
        }
    }
}
```

---

## §4 Assembly & Class Initialize

### Shared Expensive Setup
```csharp
[TestClass]
public class DatabaseIntegrationTests
{
    private static PostgreSqlContainer _postgres = null!;
    private static string _connectionString = null!;

    [ClassInitialize]
    public static async Task ClassSetup(TestContext context)
    {
        _postgres = new PostgreSqlBuilder()
            .WithImage("postgres:16-alpine")
            .WithDatabase("testdb")
            .Build();
        await _postgres.StartAsync();
        _connectionString = _postgres.GetConnectionString();

        // Run migrations
        using var conn = new NpgsqlConnection(_connectionString);
        await conn.OpenAsync();
        var evolve = new Evolve.Evolve(conn, msg => context.WriteLine(msg))
        {
            Locations = new[] { "db/migrations" },
        };
        evolve.Migrate();
    }

    [ClassCleanup]
    public static async Task ClassCleanup()
    {
        await _postgres.DisposeAsync();
    }

    [TestInitialize]
    public async Task TestSetup()
    {
        // Clean tables between tests
        using var conn = new NpgsqlConnection(_connectionString);
        await conn.OpenAsync();
        await conn.ExecuteAsync("TRUNCATE users, orders CASCADE");
    }

    [TestMethod]
    public async Task SaveAndRetrieveUser()
    {
        var repo = new UserRepository(_connectionString);
        var user = new User { Name = "Alice", Email = "alice@test.com" };

        var saved = await repo.SaveAsync(user);
        var retrieved = await repo.GetByIdAsync(saved.Id);

        Assert.IsNotNull(retrieved);
        Assert.AreEqual("Alice", retrieved.Name);
    }
}
```

### AssemblyInitialize for Global Setup
```csharp
[TestClass]
public class GlobalSetup
{
    [AssemblyInitialize]
    public static void AssemblyInit(TestContext context)
    {
        Environment.SetEnvironmentVariable("ASPNETCORE_ENVIRONMENT", "Test");
        // Global one-time setup
    }

    [AssemblyCleanup]
    public static void AssemblyCleanup()
    {
        // Global teardown
    }
}
```

---

## §5 Integration Testing with WebApplicationFactory

```csharp
[TestClass]
public class UsersApiTests
{
    private static WebApplicationFactory<Program> _factory = null!;
    private static HttpClient _client = null!;

    [ClassInitialize]
    public static void ClassSetup(TestContext context)
    {
        _factory = new WebApplicationFactory<Program>()
            .WithWebHostBuilder(builder =>
            {
                builder.ConfigureServices(services =>
                {
                    // Replace real DB with in-memory
                    var descriptor = services.SingleOrDefault(
                        d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));
                    if (descriptor != null) services.Remove(descriptor);

                    services.AddDbContext<AppDbContext>(options =>
                        options.UseInMemoryDatabase("TestDb"));

                    // Seed test data
                    var sp = services.BuildServiceProvider();
                    using var scope = sp.CreateScope();
                    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
                    db.Database.EnsureCreated();
                    db.Users.Add(new User { Id = 1, Name = "Alice", Email = "alice@test.com" });
                    db.SaveChanges();
                });
            });

        _client = _factory.CreateClient();
        _client.DefaultRequestHeaders.Add("X-Api-Key", "test-key");
    }

    [ClassCleanup]
    public static void ClassCleanup()
    {
        _client.Dispose();
        _factory.Dispose();
    }

    [TestMethod]
    public async Task GetUsers_ReturnsOk()
    {
        var response = await _client.GetAsync("/api/users");

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var users = await response.Content.ReadFromJsonAsync<List<UserDto>>();
        users.Should().NotBeEmpty();
    }

    [TestMethod]
    public async Task CreateUser_ReturnsCreated()
    {
        var payload = new { Name = "Bob", Email = "bob@test.com" };
        var response = await _client.PostAsJsonAsync("/api/users", payload);

        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var user = await response.Content.ReadFromJsonAsync<UserDto>();
        user!.Name.Should().Be("Bob");
        response.Headers.Location.Should().NotBeNull();
    }

    [TestMethod]
    public async Task CreateUser_InvalidData_ReturnsBadRequest()
    {
        var payload = new { Name = "", Email = "not-email" };
        var response = await _client.PostAsJsonAsync("/api/users", payload);

        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
        var problem = await response.Content.ReadFromJsonAsync<ValidationProblemDetails>();
        problem!.Errors.Should().ContainKey("Name");
    }
}
```

---

## §6 Test Data Generation with Bogus

```csharp
using Bogus;

[TestClass]
public class BogusDataTests
{
    private static readonly Faker<UserDto> UserFaker = new Faker<UserDto>()
        .RuleFor(u => u.Name, f => f.Person.FullName)
        .RuleFor(u => u.Email, f => f.Internet.Email())
        .RuleFor(u => u.Phone, f => f.Phone.PhoneNumber())
        .RuleFor(u => u.Address, f => f.Address.FullAddress())
        .RuleFor(u => u.CreatedAt, f => f.Date.Past(1));

    private static readonly Faker<OrderDto> OrderFaker = new Faker<OrderDto>()
        .RuleFor(o => o.Items, f => f.Make(f.Random.Int(1, 5), () => new OrderItem
        {
            Sku = f.Commerce.Ean13(),
            Quantity = f.Random.Int(1, 10),
            Price = decimal.Parse(f.Commerce.Price()),
        }))
        .RuleFor(o => o.Status, f => f.PickRandom("Pending", "Shipped", "Delivered"));

    [TestMethod]
    public async Task BulkCreate_HandlesLargeDataSets()
    {
        var users = UserFaker.Generate(100);

        var result = await _service.BulkCreateAsync(users);

        result.SuccessCount.Should().Be(100);
        result.Errors.Should().BeEmpty();
    }

    [TestMethod]
    public void OrderTotal_CalculatesCorrectly()
    {
        // Seeded for reproducibility
        var order = OrderFaker.UseSeed(12345).Generate();

        var total = _calculator.CalculateTotal(order);

        total.Should().Be(order.Items.Sum(i => i.Price * i.Quantity));
    }
}
```

---

## §7 TestContext & Logging

```csharp
[TestClass]
public class DiagnosticTests
{
    public TestContext TestContext { get; set; } = null!;

    [TestMethod]
    public async Task LongRunningOperation_CompletesInTime()
    {
        var sw = Stopwatch.StartNew();

        var result = await _service.ProcessBatchAsync(1000);

        sw.Stop();
        TestContext.WriteLine($"Batch processing took {sw.ElapsedMilliseconds}ms");
        TestContext.WriteLine($"Processed {result.Count} items");

        result.Count.Should().Be(1000);
        sw.Elapsed.Should().BeLessThan(TimeSpan.FromSeconds(5));
    }

    [TestMethod]
    [TestCategory("Integration")]
    [TestProperty("Priority", "High")]
    [Timeout(30000)]
    public async Task ExternalApi_RespondsWithinSla()
    {
        TestContext.WriteLine($"Test running at {DateTime.UtcNow}");
        var response = await _client.GetAsync("/api/health");
        TestContext.WriteLine($"Response status: {response.StatusCode}");
        response.IsSuccessStatusCode.Should().BeTrue();
    }
}
```

---

## §8 CI/CD Integration

### GitHub Actions
```yaml
name: .NET Tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: 8.0.x

      - run: dotnet restore

      - run: dotnet build --no-restore

      - name: Run Tests
        run: |
          dotnet test --no-build \
            --settings .runsettings \
            --logger "trx;LogFileName=results.trx" \
            --collect:"XPlat Code Coverage" \
            --results-directory ./TestResults

      - name: Generate Coverage Report
        run: |
          dotnet tool install -g dotnet-reportgenerator-globaltool
          reportgenerator \
            -reports:"TestResults/**/coverage.cobertura.xml" \
            -targetdir:"coveragereport" \
            -reporttypes:"Html;TextSummary"

      - name: Check Coverage
        run: |
          COVERAGE=$(grep 'Line coverage' coveragereport/Summary.txt | grep -oP '[\d.]+')
          echo "Coverage: $COVERAGE%"
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage below threshold!" && exit 1
          fi

      - name: Publish Results
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: MSTest Results
          path: TestResults/*.trx
          reporter: dotnet-trx

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: |
            TestResults/
            coveragereport/
```

### Filtering Tests
```bash
# Run by category
dotnet test --filter "TestCategory=Integration"

# Run by name pattern
dotnet test --filter "FullyQualifiedName~UserService"

# Run by priority
dotnet test --filter "TestProperty.Priority=High"

# Exclude slow tests
dotnet test --filter "TestCategory!=Slow"
```

---

## §9 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Tests not discovered | Missing `[TestClass]` or `[TestMethod]` | Add both attributes; ensure project references MSTest.TestAdapter |
| 2 | `TestInitialize` runs every test | Expected behavior — per-test setup | Use `[ClassInitialize]` for one-time expensive setup |
| 3 | Parallel tests interfere | Shared static state | Use `[DoNotParallelize]` on conflicting classes or remove shared state |
| 4 | `DynamicData` not found | Property not `public static` | Ensure `IEnumerable<object[]>` property is `public static` |
| 5 | `ExpectedException` passes unexpectedly | Wrong exception type caught | Use `Assert.ThrowsExceptionAsync<T>` instead for precise control |
| 6 | `ClassInitialize` not called | Missing `TestContext` parameter | Signature must be `public static void/Task Method(TestContext context)` |
| 7 | FluentAssertions scope reports one | Not using `AssertionScope` | Wrap multiple assertions in `using (new AssertionScope())` |
| 8 | Async test hangs | Missing `await` or wrong return type | Return `Task` from async tests; use `await` on all async calls |
| 9 | Coverage reports 0% | coverlet not collecting | Add `--collect:"XPlat Code Coverage"` flag; check .runsettings |
| 10 | WebApplicationFactory startup fails | DI conflict with test services | Remove real DB descriptor before adding in-memory; check service order |
| 11 | `DataRow` doesn't accept complex types | DataRow only supports primitives | Use `[DynamicData]` with property/method for complex objects |
| 12 | `Timeout` attribute ignored | Applied to wrong scope | `[Timeout]` applies per-test; for class-wide use `.runsettings` |

---

## §10 Best Practices Checklist

1. Use `Assert.ThrowsExceptionAsync<T>` over `[ExpectedException]` — more precise, inspectable
2. Use `[DataTestMethod]` + `[DataRow]` for simple params, `[DynamicData]` for complex
3. Use `[TestInitialize]`/`[TestCleanup]` per test, `[ClassInitialize]`/`[ClassCleanup]` per class
4. Use FluentAssertions with `AssertionScope` — see all failures at once
5. Use Bogus for realistic test data — avoid brittle hard-coded values
6. Use `[TestCategory]` for CI filtering — separate unit from integration tests
7. Set `Parallelize` in `.runsettings` — scope to ClassLevel for safety
8. Use Testcontainers for real DB tests — match production behavior
9. Use WebApplicationFactory for API integration tests — test full pipeline
10. Use `TestContext.WriteLine` for diagnostics — visible in test output
11. Set coverage thresholds in CI — fail builds that drop below 80%
12. Use `[Timeout]` on slow tests — catch infinite loops early
13. Use `DisplayName` on DataRow — make test names descriptive
14. Keep test methods focused — one logical assertion group per test
