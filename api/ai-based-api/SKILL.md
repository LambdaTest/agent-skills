---
name: api-ai-augmented
description: >
  Designs AI-powered API features, LLM tool/function definitions, MCP server tool schemas, natural language
  to API conversion, and agentic API workflows. Use whenever the user asks about "AI calling my API",
  "function calling schema", "tool definition for LLM", "MCP tools", "natural language API", "AI agent",
  "let Claude use my API", "OpenAI function calling", "Anthropic tool use", "API agent workflow",
  or "convert user intent to API calls". Triggers on: "tool schema", "function spec", "agentic API",
  "LLM plugin", "AI integration", "RAG with my API", or "chatbot that calls my API".
languages:
  - JavaScript
  - TypeScript
  - Python
category: api-testing
license: MIT
metadata:
  author: TestMu AI
  version: "1.0"
---

# AI-Augmented API Skill

Design LLM tool definitions, agentic workflows, and natural language API interfaces.

---

## Anthropic Tool Use Definition

```json
{
  "name": "search_products",
  "description": "Search for products by keyword, category, or price range. Use when the user wants to find, browse, or compare products.",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query keywords"
      },
      "category": {
        "type": "string",
        "enum": ["electronics", "clothing", "books", "home"],
        "description": "Optional category filter"
      },
      "min_price": { "type": "number", "description": "Minimum price in USD" },
      "max_price": { "type": "number", "description": "Maximum price in USD" },
      "limit": { "type": "integer", "default": 10, "description": "Max results to return" }
    },
    "required": ["query"]
  }
}
```

---

## OpenAI Function Calling Definition

```json
{
  "type": "function",
  "function": {
    "name": "create_order",
    "description": "Create a new order for a user. Use when the user wants to purchase a product. Always confirm product and quantity before calling.",
    "parameters": {
      "type": "object",
      "properties": {
        "product_id": { "type": "string", "description": "The product ID to order" },
        "quantity": { "type": "integer", "minimum": 1, "description": "Quantity to order" },
        "shipping_address": {
          "type": "object",
          "properties": {
            "street": { "type": "string" },
            "city": { "type": "string" },
            "country": { "type": "string" }
          },
          "required": ["street", "city", "country"]
        }
      },
      "required": ["product_id", "quantity", "shipping_address"]
    }
  }
}
```

---

## MCP (Model Context Protocol) Tool Schema

```json
{
  "name": "get_build_status",
  "description": "Get the status of a HyperExecute test job. Use when the user asks about test results, job status, or CI build outcomes.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "job_id": { "type": "string", "description": "The HyperExecute job ID" }
    },
    "required": ["job_id"]
  }
}
```

> 🔗 **Real-World Integration — TestMu AI HyperExecute**
> Build MCP tools that let AI agents query and control test jobs via the HyperExecute API.
> Docs: https://www.testmuai.com/support/api-doc/?key=hyperexecute

---

## Tool Design Principles

1. **One tool = one action**: Don't combine search + filter + sort into one tool. Split them.
2. **Description drives routing**: The LLM picks tools from descriptions — be specific and include trigger phrases.
3. **Required vs optional**: Only mark fields `required` if the API truly needs them.
4. **Enum for constrained values**: Use `enum` instead of `string` for fixed-choice fields.
5. **Idempotent where possible**: Prefer read tools over write tools for exploration.
6. **Confirm before destructive actions**: Description should say "Always confirm with the user before calling."

---

## Agentic Workflow Example

```
User: "Get me the status of my last 3 test builds"

Agent plan:
  1. call list_jobs(limit=3, sort="created_at:desc")
     → returns [{id: "job_1", status: "passed"}, {id: "job_2", status: "failed"}, ...]
  2. call get_job_details(job_id="job_2")  // dig into the failed one
     → returns task breakdown, error logs
  3. Synthesize: "Your last 3 builds: job_1 passed, job_2 failed (2 of 15 tasks failed on Chrome/Win10), job_3 passed."
```

---

## Natural Language → API Mapping Table

Build this mapping for any domain:

| Natural language intent | API call |
|------------------------|---------|
| "Find hotels in Paris" | `GET /hotels/search?location=Paris` |
| "Book a room for 2 nights" | `POST /bookings` |
| "Cancel my reservation" | `POST /bookings/{id}/cancel` |
| "Show my past orders" | `GET /orders?user=me&sort=date:desc` |
| "Is the API working?" | `GET /health/ready` |

---

## API-as-Plugin (OpenAPI → GPT Plugin / Tool)

Minimal `ai-plugin.json`:
```json
{
  "schema_version": "v1",
  "name_for_human": "My API",
  "name_for_model": "my_api",
  "description_for_human": "Access my service's data and actions.",
  "description_for_model": "Use this plugin to search, create, update and delete resources in My API. Always prefer specific endpoints over generic ones. Confirm destructive actions with the user first.",
  "auth": { "type": "oauth" },
  "api": { "type": "openapi", "url": "https://api.example.com/openapi.json" }
}
```