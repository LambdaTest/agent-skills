# agent-skills

> A community-driven collection of Skills for AI agents — providing reusable behaviors, structured references, and ready-to-use integrations to make agent development faster and collaborative.

---

## What is this?

**agent-skills** is a curated repository of modular *Skills* designed for AI agents. Each skill encapsulates a specific behavior or capability — such as interacting with an API, processing files, or automating workflows — so agents can reference and reuse them without reinventing the wheel.

Whether you're building a coding assistant, a data pipeline agent, or a multi-step automation bot, this repo gives you a head start.

---

## Repository Structure

```
agent-skills/
├── skills/
│   ├── api/               # Skills for interacting with external APIs
│   ├── file-handling/     # Skills for reading, writing, and transforming files
│   ├── data-processing/   # Skills for parsing, cleaning, and analyzing data
│   └── ...                # More categories coming soon
|── installer/             # Help you install a complete bundle at once
├── examples/              # Example agents using skills from this repo
├── CONTRIBUTING.md        # Contribution guidelines
└── README.md
```

---

## Getting Started

1. **Browse** the `skills/` directory to find a skill relevant to your use case.
2. **Read** the skill's `SKILL.md` file — it describes what the skill does, when to trigger it, and how to use it.
3. **Download** the skill in your system as a zip or standalone.
4. **Download** the installer file to install all the skills at once with a single command. More on this in the README.md file inside the `installer/` directory.
5. **Reference** the skill in your agent's system prompt or configuration.

---

## Skill Format

Each skill follows a consistent structure:

```
skills/<category>/<skill-name>/
├── SKILL.md       # Description, trigger conditions, and usage instructions
└── examples/      # Optional usage examples
```

A `SKILL.md` file typically includes:

- **Name** — The skill's identifier
- **Description** — What it does and when to use it
- **Trigger Conditions** — Keywords or scenarios that should invoke this skill
- **Instructions** — Step-by-step guidance for the agent

---

> More skills are being added regularly. See ___ for the full list.

---

## Contributing

Community contributions are what make this repo valuable! You can contribute by:

- **Adding a new skill** for a use case not yet covered
- **Improving an existing skill** with better instructions or examples
- **Sharing example agents** that use skills from this repo

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before submitting a pull request.

---

## Why This Exists

Building agents that reliably perform specific tasks requires well-structured, tested, and documented behaviors. Instead of every developer writing their own skill logic from scratch, **agent-skills** provides a shared foundation — so the community can build on each other's work and iterate faster.

---

## License

This repository is open source. See [LICENSE](./LICENSE) for details.

---

*Built for the community, by the community. ⚡*
