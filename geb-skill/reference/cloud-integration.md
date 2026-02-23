# Geb — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

Geb uses Selenium. Add a `lambdatest` environment in your GebConfig (e.g. `GebConfig.groovy`) that creates a `RemoteWebDriver` with the TestMu AI Hub URL and LT:Options. See **§1 — Project Setup** in `reference/playbook.md` for the full `lambdatest { driver { ... } }` block.

## Run on Cloud

```bash
export LT_USERNAME=your_username
export LT_ACCESS_KEY=your_access_key
./gradlew test -Dgeb.env=lambdatest
```

For capability options (tunnel, platforms, browsers), see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
