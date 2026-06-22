# PPP Salesforce — Shared Knowledge Base

This repo is the **shared memory** for Precision Painting Plus Salesforce work, used by everyone building on top of PPP's Salesforce org (internal admin + the Command Center engagement). Any Claude Code / AI session that has this repo in its working tree auto-loads this file — so it's the single source of truth for PPP's schema, conventions, and process playbooks.

**If you are an AI assistant:** read the full repo — this index and all docs. Work across PPP's tech stack regularly crosses areas; loading everything upfront ensures nothing is missed as a session evolves. Do not scope to a single doc or system based on how the task is framed. Treat repo docs as authoritative for everything. For live, time-sensitive data, verify against the source directly — this is a reference snapshot, not live data.

---

## 🔒 This repo is PUBLIC — curation rules (read before adding anything)

This repository is publicly visible on the internet. Everything committed here can be read, indexed, and cached by anyone. **Only sanitized reference material belongs here.**

**NEVER commit any of the following:**
- **Compensation data** — salaries, draws, commission amounts, individual quota dollar figures, GM targets per named person.
- **Personally identifying info** — employee/customer names tied to performance, internal email addresses, phone numbers, Salesforce User IDs, record IDs.
- **Customer / account data** — customer names, addresses, deal values, contact info, anything from real records.
- **Secrets** — API keys, tokens, OAuth client secrets, connection strings, `.env` contents.
- **Unrelated work** — anything not part of PPP Salesforce (e.g. personal projects).

**DO commit:** schema (field/object API names, picklists, relationships), business rules and conventions, KPI *definitions and logic*, process playbooks, and reference code that contains no real data or secrets.

**When in doubt, leave it out** — or describe the *logic* without the *values* (e.g. "draw is stored on a per-rep User field" ✓, not the actual dollar amounts ✗). The detailed/sensitive versions of this knowledge stay in the private Claude Projects on the admin's machine; this repo is the curated, shareable layer.

---

## Index

### `salesforce/` — schema & metric definitions
- **`BUSINESS_RULES.md`** — start here. Conventions and field gotchas: fiscal year, the canonical sales metric, quota = points, the GM / field-naming / `IsClosed` traps, lead-source classification, sales tax.
- **`DATA_DICTIONARY.md`** — full schema reference (custom fields, objects, flows, triggers, validation rules, record types). Snapshot from production 2026-05-11.
- **`REP_PERFORMANCE_KPIS.md`** — exact definitions of the rep-scorecard KPIs (sanitized: logic only, no comp data).
- **`architecture_*.md`** — Mermaid maps of how objects connect (sales pipeline, service delivery, fleet & quota, compliance, marketing/geo).
- **`reference-code/`** — example SOQL pulls + aggregation (Python). No real data.

### `command-center/` — the PPP Command Center app
- **`REP_PROFILES_INTEGRATION_GUIDE.md`** — how to wire PPP's canonical KPIs into the Command Center's Rep Profiles page: data-flow, KPI map, correctness pitfalls, edge cases, validation checklist.
- **`KPI_ALIGNMENT_REVIEW_2026-05-27.md`** — point-in-time audit of the Rep Profiles code (@ `e66ec60`) vs the current FPRC definitions, with ready-to-apply diffs (PFQ anchor, self-gen bucket, commissions, complaints, change orders).

### `playbooks/` — repeatable PPP Salesforce processes (conventions, sanitized)
- **`licensee-onboarding.md`** — onboarding a new PPP licensee (permissions, branded document templates, app + email-flow branching).
- **`sandbox-update-testing.md`** — testing managed-package upgrades / config changes in sandbox before production.
- **`sdocs-templates.md`** — S-Docs / S-Sign document-template conventions and prod↔sandbox sync.
- **`software-audit.md`** — monthly software license audit: platform cross-reference, Checkover field triage, cost consistency check, allocation monthly audit (reference).
- **`bmcr-recon.md`** — Benjamin Moore Contractor Rewards monthly reconciliation: SF object/fields, picklist gotchas, auto-update rules, match paths, revert procedure, edge cases.
- **`wo-cleanup.md`** — bi-weekly WO cleanup: estimate appointment violations, small balance adjustments, Opp/WO status alignment. Covers governor limit batching, `Internal_Adjustments__c` formula direction, 3-step quote sequence for Opp stage changes, ST zip validation workaround.

### `estimating/` — estimating logic for PPP tools
- **`paint-gallons-calculator.md`** — standard "gallons needed" logic for the paint-order calculator: ceiling/walls/trim formulas, door/window/closet allowances, coverage rate, 10% buffer, job-level roll-up by color/finish, and 5-gal-bucket packaging.

---

## Core PPP conventions (quick reference)

- **Org of record:** Salesforce is the source of truth. The Command Center reads it live (cached) and is not a mirror.
- **Fiscal year:** starts **Feb 1**, ends Jan 31; FY name = start year (FY26 = 2026-02-01 → 2027-01-31). Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4 Nov-Jan.
- **Primary sales metric:** `Opportunity.QuotedSubtotalWithChangeOrder__c` (WorkOrder uses `Quoted_Subtotal_with_Change_Order__c` — different API name, same concept).
- **Quota:** points, 1:1 with dollars; rep-attributable rows filter `QuotaType__c = 'Field_Member'`.
- **Field reps:** active Users on Profile `*Standard.Field`.
- See `salesforce/BUSINESS_RULES.md` for the full list and the traps.

---

## How this is used as shared memory

- **In the Command Center repo:** clone this alongside it (or reference it from the Command Center's `CLAUDE.md`) so an AI session working on the app reads these definitions automatically.
- **For PPP admin work:** clone this to a fixed local path and point to it from your user-level `~/.claude/CLAUDE.md` so your sessions read it too.
- **Keeping it current:** when a convention changes or a new process is documented, update the relevant doc here (sanitized per the rules above) and commit. This file is the index — add a one-line pointer when you add a doc.
- **Before pushing changes:** always `git fetch` first, review what's changed on remote (`git diff HEAD origin/main`), incorporate any remote updates into your edits, then `git pull --rebase` and push. Never push without checking for remote changes — this repo has multiple contributors and a blind push can silently overwrite their work.
