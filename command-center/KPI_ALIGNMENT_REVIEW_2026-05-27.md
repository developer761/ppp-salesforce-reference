# Rep Profiles ↔ FPRC Report-Card Alignment Review (2026-05-27)

**Reviewed:** `developer761/PPP-Command-Center` @ `e66ec60` (origin/main, 2026-05-27)
**Against:** PPP's live Field Performance Report Card (FPRC) definitions after the **2026-05-21 report-mirror overhaul** (see `salesforce/REP_PERFORMANCE_KPIS.md`, `salesforce/BUSINESS_RULES.md`)
**Audience:** Command Center engineering. Companion to `REP_PROFILES_INTEGRATION_GUIDE.md` — this is a point-in-time audit of the current code with ready-to-apply diffs.

> Curation note: code logic, file:line, and Salesforce field API names only. No compensation figures, no individual performance data, no names/IDs.

---

## TL;DR

The **`rep-scorecard.ts` surface is in good shape** — it correctly uses `QuotedSubtotalWithChangeOrder__c` for sales, `Gross_Margin_Percent__c` (not the NetValue-based `GrossProfitPercent__c`) for GM, real `AppointmentDate__c`/`Estimate_Sent__c` fields for activity, Account-owner attribution for reviews, and Status-string (not `IsClosed`) filtering for completed jobs. 5 of the 6 prior integration-guide bugs are closed.

**Most remaining gaps are because the shared contract drifted, not because the code is wrong.** The app faithfully implemented `ppp-salesforce-reference` as it stood, but those docs predated the 2026-05-21 FPRC overhaul. The shared docs have now been updated (self-gen bucket, commissions, PFQ reporting note — commit `77504e0`); the code diffs below bring the app in line.

**Nothing here removes Command Center-only metrics** (Conversion Rate, Avg Ticket, Speed-to-Estimate, leaderboard rank, trend charts) — those have no FPRC analog and are fine.

### Verified NON-issue: GM% scale ✅
Checked against production: `WorkOrder.Gross_Margin_Percent__c` returns values like `18.8` / `28.1` / `30.9`, matching `(GrossProfit ÷ Quoted) × 100` — i.e. stored **as a percent (42.5), not a decimal (0.425)**. The app treats it as already-a-percent (`queries.ts:1281-1284`) and `User.Gross_Margin_Goal_Percent__c` is percent-scaled too, so `avgGmPct.toFixed(1)%` and `vsTarget = avgGmPct − gmTarget` are **correct**. No change needed.

---

## Window convention — RESOLVED: single-anchor is canonical ✅

This was an open question (the FPRC cards apply a dual predicate — Opp *Created in CFY* AND {close/work date} *in PFQ*). **Resolved by PPP 2026-05-27: the single date-in-period anchor is canonical** for the Command Center and the shared KB. The scorecard already does this correctly — **no window change is required**; just apply Fix 1 (PFQ vs in-progress quarter). The report cards retain an extra "Created-in-CFY" split internally only to drive a per-rep *carry-over reference line* for two specific reps — that is a card-only presentation device, **not** a rule the app needs to mirror.

---

## Code fixes (ranked) — ready-to-apply diffs

### Fix 1 — Anchor the scorecard on PFQ, not the in-progress quarter ⬆ High · 1-liner
The scorecard uses `currentFiscalQuarter()` = the quarter containing *today*, which is **in progress**, so every period KPI shows a partial number that won't reconcile against the FPRC card (which reports the just-completed quarter). `priorFiscalQuarter()` already exists (`lib/fiscal-year.ts:103`).

**`app/dashboard/rep/[id]/page.tsx:19`** — add the import:
```diff
-import { currentFY, currentFiscalQuarter, fyLabel } from "@/lib/fiscal-year";
+import { currentFY, currentFiscalQuarter, priorFiscalQuarter, fyLabel } from "@/lib/fiscal-year";
```
**`app/dashboard/rep/[id]/page.tsx:121-128`**:
```diff
-  // KPI scorecard anchored on the current fiscal quarter — PPP's reports
-  // are fiscal-period, so this matches what staff already read in FPRC_*.
-  // Skipped on mock data (no quotas/transactions/reviews to derive from).
-  const fyNow = currentFY();
-  const fqNow = currentFiscalQuarter();
-  const scorecard: RepScorecard | null = bundle.snapshot
-    ? deriveRepScorecard(bundle.snapshot, rep.id, { fy: fyNow, q: fqNow })
-    : null;
+  // KPI scorecard anchored on the PRIOR (just-completed) fiscal quarter — the
+  // FPRC report cards report PFQ, not the in-progress quarter, so a mid-quarter
+  // partial would NOT reconcile against FPRC_*. (A period picker defaulting to
+  // PFQ would be the natural enhancement.)
+  // Skipped on mock data (no quotas/transactions/reviews to derive from).
+  const { fy: scFy, q: scQ } = priorFiscalQuarter(currentFY(), currentFiscalQuarter());
+  const scorecard: RepScorecard | null = bundle.snapshot
+    ? deriveRepScorecard(bundle.snapshot, rep.id, { fy: scFy, q: scQ })
+    : null;
```
> Also re-label any "current quarter" UI text on the card via `fyLabel(scFy, scQ)`.

### Fix 2 — Self-Gen lead bucket: 4 values, not 1 ⬆ High · fixes KPI 3 + 3b
Matches the updated `BUSINESS_RULES.md` / `REP_PERFORMANCE_KPIS.md`.
**`lib/salesforce/rep-scorecard.ts:175-177`**:
```diff
-function isSelfGen(o: SnapshotOpp): boolean {
-  return o.leadGroup === "Self-Generated";
-}
+// FPRC self-gen bucket (report-mirror overhaul 2026-05-21): four LeadGroup
+// values count as self-generated; everything else (incl. null / Partnership)
+// is marketing, so self-gen + marketing always reconciles to the total.
+const SELF_GEN_LEAD_GROUPS = new Set([
+  "Self-Generated", "Trade Show", "Repeat", "Referral",
+]);
+function isSelfGen(o: SnapshotOpp): boolean {
+  return SELF_GEN_LEAD_GROUPS.has(o.leadGroup ?? "");
+}
```

### Fix 3 — Complaints: count only the 2 true complaint Case types ⬆ Med · in-memory
The snapshot pulls all 6 customer-facing Case types; the scorecard counts all of them. FPRC counts only `Dissatisfied Customer` + `Service Call`. `c.type` is already on `SnapshotCase`, so filter in memory (keep the broad SOQL).

**`lib/salesforce/rep-scorecard.ts:484-490`**:
```diff
-  // Complaints — by Opportunity__r.OwnerId (KPI 7 spec).
-  let complaints = 0;
-  for (const c of snapshot.cases) {
-    if (c.opportunityOwnerId !== repId) continue;
-    if (!inRange(c.createdDate, start, end)) continue;
-    complaints += 1;
-  }
+  // Complaints — by Opportunity__r.OwnerId (KPI 7 spec). FPRC counts only the
+  // two true "complaint" Case types; the snapshot pulls all 6 customer-facing
+  // types, so narrow here.
+  const COMPLAINT_TYPES = new Set(["Dissatisfied Customer", "Service Call"]);
+  let complaints = 0;
+  for (const c of snapshot.cases) {
+    if (c.opportunityOwnerId !== repId) continue;
+    if (!COMPLAINT_TYPES.has(c.type ?? "")) continue;
+    if (!inRange(c.createdDate, start, end)) continue;
+    complaints += 1;
+  }
```

### Fix 4 — Commissions (KPI 9): filters + CFY window + draw scaling ⬆ High
Gaps vs FPRC: (a) no `PayeeType='Sales'` filter; (b) no `Description LIKE '%Draw%'` (and `Description__c` isn't selected); (c) payee match misses the `LC <rep>` labor-company alias; (d) earned is windowed to the quarter but FPRC windows on the **full CFY** (cumulative); (e) draw is prorated by raw days/91 but FPRC draw = `Quarterly_Draw × fiscal-quarter-index` (CFY-to-date).

**(i) Add `Description__c` to the Transaction pull — `lib/salesforce/queries.ts:1405`:**
```diff
-        const fields = "Id, RecordType.DeveloperName, Amount__c, Date__c, PayeeType__c, Payee__r.Name, WorkOrder__c, WorkOrder__r.OwnerId, Opportunity__c";
+        const fields = "Id, RecordType.DeveloperName, Amount__c, Date__c, PayeeType__c, Description__c, Payee__r.Name, WorkOrder__c, WorkOrder__r.OwnerId, Opportunity__c";
```
**(ii) Carry it on the type — `SnapshotTransaction` (~line 351):**
```diff
   payeeType: string | null;   // "Labor_Company" / "Reimbursement" / etc.
+  description: string | null; // Description__c — used to match draw payouts
   payeeName: string | null;   // resolved via Payee__r.Name
```
**(iii) Map it where the record is built (~line 1425, beside `payeeType:`):**
```diff
             payeeType: (r.PayeeType__c as string | null) ?? null,
+            description: (r.Description__c as string | null) ?? null,
```
**(iv) Rewrite the earned loop + draw — `lib/salesforce/rep-scorecard.ts:504-522`** (`fiscalRangeFor` is already imported):
```diff
-  /* ─ KPI 9 ─ Commissions ─ */
-  // Earned = Transaction Payment_Out where WO is set AND Payee.Name matches
-  // rep name. ... do a prefix match on the canonical name.
-  let earned = 0;
-  const repNameLower = rep.name.toLowerCase();
-  for (const t of snapshot.transactions) {
-    if (t.recordType !== "Payment_Out") continue;
-    if (!t.workOrderId) continue;
-    if (!t.payeeName) continue;
-    if (!inRange(t.date, start, end)) continue;
-    const payee = t.payeeName.toLowerCase();
-    if (payee === repNameLower || payee.startsWith(`${repNameLower}-`)) {
-      earned += t.amount;
-    }
-  }
-  const drawReceived = rep.quarterlyDraw !== null ? scaleDraw(rep.quarterlyDraw, start, end) : null;
-  const difference = drawReceived !== null ? earned - drawReceived : null;
+  /* ─ KPI 9 ─ Commissions ─ (CFY-to-date, NOT the single quarter) ─ */
+  // Earned = Payment_Out paid to the rep against their draw: PayeeType='Sales'
+  // AND Description contains "Draw", Date in the current FY, attributed by Payee
+  // name = "<rep>" or "LC <rep>" (labor-company alias). NOT scoped to the rep's
+  // own WOs. Watch for "<name>-inactive" / "-portal" shadow Users.
+  const cfy = fiscalRangeFor(period.fy);           // full current fiscal year
+  let earned = 0;
+  const repNameLower = rep.name.toLowerCase();
+  for (const t of snapshot.transactions) {
+    if (t.recordType !== "Payment_Out") continue;
+    if (!t.workOrderId) continue;
+    if (t.payeeType !== "Sales") continue;
+    if (!(t.description ?? "").toLowerCase().includes("draw")) continue;
+    if (!t.payeeName) continue;
+    if (!inRange(t.date, cfy.start, cfy.end)) continue;
+    const payee = t.payeeName.toLowerCase();
+    if (
+      payee === repNameLower ||
+      payee.startsWith(`${repNameLower}-`) ||   // shadow Users
+      payee === `lc ${repNameLower}`            // labor-company payee alias
+    ) {
+      earned += t.amount;
+    }
+  }
+  // Draw Received = quarterly draw × fiscal-quarter index, CFY-to-date (Q1→×1 … Q4→×4).
+  const drawReceived = rep.quarterlyDraw !== null ? rep.quarterlyDraw * period.q : null;
+  const difference = drawReceived !== null ? earned - drawReceived : null;
```
> `scaleDraw` (`rep-scorecard.ts:188-192`) becomes unused — delete it.
> ⚠️ The earned set is **CFY-cumulative while the rest of the scorecard is the single PFQ** — intentional and matches FPRC (draw/commissions reconcile year-to-date). Label the card "CFY to date."

### Fix 5 — Add Change Orders $ (KPI 7) ⬆ Med · adds a field end-to-end
`WorkOrder.TotalChangeOrder__c` is never selected, so this KPI 7 metric is missing. Three touch points:
1. **`lib/salesforce/queries.ts`** — add `TotalChangeOrder__c` to the WorkOrder SELECT (~lines 1152-1162) and to `SnapshotWorkOrder` (~line 181), mapping `totalChangeOrder: Number(w.TotalChangeOrder__c ?? 0)`.
2. **`lib/salesforce/rep-scorecard.ts`** — in the completed-WO loop for KPI 7 (~line 456-466), add `changeOrders += w.totalChangeOrder ?? 0`, surface on the return (~line 525+).
3. **`app/dashboard/rep/[id]/page.tsx`** — render in the Production Quality card.
> `TotalChangeOrder__c` already nets to Approved/Approved-Auto only (it's a rollup) — no extra status filter needed.

### Fix 6 — Tighten the completed-status set for GM & Pricing (KPI 2 / 5) ⬇ Low-Med
`COMPLETED_STATUSES` (`rep-scorecard.ts:170`) includes `"complete balance owed"`. FPRC KPI 2 (GM) and KPI 5 (Pricing) use only `Closed` + `Complete Paid in Full` (Balance-Owed jobs report separately). KPI 7 already hardcodes the strict pair (≈ 462-463). Define a strict set and use it in the GM (≈ 298-314) and Pricing (≈ 345-375) loops:
```ts
const GM_PRICING_STATUSES = new Set(["closed", "complete paid in full"]);
// …in the GM/Pricing WO loops, replace isCompleted(w) with:
//   GM_PRICING_STATUSES.has((w.status ?? "").toLowerCase())
```
Small effect (Balance-Owed is the long tail). Leave the broad `COMPLETED_STATUSES` for the Attendance gauge (KPI 4b).

---

## Larger / architectural items (recommend, no drop-in diff)

### A. Snapshot window is still `CreatedDate = LAST_N_DAYS:365` — Med-High
`queries.ts:640` (`RECENCY_WINDOW_DAYS = 365`), applied to Opps (`:645`) and WOs (`:1202`). The scorecard is computed over this snapshot, so a deal **created >365 days ago but closed in the reported quarter is absent** (undercounts KPI 1/2/3b/7/8), and KPI 6 (Pipeline, "all-time open") only sees opps created in the last year. Mitigated by the short cycle but real for long-cycle work. Recommendation: pull the revenue/WO objects on a `CloseDate`/`EndDate` window (or widen + filter in memory) for the scorecard path. This is known item #2 in `AGENTS.md`.

### B. Rep universe / team-average denominator — Med
KPI 1 rank gates on `isFieldStandard` (good), but `snapshot.reps` is the broad `isLikelyRep` set, and the rep-page team-average deltas (`rep/[id]/page.tsx:173-202`) average over all likely reps, not the `*Standard.Field` set. Gate those team-average inputs on `isFieldStandard` so "vs team" deltas match the report cards' peer set. (A permset-driven roster, e.g. `Sales_Team_Member`, is the durable answer.)

### C. No Manager-Overview analog; dashboard uses mean-of-means — Med (only if a team rollup is wanted)
The closest surface, `components/dashboard-view.tsx:124-149`, computes team close rate / avg ticket as **simple mean-of-means**, which the FPRC aggregation rule forbids — ratios must be **weighted** (Σnumerators ÷ Σdenominators); only counts/currency are summed. The rep-page team deltas *are* correctly weighted, so the pattern exists. If a real Manager Overview is built, aggregate `deriveRepScorecard` with weighted means for every ratio (GM%, Materials %, close rate, stale %) over the `*Standard.Field`/`Sales_Team_Member` set.

---

## Status of the 6 prior integration-guide bugs at `e66ec60`

1. Revenue field (Quoted vs Net) — ✅ fixed.
2. Snapshot 365-day CreatedDate window — ⚠ still present (item A; known tradeoff).
3. "lifetime" label — ✅ fixed (honest "Last 12 months").
4. Rep universe too broad — ⚠ partially fixed (rank gated, but team-average set still broad — item B).
5. Close rate / fabricated appts — ✅ mostly fixed; **residual: self-gen bucket** (Fix 2).
6. Real appointments/estimates — ✅ fixed.

---

## Appendix — per-KPI alignment at `e66ec60`

| KPI | Verdict | Fix |
|---|---|---|
| 1 Revenue | field ✅ / period ⚠ | Fix 1 (PFQ) |
| 2 Gross Margin | field ✅ / status-set ⚠ | Fix 6, Fix 1 |
| GM% scale | ✅ correct (verified) | none |
| 3 Close Rate | bucket ❌ | **Fix 2** |
| 3b Sales Mix | bucket ❌ | **Fix 2** |
| 5 Pricing | ✅ | Fix 6, Fix 1 |
| Appointments | ✅ | Fix 1 |
| Pipeline | logic ✅ / universe ⚠ | §A |
| 7 Jobs Completed | ✅ | Fix 1 |
| 7 Reviews | ✅ (Account owner) | none |
| 7 Complaints | type filter ❌ | **Fix 3** |
| 7 Change Orders $ | missing ❌ | **Fix 5** |
| 8 Money Flow | ✅ | Fix 1 |
| 9 Commissions | filters/window/draw ❌ | **Fix 4** |

**Validate after applying:** `GET /api/admin/rep-validation?repId=<sf-user-id>` for a known active field rep and reconcile against that rep's FPRC FY26 Q1 PDF card.
