# Low-code, AI-authoring and managed test tools to TestMu AI

Read this when the source is mabl, Testim (Tricentis), Momentic, ACCELQ, testRigor, Katalon, BrowserStack Low Code Automation, Sauce AI for Test Authoring, QA Wolf, Functionize, or Selenium IDE recordings. These tools store tests as recordings or natural-language steps, not as Selenium/Playwright code, so there is no hub URL to swap. The TestMu AI targets are KaneAI (natural-language web, app and API tests, stored in Test Manager, run on HyperExecute), Kane CLI (`*_test.md` tests in the repo), Test Manager (test cases and datasets), and the TestMu AI grid for any code the source can export.

Each vendor below follows TestMu AI's official migration guide; link the guide in the migration summary.

Contents
1. Fingerprints
2. What moves where (all vendors)
3. Katalon (one-click importer)
4. mabl
5. Testim
6. Momentic
7. ACCELQ
8. testRigor
9. BrowserStack Low Code Automation and Sauce AI for Test Authoring
10. QA Wolf, Functionize, Selenium IDE
11. KaneAI and Kane CLI mechanics
12. Gotchas and unverified

## 1. Fingerprints

mabl: `mabl ` CLI calls (`mabl deployments create`, `mabl tests run-cloud`, `mabl tests export`), `--api-key`/`-k`, `@mablhq/`. Testim: `@testim/testim-cli`, `testim --token`, `--project`, `--grid`. Momentic: `*.test.yaml` with `fileType: momentic/test/v2`, `*.module.yaml`, `momentic.config.yaml`, `momentic run`, `MOMENTIC_API_KEY`. ACCELQ: ACCELQ Agent config, `accelq` CI plugins. testRigor: `testrigor` CLI or API calls, test files in `.txt`/`.yaml`. Katalon: `.prj`, `Test Cases/*.tc`, `Scripts/**/*.groovy`, `Object Repository/`, `katalonc`. BrowserStack Low Code: Low Code Automation exports (`.side`, Nightwatch). Sauce AI: Sauce AI authoring exports. QA Wolf: `@qawolf/flows`, `@qawolf/cli`, `QAWOLF_API_KEY`, `qawolf flows`. Functionize: Functionize orchestration webhooks. Selenium IDE: `*.side`, `selenium-side-runner`.

## 2. What moves where

| Source asset | TestMu AI target | How |
|---|---|---|
| Tests the source can export as Playwright or Selenium code | TestMu AI grid (Browser Cloud) | export, then the CDP or hub swap (`testmu-target.md` §2 and §3) |
| Selenium IDE `.side` exports | TestMu AI Selenium grid | `selenium-side-runner` with a `.side.yml` pointing `server` at the hub (§10) |
| Test case lists (CSV) | Test Manager test cases | Test Manager **Add Test Case > Import CSV** (map at least Title; Steps, Outcome, Folder, custom fields optional) |
| PDF run reports | Test Manager test cases | **Generate With AI** (AI Test Case Generator, up to 10 files) |
| TestRail, qTest, Xray, Zephyr Scale cases linked to the source | Test Manager | one-click importers |
| Flows the team wants as maintained automation | KaneAI tests | **Automate with KaneAI** on an imported test case, or a new natural-language test |
| Shared steps, groups, flows, rules | KaneAI modules | author once, save as a module |
| Variables, environments, secrets | KaneAI variables and secrets | re-create |
| Data tables, data pools, data sets | KaneAI datasets / Test Manager datasets | CSV export, then **Import Data** |
| API steps | KaneAI API steps | paste each request as a curl command |
| Visual checks | KaneAI Visual Comparison step (SmartUI) | first run captures the baseline |
| TOTP / authenticator steps | KaneAI TOTP variables | add the Base32 secret |
| Test files kept in the repo | Kane CLI `*_test.md` | rewrite steps as Markdown |
| Run history, videos, logs | stays in the source | export for records; no importer reads them |

KaneAI imports existing tests natively only from Katalon (desktop web). Every other source is re-created.

## 3. Katalon (one-click importer)

Official guide: https://www.testmuai.com/support/docs/one-click-migration-from-katalon/. Upload the Katalon project to the migration tool, review supported and unsupported test cases, choose **Import Anyway** for partially supported ones (their unsupported steps are excluded), enter masked variable values (saved as Secret or Global Variable), preview and import. Supported desktop web cases become authored KaneAI New Experience tests with Katalon operations translated into KaneAI instructions. Not migrated: mobile app cases, generated code (generate it after import), step screenshots (appear after the first edit or run), excluded cases. Katalon projects that the team prefers to keep running as Groovy/Selenium can point at the TestMu AI grid through Katalon's remote execution settings (hub `https://hub.lambdatest.com/wd/hub`, `LT:Options` as desired capabilities) or run on HyperExecute (`katalon-integration-with-hyperexecute`).

## 4. mabl

Official guide: https://www.testmuai.com/support/docs/mabl-to-kaneai-migration-guide/
- Export browser tests: `mabl tests export <test-id> --format playwright` (TypeScript; also `side`, `json`, `csv`; options `--file`, `--mabl-branch`, `-e/--environment-id`). The export drops select, drag and drop, JavaScript snippet, API, cookie, file upload, download assertion, accessibility, MFA, email and PDF steps (`side` also drops conditionals); mark each dropped step `TODO(testmu-migration)` and re-create it in KaneAI (select: Forms and Inputs; drag and drop; JavaScript Execution; API Testing; Upload and Download Files; TOTP; Conditional Logic; accessibility via the KaneAI test run Accessibility option, Chrome and Edge only).
- Run exported Playwright on the TestMu AI grid with the canonical fixture in `testmu-target.md` §3.
- CSV exports -> Test Manager CSV import. DataTables: `mabl datatables export <id> --format csv` -> datasets. API tests: export as Postman JSON, generate curl per request, paste into KaneAI API steps. Flows -> KaneAI modules. Variables -> KaneAI variables.
- `mabl deployments create ... --browsers chrome edge firefox webkit --await-completion` in CI -> a KaneAI test run on HyperExecute triggered from CI (§11), or the exported Playwright suite run against the grid.
- mabl email and PDF assertions have no direct TestMu AI step; list as gaps.

## 5. Testim

Official guide: https://www.testmuai.com/support/docs/testim-to-kaneai-migration-guide/
- Code export (professional plan): append `?embedMode=true&exportPuppeteer=true&exportSelenium=true&exportPlaywright=true` to the Testim editor URL and export each test as Playwright; run it on the TestMu AI grid (CDP endpoint). Testim warns exported code may need manual adjustment.
- During the move: Testim has a built-in LambdaTest grid type. In Testim grid settings add a LambdaTest grid (host `hub.lambdatest.com`, port 443, TestMu AI username and access key), then run `testim --token <t> --project <p> --grid "<grid name>"` (the `--grid` parameter replaces the old `--host`/`--port`; only Selenium mode).
- Test cases: TestRail, qTest or Xray links -> one-click importers; PDF run reports -> AI Test Case Generator; CSV from the Test List view -> CSV import.
- Flows -> KaneAI (Automate with KaneAI, Create and Automate, or from scratch); groups/shared steps -> modules; test data -> parameters and datasets; custom code -> JavaScript steps; conditions -> If/Else; visual -> Visual Comparison; API -> API steps; MySQL/MongoDB -> database connections.

## 6. Momentic

Official guide: https://www.testmuai.com/support/docs/momentic-to-kaneai-migration-guide/
- Tests are `*.test.yaml` files anywhere in the repo (`fileType: momentic/test/v2`, `id`, `url`, `before`, `steps`, `after`); steps are plain natural-language strings or commands (`click: X`, `type: { text, into }`, `assert: <description>`, `navigate`, `if`, `while`, `javascript`, `request`, `visualDiff`). Modules are `*.module.yaml`.
- Mapping: natural-language steps -> KaneAI steps or Kane CLI `## ` steps (mostly verbatim); `assert` -> natural-language assertions; `if`/`while` -> If/Else and While Loop blocks; `javascript` -> JavaScript steps (page-level only; rework Node-sandbox code); `request` -> curl in API steps; `visualDiff` -> Visual Comparison; modules -> KaneAI modules; environments/variables/secrets -> KaneAI variables and secrets; mobile (`momentic-mobile`) -> KaneAI app tests after uploading the APK/IPA.
- Tests that should stay in the repo -> Kane CLI `*_test.md` (one `## Heading` per step, prose body).
- Playwright code exists only via a Momentic Enterprise eject; if the team has it, run it on the grid.
- `momentic run --env ... --url-override ...` in CI -> `kane-cli testrun run --tags ... --parallel N --remote` or a KaneAI test run on HyperExecute.

## 7. ACCELQ

Official guide: https://www.testmuai.com/support/docs/accelq-to-kaneai-migration-guide/
- Automation Scenarios with step details -> CSV -> Test Manager (Scenario name -> Title, Description, Steps, Tags up to 48 characters, custom fields, Scenario ID as a traceability custom field).
- Manual runs exported as PDF -> AI Test Case Generator.
- Web and mobile Scenarios -> KaneAI tests (Automate with KaneAI). Shared Actions -> modules. Test Cases (data variations) and Data Pools -> Excel -> CSV -> datasets. REST calls -> API steps.
- During the move: the ACCELQ Agent can use LambdaTest (TestMu AI) as its external execution provider.

## 8. testRigor

Official guide: https://www.testmuai.com/support/docs/testrigor-to-kaneai-migration-guide/
- Test case steps -> KaneAI sessions; names and steps -> CSV -> Test Manager; reusable rules -> modules; Test Data -> variables and secrets; Data Sets -> CSV -> datasets; `call api` -> API steps; authenticator 2FA -> TOTP variables; `.txt`/`.yaml` test files in a repo -> Kane CLI `*_test.md`.
- testRigor can run on the TestMu AI grid during the transition (optional step in the guide).

## 9. BrowserStack Low Code Automation and Sauce AI for Test Authoring

BrowserStack (https://www.testmuai.com/support/docs/browserstack-to-kaneai-migration-guide/): Low Code Automation tests export (Pro plan) as Selenium IDE `.side` or Nightwatch.js; run `.side` with `selenium-side-runner` against the TestMu AI hub (§10) and Nightwatch with the TestMu AI Nightwatch config; BrowserStack Test Management CSV -> Test Manager CSV import; flows to maintain -> KaneAI.
Sauce Labs (https://www.testmuai.com/support/docs/saucelabs-to-kaneai-migration-guide/): Sauce AI authoring test cases -> export generated code and run on the grid, or re-create in KaneAI; Sauce AI data variables -> KaneAI variables and secrets; Replay recordings -> re-perform the flow in KaneAI; App Storage builds -> download and re-upload for KaneAI app tests; TestRail cases -> one-click importer; Sauce Connect -> TestMu AI Tunnel selected in KaneAI.

## 10. QA Wolf, Functionize, Selenium IDE

- QA Wolf: flows live on the QA Wolf platform per environment. Pull them with the CLI (`qawolf auth login` or `QAWOLF_API_KEY`, `qawolf flows pull --env <env>`); they import a `@qawolf/flows` runtime rather than plain `@playwright/test`, and mobile flows are WebdriverIO + Appium. Replace the `@qawolf/flows` runtime with plain Playwright Test (web) or WebdriverIO (mobile), then point them at the TestMu AI grid (`testmu-target.md` §3 fixture, or `mobile-hub.lambdatest.com` with `wdio-lambdatest-service`). Where the runtime helpers have no plain equivalent, re-create the flow in KaneAI.
- Functionize: no documented code export; re-create the tests in KaneAI or Kane CLI from the Functionize test steps, and trigger them from CI through Kane CLI or the Test Manager HyperExecute API (§11).
- Selenium IDE: `selenium-side-runner` reads `-c` as space-separated `key=value` pairs with dot notation (no JSON), so use a `.side.yml`:
  ```yaml
  server: https://hub.lambdatest.com/wd/hub
  capabilities:
    browserName: chrome
    browserVersion: latest
    LT:Options:
      user: ${LT_USERNAME}
      accessKey: ${LT_ACCESS_KEY}
      platformName: Windows 11
      build: side-migration
  ```
  then `selenium-side-runner tests/*.side` (substitute the env values before running, since YAML does not expand them).

## 11. KaneAI and Kane CLI mechanics

KaneAI: author in the web app (Create a Web Test or App Test, natural-language steps, `/` menu for modules, variables, secrets, datasets, JavaScript, API, database, visual, conditionals, loops, TOTP); tests are saved as Test Manager test cases; code generation: Selenium Python and Appium Python by default, Selenium Java and Playwright Python/C#/JavaScript on request (Classic), Playwright Python and JavaScript in New Experience. Run: Test Manager > Test Runs > Create Test Run, type **KaneAI Generated Test Cases**, add cases with generated code, assign configurations, **Run on HyperExecute** (now or scheduled). Native app runs on real devices are available for KaneAI-generated runs only. CI trigger: `POST https://test-manager-api.lambdatest.com/api/atm/v1/hyperexecute` (Basic auth; body `test_run_id`, optional `concurrency`, `title`, `region`, `tunnel`, `accessibility`, `replaced_url`) returns `job_id` and `job_link`.

Kane CLI: `npm install -g @testmuai/kane-cli` (Node 18+). Interactive auth `kane-cli login`; in CI do not run `login`, pass `--username "$LT_USERNAME" --access-key "$LT_ACCESS_KEY"`. One-off: `kane-cli run "<objective>" --url <url> --headless [--timeout N] [--variables-file f] [--code-export --code-language python|javascript]`. Suites: `*_test.md` files (frontmatter `mode`, `variables`, `tags`, `target`, `device_name`, `os_version`; root-only `headless`, `chrome_profile`, `cdp_endpoint`, `ws_endpoint`, `global_context`, `local_context`; steps as `## Heading` + prose; `@import` alone on its step line), run with `kane-cli testmd run <file>` or `kane-cli testrun run --tags smoke --parallel 5`. Remote execution on TestMu AI: one-time `kane-cli plugin install remote-execution`, then add `--remote` (defaults to HyperExecute; needs a HyperExecute plan; run web and mobile in separate runs). Scaffolding: `kane-cli generate "<description>"` prints a request id, then `kane-cli generate --save --req <id> [--out <dir>]`. Machine output: `--agent` (NDJSON on stdout) and the evidence pack under `.testmuai/evidence/`. Exit codes for `run`: 0 passed, 1 failed, 2 error (setup or usage), 3 timeout (for `testrun run`, 3 means cancelled).

## 12. Gotchas and unverified

- Budget a cleanup pass for any exported code: recorder exports rarely use auto-waiting assertions; remove fixed sleeps before trusting results on a new grid.
- Recreate scheduling and alerting from the source tool in CI, Test Manager schedules or HyperExecute `slackChannel`/`callbackURL`.
- Run history never migrates; export what the team must keep before cancelling the source plan.
- Katalon tests kept in Katalon and run on the TestMu AI grid: Project > Settings > Desired Capabilities > Remote, Remote Server URL `http://<user>:<key>@hub.lambdatest.com/wd/hub`, capabilities as flat entries (the docs do not show nested `LT:Options` there).
- `selenium-side-runner`: an unquoted `LT:Options:` key parses in its YAML loader; `-c "LT:Options.user=x"` dot notation also works.
- Kane CLI frontmatter: `global_context` and `local_context` can be set per step as well as at the root.
- Unverified (27 Oct 2026): Functionize API trigger names.
- Sources: TestMu AI official migration guides listed per section, kane-cli-cli-reference, kane-cli-testrun, kane-cli-remote-execution, kane-cli-generate, kane-cli-cicd, kane-cli-testmd-composition, kaneai-ci-cd-automation; help.mabl.com mabl-tests-export and deployment-events-mabl-cli; help.testim.io exporting-a-testim-test-as-code-for-playwright and LambdaTest integration; momentic.ai/docs core-concepts/file-format and reference/commands; docs.qawolf.com local-execution; selenium.dev command-line-runner.
