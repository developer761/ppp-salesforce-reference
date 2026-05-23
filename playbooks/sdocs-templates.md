# Playbook — S-Docs / S-Sign Template Conventions

How PPP works with S-Docs (document generation) and S-Sign (e-signature) on Salesforce: onboarding users, the RENDER conditional syntax, and syncing branded templates between production and sandbox. Conventions only — no template bodies with customer data.

## S-Docs / S-Sign user onboarding

For a user to generate documents and send for signature, they need:
- The **S-Docs** permission set (object name prefix `SDOC`).
- The **S-Sign** permission set (object name prefix `SSign`).
- The corresponding **package licenses** assigned (separate from permission sets — both are required).

**Diagnostic rule:** if document generation fails and you suspect permissions, compare the Apex log line counts across retries. **Identical line counts across retries indicate the failure is not permission-related** (a permission block would short-circuit at a different point). Look elsewhere — template config, license assignment, or data.

## RENDER conditional syntax (show/hide template content)

S-Docs templates support conditional blocks that show or hide sections at render time:

```
<!--RENDER=(condition)-->
   …content shown only when the condition is true…
<!--ENDRENDER-->
```

- Reference the **running user's** fields with `{{!RUNNINGUSER.field}}`.
- **Licensee payment-hide pattern:** to hide a payment section for licensee-run documents, gate the block on the running user's licensee field (the licensee flag on the User record). This is how licensee-branded documents suppress PPP-only payment content.

## Branded templates — per brand/licensee

Each brand or licensee gets its own cloned + rebranded set of templates (Quote, Work Order, Contract, Invoice, plus email variants) rather than one heavily-conditional template. See `licensee-onboarding.md` for where this fits in onboarding.

## Syncing templates production ↔ sandbox

When templates need to move between orgs (e.g. cleaning up and re-syncing a brand's set):
- Use a **direct REST field-copy** approach for the template records rather than the S-Docs Migrator, which has been unreliable for this.
- Sync the full set for a brand together so branding stays consistent.
- Re-validate rendering in the target org afterward — see `sandbox-update-testing.md` (sandbox drift, email `.invalid` trap, document-sends-as-running-user).

## Gotchas

- **Two grants, not one:** permission set **and** package license are both required; a user with the permset but no license still fails.
- **Migrator unreliability:** prefer the direct REST field-copy for moving template records between orgs.
- **Render-as-running-user:** RENDER conditions evaluate against the user generating the document — test as that user, not as an admin.
