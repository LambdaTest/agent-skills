# Framework Templates Reference

Complete boilerplate and patterns for each supported test framework.

---

## Table of Contents

1. [pytest (Python)](#pytest)
2. [Jest (JavaScript/TypeScript)](#jest)
3. [Mocha + Chai (JavaScript)](#mocha)
4. [JUnit 5 + RestAssured (Java)](#junit)
5. [Go testing](#go)
6. [Newman (Postman CLI)](#newman)
7. [k6 (Load Testing)](#k6)
8. [Plain .http Files](#http-files)

---

## pytest (Python) {#pytest}

### Setup
```bash
pip install pytest requests pytest-dotenv
```

### Fixture Pattern (conftest.py)
```python
import pytest
import requests
import os

@pytest.fixture(scope="session")
def base_url():
    return os.getenv("API_BASE_URL", "https://api.example.com")

@pytest.fixture(scope="session")
def auth_headers():
    return {
        "Authorization": f"Bearer {os.getenv('API_TOKEN', 'test-token')}",
        "Content-Type": "application/json",
    }

@pytest.fixture(scope="session")
def session(base_url, auth_headers):
    s = requests.Session()
    s.headers.update(auth_headers)
    s.base_url = base_url
    return s
```

### Test File Template
```python
import pytest

class TestEndpointName:
    """Tests for POST /resource"""

    # --- Happy Path ---
    def test_valid_payload_returns_201(self, session):
        payload = {"field": "value"}
        res = session.post(f"{session.base_url}/resource", json=payload)
        assert res.status_code == 201
        body = res.json()
        assert "id" in body

    # --- Validation ---
    @pytest.mark.parametrize("field", ["required_field_1", "required_field_2"])
    def test_missing_required_field_returns_422(self, session, field):
        payload = {"required_field_1": "a", "required_field_2": "b"}
        del payload[field]
        res = session.post(f"{session.base_url}/resource", json=payload)
        assert res.status_code in (400, 422)

    # --- Auth ---
    def test_unauthenticated_returns_401(self, base_url):
        res = requests.post(f"{base_url}/resource", json={"field": "value"})
        assert res.status_code == 401
```

### Run
```bash
API_BASE_URL=https://staging.api.com API_TOKEN=mytoken pytest -v
```

---

## Jest (JavaScript/TypeScript) {#jest}

### Setup
```bash
npm install --save-dev jest axios @types/jest ts-jest dotenv
```

### jest.config.js
```javascript
module.exports = {
  testEnvironment: 'node',
  setupFiles: ['dotenv/config'],
};
```

### Test File Template
```typescript
import axios, { AxiosInstance } from 'axios';

const client: AxiosInstance = axios.create({
  baseURL: process.env.API_BASE_URL || 'https://api.example.com',
  headers: { Authorization: `Bearer ${process.env.API_TOKEN}` },
});

describe('POST /resource', () => {
  // Happy Path
  it('returns 201 with valid payload', async () => {
    const { status, data } = await client.post('/resource', { field: 'value' });
    expect(status).toBe(201);
    expect(data).toHaveProperty('id');
  });

  // Validation
  it.each(['field1', 'field2'])('returns 422 when %s is missing', async (field) => {
    const payload: Record<string, string> = { field1: 'a', field2: 'b' };
    delete payload[field];
    await expect(client.post('/resource', payload)).rejects.toMatchObject({
      response: { status: 422 },
    });
  });

  // Auth
  it('returns 401 without auth', async () => {
    await expect(
      axios.post(`${process.env.API_BASE_URL}/resource`, { field: 'value' })
    ).rejects.toMatchObject({ response: { status: 401 } });
  });
});
```

### Run
```bash
API_BASE_URL=https://staging.api.com API_TOKEN=mytoken npx jest --verbose
```

---

## Mocha + Chai (JavaScript) {#mocha}

### Setup
```bash
npm install --save-dev mocha chai axios
```

### Test File Template
```javascript
const { expect } = require('chai');
const axios = require('axios');

const client = axios.create({
  baseURL: process.env.API_BASE_URL || 'https://api.example.com',
  headers: { Authorization: `Bearer ${process.env.API_TOKEN}` },
});

describe('POST /resource', () => {
  it('returns 201 with valid payload', async () => {
    const { status, data } = await client.post('/resource', { field: 'value' });
    expect(status).to.equal(201);
    expect(data).to.have.property('id');
  });

  it('returns 401 without auth', async () => {
    try {
      await axios.post(`${process.env.API_BASE_URL}/resource`, { field: 'value' });
      throw new Error('Expected 401 but got success');
    } catch (err) {
      expect(err.response.status).to.equal(401);
    }
  });
});
```

### Run
```bash
npx mocha --timeout 10000
```

---

## JUnit 5 + RestAssured (Java) {#junit}

### pom.xml dependencies
```xml
<dependencies>
  <dependency>
    <groupId>io.rest-assured</groupId>
    <artifactId>rest-assured</artifactId>
    <version>5.4.0</version>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>
  </dependency>
</dependencies>
```

### Test Class Template
```java
import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class ResourceApiTest {

    @BeforeAll
    void setup() {
        RestAssured.baseURI = System.getenv().getOrDefault("API_BASE_URL", "https://api.example.com");
    }

    @Test
    void createResource_validPayload_returns201() {
        given()
            .header("Authorization", "Bearer " + System.getenv("API_TOKEN"))
            .contentType(ContentType.JSON)
            .body("{\"field\": \"value\"}")
        .when()
            .post("/resource")
        .then()
            .statusCode(201)
            .body("id", notNullValue());
    }

    @Test
    void createResource_noAuth_returns401() {
        given()
            .contentType(ContentType.JSON)
            .body("{\"field\": \"value\"}")
        .when()
            .post("/resource")
        .then()
            .statusCode(401);
    }

    @ParameterizedTest
    @ValueSource(strings = {"field1", "field2"})
    void createResource_missingField_returns422(String missingField) {
        // Build payload without the missing field and assert 400/422
        given()
            .header("Authorization", "Bearer " + System.getenv("API_TOKEN"))
            .contentType(ContentType.JSON)
            .body("{}")
        .when()
            .post("/resource")
        .then()
            .statusCode(anyOf(is(400), is(422)));
    }
}
```

### Run
```bash
mvn test -DAPI_BASE_URL=https://staging.api.com -DAPI_TOKEN=mytoken
```

---

## Go testing {#go}

### Test File Template
```go
package api_test

import (
    "bytes"
    "encoding/json"
    "net/http"
    "os"
    "testing"
)

var baseURL = getEnv("API_BASE_URL", "https://api.example.com")
var apiToken = getEnv("API_TOKEN", "test-token")

func getEnv(key, fallback string) string {
    if v, ok := os.LookupEnv(key); ok { return v }
    return fallback
}

func TestCreateResource_ValidPayload_Returns201(t *testing.T) {
    payload, _ := json.Marshal(map[string]string{"field": "value"})
    req, _ := http.NewRequest("POST", baseURL+"/resource", bytes.NewBuffer(payload))
    req.Header.Set("Authorization", "Bearer "+apiToken)
    req.Header.Set("Content-Type", "application/json")

    resp, err := http.DefaultClient.Do(req)
    if err != nil { t.Fatal(err) }
    defer resp.Body.Close()

    if resp.StatusCode != 201 {
        t.Errorf("expected 201, got %d", resp.StatusCode)
    }
}

func TestCreateResource_NoAuth_Returns401(t *testing.T) {
    payload, _ := json.Marshal(map[string]string{"field": "value"})
    req, _ := http.NewRequest("POST", baseURL+"/resource", bytes.NewBuffer(payload))
    req.Header.Set("Content-Type", "application/json")

    resp, err := http.DefaultClient.Do(req)
    if err != nil { t.Fatal(err) }
    defer resp.Body.Close()

    if resp.StatusCode != 401 {
        t.Errorf("expected 401, got %d", resp.StatusCode)
    }
}
```

### Run
```bash
API_BASE_URL=https://staging.api.com API_TOKEN=mytoken go test ./... -v
```

---

## Newman (Postman CLI) {#newman}

Generate a Postman collection JSON, then run with Newman.

### Collection Structure (JSON)
```json
{
  "info": { "name": "Resource API Tests", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" },
  "item": [
    {
      "name": "POST /resource - valid payload",
      "request": {
        "method": "POST",
        "header": [
          { "key": "Authorization", "value": "Bearer {{api_token}}" },
          { "key": "Content-Type", "value": "application/json" }
        ],
        "body": { "mode": "raw", "raw": "{\"field\": \"value\"}" },
        "url": "{{base_url}}/resource"
      },
      "event": [{
        "listen": "test",
        "script": { "exec": [
          "pm.test('Status 201', () => pm.response.to.have.status(201));",
          "pm.test('Has id', () => pm.expect(pm.response.json()).to.have.property('id'));"
        ]}
      }]
    }
  ]
}
```

### Run
```bash
newman run collection.json \
  --env-var base_url=https://staging.api.com \
  --env-var api_token=mytoken \
  --reporters cli,junit \
  --reporter-junit-export results.xml
```

---

## k6 (Load Testing) {#k6}

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },  // Ramp up
    { duration: '1m', target: 50 },   // Stay at 50 VUs
    { duration: '10s', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],    // Less than 1% errors
  },
};

const BASE_URL = __ENV.API_BASE_URL || 'https://api.example.com';
const TOKEN = __ENV.API_TOKEN || 'test-token';

export default function () {
  const payload = JSON.stringify({ field: 'value' });
  const params = {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${TOKEN}`,
    },
  };

  const res = http.post(`${BASE_URL}/resource`, payload, params);
  check(res, {
    'status is 201': (r) => r.status === 201,
    'has id in body': (r) => JSON.parse(r.body).id !== undefined,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

### Run
```bash
k6 run -e API_BASE_URL=https://staging.api.com -e API_TOKEN=mytoken load-test.js
```

---

## Plain .http Files (VS Code REST Client) {#http-files}

```http
@baseUrl = https://api.example.com
@token = mytoken

### Create resource - valid
POST {{baseUrl}}/resource
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "field": "value"
}

### Create resource - missing field (expect 422)
POST {{baseUrl}}/resource
Authorization: Bearer {{token}}
Content-Type: application/json

{}

### Create resource - no auth (expect 401)
POST {{baseUrl}}/resource
Content-Type: application/json

{
  "field": "value"
}
```