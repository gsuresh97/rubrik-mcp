# What Can It Do

The plugin exposes your entire RSC environment to your AI assistant through natural language. Ask questions the same way you'd ask a colleague — the plugin finds the right tools and synthesizes the answer.

---

## :speech_balloon: Example prompts

**Protection & compliance**
- *"Are all my VMware VMs backed up?"*
- *"Which databases don't have an SLA assigned?"*
- *"Show me objects that are out of SLA compliance"*
- *"What's our backup coverage for AWS EC2 instances?"*

**Incident response**
- *"We have a ransomware alert — what's the blast radius?"*
- *"Do we have a clean snapshot of vm-prod-01 before the incident?"*
- *"Which objects are showing anomalies right now?"*

**Investigation**
- *"Why is database-prod not backing up?"*
- *"When was the last successful backup of fileserver-01?"*
- *"Show me all backup failures in the last 24 hours"*

**Recovery planning**
- *"Can I recover oracle-db-prod to yesterday at 2pm?"*
- *"What recovery options do I have for this VM?"*
- *"Is there a clean snapshot I can restore from?"*

**Cluster & infrastructure**
- *"What's the health status of all my clusters?"*
- *"Which cluster is running out of capacity?"*
- *"Are there any clusters with pending upgrades?"*

**Security & audit**
- *"What did admin@company.com do in RSC yesterday?"*
- *"Show me recent sign-in activity"*
- *"What's our DSCC security score and top recommendations?"*

**Data governance (DSPM)**
- *"What sensitive data do we have exposed?"*
- *"Are there any data policy violations?"*
- *"What's our data governance compliance score?"*

---

## :globe_with_meridians: Coverage

The plugin covers all major RSC domains:

| Domain | What you can ask about |
|---|---|
| **Virtualization** | VMware, Hyper-V, Nutanix, Kubernetes, KubeVirt, VCD, OpenStack, OLVM, Proxmox |
| **Cloud** | AWS (EC2, EBS, RDS), Azure (VMs, SQL), GCP (GCE, Cloud SQL), OCI |
| **Database** | MSSQL, Oracle, SAP HANA, MongoDB, MySQL, Cassandra, PostgreSQL, Informix, Exchange, Db2 |
| **SaaS** | M365 (Exchange Online, SharePoint, Teams, OneDrive), Salesforce, GitHub/DevOps, Atlassian, Okta, Google Workspace |
| **NAS** | Cloud Direct, filesets, Windows Volume Groups |
| **Protection** | SLA policies, snapshots, archival, replication, recovery plans |
| **Security** | Auth, access control, users, certificates, two-person rule, audit logs |
| **Threat** | Ransomware detection, malware/anomaly detection, threat hunting, AIR, IOC feeds |
| **Identity** | Active Directory, Entra ID / Azure AD |
| **DSPM** | Data classification policies, sensitive data exposure, data access |
| **Clusters** | Health, capacity, upgrade status, networking, encryption |
| **Platform** | Orgs, feature flags, notifications, webhooks, DSCC scores |

---

## :zap: Smart workflows

The plugin includes built-in composite workflows that handle multi-step investigations in a single call:

| Ask about | What happens internally |
|---|---|
| Object investigation | Resolves name → checks SLA, snapshots, jobs, permissions → gives root-cause verdict |
| Ransomware triage | Checks all threat detections → assesses blast radius → identifies clean recovery points |
| Pre-recovery check | Validates object → finds confirmed-clean snapshot → lists recovery methods → gives GO/NO-GO |
| Cluster health | Checks all clusters → calculates capacity % → flags version spread and connectivity |
| Protection gaps | Counts unprotected objects by type → separates relics from actionable gaps |
| Identity audit | Checks AD domains and DCs → verifies FSMO role coverage → checks Entra status |
| Database posture | Inventories all database engines → identifies unprotected critical databases |
| Cloud posture | Checks AWS/Azure/GCP accounts → reports protected vs unprotected workloads |
| DSPM posture | Gets sensitive data totals → policy violations → top at-risk objects → DSCC score |

---

## :inbox_tray: On-demand loading

The plugin uses progressive loading to keep startup fast. Additional domains can be loaded on demand:

> *"Load VMware tools"*

or

> *"Load database tools for MSSQL"*

Use `rsc_describe_domains` to see all available domains.
