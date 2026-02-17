# Protractor — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

Protractor is Selenium-based. Point `seleniumAddress` to the TestMu AI Hub:

## Configuration

```javascript
// protractor.conf.js
exports.config = {
    seleniumAddress: `https://${process.env.LT_USERNAME}:${process.env.LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub`,
    capabilities: {
        browserName: 'chrome',
        browserVersion: 'latest',
        platformName: 'Windows 11',
        'LT:Options': {
            project: 'Protractor Tests',
            build: process.env.BUILD_NUMBER || 'protractor-build',
            name: 'E2E Suite',
            user: process.env.LT_USERNAME,
            accessKey: process.env.LT_ACCESS_KEY,
            console: true,
            network: true,
            video: true,
        },
    },
};
```

## Run on Cloud

```bash
export LT_USERNAME=your_username
export LT_ACCESS_KEY=your_access_key
npx protractor protractor.conf.js
```

For capability options (tunnel, platforms, browsers), see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md). See also §6 in `reference/playbook.md` for full LambdaTest integration and CI/CD.
