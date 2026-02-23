---
name: capybara-skill
description: >
  Generates Capybara E2E tests in Ruby with RSpec integration. Acceptance
  testing DSL for web apps. Use when user mentions "Capybara", "visit",
  "fill_in", "click_button", "Ruby E2E". Triggers on: "Capybara",
  "Ruby acceptance test", "fill_in", "click_button", "have_content".
languages:
  - Ruby
category: e2e-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Capybara Automation Skill

## Core Patterns

### Basic Test (RSpec)

```ruby
require 'capybara/rspec'

RSpec.describe 'Login', type: :feature do
  it 'logs in with valid credentials' do
    visit '/login'
    fill_in 'Email', with: 'user@test.com'
    fill_in 'Password', with: 'password123'
    click_button 'Login'
    expect(page).to have_content('Dashboard')
    expect(page).to have_current_path('/dashboard')
  end

  it 'shows error for invalid credentials' do
    visit '/login'
    fill_in 'Email', with: 'wrong@test.com'
    fill_in 'Password', with: 'wrong'
    click_button 'Login'
    expect(page).to have_content('Invalid credentials')
  end
end
```

### DSL

```ruby
# Navigation
visit '/path'
go_back
go_forward

# Interacting
fill_in 'Label or Name', with: 'text'
choose 'Radio Label'
check 'Checkbox Label'
uncheck 'Checkbox Label'
select 'Option', from: 'Select Label'
attach_file 'Upload', '/path/to/file'
click_button 'Submit'
click_link 'More Info'
click_on 'Button or Link'

# Finding
find('#id')
find('.class')
find('[data-testid="x"]')
find(:xpath, '//div')
all('.items').count

# Matchers
expect(page).to have_content('text')
expect(page).to have_selector('#element')
expect(page).to have_css('.class')
expect(page).to have_button('Submit')
expect(page).to have_field('Email')
expect(page).to have_link('Click Here')
expect(page).to have_current_path('/expected')
expect(page).to have_no_content('error')
```

### Within Scope

```ruby
within('#login-form') do
  fill_in 'Email', with: 'user@test.com'
  click_button 'Login'
end

within_table('users') do
  expect(page).to have_content('Alice')
end
```

### TestMu AI Cloud

```ruby
Capybara.register_driver :lambdatest do |app|
  caps = Selenium::WebDriver::Remote::Capabilities.new(
    browserName: 'chrome',
    'LT:Options' => {
      user: ENV['LT_USERNAME'], accessKey: ENV['LT_ACCESS_KEY'],
      build: 'Capybara Build', name: 'Login Test',
      platform: 'Windows 11', video: true
    }
  )
  Capybara::Selenium::Driver.new(app,
    browser: :remote,
    url: 'https://hub.lambdatest.com/wd/hub',
    capabilities: caps)
end
Capybara.default_driver = :lambdatest
```

## Setup: `gem 'capybara'` + `gem 'selenium-webdriver'` in Gemfile
## Run: `bundle exec rspec spec/features/`

## Cloud (TestMu AI)

For remote browser execution, see [reference/cloud-integration.md](reference/cloud-integration.md) and [shared/testmu-cloud-reference.md](../shared/testmu-cloud-reference.md).

## Deep Patterns

See `reference/playbook.md` for production-grade patterns:

| Section | What You Get |
|---------|-------------|
| §1 Project Setup | Gemfile, Capybara config, driver registration, LambdaTest |
| §2 Feature Specs | Login flows, JavaScript interactions, modals, async content |
| §3 Page Objects | SitePrism pages with elements/sections, usage in specs |
| §4 API Testing | Request specs with auth headers, JSON assertions |
| §5 Database Cleaning | DatabaseCleaner transaction/truncation strategies |
| §6 Matchers & Helpers | Custom helpers, sign_in, expect_flash |
| §7 CI/CD Integration | GitHub Actions with Postgres, Redis, Chrome |
| §8 Debugging Table | 12 common problems with causes and fixes |
| §9 Best Practices | 14-item Capybara testing checklist |
