# Robot Framework — Advanced Patterns & Playbook

## Custom Keywords Library

```python
# CustomLibrary.py
from robot.api.deco import keyword, library
from robot.api import logger

@library(scope='SUITE')
class CustomLibrary:
    def __init__(self, base_url='http://localhost'):
        self.base_url = base_url
        self.session = None

    @keyword("Create API Session")
    def create_session(self, auth_token=None):
        import requests
        self.session = requests.Session()
        if auth_token:
            self.session.headers['Authorization'] = f'Bearer {auth_token}'
        return self.session

    @keyword("API GET")
    def api_get(self, endpoint, expected_status=200):
        resp = self.session.get(f'{self.base_url}{endpoint}')
        if resp.status_code != int(expected_status):
            raise AssertionError(f'Expected {expected_status}, got {resp.status_code}')
        return resp.json()

    @keyword("Verify JSON Schema")
    def verify_schema(self, data, schema):
        from jsonschema import validate
        validate(instance=data, schema=schema)
```

## Data-Driven Testing

```robot
*** Settings ***
Library    DataDriver    file=test_data.csv    dialect=unix
Test Template    Login Should Succeed

*** Test Cases ***
Login with ${username} and ${password}    Default    UserData

*** Keywords ***
Login Should Succeed
    [Arguments]    ${username}    ${password}    ${expected}
    Open Browser    ${URL}    chrome
    Input Text    id:username    ${username}
    Input Text    id:password    ${password}
    Click Button    id:login
    Run Keyword If    '${expected}' == 'pass'
    ...    Page Should Contain    Welcome
    ...    ELSE    Page Should Contain    Invalid
    [Teardown]    Close Browser
```

## Resource Files & Variables

```robot
*** Settings ***
Resource    common.robot
Variables   envconfig.py

*** Variables ***
${BASE_URL}        %{APP_URL=http://localhost:3000}
${TIMEOUT}         10s
${RETRY_COUNT}     3
&{ADMIN_USER}      username=admin    password=secret    role=admin
@{BROWSERS}        chrome    firefox    edge

*** Keywords ***
Wait And Click
    [Arguments]    ${locator}
    Wait Until Element Is Visible    ${locator}    timeout=${TIMEOUT}
    Scroll Element Into View    ${locator}
    Click Element    ${locator}

Retry On Failure
    [Arguments]    ${keyword}    @{args}
    Wait Until Keyword Succeeds    ${RETRY_COUNT}x    2s    ${keyword}    @{args}
```

## Listener for Custom Reporting

```python
# CustomListener.py
class CustomListener:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, output_file='results.json'):
        self.output = output_file
        self.results = []

    def end_test(self, data, result):
        self.results.append({
            'name': result.name,
            'status': result.status,
            'duration': result.elapsedtime,
            'message': result.message
        })

    def close(self):
        import json
        with open(self.output, 'w') as f:
            json.dump(self.results, f, indent=2)

# Usage: robot --listener CustomListener:results.json tests/
```

## Page Object Pattern

```robot
*** Keywords ***
# pages/LoginPage.robot
Open Login Page
    Go To    ${BASE_URL}/login
    Wait Until Element Is Visible    id:login-form

Enter Credentials
    [Arguments]    ${username}    ${password}
    Input Text    id:username    ${username}
    Input Password    id:password    ${password}

Submit Login
    Click Button    id:submit
    Wait Until Page Contains Element    css:.dashboard    timeout=10s

Login As
    [Arguments]    ${username}    ${password}
    Open Login Page
    Enter Credentials    ${username}    ${password}
    Submit Login
```

## Anti-Patterns

- ❌ Hardcoded waits (`Sleep 5s`) — use `Wait Until` keywords
- ❌ XPath-heavy locators — prefer id, data-testid, or CSS selectors
- ❌ Monolithic test files — split into resource files and page objects
- ❌ Missing `[Teardown]` — always clean up browser/state
- ❌ Variables in test names for readability only — use `[Documentation]`
