# MCP servers

Servers rook itself, and the agents under test, may reach. Flags mirror
`claude mcp`.

```bash
rook mcp list --json
rook mcp get <name> --json
rook mcp add <name> -- <command> [args...]
rook mcp add <name> -t http --url https://host/mcp -H 'Authorization: Bearer ${TOKEN}'
rook mcp add <name> -s project -e KEY=VALUE -- <command>
rook mcp remove <name> -s project
rook mcp enable <name>
rook mcp disable <name>
rook mcp approve <name> --origin discovered
```

Scopes: `user`, `project`, `local` (default). `project` scope is
`.testmuai/rook/mcp.json`, a file rook itself writes — a different thing from
a server `explore` finds already declared in the target. `approve` trusts a
`project` or `discovered` server after rook has read what it runs; those are
the only two origins that wait for it. A `user` or `local` server is used as
declared, with no approval step.

When `explore` finds `.mcp.json` in the target, those servers appear with
origin `discovered` and need `approve` before a scenario can exercise them.
Values stay `${VAR}` references in `get` output.
