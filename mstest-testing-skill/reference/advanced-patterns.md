# MSTest — Advanced Patterns & Playbook

## Data-Driven Tests

```csharp
[TestClass]
public class CalculatorTests
{
    [DataTestMethod]
    [DataRow(1, 2, 3)]
    [DataRow(-1, -1, -2)]
    [DataRow(0, 0, 0)]
    public void Add(int a, int b, int expected)
        => Assert.AreEqual(expected, Calculator.Add(a, b));

    [TestMethod]
    [DynamicData(nameof(GetTestData), DynamicDataSourceType.Method)]
    public void Process(string input, string expected)
        => Assert.AreEqual(expected, Processor.Run(input));

    static IEnumerable<object[]> GetTestData()
    {
        yield return new object[] { "hello", "HELLO" };
        yield return new object[] { "world", "WORLD" };
    }

    // CSV data source
    [DataTestMethod]
    [CsvDataSource("TestData/users.csv")]
    public void ImportUsers(string name, string email) { /* ... */ }
}
```

## Test Lifecycle

```csharp
[TestClass]
public class IntegrationTests
{
    static HttpClient _client;

    [ClassInitialize]
    public static void ClassInit(TestContext context)
    {
        var factory = new WebApplicationFactory<Program>();
        _client = factory.CreateClient();
    }

    [ClassCleanup]
    public static void ClassCleanup() => _client?.Dispose();

    [TestInitialize]
    public void TestInit() { /* before each */ }

    [TestCleanup]
    public void TestClean() { /* after each */ }

    [TestMethod]
    public async Task GetUsers_ReturnsOk()
    {
        var response = await _client.GetAsync("/api/users");
        Assert.AreEqual(HttpStatusCode.OK, response.StatusCode);
    }
}
```

## MSTest v3 Source Generators

```csharp
// Auto-generated assertions with MSTest v3
[TestClass]
public partial class UserTests
{
    [TestMethod]
    public void UserCreation()
    {
        var user = new User("Alice", 30);
        Assert.AreEqual("Alice", user.Name);
        Assert.IsTrue(user.Age > 0);
        Assert.IsNotNull(user.Id);
        StringAssert.Contains(user.Email, "@");
        CollectionAssert.Contains(user.Roles, "default");
    }
}
```

## Anti-Patterns

- ❌ `[ClassInitialize]` without `static` — MSTest requires it
- ❌ `Assert.IsTrue(a.Equals(b))` — use `Assert.AreEqual(a, b)`
- ❌ Missing `[TestCategory]` — makes filtering in CI difficult
- ❌ `[ExpectedException]` attribute — use `Assert.ThrowsException<T>()` instead
