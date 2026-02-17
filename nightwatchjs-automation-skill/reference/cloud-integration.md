# Nightwatch.js — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Configuration

Add a `lambdatest` (or `lt`) environment in `nightwatch.conf.js`:

```javascript
// nightwatch.conf.js
module.exports = {
  test_settings: {
    default: {
      launch_url: 'http://localhost:3000',
      desiredCapabilities: { browserName: 'chrome' }
    },
    lambdatest: {
      selenium: {
        host: 'hub.lambdatest.com',
        port: 80
      },
      desiredCapabilities: {
        browserName: 'chrome',
        browserVersion: 'latest',
        'LT:Options': {
          platform: 'Windows 11',
          build: 'Nightwatch Build',
          name: 'Nightwatch Tests',
          user: process.env.LT_USERNAME,
          accessKey: process.env.LT_ACCESS_KEY,
          video: true,
          console: true,
          network: true
        }
      }
    }
  },
  page_objects_path: ['pages/'],
};
```

## Run on Cloud

```bash
export LT_USERNAME=your_username
export LT_ACCESS_KEY=your_access_key
npx nightwatch --env lambdatest
```

## Parallel / Multiple Browsers

Define multiple environments (e.g. `lambdatest_chrome`, `lambdatest_firefox`) with different `desiredCapabilities`, then run with `--env lambdatest_chrome,lambdatest_firefox` or use a matrix in CI. For capability values (platforms, browsers), see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).
