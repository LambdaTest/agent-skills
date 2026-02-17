# Laravel Dusk — Advanced Patterns & Playbook

## Component & Page Objects

```php
// tests/Browser/Pages/LoginPage.php
class LoginPage extends Page
{
    public function url() { return '/login'; }
    public function assert(Browser $browser) { $browser->assertPathIs($this->url()); }

    public function elements()
    {
        return [
            '@username' => '#email',
            '@password' => '#password',
            '@submit' => 'button[type="submit"]',
        ];
    }

    public function loginAs(Browser $browser, string $email, string $password)
    {
        $browser->type('@username', $email)
                ->type('@password', $password)
                ->click('@submit');
    }
}

// Component
class DatePicker extends Component
{
    public function selector() { return '.date-picker'; }

    public function selectDate(Browser $browser, string $date)
    {
        $browser->click('.trigger')
                ->waitFor('.calendar')
                ->click("[data-date='{$date}']");
    }
}

// Test
class LoginTest extends DuskTestCase
{
    public function test_admin_login(): void
    {
        $this->browse(function (Browser $browser) {
            $browser->visit(new LoginPage)
                    ->loginAs('admin@test.com', 'password')
                    ->assertPathIs('/dashboard')
                    ->assertSee('Welcome');
        });
    }

    // Multiple browsers
    public function test_chat(): void
    {
        $this->browse(function (Browser $first, Browser $second) {
            $first->loginAs(User::find(1))->visit('/chat');
            $second->loginAs(User::find(2))->visit('/chat');
            $first->type('#message', 'Hello!')->press('Send');
            $second->waitForText('Hello!');
        });
    }
}
```

## Authentication Helpers

```php
public function test_authenticated_page(): void
{
    $user = User::factory()->create();
    $this->browse(function (Browser $browser) use ($user) {
        $browser->loginAs($user)
                ->visit('/settings')
                ->assertSee($user->name);
    });
}
```

## Anti-Patterns

- ❌ Raw CSS selectors in tests — use `dusk="name"` attributes and `@name` syntax
- ❌ `$browser->pause(3000)` — use `waitFor`, `waitForText`, `waitUntilMissing`
- ❌ Database state from previous tests — use `DatabaseMigrations` trait
- ❌ Missing `->screenshot()` on failure — add to `tearDown` for debugging
