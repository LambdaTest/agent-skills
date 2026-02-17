# Robot Framework — Advanced Playbook

## §1 Project Setup & Configuration

### Installation
```bash
pip install robotframework
pip install robotframework-seleniumlibrary   # Web testing
pip install robotframework-requests          # API testing
pip install robotframework-datadriver        # Data-driven testing
pip install robotframework-pabot            # Parallel execution
pip install robotframework-browser          # Playwright-based (modern)
pip install robotframework-jsonlibrary      # JSON handling
pip install robotframework-databaselibrary  # Database testing
```

### Project Structure
```
robot-tests/
├── tests/
│   ├── ui/
│   │   ├── login.robot
│   │   ├── dashboard.robot
│   │   └── checkout.robot
│   ├── api/
│   │   ├── users_api.robot
│   │   ├── products_api.robot
│   │   └── auth_api.robot
│   └── e2e/
│       └── purchase_flow.robot
├── resources/
│   ├── keywords/
│   │   ├── common.resource
│   │   ├── login_keywords.resource
│   │   └── api_keywords.resource
│   ├── variables/
│   │   ├── common.yaml
│   │   ├── staging.yaml
│   │   └── production.yaml
│   └── libraries/
│       ├── CustomLibrary.py
│       └── DatabaseHelper.py
├── data/
│   ├── test_users.csv
│   └── products.json
├── results/
└── robot.yaml                # pabot / execution config
```

### Variable Files (Environment Config)
```yaml
# resources/variables/staging.yaml
BASE_URL: https://staging.example.com
API_URL: https://staging.example.com/api
BROWSER: headlesschrome
TIMEOUT: 15s
DB_HOST: staging-db.example.com
DB_NAME: testdb
```

```yaml
# resources/variables/production.yaml
BASE_URL: https://www.example.com
API_URL: https://api.example.com
BROWSER: headlesschrome
TIMEOUT: 10s
```

### Execution Commands
```bash
# Run all tests
robot --outputdir results tests/

# Run with variables file
robot --variablefile resources/variables/staging.yaml tests/

# Run by tag
robot --include smoke --outputdir results tests/
robot --exclude slow --outputdir results tests/

# Run specific suite
robot --suite tests.ui.login tests/

# Parallel execution with pabot
pabot --processes 4 --outputdir results tests/

# With Selenium Grid / LambdaTest
robot --variable REMOTE_URL:https://hub.lambdatest.com/wd/hub \
      --variable BROWSER:chrome \
      --variablefile resources/variables/staging.yaml \
      tests/ui/
```

---

## §2 Web UI Testing — SeleniumLibrary

### Login Tests with Page Objects
```robot
*** Settings ***
Library           SeleniumLibrary
Resource          ../resources/keywords/login_keywords.resource
Variables         ../resources/variables/staging.yaml
Suite Setup       Open Browser To Login Page
Suite Teardown    Close All Browsers
Test Teardown     Go To    ${BASE_URL}/login

*** Test Cases ***
Successful Login With Valid Credentials
    [Documentation]    Verify user can log in with valid email and password.
    [Tags]    smoke    login    critical
    Login With Credentials    user@test.com    ValidPass123
    Verify Dashboard Is Displayed
    Page Should Contain    Welcome back

Failed Login With Invalid Password
    [Tags]    login    negative
    Login With Credentials    user@test.com    WrongPassword
    Verify Error Message    Invalid email or password
    Location Should Not Contain    /dashboard

Failed Login With Empty Fields
    [Tags]    login    validation
    Click Button    id:login-submit
    Verify Error Message    Email is required

Login Remembers Email After Failed Attempt
    [Tags]    login    ux
    Input Text    id:email    user@test.com
    Input Password    id:password    wrong
    Click Button    id:login-submit
    Textfield Value Should Be    id:email    user@test.com

Account Lockout After Multiple Failures
    [Tags]    login    security
    FOR    ${i}    IN RANGE    5
        Login With Credentials    user@test.com    wrong-${i}
    END
    Verify Error Message    Account locked
```

### Login Keywords Resource
```robot
# resources/keywords/login_keywords.resource
*** Settings ***
Library    SeleniumLibrary

*** Keywords ***
Open Browser To Login Page
    [Documentation]    Opens browser and navigates to login page.
    Open Browser    ${BASE_URL}/login    ${BROWSER}
    ...    options=add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage")
    Set Selenium Implicit Wait    ${TIMEOUT}
    Set Selenium Speed    0.1s

Login With Credentials
    [Arguments]    ${email}    ${password}
    Wait Until Element Is Visible    id:email    timeout=${TIMEOUT}
    Clear Element Text    id:email
    Input Text    id:email    ${email}
    Input Password    id:password    ${password}
    Click Button    id:login-submit
    Sleep    1s    # Wait for response

Verify Dashboard Is Displayed
    Wait Until Location Contains    /dashboard    timeout=${TIMEOUT}
    Wait Until Element Is Visible    id:dashboard-content    timeout=${TIMEOUT}

Verify Error Message
    [Arguments]    ${expected_message}
    Wait Until Element Is Visible    css:.error-message    timeout=5s
    Element Should Contain    css:.error-message    ${expected_message}
```

### Dynamic Content & Waits
```robot
*** Test Cases ***
Product Search Returns Results
    [Tags]    ui    search
    Go To    ${BASE_URL}/products
    Input Text    id:search-input    laptop
    Click Button    id:search-button
    Wait Until Element Is Visible    css:.product-card    timeout=10s
    ${count}=    Get Element Count    css:.product-card
    Should Be True    ${count} > 0    No search results found

Pagination Works Correctly
    [Tags]    ui    pagination
    Go To    ${BASE_URL}/products
    Wait Until Element Is Visible    css:.product-card    timeout=10s
    ${page1_first}=    Get Text    css:.product-card:first-child .product-name
    Click Element    css:.pagination .next
    Wait Until Element Is Not Visible    css:.loading-spinner    timeout=10s
    ${page2_first}=    Get Text    css:.product-card:first-child .product-name
    Should Not Be Equal    ${page1_first}    ${page2_first}

Modal Dialog Interaction
    [Tags]    ui    modal
    Click Button    id:delete-account
    Wait Until Element Is Visible    id:confirm-modal    timeout=5s
    Element Should Contain    id:confirm-modal    Are you sure?
    Click Button    id:modal-cancel
    Wait Until Element Is Not Visible    id:confirm-modal    timeout=5s
```

---

## §3 API Testing — RequestsLibrary

### CRUD API Tests
```robot
*** Settings ***
Library           RequestsLibrary
Library           Collections
Library           JSONLibrary
Variables         ../resources/variables/staging.yaml
Suite Setup       Authenticate API User
Suite Teardown    Delete All Sessions

*** Variables ***
${AUTH_TOKEN}     ${EMPTY}

*** Test Cases ***
Create User Via API
    [Tags]    api    crud    smoke
    ${body}=    Create Dictionary
    ...    name=Test User
    ...    email=newuser-${TIMESTAMP}@test.com
    ...    role=viewer
    ${response}=    POST On Session    api    /users    json=${body}
    Should Be Equal As Integers    ${response.status_code}    201
    Dictionary Should Contain Key    ${response.json()}    id
    Set Suite Variable    ${CREATED_USER_ID}    ${response.json()}[id]

Get User Returns Created User
    [Tags]    api    crud
    ${response}=    GET On Session    api    /users/${CREATED_USER_ID}
    Should Be Equal As Integers    ${response.status_code}    200
    Should Be Equal    ${response.json()}[name]    Test User
    Should Be Equal    ${response.json()}[role]    viewer

Update User Via API
    [Tags]    api    crud
    ${body}=    Create Dictionary    name=Updated User    role=editor
    ${response}=    PUT On Session    api    /users/${CREATED_USER_ID}    json=${body}
    Should Be Equal As Integers    ${response.status_code}    200
    Should Be Equal    ${response.json()}[name]    Updated User

List Users With Pagination
    [Tags]    api    pagination
    ${params}=    Create Dictionary    page=1    limit=10    sort=name
    ${response}=    GET On Session    api    /users    params=${params}
    Should Be Equal As Integers    ${response.status_code}    200
    ${users}=    Get Value From Json    ${response.json()}    $.data
    ${count}=    Get Length    ${users[0]}
    Should Be True    ${count} <= 10

Delete User Via API
    [Tags]    api    crud
    ${response}=    DELETE On Session    api    /users/${CREATED_USER_ID}
    Should Be Equal As Integers    ${response.status_code}    204

Verify Deleted User Returns 404
    [Tags]    api    crud    negative
    ${response}=    GET On Session    api    /users/${CREATED_USER_ID}
    ...    expected_status=404

*** Keywords ***
Authenticate API User
    ${timestamp}=    Evaluate    int(time.time())    time
    Set Suite Variable    ${TIMESTAMP}    ${timestamp}
    Create Session    api    ${API_URL}    verify=${TRUE}
    ${body}=    Create Dictionary    email=apitest@test.com    password=TestPass123
    ${response}=    POST On Session    api    /auth/login    json=${body}
    ${token}=    Set Variable    ${response.json()}[token]
    ${headers}=    Create Dictionary
    ...    Authorization=Bearer ${token}
    ...    Content-Type=application/json
    Create Session    api    ${API_URL}    headers=${headers}    verify=${TRUE}
```

### Error Handling & Validation
```robot
*** Test Cases ***
Create User Missing Required Fields Returns 422
    [Tags]    api    validation
    ${body}=    Create Dictionary    name=Only Name
    ${response}=    POST On Session    api    /users    json=${body}
    ...    expected_status=422
    Should Contain    ${response.json()}[errors][0][field]    email

Invalid JSON Returns 400
    [Tags]    api    negative
    ${headers}=    Create Dictionary    Content-Type=application/json
    ${response}=    POST On Session    api    /users
    ...    data=not-json
    ...    headers=${headers}
    ...    expected_status=400

Unauthorized Request Returns 401
    [Tags]    api    security
    Create Session    noauth    ${API_URL}    verify=${TRUE}
    ${response}=    GET On Session    noauth    /users/me    expected_status=401
```

---

## §4 Data-Driven Testing

### DataDriver with CSV
```robot
# tests/data-driven/login_data_driven.robot
*** Settings ***
Library           SeleniumLibrary
Library           DataDriver    file=data/login_tests.csv    dialect=unix
Resource          ../resources/keywords/login_keywords.resource
Suite Setup       Open Browser To Login Page
Suite Teardown    Close All Browsers
Test Template     Login Should ${expected_result}

*** Test Cases ***
Login with ${email} and ${password} should ${expected_result}    [Tags]    data-driven

*** Keywords ***
Login Should succeed
    [Arguments]    ${email}    ${password}    ${expected_result}
    Login With Credentials    ${email}    ${password}
    Verify Dashboard Is Displayed

Login Should fail
    [Arguments]    ${email}    ${password}    ${expected_result}
    Login With Credentials    ${email}    ${password}
    Verify Error Message    Invalid
```

```csv
# data/login_tests.csv
email,password,expected_result
valid@test.com,ValidPass123,succeed
invalid@test.com,WrongPass,fail
,password,fail
user@test.com,,fail
```

### FOR Loops for Data Iteration
```robot
*** Test Cases ***
Verify All Product Categories Load
    [Tags]    api    data-driven
    @{categories}=    Create List    electronics    clothing    books    sports    home
    FOR    ${category}    IN    @{categories}
        ${response}=    GET On Session    api    /products    params=category=${category}
        Should Be Equal As Integers    ${response.status_code}    200
        ${count}=    Get Length    ${response.json()}[data]
        Should Be True    ${count} > 0    No products in category: ${category}
    END

Verify Bulk User Creation
    [Tags]    api    bulk
    @{users}=    Create List
    FOR    ${i}    IN RANGE    5
        ${body}=    Create Dictionary    name=User ${i}    email=bulk${i}@test.com
        ${response}=    POST On Session    api    /users    json=${body}
        Should Be Equal As Integers    ${response.status_code}    201
        Append To List    ${users}    ${response.json()}[id]
    END
    # Cleanup
    FOR    ${user_id}    IN    @{users}
        DELETE On Session    api    /users/${user_id}
    END
```

---

## §5 Custom Python Libraries

### Custom Library with @keyword Decorator
```python
# resources/libraries/CustomLibrary.py
from robot.api.deco import keyword, library
from robot.api import logger
import json
import hashlib
import time
import random
import string


@library(scope='GLOBAL')
class CustomLibrary:
    """Custom keywords for application-specific testing."""

    def __init__(self):
        self._created_resources = []

    @keyword("Generate Unique Email")
    def generate_unique_email(self, prefix="test"):
        """Generate a unique email address for testing."""
        timestamp = int(time.time() * 1000)
        random_str = ''.join(random.choices(string.ascii_lowercase, k=4))
        email = f"{prefix}-{timestamp}-{random_str}@test.com"
        logger.info(f"Generated email: {email}")
        return email

    @keyword("Generate Test User Data")
    def generate_test_user_data(self, **overrides):
        """Generate a complete test user with realistic data."""
        user = {
            "name": f"Test User {random.randint(1000, 9999)}",
            "email": self.generate_unique_email(),
            "password": "TestPass123!",
            "role": "viewer",
        }
        user.update(overrides)
        return user

    @keyword("Calculate MD5 Hash")
    def calculate_md5_hash(self, content):
        """Calculate MD5 hash of content for file integrity checks."""
        return hashlib.md5(content.encode()).hexdigest()

    @keyword("Parse JSON Response Field")
    def parse_json_response_field(self, response_body, json_path):
        """Extract a nested field from JSON using dot notation."""
        data = json.loads(response_body) if isinstance(response_body, str) else response_body
        for key in json_path.split("."):
            if key.isdigit():
                data = data[int(key)]
            else:
                data = data[key]
        return data

    @keyword("Track Created Resource")
    def track_created_resource(self, resource_type, resource_id):
        """Track resources for cleanup in teardown."""
        self._created_resources.append((resource_type, resource_id))
        logger.info(f"Tracking {resource_type}/{resource_id} for cleanup")

    @keyword("Get Created Resources")
    def get_created_resources(self):
        """Return list of tracked resources."""
        return list(self._created_resources)

    @keyword("Clear Tracked Resources")
    def clear_tracked_resources(self):
        """Clear tracked resources after cleanup."""
        count = len(self._created_resources)
        self._created_resources.clear()
        return count
```

### Using Custom Library in Tests
```robot
*** Settings ***
Library    ../resources/libraries/CustomLibrary.py
Library    RequestsLibrary

*** Test Cases ***
Create User With Generated Data
    [Tags]    api    custom-lib
    ${user_data}=    Generate Test User Data    role=admin
    ${response}=    POST On Session    api    /users    json=${user_data}
    Should Be Equal As Integers    ${response.status_code}    201
    Track Created Resource    user    ${response.json()}[id]

Test Teardown Cleans Up Resources
    [Teardown]    Cleanup All Tracked Resources

*** Keywords ***
Cleanup All Tracked Resources
    ${resources}=    Get Created Resources
    FOR    ${resource}    IN    @{resources}
        ${type}=    Set Variable    ${resource}[0]
        ${id}=    Set Variable    ${resource}[1]
        Run Keyword If    '${type}' == 'user'
        ...    DELETE On Session    api    /users/${id}    expected_status=any
    END
    Clear Tracked Resources
```

---

## §6 Browser Library (Playwright-Based)

### Modern Web Testing with Browser Library
```robot
*** Settings ***
Library    Browser
Suite Setup    New Browser    chromium    headless=${TRUE}
Suite Teardown    Close Browser

*** Test Cases ***
Fill and Submit Form
    [Tags]    browser    form
    New Page    ${BASE_URL}/register
    Fill Text    id=name    Test User
    Fill Text    id=email    register@test.com
    Fill Text    id=password    SecurePass123!
    Click    id=submit-btn
    Wait For Elements State    id=success-message    visible    timeout=10s
    Get Text    id=success-message    ==    Registration successful!

Handle Network Requests
    [Tags]    browser    network
    ${promise}=    Promise To Wait For Response    **/api/products
    New Page    ${BASE_URL}/products
    ${response}=    Wait For    ${promise}
    Should Be Equal As Numbers    ${response}[status]    200

Take Screenshot on Failure
    [Tags]    browser    screenshot
    [Teardown]    Take Screenshot    EMBED
    New Page    ${BASE_URL}/missing-page
    Get Title    ==    404 Not Found

Test Responsive Layout
    [Tags]    browser    responsive
    New Page    ${BASE_URL}
    Set Viewport Size    375    812    # iPhone X
    Get Style    id=sidebar    display    ==    none
    Set Viewport Size    1920    1080    # Desktop
    Get Style    id=sidebar    display    ==    flex
```

---

## §7 LambdaTest Cloud Integration

### Remote Browser Configuration
```robot
*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${LT_USERNAME}     %{LT_USERNAME}
${LT_ACCESS_KEY}   %{LT_ACCESS_KEY}
${REMOTE_URL}      https://${LT_USERNAME}:${LT_ACCESS_KEY}@hub.lambdatest.com/wd/hub

*** Keywords ***
Open LambdaTest Browser
    [Arguments]    ${browser}=chrome    ${test_name}=Robot Test
    ${lt_options}=    Create Dictionary
    ...    name=${test_name}
    ...    build=Robot-${BUILD_NUMBER}
    ...    project=MyProject
    ...    platformName=Windows 11
    ...    selenium_version=4.0
    ...    w3c=${TRUE}
    ...    visual=${TRUE}
    ...    network=${TRUE}
    ...    console=${TRUE}
    ${options}=    Evaluate
    ...    selenium.webdriver.ChromeOptions()
    ...    modules=selenium.webdriver
    Call Method    ${options}    set_capability    LT:Options    ${lt_options}
    Create Webdriver    Remote
    ...    command_executor=${REMOTE_URL}
    ...    options=${options}
    Set Selenium Implicit Wait    15s

Mark LambdaTest Test Status
    [Arguments]    ${status}    ${reason}=${EMPTY}
    Execute Javascript
    ...    lambda_status = "${status}";
    ...    lambda_reason = "${reason}";
    ...    window.lambdatest_action = {"action": "setTestStatus", "arguments": {"status": lambda_status, "remark": lambda_reason}};
```

### Cross-Browser Test Suite
```robot
*** Settings ***
Library    SeleniumLibrary
Resource    ../resources/keywords/common.resource

*** Test Cases ***
Cross Browser Login Test - Chrome
    [Tags]    cross-browser    chrome
    Open LambdaTest Browser    chrome    Login-Chrome
    Run Login Test Flow
    [Teardown]    Run Keywords    Mark LambdaTest Test Status    passed    AND    Close Browser

Cross Browser Login Test - Firefox
    [Tags]    cross-browser    firefox
    Open LambdaTest Browser    firefox    Login-Firefox
    Run Login Test Flow
    [Teardown]    Run Keywords    Mark LambdaTest Test Status    passed    AND    Close Browser

*** Keywords ***
Run Login Test Flow
    Go To    ${BASE_URL}/login
    Input Text    id:email    user@test.com
    Input Password    id:password    TestPass123
    Click Button    id:login-submit
    Wait Until Location Contains    /dashboard    timeout=15s
    Page Should Contain    Welcome
```

---

## §8 CI/CD Integration

### GitHub Actions
```yaml
name: Robot Framework Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  robot-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        suite: [ui, api, e2e]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install robotframework \
            robotframework-seleniumlibrary \
            robotframework-requests \
            robotframework-datadriver \
            robotframework-pabot \
            robotframework-jsonlibrary

      - name: Install Chrome
        if: matrix.suite == 'ui' || matrix.suite == 'e2e'
        uses: browser-actions/setup-chrome@v1

      - name: Install ChromeDriver
        if: matrix.suite == 'ui' || matrix.suite == 'e2e'
        uses: nanasess/setup-chromedriver@v2

      - name: Run Robot Tests
        run: |
          robot \
            --outputdir results/${{ matrix.suite }} \
            --variablefile resources/variables/staging.yaml \
            --variable BROWSER:headlesschrome \
            --loglevel INFO \
            --include ${{ matrix.suite }} \
            --exitonfailure \
            tests/${{ matrix.suite }}/
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
          LT_USERNAME: ${{ secrets.LT_USERNAME }}
          LT_ACCESS_KEY: ${{ secrets.LT_ACCESS_KEY }}

      - name: Generate combined report
        if: always()
        run: |
          rebot \
            --outputdir results/combined \
            --merge \
            results/${{ matrix.suite }}/output.xml

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: robot-results-${{ matrix.suite }}
          path: results/

      - name: Publish Robot Results
        uses: joonvena/robotframework-reporter-action@v2.4
        if: always()
        with:
          gh_access_token: ${{ secrets.GITHUB_TOKEN }}
          report_path: results/${{ matrix.suite }}
```

### Parallel Execution with Pabot
```bash
# Run tests in parallel across 4 processes
pabot --processes 4 \
  --outputdir results \
  --variablefile resources/variables/staging.yaml \
  --variable BROWSER:headlesschrome \
  tests/

# Parallel with suite-level granularity
pabot --processes 4 \
  --testlevelsplit \
  --outputdir results \
  tests/
```

---

## §9 Debugging Table

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | `No keyword with name 'X' found` | Library not imported or keyword name mismatch | Check `*** Settings ***` imports; keyword names are case-insensitive but space-sensitive |
| 2 | `WebDriverException: Message: unknown error` | ChromeDriver version mismatch | Match ChromeDriver to Chrome version; use `webdriver-manager` |
| 3 | `ElementNotInteractableException` | Element hidden, overlapped, or not ready | Use `Wait Until Element Is Visible` before interaction; scroll into view |
| 4 | `Variable '${VAR}' not found` | Variable not defined or wrong scope | Check variable file path; use `Set Suite Variable` for cross-test sharing |
| 5 | `Session 'api' already exists` | Session created in setup and test | Use `Create Session` in Suite Setup only; or use unique session names |
| 6 | Tests pass locally, fail in CI | Browser not installed or different env | Install headless Chrome; use `--variable BROWSER:headlesschrome` |
| 7 | DataDriver finds 0 test cases | CSV path wrong or format mismatch | Use relative path from test file; check `dialect` matches CSV format |
| 8 | Custom library not found | Wrong import path | Use absolute path or add to `PYTHONPATH`; check `__init__.py` exists |
| 9 | Pabot tests interfere with each other | Shared state (database, session) | Use unique test data per process; isolate with `--pabotlib` for shared resources |
| 10 | `HTTPError: 401` in RequestsLibrary | Token expired between tests | Re-authenticate in Suite Setup; use shorter-lived fixtures |
| 11 | Screenshots not captured on failure | Missing `Test Teardown` | Add `[Teardown] Capture Page Screenshot` or use listener |
| 12 | `FOR` loop syntax error | Wrong Robot Framework version | RF 5+ uses `FOR/END`; RF 4 uses `\` continuation; upgrade to RF 5+ |

---

## §10 Best Practices Checklist

1. Use resource files for reusable keywords — keep test files focused on scenarios
2. Use variable files for environment config — switch staging/production with `--variablefile`
3. Use `[Tags]` on every test — enable `--include`/`--exclude` for selective execution
4. Use `[Documentation]` on tests and keywords — improve report readability
5. Use custom Python libraries for complex logic — keep `.robot` files readable
6. Use `Wait Until` keywords — never use `Sleep` for synchronization
7. Use `expected_status` in RequestsLibrary — avoid manual status code checks
8. Use DataDriver for parameterized tests — separate test data from test logic
9. Use pabot for parallel execution — reduce CI pipeline duration
10. Use `Set Suite Variable` carefully — prefer test-level isolation over shared state
11. Use `[Teardown]` for cleanup — ensure resources are released even on failure
12. Use meaningful keyword names — tests should read like specifications
13. Use Browser Library for modern apps — Playwright-based auto-waits are more reliable
14. Use `rebot` for report merging — combine parallel results into single report
