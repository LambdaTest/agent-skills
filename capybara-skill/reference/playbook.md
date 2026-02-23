# Capybara — Advanced Playbook

## §1 Project Setup & Configuration

### Gemfile
```ruby
group :test do
  gem 'capybara', '~> 3.40'
  gem 'selenium-webdriver', '~> 4.18'
  gem 'rspec', '~> 3.13'
  gem 'site_prism', '~> 5.0'       # Page Objects
  gem 'capybara-screenshot', '~> 1.0'
  gem 'factory_bot', '~> 6.4'
  gem 'database_cleaner-active_record', '~> 2.1'
  gem 'webmock', '~> 3.23'
  gem 'vcr', '~> 6.2'
end
```

### spec/support/capybara.rb
```ruby
require 'capybara/rspec'
require 'capybara-screenshot/rspec'

Capybara.configure do |config|
  config.default_driver = :selenium_chrome_headless
  config.app_host = ENV.fetch('BASE_URL', 'http://localhost:3000')
  config.default_max_wait_time = 10
  config.server_port = 3001
  config.save_path = 'tmp/screenshots'
  config.automatic_label_click = true
end

Capybara.register_driver :selenium_chrome_headless do |app|
  options = Selenium::WebDriver::Chrome::Options.new
  options.add_argument('--headless=new')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')
  options.add_argument('--window-size=1920,1080')
  Capybara::Selenium::Driver.new(app, browser: :chrome, options: options)
end

# LambdaTest driver
Capybara.register_driver :lambdatest do |app|
  options = Selenium::WebDriver::Chrome::Options.new
  lt_options = {
    'name' => ENV.fetch('TEST_NAME', 'Capybara Test'),
    'build' => ENV.fetch('BUILD_NAME', 'Capybara-Build'),
    'platformName' => 'Windows 11',
    'video' => true,
    'network' => true,
  }
  options.add_option('LT:Options', lt_options)
  url = "https://#{ENV['LT_USERNAME']}:#{ENV['LT_ACCESS_KEY']}@hub.lambdatest.com/wd/hub"
  Capybara::Selenium::Driver.new(app, browser: :remote, url: url, options: options)
end
```

---

## §2 Feature Specs — Interaction Patterns

### Login Flow
```ruby
# spec/features/login_spec.rb
require 'rails_helper'

RSpec.describe 'User Login', type: :feature do
  let!(:user) { create(:user, email: 'test@example.com', password: 'ValidPass123') }

  before { visit login_path }

  context 'with valid credentials' do
    it 'logs in and redirects to dashboard' do
      fill_in 'Email', with: 'test@example.com'
      fill_in 'Password', with: 'ValidPass123'
      click_button 'Sign In'

      expect(page).to have_current_path(dashboard_path)
      expect(page).to have_content('Welcome back')
      expect(page).to have_css('.user-avatar')
    end
  end

  context 'with invalid credentials' do
    it 'shows error message' do
      fill_in 'Email', with: 'test@example.com'
      fill_in 'Password', with: 'wrong'
      click_button 'Sign In'

      expect(page).to have_css('.error-message', text: 'Invalid email or password')
      expect(page).to have_current_path(login_path)
    end
  end

  context 'with empty fields' do
    it 'shows validation errors' do
      click_button 'Sign In'
      expect(page).to have_css('.field-error', minimum: 1)
    end
  end
end
```

### Complex Interactions
```ruby
# spec/features/checkout_spec.rb
RSpec.describe 'Checkout Flow', type: :feature, js: true do
  let!(:product) { create(:product, name: 'Widget', price: 29.99) }
  let!(:user) { create(:user) }

  before do
    sign_in(user)
    visit products_path
  end

  it 'completes purchase end-to-end' do
    # Search and add to cart
    fill_in 'Search', with: 'Widget'
    click_button 'Search'
    within('.product-card', text: 'Widget') do
      click_button 'Add to Cart'
    end
    expect(page).to have_css('.cart-badge', text: '1')

    # Proceed to checkout
    visit cart_path
    click_link 'Proceed to Checkout'

    # Fill shipping
    within('#shipping-form') do
      fill_in 'Street', with: '123 Test Lane'
      fill_in 'City', with: 'Testville'
      fill_in 'ZIP', with: '12345'
      select 'United States', from: 'Country'
    end
    click_button 'Continue'

    # Payment
    within('#payment-form') do
      fill_in 'Card Number', with: '4242424242424242'
      fill_in 'Expiry', with: '12/28'
      fill_in 'CVV', with: '123'
    end
    click_button 'Place Order'

    # Verify
    expect(page).to have_content('Order Confirmed')
    expect(page).to have_content('$29.99')
  end
end
```

### Working with JavaScript & Modals
```ruby
RSpec.describe 'JavaScript Interactions', type: :feature, js: true do
  it 'handles modal dialog' do
    visit settings_path
    click_button 'Delete Account'

    within('.modal') do
      expect(page).to have_content('Are you sure?')
      click_button 'Cancel'
    end
    expect(page).not_to have_css('.modal')
  end

  it 'handles async content loading' do
    visit dashboard_path
    expect(page).to have_css('.loading-spinner')
    expect(page).to have_css('.dashboard-data', wait: 15)
    expect(page).not_to have_css('.loading-spinner')
  end

  it 'accepts browser alert' do
    visit dangerous_action_path
    click_link 'Reset Everything'
    accept_alert 'This cannot be undone'
    expect(page).to have_content('Reset complete')
  end
end
```

---

## §3 Page Objects with SitePrism

```ruby
# spec/support/pages/login_page.rb
class LoginPage < SitePrism::Page
  set_url '/login'

  element :email_field, '#email'
  element :password_field, '#password'
  element :submit_button, '#login-submit'
  element :error_message, '.error-message'
  element :remember_me, '#remember-me'

  def login(email, password)
    email_field.set(email)
    password_field.set(password)
    submit_button.click
  end
end

class DashboardPage < SitePrism::Page
  set_url '/dashboard'
  set_url_matcher %r{/dashboard}

  element :welcome_message, '.welcome-msg'
  element :user_avatar, '.user-avatar'
  elements :recent_orders, '.order-card'
  section :sidebar, SidebarSection, '.sidebar'

  def order_count
    recent_orders.count
  end
end

# Usage in specs
RSpec.describe 'Login with Page Objects' do
  let(:login_page) { LoginPage.new }
  let(:dashboard) { DashboardPage.new }

  it 'navigates through pages' do
    login_page.load
    login_page.login('user@test.com', 'ValidPass123')
    expect(dashboard).to be_displayed
    expect(dashboard.welcome_message.text).to include('Welcome')
  end
end
```

---

## §4 API Testing with Capybara

```ruby
# spec/features/api_spec.rb
require 'rails_helper'

RSpec.describe 'API Endpoints', type: :request do
  let(:user) { create(:user) }
  let(:token) { generate_jwt(user) }
  let(:auth_headers) { { 'Authorization' => "Bearer #{token}", 'Content-Type' => 'application/json' } }

  describe 'GET /api/products' do
    let!(:products) { create_list(:product, 15) }

    it 'returns paginated products' do
      get '/api/products', params: { page: 1, limit: 10 }, headers: auth_headers
      expect(response).to have_http_status(200)
      json = JSON.parse(response.body)
      expect(json['data'].length).to eq(10)
      expect(json['meta']['total']).to eq(15)
    end
  end

  describe 'POST /api/products' do
    it 'creates product with valid data' do
      post '/api/products', params: { name: 'Widget', price: 29.99 }.to_json, headers: auth_headers
      expect(response).to have_http_status(201)
      expect(JSON.parse(response.body)['name']).to eq('Widget')
    end

    it 'returns 422 with invalid data' do
      post '/api/products', params: { name: '' }.to_json, headers: auth_headers
      expect(response).to have_http_status(422)
    end
  end
end
```

---

## §5 Database Cleaning & Test Isolation

```ruby
# spec/support/database_cleaner.rb
require 'database_cleaner/active_record'

RSpec.configure do |config|
  config.before(:suite) do
    DatabaseCleaner.clean_with(:truncation)
  end

  config.before(:each) do
    DatabaseCleaner.strategy = :transaction
  end

  config.before(:each, js: true) do
    DatabaseCleaner.strategy = :truncation
  end

  config.before(:each) do
    DatabaseCleaner.start
  end

  config.after(:each) do
    DatabaseCleaner.clean
  end
end
```

---

## §6 Matchers & Custom Helpers

```ruby
# spec/support/helpers.rb
module TestHelpers
  def sign_in(user)
    visit login_path
    fill_in 'Email', with: user.email
    fill_in 'Password', with: 'ValidPass123'
    click_button 'Sign In'
    expect(page).to have_current_path(dashboard_path)
  end

  def expect_flash(message)
    expect(page).to have_css('.flash-message', text: message)
  end
end

RSpec.configure do |config|
  config.include TestHelpers, type: :feature
end
```

---

## §7 CI/CD Integration

### GitHub Actions
```yaml
name: Capybara Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  feature-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ['5432:5432']
      redis:
        image: redis:7
        ports: ['6379:6379']

    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.3'
          bundler-cache: true
      - uses: browser-actions/setup-chrome@v1

      - name: Setup database
        run: |
          bundle exec rails db:create db:migrate
        env:
          RAILS_ENV: test
          DATABASE_URL: postgres://test:test@localhost:5432/testdb

      - name: Run Capybara specs
        run: bundle exec rspec spec/features/ --format documentation --format RspecJunitFormatter --out reports/junit.xml
        env:
          RAILS_ENV: test
          DATABASE_URL: postgres://test:test@localhost:5432/testdb

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: |
            reports/
            tmp/screenshots/
```

---

## §8 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `Capybara::ElementNotFound` | Element not on page or wrong selector | Use `have_css` with `wait:` option; check selector in browser DevTools |
| 2 | Tests pass alone, fail together | Database state leaking between tests | Configure DatabaseCleaner; use `:truncation` for JS tests |
| 3 | `Selenium::WebDriver::Error` | ChromeDriver version mismatch | Use `webdrivers` gem or `setup-chrome` GitHub Action |
| 4 | JavaScript tests fail | Missing `js: true` metadata | Add `js: true` to examples needing JavaScript rendering |
| 5 | `Capybara::Ambiguous` | Multiple elements match selector | Use `within` to scope; use more specific selectors |
| 6 | Screenshot not captured | `capybara-screenshot` not configured | Add `require 'capybara-screenshot/rspec'` to spec_helper |
| 7 | Flaky tests with timing | Default wait time too short | Increase `default_max_wait_time`; use explicit `wait:` parameter |
| 8 | `fill_in` doesn't work with JS forms | React/Vue re-renders clear input | Use `find('#field').set('value')` or `execute_script` |
| 9 | `within` block finds nothing | Container element not visible yet | Wait for container first: `expect(page).to have_css('.container')` |
| 10 | Remote driver connection refused | Selenium server not running | Check Selenium Grid URL; verify container is healthy |
| 11 | Tests slow due to browser startup | New browser per test | Use `before(:all)` for shared browser; use headless mode |
| 12 | `have_content` fails on dynamic text | Content loaded after assertion | Use `have_content(text, wait: 10)` for async content |

---

## §9 Best Practices Checklist

1. Use `have_css` and `have_content` with wait — Capybara auto-waits for matchers
2. Use `within` blocks to scope interactions — avoid ambiguous element matches
3. Use `js: true` only when needed — non-JS tests are faster with Rack driver
4. Use SitePrism Page Objects — keep specs readable and selectors maintainable
5. Use DatabaseCleaner with strategy per context — transaction for unit, truncation for JS
6. Use `capybara-screenshot` — auto-capture on failure for debugging
7. Use `fill_in` by label text — more resilient than CSS selectors
8. Use FactoryBot for test data — realistic, isolated data per test
9. Use `default_max_wait_time` wisely — 10s default, increase for slow APIs
10. Use `find` with `visible: :all` sparingly — prefer testing what users see
11. Use environment variables for config — switch drivers and URLs without code changes
12. Use `current_path` matcher — verify navigation after form submissions
13. Use `accept_alert` / `dismiss_confirm` — handle browser dialogs explicitly
14. Run headless in CI — Chrome headless mode is faster and more reliable
