# Laravel Dusk — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

Use a custom driver that creates a `RemoteWebDriver` with the TestMu AI Hub URL and ChromeOptions + LT:Options. See **§7 — LambdaTest Integration** in `reference/playbook.md` for the full `LambdaTestDuskTestCase` implementation.

## Hub URL

```
https://{LT_USERNAME}:{LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub
```

Set `LT_USERNAME` and `LT_ACCESS_KEY` in `.env` or the environment. For capability options (tunnel, platforms), see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
