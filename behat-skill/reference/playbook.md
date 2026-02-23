# Behat — Advanced Playbook

## §1 Project Setup & Configuration

### composer.json
```json
{
  "require-dev": {
    "behat/behat": "^3.14",
    "behat/mink-extension": "^2.3",
    "behat/mink-selenium2-driver": "^1.7",
    "friends-of-behat/mink-browserkit-driver": "^1.6",
    "friends-of-behat/symfony-extension": "^2.5",
    "friends-of-behat/page-object-extension": "^0.3",
    "behatch/contexts": "^3.3"
  }
}
```

### behat.yml
```yaml
default:
  suites:
    ui:
      contexts:
        - App\Tests\Behat\FeatureContext
        - App\Tests\Behat\LoginContext
        - App\Tests\Behat\ApiContext
        - Behatch\Context\JsonContext
      filters:
        tags: "@ui"
    api:
      contexts:
        - App\Tests\Behat\ApiContext
        - Behatch\Context\RestContext
        - Behatch\Context\JsonContext
      filters:
        tags: "@api"

  extensions:
    Behat\MinkExtension:
      base_url: "https://staging.example.com"
      sessions:
        default:
          selenium2:
            wd_host: "http://localhost:4444/wd/hub"
            capabilities:
              browserName: "chrome"
              goog:chromeOptions:
                args:
                  - "--headless"
                  - "--no-sandbox"
                  - "--disable-dev-shm-usage"
        javascript:
          selenium2:
            wd_host: "http://localhost:4444/wd/hub"

  formatters:
    pretty: true
    junit:
      output_path: reports/junit

staging:
  extensions:
    Behat\MinkExtension:
      base_url: "https://staging.example.com"

production:
  extensions:
    Behat\MinkExtension:
      base_url: "https://www.example.com"
```

### Project Structure
```
tests/
├── Behat/
│   ├── FeatureContext.php
│   ├── LoginContext.php
│   ├── ApiContext.php
│   ├── PageObject/
│   │   ├── LoginPage.php
│   │   └── DashboardPage.php
│   └── Helper/
│       ├── DatabaseHelper.php
│       └── FixtureLoader.php
├── features/
│   ├── login.feature
│   ├── checkout.feature
│   ├── api/
│   │   ├── users.feature
│   │   └── products.feature
│   └── bootstrap/
│       └── FeatureContext.php
└── behat.yml
```

---

## §2 Feature Files — Gherkin Patterns

### UI Feature with Scenario Outline
```gherkin
# features/login.feature
@ui @smoke
Feature: User Authentication
  As a registered user
  I want to log in to my account
  So that I can access the dashboard

  Background:
    Given the database is seeded with test data
    And I am on the login page

  @critical
  Scenario: Successful login with valid credentials
    When I fill in "email" with "user@test.com"
    And I fill in "password" with "ValidPass123"
    And I press "Sign In"
    Then I should see "Welcome back"
    And I should be on the dashboard page
    And I should see my account name "Test User"

  @negative
  Scenario Outline: Failed login with invalid credentials
    When I fill in "email" with "<email>"
    And I fill in "password" with "<password>"
    And I press "Sign In"
    Then I should see the error "<error_message>"
    And I should still be on the login page

    Examples:
      | email            | password     | error_message                |
      | wrong@test.com   | ValidPass123 | Invalid email or password    |
      | user@test.com    | wrong        | Invalid email or password    |
      |                  | ValidPass123 | Email is required            |
      | user@test.com    |              | Password is required         |
      | not-an-email     | ValidPass123 | Please enter a valid email   |

  @security
  Scenario: Account lockout after multiple failed attempts
    When I attempt to login 5 times with wrong credentials
    Then I should see "Account locked"
    And I should see "Try again in 15 minutes"
```

### E2E Feature with Complex Flow
```gherkin
# features/checkout.feature
@ui @e2e
Feature: Product Checkout
  As a customer
  I want to purchase products
  So that I can receive items I need

  @happy-path
  Scenario: Complete purchase with credit card
    Given I am logged in as "customer@test.com"
    And my cart has the following items:
      | product       | quantity | price  |
      | Wireless Mouse| 2        | 29.99  |
      | USB-C Cable   | 1        | 12.99  |
    When I proceed to checkout
    And I fill in the shipping address:
      | field   | value              |
      | street  | 123 Test Lane      |
      | city    | Testville          |
      | zip     | 12345              |
      | country | United States      |
    And I select "Credit Card" as payment method
    And I enter the card details:
      | field       | value              |
      | number      | 4242424242424242   |
      | expiry      | 12/28              |
      | cvv         | 123                |
    And I confirm the order
    Then I should see "Order confirmed"
    And the order total should be "$72.97"
    And I should receive an order confirmation email
```

---

## §3 Context Classes — Step Definitions

### Feature Context with Dependency Injection
```php
<?php
// tests/Behat/FeatureContext.php
namespace App\Tests\Behat;

use Behat\Behat\Context\Context;
use Behat\Behat\Hook\Scope\BeforeScenarioScope;
use Behat\Behat\Hook\Scope\AfterScenarioScope;
use Behat\MinkExtension\Context\MinkContext;
use Behat\Gherkin\Node\TableNode;

class FeatureContext extends MinkContext implements Context
{
    private DatabaseHelper $db;
    private array $scenarioData = [];

    public function __construct(DatabaseHelper $db)
    {
        $this->db = $db;
    }

    /** @Given the database is seeded with test data */
    public function seedDatabase(): void
    {
        $this->db->resetAndSeed();
    }

    /** @Given I am logged in as :email */
    public function loginAs(string $email): void
    {
        $this->visit('/login');
        $this->fillField('email', $email);
        $this->fillField('password', 'TestPass123');
        $this->pressButton('Sign In');
        $this->assertPageContainsText('Dashboard');
    }

    /** @Given my cart has the following items: */
    public function addCartItems(TableNode $table): void
    {
        foreach ($table->getHash() as $row) {
            $this->visit('/products');
            $this->clickLink($row['product']);
            $this->selectOption('quantity', $row['quantity']);
            $this->pressButton('Add to Cart');
            $this->assertPageContainsText('Added to cart');
        }
    }

    /** @When I fill in the shipping address: */
    public function fillShippingAddress(TableNode $table): void
    {
        foreach ($table->getRowsHash() as $field => $value) {
            $this->fillField("shipping_{$field}", $value);
        }
    }

    /** @When I enter the card details: */
    public function fillCardDetails(TableNode $table): void
    {
        foreach ($table->getRowsHash() as $field => $value) {
            $this->fillField("card_{$field}", $value);
        }
    }

    /** @When I attempt to login :count times with wrong credentials */
    public function attemptMultipleLogins(int $count): void
    {
        for ($i = 0; $i < $count; $i++) {
            $this->visit('/login');
            $this->fillField('email', 'user@test.com');
            $this->fillField('password', "wrong-pass-{$i}");
            $this->pressButton('Sign In');
        }
    }

    /** @Then I should see the error :message */
    public function assertErrorMessage(string $message): void
    {
        $this->assertElementContainsText('.error-message', $message);
    }

    /** @Then the order total should be :total */
    public function assertOrderTotal(string $total): void
    {
        $this->assertElementContainsText('.order-total', $total);
    }

    /** @Then I should still be on the login page */
    public function assertOnLoginPage(): void
    {
        $this->assertUrlRegExp('/\/login$/');
    }
}
```

### API Context
```php
<?php
// tests/Behat/ApiContext.php
namespace App\Tests\Behat;

use Behat\Behat\Context\Context;
use Behat\Gherkin\Node\PyStringNode;
use Behat\Gherkin\Node\TableNode;
use GuzzleHttp\Client;
use PHPUnit\Framework\Assert;

class ApiContext implements Context
{
    private Client $client;
    private ?\Psr\Http\Message\ResponseInterface $response = null;
    private string $authToken = '';

    public function __construct(string $baseUrl = 'https://staging.example.com')
    {
        $this->client = new Client(['base_uri' => $baseUrl]);
    }

    /** @Given I am authenticated as :email */
    public function authenticate(string $email): void
    {
        $response = $this->client->post('/api/auth/login', [
            'json' => ['email' => $email, 'password' => 'TestPass123'],
        ]);
        $data = json_decode($response->getBody()->getContents(), true);
        $this->authToken = $data['token'];
    }

    /** @When I send a :method request to :url */
    public function sendRequest(string $method, string $url): void
    {
        $options = ['http_errors' => false];
        if ($this->authToken) {
            $options['headers'] = ['Authorization' => "Bearer {$this->authToken}"];
        }
        $this->response = $this->client->request($method, $url, $options);
    }

    /** @When I send a :method request to :url with body: */
    public function sendRequestWithBody(string $method, string $url, PyStringNode $body): void
    {
        $options = [
            'json' => json_decode($body->getRaw(), true),
            'http_errors' => false,
        ];
        if ($this->authToken) {
            $options['headers'] = ['Authorization' => "Bearer {$this->authToken}"];
        }
        $this->response = $this->client->request($method, $url, $options);
    }

    /** @Then the response status code should be :code */
    public function assertStatusCode(int $code): void
    {
        Assert::assertEquals($code, $this->response->getStatusCode());
    }

    /** @Then the response should contain :key with value :value */
    public function assertJsonField(string $key, string $value): void
    {
        $body = json_decode($this->response->getBody()->getContents(), true);
        Assert::assertEquals($value, $body[$key] ?? null);
    }

    /** @Then the response should contain :count items */
    public function assertItemCount(int $count): void
    {
        $body = json_decode($this->response->getBody()->getContents(), true);
        Assert::assertCount($count, $body['data'] ?? $body);
    }
}
```

---

## §4 Hooks — Lifecycle Management

```php
<?php
// tests/Behat/FeatureContext.php (hooks section)
use Behat\Behat\Hook\Scope\BeforeScenarioScope;
use Behat\Behat\Hook\Scope\AfterScenarioScope;
use Behat\Behat\Hook\Scope\BeforeFeatureScope;
use Behat\Behat\Hook\Scope\AfterStepScope;
use Behat\Testwork\Tester\Result\TestResult;

trait HooksTrait
{
    /** @BeforeSuite */
    public static function setupSuite(): void
    {
        // Run migrations, start services
        exec('php artisan migrate:fresh --seed --env=testing');
    }

    /** @BeforeScenario */
    public function beforeScenario(BeforeScenarioScope $scope): void
    {
        // Reset database state per scenario
        $this->db->beginTransaction();
    }

    /** @AfterScenario */
    public function afterScenario(AfterScenarioScope $scope): void
    {
        // Rollback to clean state
        $this->db->rollback();

        // Screenshot on failure
        if ($scope->getTestResult()->getResultCode() === TestResult::FAILED) {
            $this->saveScreenshot($scope);
        }
    }

    /** @AfterStep */
    public function afterStep(AfterStepScope $scope): void
    {
        // Screenshot after every failed step
        if ($scope->getTestResult()->getResultCode() === TestResult::FAILED) {
            $scenarioTitle = $scope->getFeature()->getTitle();
            $stepText = $scope->getStep()->getText();
            $filename = preg_replace('/[^a-z0-9]+/i', '-', "{$scenarioTitle}-{$stepText}");
            $filepath = "reports/screenshots/{$filename}.png";
            file_put_contents($filepath, $this->getSession()->getScreenshot());
        }
    }

    /** @BeforeScenario @javascript */
    public function beforeJavascriptScenario(): void
    {
        $this->getSession()->resizeWindow(1920, 1080, 'current');
    }

    private function saveScreenshot(AfterScenarioScope $scope): void
    {
        $title = preg_replace('/[^a-z0-9]+/i', '-', $scope->getScenario()->getTitle());
        $filepath = "reports/screenshots/{$title}.png";
        @mkdir(dirname($filepath), 0777, true);
        file_put_contents($filepath, $this->getSession()->getScreenshot());
    }
}
```

---

## §5 Page Objects & Reusable Components

### Page Object Pattern
```php
<?php
// tests/Behat/PageObject/LoginPage.php
namespace App\Tests\Behat\PageObject;

use SensioLabs\Behat\PageObjectExtension\PageObject\Page;

class LoginPage extends Page
{
    protected $path = '/login';

    protected $elements = [
        'email field'    => '#email',
        'password field' => '#password',
        'submit button'  => '#login-submit',
        'error message'  => '.error-message',
        'remember me'    => '#remember-me',
    ];

    public function login(string $email, string $password): void
    {
        $this->fillField('email field', $email);
        $this->fillField('password field', $password);
        $this->pressButton('submit button');
    }

    public function getErrorMessage(): string
    {
        return $this->find('css', '.error-message')->getText();
    }

    public function isRememberMeChecked(): bool
    {
        return $this->find('css', '#remember-me')->isChecked();
    }
}
```

### Using Page Objects in Context
```php
<?php
use App\Tests\Behat\PageObject\LoginPage;
use App\Tests\Behat\PageObject\DashboardPage;

class LoginContext implements Context
{
    private LoginPage $loginPage;
    private DashboardPage $dashboardPage;

    public function __construct(LoginPage $loginPage, DashboardPage $dashboardPage)
    {
        $this->loginPage = $loginPage;
        $this->dashboardPage = $dashboardPage;
    }

    /** @Given I am on the login page */
    public function onLoginPage(): void
    {
        $this->loginPage->open();
    }

    /** @When I login with :email and :password */
    public function login(string $email, string $password): void
    {
        $this->loginPage->login($email, $password);
    }

    /** @Then I should be on the dashboard page */
    public function onDashboard(): void
    {
        Assert::assertTrue($this->dashboardPage->isOpen());
    }
}
```

---

## §6 LambdaTest Cloud Integration

### behat.yml for LambdaTest
```yaml
lambdatest:
  extensions:
    Behat\MinkExtension:
      base_url: "https://staging.example.com"
      sessions:
        default:
          selenium2:
            wd_host: "https://%env(LT_USERNAME)%:%env(LT_ACCESS_KEY)%@hub.lambdatest.com/wd/hub"
            capabilities:
              browserName: "chrome"
              browserVersion: "latest"
              LT:Options:
                platformName: "Windows 11"
                build: "Behat-Build"
                name: "Behat Test"
                video: true
                network: true
                console: true
                visual: true
```

```bash
# Run with LambdaTest profile
vendor/bin/behat --profile=lambdatest --tags=@smoke
```

---

## §7 Custom Formatters & Reporting

### HTML Report Formatter
```php
<?php
// tests/Behat/Formatter/HtmlFormatter.php
namespace App\Tests\Behat\Formatter;

use Behat\Behat\EventDispatcher\Event\ScenarioTested;
use Behat\Behat\EventDispatcher\Event\StepTested;
use Behat\Testwork\Output\Formatter;

class HtmlFormatter implements Formatter
{
    private array $results = [];

    public static function getSubscribedEvents(): array
    {
        return [
            ScenarioTested::AFTER => 'afterScenario',
        ];
    }

    public function afterScenario(ScenarioTested $event): void
    {
        $this->results[] = [
            'title' => $event->getScenario()->getTitle(),
            'status' => $event->getTestResult()->isPassed() ? 'passed' : 'failed',
            'file' => $event->getFeature()->getFile(),
            'line' => $event->getScenario()->getLine(),
        ];
    }
}
```

---

## §8 CI/CD Integration

### GitHub Actions
```yaml
name: Behat Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  behat:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: testdb
        ports: ['3306:3306']
        options: --health-cmd="mysqladmin ping" --health-interval=10s
      selenium:
        image: selenium/standalone-chrome:latest
        ports: ['4444:4444']

    steps:
      - uses: actions/checkout@v4

      - uses: shivammathur/setup-php@v2
        with:
          php-version: '8.3'
          extensions: pdo_mysql, mbstring

      - run: composer install --no-interaction

      - name: Setup database
        run: php artisan migrate --seed --env=testing

      - name: Run Behat
        run: |
          vendor/bin/behat \
            --format=pretty \
            --format=junit --out=reports/junit \
            --colors \
            --strict \
            --tags="~@wip"
        env:
          APP_ENV: testing
          DATABASE_URL: mysql://root:root@127.0.0.1:3306/testdb

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: behat-results
          path: |
            reports/
            screenshots/

      - name: Publish Test Report
        uses: mikepenz/action-junit-report@v4
        if: always()
        with:
          report_paths: reports/junit/*.xml
```

---

## §9 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `Step is not defined` | Missing step definition or regex mismatch | Run `behat --snippets` to generate stubs; check argument types |
| 2 | `Session not started` | Mink not configured or Selenium not running | Check `behat.yml` Mink extension; verify Selenium is accessible |
| 3 | `Element not found` | Element not visible or wrong selector | Use `waitFor()` or `spin()` helper; verify CSS/XPath selector |
| 4 | Tests fail with stale data | Database not reset between scenarios | Use `@BeforeScenario` hook with transaction rollback |
| 5 | Ambiguous step definition | Multiple contexts match same step pattern | Make patterns more specific; use regex with anchors |
| 6 | `@javascript` tag not working | No JavaScript-capable session configured | Configure Selenium session and tag in `behat.yml` |
| 7 | Screenshots blank or wrong | Selenium window not sized | Add `resizeWindow(1920, 1080)` in `@BeforeScenario` |
| 8 | Context injection fails | Service not registered in `behat.yml` | Add context class to suite config; use constructor injection |
| 9 | Scenario Outline data ignored | Wrong `Examples` table format | Ensure pipe-delimited table with header row matching `<placeholders>` |
| 10 | Profile not found | Wrong profile name in command | Verify profile key matches exactly in `behat.yml` |
| 11 | Hooks fire in wrong order | Multiple contexts with same hook | Use `@BeforeScenario` priority parameter; check hook scope |
| 12 | CI tests timeout | Selenium container not ready | Add health check on Selenium port; increase step timeout |

---

## §10 Best Practices Checklist

1. Use Background for common preconditions — keep scenarios focused
2. Use Scenario Outline for parameterized tests — avoid duplicating scenarios
3. Use TableNode for structured test data — tables are readable and maintainable
4. Use separate contexts per domain — LoginContext, CartContext, ApiContext
5. Use Page Objects for UI interaction — abstract selectors from step definitions
6. Use hooks for setup/teardown — `@BeforeScenario`/`@AfterScenario` for isolation
7. Use transaction rollback — fastest database reset between scenarios
8. Use `@wip` tag for work in progress — exclude from CI with `--tags="~@wip"`
9. Use JUnit formatter for CI — parse results with standard test report tools
10. Use screenshot on failure — attach to test reports for debugging
11. Use profiles for environments — switch staging/production with `--profile`
12. Use `--strict` mode in CI — fail on undefined or pending steps
13. Use Gherkin linting — enforce consistent feature file formatting
14. Write scenarios in business language — non-technical stakeholders should understand them
