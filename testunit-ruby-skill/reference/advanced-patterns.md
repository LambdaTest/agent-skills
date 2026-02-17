# Test::Unit Ruby — Advanced Patterns & Playbook

## Custom Assertions & Fixtures

```ruby
require 'test/unit'

class UserServiceTest < Test::Unit::TestCase
  def setup
    @db = TestDatabase.new
    @service = UserService.new(@db)
  end

  def teardown
    @db.rollback
    @db.close
  end

  # Data-driven
  data("valid email" => ["alice@test.com", true],
       "invalid" => ["not-email", false],
       "empty" => ["", false])
  def test_email_validation(data)
    email, expected = data
    assert_equal expected, Validator.valid_email?(email)
  end

  def test_create_user
    user = @service.create(name: "Alice", email: "alice@test.com")
    assert_not_nil user.id
    assert_equal "Alice", user.name
    assert_match(/\A[\w.]+@[\w.]+\z/, user.email)
  end

  def test_duplicate_raises
    @service.create(name: "Alice", email: "alice@test.com")
    assert_raise(DuplicateError) { @service.create(name: "Bob", email: "alice@test.com") }
  end

  # Sub-tests
  def test_bulk_operations
    users = %w[Alice Bob Charlie]
    users.each do |name|
      sub_test_case(name) do
        user = @service.create(name: name, email: "#{name.downcase}@test.com")
        assert_equal name, user.name
      end
    end
  end
end
```

## Test Suite Organization

```ruby
# Priority and tagging
class SmokeTest < Test::Unit::TestCase
  def self.priority; :must; end

  def test_homepage_loads
    response = HttpClient.get("/")
    assert_equal 200, response.status
  end
end

# Custom test runner
class VerboseRunner < Test::Unit::UI::Console::TestRunner
  def test_started(name)
    puts "  ▶ #{name}"
  end
  def test_finished(name)
    puts "  ✓ #{name}"
  end
end
```

## Anti-Patterns

- ❌ `assert result` without specific value — use `assert_equal expected, actual`
- ❌ Tests depending on execution order — each test must be independent
- ❌ Long setup methods — extract to factory/builder helpers
- ❌ Rescue in test methods — let exceptions propagate to runner
