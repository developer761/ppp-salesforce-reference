# Playbook — WO Cleanup (Bi-Weekly)

Recurring cleanup of three categories of WorkOrder data violations in PPP's Salesforce org. Runs bi-weekly via `/wo-cleanup` slash command.

---


## What this process is for

**The cleanup keeps work order records accurate — it is not a collections process.** Chasing customer
balances sits with the field team; this process only ensures the record matches what actually happened,
so jobs can close and the data can be trusted.

That distinction changes how the time-based checks read. A work order that has sat untouched past its
window is flagged **to capture a change**, not to chase money: a job that stalls with nothing logged has
usually been rescheduled, re-scoped or canceled without anyone updating the record. The ask is
"what happened?", so the record can be corrected.

Dollar figures are used to size and rank the work, never as a recovery target.

### Measurement traps

- **`EndDate` is an estimated date**, not when work actually ended, so don't use it as the basis for
  duration or timing *metrics*. (It remains valid inside the cleanup rules themselves — this is a
  reporting caveat, not a rule caveat.) For any timing measure use the status change into a Complete
  status → the change to Closed; both are real recorded events.
- **`BalanceOwed__c` is structurally ~$0 on any Closed work order** — closing settles it. A rule operating
  on closed records will always look like near-zero exposure no matter how incomplete the records are, so
  read the record count rather than the dollars. There is no single dollar metric spanning open and closed
  rules: balance for open, quoted value for closed.
- **Work order status history has a retention horizon** (roughly 18 months). There is no close-date field,
  so for anything closed before that horizon the close date is unrecoverable. Cohort analysis keyed on
  created date avoids the limit and is less distorted by backlog clearing.

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
- `CloseDate` is set using the **three-tier fallback** below — not the WO end date or last payment date

#### Setting `CloseDate` on a corrected opp — three-tier fallback

`CloseDate` means **when the deal was booked**, not when the job was delivered or paid — realized sales
anchor on it (see `BUSINESS_RULES.md`). An opp being promoted into Closed Won by these rules often has no
legitimate close date to restore, so supply one in this order:

1. **Restore the pre-corruption value from `OpportunityFieldHistory`** (`Field = 'CloseDate'`).
   Authoritative whenever the opp did legitimately close once. See the recovery query below.
2. **No history → use the real WO's `CreatedDate`.** The WO-creation chain fires on Closed Won + a synced
   quote, so WO creation is a booking-time proxy for the sale.
3. **Never use WO end date or last payment date.** Those are delivery/collection dates. Measured against
   production, they fall in a *different calendar month* than the WO's created date roughly 58% and 66% of
   the time respectively — which posts the sale 1–8 months after it happened. By contrast `CloseDate` and
   WO `CreatedDate` already agree on ~99% of opps under normal operation, so a month-level mismatch is a
   reliable corruption signal rather than noise.

⚠️ **`CloseDate` has two independent setters** — an Apex before-update handler and a record-before-save
flow, both firing on the transition into Closed Won. Any correction must survive both.

**Exclusions (Rule 1):** estimate appointment WOs, opps owned by specific excluded owners, opps where `Corporate_Name__c` matches a configured corporate exclusion (see script config).

### Rule 2: Opp Closed Won + all real WOs Canceled → update Opp stage to Opportunity Lost
**Logic:** If all real WOs are canceled, the job did not proceed and the Opp stage should reflect that.

⚠️ **Attendance is deliberately NOT a gate on this rule.** Logged attendance or payouts on a *canceled*
WO is normal, not a data error — crew days can be recorded before a job is called off, and those balances
are not collected. An opp whose real WOs are all canceled moves to Lost **even when attendance exists**.
Do not "fix" this by adding an attendance check.

⚠️ **Canceled only — this rule must not extend to Pending.** A real WO sitting in Pending is a *user
error* (Pending is the creation default that real WOs are advanced off of), not a dead deal. Treating
all-Pending the same as all-Canceled would move live deals to Lost. Pending real WOs are caught by their
own check instead.

- **Auto-update stage to Opportunity Lost** if no related `Transaction__c` records exist on any WO
- **Flag** if `Transaction__c` records are present — validate record dates vs current FY before updating; pre-FY records are generally safe to proceed
- **Skip** if opp has any other active (non-Canceled) real WO — work is still in progress → Closed Won is correct

**Exclusions (Rule 2):** estimate appointment WOs, opps owned by specific excluded owners, opps where `Corporate_Name__c` matches a configured corporate exclusion (see script config).

### Rule 3: Opp still in an early stage + real WO already active → flag for Closed Won

The mirror image of Rule 1 from the pre-close side. An opp still in **Opportunity Assigned** or **Estimate Sent** while a real (non-appointment) WO is already in an active status (Coordination, Scheduling, Work In Progress, On Hold, Complete Balance Owed, Complete Paid in Full, Closed) means work started but the opp never advanced. The WO is ground truth → the opp should be Closed Won.

- **Flag all matches for manual review** — do not auto-change stage. Fix = the same 3-step quote sequence + CloseDate correction as Rule 1.
- Same exclusions as Rules 1/2.

### $0-amount Closed Won data check (financial-field clobber recurrence)

A recurring **read-only** detector for a known failure mode: a WorkOrder after-save flow that writes the WO's financials up to the Opp had no work-type entry filter, so an estimate-appointment WO (value $0) saving after the real WO would **zero the Opp's amount fields** (last-writer-wins). Fixed forward by adding an entry filter that excludes appointment work types, but a recurrence detector belongs in the recurring run.

- **Signature (precise, not the raw condition):** Opp `StageName = 'Closed Won'` AND `TotalAmount__c = 0` AND has a real active WO with `Quoted_Subtotal_with_Change_Order__c > 0` — i.e. the amount was clobbered and *should* be non-zero. Detecting on the raw "$0 Closed Won" condition alone floods with legitimately-$0 opps; the real-valued-WO join isolates the actual defect.
- **Flag-only.** Fix = a **no-op re-save of the real WO** (`Status` → its current value), which re-fires the now-filtered flow and repopulates the four Opp financial fields. Idempotent (the flow writes only when a field differs). Requires the edit-closed bypass permission set since most real WOs are Closed.
- Excludes self-managed owners, the corporate exclusion, and internal test opps.

These two flag-only checks plus Rules 1/2 make the recurring run consume every condition on the source "bad Opp/WO data" review report (its two buckets: possible-no-WO → the field-triage no-WO report; status/data mismatch → Rules 1/2 + these two checks).

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
`Opportunity.FY_Assigned__c` (`Text(10)`, e.g. "2026") represents the PPP fiscal year the opp is assigned to, using the FY **starting** year. No flow updates it when CloseDate changes — run a separate correction pass if CloseDates are bulk-corrected.

⚠️ **It is not a formula and is not derived from `CloseDate`.** An earlier version of this playbook
documented it as `month >= 2 → FY = CloseDate.year; month == 1 → FY = CloseDate.year - 1`. That describes
the *intent*, not the implementation. In practice the field is written by the same record-before-save flow
that stamps `CloseDate` on the transition into Closed Won, and the value it writes is a **hardcoded text
template** that must be edited manually each fiscal year. Consequences:

- Correcting a `CloseDate` across a fiscal-year boundary leaves `FY_Assigned__c` stamped with the value
  that was hardcoded at the time of the stage change — it will not follow the corrected date.
- If the template is not updated at the FY rollover, opps in the new FY are silently stamped with the
  **prior** year. A wrong value is worse than a blank one: blanks are visibly missing, wrong values aren't.
- `FY_Status__c` is a formula off `FY_Assigned__c`, so a blank or stale `FY_Assigned__c` propagates into
  any report filtering or grouping on FY status.

Verify the current template value before relying on the field at the start of any fiscal year.

PPP FY starts Feb 1 (FY26 = Feb 1, 2026 – Jan 31, 2027).

---

## Section 4 — Move WOs to Closed

Real (non-estimate) WOs where the job is fully complete should move to `Status = 'Closed'`. Because the `WorkOrder_DisallowEditWhenClosed` flow blocks edits once a WO is Closed, this step is **two-step and never auto-closes**: export candidates → human validates → close only the approved Ids.

### Auto-close criteria (all must be true)
- `Status` NOT IN (Coordination, Scheduling, On Hold, Pending, Canceled, Closed)
- `StartDate` and `EndDate` both set
- **Attendance complete** — `LaborDaysActual__c` reaches the day estimate (see "Attendance completeness rule" below); merely `!= 0` is not enough. A partially-logged WO (e.g. 2 of 12 days) is **flagged**, not closed.
- `Contractor__c` != null (crew assigned)
- `RequestReview__c` != null
- `BalanceOwed__c` within ±$0.01 (`>= -0.01 AND <= 0.01`) — only the unavoidable tax-rounding penny left after balance adjustments; the target is `$0`. Larger balances fall through to the small-balance adjustment pass first, then close on the next run. (Was `= 0`, briefly ±$0.05.)
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
- `RequestReview__c != null` (estimator-finalized signal — see below)
- WorkType does not contain "Appointment"

**Status is not gated on a specific done-status.** For these corps the label is unreliable (jobs sit on "Work In Progress" long after they settle), so completeness is established by the estimator-finalized signal + dates + `$0` balance + crew payout instead. `Canceled`/`Closed` stay excluded — never close those.

**`RequestReview__c` requirement.** This field is set by the estimator (it drives whether account management solicits a customer review); a non-null value means the estimator has finalized the WO. The scheduled status-automation batch (`WorkOrderStatusAutomation`) won't advance a WO to a Complete status while it's null, so this pass must not either — never close a WO the estimator hasn't finalized.

### Then classify (mirrors Section 4)
- `TotalPayoutsForLabor__c` > 0 → **close-eligible** (crew was paid = work happened)
- `TotalPayoutsForLabor__c` = 0 AND `EndDate` older than 60 days → **flag** for review, never auto-close (payout would have been recorded by now — either unrecorded or the job wasn't actually done)
- `TotalPayoutsForLabor__c` = 0 AND `EndDate` within 60 days → silent skip (too recent — payout may simply be unrecorded)

### Preferred end state (retires 4b)
Fold the exemption into the Section 4 candidate logic: drop `LaborDaysActual__c != 0` from the hard filter and enforce it in classification instead — require it **unless** the owner is attendance-exempt, in which case use `TotalPayoutsForLabor__c` as the work-happened signal per the rules above. Validate with a read-only pass before adopting so nothing over-closes.

---

## Attendance completeness rule

Attendance is judged against the **day estimate**, not merely non-zero. A WO with a little attendance logged (e.g. 2 of 12 days) is *not* complete — closing it buries an under-logged job.

```
denom = LaborDaysProjected__c            if projected is credible (QuotedSubtotal__c / projected <= $1,500 per projected day)
      = QuotedSubtotal__c / $572          otherwise
attendance complete  ⇔  LaborDaysActual__c >= 0.80 * denom      (0 logged is always incomplete)
```

**Why the fallback:** `LaborDaysProjected__c` is a reliable denominator most of the time, but on a small share of WOs it's left as a 1–2-day placeholder on large-dollar jobs (a high-value job "projected" at 1 day). When `subtotal / projected` exceeds the credibility cap, projected is not trusted and a subtotal-implied day estimate is used instead. The constants are calibrated from the historical median of subtotal-per-actual-labor-day on cleanly-logged, closed WOs; recalibrate if job mix shifts.

**Not a hard no-close for the field list** — below standard becomes a quantified email line ("attendance is X% below your projected labor days — logged A of D"). But for the **auto-close** pass (Section 4) it is a hard gate: partial-attendance WOs are flagged, never closed. The same rule governs both so triage and close stay consistent.

---

## Section 5 — Field Triage & Cleanup Emails

The cleanup is the **whole ticket**, i.e. every linked report — not only the categories the automated phases fix. Records left on a linked report that need a human/field fix are emailed to the responsible field user (the opportunity owner), one email per person covering all their WOs.

### Read the report, don't rebuild its filter
Each linked report is a curated population. Read its rows via the **Analytics API** (`/services/data/vXX.0/analytics/reports/{id}?includeDetails=true`), not a hand-reconstructed SOQL filter — reconstructed filters drift from the report (owner exclusions, date/status nuances, folder scoping are easy to miss). Resolve records off `WorkOrderNumber`; the Analytics ID column's `label` is truncated. Use live SOQL only to *enrich* the report's rows with fields it doesn't carry, never to redefine the population.

### Classify every record
- **FIELD** — needs a field fix → goes in the owner's email, with the specific missing signals (Start/End dates, attendance shortfall, crew, request-review, undeposited $, wrong status).
- **SLIDE** — auto-handled by another phase, an acceptable final state, too recent to act on, a self-managed owner, or an internal test WO.
- **REVIEW** — route to management first (e.g. overpayment / negative-balance and owner-mismatch reports) before any field contact, rather than emailing the field directly.

### Cadence & follow-up
Most reports need **no ongoing list** — each run re-reads them fresh. The one persistent list is a follow-up tracker: a record that reappears across runs increments a follow-up count, and a 3rd follow-up escalates to the manager. Emails are generated as **drafts** for human review — never auto-sent. A human validates the field list before any draft goes out.

**The hand-off is the sheet, not the email.** Run the detection sweep (read-only) → publish the review sheet → **stop there.** Drafting or sending field emails requires an explicit go-ahead **each cycle**, not a standing one. A record landing in the FIELD bucket is a *candidate* for outreach, not an instruction to send. A leftover drafts file in the working folder is a source artifact from a prior cycle — never treat its presence as evidence that emails are outstanding.

**Track dispositions on the sheet, and re-read it immediately before acting.** The working population is the review sheet filtered to rows with an empty disposition column — not a fresh SOQL pull. The reviewer edits that column continuously while working, so a count captured minutes earlier is already stale.

---

## Enforce at the gate, not after the fact

A recurring failure mode: a rule that fires on **already-closed** records asks someone to reconstruct
information from months ago, so every row gets dismissed. The same rule applied while the record is still
**open** is actionable, because the person who can fix it still has the leverage to.

Worked example — attendance. A rule flagged closed work orders whose crew days were never logged, keyed on
*when the record was closed*. A job worked in May but closed in August therefore owed attendance months
after the fact; 55 records surfaced and 53 were dismissed as not-worth-doing. The team lead's own policy
was **"don't close it until attendance is entered"** — a close gate, i.e. leverage that only exists before
closing. Correct resolution: **remove the check from closed records entirely, keep it on open ones, and
enforce it with a validation rule at close.** Detection moved upstream, the dismissal rate went to zero,
and the backlog of unfixable history stopped being generated.

**Generalise:** before adding a rule that inspects finished records, ask what action it implies and whether
anyone can still take it. If the answer is "reconstruct it from memory," the rule belongs at the gate.

## Scope exclusions are a design surface, not a footnote

Cleanup rules accumulate populations that must be treated differently. Make each an explicit, documented
decision rather than an inherited filter:

- **Onboarded/migrated operators** — historical records loaded in after the fact will not satisfy
  date-relationship rules (close date vs record created date), because the dates describe the migration,
  not the work. Exclude them from date-based rules specifically, not from the cleanup wholesale.
- **Self-managed divisions** — a division that runs its own cleanup still benefits from *data-integrity*
  findings surfaced to its manager, who may not see them in their own reports. Split by rule type:
  integrity findings route to them; close-readiness prompts ("this record needs X before it can close") do
  not. Wholesale exclusion hides real defects; wholesale inclusion is nagging.
- **Per-field policy exemptions** — where a requirement genuinely doesn't apply to a group (e.g. a review
  request some operators never solicit), key the exemption on **profile**, not a hardcoded user list, so
  new users are covered automatically. ⚠️ Never key it on a person's *name*: near-identical names across
  different profiles are common, and a name match will silently exempt the wrong user.

## Rules that fire on finished records need a staleness ceiling

The companion to "enforce at the gate." Where a gate isn't available, a rule that inspects completed
records must **age out**, or it manufactures an unfixable backlog in perpetuity — every cycle it
re-presents the same rows, and every cycle they are dismissed.

Worked example — missing crew payouts and missing review requests on closed work orders. Both tests fired
at any age, so they surfaced hundreds of rows about jobs finished a year or more earlier. The operating
reality is that **crews chase their own payment**: a job whose work ended two months ago with no payout
recorded is settled in practice, not an open gap. Resolution: **stop flagging either once the record is
more than 60 days past its end date.** Fields that describe what happened — start, end, crew, undeposited
payments — are *not* aged out; those stay wrong forever and remain flagged at any age.

**The distinction that matters:** age out the tests whose *answer decays* (was this paid? was a review
requested?). Never age out the tests whose answer is permanent (who did this work?).

⚠️ **Same threshold, opposite polarity — do not "harmonize" these two rules.** Both use 60 days from
`EndDate`, and they mean inverted things because they act on different populations:

| Population | No payout + end date **older** than 60d | No payout + end date **within** 60d |
|---|---|---|
| **Open** WO, auto-close candidate (Section 4b) | **flag** — never auto-close | silent skip — too recent to judge |
| **Already-closed** WO, integrity sweep | **silent** — settled in practice | **flag** — recent enough to act on |

Before closing, a missing payout is a reason to withhold the close. After closing, it is only actionable
while the job is fresh. Anyone reconciling these into one rule will break one of them.

## Choose a date anchor by what it cannot see

When a rule keys on a date and several fields are candidates, the objection "any of these can be edited
long after the work happened" is usually true of all of them and does not decide anything. **Settle it by
measuring what each candidate is structurally blind to** — run the rule under each anchor and compare.

An inaccurate anchor produces wrong rows you can see and dismiss. A *blind* anchor produces nothing, and
looks exactly like clean data. That asymmetry is why this has to be measured rather than argued.

Two decisions made this way:

- **Close-date-vs-record-created mismatch.** Anchoring the review window on the opportunity's *close*
  date caught real cases; anchoring on its *created* date caught **zero** — an opportunity created and
  won in the same month has its work order created that month too, so it can never mismatch. The created
  date anchor also permanently hides **re-won** opportunities, which is the population the rule actually
  detects, since the close-date automation restamps the date on every re-win.
- **The staleness ceiling above.** The end date beat the status-change-to-closed event: it is populated
  on 100% of the closed book, needs no field-history query, and cannot be restarted by reopening and
  re-closing a record. Field history also only reaches back a limited retention window, so it could not
  gate the older book at all.

**Always state the accepted blind spot as a number**, in the code and the process doc. For the ceiling
above: 14.5% of work orders are already more than 60 days past their end date at the moment they close,
so the test can never fire on them — accepted, because by the operating rule those jobs are settled.

⚠️ **Don't over-apply a field's caveat.** An end date documented as "estimated — never use for timing
metrics" is still fine for a 60-day staleness window: an estimate off by a week doesn't change that
verdict. Match the precision of the field to the precision the test needs, rather than banning it outright.

## Pin the historical backlog explicitly, don't let a rule quietly carry it

A detection rule written against a live process will, on first run, surface the entire back catalogue.
Decide deliberately whether that history is in scope — and if it isn't, **move the rule's floor forward
rather than dismissing rows by hand each cycle.**

Where correcting history would restate a closed accounting period, fixing it is the *wrong* action even
when the rule is right: the recorded value is a faithful record of what the system did at the time.
Set the floor at the start of the open period and keep the rule running forward, so a later automation
touching an old record still resurfaces it — a floor on the *close* date preserves that visibility,
whereas a floor on the record's creation date would blind the rule to old records being re-touched now.
