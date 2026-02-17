# Robot Framework — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

Use SeleniumLibrary with a remote URL pointing to the TestMu AI Hub. See **§7 — LambdaTest Cloud Integration** in `reference/playbook.md` for the full `Open LambdaTest Browser` keyword and capability setup.

## Remote URL

```
https://${LT_USERNAME}:${LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub
```

Run with:

```bash
export LT_USERNAME=your_username
export LT_ACCESS_KEY=your_access_key
robot --variable REMOTE_URL:https://%{LT_USERNAME}:%{LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub tests/
```

For capability options (tunnel, platforms, status reporting), see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
