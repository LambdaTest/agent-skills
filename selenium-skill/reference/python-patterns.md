# Selenium — Python Patterns

## Setup

```bash
pip install selenium pytest
```

## Basic Test

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

class TestLogin:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def test_login(self):
        self.driver.get("https://example.com/login")
        self.wait.until(EC.visibility_of_element_located((By.ID, "username"))).send_keys("user@test.com")
        self.driver.find_element(By.ID, "password").send_keys("password123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait.until(EC.url_contains("/dashboard"))
        assert "Dashboard" in self.driver.title

    def teardown_method(self):
        if self.driver:
            self.driver.quit()
```

## Pytest Fixtures

```python
import pytest
from selenium import webdriver

@pytest.fixture
def driver():
    d = webdriver.Chrome()
    d.maximize_window()
    yield d
    d.quit()

@pytest.fixture
def cloud_driver():
    username = os.environ["LT_USERNAME"]
    access_key = os.environ["LT_ACCESS_KEY"]
    options = webdriver.ChromeOptions()
    lt_options = {
        "platform": "Windows 11",
        "build": "Python Build",
        "name": "Python Test",
        "video": True,
        "network": True,
    }
    options.set_capability("LT:Options", lt_options)
    d = webdriver.Remote(
        command_executor=f"https://{username}:{access_key}@hub.lambdatest.com/wd/hub",
        options=options,
    )
    yield d
    d.quit()
```

## Page Object in Python

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def navigate(self):
        self.driver.get("https://example.com/login")
        return self

    def login(self, username, password):
        self.wait.until(EC.visibility_of_element_located(self.USERNAME)).send_keys(username)
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.SUBMIT).click()
        return DashboardPage(self.driver)
```
