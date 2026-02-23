# WebdriverIO — TestMu AI Cloud

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Install LambdaTest Service

```bash
npm install @wdio/lambdatest-service --save-dev
```

## Configuration

```javascript
// wdio.lambdatest.conf.js
const baseConfig = require('./wdio.conf.js');

exports.config = {
    ...baseConfig.config,
    user: process.env.LT_USERNAME,
    key: process.env.LT_ACCESS_KEY,
    hostname: 'hub.lambdatest.com',
    port: 80,
    path: '/wd/hub',
    services: ['lambdatest'],
    capabilities: [
        {
            browserName: 'Chrome',
            browserVersion: 'latest',
            'LT:Options': {
                platform: 'Windows 11',
                build: 'WDIO Build',
                name: 'WDIO Test',
                video: true, network: true,
            }
        },
        {
            browserName: 'Firefox',
            browserVersion: 'latest',
            'LT:Options': {
                platform: 'macOS Sequoia',
                build: 'WDIO Build',
                name: 'WDIO Firefox',
                video: true,
            }
        }
    ],
};
```

## Run

```bash
npx wdio run wdio.lambdatest.conf.js
```
