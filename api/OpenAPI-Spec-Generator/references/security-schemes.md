# Security Schemes Reference

## OpenAPI 3.x (`components/securitySchemes`)

### Bearer JWT (most common)
```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT access token. Obtain via /auth/token.
        Include as: Authorization: Bearer <token>

security:
  - BearerAuth: []
```

### API Key — Header
```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key issued from the developer portal.

security:
  - ApiKeyAuth: []
```

### API Key — Query (avoid in production; leaks in logs)
```yaml
components:
  securitySchemes:
    QueryApiKey:
      type: apiKey
      in: query
      name: api_key
```

### OAuth 2.0 — Authorization Code
```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/oauth/authorize
          tokenUrl: https://auth.example.com/oauth/token
          refreshUrl: https://auth.example.com/oauth/refresh
          scopes:
            read:users: Read user profiles
            write:users: Create and update users
            admin: Full administrative access

security:
  - OAuth2: [read:users]
```

### OAuth 2.0 — Client Credentials (machine-to-machine)
```yaml
components:
  securitySchemes:
    ClientCredentials:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://auth.example.com/oauth/token
          scopes:
            api:read: Read access
            api:write: Write access
```

### OAuth 2.0 — Password (legacy, avoid)
```yaml
components:
  securitySchemes:
    PasswordFlow:
      type: oauth2
      flows:
        password:
          tokenUrl: https://auth.example.com/oauth/token
          scopes:
            read: Read access
```

### OAuth 2.0 — Implicit (deprecated, avoid)
```yaml
components:
  securitySchemes:
    ImplicitFlow:
      type: oauth2
      flows:
        implicit:
          authorizationUrl: https://auth.example.com/oauth/authorize
          scopes:
            read: Read access
```

### Basic Auth
```yaml
components:
  securitySchemes:
    BasicAuth:
      type: http
      scheme: basic
      description: Base64-encoded username:password. Only use over HTTPS.
```

### OpenID Connect
```yaml
components:
  securitySchemes:
    OpenIDConnect:
      type: openIdConnect
      openIdConnectUrl: https://auth.example.com/.well-known/openid-configuration
```

### Multiple Schemes (AND — both required)
```yaml
# Operation requires BOTH API key AND Bearer token
security:
  - ApiKeyAuth: []
    BearerAuth: []
```

### Multiple Schemes (OR — either works)
```yaml
# Operation accepts either API key OR Bearer token
security:
  - ApiKeyAuth: []
  - BearerAuth: []
```

### Public endpoint (override global security)
```yaml
paths:
  /health:
    get:
      summary: Health check
      security: []   # No auth required
      responses:
        "200":
          description: OK
```

---

## Swagger 2.0 (`securityDefinitions`)

### Bearer JWT
```yaml
securityDefinitions:
  BearerAuth:
    type: apiKey
    name: Authorization
    in: header
    description: "JWT token. Format: Bearer <token>"

security:
  - BearerAuth: []
```
> Note: Swagger 2.0 has no `http` type; simulate bearer with `apiKey`.

### API Key
```yaml
securityDefinitions:
  ApiKeyAuth:
    type: apiKey
    name: X-API-Key
    in: header
```

### OAuth 2.0
```yaml
securityDefinitions:
  OAuth2:
    type: oauth2
    flow: accessCode
    authorizationUrl: https://auth.example.com/oauth/authorize
    tokenUrl: https://auth.example.com/oauth/token
    scopes:
      read:users: Read user profiles
      write:users: Modify users
```

### Basic Auth
```yaml
securityDefinitions:
  BasicAuth:
    type: basic
```