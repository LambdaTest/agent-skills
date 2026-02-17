# Espresso — TestMu AI Cloud Integration

For full device catalog, capabilities, and LT:Options reference, see [shared/testmu-cloud-reference.md](../../shared/testmu-cloud-reference.md).

## Upload APKs

```bash
# App APK
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@app-debug.apk" -F "type=android"
# Returns: { "app_url": "lt://APP123" }

# Test APK
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://manual-api.lambdatest.com/app/upload/realDevice" \
  -F "appFile=@app-debug-androidTest.apk" -F "type=android"
# Returns: { "app_url": "lt://TEST456" }
```

## Execute Tests

```bash
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  -X POST "https://mobile-api.lambdatest.com/framework/v1/espresso/build" \
  -H "Content-Type: application/json" \
  -d '{
    "app": "lt://APP123",
    "testSuite": "lt://TEST456",
    "device": ["Pixel 8-14", "Pixel 7-13", "Galaxy S24-14"],
    "build": "Espresso Cloud",
    "video": true,
    "deviceLog": true,
    "queueTimeout": 600,
    "idleTimeout": 150
  }'
```

## Check Build Status

```bash
curl -u "$LT_USERNAME:$LT_ACCESS_KEY" \
  "https://mobile-api.lambdatest.com/framework/v1/espresso/build/<build_id>"
```
