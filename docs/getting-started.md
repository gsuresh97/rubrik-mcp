# Getting Started

## Prerequisites

- An active Rubrik Security Cloud account
- An RSC service account with appropriate permissions (see [Authentication](authentication.md))
- One of the [supported AI platforms](platforms.md)

---

## Installation

### Claude Code (recommended)

If you use Claude Code, the plugin is available directly from the plugin marketplace:

1. Open Claude Code
2. Run `/plugins` and search for **Rubrik**
3. Click **Install**
4. Set your environment variables (see below)
5. Run `/reload-plugins`

### Manual installation

1. Download the binary for your platform from [GitHub Releases](../../releases)

2. Make the binary executable (macOS/Linux):
   ```bash
   chmod +x rsc-server-darwin-arm64   # adjust for your platform
   ```

3. Place it somewhere on your PATH, or note the full path for your platform config.

---

## Configuration

Create an accounts file at `~/.rsc/accounts.json`:

```json
{
  "prod": "/path/to/your-service-account.json"
}
```

Set these environment variables:

```bash
export RSC_ACCOUNTS_FILE=~/.rsc/accounts.json
export RSC_ACCOUNT=prod
```

For persistent configuration, add these to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.).

---

## Verify it works

Once installed and configured, try asking your AI assistant:

> *"What is the health status of my Rubrik clusters?"*

You should get a response with live data from your RSC environment.

---

## Next steps

- [Authenticate with a service account](authentication.md)
- [Configure your platform](platforms.md)
- [See what the plugin can do](what-can-it-do.md)
