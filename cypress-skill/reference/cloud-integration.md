# Cypress — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Setup

```bash
npm install lambdatest-cypress-cli --save-dev
npx lambdatest-cypress init
```

This creates `lambdatest-config.json`:

```json
{
  "lambdatest_auth": {
    "username": "${LT_USERNAME}",
    "access_key": "${LT_ACCESS_KEY}"
  },
  "browsers": [
    {
      "browser": "Chrome",
      "platform": "Windows 11",
      "versions": ["latest"]
    },
    {
      "browser": "MicrosoftEdge",
      "platform": "Windows 11",
      "versions": ["latest"]
    },
    {
      "browser": "Firefox",
      "platform": "macOS Sequoia",
      "versions": ["latest"]
    }
  ],
  "run_settings": {
    "cypress_config_file": "cypress.config.js",
    "build_name": "Cypress Cloud Build",
    "parallels": 5,
    "specs": "cypress/e2e/**/*.cy.{js,ts}",
    "ignore_files": "",
    "network": true,
    "headless": true,
    "npm_dependencies": {}
  },
  "tunnel_settings": {
    "tunnel": false,
    "tunnelName": ""
  }
}
```

## Run on Cloud

```bash
# All specs
npx lambdatest-cypress run

# Specific specs
npx lambdatest-cypress run --specs "cypress/e2e/login.cy.js"

# With tunnel (for localhost)
npx lambdatest-cypress run --tunnel
```

## Parallel Execution

Set `parallels` in config. Tests distribute across browsers automatically.

```json
{
  "run_settings": {
    "parallels": 10
  }
}
```
