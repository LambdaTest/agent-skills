# OpenAPI Parsing Guide

How to extract test-relevant data from OpenAPI 3.x and Swagger 2.0 specs.

---

## Key Fields to Extract

### From each `paths` entry:

```yaml
paths:
  /users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
```

Extract:
- **Path params**: `id` is required, must be a UUID → test with valid UUID, invalid UUID, missing (404)
- **Status codes**: `200` (success), `404` (not found) → create a test for each

### From `requestBody`:

```yaml
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        required: [name, email]
        properties:
          name:
            type: string
            minLength: 1
            maxLength: 100
          email:
            type: string
            format: email
          age:
            type: integer
            minimum: 0
            maximum: 150
```

Extract:
- **Required fields**: `name`, `email` → each needs a "missing field" test
- **Optional fields**: `age` → test with and without it
- **Constraints**:
  - `name`: minLength 1 → test empty string; maxLength 100 → test 101-char string
  - `email`: format email → test invalid email format
  - `age`: minimum 0 → test -1; maximum 150 → test 151

### From `components/securitySchemes`:

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
```

→ All secured endpoints need: no-auth test (401), invalid-token test (401)

---

## Deriving Edge Cases from Schema Types

| Schema type/constraint | Tests to generate |
|---|---|
| `required: true` | Missing field → 400/422 |
| `type: string, minLength: N` | Length N-1 (fail), length N (pass) |
| `type: string, maxLength: N` | Length N (pass), length N+1 (fail) |
| `type: string, format: email` | Invalid email → 400/422 |
| `type: string, format: uuid` | Non-UUID string → 400 |
| `type: string, format: date-time` | Invalid date → 400 |
| `type: integer, minimum: N` | N-1 (fail), N (pass) |
| `type: integer, maximum: N` | N (pass), N+1 (fail) |
| `enum: [a, b, c]` | Value not in enum → 400/422 |
| `nullable: true` | null value → should pass |
| `nullable: false` (default) | null value → 400/422 |
| `type: array, minItems: N` | N-1 items (fail), N items (pass) |
| `type: array, maxItems: N` | N items (pass), N+1 items (fail) |

---

## Resolving `$ref`

When a schema uses `$ref: '#/components/schemas/User'`, look up the referenced schema in `components/schemas` and apply the same field extraction logic recursively.

---

## Extracting Example Values

OpenAPI specs often include `example` or `examples` fields — use these as the basis for your "valid payload" in happy-path tests:

```yaml
properties:
  email:
    type: string
    format: email
    example: alice@example.com
```

→ Use `alice@example.com` in your valid payload test.

---

## Swagger 2.0 Differences

| Feature | OpenAPI 3.x | Swagger 2.0 |
|---|---|---|
| Request body | `requestBody` | `parameters` with `in: body` |
| Responses | `content` + media type | `schema` directly on response |
| Auth | `components/securitySchemes` | `securityDefinitions` |
| Servers | `servers[].url` | `host` + `basePath` + `schemes` |

Adjust extraction logic accordingly when parsing Swagger 2.0 files.