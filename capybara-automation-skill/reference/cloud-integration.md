# Capybara — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

Capybara uses the Selenium driver for remote browsers. Configure the default driver to use TestMu AI Hub:

## Configuration

```ruby
# spec/spec_helper.rb or spec/rails_helper.rb
require 'capybara/rspec'
require 'selenium-webdriver'

Capybara.register_driver :lambdatest do |app|
  caps = Selenium::WebDriver::Remote::Capabilities.new
  caps['browserName'] = 'Chrome'
  caps['browserVersion'] = 'latest'
  caps['LT:Options'] = {
    'platform' => 'Windows 11',
    'build' => 'Capybara Build',
    'name' => 'Capybara Test',
    'user' => ENV['LT_USERNAME'],
    'accessKey' => ENV['LT_ACCESS_KEY'],
    'video' => true,
    'network' => true
  }

  Capybara::Selenium::Driver.new(
    app,
    browser: :remote,
    url: "https://#{ENV['LT_USERNAME']}:#{ENV['LT_ACCESS_KEY']}@hub.lambdatest.com/wd/hub",
    desired_capabilities: caps
  )
end

# Use with: Capybara.default_driver = :lambdatest
# Or: SCREENSHOT_DRIVER=lambdatest bundle exec rspec
Capybara.default_driver = ENV['LT_USERNAME'] ? :lambdatest : :selenium_chrome
```

## Run on Cloud

```bash
export LT_USERNAME=your_username
export LT_ACCESS_KEY=your_access_key
bundle exec rspec spec/features/
```

For capability options (tunnel, geoLocation, platforms), see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
