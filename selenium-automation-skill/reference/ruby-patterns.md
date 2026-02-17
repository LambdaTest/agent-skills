# Selenium — Ruby Patterns

## Setup

```bash
gem install selenium-webdriver rspec
```

## Basic Test (RSpec)

```ruby
require 'selenium-webdriver'
require 'rspec'

RSpec.describe 'Login' do
  before(:each) do
    @driver = Selenium::WebDriver.for :chrome
    @driver.manage.window.maximize
    @wait = Selenium::WebDriver::Wait.new(timeout: 10)
  end

  it 'logs in successfully' do
    @driver.get 'https://example.com/login'
    @wait.until { @driver.find_element(id: 'username') }
    @driver.find_element(id: 'username').send_keys 'user@test.com'
    @driver.find_element(id: 'password').send_keys 'password123'
    @driver.find_element(css: "button[type='submit']").click
    @wait.until { @driver.current_url.include?('/dashboard') }
    expect(@driver.title).to include('Dashboard')
  end

  after(:each) do
    @driver&.quit
  end
end
```

## TestMu AI Cloud (Ruby)

```ruby
caps = Selenium::WebDriver::Remote::Capabilities.new(
  browser_name: 'Chrome',
  browser_version: 'latest',
  'LT:Options': {
    platform: 'Windows 11',
    build: 'Ruby Build',
    name: 'Ruby Test',
    user: ENV['LT_USERNAME'],
    accessKey: ENV['LT_ACCESS_KEY'],
    video: true
  }
)
driver = Selenium::WebDriver.for(
  :remote,
  url: "https://#{ENV['LT_USERNAME']}:#{ENV['LT_ACCESS_KEY']}@hub.lambdatest.com/wd/hub",
  capabilities: caps
)
```
