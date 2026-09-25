<!-- Read this when authoring objective strings — for either `kane-cli run "..."` or step bodies inside a `_test.md`. Owns the full catalog of action verbs, assertion patterns, checkpoint analyze methods (Visual, Textual/DOM, URL, Title, DevTools→Network/Console/Performance/Cookies/localStorage), operators, extraction patterns, direct API calls, chaining, variables, and common pitfalls. The same objective grammar applies to one-shot runs and testmd steps. -->

# Writing Kane-CLI Objectives — Pattern Cookbook

Read this whenever you're constructing the prose objective for `kane-cli run "<objective>"` or the body of a `## Step` in a `_test.md` file. Both surfaces feed the same agent and accept the same grammar.

> **Mobile runs** (`--target emulator|simulator`) share this objective grammar. Checkpoint support depends on platform and app: native network and Android Chrome/debuggable-WebView storage paths exist, but desktop parity and iOS equivalents must be verified. Read `references/mobile.md` for the capability boundary and local/cloud prerequisites.

---

## 1. Anatomy of a good objective

Three properties make an objective reliable:

- **Specific** — name the site, the action, and the field values where they matter.
- **Action-oriented** — lead with a verb (`go to`, `search`, `open`, `fill`, `click`, `verify`).
- **Has a success criterion** — state what "done" looks like so the agent knows when to stop.

Bad → better:

| | Objective |
|---|---|
| ❌ | Test the login page. |
| ✅ | Open `https://app.example.com/login`, log in as `{{tester}}`, and verify the dashboard URL contains `/home`. |

The bad version leaves "test" undefined and gives the agent no end state. The better version names the URL, the credentials, and the assertion that closes the loop.

Two rules turn those properties into a flow that replays reliably.

### 1.1 End every flow in a terminal assertion

Close each objective with a claim about the resulting **page state** — not a bare `submit`, not `confirm the dialog`. A closing assertion is what a replay checks: with it, the run passes or fails on the real end state; without it, "done" only means the agent believed it finished.

```text
❌ Add a laptop to the cart
✅ Add a laptop to the cart, then verify the cart shows 1 item
```

If an objective has several phases (log in, then search, then check out), **each phase ends in its own assertion** — an intermediate phase with no check runs unverified, and a replay can't tell you which phase drifted.

**The closing assertion is a look, not a trip.** Phrase it as a claim about what is on screen once the last action completes, so the agent verifies it without clicking, navigating, scrolling, or typing anywhere else. If the evidence lives somewhere else (Order History, the cart, a details drawer), add the action that gets there as its own step, then assert.

```text
❌ Place the order, then verify it succeeded by checking that it appears in Order History
✅ Place the order, open Order History, then verify the newest order shows "Processing"
```

The ❌ version hides an action inside a check. The agent has to find its own way to Order History on every run, so the route can differ between runs and is never a step you can read or fix. The ✅ version keeps the route in the actions and leaves the assertion a pure observation of the page it lands on.

Two things look like assertions but are not:

- **A UI-commit "confirm" is an action, not a check.** `confirm the dialog` / `click OK to confirm` presses a control; it verifies nothing about the outcome. Follow it with a real check: `… then verify the confirmation reads "Order placed"`.
- **Don't assert the trigger.** `verify the Submit button is visible` fails exactly when the action worked — the control disappears on success. Assert the **outcome**, never the control that caused it.

### 1.2 Intent for the actions, literal for the data

Phrase actions as **goals**, not click-by-click scripts. A goal-level step lets the run absorb a new consent popup or a reordered form; a fixed click sequence is pinned to a layout that may have changed.

```text
❌ Click the email field, type alice@x.com, click the password field, type hunter2, click Sign in
✅ Log in with {{user}} / {{password}}, then verify the account menu shows "{{user}}"
```

Keep exact values — credentials, search terms, prices, URLs — **literal, or lifted into `{{variables}}`** (§6). Intent for the verbs; literal or variable for the payloads.

For an expected-but-optional branch (a cookie banner that only *sometimes* appears), author it as a conditional (§7) rather than assuming it away or hard-scripting it as an unconditional step.

**The shape of a good step:** an intent action carrying literal data, then a verify of an observable end state —

```text
Search for "{{query}}" and open the first result, then verify the product title contains "{{query}}"
```

---

## 2. Action verbs — quick catalog

Reference list. Use these in your prose; the agent recognizes them all.

| Category | Verbs |
|---|---|
| **Navigation** | go to, open, navigate to, visit, reload, go back, switch to tab/window |
| **Input** | type, fill, enter, paste, clear, select (dropdown), check (checkbox), uncheck, toggle |
| **Click/hover** | click, double-click, right-click, hover, long-press |
| **Scroll/drag** | scroll to, scroll down/up, drag to, drop on |
| **Wait** | wait for, wait until, pause for |
| **File** | upload, attach, download |
| **Cookies** | set cookie name=value, delete the X cookie, clear all cookies |
| **localStorage** | set localStorage key=value, delete the X key from localStorage, clear localStorage |
| **Clipboard** | write X to the clipboard, paste from the clipboard, clear the clipboard |
| **Misc** | dismiss, accept dialog, switch frame, take screenshot |

Always include a **starting URL** somewhere in the first action verb if the agent needs to navigate. Never assume the agent knows where to start.

Browser-state notes:
- **Cookies**: values accept `{{variables}}`. A cookie without a domain applies to the current page's site — navigate first. Reload after setting if the page must pick it up.
- **localStorage**: per-site — navigate to the target site before setting. Reload if the app only reads storage on load.
- **Clipboard**: the run uses an **isolated test clipboard** — your real OS clipboard is never read or written. Site Copy buttons are captured into it automatically. To paste: click/focus the target field first, then say paste (Ctrl/Cmd+V works too). Text and images both paste.

---

## 3. Assertions, extractions, and if/else — using checkpoints

Checkpoints are the agent's verification primitives. There are three kinds, and each one works with every analyze method below:

| Kind | Phrasing | What happens |
|---|---|---|
| **Assertion** | "Assert: …", "Verify …", "Confirm …" | Fails the run if the condition is false. |
| **Extraction** | "Store …", "Extract …", "Get …" | Saves a value into `run_end.final_state` for later use. |
| **If/Else** | "If … then … else …" | Branches the run based on a condition. |

### 3.1 Analyze methods — where the agent looks

The agent automatically picks the right method based on phrasing. To get the method you want, use the language column.

| Method | Use it for | Phrasing the agent recognizes |
|---|---|---|
| **Visual** (default) | Visible text, prices, labels, counts, color names, visibility | "the price …", "the heading …", "is visible", "displays", "is shown" |
| **Textual (DOM)** | Element states, CSS properties, HTML attributes, exact CSS color values | "is disabled / enabled / checked / readonly", "the placeholder of …", "the aria-label of …", "the font-size of …", "rgb(…)" / "#hex" |
| **URL** | Address bar — path, query, fragment, redirects | "URL contains …", "URL path is …", "URL has param …", "redirected to …" |
| **Title** | Browser tab `document.title` | "page title contains …", "title is …" |
| **DevTools** | Things not visible on screen — network, console, performance, cookies, localStorage | see §3.2 below |

### 3.2 DevTools analyze methods

Five subdomains. Each one is the right choice when the data you care about lives in the browser's internals rather than on the page.

#### Network (HTTP traffic)

The agent captures every HTTP request/response per step. **Resets each step** — assert on traffic in the same step it happens (or extract and carry forward).

These assertions also cover API calls **you** make directly in an objective (§3.5), not just the requests the page makes on its own — the agent records its own calls and you query them with the same fields below.

Queryable fields: `method`, `url`, `domain`, `path`, `query_params`, `resource_type`, `request_headers`, `request_body`, `response_status`, `response_headers`, `response_body`, `timing.duration_ms`, `timing.ttfb_ms`, `failed`, `failure_reason`.

```text
Assert: no API calls returned 5xx status codes
Assert: the POST /api/login returned HTTP status 200
Assert: all API responses completed in under 2 seconds
Assert: no network requests failed with connection errors
Assert: the /posts endpoint returned at least 10 items in the response body

Store the response body of the POST /api/login request
Extract the status code of the last API call to /api/users
Store all API request URLs

If the /api/auth returned 200 then proceed to dashboard, else show error message
```

Limits: up to 5,000 requests per step, response bodies capped at 64KB, binary content (images/fonts/videos) skipped.

**Downloads are not pages.** Navigating to a URL that answers with `content-disposition: attachment` starts a file download instead of loading a page, and the navigate step reports that a download started. The request still lands in the capture with its status and headers, so assert those in the step that triggered it — but treat the downloaded body as unavailable: assert status and headers, not a hash or a byte count. Prefer triggering the download from the UI (click the file's link) over navigating to its URL.

#### Console (browser console output)

Captures every `console.log/warn/error/info/debug` and every uncaught JS exception. **Resets each step**. Top frame only — iframes (payment widgets, third-party embeds) are not captured.

Levels normalize to: `log`, `warning`, `error`, `info`, `debug`. `errors` includes both `console.error()` and uncaught exceptions; `exceptions` is just the uncaught-exception subset (where `is_exception: true`).

```text
Assert: no console errors on the page
Assert: no uncaught JavaScript exceptions
Assert: no JS errors after clicking Submit
Assert: console contains "Amplitude SDK triggered"
Assert: no console warnings

Store all console error messages
Extract the first console error text

If console contains "feature_flag_enabled" then use new flow, else use legacy flow
```

#### Performance (Core Web Vitals)

Point-in-time read of the **last full page navigation's** metrics. Place the assertion after the page has loaded; use a wait step if the page needs time to settle.

Available metrics with good thresholds:

| Metric | Measures | Good |
|---|---|---|
| **LCP** | Largest Contentful Paint | < 2,500ms |
| **CLS** | Cumulative Layout Shift | < 0.1 |
| **INP** | Interaction to Next Paint (requires user interaction) | < 200ms |
| **FCP** | First Contentful Paint | < 1,800ms |
| **TTFB** | Time to First Byte | < 800ms |

```text
Assert: page LCP is under 2500ms
Assert: CLS is below 0.1
Assert: TTFB is under 800ms
Assert: page performance meets Core Web Vitals thresholds

Store the page LCP value
Extract all web vitals metrics
```

#### Cookies

Snapshot at assertion time. Sees `httpOnly` cookies too (unlike `document.cookie`). Cookies persist across steps; asserting on a different domain may show different cookies.

Fields: `name`, `value`, `domain`, `path`, `expires`, `http_only`, `secure`, `same_site` (`Strict`/`Lax`/`None`).

```text
Assert: a cookie named "session_id" exists
Assert: the session cookie is httpOnly
Assert: no cookies are set without the Secure flag
Assert: the auth cookie has sameSite set to "Strict"

Store all cookies
Extract the value of the "session_id" cookie

If a cookie named "auth_token" exists then go to dashboard, else go to login
```

#### localStorage

Snapshot at assertion time. Per-origin (protocol + domain + port). Persists across steps as long as you stay on the same origin. Values are always strings — if the app stores JSON, the value is the raw JSON string but the agent will parse it to drill into fields.

```text
Assert: auth_token exists in localStorage
Assert: the theme preference in localStorage is "dark"
Assert: localStorage has fewer than 10 items
Assert: the "theme" field in the user_prefs localStorage item is "dark"

Store all localStorage items
Extract the auth_token from localStorage
Get all localStorage keys

If localStorage has "onboarding_complete" then show dashboard, else start onboarding
```

#### Clipboard

The test's isolated clipboard (the OS clipboard is never involved). Holds **one current entry** — every copy or clipboard write replaces it, so **verify a clipboard value before the next clipboard write/clear**. An entry can carry text, HTML, and an image at once (e.g. a site's "Copy image" button).

```text
Click the Copy link button, then verify the clipboard contains "/inv/42"
Store the copied coupon code as 'coupon'
Verify an image was copied to the clipboard
Write "INV-2026-042" to the clipboard, verify the clipboard contains "INV-2026-042", then clear the clipboard and verify the clipboard text is empty
```

Do **not** paste into a field just to check a copied value — assert on the clipboard directly. For absence checks, prefer positive phrasing ("verify the clipboard text is empty") over negations.

### 3.3 Operators

Assertions support these comparisons. Phrase them naturally — the agent maps to the right operator.

| Operator | Meaning | Example |
|---|---|---|
| `equals` | Exact match | "price equals $29.99", "title is 'Home'" |
| `contains` | Substring match | "URL contains /checkout" |
| `not_contains` | Does not contain | "title not contains 'Error'" |
| `gt` / `gte` | Greater than / or equal | "items greater than 5" |
| `lt` / `lte` | Less than / or equal | "LCP less than 2500" |
| `not_equals` | Not equal | "status not equals 'failed'" |

### 3.4 Picking the right method when in doubt

- "Is the price $29.99?" — **Visual** (it's on screen).
- "Is the submit button disabled?" — **Textual/DOM** (state, not visible text).
- "Does this red background match exactly `rgb(220, 38, 38)`?" — **Textual/DOM** (exact CSS).
- "Are we on the checkout page?" — **URL** (address bar).
- "Did the page send any failed API calls?" — **DevTools/Network**.
- "Are there console errors?" — **DevTools/Console**.
- "Is the page fast?" — **DevTools/Performance** (LCP/FCP/TTFB).
- "Did the login set a session cookie?" — **DevTools/Cookies**.
- "Did the app store the auth token?" — **DevTools/localStorage**.

If you're not sure which method, default to **Visual** — that's what the agent does too.

### 3.5 Calling an API directly

Distinct from observing the page's network traffic (§3.2): you can have the agent **make an HTTP request itself** as part of an objective — to seed data, hit a backend, or check a service — then assert on or reuse the response.

Phrase an explicit call and name the response with "save the response as …":

```text
Call POST https://api.example.com/orders with body {"item": "sku_42", "qty": 1}, save the response as order
Hit GET https://api.example.com/orders/123, save the response as fetched
```

A pasted `curl` works too and is kept verbatim (method, headers, body, auth):

```text
curl -X POST https://api.example.com/login -H 'Content-Type: application/json' -d '{"u":"a","p":"b"}', save the response as login
```

Once the call is made, use the response in plain English. `{{name}}` is reserved for global variables and secrets (§6); a value the run produces is never written that way.

| To use | Say |
|---|---|
| the HTTP status code | `assert the response status is 201` |
| a field from the JSON body | `store the id from the response body as 'order_id'` |
| the whole body | `store the response body as 'order_body'` |
| a value later in the run | `the stored order_id value` |

When one objective makes several calls, name each response (`save the response as order`) and say which one you mean: `assert the order response status is 201`.

Then assert or chain on it — API calls and browser actions mix freely in one objective:

```text
Call POST https://api.example.com/login with body {"u": "{{user}}", "p": "{{password}}"}, save the response as login,
assert the response status is 200,
then open https://app.example.com and verify the dashboard loads
```

**Direct call vs. DevTools/Network (§3.2):** use a **direct call** when *you* want the agent to make the request (seed a record, call a backend, set up state). Use **DevTools/Network** when you want to **observe the requests the page itself makes** during a UI flow. They compose: seed via a direct call, drive the UI, then assert on the page's traffic.

**Tokens:** put any credential/token in a variable marked `secret: true` (§6) so it's masked and never logged.

**Session:** a direct call is made by the agent, not by the page — do not assume it shares the browser's cookies or login. An endpoint behind the app's sign-in may answer a direct call as an anonymous client (401/403) even while the browser is signed in. To exercise such an endpoint as the signed-in user, trigger the request from the UI and observe it (§3.2); to call it directly, pass the credential explicitly (a bearer token or API key in a `secret: true` variable, §6).

---

## 4. Extraction — the "store as" rule

Vague phrasing like "read", "tell me", "report" does NOT reliably persist data. The agent may *observe* the value but won't *capture* it into `run_end.final_state`.

```text
❌ "go to example.com and read the page title"
❌ "go to example.com and tell me the price"

✅ "go to example.com, store the page title as 'page_title'"
✅ "go to example.com, store the price of the first item as 'price'"
```

For DevTools extractions, the same rule applies — use "store" or "extract":

```text
✅ "store the response body of the POST /api/login as 'login_response'"
✅ "extract the value of the session_id cookie as 'session'"
```

Stored values land in `run_end.final_state` and feed the second results table per `SKILL.md §1.4`.

Refer back to a stored value in plain English (`the stored price value`, `the same version as the stored api_tag value`), never as `{{price}}`. The `{{name}}` form is for global variables and secrets only (§6).

---

## 5. Chaining — action → extraction → assertion

Multi-clause objectives are fine — and often preferable to splitting into multiple steps when the operations are tightly coupled.

```text
"go to {{app_url}}/dashboard,
 store the welcome message as 'welcome_text',
 store the user role in the sidebar as 'role',
 assert the role is 'Admin'"
```

```text
"open https://shop.example.com,
 add the first 'Wireless Headphones' result to the cart,
 navigate to the cart,
 store the cart total as 'total',
 assert the cart contains exactly one item"
```

```text
"go to {{app_url}}/api-health,
 store the API response body as 'health',
 assert no console errors,
 assert no API calls returned 5xx"
```

When chaining, keep each clause as a complete instruction. The agent processes them in order.

### Splitting vs. chaining — when to break into multiple steps

| Chain in one objective | Split into separate steps |
|---|---|
| ≤ 15 clauses, related state | > 15 reasoning steps expected |
| All happen on one page or flow | Different flows / different user roles |
| Extraction needed for the assertion in the same objective | Each step is independently testable |

For `_test.md` step bodies, each step is its own objective — split aggressively. For one-shot `kane-cli run`, chain when the operations share state.

---

## 6. Variables and context

Use `{{name}}` syntax for values that should be parameterized:

```text
"Log in as {{username}} with password {{password}}, then verify the dashboard loads"
```

**Always parameterize:** credentials, API keys, tokens, environment-specific URLs.
**OK to hardcode:** one-off URLs, static UI text, navigation paths.
**Never `{{name}}`:** anything the run itself produces. A stored value or an API response is referenced in plain English (§3.5, §4): `the stored order_id value`, `the response status`.

Mark credentials with `secret: true` in the variables JSON so they're masked in logs and routed to the secrets store:

```json
{
  "username": { "value": "alice", "secret": false },
  "password": { "value": "s3cret!", "secret": true }
}
```

For the full variables-loading precedence and context-file behavior, Read `references/setup-and-config.md`.

---

## 7. Conditional and negative patterns

Conditional objectives let the agent handle optional UI states without failing:

```text
"go to {{app_url}}, if a cookie banner appears then dismiss it, then assert the homepage loads"

"open the dashboard, if a 'What's new' modal is visible then close it, then click Settings"
```

Negative assertions verify the *absence* of something:

```text
"after submitting, assert no error message or red banner is visible"
"assert no console errors after clicking Save"
"assert no API calls failed during the checkout flow"
```

Positional assertions check where something is on the page:

```text
"assert 'Settings' appears in the left sidebar navigation"
"assert the 'Cancel' button is on the right side of the modal footer"
```

---

## 8. Common pitfalls

- **Setting localStorage or clipboard before navigating** — both need a page loaded first (storage is per-site; the clipboard tools live in the page). Navigate, then mutate.
- **Clipboard checkpoint after the next clipboard mutation** — the clipboard holds one entry; a later write/clear replaces it. Verify immediately after the copy/write you're checking.

| ❌ Don't | ✅ Do | Why |
|---|---|---|
| "Test the checkout flow" | "Go to /cart, click Checkout, fill the address form with {{tester}}, click Pay, assert the order confirmation page loads" | "Test" has no end state — the agent doesn't know when to stop. |
| "Add the item" | "Click the 'Add to Cart' button on the first product card" | Vague target — agent may click the wrong element. |
| "Tell me the price" | "Store the cart total as 'total'" | Vague verbs don't extract — use "store" / "extract" / "get". |
| Hardcode credentials in the objective | Use `{{username}}` / `{{password}}` from `--variables-file` | Credentials in plain text leak into logs and TMS. |
| Omit the URL | "Go to https://example.com/login first, then …" | Agent doesn't know where to start. |
| Cram 25 operations into one objective | Split at logical boundaries (login, navigate, action, verify) | Long runs drift and stall. |
| "Check the page is fast" | "Assert LCP is under 2500ms and CLS is below 0.1" | Use the explicit web-vital metric, not a vague "fast." |
| "Make sure no errors" | "Assert no console errors and no API calls returned 5xx" | Be explicit about which kind of error you're checking. |
| "Place the order, then verify it succeeded by checking Order History" | "Place the order, open Order History, then verify the newest order shows 'Processing'" | A check that needs its own navigation is an action hiding inside an assertion. Put the route in the actions and keep the assertion a pure observation of the screen it lands on. |
| "Use DevTools to intercept the response and issue a GET to the invoice endpoint" | "Open the invoice from the order page, then verify the request to `/api/orders/42/invoice` returned 200 with `content-disposition: attachment`" | Describe the user action and the observable outcome, not the mechanism — the agent picks the method, and a prescribed mechanism it cannot perform leaves it stuck. |

---

## 9. Worked end-to-end examples

### Example A — Single-page assertion suite

```text
"go to https://shop.example.com/products/42,
 assert the product title is 'Wireless Headphones',
 assert the price is $129.99,
 store the SKU as 'sku',
 assert URL contains /products/42,
 assert page LCP is under 2500ms,
 assert no console errors"
```

This exercises Visual (title, price), Extraction (SKU), URL, Performance, and Console — all in one objective.

### Example B — Login + dashboard verification

```text
"open https://app.example.com/login,
 log in with email {{tester.email}} and password {{tester.password}},
 assert the URL redirected to /dashboard,
 assert a cookie named 'session_id' exists and is httpOnly,
 assert no API calls returned 5xx during login,
 store the user role from the sidebar as 'role',
 assert the role is 'Admin'"
```

### Example C — testmd step body (same grammar)

In a `_test.md` file:

```markdown
## Verify checkout flow happy path
Open https://shop.example.com, log in as {{tester}}, add the first
'Wireless Headphones' result to the cart, navigate to checkout,
fill the shipping address with {{tester.address}}, click Pay.
Assert the order confirmation page loads.
Assert no console errors and no API calls returned 5xx.
Store the order number as 'order_id'.
```

The step body is exactly the same grammar as `kane-cli run`. Everything in this cookbook applies.

### Example D — Seed via API, then verify in the UI

```text
"Call POST https://api.example.com/orders with body {"item": "sku_42", "qty": 1},
 save the response as order,
 assert the response status is 201,
 then open https://app.example.com/orders,
 assert an order for 'sku_42' is visible"
```

The agent makes the API call directly, captures the response, asserts on its status, then drives the UI to confirm the seeded data appears. (Direct call → UI verify — contrast with §3.2, where you observe the page's own traffic.)
