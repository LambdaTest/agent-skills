# TestCafe — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Setup

TestCafe uses the `lambdatest` browser alias. Set credentials and run:

```bash
export LT_USERNAME=your_username
export LT_ACCESS_KEY=your_access_key
npx testcafe "lambdatest:Chrome@latest:Windows 11" tests/
```

## Multiple Browsers

```bash
npx testcafe "lambdatest:Chrome@latest:Windows 11,lambdatest:Firefox@latest:macOS Sequoia" tests/
```

## In Code (Programmatic)

When using TestCafe's programmatic API, pass the same browser string. For tunnel (localhost), use TestCafe's `--tunnel` or configure via LambdaTest tunnel settings in the dashboard.

For capability options (tunnel, geoLocation, resolution, video), see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
