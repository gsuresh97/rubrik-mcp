# Troubleshooting

---

## The plugin isn't connecting

**Check your environment variables are set:**
```bash
echo $RSC_ACCOUNTS_FILE
echo $RSC_ACCOUNT
```

**Check the accounts file exists and is valid JSON:**
```bash
cat $RSC_ACCOUNTS_FILE
```

**Check the service account file is accessible:**
```bash
cat /path/to/your-service-account.json
```

**Verify your RSC base URL is reachable:**
```bash
curl -s https://yourcompany.my.rubrik.com/api/client_token -o /dev/null -w "%{http_code}"
```

---

## "Permission denied" or missing data

The service account may not have sufficient permissions for the operation.

**What to check:**
1. In RSC, go to **Settings → User Management → Service Accounts** and verify the account has the correct role assigned
2. The built-in **Read-only** role covers all query operations
3. If you're seeing empty results rather than errors, the account may have `VIEW_INVENTORY` scope limitations — ask: *"What permissions does my service account have?"*

---

## "Feature not enabled" errors

Some RSC features require specific licenses or feature flags. If a query returns a feature-not-enabled error, the feature is not licensed for your account. The plugin will note this and continue with available data from other tools.

---

## Slow responses or timeouts

The default timeout is 30 seconds. For large environments or slow network connections, increase it:

```bash
export RSC_TIMEOUT_SECONDS=60
```

---

## "Schema mismatch" errors

If you see `GraphQL schema mismatch` errors, the plugin version may be out of sync with your RSC version. [Download the latest release](../../releases) and reinstall.

---

## The plugin loads but returns no results

Before concluding your environment is clean or empty, this could be a scope limitation. Ask:

> *"What permissions does my RSC service account have?"*

`VIEW_INVENTORY` limitations silently restrict what objects are returned without producing an error.

---

## Null scan flags on snapshots

If a snapshot shows `scan status: unverified`, it means the anomaly scan has not yet completed for that snapshot — not that it is confirmed clean. Do not use an unverified snapshot as a confirmed clean recovery point.

---

## Write operations not working

1. Verify `RSC_WRITE_ENABLED=true` is set in your platform configuration
2. For destructive operations, also verify `RSC_DESTRUCTIVE_ENABLED=true`
3. Check that your service account has a role with write permissions

---

## Getting help

- **GitHub Issues:** [github.com/rubrikinc/rubrik-mcp/issues](../../issues)
- **Rubrik Support:** [support.rubrik.com](https://support.rubrik.com)
