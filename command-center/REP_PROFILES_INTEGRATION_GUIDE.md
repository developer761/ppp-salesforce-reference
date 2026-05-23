# Integrating PPP's Salesforce KPIs into the Command Center Rep Profiles

**Audience:** the engineer / AI assistant working on the PPP Command Center codebase.
**Goal:** wire PPP's *canonical* rep-performance KPIs into the existing **Rep Profiles** page (`/dashboard/rep` index + `/dashboard/rep/[id]` detail), using the same definitions PPP uses in its own Salesforce reports — so the dashboard's numbers match what PPP staff already read.

**Companion reference docs (this repo):**
- `salesforce/BUSINESS_RULES.md` — field-level gotchas (fiscal year, naming traps, `IsClosed`, GM field choice).
- `salesforce/REP_PERFORMANCE_KPIS.md` — exact KPI definitions (the spec).
- `salesforce/DATA_DICTIONARY.md` — every field/object API name.

> This guide assumes the reader has read those three files. It is written against the Command Center code as of the 2026-05 snapshot and cites real file paths and line ranges.

---

## 0. TL;DR

1. The Rep Profiles page **already works** off a bulk Salesforce snapshot (`lib/salesforce/queries.ts`) that pages **derive** from (`lib/salesforce/derive.ts`). Keep that pattern — add fields/objects to the *one* snapshot fetch and write new pure derivations. **Do not add per-rep SOQL** (it breaks the single-fetch, 5-min-cache model and N+1s at PPP's 89k-opp scale).
2. Before adding new KPIs, **fix five correctness mismatches** (Section 4) — otherwise the existing "Revenue Sold", "Conversion Rate", and "Activity" numbers silently disagree with PPP's reports.
3. Then layer in the missing scorecard KPIs (Section 3): % to Goal, Gross Margin vs target, Revenue per Labor Day, Materials %, appointments/estimates, stale pipeline, reviews, complaints, money flow, commissions.
4. **Validate every number against PPP's native FPRC Salesforce reports** (Section 7) before shipping. The reference KPI defs *are* those reports.

---

## 1. How the rep data flows today (shared context)

```
loadDashboardData()            lib/data-source.ts
  └─ getStoredSalesforceCredentials()   (Supabase-stored refresh token)
  └─ loadSalesforceSnapshot()    lib/salesforce/queries.ts   ← ONE bulk fetch, cached 5 min (Promise-cached)
       → SalesforceSnapshot { reps, opportunities, workOrders, accounts, quotes, … }
  └─ falls back to lib/mock-data.ts when SF not connected / returns 0 reps

Pages DERIVE views from the snapshot (no further SF calls):
  lib/salesforce/derive.ts
    deriveRepsForPeriod()      → Rep[]  (leaderboard + cards)
    deriveRepMonthly()         → 12-mo trend
    deriveRepRecentDeals()     → recent deals table
    deriveRepAccountStats()    → customer mix / repeat / BM / lifetime
```

**Rep Profiles surfaces:**
- `app/dashboard/rep/page.tsx` → `components/rep-index-view.tsx` (grid of `RepCard`s; period/region/sort filters).
- `app/dashboard/rep/[id]/page.tsx` (the detail page — **this is the main integration target**). It calls `deriveRepsForPeriod(snapshot, "lifetime")`, then renders: header (tenure, TTM revenue), a 4-up KPI row (Revenue Sold / Conversion Rate / Avg Ticket / Open Pipeline), Customer Mix + Lead Sources, 12-mo trends, an **"Activity · Last 30 Days"** block, and a Recent Deals table.

**The current `Rep` shape** (from `lib/mock-data.ts`): `revenueSold`, `closeRate`, `avgTicket`, `openPipeline`, `daysAvgClose`, `appointmentsHeld`, `quotesSent`, `region`, `serviceLine`, `startedAt`. Several of these are **proxies**, not PPP's real metrics — see Section 4.

---

## 2. Recommended integration approach

**Extend the snapshot, derive on the client. Three layers, in order:**

1. **`lib/salesforce/queries.ts` — add to the bulk fetch.**
   - Add the missing fields to existing object pulls (Opportunity, WorkOrder, User, Account).
   - Add new windowed pulls for `Transaction__c`, `Review__c`, `Case`, and the quota objects (`TotalQuota__c` / `SubQuota__c`). Mirror the existing parallel-promise + `queryMore` pagination pattern. Window them (`LAST_N_DAYS` / FY bounds) — `Transaction__c` and `Case` are high-volume.
   - Extend the `SalesforceSnapshot` type with the new arrays/fields.

2. **`lib/salesforce/derive.ts` — add pure per-rep derivations.**
   - One function per KPI group, e.g. `deriveRepScorecard(snapshot, repId, period)` returning the full KPI bundle. Pure functions, no SF calls, safe to run server- or client-side.
   - Reuse the existing `periodRange()` / `isInRange()` helpers — **but** add PPP fiscal-period helpers (Section 5, fiscal year). PPP anchors most KPIs on **fiscal** periods, not rolling calendar windows.

3. **`app/dashboard/rep/[id]/page.tsx` — render new sections.**
   - Add KPI cards / mini-tables that read the new derived bundle. Keep the existing mobile-first card patterns and brand classes (`ppp-*`). Gate each new section on data presence (`{stats && …}`) exactly like the current Customer Mix block, so a rep with no quota/cost data degrades gracefully instead of rendering `$0` / `NaN`.

**Why not per-rep SOQL?** The snapshot is fetched once per page load and shared by every card via a Promise cache (`queries.ts` `cached()`). Per-rep queries would multiply SF API calls by ~26 reps and defeat the cache. Pull once in bulk, slice per rep in memory.

---

## 3. KPI integration map

For each PPP KPI: the canonical definition (see `REP_PERFORMANCE_KPIS.md`), the SF source, what to change in the snapshot, and where it lands on the rep profile. **Bold = not currently pulled.**

| KPI | PPP definition (canonical) | SF source | Snapshot change | Rep-profile placement |
|---|---|---|---|---|
| **Revenue / sales** | `SUM(Opportunity.QuotedSubtotalWithChangeOrder__c)` where `IsWon`, by `OwnerId`, dated by `CloseDate` | Opp (or WO `Quoted_Subtotal_with_Change_Order__c`) | **Switch canonical field** — see §4.1 | Existing "Revenue Sold" card (fix the field) |
| **% to Goal** | Sales ÷ `TotalQuota__c.QuotaAssigned__c` (Owner/Active/CFY) or `SubQuota__c.Assigned__c` | **`TotalQuota__c` / `SubQuota__c`** | **New pull**; join `TotalQuota__r.User__c → rep` | New "Quota" card (gauge: attained vs goal) |
| **Gross Margin %** | `WorkOrder.Gross_Margin_Percent__c` = `GrossProfit__c / Quoted_Subtotal_with_Change_Order__c`; target = `User.Gross_Margin_Goal_Percent__c` | WO formula field + **User field** | **Add `Gross_Margin_Percent__c`** to WO select; **add `Gross_Margin_Goal_Percent__c`** to User | New "Gross Margin vs target" card |
| **Close rate** | won ÷ opps **created in period**, bucketed self-gen vs marketing by **`Opportunity.LeadGroup__c`** | Opp (`LeadGroup__c`, `IsWon`, `CreatedDate`) | **Add `Opportunity.LeadGroup__c`** (snapshot only pulls `Account.LeadGroup__c`) | Replace current "Conversion Rate" (see §4.5) |
| **Pricing: Rev per Labor Day** | `SUM(quoted) / SUM(LaborDaysActual)` vs `…/Projected`, **logged subset only** (`LaborDaysActual > 0`) | WO `LaborDaysActual__c`/`Projected__c` (already in snapshot!) | none (already pulled) | New "Pricing discipline" card |
| **Materials %** | `SUM(TotalNonBillablePurchases__c) / SUM(quoted)` | **`WorkOrder.TotalNonBillablePurchases__c`** | **Add field** | Pricing card sub-stat |
| **Appointments / Estimates** | `AppointmentDate__c` in period + `Cancelled_Appointment__c=false`; `% Estimate_Sent__c` | **Opp `AppointmentDate__c`, `Cancelled_Appointment__c`, `Estimate_Sent__c`, `Date_Estimate_Sent__c`** | **Add fields** | Replace the fake "Activity · Last 30 Days" block (§4.6) |
| **Stale pipeline %** | open opps w/ `Date_Estimate_Sent__c < TODAY−30` ÷ all open | Opp (add the estimate date field) | **Add field** | New "Pipeline health" stat (note: 30d, not the current 14d — §5) |
| **Jobs completed vs sold** | `COUNT(WO Status∈completed, EndDate in period)` ÷ `COUNT(Opp IsWon, CloseDate in period)` | WO `Status` (in snapshot) + Opp | none / minor | New "Production" stat |
| **Reviews** | `Review__c` `GoodReview__c`/`BadReview__c`, exclude `Removed__c`, by `Account__r.OwnerId` | **`Review__c`** | **New pull** | New "Reviews" stat |
| **Complaints** | `Case.Type IN (…)`, opened in period, by `Case.Opportunity__r.OwnerId` | **`Case`** | **New pull** | New "Complaints" stat |
| **Money Flow** | `Transaction__c` `Payment_In` / `Payment_Out`(Labor) / `Purchase` by `WorkOrder__r.OwnerId` | **`Transaction__c`** | **New pull (windowed!)** | New "Money Flow" card |
| **Commissions** | `User.Quarterly_Draw__c` vs `SUM(Transaction Payment_Out, Payee=rep)` | **User field + Transaction** | **Add field + pull** | New "Commissions" card (green=underpaid / red=overpaid) |

> The snapshot **already carries** the WorkOrder ops fields (`grossProfit`, `commissionAmount`, `costMaterials`, `totalPayoutsForLabor`, `laborDaysActual/Projected/Remaining`, `balanceOwed`, `finalBalanceAging`). So **Pricing/Labor-Day, Materials (after adding one field), AR/balance, and per-WO margin are reachable with little new query work.** The expensive additions are `Transaction__c`, `Review__c`, `Case`, and the quota objects.

---

## 4. ⚠️ Critical mismatches — fix these first (correctness, not features)

These make the *existing* rep numbers disagree with PPP's reports. Fix before adding KPIs.

### 4.1 Revenue field: `NetValue__c` vs `QuotedSubtotalWithChangeOrder__c`
`queries.ts` prefers **`NetValue__c`** as the canonical revenue field for both Opp and WO (`PREFERRED_OPP_REVENUE_FIELDS` / `PREFERRED_WO_REVENUE_FIELDS`, both start with `NetValue__c`). PPP's rep "sales" metric — and everything tied to quota — is **`QuotedSubtotalWithChangeOrder__c`** (Opp) / **`Quoted_Subtotal_with_Change_Order__c`** (WO). These differ whenever a job didn't collect the full quote (NetValue = settled; QuotedSubtotal = billable). **Effect:** "Revenue Sold" won't match the rep's quota attainment or PPP's "FY Sales by Close Month."
**Fix:** for rep-performance/quota surfaces, derive revenue from the *quoted* field. The WO query currently throws the quoted figure away — `quotedSubtotal` is hardcoded `0` (`queries.ts` ~669) and the field isn't even selected. Add `Quoted_Subtotal_with_Change_Order__c` to the WO select and populate `quotedSubtotal`, then have `revenueRows()` (in `derive.ts`) use it for the sales/quota KPIs. Keep `NetValue__c` available for "realized/collected" views, but label them distinctly.

### 4.2 Snapshot window filters on `CreatedDate`, but revenue buckets on `CloseDate`
The snapshot pulls `WHERE CreatedDate = LAST_N_DAYS:365` (`RECENCY_WINDOW_DAYS`, used for Opps, WOs, Quotes). But `deriveRepsForPeriod` / `deriveCompanyTrend` bucket revenue by **`closeDate`**. A deal **created >365 days ago but closed last week is absent from the snapshot entirely**, yet it belongs in this month's revenue. **Effect:** recent revenue is undercounted for long-cycle jobs; the longer PPP's sales cycle, the worse. PPP reports anchor on CloseDate (often Created-in-CFY **and** CloseDate-in-quarter).
**Fix:** pull the revenue objects with a `CloseDate`-based window (or widen materially and filter in-memory). At minimum, document the bias. Reconcile against the FPRC reports' CFY/PFQ windowing.

### 4.3 "lifetime" on the rep detail isn't lifetime
`rep/[id]/page.tsx` (~71) calls `deriveRepsForPeriod(snapshot, "lifetime")` and the header shows "Trailing 12-month revenue" / lifetime customer counts. But the snapshot only holds ~365 days of *created* records (§4.2). So "lifetime" ≈ "last 12 months by created date." **Effect:** tenure-long totals and repeat-customer history are truncated. **Fix:** either widen the pull for the detail page, or relabel these as 12-month figures so they're not read as career totals.

### 4.4 Rep universe is broader than PPP's field-sales team
`isLikelyRep()` (`queries.ts` ~224) includes any active `Standard`/`PowerPartner`/null-UserType user not on a skip-list, and `deriveRepsForPeriod` even appends **"orphan owners"** (admins who own WOs, ~289-310). PPP's actual rep universe is **Profile = `*Standard.Field`** (~26 active); the sales manager's team is the **`Sales_Team_Member`** permset. **Effect:** office/admin/manager/internal users appear as "reps," and they pollute the **team-average denominators** the detail page computes (`teamAvgRevenue`, `teamAvgCloseRate`, …). **Fix:** filter the rep roster to Profile `*Standard.Field` (or the `Sales_Team_Member` permset for the manager view). Keep an "include orphan owners" escape hatch only for an explicit admin/debug view.

### 4.5 Close-rate definition differs (and the "100% won" trap)
Current close rate = **Opp→WO conversion** (`derive.ts` ~215-240). The code comment notes PPP's stages have **no "Closed Lost" type, so `IsWon`/`IsClosed` reads ~100%** — a real and important PPP quirk. PPP's *KPI* close rate is **won ÷ opps created in the period**, split self-gen vs marketing by **`Opportunity.LeadGroup__c`** (`Self-Generated`, `Trade Show`, `Repeat`, `Referral` = self-gen; everything else = marketing — note "Trade Show" has a space). **Fix:** confirm how "lost" deals are represented in PPP's data, then implement the cohort-based won-rate with the LeadGroup buckets. Pull `Opportunity.LeadGroup__c` (the snapshot only has `Account.LeadGroup__c` today, which is *not* the same field PPP classifies on).

### 4.6 "Appointments held" and "Quotes sent" are fakes
`deriveRepsForPeriod` sets `appointmentsHeld = quotesSent = a.total` (opp count proxy, ~275-276). The detail page's **"Activity · Last 30 Days"** renders these as real appointment/quote counts — they aren't. Also `Quote.opportunityId` is hardcoded `null` in the snapshot (`queries.ts` ~452), so quotes can't be attributed to a rep at all. **Fix:** for appointments use `Opportunity.AppointmentDate__c` + `Cancelled_Appointment__c`; for "estimates sent" use `Estimate_Sent__c` / `Date_Estimate_Sent__c`; if you want true quote counts per rep, re-link `Quote` to its Opportunity (restore `OpportunityId`).

---

## 5. Edge cases & gotchas

- **Field-naming trap (Opp vs WO).** Same concept, two API names: `Opportunity.QuotedSubtotalWithChangeOrder__c` (no underscores) vs `WorkOrder.Quoted_Subtotal_with_Change_Order__c` (underscores). A SOQL written for one fails on the other. The snapshot's schema auto-detection already handles both — keep that when adding fields.
- **Fiscal year.** PPP FY = **Feb 1 → Jan 31**, FY name = start year. Quarters: Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4 Nov-Jan. The current `periodRange()` uses **calendar** year/month/rolling windows — add fiscal-period helpers, because % to Goal, quota, and the FPRC reports are all fiscal ("Created in CFY AND CloseDate in PFQ").
- **`WorkOrder.IsClosed` is unreliable** — true only for `Status='Closed'`, misses `'Complete Paid in Full'` / `'Complete Balance Owed'`. The Command Center already filters on the **Status string** (`woStatusBucket`, funnel "paid in full") — good; keep doing that, don't switch to `IsClosed`. Completed-job set = `Status IN ('Closed','Complete Paid in Full','Complete Balance Owed')`.
- **Gross-margin "fake 100%".** The Command Center's `trueGrossProfit()` distrusts `Gross_Profit__c` (it can equal the amount when costs aren't entered) and recomputes GP from explicit costs with a 5-85% sanity band. That's a sound *data-quality* guard, but PPP's **canonical** GM% is the formula field `WorkOrder.Gross_Margin_Percent__c` (= `GrossProfit__c / Quoted_Subtotal_with_Change_Order__c`). **Do not** use `GrossProfitPercent__c` (its denominator is `NetValue__c`, inflating margins). Recommended: read PPP's `Gross_Margin_Percent__c` for display, but keep the cost-coverage caveat — surface "GM based on N of M jobs with cost data entered," since a large share of completed WOs have incomplete cost/attendance data.
- **Quota = points, 1:1 with dollars**, but **quota data is sparse** — most reps don't have an Owner-allocated `TotalQuota__c` set up yet. So **% to Goal will be empty for most reps** in both prod and sandbox. Render a graceful "no quota set" state, not `0%` or `Infinity`. Filter `TotalQuota__c` to `Allocation__c='Owner'`, `Status__c='Active'`, `QuotaType__c='Field_Member'` and exclude `CatchAll`. Trap: `SubQuota__c.CurrentUserId__c` is the *viewer's* id, not the rep — join on `TotalQuota__r.User__c`.
- **Stale-pipeline threshold.** `derivePipelineAtRisk` uses **14 days** on `lastActivityDate`. PPP's KPI uses **>30 days** on `Date_Estimate_Sent__c` over open opps. Different field, different threshold — don't conflate the "at risk" company metric with the rep "stale estimate %" KPI.
- **Region / service line.** Region is inferred as the rep's most-common `Account.Region__c`; service line from a role/profile string match. PPP's geographic truth is `ServiceTerritory` (`Account.Service_Territory__c`, already in the snapshot) and `Region__c` values may be coarser than the mock's borough split. Verify against real values before trusting region filters; treat service line as low-confidence until a real field is confirmed.
- **FLS + read-only access (important).** The Command Center's SF access is **read-only**. Every new field/object the integration reads (`Gross_Margin_Goal_Percent__c`, `Quarterly_Draw__c`, `TotalQuota__c`/`SubQuota__c`, `Transaction__c`, `Review__c`, `Case`, `TotalNonBillablePurchases__c`, `Opportunity.LeadGroup__c`, appointment/estimate fields) must be **readable by the integration user's profile/permission sets**. In Salesforce, a field the running user can't see is **silently omitted** (or errors the SOQL) — you'll get `0`/missing, not an exception you'll notice. Confirm FLS for the OAuth service-account user before trusting any new KPI. (PPP uses a granular permission-set-group model; new read access may need a permset.)
- **Service-account record visibility.** Per `lib/salesforce/client.ts`, queries run as whoever completed the OAuth dance. If that user sits low in the role hierarchy or sharing is private, they won't see other reps' Opps/WOs → systematic undercount. Use a service account with org-wide read (View All) for complete cross-rep data.
- **Sandbox vs prod drift.** The snapshot auto-detects sandbox. Sandbox FLS/data drifts from prod (some fields/records present in one only). Validate in whichever org is wired, and re-validate after a prod cutover. The rep index already shows a "Sandbox data" banner — keep it.
- **Performance at PPP scale.** 89k+ Opps, 88k+ WOs lifetime; the snapshot is deliberately narrowed and windowed to survive serverless timeouts/memory. New objects must be windowed too — `Transaction__c` especially is high-volume. Add only the fields each KPI needs, keep the parallel-promise pattern, and watch the payload size. Consider a separate, smaller cached fetch for the per-rep detail if the bundle grows too large.
- **Timezone.** Revenue "today/this-month" math is anchored to **America/New_York** (`startOfTodayInNY`, PPP HQ). Keep new period math consistent or month boundaries will drift a few hours nightly.

---

## 6. Implementation plan (suggested order)

1. **Fix revenue field + WO quoted figure** (§4.1) — unblocks correct sales/quota numbers.
2. **Fix the data window** (§4.2/4.3) — close-date-based pull or relabel.
3. **Constrain the rep universe** to `*Standard.Field` (§4.4) — fixes roster + team averages.
4. **Add fiscal-period helpers** to `derive.ts` (§5).
5. **Add Opp fields**: `LeadGroup__c`, `AppointmentDate__c`, `Cancelled_Appointment__c`, `Estimate_Sent__c`, `Date_Estimate_Sent__c` → real close rate + appointments/estimates (§4.5/4.6).
6. **Add WO fields**: `Gross_Margin_Percent__c`, `TotalNonBillablePurchases__c` → GM vs target + Materials % + Pricing/Labor-Day (labor-day fields already present).
7. **Add User fields**: `Gross_Margin_Goal_Percent__c`, `Quarterly_Draw__c`.
8. **New pulls** (windowed): `TotalQuota__c`/`SubQuota__c` (% to goal), `Transaction__c` (money flow + commissions), `Review__c`, `Case` (complaints).
9. **`deriveRepScorecard()`** assembling all of the above per rep/period.
10. **Render** new cards on `rep/[id]/page.tsx` (and optionally summary chips on the index `RepCard`), each gated on data presence.
11. **Validate** (Section 7), then polish for mobile (PPP's CEO reads this on a phone — hard requirement).

---

## 7. Validation checklist (do this before shipping)

PPP maintains native Salesforce reports (folder `FPRC_Reports`) that are the source of truth for these KPIs. For a sample rep and a known fiscal quarter, confirm the Command Center matches:

- [ ] **Revenue** matches `FPRC_KPI1_Revenue_By_Rep` (uses `QuotedSubtotalWithChangeOrder__c`, won, CloseDate).
- [ ] **Close rate** buckets match the report's self-gen vs marketing split (`Opportunity.LeadGroup__c`).
- [ ] **Gross Margin %** matches `Gross_Margin_Percent__c` (not your recomputed GP, and not `GrossProfitPercent__c`).
- [ ] **Revenue per Labor Day** restricted to `LaborDaysActual > 0`; excluded-WO count surfaced.
- [ ] **% to Goal** uses `TotalQuota__c` Owner/Active/CFY; reps without quota show "no quota set," not 0/∞.
- [ ] **Money Flow / Commissions** record-type + payee filters match (`Payment_In`/`Payment_Out`+Labor/`Purchase`; commissions by `Payee` name match, watch `<Name>-inactive`/`-portal`).
- [ ] **Reps shown** = active `*Standard.Field`; no admins/office users; team averages recomputed on that set.
- [ ] **Totals reconcile** between the rep index team strip and the company overview for the same period.
- [ ] Spot-check **one long-cycle deal** (created >12 mo ago, closed recently) to confirm the window fix (§4.2) actually includes it.

---

## 8. Reference

- KPI definitions, field gotchas, schema: the `salesforce/` folder in this repo.
- Command Center code touchpoints: `lib/salesforce/queries.ts` (snapshot), `lib/salesforce/derive.ts` (derivations), `app/dashboard/rep/[id]/page.tsx` (detail UI), `components/rep-index-view.tsx` (index UI), `lib/data-source.ts` (mock/live switch).
- Questions on a definition or a field that isn't behaving: ask PPP (Katie) — some fields (e.g. quota records) are sparsely populated by design, and compensation fields are intentionally restricted.
