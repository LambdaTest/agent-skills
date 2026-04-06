# Common OpenAPI Patterns

## Pagination

### Cursor-based (recommended for large datasets)
```yaml
components:
  schemas:
    CursorPage:
      type: object
      required: [items, pagination]
      properties:
        items:
          type: array
          items: {}
        pagination:
          type: object
          properties:
            nextCursor:
              type: string
              nullable: true
              example: "eyJpZCI6MTAwfQ=="
            prevCursor:
              type: string
              nullable: true
            hasMore:
              type: boolean

  parameters:
    CursorParam:
      name: cursor
      in: query
      schema:
        type: string
    LimitParam:
      name: limit
      in: query
      schema:
        type: integer
        format: int32
        minimum: 1
        maximum: 100
        default: 20
```

### Offset-based
```yaml
components:
  schemas:
    OffsetPage:
      type: object
      required: [items, total, page, pageSize]
      properties:
        items:
          type: array
          items: {}
        total:
          type: integer
          format: int64
        page:
          type: integer
          format: int32
        pageSize:
          type: integer
          format: int32
        totalPages:
          type: integer
          format: int32

  parameters:
    PageParam:
      name: page
      in: query
      schema:
        type: integer
        default: 1
        minimum: 1
    PageSizeParam:
      name: pageSize
      in: query
      schema:
        type: integer
        default: 20
        minimum: 1
        maximum: 100
```

---

## Problem Details (RFC 7807)

Standard error body format — use instead of ad-hoc error schemas:

```yaml
components:
  schemas:
    ProblemDetails:
      type: object
      properties:
        type:
          type: string
          format: uri
          example: https://api.example.com/errors/not-found
        title:
          type: string
          example: Resource Not Found
        status:
          type: integer
          example: 404
        detail:
          type: string
          example: User with id '123' does not exist.
        instance:
          type: string
          format: uri
          example: /users/123
        errors:
          type: object
          additionalProperties:
            type: array
            items:
              type: string
          description: Field-level validation errors

  responses:
    BadRequest:
      description: Validation error
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetails"
    NotFound:
      description: Resource not found
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetails"
    Unauthorized:
      description: Authentication required
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetails"
    Forbidden:
      description: Insufficient permissions
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetails"
    TooManyRequests:
      description: Rate limit exceeded
      headers:
        Retry-After:
          schema:
            type: integer
          description: Seconds to wait before retrying
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetails"
    InternalError:
      description: Unexpected server error
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/ProblemDetails"
```

---

## File Upload

### Multipart form (file + metadata)
```yaml
paths:
  /uploads:
    post:
      summary: Upload a file
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required: [file]
              properties:
                file:
                  type: string
                  format: binary
                  description: File to upload (max 10MB)
                description:
                  type: string
                  maxLength: 500
                tags:
                  type: array
                  items:
                    type: string
            encoding:
              file:
                contentType: image/png, image/jpeg, application/pdf
      responses:
        "201":
          description: File uploaded
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UploadedFile"
```

### Binary upload (raw body)
```yaml
paths:
  /files/{fileId}/content:
    put:
      summary: Replace file content
      parameters:
        - name: fileId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
      responses:
        "204":
          description: Content replaced
```

---

## Webhooks (OAS 3.1)

```yaml
webhooks:
  orderCreated:
    post:
      summary: New order notification
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/OrderEvent"
      responses:
        "200":
          description: Webhook acknowledged
```

---

## HATEOAS Links

```yaml
components:
  schemas:
    Link:
      type: object
      properties:
        href:
          type: string
          format: uri
        rel:
          type: string
        method:
          type: string
          enum: [GET, POST, PUT, PATCH, DELETE]

    ResourceWithLinks:
      allOf:
        - $ref: "#/components/schemas/Resource"
        - type: object
          properties:
            _links:
              type: object
              additionalProperties:
                $ref: "#/components/schemas/Link"
              example:
                self:
                  href: /users/123
                  rel: self
                  method: GET
                update:
                  href: /users/123
                  rel: update
                  method: PATCH
```

---

## Sorting and Filtering

```yaml
components:
  parameters:
    SortParam:
      name: sort
      in: query
      description: "Sort field, prefix with - for descending. E.g. -createdAt,name"
      schema:
        type: string
        example: "-createdAt"

    FilterParam:
      name: filter
      in: query
      description: "Filter expression. E.g. status=active&role=admin"
      style: deepObject
      explode: true
      schema:
        type: object
        additionalProperties:
          type: string
```

---

## Versioning Patterns

### URL versioning (most common)
```yaml
servers:
  - url: https://api.example.com/v1
  - url: https://api.example.com/v2
```

### Header versioning
```yaml
components:
  parameters:
    ApiVersion:
      name: API-Version
      in: header
      required: false
      schema:
        type: string
        enum: ["2023-01", "2024-01"]
        default: "2024-01"
```

---

## Rate Limiting Headers

Document rate limit headers in responses:
```yaml
components:
  headers:
    X-RateLimit-Limit:
      description: Maximum requests per window
      schema:
        type: integer
    X-RateLimit-Remaining:
      description: Remaining requests in current window
      schema:
        type: integer
    X-RateLimit-Reset:
      description: UTC epoch seconds when window resets
      schema:
        type: integer
        format: int64
```

Apply to responses:
```yaml
responses:
  "200":
    headers:
      X-RateLimit-Limit:
        $ref: "#/components/headers/X-RateLimit-Limit"
      X-RateLimit-Remaining:
        $ref: "#/components/headers/X-RateLimit-Remaining"
      X-RateLimit-Reset:
        $ref: "#/components/headers/X-RateLimit-Reset"
```

---

## Idempotency Key

```yaml
components:
  parameters:
    IdempotencyKey:
      name: Idempotency-Key
      in: header
      required: false
      description: |
        Client-generated UUID for idempotent POST requests.
        Same key returns cached response if request was already processed.
      schema:
        type: string
        format: uuid
        example: 123e4567-e89b-12d3-a456-426614174000
```