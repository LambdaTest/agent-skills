# Laravel Dusk — Advanced Playbook

## §1 — Project Setup

### Installation
```bash
# Install Dusk
composer require laravel/dusk --dev

# Install Dusk scaffolding
php artisan dusk:install

# Install ChromeDriver
php artisan dusk:chrome-driver --detect
```

### Project Structure
```
project/
├── tests/
│   └── Browser/
│       ├── LoginTest.php
│       ├── CheckoutTest.php
│       ├── DashboardTest.php
│       ├── Components/
│       │   ├── DatePickerComponent.php
│       │   └── ModalComponent.php
│       ├── Pages/
│       │   ├── LoginPage.php
│       │   ├── DashboardPage.php
│       │   └── CheckoutPage.php
│       └── screenshots/
│           └── .gitkeep
├── .env.dusk.local
├── .env.dusk.testing
└── DuskTestCase.php
```

### Environment Configuration
```env
# .env.dusk.local
APP_URL=http://localhost:8001
DB_DATABASE=testing_dusk
DB_CONNECTION=mysql
SESSION_DRIVER=file
MAIL_MAILER=array
QUEUE_CONNECTION=sync
```

### DuskTestCase Customization
```php
<?php

namespace Tests;

use Facebook\WebDriver\Chrome\ChromeOptions;
use Facebook\WebDriver\Remote\DesiredCapabilities;
use Facebook\WebDriver\Remote\RemoteWebDriver;
use Laravel\Dusk\TestCase as BaseTestCase;

abstract class DuskTestCase extends BaseTestCase
{
    protected function driver(): RemoteWebDriver
    {
        $options = (new ChromeOptions)->addArguments(collect([
            $this->shouldBeHeadless() ? '--headless=new' : null,
            '--disable-gpu',
            '--no-sandbox',
            '--window-size=1920,1080',
            '--disable-search-engine-choice-screen',
        ])->filter()->all());

        return RemoteWebDriver::create(
            $_ENV['DUSK_DRIVER_URL'] ?? env('DUSK_DRIVER_URL', 'http://localhost:9515'),
            DesiredCapabilities::chrome()->setCapability(
                ChromeOptions::CAPABILITY, $options
            )
        );
    }

    protected function shouldBeHeadless(): bool
    {
        return isset($_SERVER['DUSK_HEADLESS']) ||
               isset($_ENV['DUSK_HEADLESS']);
    }
}
```

---

## §2 — Browser Test Patterns

### Login & Authentication
```php
<?php

namespace Tests\Browser;

use App\Models\User;
use Laravel\Dusk\Browser;
use Tests\DuskTestCase;
use Illuminate\Foundation\Testing\DatabaseMigrations;

class LoginTest extends DuskTestCase
{
    use DatabaseMigrations;

    public function testSuccessfulLogin(): void
    {
        $user = User::factory()->create([
            'email' => 'test@example.com',
        ]);

        $this->browse(function (Browser $browser) use ($user) {
            $browser->visit('/login')
                ->waitForText('Sign In')
                ->type('email', $user->email)
                ->type('password', 'password')
                ->press('Sign In')
                ->waitForLocation('/dashboard')
                ->assertPathIs('/dashboard')
                ->assertSee('Welcome');
        });
    }

    public function testLoginValidationErrors(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/login')
                ->press('Sign In')
                ->waitForText('The email field is required')
                ->assertSee('The email field is required')
                ->assertSee('The password field is required');
        });
    }

    public function testLoginRateLimiting(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/login');

            for ($i = 0; $i < 6; $i++) {
                $browser->type('email', 'wrong@example.com')
                    ->type('password', 'wrongpassword')
                    ->press('Sign In')
                    ->pause(500);
            }

            $browser->assertSee('Too many login attempts');
        });
    }

    public function testLogout(): void
    {
        $user = User::factory()->create();

        $this->browse(function (Browser $browser) use ($user) {
            $browser->loginAs($user)
                ->visit('/dashboard')
                ->click('@user-menu')
                ->waitFor('@logout-button')
                ->click('@logout-button')
                ->waitForLocation('/login')
                ->assertPathIs('/login')
                ->assertGuest();
        });
    }
}
```

### Form Interactions
```php
class FormTest extends DuskTestCase
{
    use DatabaseMigrations;

    public function testCompleteProfileForm(): void
    {
        $user = User::factory()->create();

        $this->browse(function (Browser $browser) use ($user) {
            $browser->loginAs($user)
                ->visit('/profile/edit')
                ->type('name', 'Updated Name')
                ->type('bio', 'This is my updated bio text')
                ->select('timezone', 'America/New_York')
                ->check('notifications_email')
                ->uncheck('notifications_sms')
                ->radio('theme', 'dark')
                ->attach('avatar', __DIR__.'/fixtures/avatar.jpg')
                ->press('Save Changes')
                ->waitForText('Profile updated')
                ->assertSee('Profile updated')
                ->assertInputValue('name', 'Updated Name')
                ->assertSelected('timezone', 'America/New_York')
                ->assertChecked('notifications_email')
                ->assertNotChecked('notifications_sms')
                ->assertRadioSelected('theme', 'dark');
        });
    }

    public function testMultiStepWizard(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/onboarding')
                // Step 1: Personal info
                ->waitForText('Step 1')
                ->type('first_name', 'Jane')
                ->type('last_name', 'Doe')
                ->press('Next')
                // Step 2: Preferences
                ->waitForText('Step 2')
                ->select('industry', 'technology')
                ->check('interests[]', 'testing')
                ->check('interests[]', 'devops')
                ->press('Next')
                // Step 3: Confirmation
                ->waitForText('Step 3')
                ->assertSee('Jane Doe')
                ->assertSee('technology')
                ->press('Complete')
                ->waitForLocation('/dashboard')
                ->assertSee('Welcome, Jane');
        });
    }
}
```

### Multiple Browsers (Concurrent Users)
```php
class CollaborationTest extends DuskTestCase
{
    use DatabaseMigrations;

    public function testRealTimeCollaboration(): void
    {
        $userA = User::factory()->create(['name' => 'Alice']);
        $userB = User::factory()->create(['name' => 'Bob']);

        $this->browse(function (Browser $alice, Browser $bob) use ($userA, $userB) {
            // Alice creates a document
            $alice->loginAs($userA)
                ->visit('/documents/create')
                ->type('title', 'Shared Document')
                ->press('Create')
                ->waitForText('Document created');

            // Bob opens the same document
            $bob->loginAs($userB)
                ->visit('/documents/1')
                ->assertSee('Shared Document');

            // Alice makes an edit
            $alice->type('@editor', 'Hello from Alice')
                ->pause(1000);

            // Bob sees the edit
            $bob->waitForText('Hello from Alice')
                ->assertSee('Hello from Alice');
        });
    }
}
```

---

## §3 — Page Objects

### Page Object Definition
```php
<?php

namespace Tests\Browser\Pages;

use Laravel\Dusk\Browser;
use Laravel\Dusk\Page;

class LoginPage extends Page
{
    public function url(): string
    {
        return '/login';
    }

    public function assert(Browser $browser): void
    {
        $browser->assertPathIs($this->url())
            ->waitFor('@login-form');
    }

    public function elements(): array
    {
        return [
            '@email'    => 'input[name="email"]',
            '@password' => 'input[name="password"]',
            '@submit'   => 'button[type="submit"]',
            '@error'    => '[role="alert"]',
            '@remember' => 'input[name="remember"]',
        ];
    }

    public function loginAs(Browser $browser, string $email, string $password): void
    {
        $browser->type('@email', $email)
            ->type('@password', $password)
            ->press('@submit');
    }

    public function assertHasError(Browser $browser, string $message): void
    {
        $browser->waitFor('@error')
            ->assertSeeIn('@error', $message);
    }
}
```

### Dashboard Page Object
```php
class DashboardPage extends Page
{
    public function url(): string
    {
        return '/dashboard';
    }

    public function assert(Browser $browser): void
    {
        $browser->assertPathIs($this->url())
            ->waitFor('@dashboard-content');
    }

    public function elements(): array
    {
        return [
            '@welcome'     => '[data-testid="welcome"]',
            '@stats'       => '[data-testid="stats-grid"]',
            '@stat-card'   => '[data-testid="stat-card"]',
            '@recent'      => '[data-testid="recent-items"]',
            '@user-menu'   => '[data-testid="user-menu"]',
            '@nav'         => 'nav[data-testid="main-nav"]',
        ];
    }

    public function navigateTo(Browser $browser, string $section): void
    {
        $browser->within('@nav', function (Browser $nav) use ($section) {
            $nav->clickLink($section);
        });
    }

    public function getStatValue(Browser $browser, string $label): string
    {
        return $browser->text("[data-testid='stat-{$label}'] .value");
    }
}
```

### Using Page Objects in Tests
```php
class DashboardTest extends DuskTestCase
{
    use DatabaseMigrations;

    public function testDashboardAccess(): void
    {
        $user = User::factory()->create();

        $this->browse(function (Browser $browser) use ($user) {
            $browser->loginAs($user)
                ->visit(new DashboardPage)
                ->assertSeeIn('@welcome', 'Welcome')
                ->within('@stats', function (Browser $stats) {
                    $stats->assertVisible('@stat-card');
                });
        });
    }

    public function testLoginThenDashboard(): void
    {
        $user = User::factory()->create();

        $this->browse(function (Browser $browser) use ($user) {
            $browser->visit(new LoginPage)
                ->loginAs($user->email, 'password')
                ->on(new DashboardPage)
                ->assertSeeIn('@welcome', $user->name);
        });
    }
}
```

---

## §4 — Components

### Reusable Component
```php
<?php

namespace Tests\Browser\Components;

use Laravel\Dusk\Browser;
use Laravel\Dusk\Component as BaseComponent;

class DatePickerComponent extends BaseComponent
{
    public function selector(): string
    {
        return '[data-testid="date-picker"]';
    }

    public function assert(Browser $browser): void
    {
        $browser->assertVisible($this->selector());
    }

    public function elements(): array
    {
        return [
            '@input'     => 'input.date-input',
            '@calendar'  => '.calendar-popup',
            '@prev-month'=> '.prev-month',
            '@next-month'=> '.next-month',
            '@day'       => '.calendar-day',
            '@today'     => '.calendar-day.today',
        ];
    }

    public function selectDate(Browser $browser, string $date): void
    {
        $browser->click('@input')
            ->waitFor('@calendar')
            ->within('@calendar', function (Browser $cal) use ($date) {
                $cal->click("[data-date='{$date}']");
            });
    }

    public function selectToday(Browser $browser): void
    {
        $browser->click('@input')
            ->waitFor('@calendar')
            ->click('@today');
    }
}

class ModalComponent extends BaseComponent
{
    public string $name;

    public function __construct(string $name = 'modal')
    {
        $this->name = $name;
    }

    public function selector(): string
    {
        return "[data-testid='{$this->name}']";
    }

    public function assert(Browser $browser): void
    {
        $browser->waitFor($this->selector());
    }

    public function elements(): array
    {
        return [
            '@title'   => '.modal-title',
            '@body'    => '.modal-body',
            '@close'   => '.modal-close',
            '@confirm' => '.modal-confirm',
            '@cancel'  => '.modal-cancel',
        ];
    }

    public function confirm(Browser $browser): void
    {
        $browser->click('@confirm')
            ->waitUntilMissing($this->selector());
    }

    public function cancel(Browser $browser): void
    {
        $browser->click('@cancel')
            ->waitUntilMissing($this->selector());
    }
}
```

### Using Components
```php
class BookingTest extends DuskTestCase
{
    public function testSelectDatesAndConfirm(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->loginAs(User::factory()->create())
                ->visit('/bookings/create')
                ->within(new DatePickerComponent, function (Browser $picker) {
                    $picker->selectDate('2025-03-15');
                })
                ->press('Book Now')
                ->within(new ModalComponent('confirm-modal'), function (Browser $modal) {
                    $modal->assertSeeIn('@title', 'Confirm Booking')
                        ->confirm();
                })
                ->waitForText('Booking confirmed');
        });
    }
}
```

---

## §5 — Advanced Interactions

### JavaScript Execution
```php
class AdvancedTest extends DuskTestCase
{
    public function testScrollAndLazyLoad(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/products')
                ->waitFor('[data-testid="product-grid"]')
                ->assertVisible('[data-testid="product-card"]');

            // Scroll to bottom to trigger lazy load
            $browser->script('window.scrollTo(0, document.body.scrollHeight)');
            $browser->pause(1000);

            // Verify more items loaded
            $initialCount = count($browser->elements('[data-testid="product-card"]'));
            $browser->script('window.scrollTo(0, document.body.scrollHeight)');
            $browser->pause(1000);

            $newCount = count($browser->elements('[data-testid="product-card"]'));
            $this->assertGreaterThan($initialCount, $newCount);
        });
    }

    public function testLocalStorageInteraction(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/settings');

            // Set localStorage value
            $browser->script("localStorage.setItem('theme', 'dark')");
            $browser->refresh();

            // Verify theme applied
            $theme = $browser->script("return localStorage.getItem('theme')");
            $this->assertEquals('dark', $theme[0]);
        });
    }

    public function testDragAndDrop(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->loginAs(User::factory()->create())
                ->visit('/kanban')
                ->waitFor('[data-testid="board"]')
                ->drag('[data-testid="card-1"]', '[data-testid="column-done"]')
                ->pause(500)
                ->within('[data-testid="column-done"]', function (Browser $col) {
                    $col->assertSee('Task 1');
                });
        });
    }
}
```

### Waiting Strategies
```php
class WaitingTest extends DuskTestCase
{
    public function testVariousWaitStrategies(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/dashboard');

            // Wait for element to appear
            $browser->waitFor('[data-testid="loaded"]', 10);

            // Wait for text
            $browser->waitForText('Dashboard loaded', 5);

            // Wait until element disappears
            $browser->waitUntilMissing('.loading-spinner');

            // Wait for specific condition
            $browser->waitUsing(10, 500, function () use ($browser) {
                return count($browser->elements('.data-row')) >= 5;
            }, 'Waiting for at least 5 data rows');

            // Wait for JavaScript expression
            $browser->waitUntil('window.appReady === true', 15);

            // Wait for route (Vue/React SPA)
            $browser->waitForRoute('dashboard.index');

            // Wait for reload
            $browser->waitForReload(function (Browser $browser) {
                $browser->press('Refresh');
            });
        });
    }
}
```

---

## §6 — Database & Test Data

### Database Strategies
```php
class DataTest extends DuskTestCase
{
    use DatabaseMigrations; // Recommended for Dusk

    public function testWithSeededData(): void
    {
        // Seed specific data
        $this->seed(\Database\Seeders\ProductSeeder::class);

        $this->browse(function (Browser $browser) {
            $browser->loginAs(User::factory()->create(['role' => 'admin']))
                ->visit('/admin/products')
                ->assertSee('Seeded Product 1');
        });
    }

    public function testWithFactoryRelationships(): void
    {
        $user = User::factory()
            ->has(Order::factory()->count(3)->has(
                OrderItem::factory()->count(2)
            ))
            ->create();

        $this->browse(function (Browser $browser) use ($user) {
            $browser->loginAs($user)
                ->visit('/orders')
                ->waitFor('[data-testid="order-list"]')
                ->assertPresent('[data-testid="order-row"]');

            $orderCount = count($browser->elements('[data-testid="order-row"]'));
            $this->assertEquals(3, $orderCount);
        });
    }
}
```

### Screenshots & Console Logs
```php
class DebugTest extends DuskTestCase
{
    public function testWithScreenshot(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/complex-page')
                ->screenshot('before-interaction')
                ->click('@submit')
                ->pause(1000)
                ->screenshot('after-interaction');
        });
    }

    public function testWithConsoleLogs(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit('/spa')
                ->waitForText('Loaded');

            $logs = $browser->driver->manage()->getLog('browser');
            foreach ($logs as $log) {
                if ($log['level'] === 'SEVERE') {
                    $this->fail("Console error: {$log['message']}");
                }
            }
        });
    }
}
```

---

## §7 — LambdaTest Integration

### Remote Driver Configuration
```php
abstract class LambdaTestDuskTestCase extends DuskTestCase
{
    protected function driver(): RemoteWebDriver
    {
        $capabilities = DesiredCapabilities::chrome();

        $chromeOptions = new ChromeOptions();
        $chromeOptions->setPlatformName('Windows 11');
        $chromeOptions->setBrowserVersion('latest');

        $ltOptions = [
            'project'  => 'Laravel Dusk',
            'build'    => 'dusk-' . env('BUILD_NUMBER', 'local'),
            'name'     => $this->getName(),
            'console'  => true,
            'network'  => true,
            'visual'   => true,
            'w3c'      => true,
        ];
        $chromeOptions->setCapability('LT:Options', $ltOptions);
        $capabilities->setCapability(ChromeOptions::CAPABILITY, $chromeOptions);

        return RemoteWebDriver::create(
            'https://' . env('LT_USERNAME') . ':' . env('LT_ACCESS_KEY') .
                '@hub.lambdatest.com/wd/hub',
            $capabilities,
            60000, // Connection timeout
            90000  // Request timeout
        );
    }
}
```

---

## §8 — CI/CD Integration

### GitHub Actions
```yaml
name: Laravel Dusk Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  dusk-tests:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: password
          MYSQL_DATABASE: testing_dusk
        ports: ['3306:3306']
        options: >-
          --health-cmd "mysqladmin ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis
        ports: ['6379:6379']

    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: '8.3'
          extensions: dom, curl, mbstring, zip, pdo, mysql, gd
          coverage: none

      - name: Install dependencies
        run: composer install --no-interaction --prefer-dist

      - name: Prepare environment
        run: |
          cp .env.dusk.testing .env
          php artisan key:generate
          php artisan migrate --seed

      - name: Setup Chrome
        uses: browser-actions/setup-chrome@latest
        with:
          chrome-version: stable

      - name: Start ChromeDriver
        run: |
          chromedriver --port=9515 &
          sleep 2

      - name: Start application
        run: |
          php artisan serve --port=8001 &
          sleep 3
        env:
          APP_URL: http://localhost:8001

      - name: Run Dusk tests
        run: php artisan dusk --env=testing
        env:
          APP_URL: http://localhost:8001
          DUSK_HEADLESS: true

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: dusk-screenshots
          path: tests/Browser/screenshots/

      - name: Upload console logs
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: dusk-console
          path: tests/Browser/console/
```

### CLI Commands
```bash
# Run all Dusk tests
php artisan dusk

# Run specific test file
php artisan dusk tests/Browser/LoginTest.php

# Run specific method
php artisan dusk --filter testSuccessfulLogin

# Run with specific group
php artisan dusk --group smoke

# Run in specific environment
php artisan dusk --env=staging

# Run without stopping on first failure
php artisan dusk --stop-on-failure

# Update ChromeDriver
php artisan dusk:chrome-driver --detect
```

---

## §9 — Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `Facebook\WebDriver\Exception\SessionNotCreatedException` | ChromeDriver version mismatch with Chrome | Run `php artisan dusk:chrome-driver --detect` to auto-detect and install matching version |
| 2 | Test works locally, fails in CI | Missing `DUSK_HEADLESS` env or Chrome not installed | Set `DUSK_HEADLESS=true`; ensure Chrome and ChromeDriver are installed in CI |
| 3 | `Element not interactable` | Element hidden, overlapped, or not in viewport | Add `waitFor()` before interaction; use `scrollIntoView` via `script()`; check for overlapping modals |
| 4 | `loginAs()` doesn't work | Session/cookie domain mismatch with `APP_URL` | Ensure `.env.dusk.local` `APP_URL` matches the served URL exactly (port included) |
| 5 | Database state leaks between tests | Not using `DatabaseMigrations` trait | Add `use DatabaseMigrations` to test class; ensure `.env.dusk` points to separate test database |
| 6 | Screenshots empty/blank | Page not loaded when screenshot taken | Add `pause(500)` or `waitFor()` before `screenshot()`; check if page errored |
| 7 | `waitForText` times out on visible text | Text inside shadow DOM or iframe | Use `withinFrame()` for iframes; for shadow DOM use `script()` to access content |
| 8 | Multiple browser test fails | Shared session state between Browser instances | Each `Browser` instance gets its own session; avoid relying on server-side session sharing |
| 9 | `assertSee` passes but text not visible | Text exists in DOM but hidden with CSS | Use `assertVisible` to check display state; `assertSee` only checks DOM text content |
| 10 | File upload fails | Path is relative or file doesn't exist | Use `__DIR__.'/fixtures/file.jpg'` for absolute path; verify file exists in test directory |
| 11 | SPA navigation not detected | `assertPathIs` runs before client-side routing completes | Use `waitForLocation('/path')` instead of `assertPathIs` for SPA route changes |
| 12 | `.env.dusk.local` not loaded | Wrong filename or missing from project root | File must be `.env.dusk.{environment}` — e.g., `.env.dusk.local` for local; check `APP_ENV` matches |

---

## §10 — Best Practices Checklist

1. Use `DatabaseMigrations` trait — ensures clean state for every test
2. Use `.env.dusk.local` with separate test database — never run Dusk against production data
3. Prefer `dusk="selector"` attributes over CSS classes — resilient to styling changes
4. Use `loginAs($user)` to skip login UI for non-authentication tests
5. Use `waitFor()` / `waitForText()` over `pause()` — deterministic waits are faster and more reliable
6. Create page objects for reusable page interactions — keeps tests DRY and readable
7. Create components for reusable UI elements — date pickers, modals, dropdowns
8. Take screenshots at key steps during debugging — `$browser->screenshot('step-name')`
9. Use `@group` annotations for selective test execution — `@group smoke`, `@group checkout`
10. Keep Dusk tests for user journeys — use Feature/Unit tests for business logic
11. Run `php artisan dusk:chrome-driver --detect` regularly — keeps ChromeDriver in sync
12. Handle async content with proper waits — `waitUsing()` for custom conditions
13. Use multiple Browser instances for collaboration tests — not for parallelism
14. Capture console logs on failure — helps debug JavaScript errors in SPA tests
