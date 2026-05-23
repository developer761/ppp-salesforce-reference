# Playbook — Testing System Updates in Sandbox Before Production

Reusable workflow for validating managed-package upgrades and config changes in PPP's Salesforce **sandbox** before applying them to **production**. The goal is a defensible go/no-go decision, not a vibe check.

## When to use

- Managed-package version upgrades (e.g. document-generation / e-signature packages).
- Config or schema changes with broad blast radius (flows, permission models, page layouts).
- Anything that could regress document generation, email, or the core lead→work-order lifecycle.

## The workflow

1. **Baseline** — capture the current healthy state in sandbox: package versions, key config, a set of representative records, and a record of what "working" looks like (e.g. a successful document render + email). This is what you compare against after the change.
2. **Apply the change in sandbox** — perform the upgrade/config change in sandbox only. Never in production first.
3. **Multi-part validation** — run independent checks, ideally in parallel, covering each area the change could touch:
   - **Apex regression** — run the relevant Apex tests; compare pass/fail and (a useful trick) line counts across retries to tell genuine permission issues from flaky ones.
   - **Config integrity** — confirm flows are Active (not Draft — flow deploys can silently land in Draft), permission sets/groups intact, layouts unchanged.
   - **Functional smoke tests** — exercise the real processes end to end: document generation, e-signature, and the lead → conversion → appointment → quote → quote-acceptance → work-order lifecycle.
   - **Email delivery** — verify branded emails send and render for a representative user.
4. **Go / no-go** — only recommend the production change when every validation area is healthy. Document what was tested and what was deferred.
5. **Production cutover** — apply the validated change in production; for matched package pairs, cut over together.

## Conventions & gotchas

- **Sandbox email trap:** sandbox user emails are often masked (e.g. an `.invalid` suffix), so real sends won't deliver. Keep a dedicated clone test user with a deliverable address and "Log in as" to test outbound email/document delivery.
- **Document generation sends as the running user** — test as the user who will actually trigger it, not just as an admin.
- **Sandbox drifts from production** — FLS and data differ between orgs, producing "phantom" gaps that don't exist in prod (and vice versa). Validate in the org you're shipping to, and re-validate after a prod cutover.
- **Flow-deploy-to-Draft quirk** — after deploying a flow, verify the active version; it can land in Draft and silently stop firing.
- **Subagent fan-out** — the validation areas are independent, so running them as parallel agents (one per area, each returning a health verdict) is efficient and keeps the evidence separated by concern.

The detailed test playbook and per-run questionnaire live in the private project; this is the reusable shape.
