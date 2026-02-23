# Appium — Python Patterns

## Setup

```bash
pip install Appium-Python-Client pytest
```

## Android Test

```python
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

@pytest.fixture
def android_driver():
    options = UiAutomator2Options()
    options.platform_name = "android"
    options.device_name = "emulator-5554"
    options.app = "/path/to/app.apk"
    options.automation_name = "UiAutomator2"

    driver = webdriver.Remote("http://localhost:4723", options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def test_login(android_driver):
    driver = android_driver
    wait = WebDriverWait(driver, 15)

    email = wait.until(EC.visibility_of_element_located(
        (AppiumBy.ACCESSIBILITY_ID, "emailInput")))
    email.send_keys("user@test.com")

    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "passwordInput").send_keys("pass123")
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "loginButton").click()

    wait.until(EC.visibility_of_element_located(
        (AppiumBy.ACCESSIBILITY_ID, "dashboard")))
```

## Cloud Integration

```python
@pytest.fixture
def cloud_driver():
    options = UiAutomator2Options()
    options.platform_name = "android"
    options.device_name = "Pixel 7"
    options.platform_version = "13"
    options.app = "lt://APP1234567890"
    options.set_capability("LT:Options", {
        "w3c": True, "build": "Python Build", "name": "Login Test",
        "isRealMobile": True, "video": True,
    })

    hub = f"https://{os.environ['LT_USERNAME']}:{os.environ['LT_ACCESS_KEY']}@mobile-hub.lambdatest.com/wd/hub"
    driver = webdriver.Remote(hub, options=options)
    yield driver
    driver.quit()
```
