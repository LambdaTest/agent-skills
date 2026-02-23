# Nemo.js — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

Nemo.js is Selenium-based. Configure the driver to use the TestMu AI Hub when initializing Nemo.

## Configuration

Pass a custom WebDriver config that uses the remote hub URL and capabilities. In your Nemo setup (e.g. `nemo.config.js` or where you call `Nemo()`):

```javascript
const hubUrl = `https://${process.env.LT_USERNAME}:${process.env.LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub`;
const capabilities = {
    browserName: 'Chrome',
    browserVersion: 'latest',
    'LT:Options': {
        platform: 'Windows 11',
        build: 'Nemo Build',
        name: 'Nemo Test',
        user: process.env.LT_USERNAME,
        accessKey: process.env.LT_ACCESS_KEY,
        video: true,
        network: true,
    },
};
// Pass to your driver factory so Nemo uses RemoteWebDriver with hubUrl and capabilities
```

Ensure `LT_USERNAME` and `LT_ACCESS_KEY` are set. For capability options (tunnel, platforms), see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
