---
name: xunit-skill
description: >
  Generates xUnit.net tests in C#. Covers Fact/Theory, constructor injection,
  IClassFixture, and FluentAssertions. Use when user mentions "xUnit",
  "[Fact]", "[Theory]", "Assert.Equal", "C# xUnit". Triggers on: "xUnit",
  "[Fact]", "[Theory]", "Assert.Equal C#", "xUnit.net".
languages:
  - C#
category: unit-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# xUnit.net Testing Skill

## Core Patterns

### Basic Test

```csharp
using Xunit;

public class CalculatorTests
{
    private readonly Calculator _calc = new();

    [Fact]
    public void Add_TwoPositiveNumbers_ReturnsSum()
    {
        Assert.Equal(5, _calc.Add(2, 3));
    }

    [Fact]
    public void Divide_ByZero_ThrowsException()
    {
        Assert.Throws<DivideByZeroException>(() => _calc.Divide(10, 0));
    }
}
```

### Theory (Parameterized)

```csharp
[Theory]
[InlineData(2, 3, 5)]
[InlineData(-1, 1, 0)]
[InlineData(0, 0, 0)]
public void Add_ReturnsCorrectSum(int a, int b, int expected)
{
    Assert.Equal(expected, _calc.Add(a, b));
}

[Theory]
[MemberData(nameof(GetTestData))]
public void Add_WithMemberData(int a, int b, int expected)
{
    Assert.Equal(expected, _calc.Add(a, b));
}

public static IEnumerable<object[]> GetTestData()
{
    yield return new object[] { 1, 2, 3 };
    yield return new object[] { -1, -1, -2 };
}

[Theory]
[ClassData(typeof(CalculatorTestData))]
public void Add_WithClassData(int a, int b, int expected)
{
    Assert.Equal(expected, _calc.Add(a, b));
}
```

### Assertions

```csharp
Assert.Equal(expected, actual);
Assert.NotEqual(unexpected, actual);
Assert.True(condition);
Assert.False(condition);
Assert.Null(obj);
Assert.NotNull(obj);
Assert.Contains("sub", str);
Assert.DoesNotContain("x", str);
Assert.Empty(collection);
Assert.Single(collection);
Assert.Collection(list,
    item => Assert.Equal("first", item),
    item => Assert.Equal("second", item));
Assert.IsType<MyClass>(obj);
var ex = Assert.Throws<ArgumentException>(() => Method());
Assert.Equal("message", ex.Message);
Assert.InRange(value, 1, 10);
```

### Shared Context (IClassFixture)

```csharp
public class DatabaseFixture : IDisposable
{
    public DbConnection Connection { get; }
    public DatabaseFixture() { Connection = new DbConnection("test"); }
    public void Dispose() { Connection.Close(); }
}

public class UserTests : IClassFixture<DatabaseFixture>
{
    private readonly DatabaseFixture _fixture;
    public UserTests(DatabaseFixture fixture) { _fixture = fixture; }

    [Fact]
    public void GetUser_ReturnsUser()
    {
        var user = _fixture.Connection.Query<User>("SELECT * FROM Users LIMIT 1");
        Assert.NotNull(user);
    }
}
```

### Constructor/Dispose (Per-Test Setup)

```csharp
public class MyTests : IDisposable
{
    private readonly MyService _service;
    public MyTests() { _service = new MyService(); }   // SetUp
    public void Dispose() { _service.Cleanup(); }       // TearDown

    [Fact]
    public void TestSomething() { Assert.True(_service.IsReady); }
}
```

### Anti-Patterns

| Bad | Good | Why |
|-----|------|-----|
| `[Fact]` with parameters | `[Theory]` + `[InlineData]` | xUnit convention |
| Static state | `IClassFixture` | Test isolation |
| No `IDisposable` | Implement for cleanup | Resource management |

## Setup: `dotnet add package xunit xunit.runner.visualstudio Microsoft.NET.Test.Sdk`
## Run: `dotnet test` or `dotnet test --filter "FullyQualifiedName~Calculator"`

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
