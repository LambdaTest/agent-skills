# Capybara — Advanced Patterns & Playbook

## Page Object with Site Prism

```ruby
class LoginPage < SitePrism::Page
  set_url "/login"

  element :email_field, "#email"
  element :password_field, "#password"
  element :submit_button, "button[type='submit']"
  element :error_message, ".alert-danger"

  def login(email, password)
    email_field.set(email)
    password_field.set(password)
    submit_button.click
  end
end

class DashboardPage < SitePrism::Page
  set_url "/dashboard"
  section :nav, NavigationSection, ".navbar"
  elements :cards, ".dashboard-card"

  def card_titles
    cards.map { |c| c.find("h3").text }
  end
end

# Test
RSpec.describe "Login", type: :feature do
  let(:login_page) { LoginPage.new }

  it "logs in successfully" do
    login_page.load
    login_page.login("admin@test.com", "password")
    expect(page).to have_current_path("/dashboard")
  end
end
```

## Advanced Matchers & Finders

```ruby
# Scoped finders
within("#user-form") do
  fill_in "Name", with: "Alice"
  select "Admin", from: "Role"
  check "Active"
  click_button "Save"
end

# Custom matchers
expect(page).to have_css(".product", count: 5)
expect(page).to have_css(".product", minimum: 1, maximum: 10)
expect(page).to have_selector(:xpath, "//table//tr", count: 3)
expect(page).to have_text("Welcome", wait: 10)

# JavaScript evaluation
total = page.evaluate_script("document.querySelectorAll('.item').length")
expect(total).to eq(5)

# Accept/dismiss dialogs
accept_confirm("Are you sure?") { click_link "Delete" }
dismiss_prompt { click_link "Rename" }
```

## Driver Configuration

```ruby
# spec/support/capybara.rb
Capybara.configure do |config|
  config.default_max_wait_time = 10
  config.default_normalize_ws = true
  config.save_path = "tmp/capybara"
  config.automatic_label_click = true
end

Capybara.register_driver :headless_chrome do |app|
  options = Selenium::WebDriver::Chrome::Options.new
  options.add_argument("--headless=new")
  options.add_argument("--no-sandbox")
  options.add_argument("--window-size=1920,1080")
  Capybara::Selenium::Driver.new(app, browser: :chrome, options: options)
end

Capybara.javascript_driver = :headless_chrome
```

## Anti-Patterns

- ❌ `sleep(5)` — use Capybara's built-in waiting: `have_css`, `have_text`
- ❌ `find(".class").click` without waiting — use `click_link`/`click_button` (auto-waits)
- ❌ `page.html.include?("text")` — use `have_text` matcher (handles async)
- ❌ XPath selectors when CSS suffices — CSS is more readable
