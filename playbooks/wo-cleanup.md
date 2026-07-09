# Playbook — WO Cleanup (Bi-Weekly)

Recurring cleanup of three categories of WorkOrder data violations in PPP's Salesforce org. Runs bi-weekly via `/wo-cleanup` slash command.

---

## Section 1 — Estimate Appointment WO Violations

WOs whose `WorkType.Name` contains "Estimate Appointment" should be inert: `Status = Pending`, no dates, no crew, no transactions, no change orders, no balance.

### Violation phases (applied in order)

| Phase | What | Object | Key field |
|-------|------|--------|-----------|
| 1 | Deny open change orders | `ChangeOrder__c` | `Status != 'Denied'` |
| 2 | Delete attendance | `WorkOrderCrew__c` | — |
| 3 | Clear WO fields + set Pending | `WorkOrder` | `StartDate, EndDate, Contractor__c, RequestReview__c, Status` |
| 4 | Delete line items | `ChangeOrderLineItem__c` → `WorkOrderLineItem` | Delete COLIs first (blocks WOLI deletion if present) |
| 5 | Zero residual balance fields | `WorkOrder` | `Discount_Amount__c, CostMaterials__c` |

### `Canceled_Line_Items__c` is read-only
This stored Currency field on `WorkOrder` is populated by flow/trigger when WOLIs are canceled. It **cannot be set via Apex or API** — attempting to write it throws a compile error.

**Fix:** Delete the underlying WOLIs (and their `ChangeOrderLineItem__c` children first). The field recalculates to 0 automatically.

### Governor limit — batch WO updates at 10
Updating `WorkOrder` fields (including `Status`) fires:
`WorkOrder → WorkOrder_SetOpportunityFinancialFields → Opportunity update → Opportunity:Quota Points Record Creation`

At ~20+ WOs in a single DML, this chain hits a governor limit on Quota Points creation. Batch WO updates in groups of 10.

---

## Section 2 — Small Balance WOs

Real (non-estimate) WOs with small residual balances. Fix via `Internal_Adjustments__c`.

### Formula direction
`BalanceOwed__c = f(Revenue, Payments) + Internal_Adjustments__c`

`Internal_Adjustments__c` **adds** to the balance. To zero the balance:
```
Internal_Adjustments__c = (current ?? 0) - BalanceOwed__c
```
Adding BalanceOwed (intuitive direction) doubles the imbalance instead of zeroing it.

### Eligibility groups
| Group | Condition |
|-------|-----------|
| A | -$10 ≤ BalanceOwed < -$0.01 |
| B | $0 < BalanceOwed ≤ $10, EndDate > 60 days ago |
| C | $0 < BalanceOwed ≤ $1, any age |

**Excludes:** estimate appointment work types, WOs started/ended current month, WOs at exactly -$0.01 (acceptable final state).

### Two-pass rounding
After the initial adjustment, tax recalculation can leave a +$0.01 artifact. A second pass applies `-$0.01` to push to -$0.01 (acceptable). Target final state: `$0.00` or `-$0.01`.

### ±$10 guard
Before applying any adjustment, check: would `cur - BalanceOwed` fall outside `[-10, 10]`? If yes, flag for manual review. A large existing `InternalAdj` (e.g. $24) indicates prior manual intervention.

---

## Section 3 — Opp/WO Status Alignment

Detects and corrects mismatches between `Opportunity.StageName` and `WorkOrder.Status`.

"WO" in both rules means **real (non-estimate-appointment) WOs only** — estimate appointment WOs are excluded from all logic here.

### Transaction detection
Whether a WO "has transactions" is determined by querying related `Transaction__c` records (master-detail via `WorkOrder__c`), not by the aggregate currency fields (`TotalPaymentsIn__c` etc.) on the WO. Those aggregate fields can lag or differ.

### Rule 1: Opp Lost + real WO not Canceled → flag for manual review
**Logic:** A non-canceled real WO means actual work happened (or was in progress). The WO status reflects ground truth. If the WO isn't canceled, the job wasn't canceled — the Opp stage should be Closed Won, not Lost, and CloseDate will need to be corrected.

- **Flag all matches for manual review** — do not auto-change stage
- Reviewer sets `StageName = 'Closed Won'` and corrects `CloseDate` (3-step quote sequence required — see below)
- `CloseDate` should be set to a meaningful date (WO end date or last payment date)

**Exclusions (Rule 1):** estimate appointment WOs, opps owned by specific excluded owners, opps where `Corporate_Name__c` matches a configured corporate exclusion (see script config).

### Rule 2: Opp Closed Won + all real WOs Canceled → update Opp stage to Opportunity Lost
**Logic:** If all real WOs are canceled, no work was done. The Opp stage should reflect that.

- **Auto-update stage to Opportunity Lost** if no related `Transaction__c` records exist on any WO
- **Flag** if `Transaction__c` records are present — validate record dates vs current FY before updating; pre-FY records are generally safe to proceed
- **Skip** if opp has any other active (non-Canceled) real WO — work is still in progress → Closed Won is correct

**Exclusions (Rule 2):** estimate appointment WOs, opps owned by specific excluded owners, opps where `Corporate_Name__c` matches a configured corporate exclusion (see script config).

### Required sequence for any Opp stage change

A synced quote fights the stage change and triggers a bounce-back. `Opportunity_SetCloseDateOnClosedWon` (record-before-save flow) fires during the bounce and stamps `CloseDate = today`, corrupting it even though the stage change ultimately fails.

**Always use this 3-step sequence:**
```
1. Opportunity.SyncedQuoteId = null   →  update Opp  (unsync)
2. Quote.Status = 'Rejected'          →  update all non-rejected Quotes on Opp
3. Opportunity.StageName = '<target>' →  update Opp
```

Applies in both directions: Closed Won → Opportunity Lost and Opportunity Lost → Closed Won.

**If CloseDate is corrupted:** recover the pre-corruption value from:
```sql
SELECT OldValue, NewValue FROM OpportunityFieldHistory
WHERE OpportunityId = '<id>' AND Field = 'CloseDate'
```
Filter in Python for records where `CreatedDate` matches today.

### `WorkOrder_DisallowEditWhenClosed` flow
This record-before-save flow blocks edits to WOs in "Closed" status. Bypass requires `WorkOrder_AllowEditClosed` permission set.

### ST zip validation rule
Changing `Opportunity.StageName` triggers territory validation. Some opps fail with:
`FIELD_CUSTOM_VALIDATION_EXCEPTION: No Service Territory was found for ZIP code XXXXX`

**Fix:** Add the zip to the out-of-area ST → update the opp stage → remove the zip. Hyphenated zips (`11801-4431`) may need the 5-digit form (`11801`) added — check whether the base form exists first.

### `FY_Assigned__c` — no auto-update on CloseDate change
`Opportunity.FY_Assigned__c` (text, e.g. "2026") represents the PPP fiscal year the opp is assigned to, using the FY **starting** year. No flow updates it when CloseDate changes — run a separate correction pass if CloseDates are bulk-corrected.

Formula: `month >= 2 → FY = CloseDate.year; month == 1 → FY = CloseDate.year - 1`

PPP FY starts Feb 1 (FY26 = Feb 1, 2026 – Jan 31, 2027).

---

## Section 4 — Move WOs to Closed

Real (non-estimate) WOs where the job is fully complete should move to `Status = 'Closed'`. Because the `WorkOrder_DisallowEditWhenClosed` flow blocks edits once a WO is Closed, this step is **two-step and never auto-closes**: export candidates → human validates → close only the approved Ids.

### Auto-close criteria (all must be true)
- `Status` NOT IN (Coordination, Scheduling, On Hold, Pending, Canceled, Closed)
- `StartDate` and `EndDate` both set
- `LaborDaysActual__c` != 0
- `Contractor__c` != null (crew assigned)
- `RequestReview__c` != null
- `BalanceOwed__c` = 0
- `Total_Undeposited_Payments__c` = 0 — the **amount** field; do not use the count field `UndepositedTransactions__c`
- `LastPaymentIn__c` != null AND older than 7 days
- `TotalPayoutsForLabor__c` != 0
- **Excludes:** opps owned by specific excluded owners, opps where `Corporate_Name__c` matches a configured corporate exclusion (same exclusions as Section 3)

### Flag for manual review (meets all completion signals except one — do not close)
- `LastPaymentIn__c` is null → "no last payment date" (should not normally occur)
- `TotalPayoutsForLabor__c` = 0 AND `EndDate` older than 60 days → labor would have requested payment by then

### Silent skip (not closed, not flagged — reconsider next run)
- `TotalPayoutsForLabor__c` = 0 AND `EndDate` within 60 days → payout may simply be unrecorded
- `LastPaymentIn__c` within the last 7 days → too recent

### Batching
Close via REST composite (`PATCH /composite/sobjects`) in batches of 10 with `allOrNone=false` — same governor-limit reasoning as Section 1.

---

## Section 4b — Attendance-exempt corps (recurring)

Some licensee / commercial operators are not yet held to the attendance-logging policy and leave `LaborDaysActual__c` blank, so their completed WOs are structurally skipped by the Section 4 filter (which requires `LaborDaysActual__c != 0`). They accumulate as done-but-open WOs and need a separate close pass each cycle. Same two-step, never-auto-close discipline and REST-composite batching (10/batch, `allOrNone=false`) as Section 4.

### Base filter (WOs owned by a configured attendance-exempt owner list)
- Opp `StageName = 'Closed Won'`
- `Status` NOT IN (Coordination, Scheduling, On Hold, Pending, Canceled, Closed)
- `BalanceOwed__c = 0`
- `Total_Undeposited_Payments__c = 0`
- `StartDate` and `EndDate` both set
- WorkType does not contain "Appointment"

**Status is not gated on a specific done-status.** For these corps the label is unreliable (jobs sit on "Work In Progress" long after they settle), so doneness is established by dates + `$0` balance + crew payout instead. `Canceled`/`Closed` stay excluded — never close those.

### Then classify (mirrors Section 4)
- `TotalPayoutsForLabor__c` > 0 → **close-eligible** (crew was paid = work happened)
- `TotalPayoutsForLabor__c` = 0 AND `EndDate` older than 60 days → **flag** for review, never auto-close (payout would have been recorded by now — either unrecorded or the job wasn't actually done)
- `TotalPayoutsForLabor__c` = 0 AND `EndDate` within 60 days → silent skip (too recent — payout may simply be unrecorded)

### Preferred end state (retires 4b)
Fold the exemption into the Section 4 candidate logic: drop `LaborDaysActual__c != 0` from the hard filter and enforce it in classification instead — require it **unless** the owner is attendance-exempt, in which case use `TotalPayoutsForLabor__c` as the work-happened signal per the rules above. Validate with a read-only pass before adopting so nothing over-closes.
