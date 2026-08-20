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

## Porting a single component into sandbox

Backfilling one component (a validation rule, a flow, a field) so the orgs match is a smaller job than
a package upgrade, but it has its own failure modes.

- **Generate the metadata from the source org — never retype it.** Pull the live definition
  (`sf data query --use-tooling-api ... SELECT Metadata FROM ValidationRule ...`) and write the
  `-meta.xml` from that value programmatically, XML-escaping as you go. Formulas contain `>`, quotes
  and significant whitespace; hand-transcription silently changes behaviour and the deploy still
  succeeds.
- **Dry-run first** (`sf project deploy start --dry-run`). For a formula component this is a free
  compile check in the target org, which is the main thing that can fail.
- **Verify by reading it back and diffing against the source — but normalise whitespace.** Deploys
  normalise line endings, so a raw string comparison reports "different" on an identical rule. Diff
  the lines, then compare with whitespace stripped, and only investigate if *that* differs.

### Metadata parity is not behavioural parity

The trap worth naming separately: **a component whose logic reads org *data* can deploy cleanly,
compile cleanly, be Active — and still be permanently inert in the target org.**

The case that surfaced this: a validation rule scoping records by the owner's **management chain**
(`Owner:User.Manager…`) and matching on a manager's name. Every *metadata* dependency existed in
sandbox — the custom permission, the roll-up field, the custom name field on User — and the two-level
relationship traversal compiled. But sandbox held **no user with that manager's name at all**, and
only a small fraction of sandbox users had any `ManagerId` populated. The owner clause could never
evaluate TRUE, so the rule enforced nothing there and its silence was indistinguishable from a rule
that was working.

**How to apply:** before treating a sandbox port as testable, check the **data the formula reads**,
not just the fields it references. For anything keyed on ownership, role hierarchy, management chain,
record type population, or a named user, run the underlying query in the target org and confirm a
non-empty result. If it comes back empty, the port is metadata parity only — record that explicitly
so nobody later reads the rule's silence in sandbox as evidence it is broken, or as evidence it is
safe. Sandboxes are refreshed on their own cadence and user records are among the first things to
diverge.

The detailed test playbook and per-run questionnaire live in the private project; this is the reusable shape.
