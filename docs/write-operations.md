# Write Operations

By default, the plugin is **read-only**. All queries run without making any changes to your RSC environment. Write operations — backups, restores, SLA assignment, and configuration changes — are available but require explicit opt-in.

---

## :white_check_mark: Enabling write operations

Set `RSC_WRITE_ENABLED=true` in your platform configuration to enable write operations:

```json
{
  "mcpServers": {
    "RSC": {
      "command": "/path/to/rsc-server",
      "env": {
        "RSC_ACCOUNTS_FILE": "/path/to/rsc_accounts.json",
        "RSC_ACCOUNT": "prod",
        "RSC_WRITE_ENABLED": "true"
      }
    }
  }
}
```

---

## :warning: Destructive operations

Some operations are irreversible — restores that overwrite live data, SLA policy removals, encryption key changes. These require an additional environment variable:

```bash
RSC_DESTRUCTIVE_ENABLED=true
```

Every destructive operation also requires you to provide an **audit note** explaining why the action is being taken. The AI assistant will prompt you for this before proceeding.

---

## :shield: Safety model

The plugin uses a three-layer protection model for all write operations:

**Layer 1 — Approval gate**
Every write operation pauses and requires your explicit approval before executing. Your AI assistant will describe exactly what will happen and ask you to confirm.

**Layer 2 — Environment gates**
- Additive operations (on-demand backup, live mount, SLA assignment): `RSC_WRITE_ENABLED=true`
- Irreversible operations (restore, delete, encryption changes): `RSC_WRITE_ENABLED=true` + `RSC_DESTRUCTIVE_ENABLED=true`

**Layer 3 — Blast radius cap**
Before executing any destructive operation, the plugin:
1. Resolves all affected object names (no anonymous UUIDs)
2. Counts how many objects will be affected
3. Refuses to proceed if the count exceeds the cap (default: 10 objects) without explicit override
4. Requires `dry_run=true` first if the blast radius is large

This prevents an AI from silently cascading a destructive operation to hundreds of objects.

---

## :pencil: What write operations are available

| Category | Examples |
|---|---|
| **On-demand backup** | Trigger backup now for a VM, database, or fileset |
| **SLA management** | Assign, update, or remove SLA policies |
| **Recovery** | Live mount, restore, export snapshots |
| **Archival** | Create and manage archival targets |
| **Cluster management** | Manage networking, encryption, upgrades |
| **Security** | Manage users, roles, certificates, TPR workflows |

---

## :bulb: Example

With `RSC_WRITE_ENABLED=true`:

> *"Trigger an on-demand backup of vm-prod-01"*

The assistant will confirm the target, show you what will happen, and ask for your approval before proceeding.

With `RSC_DESTRUCTIVE_ENABLED=true`:

> *"Restore oracle-db to the snapshot from last Tuesday"*

The assistant will identify the correct snapshot, show you the full restore plan including what will be overwritten, require an audit note, and ask for explicit confirmation.
