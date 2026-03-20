# Rubrik MCP Plugin for AI Assistants

Connect your AI assistant to Rubrik Security Cloud. Ask natural-language questions about backup protection, ransomware detections, SLA compliance, cluster health, and recovery readiness — and get answers directly from your RSC environment.

!!! note "Read-only by default"
    All queries run without making changes to your environment. Write operations are opt-in and require explicit configuration — see [Write Operations](write-operations.md).

---

## Quick Start

**1.** [Download the binary](https://github.com/rubrikinc/rubrik-mcp/releases) for your platform.

**2.** Create `~/.rsc/accounts.json`:

```json
{
  "prod": "/path/to/your-service-account.json"
}
```

**3.** Set environment variables:

```bash
export RSC_ACCOUNTS_FILE=~/.rsc/accounts.json
export RSC_ACCOUNT=prod
```

**4.** Configure your AI platform — see [Platform Setup](platforms.md).

---

## Supported Platforms

| Platform | Status |
|---|---|
| Claude Code | ✅ Fully supported |
| Cursor | ✅ Fully supported |
| Windsurf | ✅ Fully supported |
| Cline | ✅ Fully supported |
| Continue.dev | ✅ Fully supported |
| VS Code Copilot | ✅ Fully supported |
| Gemini CLI | ✅ Fully supported |
| OpenAI Agents SDK | ✅ Fully supported |

---

## What's in This Docs

| | |
|---|---|
| [Getting Started](getting-started.md) | Download, install, and run your first query |
| [Authentication](authentication.md) | Create an RSC service account and configure credentials |
| [Platform Setup](platforms.md) | Configuration for Claude Code, Cursor, Windsurf, and more |
| [What Can It Do](what-can-it-do.md) | Example prompts and full domain coverage |
| [Write Operations](write-operations.md) | Enable backups, restores, and configuration changes |
| [Troubleshooting](troubleshooting.md) | Common issues and fixes |
