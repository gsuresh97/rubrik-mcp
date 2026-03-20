# Authentication

The plugin authenticates with RSC using a **service account** with OAuth2 client credentials. No credentials are stored by Claude or any AI platform — all API calls go directly from your machine to your RSC instance.

---

## :lock: Create an RSC service account

1. Log into RSC and navigate to **Settings → User Management → Service Accounts**
2. Click **Create Service Account**
3. Give it a name (e.g. `mcp-plugin`)
4. Assign the appropriate role:
   - **Read-only use:** Assign the built-in `Read-only` role
   - **Write operations:** Assign a role with the permissions you want to delegate (see [Write Operations](write-operations.md))
5. Click **Create** and download the service account JSON file

> Keep this file secure — it contains credentials that grant access to your RSC environment.

---

## :memo: Configure the accounts file

The plugin uses an accounts file to support multiple RSC environments (prod, dev, staging, etc.).

Create `~/.rsc/accounts.json`:

```json
{
  "prod": "/path/to/prod-service-account.json"
}
```

For multiple environments:

```json
{
  "prod": "/path/to/prod-service-account.json",
  "dev":  "/path/to/dev-service-account.json"
}
```

---

## :wrench: Environment variables

| Variable | Required | Description |
|---|---|---|
| `RSC_ACCOUNTS_FILE` | Yes | Path to your accounts JSON file |
| `RSC_ACCOUNT` | Yes | Name of the active account (e.g. `prod`) |
| `RSC_TIMEOUT_SECONDS` | No | HTTP timeout in seconds (default: 30) |

### Single-account shortcut

If you only have one environment, you can use:

| Variable | Description |
|---|---|
| `RSC_SERVICE_ACCOUNT_FILE` | Direct path to the service account JSON file |
| `RSC_BASE_URL` | RSC base URL (e.g. `https://mycompany.my.rubrik.com`) |
| `RSC_CLIENT_ID` | Service account client ID |
| `RSC_CLIENT_SECRET` | Service account client secret |

---

## :mag: Targeting a specific environment

Pass `account="dev"` in any prompt to target a non-default environment:

> *"Show me cluster health in the dev environment"*

The plugin passes this to every tool call automatically.
