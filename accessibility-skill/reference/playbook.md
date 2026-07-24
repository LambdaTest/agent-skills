# Accessibility Testing - Advanced Playbook

## §1 - Setup and the Capability Model

Accessibility scanning is enabled through driver capabilities on your existing TestMu AI
automation. Requirements:

- A Selenium, Playwright, or Cypress suite running on the TestMu AI grid
- `LT_USERNAME` and `LT_ACCESS_KEY` from your Profile page
- Chrome or Edge, version 90 or higher (the scan uses an internal Chrome extension)

```bash
export LT_USERNAME="your-username"
export LT_ACCESS_KEY="your-access-key"
```

### Capability reference

| Capability | Type | Default | What it does |
|------------|------|---------|--------------|
| `accessibility` | boolean | off | Master switch. Required. Nothing scans without it. |
| `accessibility.autoscan` | boolean | - | Scan on every page navigation, no hooks. **Selenium only.** |
| `accessibility.wcagVersion` | string | not stated | Ruleset. Documented tokens: `wcag21a`, `wcag21aa`. |
| `accessibility.bestPractice` | boolean | `false` | Include best-practice checks beyond strict WCAG. |
| `accessibility.needsReview` | boolean | - | Include ambiguous issues that need human confirmation. |
| `accessibility.captureScreenshot` | boolean | - | Capture element screenshots with each violation. |
| `accessibility.passedTestCases` | boolean | - | Record checks that passed, not only failures. |

> `wcagVersion` is under-documented. Only `wcag21a` (2.1 A) and `wcag21aa` (2.1 AA) appear as
> literal tokens, though prose mentions 2.0, 2.2, and AAA. The dashboard Web Scanner defaults to
> 2.1 AA. For 2.2 or AAA via automation, verify the token empirically before relying on it.

### Two ways to run a scan

1. **On-demand hook** (recommended): enable the capability, then call
   `lambda-accessibility-scan` at each page or state you care about. Precise and faster. If you
   never call the hook, no report is generated.
2. **Autoscan** (Selenium only): set `accessibility.autoscan: true` and every navigation scans
   automatically. Slower, since it scans everything.

---

## §2 - Selenium Integration

```java
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.remote.RemoteWebDriver;
import java.net.URL;

ChromeOptions options = new ChromeOptions();
options.setCapability("browserName", "Chrome");
options.setCapability("browserVersion", "latest");

Map<String, Object> ltOptions = new HashMap<>();
ltOptions.put("user", System.getenv("LT_USERNAME"));
ltOptions.put("accessKey", System.getenv("LT_ACCESS_KEY"));
ltOptions.put("build", "Accessibility Build");
ltOptions.put("name", "Accessibility Test");
options.setCapability("LT:Options", ltOptions);

// Enable accessibility + refinements
options.setCapability("accessibility", true);
options.setCapability("accessibility.wcagVersion", "wcag21aa");
options.setCapability("accessibility.bestPractice", false);
options.setCapability("accessibility.needsReview", true);

WebDriver driver = new RemoteWebDriver(
    new URL("https://hub.lambdatest.com/wd/hub"), options);

// Option A - on-demand hook
driver.get("https://example.com");
driver.executeScript("lambda-accessibility-scan");        // scan this page
driver.get("https://example.com/pricing");
driver.executeScript("lambda-accessibility-scan");        // scan again

// Option B - autoscan (instead of the hook): add this capability and drop the hook calls
// options.setCapability("accessibility.autoscan", true);
```

Run: `mvn test`. In Python use `driver.execute_script("lambda-accessibility-scan")`.

---

## §3 - Playwright Integration

Playwright has no `autoscan` and no `lambda-accessibility-scan` hook. Instead it loads the
internal scan extension once, and it must run on **Chrome**, not Chromium.

```javascript
const capabilities = {
  browserName: 'Chrome',
  browserVersion: 'latest',
  'LT:Options': {
    platform: 'Windows 10',
    build: 'Playwright Accessibility',
    name: 'Playwright Accessibility',
    user: process.env.LT_USERNAME,
    accessKey: process.env.LT_ACCESS_KEY,
  },
  accessibility: true,
  'accessibility.wcagVersion': 'wcag21a',
  'accessibility.bestPractice': false,
  'accessibility.needsReview': true,
};
```

```javascript
// In lambdatest-setup.js, after page creation - loads the report-generating extension:
await ltPage.goto("chrome://extensions/?id=johgkfjmgfeapgnbkmfkfkaholjbcnah");
const secondToggleButton = ltPage.locator('#crToggle').nth(0);
await secondToggleButton.click();
```

Run: `npx playwright test`.

---

## §4 - Cypress Integration

Capabilities live in `lambdatest-config.json` (dotted keys). The scanner is registered in
different files depending on Cypress version.

```json
{
  "accessibility": true,
  "accessibility.wcagVersion": "wcag21aa",
  "accessibility.bestPractice": false,
  "accessibility.needsReview": true
}
```

**Cypress v10 and above**
- Import the scanner in `cypress/support/e2e.js`
- Register the plugin in `cypress.config.js`

**Cypress v9**
- Import the scanner in `cypress/support/index.js`
- Register the plugin in `cypress/plugins/index.js`

Run: `lambdatest-cypress-cli run`.

---

## §5 - HyperExecute

Under HyperExecute the capabilities become **camelCase** in a `cypressOps:` YAML block, and the
feature is **gated**: it must be enabled on your account by the TestMu AI support team.

```yaml
cypressOps:
  accessibility: true
  accessibilityWcagVersion: wcag21aa
  accessibilityBestPractice: false
  accessibilityNeedsReview: true
```

Run: `./hyperexecute --config <yaml>`. There is no `autoscan` variant under HyperExecute.

---

## §6 - Native Mobile App (Appium)

For native apps the scan hook is **mandatory** (there is no autoscan mode).

```python
capabilities = {
  "deviceName": "iPhone 12",
  "platformName": "ios",
  "platformVersion": "16.5",
  "app": "lt://APP_ID",
  "accessibility": True,
}
# after the screen is loaded:
driver.execute_script("lambda-accessibility-scan")
```

Hub: `mobile-hub.lambdatest.com/wd/hub`. iOS 16.5 or higher.

---

## §7 - Reading Results

All automation paths write to the Automation Dashboard: `accounts.lambdatest.com/dashboard` ->
Accessibility tab. There is **no results JSON, no exit code, and no pass/fail flag** on these
paths. Plan for a human (or the MCP server, §8) to read the report.

### The accessibility score

Each scan produces a proprietary score from 0 to 100:

- Severity weights: Critical `1.0`, Serious `0.75`, Moderate `0.50`, Minor `0.25`
- `z` (weighted severity) `= (%critical x 1.0) + (%serious x 0.75) + (%moderate x 0.50) + (%minor x 0.25)`
- `y` (density) `= total issues / total elements`
- **Score `= 100 - (y x 100 x z)`**

| Band | Meaning |
|------|---------|
| 90-100 | Excellent, minimal issues |
| 70-89 | Good, room for improvement |
| 50-69 | Moderate issues, needs attention |
| below 50 | Significant barriers |

### Severity vocabulary

**Critical / Serious / Moderate / Minor.** Each issue also carries the WCAG success criterion it
violates. Result views include Issue Summary, All Issues, Needs Review (manual confirmation), and
optional Passed Audits.

---

## §8 - Programmatic Access: the MCP Server

The Accessibility MCP server is the only path that returns a report to the caller, which makes it
the agent-native way to check a page and act on the result.

| Tool | Input | What it does |
|------|-------|--------------|
| `getAccessibilityReport` | a public URL | Scans the URL and returns the report |
| `buildLocalAppForAnalysis` | a local app | Builds and serves a local app, then scans it |
| `AnalyseAppViaTunnel` | a tunnelled local app | Scans a local app already running behind a tunnel |

`buildLocalAppForAnalysis` and `AnalyseAppViaTunnel` scan a page an agent just built, before it is
deployed - the closest thing to "accessibility check after every build."

---

## §9 - What Automation Covers (and Does Not)

**Automated scanning catches only a portion of WCAG.** Industry testing puts automated detection
at roughly a third to a half of success criteria. Reports separate results into violations,
passes, and **incomplete** (flagged for manual verification) - the platform's own admission that
automation cannot decide everything.

**Reliably automatable:** presence of `alt`, colour contrast (solid colours), form labels,
name/role/value markup, heading structure, focus-visible, link text.

**Needs manual / screen-reader testing:** whether alt text is *meaningful* (1.1.1), keyboard
operability (2.1.1, 2.1.2), focus order (2.4.3), use of colour (1.4.1), sensory characteristics
(1.3.3), error suggestion (3.3.3), status messages (4.1.3), all time-based media (1.2.x), reflow
(1.4.10), and hover/focus content (1.4.13).

Passing an automated scan is necessary, not sufficient. Never report "0 issues" as "accessible."

---

## §10 - Remediation: Rule to WCAG to Fix

The top web rules the engine reports and how to make them pass. Fixing is code work; the scan
tells you *which* criterion failed.

| Rule | WCAG (severity) | Fix |
|------|-----------------|-----|
| Image alt | 1.1.1 (Critical) | Descriptive `alt` on informative images; `alt=""` on decorative ones. |
| Info & relationships | 1.3.1 (Serious) | Semantic HTML and landmarks; `<label for>`; table `scope`. |
| Use of colour | 1.4.1 (Serious) | Add a non-colour cue (text, icon, underline), not colour alone. |
| Contrast (minimum) | 1.4.3 (Serious) | >= 4.5:1 for normal text, >= 3:1 for large text. |
| Keyboard | 2.1.1 (Critical) | Use `<button>` / `<a href>`, or `tabindex="0"` plus key handlers. |
| No keyboard trap | 2.1.2 (Serious) | Focus can leave via Tab / Escape. |
| Page titled | 2.4.2 (Serious) | Unique, descriptive `<title>`. |
| Focus order | 2.4.3 (Serious) | Logical DOM order; avoid positive `tabindex`. |
| Link purpose | 2.4.4 (Serious) | Descriptive link text; no bare "click here." |
| Focus visible | 2.4.7 (Serious) | Visible focus ring; `:focus-visible`. |
| Label in name | 2.5.3 (Serious) | Accessible name includes the visible label text. |
| Error identification | 3.3.1 (Serious) | Errors in text; `aria-invalid` / `aria-describedby`. |
| Labels or instructions | 3.3.2 (Serious) | `<label for>` / `aria-labelledby`, not placeholder-only. |
| Name, role, value | 4.1.2 (Critical) | Native controls, or ARIA role + name + state. |
| Status messages | 4.1.3 (Serious) | `role="status"` / `aria-live` for dynamic updates. |

### Mobile notes

Native apps have no DOM or ARIA. Android uses `contentDescription`, `labelFor`,
`TextInputLayout`, and `announceForAccessibility()` (TalkBack). iOS uses `accessibilityLabel`,
accessibility traits, and `isAccessibilityElement` (VoiceOver). Mobile adds first-class
touch-target rules (48dp Android, 44pt iOS), orientation-lock, and dynamic-type handling.

---

## §11 - Anti-Patterns and Gotchas

| Bad | Good | Why |
|-----|------|-----|
| `accessibility: true` but no hook call | Call `lambda-accessibility-scan`, or use `autoscan` | Hook path generates nothing without the call |
| `autoscan` on Playwright / Cypress | `autoscan` is Selenium only | It is ignored elsewhere; use the hook or extension |
| Running Playwright on Chromium | Use Chrome | The scan extension needs Chrome |
| Cypress scanner in the wrong file | v10 uses `support/e2e.js`; v9 uses `support/index.js` | Version-specific registration |
| Expecting a results API to gate CI | Use the MCP server, or a human reads the dashboard | No results API on automation paths |
| Treating "0 issues" as compliant | Add manual + screen-reader testing | Automation catches a fraction of WCAG |
| Assuming HyperExecute a11y works out of the box | Ask support to enable it | It is a gated feature |
