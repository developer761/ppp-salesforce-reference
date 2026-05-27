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
| S-Sign | `PermissionSetAssignment WHERE PermissionSet.Name = 'SSign_Experience_Cloud_User'` |
| Dialpad | REST API — `/users` endpoint |
| Google PPP | GAM CLI — `gam print users` |
| Slack PPP | Slack API — `users.list` |
| Slack O3 | Slack API — `users.list` (separate workspace) |

---

## Step 1 — Run the audit script

The script (`software_audit.py`) handles all data collection automatically:

1. Queries each platform for active license count and user list
2. Compares counts against contract limits
3. Cross-references platform user emails against `Software__c` active records — flags anyone in a platform with no SW record, or in SW with no platform presence
4. Enriches gaps into three buckets: email mismatch (SW record exists under different email), known staff (SW record of this type missing), unknown (no SF footprint — investigate before creating anything)
5. Creates the Airtable ticket with an action items block and full audit report

Review output before proceeding. Resolve or note any gaps.

---

## Step 2 — Checkover field audit

Query `Software__c` and `Allocation__c` for records where `Checkover__c != 'Good'` and `Status__c = 'Active'`.

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

## Email normalization note

Salesforce users may be set up with `.com` or `.net` email variants; SW records may use either. During cross-reference, normalize both sides to `.com` before comparing to avoid false-positive mismatches. Do not modify any records based on the normalization — it is in-memory only.

---

## Known platform gaps (do not flag as errors)

| Platform | Gap | Notes |
|---|---|---|
| S-Sign | Unlimited license — live count will exceed SW records | By design |
| Salesforce system accounts | Integration/analytics users appear in the SF user list | Maintain an exclusion list of known system account emails in the script |
| Dialpad office/dept lines | Appear in the number pool but are not billed as user licenses | Document in SW record notes; offset the expected count |
| Google O3 | Small fixed list — cross-ref handled manually | Automate if the list grows |

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
