# Codeception — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

Use the WebDriver module with `host: hub.lambdatest.com` and LT:Options in capabilities.

## Configuration (acceptance.suite.yml)

```yaml
actor: AcceptanceTester
modules:
  enabled:
    - WebDriver:
        url: 'https://%LT_USERNAME%:%LT_ACCESS_KEY%@hub.lambdatest.com/wd/hub'
        browser: chrome
        capabilities:
          browserVersion: 'latest'
          platformName: 'Windows 11'
          'LT:Options':
            user: '%LT_USERNAME%'
            accessKey: '%LT_ACCESS_KEY%'
            build: 'Codeception Build'
            name: 'Acceptance Test'
            video: true
            network: true
```

Or use `host: 'hub.lambdatest.com'` with credentials in the URL. Set `LT_USERNAME` and `LT_ACCESS_KEY` in the environment or in `.env`. For capability options (tunnel, platforms), see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
