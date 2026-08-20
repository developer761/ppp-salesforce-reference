# Playbook — Monthly Software Audit

Monthly process that cross-references active `Software__c` records in Salesforce against live license counts from each platform, flags gaps, checks allocation accuracy, and produces a single Airtable support ticket with findings.

**Cadence:** First week of each month
**Output:** One Airtable support ticket per run

---

## Systems Covered

| System | Source |
|---|---|
| Salesforce Full | `User WHERE Profile.UserLicense.Name = 'Salesforce'` |
| Salesforce Portal | `User WHERE UserType = 'PowerPartner'` |
| SDocs | `UserPackageLicense WHERE PackageLicenseId = <package_id>` |
| S-Sign | `PermissionSetAssignment WHERE PermissionSet.Name = 'SSign_Experience_Cloud_User'` — count + email cross-ref via `Assignee.Email` |
| Dialpad | REST API — `/users` endpoint |
| Google PPP | GAM CLI — `gam print users` |
| Google O3 | GAM CLI — separate config directory for O3 workspace |
| Slack PPP | Slack API — `users.list` |
| Slack O3 | Slack API — `users.list` (separate workspace) |

---

## Step 1 — Run the audit script

The script (`software_audit.py`) handles all data collection automatically:

1. Queries each platform for active license count and user list
2. Compares counts against contract limits
3. Cross-references platform user emails against `Software__c` active records — flags anyone in a platform with no SW record, or in SW with no platform presence
4. Enriches gaps into three buckets: email mismatch (the *same account* under a new address — update the record), known staff (a *different account* on a known staff record, or a type not yet recorded — create a record), unknown (no SF footprint — investigate before creating anything). See **Account identity** below for how the two are told apart, and why "the staff record already has one" is not sufficient evidence.
5. Runs `Allocation__c` checkover query and flags people where `Checkover__c = 'Check'`
6. If any platform fails, prints all errors and prompts before writing to Airtable — abort (`n`) to fix and re-run; proceeding (`y`) shows `⚠️ ERROR` for failed systems
7. Updates the recurring audit ticket's `**AUDIT ACTION ITEMS**` section — PRE-AUDIT and POST-AUDIT sections above the marker are preserved

Review output before proceeding. Resolve or note any gaps.

---

## Step 2 — Checkover field audit

The audit script automatically surfaces both `Software__c` and `Allocation__c` checkover flags in the ticket (action items 3 and 5 respectively). No manual queries needed unless you want to investigate a specific flag in more detail.

### Software__c — Checkover formula logic

The formula returns `"Check"` when any of the following are true (evaluated in order):

| Condition | Meaning |
|---|---|
| Staff has `Termination_Date__c` AND Status = Active | Staff is gone, license still open |
| Staff `Employee_Status__c = Terminated` AND Status = Active | Same, via status field |
| Status = Transferred/Expired/Deactivated but `End_Date__c` is in the future | Mismatch between status and date |
| `End_Date__c` ≤ today AND Status = Active | Date passed, status not updated |
| `Start_Date__c` is blank | Required field missing |
| `End_Date__c` is blank AND Type is not Slack/PPP or Google/O3 | Required field missing (those two types are open-ended by design) |
| `Cost__c` is blank | Required field missing |

### Allocation__c — Checkover formula logic

The formula returns `"Check"` when any of the following are true:

| Condition | Meaning |
|---|---|
| Any monthly field (Jan–Dec), Start Date, End Date, Status, or Bill To Corp is blank | Required field missing |
| Status = Active AND `Employee_Status__c = Terminated` | Staff gone, allocation still open |
| Status = Active AND `End_Date__c` < today | Allocation past its end date |
| Current month's field ≠ `Allocated_Cost__c` | Monthly amount out of sync with expected cost |

### How to handle each issue type

| Root cause | Action |
|---|---|
| Terminated employee — active SW record | **Flag only.** No action until leadership confirms offboarding. |
| Terminated employee — active allocation | **Flag only.** Same hold. |
| Missing End Date on non-employee SW record | Add an end date (contract renewal or fiscal year end) |
| Active SW with past End Date | Update status to Expired or investigate |
| Blank Start Date or Cost | Fill in or investigate |
| Monthly amount ≠ Allocated_Cost | Check for mid-month timing (see allocation section); update if genuinely wrong |
| Blank Bill To Corp on Non-Employee allocation | Expected — no corp to bill for pooled licenses |

---

## Step 2b — Active-staff coverage gaps

The allocation checkover and the allocation-vs-software comparison are both *comparisons*, so they are **blind when allocation and software agree at $0**. An active staff member with no software has allocation = $0 and software cost = $0 — not a mismatch — so a lapsed or un-provisioned active person can sit undetected: software shut off at fiscal-year close, but the profile never terminated or re-provisioned.

The script asserts the **invariant** instead — *an active, non-terminated staff member must cost more than $0 and have an allocation* — via a two-way check:

- **Direction A ($0 blind spot):** active staff whose active `Software__c` cost sums to $0. Catches removed software, missed terminations, and un-provisioned hires.
- **Direction B (missing allocation):** active staff holding *paid* software but with **no** active `Allocation__c` record at all. A comparison that iterates allocations can't see a missing one; starting from the staff list catches it. (This is also why an allocation-anchored manual scan misses these people — enumerate *staff*, not allocations.)

### Legitimate $0 exceptions

Some active staff genuinely cost $0 and should not flag. Maintain two whitelists in the script:

- **Free-software-only** — staff whose only active software is a free-tier product (e.g. the free Slack plan). Keyed by `(Type, License_Type)`.
- **Named no-software staff** — active contractors who legitimately hold no company software. Keyed by `SFDC_Staff__c` Id (names can carry stray whitespace).

Anything reading $0 that is not on a whitelist surfaces for review. To accept a new one, add it to the appropriate list with a one-line reason.

---

## Step 3 — Cost consistency check

Pull all active `Software__c` records and verify that every combination of `Type__c` + `License_Type__c` has a single consistent `Cost__c` value.

```sql
SELECT Type__c, License_Type__c, Cost__c
FROM Software__c
WHERE Status__c = 'Active'
ORDER BY Type__c, License_Type__c, Cost__c
```

Flag any type/license pair with more than one distinct cost. Investigate whether it reflects a legitimate pricing tier or a data entry error.

**Known exception:** some license types carry two cost tiers due to a legacy pricing change. Confirm with whoever manages contracts before treating as an error.

---

## Step 4 — Append findings and close

Add any manual findings from Steps 2–3 to the ticket Internal Notes created in Step 1. One ticket per run — do not create duplicates.

---

## Removal date lookup

For every "Active in SF, not found in external platform" gap (action item 2), the script attempts to surface a suggested `End_Date__c` to fill on the SW record. It uses a three-tier hierarchy:

1. **Reliable platform date** — use directly:
   - Google: exact date from GAM admin audit log (`suspend_user` / `delete_user` events)
   - Slack: `updated` timestamp on deleted member, validated within ±7 days of `SFDC_Staff__c.Termination_Date__c`

2. **Airtable offboarding ticket** — if no reliable platform date, the script queries Support Tix for Issue Type = On/Offboarding within ±15 days of the staff member's termination date, then parses Internal Notes for a dated line matching the platform. If a date is found, it is surfaced inline; if a ticket is found but has no date for this platform, a hyperlink to the ticket is shown for manual review.

3. **Flag** — if nothing resolves: "No removal date found — flag for review."

The script never writes these dates to Salesforce — they are suggestions only, displayed in the action items block for human follow-through.

---

## Email normalization note

Salesforce users may be set up with `.com` or `.net` email variants; SW records may use either. During cross-reference, normalize both sides to `.com` before comparing to avoid false-positive mismatches. Do not modify any records based on the normalization — it is in-memory only.

---

## Known platform gaps (do not flag as errors)

| Platform | Gap | Notes |
|---|---|---|
| S-Sign | Unlimited license — live count will exceed SW records | By design |
| Salesforce system accounts | Integration/analytics users appear in the SF user list | Maintain an exclusion list of known system account emails in the script |
| Dialpad office/dept lines | Appear in the number pool but are not billed as user licenses | Document in SW record notes; offset the expected count |
| Google O3 | ✓ Automated — separate GAM config for O3 workspace | — |

---

## Reference: Allocation Monthly Audit

Run as needed — not part of the standard monthly cadence. Use when there is reason to believe allocation monthly amounts have drifted from actual SW costs (e.g., after bulk onboarding, a pricing change, or a termination wave).

### Approach

For each active `Allocation__c` record:

1. Pull all `Software__c` records for that staff member (all statuses, no date filter)
2. For each FY month (Feb–Jan): sum `Cost__c` for SW records where `Start_Date__c` ≤ last day of month AND (`End_Date__c` ≥ first day of month OR `End_Date__c` is null)
3. Compare to the recorded monthly field; flag differences above a small tolerance (e.g. ≥ $0.02)

### Interpretation

| Month type | Interpretation |
|---|---|
| Past months (already occurred) | Differences are real — investigate and correct |
| Future months | Often intentional — allocation assumes license renewal while SW `End_Date__c` reflects current contract period only. Confirm intent before changing. |

### Mid-month timing policy

PPP applies mid-month license changes in one of two ways:
- **Prorate** the cost in the month the change occurred
- **Apply from the next full month**

Both are valid. Do not flag a past-month difference as an error without first checking whether the change happened mid-month.

### Systematic future-month patterns to expect

When SW licenses have End Dates that fall mid-year (e.g., SDocs/SSign expiring in August, Google expiring in December), the expected SW cost will drop below the recorded allocation in later months. This is normal — the allocation assumes renewal. Only investigate if the license is genuinely not being renewed.

---

## Two-pass reconciliation

Keeping `Software__c` records in sync with the platforms is a two-directional check:

1. **SF → platform** — for each *Active* SW record, confirm the person actually holds that license live on the platform. Active-in-SF-but-absent-from-the-platform = stale → set `End_Date__c` + `Status__c`, or confirm it's an accepted exception. Verify against the real platform roster, not only the cross-referenced email match — matches can throw false negatives when a user's platform login domain differs from the email on the SW record.
2. **platform → SF** — every live platform seat needs an Active SW record; a seat with no record = create one.

The audit's cross-reference produces both directions ("active in SF, not found in platform" and "active in platform, not in SF").

**Accepted noise:** an unlimited-license product (e.g. S-Sign) will show SW records "active in SF, not on platform". These are usually false negatives, not stale records — don't chase them, but understand *why* before dismissing them.

### Checking a managed package's real roster

A user can hold a managed-package license through **four independent paths**. Querying one and concluding "not on platform" produces false negatives every run:

1. **Permission sets** — a package typically ships *several* (e.g. an Experience Cloud user set, a general user set, an administrator set, a site internal-user set). Query them **all**, not the first one you find:
   ```sql
   SELECT Name, Label FROM PermissionSet WHERE Name LIKE '%<pkg>%'
   ```
2. **Permission set groups** — `PermissionSetAssignment` returns the *group's* aggregate entry, not the sets inside it. Expand via `PermissionSetGroupComponent`.
3. **Profile-based access** — a System Administrator profile can grant the package's objects directly with **no permission set at all**. This path is invisible to every permission-set query.
4. **`UserPackageLicense`** — only meaningful when the package is seat-limited. On an unlimited license (`PackageLicense.AllowedLicenses = -1`) Salesforce doesn't enforce per-user rows, so this table **drifts and fills with inactive users**. Do not treat it as the roster on an unlimited product.

**The decisive check is usage, not configuration.** Config tells you who *could* use the product; the package's own records tell you who *does*. Query the package's primary object grouped by `CreatedBy` (for an e-signature product, the envelope object) over a trailing window. A user with real activity holds a real license regardless of which access path grants it.

> Worked example: an S-Sign cross-ref keyed on a single permission set flagged ~10 senior staff as "not on platform" every month. Widening to all four permission sets cleared most; the remainder were System Administrators with direct object access, confirmed as genuine users by their envelope-creation history. Zero were stale.

---

## Account identity — a renamed address vs. a second person

When the cross-reference finds a live platform account with no `Software__c` record, the audit
has to decide between two possibilities that look identical if you only compare email strings:

- the **same account** under a new address (the person's email changed) -> update the record
- a **different account** on a staff record that already has one -> create a new record

Getting this wrong is expensive in one direction: reporting "update the existing record" when the
account actually belongs to someone else tells the operator to overwrite a live colleague's record,
which drops a real seat from tracking and misdates the allocation. It is also unstable — once
actioned, the same record flips back the following month.

**Why "the staff record already has one" is not enough.** A staff record does not always represent
one human. Licensee, affiliate and pooled records (a shared non-employee bucket, a partner entity)
legitimately carry several people's seats under a single staff record. Any classifier that keeps
one email per (staff, type, license), or that treats "the stored address differs from the platform
address" as proof of a rename, will misread every additional seat on those records as a rename.

**Use three signals, conjunctively.** Report a rename only when all applicable signals agree;
otherwise report that a new record is needed.

| Signal | Rule | Rationale |
|---|---|---|
| **Liveness** | the stored address must no longer be a live account on that platform | an address still in use belongs to someone still using it |
| **Name** | platform account name must match the staff record name above a threshold | shared entities score far below real people; the gap is wide |
| **Created** | the account must not have been created materially after the record's `Start_Date__c` | a brand-new account cannot be a rename of an older record |

### Signal availability differs by platform — check before relying on one

Do not assume a signal exists everywhere. Verify per platform:

| Platform family | Name signal | Creation date |
|---|---|---|
| Salesforce (and any product whose seats are SF Users) | yes — `User.Name` is admin-managed | `User.CreatedDate` |
| Google Workspace | yes — directory-managed | GAM `creationTime` |
| Dialpad | yes | `date_added` |
| Slack | **no** — see below | **no** — see below |

**Slack is the exception on both counts.**

- `users.list` exposes no account-creation field. The value lives on the SCIM API, which requires
  an admin *user* token (not a bot token) **and** a Business+/Enterprise Grid plan. A read-scoped
  bot token on a free workspace gets `401`. Confirm token type and plan before concluding the data
  is missing.
- Slack display names are **user-edited**, so they do not separate people from entities the way
  admin-managed names do. Real people commonly appear as a first name only, an accented spelling,
  or a first-name-plus-initial, scoring in the same range as pooled entity records. Never gate a
  Slack decision on a name match.

Liveness alone is sufficient for Slack, and it handles an email-domain migration correctly: changing
the address on an existing Slack account preserves the member id and removes the old address from the
roster, so the old address goes stale and the rename is detected. Where certainty is required,
store the platform's stable member id on the SW record instead of inferring from the address.

### `Start_Date__c` is a tracking date, not an account birthday

Bulk onboarding leaves large clusters of records sharing one `Start_Date__c` — the date tracking
began, unrelated to when any account was created. The creation-date signal must **abstain** on those
dates rather than guess. Identify them by grouping active records by `Type__c` and `Start_Date__c`
and looking for a single date holding a large share of one type.

Do **not** paper over this with a fuzzy tolerance window. A window wide enough to absorb one
platform's backfill will still miss another's (observed: over a year of skew), while being
unnecessary on a platform whose dates are clean. Abstaining on the known bulk dates is exact and
leaves only genuine provisioning lag (a few days) to absorb.

### On adding a "shared entity" flag to the staff object

Tagging pooled/licensee staff records with a picklist value is a reasonable instinct and is fine to
maintain for billing or reporting. It is **not** sufficient as the audit's differentiator: it only
works where it has already been backfilled, it depends on discipline for every new partner, and it
still does not answer whether the existing record is stale. The name signal covers the same case
with no data dependency. Prefer signals derived from the systems themselves over flags that require
upkeep.

### Regression controls

Keep the classifier directly unit-testable and assert both directions — a "no mismatches found"
result is only meaningful if the rename path can still fire:

- **rename must fire:** a stale address on a single-person staff record; an email-domain migration
- **rename must not fire:** an additional seat on a shared record; churn on a shared record, where
  the old seat *is* stale and a different person joins (liveness alone misfires here; the name
  signal is what catches it)
- **abstention:** a record sitting on a bulk-backfill date must not be treated as date evidence

---

## Creating Software__c records — RecordType is required

`Type__c` and `License_Type__c` are **restricted picklists gated by the record's RecordType**. Inserting a record without the matching `RecordTypeId` fails with `INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST` — through the CLI *and* Apex. **Updates** to existing records don't need it (they inherit the RecordType). Set the RecordType that matches the platform Type (Slack, E-Document, Salesforce, Google, Dialpad, or Other) on every insert.

**Non-billed external users** (external parties using PPP software without being invoiced): record their seats against the shared **Non-Employee** staff record at standard cost, so the consumption is tracked as an overage against that bucket rather than lost.
