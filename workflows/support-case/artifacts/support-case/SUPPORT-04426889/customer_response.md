# Operator Response: Case 04426889

## Summary

The "Attach Interface" action in Horizon fails after upgrading from RHOSP 16.2
to RHOSP 17.1 because the Nova compute service changed how it organizes its
authorization rules. Horizon was not fully updated to match these changes,
causing a mismatch between what the dashboard allows and what the compute
service accepts.

## What We Found

During the upgrade from RHOSP 16.2 (Train) to 17.1 (Wallaby), Nova reorganized
its policy rules for interface operations. Previously, there was one rule
controlling all interface actions. In the newer version, this was split into
separate rules for listing, viewing, creating, and deleting interfaces.

Horizon's "Attach Interface" button still checks against the old combined rule,
which now maps to "list interfaces" (read-only access). However, when you
actually click the button, the compute service checks the new "create interface"
rule (write access). This mismatch means the button appears available, but the
operation is rejected by the compute service.

A secondary finding: when an administrator operates from the admin project and
tries to attach an interface to a VM in another project, the network dropdown
may show no networks. This is because the dropdown only loads networks visible
to the admin project, not the target VM's project.

## Recommended Action

Check your Nova configuration first:

```bash
grep -r "enforce_new_defaults\|enforce_scope" /etc/nova/nova.conf
```

**If both values are `false` (or absent):** The old policy behavior is preserved
through backward-compatible aliases. The issue should not occur with default
settings. If it is occurring, check for custom policy overrides in
`/etc/nova/policy.yaml` or `/etc/nova/policy.d/`.

**If `enforce_new_defaults` is `true`:** You have two options:

1. **Add a policy override** (quick fix):

   Add this line to `/etc/nova/policy.yaml`:

   ```yaml
   "os_compute_api:os-attach-interfaces": "rule:project_member_or_admin"
   ```

   Then restart the Nova API service.

2. **Use the CLI** as an alternative to the Horizon button:

   ```bash
   openstack server add port <server-id> <port-id>
   ```

## What To Verify

After applying the fix:

1. Log into Horizon as a project member
2. Navigate to Project > Compute > Instances
3. Select an instance and click "Attach Interface"
4. Verify the network dropdown shows available networks
5. Complete the attach operation and confirm it succeeds

## Additional Notes

- The CLI (`openstack server add port`) is always available as a fallback
  and is not affected by this issue.
- This issue affects only the Horizon dashboard; API and CLI access to
  the attach-interface operation works correctly.
- Always test policy changes in a non-production environment first.
- If your deployment requires `enforce_new_defaults=true` for compliance,
  the policy override (Option 1) is the recommended approach until a
  Horizon code fix is available upstream.
