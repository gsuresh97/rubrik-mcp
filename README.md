# Rubrik MCP Plugin for AI Assistants

Connect your AI assistant to Rubrik Security Cloud. Ask natural-language questions about backup protection, ransomware detections, SLA compliance, cluster health, and recovery readiness — and get answers directly from your RSC environment.

> **Read-only by default.** All queries run without making changes. Write operations (backup, restore, SLA assignment) are opt-in and require explicit configuration.

---

## :rocket: Quick Start

**1. Download the binary** for your platform from [Releases](../../releases):

| Platform | Binary |
|---|---|
| macOS (Apple Silicon) | `rsc-server-darwin-arm64` |
| macOS (Intel) | `rsc-server-darwin-amd64` |
| Linux (x86-64) | `rsc-server-linux-amd64` |
| Linux (ARM64) | `rsc-server-linux-arm64` |
| Windows | `rsc-server-windows-amd64.exe` |

**2. Create your accounts file** at `~/.rsc/accounts.json`:

```json
{
  "prod": "/path/to/your-service-account.json"
}
```

**3. Set environment variables:**

```bash
export RSC_ACCOUNTS_FILE=~/.rsc/accounts.json
export RSC_ACCOUNT=prod
```

Then configure your AI platform — see [Platform Setup](docs/platforms.md).

---

## :computer: Supported Platforms

| Platform | Status |
|---|---|
| Claude Code | :white_check_mark: Fully supported |
| Cursor | :white_check_mark: Fully supported |
| Windsurf | :white_check_mark: Fully supported |
| Cline | :white_check_mark: Fully supported |
| Continue.dev | :white_check_mark: Fully supported |
| VS Code Copilot | :white_check_mark: Fully supported |
| Gemini CLI | :white_check_mark: Fully supported |
| OpenAI Agents SDK | :white_check_mark: Fully supported |

---

## :blue_book: Documentation

| Guide | Description |
|---|---|
| [Getting Started](docs/getting-started.md) | Download, install, and run your first query |
| [Authentication](docs/authentication.md) | Create an RSC service account and configure credentials |
| [Platform Setup](docs/platforms.md) | Step-by-step configuration for each supported AI platform |
| [What Can It Do](docs/what-can-it-do.md) | Domains covered, example prompts, and common workflows |
| [Write Operations](docs/write-operations.md) | Enable backup, restore, and SLA management operations |
| [Troubleshooting](docs/troubleshooting.md) | Common errors and how to resolve them |

---

## :shield: Security

The plugin authenticates using an RSC service account with OAuth2 client credentials. No credentials are sent to any third party — all API calls go directly from your machine to your RSC instance.

---

## :handshake: Support

- **Issues:** [GitHub Issues](../../issues)
- **Rubrik Support:** [support.rubrik.com](https://support.rubrik.com)
