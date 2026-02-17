# xUnit.net — Advanced Patterns & Playbook

## Theory Data Sources

```csharp
// Inline data
[Theory]
[InlineData(1, 2, 3)]
[InlineData(-1, 1, 0)]
[InlineData(100, -50, 50)]
public void Add_ReturnsSum(int a, int b, int expected)
    => Assert.Equal(expected, Calculator.Add(a, b));

// Class data
public class ValidEmailData : TheoryData<string, bool>
{
    public ValidEmailData()
    {
        Add("user@test.com", true);
        Add("invalid", false);
        Add("", false);
    }
}

[Theory, ClassData(typeof(ValidEmailData))]
public void IsValidEmail(string email, bool expected)
    => Assert.Equal(expected, Validator.IsValid(email));

// Member data
[Theory, MemberData(nameof(GetTestUsers))]
public void UserCreation(string name, int age)
{
    var user = new User(name, age);
    Assert.Equal(name, user.Name);
}
public static IEnumerable<object[]> GetTestUsers()
{
    yield return new object[] { "Alice", 30 };
    yield return new object[] { "Bob", 25 };
}
```

## Fixtures & Shared Context

```csharp
// Class fixture — shared across tests in one class
public class DatabaseFixture : IAsyncLifetime
{
    public DbContext Db { get; private set; }
    public async Task InitializeAsync()
    {
        Db = new TestDbContext();
        await Db.Database.MigrateAsync();
        await Db.SeedAsync();
    }
    public async Task DisposeAsync() => await Db.DisposeAsync();
}

public class UserTests : IClassFixture<DatabaseFixture>
{
    private readonly DatabaseFixture _db;
    public UserTests(DatabaseFixture db) { _db = db; }

    [Fact]
    public async Task FindsUser() =>
        Assert.NotNull(await _db.Db.Users.FindAsync(1));
}

// Collection fixture — shared across multiple test classes
[CollectionDefinition("Database")]
public class DatabaseCollection : ICollectionFixture<DatabaseFixture> { }

[Collection("Database")]
public class OrderTests { /* uses same fixture */ }
```

## Custom Assertions

```csharp
public static class AssertEx
{
    public static async Task ThrowsWithMessageAsync<T>(
        Func<Task> action, string expectedMessage) where T : Exception
    {
        var ex = await Assert.ThrowsAsync<T>(action);
        Assert.Contains(expectedMessage, ex.Message);
    }

    public static void JsonEqual(string expected, string actual)
    {
        var e = JsonDocument.Parse(expected);
        var a = JsonDocument.Parse(actual);
        Assert.Equal(e.RootElement.ToString(), a.RootElement.ToString());
    }
}
```

## Output & Logging

```csharp
public class LoggingTests
{
    private readonly ITestOutputHelper _output;
    public LoggingTests(ITestOutputHelper output) { _output = output; }

    [Fact]
    public void LogsSteps()
    {
        _output.WriteLine("Step 1: Creating user...");
        var user = new User("Alice");
        _output.WriteLine($"Step 2: User created with id {user.Id}");
        Assert.NotNull(user);
    }
}
```

## Anti-Patterns

- ❌ Constructor logic without `IClassFixture` — xUnit creates new instance per test
- ❌ `IDisposable` instead of `IAsyncLifetime` for async cleanup
- ❌ `Assert.True(a == b)` — use `Assert.Equal(a, b)` for better error messages
- ❌ Static state between tests — xUnit parallelizes by default
