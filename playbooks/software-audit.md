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
| Active SW with past End Date | **Read End Date with Status, never alone** — see "Expired vs removed" below. Usually a lapsed contract, not a departure. |
| Blank Start Date or Cost | Fill in or investigate |
| Monthly amount ≠ Allocated_Cost | Check for mid-month timing (see allocation section); update if genuinely wrong |
| Blank Bill To Corp on Non-Employee allocation | Expected — no corp to bill for pooled licenses |

---

## Link every record the audit names

Any record named in an audit deliverable should be a deep link to that record. An unlinked
record name is a copy-paste-into-search round trip, paid once per row, by the reviewer, every
time the deliverable is produced. Scope it to the sections a human actually works through —
links on bulk data tabs are noise.

Plumbing this means carrying the record id through to the output: select `Id` in every query
that feeds a findings section, and have the comparison step return an identifier→id map
alongside its results. Build links through one helper that **falls back to plain text when the
id is missing**, so a failed lookup degrades gracefully instead of emitting a dead link.

**Verify the links; do not trust them.** After generating, query the ids back and assert each
link's text matches the record it targets. A mis-targeted link is worse than no link — the
reviewer acts on the wrong record and nothing looks broken. The two failure modes to watch for
both occur in *hand-written* prose rather than generated output:

- an **id invented from memory** — the link 404s, which at least announces itself
- a **record name invented** next to a correct id — the link resolves but names a different
  record; this one is silent and far more dangerous

Never hand-type a record id or name into a deliverable. Query it, then paste it.

⚠️ **Watch the loop variable.** If findings are grouped by system or category in an outer loop,
do not rebind that variable when wrapping it in a link inside an inner loop — it corrupts every
later iteration. Append the linked string to a list instead.

---

## Different addresses on different platforms are normal — not typos

One person can legitimately hold different addresses on different systems. **Only flag an address
when it does not match the one that service actually uses.** An address that merely differs from the
person's other records is not evidence of anything.

The case that makes this concrete: a directory provider once enforced a **minimum last-name length**,
so accounts with short surnames were created under a padded spelling. The person then has both forms
live — the padded one as the account primary, the short one as an alias — and each downstream system
holds whichever was used when its account was made. Nothing is misspelled.

**Resolve the address on the platform before judging it.** Directory tooling that resolves an alias
to its primary (`gam info user <address>` for Google Workspace) settles it in one call. Records whose
seats are provisioned as CRM users take the CRM user's address; records on the directory platform
take the directory primary.

In the worked case only **one** of six records was actually wrong — an e-signature record carrying the
directory-primary form for a service whose seats are CRM users, while its sibling document-generation
record on the same staff already used the correct form.

⚠️ **Do not fix this by teaching the matcher to treat the two forms as equivalent.** A global alias
rule suppresses the genuine per-service mismatch along with the false one. The per-service
cross-reference is already the right instrument: a gap reported for one service and not another is
the signal, not noise.

---

## ⚠️ Period fields named by month carry no year — the record's span supplies it

Where an allocation object stores twelve month columns (`January` … `December`) rather than dated
rows, **the year is not in the field name.** It comes from the record's own start/end span. The same
`February` column means February 2025 on one record and February 2026 on another.

**Three rules follow:**

- Match every period to the record whose span covers it before reading *or* writing. Writing a current
  figure into a prior-year record's column silently rewrites history and reports success.
- Never sum a month column across a person's records without filtering by span — that adds years
  together.
- A record whose span has ended still holds values in columns outside it. Those are stale leftovers
  belonging to no period. **Leave them alone.**

⚠️ **A completeness check will flag those leftovers as "cells the rebuild missed."** They are not
missed — they belong to a different year, and "fixing" them destroys prior-year data. Before treating
a skipped cell as a gap, check which period its record actually covers.

**Corollary:** when a person's allocation span ends but their licences keep running, the months after
the end date hold cost with nothing to carry it. Either extend the span or end the licences — and note
that clearing the end date is the right move when the spend genuinely continues, since it puts those
months back in period.

---

## A period field holds that period's ACTUAL cost — so partial periods "mismatch" by design

Where a period field is defined as *the actual cost incurred in that period*, a partial period
legitimately holds a smaller figure than a full one. Meanwhile the roll-up a checkover formula
compares it against is the **full rate** of currently-active items, and has no way to know the period
was partial.

So in any period containing a mid-period change the two **must** differ, and the check fires. **That
is a formula limitation, not a data error** — formula languages generally cannot aggregate child
records across dates, so proration is not computable where the check lives.

### Classify, don't reshape the data

The wrong instinct is to make the data satisfy the check — writing full-rate values, or inventing a
ritual to rewrite periods around the constraint. The right move is to have the **audit** decide:
recompute the period's prorated cost, and if the stored figure reproduces it, report the row as
*explained — no action* rather than as an error. Return two lists, not one, and render them
separately with the reasoning attached so a reviewer can see why a row was dismissed.

⚠️ **A period reporting `0 explained / N genuine` is a signature, not a clean bill of health.** It
means that period's values have never been written — nothing can be "explained" because the stored
figures match neither the full rate nor the prorated cost. Compare against a period you know was
rebuilt: if that one classifies almost everything as explained and the suspect one classifies nothing,
the difference is the tell.

### The one real constraint

**Never write a prorated value into the period the check is currently policing.** Write it once the
period closes — which, for a monthly process that runs on the 1st, is exactly when the run happens.
No extra cadence is required; the timing falls out of the existing schedule.

---

## Two traps when writing allocation figures programmatically

**Percent fields are not fractions outside formulas.** A platform may treat a percent field as a
fraction *inside* its own formula language while storing `100` for 100%. Reproducing that formula in
external code without dividing by 100 produces values 100× too large — and they look plausible enough
to write. Verify against a **split** record (one at 50% should come out half) before any bulk update.

**Allocation records are usually date-ranged and generational, like the licence records they mirror.**
One person holds several covering different periods; a given month's figure is only meaningful on the
record whose span covers that month.

⚠️ **Filtering to "active" allocations is the same mistake as filtering the checkover to active
licences.** Closed months live on *inactive* records, so an active-only query reads them as zero and
reports large phantom gaps — in one case a full monthly cost, twice over, for a person whose records
were entirely correct. Match each period to the record covering it, regardless of status. Correcting
history means writing to inactive records, and that is expected rather than suspicious.

---

## Reconstructing cost history from the records

Per-person monthly cost can be rebuilt from the licence records alone — sum each record whose date
range covers the month — but only under conditions worth checking before relying on it.

**It requires generational cost changes.** A new contract term must create a NEW record with its own
dates and cost, so the previous cost stays attached to the months it applied to. An in-place edit to
a cost field silently rewrites history for every past month. Check whether field history is tracked
before assuming an edit could be reconstructed — an object can have history enabled while tracking
**no fields**, which logs record creation and nothing else.

**It reads records of every status, so their end dates must be right.** This is where an
Active-only audit filter becomes dangerous: a deactivated record carrying a future end date keeps
contributing cost forever, and an audit that only inspects active records can never see it. If the
checkover logic has branches for non-active records, the query feeding it must not filter them out.

### Two conventions to fix before the numbers mean anything

**1. Contract boundaries.** When one term ends the same day the next begins, both records cover that
day — double-counting it, and the whole month under full-month proration. Fix it by **anchoring to
the invoice**: the new term starts on the invoiced date, and the *previous* record's end date is
pulled back to the day before. Adjust the derived value, not the documented one.

**2. Mid-month starts.** Decide once and apply everywhere. Day-count proration
(`cost × days covered ÷ days in month`) is the standard vendor-side formula and is the better
default when the calculation is automated. Full-month is defensible if round numbers that reconcile
to invoices matter more.

⚠️ **There is no industry standard for internal chargeback timing.** TBM specifies allocation
*methods* and is silent on mid-month proration — it is a policy choice. What matters is that one
choice is applied uniformly; the failure mode is several conventions coexisting undocumented.

⚠️ **Do not pick the convention that best matches your stored figures.** If stored values are flat
monthly amounts, full-month proration will always "agree" more — that measures conformity with the
existing inconsistency, not correctness.

### Set a trust floor

Reconstruction reaches as far back as records exist, which is usually further than the data
deserves. Where earlier figures were imported from manually-maintained spreadsheets, declare the
earliest trustworthy fiscal year, warn below it, and do not spend effort correcting data beneath
that line.

---

## Commitment shape decides whether a blank End Date is a gap

An end date is not universally required. Whether its absence is a data gap depends on how the
licence is *committed*, which is a different axis from how often it is billed:

| Shape | End date | Why |
|---|---|---|
| Monthly billed, **on contract** | required | there is a term, and it ends |
| Monthly billed, **no contract** | **not required** | month-to-month, cancel any time |
| **Annual** | required | there is a term |
| **Free** | **not required** | nothing committed |

Record this on a dedicated picklist field. Do **not** infer it from free-text notes, and do not
hardcode product names into the checkover formula — a formula that names products has to be edited
every time a new product arrives, and each edit is a chance to break the branch.

⚠️ **Cost normalisation hides billing frequency.** Where per-seat cost is stored monthly-normalised
(so annual products are divided down), annual and monthly-on-contract licences look identical in the
data. The shape cannot be derived after the fact — it has to be captured.

### Free-text exemptions are a trap worth naming

A request of the form *"exempt it when the notes say X"* fails three ways at once, and it is worth
checking all three before agreeing to build it:

1. **The field may not be referenceable.** Long text areas cannot be used in formula fields at all —
   check the field's type and length before designing around it.
2. **Substring matching is case-sensitive** in most formula languages, so `CONTAINS` on a lowercase
   literal misses the capitalised spelling.
3. **It only catches the records phrased that way.** In the case that prompted this, one of the two
   affected records used the wording and the other did not, so the rule would have fixed half the
   problem and looked like it worked.

### Deploy the formula before the backfill

When a formula gains a clause referencing a **new, empty** field, deploying it first is a provable
no-op: every new clause evaluates false, so behaviour is unchanged. Verify that — compare the
formula's output on every record before and after; the count of changed records should be zero. Then
backfill, and confirm that only the intended records flipped.

This separates a schema change from a data change, so if something moves you know which one did it.
Sequencing them the other way leaves nothing to isolate against.

### Watch for redundancy, but do not clean it up in the same pass

Once the field exists, product-specific exemptions already in the formula become redundant. Leave
them until the backfill is verified complete — removing them in the same change means an incomplete
backfill silently starts flagging every record they used to cover.

---

## Expired vs removed — End Date only means something alongside Status

A software record's end-date field carries two different meanings, and which one applies is
determined by the status field. Reading the date on its own is how a lapsed vendor contract gets
misread as a wave of departures — or how a real departure hides inside contract noise.

| Status | What the End Date means | Shape in the data |
|---|---|---|
| Active | the **contract term** ends then | one shared date across every record of that type/license; start dates vary per person |
| Deactivated | **that person** lost the seat on that date | dates all differ — they are individual removal dates |
| Expired | the term ended; that whole generation is retired | one shared date, matching the Active generation it replaced |

**The shape is the tell.** If every flagged record in a type/license group shares the same end
date, it is a contract event. If the dates scatter, they are individual removals.

### Contract generations

Software records are **generational**: one record = one person, one license, **one contract term**.
On renewal the existing generation is set to Expired and a **new generation of records is created**
with the new term — records are not edited in place to extend them. A platform that has renewed
several times accumulates many Expired records; one that has never renewed under this model has
none, and its first flip has no precedent to copy.

### Surface it as one line, not sixty

Group these flags by (type, license, end date) rather than listing them per person. A lapsed
contract affecting sixty seats is **one** finding that names the contract — sixty individual
checkover lines bury the signal and say nothing about why. Reserve per-person lines for flags
whose causes genuinely differ.

Where renewals are handled by a person who is already in the loop, the audit does not need to
predict or automate them. It only needs to say *"this looks expired"* clearly enough that the
lapse can be tracked down — a look-ahead or auto-renewal mechanism is scope the process does not
need and will drift out of date.

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

## A credential failure must never be silent

A bare `except: pass` around an API call turns an expired credential into a permanent, invisible
downgrade. In one case an offboarding-ticket lookup used to suggest removal dates sat behind exactly
that, and a dead token meant **every** suggestion fell through to "not found" — for months, with no
error, and output that still looked reasonable. The message was read as a finding about the data
rather than a symptom of a broken credential.

**Print a reason on every failed call**, including which credential failed and what degrades as a
result.

## Before maintaining a script-owned credential, check whether anything headless actually runs

A script that writes to a ticketing system usually needs its own token *because a scheduler runs it
unattended*. If there is no scheduler — no cron entry, no launchd job, the runner script called by
nothing — that justification is gone, and the credential is pure maintenance cost.

The alternative is to let the script **produce** its output and have the interactive agent **push**
it, using whatever integration the session already has. Note the hard constraint: **a standalone
script cannot call an MCP server** — that lives in the agent's session, not in the process. So the
split is: script writes files to disk and prints the exact prompt for pushing them; agent does the
API call.

Make that the documented path rather than a workaround, and have the no-credential branch degrade
loudly — write the output, name the file, state what was skipped.

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

> Worked example: an e-signature cross-ref keyed on a single permission set flagged ~10 senior staff as "not on platform" every month. Widening to all permission sets **plus the System Administrator profile** dropped that list from 10 to 1 — every one of the 10 was a false negative, confirmed by envelope-creation history. Zero were stale.

**The narrow query was also hiding real findings.** After widening, the *other* direction of the
cross-ref surfaced four genuine items that had been invisible: a shared service account with no
software record, two people holding the license and actively using it with no record at all, and
one record carrying a misspelled email address. A check that is too narrow does not just add
noise — it suppresses signal, because the people it wrongly flags are the same people it never
looks up correctly.

⚠️ **When you measure a cross-ref change, replicate the pipeline's own email normalization.**
Platform rosters and software records often differ by domain (`.net` vs `.com`) and the script
normalizes both sides before comparing. A comparison that skips that step makes every person
appear on *both* sides of the gap, which reads as the fix having made things dramatically worse.
Compare against the normalized inputs, not the raw query results.

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

---

## Writing audit results back into a spreadsheet someone else maintains

When the audit's numbers already have a home — a monthly sheet a stakeholder reads and reconciles —
updating that sheet in place beats handing over a new export. The format they trust survives, and
the double entry disappears. Three things make the difference between that working and quietly
corrupting their file.

### Count usage from the platform, not from the licence records

An audit usually maintains its own licence records, and it is tempting to count those. Don't — not
for a *usage* number. Those records carry **contract dates**, so a licence whose term lapses
mid-month computes to **zero** at month end while the seats are plainly still in use. A renewal that
extends a term to the 30th makes every 31st-of-the-month count read zero.

Prefer, in order:

1. **Org licence objects** — these carry purchased *and* consumed seats together, so allowed and
   in-use come from one source that cannot disagree with itself.
2. **Managed-package licence objects** — same, per package.
3. **The vendor's own directory API** for anything with no in-org object.

Only fall back to your own records where no platform source exists. The platforms have no notion of
your contract calendar, so the contract can never corrupt a usage figure.

Two traps in the licence objects themselves: an *allowed* value of **-1 means the package does not
meter seats at all** — report that as unknown, never as zero, because the real number lives in the
contract. And an allowed figure with no API behind it is a contract term; leave those cells alone
rather than writing a guess.

### A live count cannot reconstruct a past month

This is the hard limit of the whole approach and it deserves an explicit guard, not a note in a
runbook. A platform count is a snapshot of *right now*. Run the job in December to fill August and
it will cheerfully stamp December's headcount into August's column, with no error and no way to
tell afterwards.

Encode the calendar as refusals:

- target month has not closed → refuse
- target is older than the month that just closed → refuse
- run is more than about a week past month end → proceed, but warn that the figure has drifted

Each refusal wants an override flag, because someone will eventually have a reason. What matters is
that the default is refusal and the override is a deliberate keystroke. Backfilling anything older
needs a historical source; this mode is not one.

### Bound every row scan by its block — an overrun conceals itself

A sheet tab often holds several stacked blocks: a header row naming the periods, some labelled
metric rows, then a free-form list running down under one of them. Writing that list means scanning
down a column — and a **fixed-width window is wrong**, because the list's length varies and the
window will reach into the block below.

What makes this worse than an ordinary off-by-one: the overrun blanks the *next* block's header row.
If blocks are located by matching their header — which is the right way to do it, since it survives
tab renames and shifted rows — then destroying a header makes that block **invisible to every
subsequent run**. The job then reports success while silently writing half of what it should. The
first run does the damage; every later run hides it.

Two limits, and both are required:

- stop at the next period-header row, and
- stop at the next labelled row in the first column

Neither alone suffices, because a header row's own first column is typically blank — so the
label test walks straight past it into the following metric row.

Also **blank the tail**. A list that is shorter this month than last leaves the previous run's
entries sitting underneath it, and they read as part of this month's data.

### Prove it on a copy, and diff the copy against the original

Copy the file, point the code at the copy, run it, then **diff the copy against the original
column by column**. Not "does it look right" — an actual cell-by-cell comparison, which is the only
thing that surfaces a write outside the intended range. The overrun above was found exactly this
way, and every difference the diff reported was either an intended write or a pre-existing
difference in the copy; that is the standard to hold.

Then verify every write by reading it back and comparing to the source. A spreadsheet write call
returns success for values that were coerced, dropped, or landed somewhere unexpected.

### Reaching a file the automation did not create

An OAuth token scoped to only the files an app created cannot touch a document owned by someone
else — which is exactly the case for a sheet a colleague maintains. A broad drive scope can. If a
past attempt concluded "this can only create documents, not edit them," re-check the token's current
scopes before designing around that limitation; scope sets change when other features are added, and
the conclusion goes stale silently.
