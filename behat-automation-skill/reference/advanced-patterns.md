# Behat (PHP BDD) — Advanced Patterns & Playbook

## Context with Mink Integration

```php
use Behat\MinkExtension\Context\MinkContext;

class FeatureContext extends MinkContext
{
    private array $testData = [];

    /** @Given I am logged in as :role */
    public function loginAs(string $role): void
    {
        $creds = $this->getCredentials($role);
        $this->visit('/login');
        $this->fillField('email', $creds['email']);
        $this->fillField('password', $creds['password']);
        $this->pressButton('Login');
        $this->assertPageContainsText('Dashboard');
    }

    /** @When I create a product with name :name and price :price */
    public function createProduct(string $name, string $price): void
    {
        $this->visit('/products/new');
        $this->fillField('Product Name', $name);
        $this->fillField('Price', $price);
        $this->pressButton('Save');
    }

    /** @Then I should see :count products in the list */
    public function verifyProductCount(int $count): void
    {
        $elements = $this->getSession()->getPage()->findAll('css', '.product-row');
        Assert::assertCount($count, $elements);
    }

    /** @Transform :price */
    public function transformPrice(string $price): float
    {
        return (float) str_replace(['$', ','], '', $price);
    }
}
```

## API Context

```php
class ApiContext implements Context
{
    private Client $client;
    private ?Response $response = null;

    public function __construct(string $baseUrl)
    {
        $this->client = new Client(['base_uri' => $baseUrl]);
    }

    /** @When I send a :method request to :uri with body: */
    public function sendRequest(string $method, string $uri, PyStringNode $body): void
    {
        $this->response = $this->client->request($method, $uri, [
            'json' => json_decode($body->getRaw(), true),
            'http_errors' => false
        ]);
    }

    /** @Then the response status should be :code */
    public function assertStatus(int $code): void
    {
        Assert::assertEquals($code, $this->response->getStatusCode());
    }
}
```

## Configuration

```yaml
# behat.yml
default:
  suites:
    ui:
      contexts: [FeatureContext]
      filters: { tags: "@ui" }
    api:
      contexts: [ApiContext]
      filters: { tags: "@api" }
  extensions:
    Behat\MinkExtension:
      base_url: http://localhost:8080
      sessions:
        default: { selenium2: { browser: chrome } }
```

## Anti-Patterns

- ❌ CSS/XPath selectors in feature files — keep Gherkin business-readable
- ❌ `$this->getSession()->wait(5000)` — use `$this->getSession()->wait(5000, '...')`
- ❌ Monolithic Context class — split into domain-specific contexts
- ❌ Missing `@Transform` for custom types — step defs become brittle
