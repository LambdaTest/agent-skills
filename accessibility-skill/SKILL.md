---
name: accessibility-skill
description: >
  Adds automated accessibility (a11y) testing to test suites on TestMu AI cloud
  by enabling WCAG scans through driver capabilities. Framework-agnostic, works
  with Selenium, Playwright, and Cypress. Use when user mentions "accessibility",
  "a11y", "WCAG", "accessibility scan", "accessibility testing". Triggers on:
  "accessibility testing", "a11y scan", "WCAG compliance", "accessibility audit
  LambdaTest", "is my page accessible".
languages:
  - JavaScript
  - TypeScript
  - Java
category: accessibility-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# Accessibility Testing Skill

Accessibility testing on TestMu AI is layered onto an existing automation suite. You do not
install a separate tool: you enable a capability on your driver and either trigger scans at
chosen points or let every navigation scan automatically. Results appear on the Accessibility
dashboard.

**Know the one hard limit up front:** the automation capabilities can *start* a scan, but there
is no results API, no exit code, and no build-gating flag. To read a report back programmatically
(for example, to fail a build), use the Accessibility MCP server (see Core Patterns). Automated
scanning also catches only a portion of WCAG; it never replaces manual and screen-reader testing.

## Core Patterns

### Enable accessibility (capabilities)

```java
// One master switch is required; everything else is optional refinement.
capability.setCapability("accessibility", true);                 // required
capability.setCapability("accessibility.wcagVersion", "wcag21aa"); // wcag21a | wcag21aa
capability.setCapability("accessibility.bestPractice", false);    // default false
capability.setCapability("accessibility.needsReview", true);      // include ambiguous issues
```

### Selenium + accessibility

```java
// Option A: trigger a scan at a chosen point (recommended - precise, faster)
capability.setCapability("accessibility", true);
driver.get("https://example.com");
driver.executeScript("lambda-accessibility-scan"); // scan the current page; call as often as needed

// Option B: auto-scan every navigation (Selenium only)
capability.setCapability("accessibility", true);
capability.setCapability("accessibility.autoscan", true);
```

Run with your normal command, e.g. `mvn test`. If you use the hook and never call it, no report
is generated.

### Playwright + accessibility

```javascript
const capabilities = {
  "accessibility": true,
  "accessibility.wcagVersion": "wcag21a",
  "accessibility.bestPractice": false,
  "accessibility.needsReview": true
};
```

```javascript
// Playwright needs the internal scan extension loaded once, after page creation.
// Use Chrome (not Chromium). There is no autoscan/hook on this path.
await ltPage.goto("chrome://extensions/?id=johgkfjmgfeapgnbkmfkfkaholjbcnah");
const toggle = ltPage.locator('#crToggle').nth(0);
await toggle.click();
```

Run with `npx playwright test`.

### Cypress + accessibility

```json
// lambdatest-config.json - capabilities are dotted here
{ "accessibility": true, "accessibility.wcagVersion": "wcag21aa", "accessibility.needsReview": true }
```

Register the scanner (file differs by Cypress version):
- **v10+**: import in `cypress/support/e2e.js`, plugin in `cypress.config.js`
- **v9**: import in `cypress/support/index.js`, plugin in `cypress/plugins/index.js`

Run with `lambdatest-cypress-cli run`.

### Native mobile app (Appium)

```python
# The scan hook is mandatory for native apps (no autoscan mode).
caps["accessibility"] = True
driver.execute_script("lambda-accessibility-scan")
```

### Read results programmatically (MCP server)

The automation paths write to the dashboard only. The **Accessibility MCP server** is the one
path that returns a report to the caller:

- `getAccessibilityReport` - scan a public URL and return the report
- `buildLocalAppForAnalysis` - build and serve a local app, then scan it (before deploy)
- `AnalyseAppViaTunnel` - scan a local app already running behind a tunnel

Use it for a real "scan after every build" loop where an agent must act on the result.

### Authentication

```bash
export LT_USERNAME="your-username"     # from your TestMu AI Profile page
export LT_ACCESS_KEY="your-access-key"
```

## Quick Reference

| Task | How |
|------|-----|
| Enable scanning | `accessibility: true` capability (required) |
| WCAG level | `accessibility.wcagVersion` = `wcag21a` or `wcag21aa` |
| Best-practice checks | `accessibility.bestPractice` = `true` (default `false`) |
| Ambiguous issues | `accessibility.needsReview` = `true` |
| Scan at a point | `driver.executeScript("lambda-accessibility-scan")` |
| Scan every navigation | `accessibility.autoscan` = `true` (Selenium only) |
| Read results in code | Accessibility MCP server (dashboard-only otherwise) |
| Dashboard | `https://accounts.lambdatest.com/dashboard` -> Accessibility |

## Deep Patterns

For per-framework setup, the full capability reference, the accessibility score, severity
levels, the WCAG rule-to-fix mapping (remediation), and what automation does and does not cover,
see `reference/playbook.md`.
