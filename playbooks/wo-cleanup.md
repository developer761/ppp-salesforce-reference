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

### Rule 1: Opp Lost + WO not Canceled
**Expected:** when Opp is "Opportunity Lost", all WOs should be Canceled.

- **Auto-cancel** if WO has no transactions (`TotalPaymentsIn__c`, `TotalPayoutsForLabor__c`, `TotalNonBillablePurchases__c`, `TotalBillablePurchases__c` all zero/null)
- **Flag** if transactions present — requires manual review before canceling

### Rule 2: Opp Closed Won + all WOs Canceled
**Expected:** a Closed Won opp should have at least one active (non-Canceled) non-estimate WO.

- **Auto-move to Opportunity Lost** if no transactions on any WO
- **Flag** if transactions present — validate transaction dates before moving
- **Skip** if opp has another active non-estimate WO (real job still active → Closed Won is correct)

**Exclusions (both rules):** estimate appointment WOs, opps owned by specific excluded owners, opps where `Corporate_Name__c` contains 'tomco'.

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

**Fix:** Add the zip to the out-of-area ST → move the opp → remove the zip. Hyphenated zips (`11801-4431`) may need the 5-digit form (`11801`) added — check whether the base form exists first.

### `FY_Assigned__c` — no auto-update on CloseDate change
`Opportunity.FY_Assigned__c` (text, e.g. "2026") represents the PPP fiscal year the opp is assigned to, using the FY **starting** year. No flow updates it when CloseDate changes — run a separate correction pass if CloseDates are bulk-corrected.

Formula: `month >= 2 → FY = CloseDate.year; month == 1 → FY = CloseDate.year - 1`

PPP FY starts Feb 1 (FY26 = Feb 1, 2026 – Jan 31, 2027).
