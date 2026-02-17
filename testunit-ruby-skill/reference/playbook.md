# Test::Unit (Ruby) — Advanced Playbook

## §1 — Project Setup

### Gemfile
```ruby
# Gemfile
source 'https://rubygems.org'

group :test do
  gem 'test-unit', '~> 3.6'
  gem 'test-unit-rr', '~> 1.0'   # Mocking
  gem 'webmock', '~> 3.23'       # HTTP stubbing
  gem 'rack-test', '~> 2.1'      # Rack app testing
  gem 'simplecov', '~> 0.22'     # Coverage
  gem 'selenium-webdriver', '~> 4.18'
  gem 'capybara', '~> 3.40'      # Optional for UI
end
```

### Project Structure
```
project/
├── Gemfile
├── Rakefile
├── lib/
│   ├── user_service.rb
│   ├── email_validator.rb
│   └── api_client.rb
├── test/
│   ├── test_helper.rb
│   ├── unit/
│   │   ├── test_user_service.rb
│   │   ├── test_email_validator.rb
│   │   └── test_api_client.rb
│   ├── integration/
│   │   ├── test_user_api.rb
│   │   └── test_auth_flow.rb
│   └── fixtures/
│       ├── users.yml
│       └── responses/
│           └── user_response.json
└── .simplecov
```

### test_helper.rb
```ruby
require 'simplecov'
SimpleCov.start do
  add_filter '/test/'
  add_group 'Models', 'lib/models'
  add_group 'Services', 'lib/services'
  minimum_coverage 80
end

require 'test/unit'
require 'test/unit/rr'
require 'webmock/test_unit'
require 'json'
require 'yaml'

# Load application code
$LOAD_PATH.unshift File.join(__dir__, '..', 'lib')

module TestHelpers
  def fixture_path(name)
    File.join(__dir__, 'fixtures', name)
  end

  def load_fixture(name)
    path = fixture_path(name)
    case File.extname(name)
    when '.json' then JSON.parse(File.read(path))
    when '.yml', '.yaml' then YAML.load_file(path)
    else File.read(path)
    end
  end

  def assert_raises_with_message(exception_class, message_pattern)
    error = assert_raise(exception_class) { yield }
    assert_match(message_pattern, error.message)
    error
  end
end
```

### Rakefile
```ruby
require 'rake/testtask'

Rake::TestTask.new(:test) do |t|
  t.libs << 'test' << 'lib'
  t.pattern = 'test/**/test_*.rb'
  t.verbose = true
  t.warning = false
end

Rake::TestTask.new(:unit) do |t|
  t.libs << 'test' << 'lib'
  t.pattern = 'test/unit/**/test_*.rb'
  t.verbose = true
end

Rake::TestTask.new(:integration) do |t|
  t.libs << 'test' << 'lib'
  t.pattern = 'test/integration/**/test_*.rb'
  t.verbose = true
end

task default: :test
```

---

## §2 — Core Test Patterns

### Basic Assertions
```ruby
require 'test_helper'
require 'user_service'

class TestUserService < Test::Unit::TestCase
  include TestHelpers

  def setup
    @repo = MockRepo.new
    @service = UserService.new(@repo)
  end

  def teardown
    @repo.reset!
  end

  # Basic assertions
  def test_create_user_returns_user_with_id
    user = @service.create(name: 'Alice', email: 'alice@test.com')
    assert_not_nil user.id, 'User should have an ID after creation'
    assert_equal 'Alice', user.name
    assert_equal 'alice@test.com', user.email
  end

  def test_create_user_with_invalid_email_raises
    assert_raise(ValidationError) do
      @service.create(name: 'Alice', email: 'bad-email')
    end
  end

  def test_find_returns_nil_for_missing_user
    assert_nil @service.find(999)
  end

  def test_list_users_returns_array
    @service.create(name: 'Alice', email: 'alice@test.com')
    @service.create(name: 'Bob', email: 'bob@test.com')

    users = @service.list
    assert_kind_of Array, users
    assert_equal 2, users.length
  end

  # Boolean assertions
  def test_user_is_active_by_default
    user = @service.create(name: 'Alice', email: 'alice@test.com')
    assert user.active?, 'New user should be active'
  end

  def test_deleted_user_is_not_active
    user = @service.create(name: 'Alice', email: 'alice@test.com')
    @service.delete(user.id)
    assert_false user.active?
  end

  # Collection assertions
  def test_search_returns_matching_users
    @service.create(name: 'Alice Smith', email: 'alice@test.com')
    @service.create(name: 'Bob Jones', email: 'bob@test.com')

    results = @service.search('Alice')
    assert_not_empty results
    assert results.all? { |u| u.name.include?('Alice') }
  end

  # Numeric assertions
  def test_user_count_increments
    initial = @service.count
    @service.create(name: 'New User', email: 'new@test.com')
    assert_equal initial + 1, @service.count
  end

  def test_balance_within_range
    user = @service.create(name: 'Alice', email: 'alice@test.com')
    assert_in_delta 0.0, user.balance, 0.01
  end

  # String assertions
  def test_user_full_name
    user = @service.create(name: 'Alice', email: 'alice@test.com', last_name: 'Smith')
    assert_match(/Alice\s+Smith/, user.full_name)
  end
end
```

---

## §3 — Data-Driven Testing

### Using `data` Method
```ruby
class TestEmailValidator < Test::Unit::TestCase

  # Data-driven with named test cases
  data(
    'valid standard'    => ['user@example.com', true],
    'valid with dots'   => ['first.last@example.com', true],
    'valid with plus'   => ['user+tag@example.com', true],
    'valid subdomain'   => ['user@sub.example.com', true],
    'invalid no at'     => ['userexample.com', false],
    'invalid no domain' => ['user@', false],
    'invalid no user'   => ['@example.com', false],
    'empty string'      => ['', false],
    'nil value'         => [nil, false],
    'spaces only'       => ['   ', false]
  )
  def test_email_validation(data)
    email, expected = data
    assert_equal expected, EmailValidator.valid?(email),
      "Expected EmailValidator.valid?(#{email.inspect}) to be #{expected}"
  end

  # Data from CSV-like structure
  data do
    data_set = {}
    [
      ['password123', false, 'too simple'],
      ['P@ssw0rd!Long', true, 'meets all requirements'],
      ['short', false, 'too short'],
      ['NoSpecialChar1', false, 'missing special character'],
    ].each do |password, valid, description|
      data_set[description] = [password, valid]
    end
    data_set
  end
  def test_password_strength(data)
    password, expected_valid = data
    assert_equal expected_valid, PasswordValidator.strong?(password)
  end

  # Data from fixtures
  data do
    users = YAML.load_file('test/fixtures/users.yml')
    users.transform_values { |u| [u['email'], u['valid']] }
  end
  def test_user_email_from_fixtures(data)
    email, expected = data
    assert_equal expected, EmailValidator.valid?(email)
  end
end
```

### Test Suites and Ordering
```ruby
class TestUserWorkflow < Test::Unit::TestCase
  # Priority-based ordering
  def test_01_create_user
    # runs first
  end

  def test_02_update_user
    # runs second
  end

  def test_03_delete_user
    # runs third
  end

  # Sub-test for grouping
  sub_test_case 'when user is admin' do
    def setup
      @user = create_admin_user
    end

    def test_can_access_admin_panel
      assert @user.can_access?(:admin_panel)
    end

    def test_can_manage_users
      assert @user.can_manage?(:users)
    end
  end

  sub_test_case 'when user is regular' do
    def setup
      @user = create_regular_user
    end

    def test_cannot_access_admin_panel
      assert_false @user.can_access?(:admin_panel)
    end
  end
end
```

---

## §4 — Mocking & Stubbing

### Using test-unit-rr
```ruby
class TestAPIClient < Test::Unit::TestCase
  include TestHelpers

  def setup
    @http = Object.new
    @client = APIClient.new(http: @http)
  end

  # Stub return values
  def test_fetch_user_parses_response
    response_body = load_fixture('responses/user_response.json')
    stub(@http).get('/api/users/1') {
      OpenStruct.new(code: '200', body: response_body.to_json)
    }

    user = @client.fetch_user(1)
    assert_equal 'Alice', user['name']
    assert_equal 'alice@test.com', user['email']
  end

  # Verify method calls
  def test_create_user_sends_post_request
    mock(@http).post('/api/users', is_a(String)) {
      OpenStruct.new(code: '201', body: '{"id": 1}')
    }

    @client.create_user(name: 'Alice', email: 'alice@test.com')
    # rr automatically verifies mock expectations
  end

  # Stub with conditions
  def test_handles_404_gracefully
    stub(@http).get(anything) {
      OpenStruct.new(code: '404', body: '{"error": "Not found"}')
    }

    result = @client.fetch_user(999)
    assert_nil result
  end

  # Stub sequence of calls
  def test_retry_on_failure
    call_count = 0
    stub(@http).get('/api/health') {
      call_count += 1
      if call_count < 3
        raise Net::ReadTimeout
      end
      OpenStruct.new(code: '200', body: '{"status": "ok"}')
    }

    result = @client.health_check(retries: 3)
    assert_equal 'ok', result['status']
    assert_equal 3, call_count
  end
end
```

### WebMock for HTTP
```ruby
class TestExternalAPI < Test::Unit::TestCase
  def setup
    WebMock.disable_net_connect!(allow_localhost: true)
  end

  def test_fetches_external_data
    stub_request(:get, 'https://api.example.com/data')
      .with(headers: { 'Authorization' => 'Bearer token123' })
      .to_return(
        status: 200,
        body: { results: [{ id: 1, name: 'Item' }] }.to_json,
        headers: { 'Content-Type' => 'application/json' }
      )

    client = ExternalAPIClient.new(token: 'token123')
    data = client.fetch_data
    assert_equal 1, data['results'].length
  end

  def test_handles_timeout
    stub_request(:get, 'https://api.example.com/data')
      .to_timeout

    client = ExternalAPIClient.new(token: 'token123')
    assert_raise(APITimeoutError) { client.fetch_data }
  end

  def test_handles_server_error_with_retry
    stub_request(:get, 'https://api.example.com/data')
      .to_return(status: 500).then
      .to_return(status: 500).then
      .to_return(status: 200, body: '{"ok": true}')

    client = ExternalAPIClient.new(token: 'token123', retries: 3)
    result = client.fetch_data
    assert_equal true, result['ok']
  end
end
```

---

## §5 — Custom Assertions

### Creating Custom Assertions
```ruby
module CustomAssertions
  def assert_valid_email(email, message = nil)
    full_message = build_message(message, "Expected <?> to be a valid email", email)
    assert_block(full_message) { email =~ /\A[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+\z/i }
  end

  def assert_json_schema(json, schema, message = nil)
    errors = JSON::Validator.validate(schema, json, list: true)
    full_message = build_message(message,
      "JSON does not match schema.\nErrors: ?", errors.join(', '))
    assert_block(full_message) { errors.empty? }
  end

  def assert_response_success(response, message = nil)
    full_message = build_message(message,
      "Expected successful response, got status ?", response.code)
    assert_block(full_message) { (200..299).include?(response.code.to_i) }
  end

  def assert_eventually(timeout: 5, interval: 0.5, message: nil)
    deadline = Time.now + timeout
    last_error = nil
    while Time.now < deadline
      begin
        yield
        return
      rescue Test::Unit::AssertionFailedError => e
        last_error = e
        sleep interval
      end
    end
    raise last_error || AssertionFailedError.new(message || "Condition not met within #{timeout}s")
  end
end

# Usage
class TestWithCustomAssertions < Test::Unit::TestCase
  include CustomAssertions

  def test_email_format
    assert_valid_email('user@test.com')
  end

  def test_async_operation
    service = AsyncService.new
    service.start_job

    assert_eventually(timeout: 10, interval: 1) do
      assert_equal 'completed', service.job_status
    end
  end
end
```

---

## §6 — Integration Testing

### Rack App Testing
```ruby
require 'rack/test'

class TestWebApp < Test::Unit::TestCase
  include Rack::Test::Methods

  def app
    MyApp.new
  end

  def test_homepage_returns_200
    get '/'
    assert_equal 200, last_response.status
    assert last_response.body.include?('Welcome')
  end

  def test_create_user_api
    post '/api/users',
      { name: 'Alice', email: 'alice@test.com' }.to_json,
      { 'CONTENT_TYPE' => 'application/json' }

    assert_equal 201, last_response.status

    body = JSON.parse(last_response.body)
    assert_not_nil body['id']
    assert_equal 'Alice', body['name']
  end

  def test_authentication_required
    get '/api/protected'
    assert_equal 401, last_response.status
  end

  def test_authenticated_request
    # Login first
    post '/api/login', { email: 'admin@test.com', password: 'password' }.to_json,
      { 'CONTENT_TYPE' => 'application/json' }
    token = JSON.parse(last_response.body)['token']

    # Use token
    get '/api/protected', {}, { 'HTTP_AUTHORIZATION' => "Bearer #{token}" }
    assert_equal 200, last_response.status
  end
end
```

---

## §7 — CI/CD Integration

### GitHub Actions
```yaml
name: Ruby Test::Unit Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        ruby-version: ['3.2', '3.3']

    steps:
      - uses: actions/checkout@v4

      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: ${{ matrix.ruby-version }}
          bundler-cache: true

      - name: Run tests
        run: bundle exec rake test

      - name: Run tests with verbose output
        run: bundle exec ruby -Itest -Ilib -e "Dir.glob('test/**/test_*.rb').each { |f| require f }"
        if: failure()

      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.ruby-version }}
          path: coverage/
```

### Code Coverage Gate
```ruby
# .simplecov
SimpleCov.start do
  add_filter '/test/'
  add_filter '/vendor/'

  add_group 'Models', 'lib/models'
  add_group 'Services', 'lib/services'
  add_group 'API', 'lib/api'

  minimum_coverage 80
  minimum_coverage_by_file 70

  refuse_coverage_drop
end
```

---

## §8 — Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `test_` method not running | Method name doesn't start with `test_` | All test methods must be named `test_*` |
| 2 | `data` method test shows 1 test | Data block returns wrong format | Return Hash: `{ 'label' => [args] }` |
| 3 | `setup` runs but tests fail | Instance variables from setup not accessible | Use `@` instance variables; ensure `setup` is spelled correctly |
| 4 | `sub_test_case` not recognized | Wrong gem version or missing require | Requires `test-unit` gem ≥ 3.0; add `require 'test/unit'` |
| 5 | Mock expectations not verified | Using stubs instead of mocks | Use `mock(obj).method` for verification; `stub` doesn't verify calls |
| 6 | `WebMock` not intercepting | `disable_net_connect!` not called | Add `WebMock.disable_net_connect!` in `setup` |
| 7 | Fixture file not found | Wrong path relative to test | Use `File.join(__dir__, 'fixtures', name)` for reliable paths |
| 8 | Tests run in random order | Test::Unit randomizes by default | Use `test_01_`, `test_02_` prefix for explicit ordering if needed |
| 9 | `assert_raise` catches wrong exception | Exception hierarchy mismatch | Specify exact exception class; use `assert_raise(SpecificError)` |
| 10 | Coverage below threshold | New code not covered | Check `coverage/index.html` for uncovered lines; add targeted tests |
| 11 | `require` fails for app code | `$LOAD_PATH` not configured | Add `$LOAD_PATH.unshift File.join(__dir__, '..', 'lib')` in test_helper |
| 12 | Teardown not cleaning up | Exception in teardown suppressed | Wrap teardown logic in begin/ensure; check for nil references |

---

## §9 — Best Practices Checklist

1. **Prefix all test methods with `test_`** — only `test_*` methods execute as tests
2. **Use `setup`/`teardown` for lifecycle** — initialize in `setup`, clean up in `teardown`
3. **`data` method for parameterized tests** — data-driven with named cases for clarity
4. **`sub_test_case` for grouping** — organize related tests without separate files
5. **Custom assertions for domain logic** — `assert_valid_email`, `assert_json_schema` for readability
6. **WebMock for HTTP isolation** — stub external APIs; `disable_net_connect!` prevents leaks
7. **test-unit-rr for mocking** — `mock` for verification, `stub` for return values
8. **Fixtures for test data** — YAML/JSON files in `test/fixtures/` loaded via helper
9. **SimpleCov for coverage** — minimum 80% coverage with `refuse_coverage_drop`
10. **Rakefile with task targets** — `rake test`, `rake unit`, `rake integration` for selective runs
11. **`assert_raise` with block** — capture exceptions and verify message content
12. **Test helper module** — shared utilities included in test classes
13. **Verbose output for debugging** — `ruby -v` or `--verbose` flag for detailed failure info
14. **Consider RSpec migration** — for new projects, RSpec offers richer DSL and better community support
