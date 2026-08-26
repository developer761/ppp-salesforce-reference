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

## Shipping a flow change to production as an inactive Draft

For a flow change that a second person should review against real production config before it takes
effect, deploy it **as a Draft** rather than activating on deploy.

- **Set `<status>Draft</status>` before deploying to prod.** Metadata retrieved from an org carries
  `<status>Active</status>`; deploying that file as-is *may* make the change **live on arrival**.
  Flipping it explicitly creates a new version alongside the running one that changes no behaviour
  until somebody activates it in Setup. ⚠️ The converse does **not** hold — an `Active` status in the
  XML does not guarantee activation, and in an org without the activation setting it lands as Draft
  regardless. See the next section. Set the status you want either way and **verify the result**;
  never infer what happened from what the file said.
- **This makes rollback free.** Reverting is re-activating the prior version from the flow's version
  list — instant, no deploy, no metadata round-trip. Keep the pre-change XML as a backup anyway, but
  it is the second line of defence, not the first.
- **Nothing happens until activation.** Any data backfill whose values are produced *by* the flow
  must run **after** activation. Running it against the old active version silently does nothing and
  the work has to be repeated.
- **Flow version numbers are per-org and do not correspond.** Sandbox and production routinely hold
  byte-identical definitions at different version numbers, because each org increments on its own
  edit history. **Diff the XML to establish parity; never infer it from the version number.**
- **Keep backup copies out of the package directory.** Every file under `force-app/` is a component
  to the deploy. A sibling backup such as `X.flow-meta.xml.orig` is picked up as a *second* Flow
  component and the deploy fails with a source conflict that names the backup, not the real file.

Validate the same way as any other component: `sf project deploy start --dry-run` first, then deploy,
then read the version list back and confirm the intended version is Draft and the prior one is still
Active.

## A production deploy can land as Draft even when the XML says Active

**`Status: Succeeded` on a flow deploy does not mean the flow is running.** Production will not
activate a deployed flow unless the org has the *deploy processes and flows as active* preference
enabled **and** the flow meets the test-coverage requirement. Where either is missing, the deploy
reports success, creates the new version, and leaves it **Draft** with the previous version still
Active. Nothing in the deploy output says so.

This is the quiet failure mode of the whole procedure: the change is deployed, the CLI says it
worked, and the old logic is still the one running. Every downstream step then reads as correct
while operating on stale behaviour.

- **Always read the version list back after deploying** — not the deploy result. Query
  `Flow` via the Tooling API filtered on `Definition.DeveloperName`, ordered by `VersionNumber`
  descending, and confirm which version actually holds `Status = 'Active'`.
- **Activate explicitly with a `FlowDefinition`.** Deploy a second component containing only
  `<activeVersionNumber>N</activeVersionNumber>` for the version you want live. This is a separate
  deploy from the flow itself and is the supported way to activate without opening Setup.
- **Then verify a third time by re-retrieving the flow from the target org** and diffing it against
  the pre-change backup. Confirm the intended change is present *and* that it is the only
  difference — a retrieve returns the active version, so this proves what is actually running rather
  than what was sent.
- **Sequence matters when a create-triggered flow supplies a field value.** If records are inserted
  between the flow deploy and its activation, the *old* version stamps them. Activate and verify
  before any batch that depends on the new behaviour, or the batch has to be corrected afterwards.

The three-step shape — deploy, activate, re-retrieve and diff — costs about a minute and is the only
way to distinguish "deployed" from "running".

## Back up an Apex class before you deploy over it

**Salesforce does not version Apex class bodies.** Unlike a Flow, which keeps every version and lets
you re-activate a prior one from Setup, an `ApexClass` has a single body that a deploy overwrites in
place. There is no prior version to retrieve, no org-side history, and nothing in the deployment
record that reproduces what was there before. Once both sandbox and production hold the new version,
the original is gone unless it was captured somewhere first.

- **Capture the current body before deploying**, even for a change you are confident in, and even
  when the class is small. `sf project retrieve start --metadata ApexClass:TheClass` into a location
  *outside* the package directory, or commit the package directory to git before the first edit. A
  source-tracked package directory that was never committed provides no rollback.
- **Do not assume the sandbox copy is a backup.** A sandbox that received the change first holds the
  *new* version too. Check `LengthWithoutComments` in both orgs before relying on either.

### Reconstructing a class body that was not captured

If the original is already gone, it can be reconstructed when the change was strictly additive —
but only verifiably so. `ApexClass.LengthWithoutComments` (Tooling API) is the handle:

1. **Positive control first.** Write a comment-stripper and run it against the *current* class. It
   must reproduce that class's `LengthWithoutComments` exactly before you trust it on anything else.
   The rule is: strip `//` and `/* */` comments (respecting string literals), then drop blank lines.
2. Remove the additions from a copy of the current source and measure. Hitting the original's
   recorded `LengthWithoutComments` exactly is strong evidence the code is byte-identical.
3. **Know the boundary.** An exact length match proves the non-comment character *count* matches; it
   does not prove comment text was identical, and it is not a compile check. Record both limits
   alongside the artifact so a later reader does not over-trust it.

### A restored original is not automatically the safe rollback

Check what the new version added before reaching for the old source. If the change widened a
condition so that records missed on one run are picked up on a later one, restoring the original
narrows it again — and anything the new logic deliberately deferred is then stranded permanently,
because the original never had the catch-up path that would release it.

Where a change is gated behind a feature flag, **switching the flag off is usually the better
rollback than restoring the source**: it exercises a code path that was written and tested with the
deferred records in mind. Design the flag so the catch-up path keys off *scope*, not off the enabled
flag — otherwise turning the gate off closes the very window that releases what it held, and the off
switch becomes the failure it was meant to undo.

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
