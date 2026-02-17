# RSpec — Advanced Implementation Playbook

## §1 Project Setup & Configuration

### Gemfile
```ruby
group :test do
  gem 'rspec', '~> 3.13'
  gem 'rspec-rails', '~> 6.1'      # for Rails projects
  gem 'factory_bot_rspec', '~> 6.2'
  gem 'faker', '~> 3.2'
  gem 'shoulda-matchers', '~> 6.0'
  gem 'webmock', '~> 3.19'
  gem 'vcr', '~> 6.2'
  gem 'simplecov', '~> 0.22', require: false
  gem 'timecop', '~> 0.9'
  gem 'database_cleaner-active_record', '~> 2.1'
end
```

### .rspec
```
--require spec_helper
--format documentation
--color
--order random
--profile 10
```

### spec/spec_helper.rb
```ruby
require 'simplecov'
SimpleCov.start do
  add_filter '/spec/'
  add_group 'Models', 'app/models'
  add_group 'Services', 'app/services'
  add_group 'Controllers', 'app/controllers'
  minimum_coverage 90
end

RSpec.configure do |config|
  config.expect_with :rspec do |expectations|
    expectations.include_chain_clauses_in_custom_matcher_descriptions = true
  end

  config.mock_with :rspec do |mocks|
    mocks.verify_partial_doubles = true
  end

  config.shared_context_metadata_behavior = :apply_to_host_groups
  config.filter_run_when_matching :focus
  config.example_status_persistence_file_path = 'spec/examples.txt'
  config.disable_monkey_patching!
  config.order = :random
  Kernel.srand config.seed
end
```

### spec/rails_helper.rb (Rails)
```ruby
require 'spec_helper'
ENV['RAILS_ENV'] ||= 'test'
require_relative '../config/environment'
require 'rspec/rails'

Dir[Rails.root.join('spec/support/**/*.rb')].each { |f| require f }

RSpec.configure do |config|
  config.use_transactional_fixtures = true
  config.infer_spec_type_from_file_location!
  config.filter_rails_from_backtrace!

  config.include FactoryBot::Syntax::Methods
  config.include Shoulda::Matchers::ActiveModel, type: :model
  config.include Shoulda::Matchers::ActiveRecord, type: :model

  config.before(:suite) do
    DatabaseCleaner.strategy = :transaction
    DatabaseCleaner.clean_with(:truncation)
  end
end

Shoulda::Matchers.configure do |config|
  config.integrate do |with|
    with.test_framework :rspec
    with.library :rails
  end
end
```

---

## §2 Model & Service Tests

### Service Tests with Doubles
```ruby
RSpec.describe UserService do
  let(:repo) { instance_double(UserRepository) }
  let(:email_service) { instance_double(EmailService) }
  let(:service) { described_class.new(repo, email_service) }

  describe '#create' do
    context 'with valid data' do
      let(:user) { User.new(id: 1, name: 'Alice', email: 'alice@test.com') }

      before do
        allow(repo).to receive(:find_by_email).and_return(nil)
        allow(repo).to receive(:save).and_return(user)
        allow(email_service).to receive(:send_welcome)
      end

      it 'creates and returns the user' do
        result = service.create(name: 'Alice', email: 'alice@test.com')
        expect(result.name).to eq('Alice')
      end

      it 'sends welcome email' do
        service.create(name: 'Alice', email: 'alice@test.com')
        expect(email_service).to have_received(:send_welcome).with('alice@test.com').once
      end

      it 'persists to repository' do
        service.create(name: 'Alice', email: 'alice@test.com')
        expect(repo).to have_received(:save).once
      end
    end

    context 'with duplicate email' do
      before { allow(repo).to receive(:find_by_email).and_return(User.new(id: 1)) }

      it 'raises ConflictError' do
        expect { service.create(name: 'Alice', email: 'alice@test.com') }
          .to raise_error(ConflictError, /already exists/i)
      end

      it 'does not send welcome email' do
        service.create(name: 'Alice', email: 'alice@test.com') rescue nil
        expect(email_service).not_to have_received(:send_welcome)
      end
    end
  end

  describe '#find' do
    subject { service.find(1) }

    context 'when user exists' do
      before { allow(repo).to receive(:find).with(1).and_return(User.new(id: 1, name: 'Alice')) }
      it { is_expected.to be_a(User) }
      it { is_expected.to have_attributes(id: 1, name: 'Alice') }
    end

    context 'when user not found' do
      before { allow(repo).to receive(:find).with(1).and_return(nil) }
      it { is_expected.to be_nil }
    end
  end
end
```

### Rails Model Tests with Shoulda
```ruby
RSpec.describe User, type: :model do
  describe 'validations' do
    it { is_expected.to validate_presence_of(:name) }
    it { is_expected.to validate_presence_of(:email) }
    it { is_expected.to validate_uniqueness_of(:email).case_insensitive }
    it { is_expected.to validate_length_of(:name).is_at_most(100) }
  end

  describe 'associations' do
    it { is_expected.to have_many(:orders).dependent(:destroy) }
    it { is_expected.to belong_to(:organization).optional }
    it { is_expected.to have_one(:profile) }
  end

  describe 'scopes' do
    describe '.active' do
      it 'returns only active users' do
        active = create(:user, active: true)
        create(:user, active: false)
        expect(User.active).to contain_exactly(active)
      end
    end
  end
end
```

---

## §3 Shared Examples & Contexts

### Shared Examples
```ruby
RSpec.shared_examples 'a searchable resource' do |factory_name|
  describe '.search' do
    let!(:matching) { create(factory_name, name: 'Alice Smith') }
    let!(:non_matching) { create(factory_name, name: 'Bob Jones') }

    it 'finds by partial name' do
      expect(described_class.search('Alice')).to include(matching)
    end

    it 'excludes non-matching records' do
      expect(described_class.search('Alice')).not_to include(non_matching)
    end

    it 'returns empty for no match' do
      expect(described_class.search('zzz')).to be_empty
    end

    it 'is case-insensitive' do
      expect(described_class.search('alice')).to include(matching)
    end
  end
end

RSpec.describe User do
  it_behaves_like 'a searchable resource', :user
end

RSpec.describe Product do
  it_behaves_like 'a searchable resource', :product
end
```

### Shared Context
```ruby
RSpec.shared_context 'authenticated user' do
  let(:current_user) { create(:user, role: :admin) }
  let(:auth_headers) { { 'Authorization' => "Bearer #{current_user.auth_token}" } }

  before { allow(AuthService).to receive(:current_user).and_return(current_user) }
end

RSpec.describe Admin::UsersController, type: :controller do
  include_context 'authenticated user'

  describe 'GET #index' do
    it 'returns success' do
      get :index, headers: auth_headers
      expect(response).to have_http_status(:ok)
    end
  end
end
```

---

## §4 FactoryBot & Test Data

```ruby
# spec/factories/users.rb
FactoryBot.define do
  factory :user do
    name { Faker::Name.full_name }
    email { Faker::Internet.unique.email }
    password { 'password123' }
    active { true }

    trait :admin do
      role { :admin }
    end

    trait :with_orders do
      transient do
        order_count { 3 }
      end
      after(:create) do |user, evaluator|
        create_list(:order, evaluator.order_count, user: user)
      end
    end

    trait :inactive do
      active { false }
    end

    factory :admin_user, traits: [:admin]
  end
end

# Usage in tests
let(:user) { create(:user) }
let(:admin) { create(:user, :admin) }
let(:user_with_orders) { create(:user, :with_orders, order_count: 5) }
let(:users) { create_list(:user, 10) }
```

---

## §5 HTTP Mocking with WebMock & VCR

### WebMock
```ruby
require 'webmock/rspec'
WebMock.disable_net_connect!(allow_localhost: true)

RSpec.describe ExternalApiClient do
  describe '#fetch_weather' do
    before do
      stub_request(:get, 'https://api.weather.com/v1/forecast')
        .with(query: { city: 'London' })
        .to_return(
          status: 200,
          body: { temp: 15, condition: 'Cloudy' }.to_json,
          headers: { 'Content-Type' => 'application/json' }
        )
    end

    it 'returns parsed weather data' do
      result = subject.fetch_weather('London')
      expect(result[:temp]).to eq(15)
    end
  end

  context 'when API is down' do
    before { stub_request(:get, /api\.weather\.com/).to_timeout }

    it 'raises TimeoutError' do
      expect { subject.fetch_weather('London') }.to raise_error(TimeoutError)
    end
  end
end
```

### VCR for Recording
```ruby
# spec/support/vcr.rb
VCR.configure do |config|
  config.cassette_library_dir = 'spec/cassettes'
  config.hook_into :webmock
  config.configure_rspec_metadata!
  config.filter_sensitive_data('<API_KEY>') { ENV['API_KEY'] }
end

RSpec.describe 'GitHub API', :vcr do
  it 'fetches repository info' do
    client = GitHubClient.new
    repo = client.get_repo('rails/rails')
    expect(repo[:full_name]).to eq('rails/rails')
  end
end
```

---

## §6 Request & Controller Tests (Rails)

```ruby
RSpec.describe 'Users API', type: :request do
  describe 'GET /api/users' do
    let!(:users) { create_list(:user, 3) }

    it 'returns paginated users' do
      get '/api/users', params: { page: 1, per: 2 }
      expect(response).to have_http_status(:ok)
      body = JSON.parse(response.body)
      expect(body['data'].length).to eq(2)
      expect(body['meta']['total']).to eq(3)
    end
  end

  describe 'POST /api/users' do
    let(:valid_params) { { user: { name: 'Alice', email: 'alice@test.com' } } }
    let(:invalid_params) { { user: { name: '', email: 'bad' } } }

    context 'with valid params' do
      it 'creates user and returns 201' do
        expect { post '/api/users', params: valid_params }
          .to change(User, :count).by(1)
        expect(response).to have_http_status(:created)
      end
    end

    context 'with invalid params' do
      it 'returns 422 with errors' do
        post '/api/users', params: invalid_params
        expect(response).to have_http_status(:unprocessable_entity)
        errors = JSON.parse(response.body)['errors']
        expect(errors).to include('Name can\'t be blank')
      end
    end
  end
end
```

---

## §7 Time-Based Testing

```ruby
require 'timecop'

RSpec.describe Subscription do
  describe '#expired?' do
    let(:subscription) { create(:subscription, expires_at: 1.month.from_now) }

    it 'returns false before expiry' do
      expect(subscription).not_to be_expired
    end

    it 'returns true after expiry' do
      Timecop.travel(2.months.from_now) do
        expect(subscription).to be_expired
      end
    end
  end

  describe '.expiring_soon' do
    it 'returns subscriptions expiring within 7 days' do
      expiring = create(:subscription, expires_at: 5.days.from_now)
      not_expiring = create(:subscription, expires_at: 30.days.from_now)

      Timecop.freeze(Time.current) do
        expect(Subscription.expiring_soon).to include(expiring)
        expect(Subscription.expiring_soon).not_to include(not_expiring)
      end
    end
  end
end
```

---

## §8 Custom Matchers

```ruby
# spec/support/matchers/have_json_body.rb
RSpec::Matchers.define :have_json_body do |expected|
  match do |response|
    body = JSON.parse(response.body, symbolize_names: true)
    values_match?(expected, body)
  end

  failure_message do |response|
    "expected response body to match #{expected.inspect}, got #{JSON.parse(response.body).inspect}"
  end
end

# Usage:
expect(response).to have_json_body(include(name: 'Alice'))
```

---

## §9 CI/CD Integration

```yaml
name: RSpec CI
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: password }
        ports: ['5432:5432']
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
      redis:
        image: redis:7
        ports: ['6379:6379']

    env:
      DATABASE_URL: postgres://postgres:password@localhost:5432/test
      RAILS_ENV: test

    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.3', bundler-cache: true }
      - run: bundle exec rails db:create db:migrate
      - run: bundle exec rspec --format progress --format RspecJunitFormatter --out results/junit.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: rspec-results, path: results/ }
```

---

## §10 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | Tests pass in isolation, fail together | Shared database state or global variables | Use `DatabaseCleaner` with `:transaction` strategy; avoid global state |
| 2 | `instance_double` raises `VerifyingDouble` error | Method signature mismatch | Ensure double's method matches real class interface exactly |
| 3 | `let` value stale across examples | Memoized value cached | Use `let!` for eager evaluation or new `let` in nested context |
| 4 | Factory creates too many DB records | Nested associations auto-create | Use `build_stubbed` for unit tests; only `create` for integration |
| 5 | `stub_request` not intercepting | URL mismatch (trailing slash, params) | Use regex matcher: `stub_request(:get, /api\.weather/)` |
| 6 | Random test order failures | Implicit dependency on execution order | Run with `--bisect` to find coupled tests; fix shared state |
| 7 | `have_received` fails | Mock set up with `allow` but not called | Verify the code path actually calls the mocked method |
| 8 | `Timecop.freeze` leaks to other tests | Missing `Timecop.return` in `after` | Use block form: `Timecop.freeze(time) { ... }` |
| 9 | `VCR::Errors::UnhandledHTTPRequestError` | New HTTP call not recorded | Run test once without VCR to record cassette; or add new `stub_request` |
| 10 | Coverage drops after refactor | New code paths untested | Run `simplecov` with `minimum_coverage 90`; add missing specs |

---

## §11 Best Practices Checklist

1. ✅ Use `let` (lazy) over `before` for variable setup — only evaluated when referenced
2. ✅ Use `describe` for methods, `context` for conditions (When X / With Y)
3. ✅ Use `instance_double` for strict type-checked mocks — catches interface changes
4. ✅ Use `shared_examples` for reusable spec groups across similar models
5. ✅ Use `subject` for the object under test — enables one-liner syntax
6. ✅ Use FactoryBot with traits for flexible test data
7. ✅ Use `build_stubbed` for unit tests (no DB), `create` for integration
8. ✅ Use WebMock to disable all external HTTP — `disable_net_connect!`
9. ✅ Use `--format documentation` for readable output, `--profile` for slow test detection
10. ✅ Use `--fail-fast` during development, full suite in CI
11. ✅ Use `--bisect` to isolate random-order failures
12. ✅ Use `Timecop.freeze` block form for time-dependent tests
13. ✅ Use `SimpleCov` with minimum coverage threshold
14. ✅ Keep specs adjacent: `app/models/user.rb` → `spec/models/user_spec.rb`
