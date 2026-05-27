# PPP Rep-Performance KPIs — Definitions

How Precision Painting Plus measures Field Member reps today. These are the exact metric definitions behind PPP's monthly/quarterly scorecards — use them so the Command Center's leaderboard and rep profiles match the org's existing numbers. Field-name and object gotchas are in `BUSINESS_RULES.md`; concrete SOQL examples are in `reference-code/`.

> **Intentionally excluded:** actual per-rep compensation figures (draws), individual GM targets, and internal recipient emails/User IDs. This doc is the *logic*, not the data. Pull live values from Salesforce.

**Universe:** active `User` with Profile `*Standard.Field`. **Sales metrics attribute by `Opportunity.OwnerId`; WorkOrder metrics by `WorkOrder.OwnerId`; reviews by `Account.OwnerId`.**

**Reporting period:** the standard quarterly scorecard reports the **just-completed fiscal quarter** (the "previous fiscal quarter," PFQ) — *not* the in-progress quarter — typically run ~the 5th of the following period so reps can finish entering the prior period's data. Most KPIs anchor on a single in-period date (`CloseDate` / WO `EndDate` / `AppointmentDate__c` / Transaction `Date__c`); **Commissions (KPI 9) is the exception** — it reconciles cumulatively over the current fiscal year (CFY-to-date).

---

## KPI 1 — Revenue Performance
- **Total sales:** `SUM(Opportunity.QuotedSubtotalWithChangeOrder__c)` where `IsWon = true`, by `OwnerId`, dated by `CloseDate` in period. (Shortcut: `SubQuota__c.Attained__c` holds this rolling sum per rep/month — cheaper, cross-check against the Opportunity aggregate.)
- **Goal:** annual `TotalQuota__c.QuotaAssigned__c` (Owner allocation, Active, current FY); monthly `SubQuota__c.Assigned__c`. Quarterly = sum the 3 fiscal-quarter SubQuotas. Stored in points = dollars 1:1.
- **% to Goal:** Total Sales ÷ Goal. **Rank vs team:** dense rank of Total Sales across the active rep set.

## KPI 2 — Gross Margin (on completed Work Orders)
- **Avg GM%:** `AVG(WorkOrder.Gross_Margin_Percent__c)`; **Total GP$:** `SUM(WorkOrder.GrossProfit__c)`. Completed jobs only (`Status IN ('Closed','Complete Paid in Full','Complete Balance Owed')`), dated by `EndDate`.
- **GM vs target:** rep's avg GM% minus `User.Gross_Margin_Goal_Percent__c` (per-rep target field).

## KPI 3 — Close Rate
- For Opportunities **created** in the period (by `OwnerId`), fraction with `IsWon = true`.
- **Self-gen** = `LeadGroup__c` ∈ {`'Self-Generated'`, `'Trade Show'`, `'Repeat'`, `'Referral'`} *(updated 2026-05-21)*; **Marketing** = everything else (+ null); **Overall** = combined. Three cells.

## KPI 3b — Sales Mix (self-gen vs marketing share)
- Of Closed-Won sales **closed** in the period (anchor `CloseDate` — note: different anchor than KPI 3), the **$-based** self-gen share: `SUM(QuotedSubtotalWithChangeOrder__c)` for self-gen ÷ total. (Count-based version also computable from the same query but not the committed metric.)

## KPI 4 — Pricing Discipline (completed WOs, by `WorkOrder.OwnerId`, dated `EndDate`)
- **Revenue per Labor Day — projected vs actual**, computed over the **attendance-logged subset only** (`LaborDaysActual__c > 0`) so the two ratios are apples-to-apples:
  - Projected = `SUM(Quoted_Subtotal_with_Change_Order__c) / SUM(LaborDaysProjected__c)`
  - Actual = `SUM(Quoted_Subtotal_with_Change_Order__c) / SUM(LaborDaysActual__c)`
  - ~32% of completed WOs have no attendance logged; if you sum revenue over *all* WOs but days over only logged ones, Actual $/day inflates ~3×. Restrict both sides to the logged subset.
  - **Don't use `WorkOrder.RevenuePerLaborDay__c`** (uses settled `NetValue__c` + only the actual side).
- **Materials %:** `SUM(TotalNonBillablePurchases__c) / SUM(Quoted_Subtotal_with_Change_Order__c)` (weighted). Use `TotalNonBillablePurchases__c`, not `CostMaterials__c`. Lower is better.

## KPI 4b — Crew Attendance Completeness (data-quality check; completed WOs, by `WorkOrder.OwnerId`, dated `EndDate`)
The "logged subset only" filter in KPI 4 exists because crew attendance is frequently never entered on completed jobs. Tracking the gap turns it into something reps can act on.
- **Completed WO universe:** `Status IN ('Closed','Complete Paid in Full')`, `EndDate` in period, by `OwnerId`.
- **Missing attendance:** of those, the WOs with `LaborDaysActual__c = 0 OR LaborDaysActual__c = null` — i.e. no `WorkOrderCrew__c` ("Crew Attendance") child records have rolled up. (`LaborDaysActual__c` = sum of labor days from the related Crew Attendance records.)
- **Completeness %** = logged ÷ completed; higher is better. Roughly two-thirds of completed WOs are logged org-wide — the same ~32% gap cited in KPI 4.
- **Why it matters:** a no-attendance WO has `LaborDaysActual__c = 0`, so KPI 4 must exclude it; its revenue still lands elsewhere, so leaving it unlogged understates labor and (if not excluded) inflates Actual $/day ~3×. The `Add_Assigned_Labor_Crew` validation rule already forces the `Contractor__c` ("Assigned Labor Crew") lookup before close, but does **not** force attendance records — hence the gap.
- **Rep follow-up list:** the specific missing WOs, grouped by `OwnerId`, with `WorkOrderNumber`, `Account.Name`, `Quoted_Subtotal_with_Change_Order__c`, `StartDate`, `EndDate`, `Contractor__r.Name`. SOQL in `reference-code/queries.py`. *(The rendered list is live customer/rep data — kept out of this repo per the curation rules.)*

## KPI 5 — Appointments Activity (Opportunity, by `OwnerId`)
- **# appointments run:** `AppointmentDate__c` in period AND `Cancelled_Appointment__c = false`. (Context only — marketing-driven, no good/bad trend arrow.)
- **% estimates sent:** of those appointments, the subset with `Estimate_Sent__c = true`. ↑ good.
- **% cancelled:** appointments scheduled in period (`AppointmentDate__c`) with `Cancelled_Appointment__c = true` ÷ all scheduled. ↓ good.

## KPI 6 — Pipeline Management (snapshot, by `OwnerId`)
- **% open Opps with stale estimate:** `IsClosed = false` AND `Estimate_Sent__c = true` AND `Date_Estimate_Sent__c < TODAY−30`, over **all** open Opps. (PPP cycle is ~3–4 weeks, so >30-day-old open estimates signal weak follow-up.) ↓ good.

## KPI 7 — Production Quality
- **Jobs completed vs sold:** `COUNT(WorkOrder Status IN ('Closed','Complete Paid in Full'), EndDate in period, by OwnerId)` ÷ `COUNT(Opportunity IsWon=true, CloseDate in period, by OwnerId)`.
- **Change orders:** `SUM(WorkOrder.TotalChangeOrder__c)` (rolls up approved `ChangeOrder__c.CostChange__c`).
- **Reviews:** count `Review__c` with `GoodReview__c` / `BadReview__c`, `Removed__c = false`, by `Account__r.OwnerId`.
- **Complaints:** `Case.Type IN ('Dissatisfied Customer','Service Call')`, opened in period, by `Case.Opportunity__r.OwnerId`.

## KPI 8 — Money Flow (`Transaction__c`, `Date__c` in period, by `WorkOrder__r.OwnerId`)
- **Money Collected:** `SUM(Amount__c)` for record type `Payment_In`.
- **Labor Paid Out:** `SUM(Amount__c)` for `Payment_Out` AND `PayeeType__c = 'Labor_Company'`.
- **Total Purchases:** `SUM(Amount__c)` for record type `Purchase`.

## KPI 9 — Commissions
- **Draw Received:** `User.Quarterly_Draw__c × fiscal-quarter index`, CFY-to-date cumulative (Q1→×1, Q2→×2, Q3→×3, Q4→×4) so it lines up with the CFY paid window. *(Actual per-rep values intentionally not in this doc — read from the field.)*
- **Commissions Earned:** `SUM(Transaction__c.Amount__c)` where record type `Payment_Out`, `WorkOrder__c != null`, **`PayeeType__c = 'Sales'`**, **`Description__c LIKE '%Draw%'`**, `Date__c` in the **current fiscal year** (CFY — cumulative, not a single quarter). Attributed by Payee name = **`User.Name` OR `'LC ' + User.Name`** (the labor-company alias; payee naming is inconsistent across reps). Not scoped to the rep's own WOs. Watch for `<Name>-inactive`/`-portal` shadow Users. *(Redefined 2026-05-21.)*
- **Difference** = Earned − Draw. >0 underpaid (green), <0 overpaid (red).

---

## Manager-overview rollups
- Team membership from the `Sales_Team_Member` permset.
- **Aggregation rule:** weighted means for ratios (GM%, Materials %, close rate, stale %); simple sums for counts/currency. Never mean-of-means for ratios.
- Comparison periods: YTD vs prior YTD · month-over-month · quarter-over-prior-quarter.
