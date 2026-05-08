# api-skills

> A community-driven collection of Skills for AI agents — providing reusable behaviors, structured references, and ready-to-use integrations to make agent development faster and collaborative.

---

## What is this?

**api-skills** is a curated collection of modular *Skills* designed for AI agents. Each skill encapsulates a specific behavior or capability — such as interacting with an API, processing files, or automating workflows — so agents can reference and reuse them without reinventing the wheel.

Whether you're building a coding assistant, a data pipeline agent, or a multi-step automation bot, this collection gives you a head start.

---

## Repository Structure

```
api-skill/
├── ai-based-api/                # AI-augmented API design, LLM tool definitions, agentic workflows
├── api-analyzer/                # Validate and debug API requests
├── api-compliance/              # GDPR, PCI-DSS, HIPAA, SOC2 compliance patterns
├── api-designer/                # REST API endpoint design and specification
├── api-documentation/           # Generate professional API documentation
├── api-health-monitoring/       # Health checks, SLA definitions, observability
├── api-inference-from-files/    # Infer API endpoints from project file structures
├── api-integration-helper/      # Webhooks, event-driven architectures, API chaining
├── api-mocking/                 # Mock servers, sandbox environments, API stubs
├── api-ratelimit-helper/        # Rate limiting, throttling, and retry strategies
├── api-sdk-generator/           # Generate client SDKs and API wrapper libraries
├── api-security-patterns/       # OAuth, JWT, RBAC, and API security patterns
├── api-to-testcase-generator/   # Generate test cases from API definitions
├── api-versioning-helper/       # API versioning strategies and migration guides
├── graphql-grpc-helper/         # GraphQL schemas and gRPC protobuf definitions
├── newman/
│   ├── newman-cicd-helper/      # Newman CI/CD pipeline configurations
│   ├── newman-report-analyzer/  # Analyze Newman test run results
│   └── newman-script-helper/    # Generate Newman CLI commands
├── openapi-spec-generator/      # Generate OpenAPI 3.x and Swagger 2.0 specs
├── popular-api-fetcher/         # Real-world API examples from well-known platforms
├── postman/
│   ├── postman-collection-generator/  # Generate Postman Collection v2.1 JSON
│   ├── postman-openapi-converter/     # Convert OpenAPI specs to Postman collections
│   ├── postman-testcase-generator/    # Write Postman test scripts
│   └── postman-to-newman/             # Automate Postman collections with Newman
├── installer/                   # Install a complete bundle at once
└── README.md
```

---

## Getting Started

1. **Browse** the `api-skill/` directory to find a skill relevant to your use case.
2. **Read** the skill's `SKILL.md` file — it describes what the skill does, when to trigger it, and how to use it.
3. **Download** the skill in your system as a zip or standalone.
4. **Download** the installer file to install all the skills at once with a single command. More on this in the README.md file inside the `installer/` directory.
5. **Reference** the skill in your agent's system prompt or configuration.

---

## Skill Format

Each skill follows a consistent structure:

```
api-skill/<category>/<skill-name>/
├── SKILL.md       # Description, trigger conditions, and usage instructions
```

A `SKILL.md` file typically includes:

- **Name** — The skill's identifier
- **Description** — What it does and when to use it
- **Trigger Conditions** — Keywords or scenarios that should invoke this skill
- **Instructions** — Step-by-step guidance for the agent

---

> See the root [skills_index.json](../skills_index.json) for the complete machine-readable registry of all skills.

---

## Contributing

Community contributions are what make this repo valuable! You can contribute by:

- **Adding a new skill** for a use case not yet covered
- **Improving an existing skill** with better instructions or examples
- **Sharing example agents** that use skills from this repo

Please read [CONTRIBUTING.md](../CONTRIBUTING.md) before submitting a pull request.

---

## Why This Exists

Building agents that reliably perform specific tasks requires well-structured, tested, and documented behaviors. Instead of every developer writing their own skill logic from scratch, **api skills** provides a shared foundation — so the community can build on each other's work and iterate faster.

---

## License

This repository is open source. See [LICENSE](../LICENSE) for details.

---

*Built for the community, by the community. ⚡*
