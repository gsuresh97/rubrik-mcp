# Platform Setup

The plugin works with any MCP-compatible AI platform. Follow the instructions for your platform below.

---

## Claude Code

Claude Code is the recommended platform — it has the richest integration including skills, slash commands, and native plugin management.

**Install from the plugin marketplace:**
1. Run `/plugins` in Claude Code
2. Search for **Rubrik**
3. Click **Install** and follow the prompts

**Manual configuration** (`.mcp.json` in your project or `~/.claude/.mcp.json` globally):

```json
{
  "mcpServers": {
    "RSC": {
      "command": "/path/to/rsc-server",
      "env": {
        "RSC_ACCOUNTS_FILE": "/path/to/rsc_accounts.json",
        "RSC_ACCOUNT": "prod",
        "RSC_TOOL_PROFILE": "standard"
      }
    }
  }
}
```

---

## Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "RSC": {
      "command": "/path/to/rsc-server",
      "env": {
        "RSC_ACCOUNTS_FILE": "/path/to/rsc_accounts.json",
        "RSC_ACCOUNT": "prod"
      }
    }
  }
}
```

---

## Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "RSC": {
      "command": "/path/to/rsc-server",
      "env": {
        "RSC_ACCOUNTS_FILE": "/path/to/rsc_accounts.json",
        "RSC_ACCOUNT": "prod"
      }
    }
  }
}
```

---

## Cline

1. Open Cline settings → **MCP Servers**
2. Click **Add Server**
3. Set:
   - **Command:** `/path/to/rsc-server`
   - **Environment:** `RSC_ACCOUNTS_FILE=/path/to/rsc_accounts.json`, `RSC_ACCOUNT=prod`

---

## Continue.dev

Add to `~/.continue/config.json` under `mcpServers`:

```json
{
  "mcpServers": [
    {
      "name": "RSC",
      "command": "/path/to/rsc-server",
      "env": {
        "RSC_ACCOUNTS_FILE": "/path/to/rsc_accounts.json",
        "RSC_ACCOUNT": "prod"
      }
    }
  ]
}
```

---

## VS Code Copilot

Add to your VS Code `settings.json`:

```json
{
  "github.copilot.chat.mcp.servers": {
    "RSC": {
      "command": "/path/to/rsc-server",
      "env": {
        "RSC_ACCOUNTS_FILE": "/path/to/rsc_accounts.json",
        "RSC_ACCOUNT": "prod"
      }
    }
  }
}
```

---

## Gemini CLI

Add to `~/.gemini/settings.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "RSC": {
      "command": "/path/to/rsc-server",
      "env": {
        "RSC_ACCOUNTS_FILE": "/path/to/rsc_accounts.json",
        "RSC_ACCOUNT": "prod"
      }
    }
  }
}
```

---

## OpenAI Agents SDK

Use the included system prompt template when initializing your agent:

```python
from agents import Agent, MCPServerStdio

rsc_server = MCPServerStdio(
    params={
        "command": "/path/to/rsc-server",
        "env": {
            "RSC_ACCOUNTS_FILE": "/path/to/rsc_accounts.json",
            "RSC_ACCOUNT": "prod",
        },
    }
)

agent = Agent(
    name="RSC Assistant",
    instructions="You are a Rubrik Security Cloud assistant...",
    mcp_servers=[rsc_server],
)
```

See [`openai-agents-system-prompt.md`](../openai-agents-system-prompt.md) in the release archive for the full system prompt.

---

## Tool profile

Set `RSC_TOOL_PROFILE` to control how many tools load at startup:

| Value | Tools loaded | Best for |
|---|---|---|
| `minimal` | ~120 | Fast startup, on-demand loading |
| `standard` | ~1,700 | General use (default) |
| `full` | ~3,100 | All tools including writes |

The plugin supports on-demand tool loading — start with `minimal` and load additional domains as needed using `rsc_load_domain`.
