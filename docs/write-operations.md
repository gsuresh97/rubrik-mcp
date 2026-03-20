# Write Operations

By default, the plugin is **read-only**. All queries run without making any changes to your RSC environment. Write operations — backups, restores, SLA assignment, and configuration changes — are available but require explicit opt-in.

---

## Enabling write operations

Set `RSC_WRITE_ENABLED=true` in your platform configuration:

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

## Destructive operations

Some operations are irreversible — restores that overwrite live data, SLA policy removals, encryption key changes. These require an additional variable:

```bash
RSC_DESTRUCTIVE_ENABLED=true
```

Every destructive operation also requires an **audit note** explaining why the action is being taken. The assistant will prompt you for this before proceeding.

---

## Safety model

The plugin uses a three-layer protection model:

**Layer 1 — Approval gate**
Every write operation pauses and requires your explicit approval. The assistant describes exactly what will happen and asks you to confirm.

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

## Available write operations

| Category | Examples |
|---|---|
| **On-demand backup** | Trigger backup now for any VM, database, fileset, or cloud workload |
| **SLA management** | Assign, update, remove, or pause SLA policies; bulk-assign across hierarchies |
| **Recovery** | Live mount, instant recovery, in-place restore, export snapshots |
| **Virtualization** | Backup, export, mount, and restore VMware, Hyper-V, Nutanix, Kubernetes, OpenStack, OLVM, Proxmox, VCD |
| **Cloud** | On-demand snapshots and restores for EC2, EBS, RDS, Azure VMs, managed disks, SQL databases, GCP instances |
| **Databases** | On-demand backup and restore for MSSQL, Oracle, SAP HANA, MongoDB, MySQL, PostgreSQL, Cassandra, Db2, Informix, Exchange |
| **SaaS** | Backup and restore for M365 (Exchange, SharePoint, Teams, OneDrive), Salesforce, GitHub, Atlassian, Okta, Google Workspace |
| **NAS** | Recover files and shares from Cloud Direct and fileset snapshots |
| **Archival** | Create and manage archival targets; tier snapshots; manage reader targets |
| **Replication** | Configure replication pairs; enable, disable, and pause replication |
| **Recovery plans** | Create, update, and execute orchestrated recovery plans and failover groups |
| **Legal hold** | Place and dissolve legal holds on snapshots |
| **Managed volumes** | Create, resize, open/close, and snapshot managed volumes |
| **Cluster management** | Manage networking, NTP, DNS, certificates, upgrades, node operations, encryption keys |
| **Security** | Manage users, roles, service accounts, certificates, TPR workflows, IP allowlists, MFA settings |
| **Identity** | Restore Active Directory objects, domains, and forests; restore Entra ID / Azure AD objects |
| **Threat** | Quarantine and release snapshots; start and cancel threat hunts; manage AIR policies |
| **DSPM** | Create and update data classification policies; manage SONAR crawls; update policy objects |
| **Platform** | Manage orgs, notifications, webhooks, event digests, OAuth apps, feature flags |

---

## Example

With `RSC_WRITE_ENABLED=true`:

> *"Trigger an on-demand backup of vm-prod-01"*

The assistant will confirm the target, show you what will happen, and ask for your approval before proceeding.

With `RSC_DESTRUCTIVE_ENABLED=true`:

> *"Restore oracle-db to the snapshot from last Tuesday"*

The assistant will identify the correct snapshot, show you the full restore plan including what will be overwritten, require an audit note, and ask for explicit confirmation.
