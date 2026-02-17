# Migration Overview — Framework Comparison and Language Matrix

## Framework Comparison

| Aspect | Selenium | Playwright | Puppeteer | Cypress |
|--------|----------|------------|-----------|---------|
| **Protocol / model** | WebDriver (W3C), multi-vendor | CDP / WebDriver BiDi, modern | Chrome DevTools Protocol (CDP) | Proprietary runner + browser |
| **Languages** | Java, Python, JS, C#, Ruby, PHP | JS, TS, Python, Java, C# | JS, TS | JS, TS |
| **Waits** | Explicit (WebDriverWait) required | Auto-wait on actions/assertions | Manual (waitForSelector, etc.) | Built-in retry-ability on cy commands |
| **Execution** | In-process driver; can be remote (Grid) | In-process or connect to browser | In-process (Chrome/Chromium) | Runner + browser; no true multi-tab |
| **Cross-browser** | Chrome, Firefox, Safari, Edge via drivers | Chromium, Firefox, WebKit out of box | Chrome/Chromium (experimental others) | Chrome, Firefox, Edge, Safari (limited) |
| **Typical use** | Enterprise, multi-language teams, Grid | E2E tests, modern stack, API mock | Scraping, PDF, Chrome-only automation | E2E + component tests, dev-friendly |

## When to Migrate

| From → To | Common reasons |
|-----------|-----------------|
| Selenium → Playwright | Reduce flakiness (auto-wait), better debugging (trace), API mocking, single codebase (JS/TS). |
| Selenium → Puppeteer | Simplify stack to Chrome-only, lighter weight, scraping/PDF needs. |
| Playwright → Selenium | Need Java/Python/C# or existing Selenium Grid / enterprise tooling. |
| Puppeteer → Playwright | Need Firefox/WebKit, stronger test APIs (assertions, trace), multi-browser. |
| Cypress → Playwright | Need multiple tabs, non-Chromium browsers, or run in existing Node CI without Cypress runner. |
| Playwright → Cypress | Team preference for Cypress DX, component testing in Cypress, existing Cypress cloud. |

## Language Matrix

Use this to set expectations when the user does not specify a target language:

| Framework | Java | Python | JavaScript | TypeScript | C# | Ruby | PHP |
|-----------|------|--------|------------|------------|-----|------|-----|
| **Selenium** | Yes | Yes | Yes | — | Yes | Yes | Yes |
| **Playwright** | Yes | Yes | Yes | Yes | Yes | — | — |
| **Puppeteer** | — | — | Yes | Yes | — | — | — |
| **Cypress** | — | — | Yes | Yes | — | — | — |

- **Selenium (Java/Python/C#) → Playwright:** Playwright’s primary ecosystem is JS/TS. Migration usually means rewriting to TypeScript or JavaScript. Playwright does support Java, Python, and C#, but the most common migration path is to JS/TS.
- **Playwright/Puppeteer/Cypress → Selenium:** Target language can be any supported by Selenium; choose based on project or ask the user.
- **Puppeteer/Cypress:** No Java/Python/C#; migration to or from them implies JS/TS.

## Supported Migration Pairs

| Direction | Reference file |
|-----------|----------------|
| Selenium → Playwright | [selenium-to-playwright.md](selenium-to-playwright.md) |
| Playwright → Selenium | [playwright-to-selenium.md](playwright-to-selenium.md) |
| Selenium → Puppeteer | [selenium-to-puppeteer.md](selenium-to-puppeteer.md) |
| Puppeteer → Selenium | [puppeteer-to-selenium.md](puppeteer-to-selenium.md) |
| Puppeteer → Playwright | [puppeteer-to-playwright.md](puppeteer-to-playwright.md) |
| Playwright → Puppeteer | [playwright-to-puppeteer.md](playwright-to-puppeteer.md) |
| Cypress → Playwright | [cypress-to-playwright.md](cypress-to-playwright.md) |
| Playwright → Cypress | [playwright-to-cypress.md](playwright-to-cypress.md) |
| Selenium → Cypress | [selenium-to-cypress.md](selenium-to-cypress.md) |
| Cypress → Selenium | [cypress-to-selenium.md](cypress-to-selenium.md) |

Each reference file contains API mapping tables, before/after snippets, lifecycle notes, TestMu cloud pointers, and gotchas for that pair.
