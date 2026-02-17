# Puppeteer — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Connection (CDP WebSocket)

Puppeteer connects to TestMu AI via Chrome DevTools Protocol WebSocket:

```javascript
const puppeteer = require('puppeteer');

const capabilities = {
    browserName: 'Chrome',
    browserVersion: 'latest',
    'LT:Options': {
        platform: 'Windows 11',
        build: 'Puppeteer Build',
        name: 'My Test',
        user: process.env.LT_USERNAME,
        accessKey: process.env.LT_ACCESS_KEY,
        video: true,
        network: true,
    },
};

const browser = await puppeteer.connect({
    browserWSEndpoint: `wss://cdp.lambdatest.com/puppeteer?capabilities=${encodeURIComponent(JSON.stringify(capabilities))}`,
});

const page = await browser.newPage();
// ... run test ...
await browser.close();
```

## Environment Variables

```bash
export LT_USERNAME="your_username"
export LT_ACCESS_KEY="your_access_key"
```

## Test Status

Report pass/fail to the dashboard (if supported by your runner). For capability options (tunnel, geoLocation, resolution, etc.), see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
