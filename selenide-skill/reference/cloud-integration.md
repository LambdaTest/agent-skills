# Selenide — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

Selenide uses Selenium under the hood. Set `Configuration.remote` to the TestMu AI Hub URL and add LT:Options to `Configuration.browserCapabilities`. See **§6 — LambdaTest Integration** in `reference/playbook.md` for the full `LambdaTestConfig` and BaseTest setup.

## Hub URL

```
https://{LT_USERNAME}:{LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub
```

Run with `LT_USERNAME` and `LT_ACCESS_KEY` set. For capability options (tunnel, platforms), see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
