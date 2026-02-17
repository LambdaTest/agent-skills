---
name: testunit-ruby-skill
description: >
  Generates Test::Unit tests in Ruby. Classic xUnit-style testing with assert
  methods and test case classes. Use when user mentions "Test::Unit",
  "assert_equal Ruby", "Ruby test-unit". Triggers on: "Test::Unit",
  "Ruby test-unit", "assert_equal Ruby" (not RSpec).
languages:
  - Ruby
category: unit-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Test::Unit Ruby Skill

## Core Patterns

### Basic Test

```ruby
require 'test/unit'

class TestCalculator < Test::Unit::TestCase
  def setup
    @calc = Calculator.new
  end

  def test_addition
    assert_equal(5, @calc.add(2, 3), "2 + 3 should equal 5")
  end

  def test_subtraction
    assert_equal(1, @calc.subtract(3, 2))
  end

  def test_division_by_zero
    assert_raise(ZeroDivisionError) { @calc.divide(10, 0) }
  end

  def test_float_division
    assert_in_delta(3.33, @calc.divide(10, 3), 0.01)
  end

  def teardown
    # cleanup
  end
end
```

### Assertions

```ruby
assert_equal(expected, actual, message = nil)
assert_not_equal(unexpected, actual)
assert_true(value)
assert_false(value)
assert_nil(value)
assert_not_nil(value)
assert_instance_of(klass, obj)
assert_kind_of(klass, obj)
assert_respond_to(obj, :method_name)
assert_match(/pattern/, string)
assert_no_match(/pattern/, string)
assert_include(collection, item)
assert_not_include(collection, item)
assert_empty(collection)
assert_not_empty(collection)
assert_raise(ErrorClass) { block }
assert_nothing_raised { block }
assert_in_delta(expected, actual, delta)
assert_operator(value, :>, 5)
assert_send([obj, :method, arg])
assert_block("message") { condition }
```

### Test Fixtures

```ruby
class TestDatabase < Test::Unit::TestCase
  def self.startup
    # Once before all tests in class
    @@db = Database.connect('test')
  end

  def self.shutdown
    # Once after all tests in class
    @@db.disconnect
  end

  def setup
    # Before each test
    @@db.begin_transaction
  end

  def teardown
    # After each test
    @@db.rollback
  end
end
```

### Test Ordering and Naming

```ruby
class TestUserService < Test::Unit::TestCase
  # Methods must start with 'test_'
  def test_create_user
    user = UserService.create('Alice', 'alice@test.com')
    assert_not_nil(user)
    assert_equal('Alice', user.name)
  end

  def test_find_user_by_email
    user = UserService.find_by_email('alice@test.com')
    assert_instance_of(User, user)
  end
end
```

## Setup: `gem install test-unit`
## Run: `ruby test/test_calculator.rb` or `ruby -Itest -e "Dir.glob('test/**/test_*.rb').each{|f| require f}"`
## Autodiscovery: `testrb test/` (with test-unit gem)

## Deep Patterns

For advanced patterns, debugging guides, CI/CD integration, and best practices,
see `reference/playbook.md`.
