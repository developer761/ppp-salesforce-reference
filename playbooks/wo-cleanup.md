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
- **No transaction activity for more than 7 days** — see "Anchor the quiet-period gate on all activity" below
- `TotalPayoutsForLabor__c` != 0
- **Labor payouts clear the payout floor** — payouts must be **>= 20% of the quoted value net of materials**, not merely non-zero. See "Payout floor" below. Below the floor the WO is **flagged, never closed**.
- **Excludes:** opps owned by specific excluded owners, opps where `Corporate_Name__c` matches a configured corporate exclusion (same exclusions as Section 3)

### Flag for manual review (meets all completion signals except one — do not close)
- No transaction of any kind on the record → should not normally occur on a complete, settled job
- **Owner is configured surface-only** — some owners keep every rule but are never auto-written: a would-be close becomes a flag so it is raised with them instead. Apply this test *last*, so it converts an otherwise-eligible close into a flag rather than pulling records that the silent-skip rules would have held onto the sheet every cycle.
- `TotalPayoutsForLabor__c` = 0 AND `EndDate` older than 60 days → labor would have requested payment by then

### Silent skip (not closed, not flagged — reconsider next run)
- `TotalPayoutsForLabor__c` = 0 AND `EndDate` within 60 days → payout may simply be unrecorded
- Transaction activity within the last 7 days → still settling, too recent

### Anchor the quiet-period gate on all activity, not just customer payments

The gate that holds a work order open until it has "gone quiet" must key on **every kind of
transaction that means someone is still working the record** — materials purchases, customer payments
in, and crew payouts — not on the last-customer-payment field alone.

Measured over ~3,200 work orders closed in a year, activity landing *after* a work order became
close-eligible broke down as **purchases 635, crew payouts 206, customer payments 9**. A gate anchored
on the payment field was blind to 841 of those 850 events and watched the 9 that essentially never
happen. Switching the anchor cut closes-landing-on-top-of-later-activity from **9.2% to 7.0%** — about
70 fewer premature closes a year — at no cost in window length.

⚠️ **Two traps when implementing this:**

- **Identify transaction kinds by record type, not by payee type.** A null payee type covers *both*
  purchases and customer payments in — they are different record types. Splitting on payee type alone
  silently merges two populations.
- **Exclude sales commission from the gate.** Commission payouts are ~99% *created after* the close
  (median two weeks after), because closing is what triggers them. Including them in a
  "quiet period" test means any reopened work order can never close again — the act of closing
  generates the transaction that blocks the next close.

**State the blind spot as a number:** purchases carry an entry-lag tail — roughly 14% are entered more
than a week after the date they carry — so the gate cannot see those coming at any window length.
Payouts and payments-in are entered same-day. Accepted, and documented rather than discovered later.

**This gate tests recency, not completeness.** It does not replace the payout floor (which asks whether
payouts are *proportionate* to job value). Both run; they answer different questions.

⚠️ **Put the gate in one module and import it.** This logic existed in two scripts with the same
constant and the same field, which is the drift failure mode described under "Scope exclusions are a
design surface" — the copy you forget is the one that writes to production.

### Batching
Close via REST composite (`PATCH /composite/sobjects`) in batches of 10 with `allOrNone=false` — same governor-limit reasoning as Section 1.

### Re-verify against the classifier itself, not a paraphrase of it

The review sheet is a snapshot. Hours or a day pass between the sweep that classified a record and
the human approval that acts on it, and records move in that window — so the apply step must re-check
every condition live before it writes. Two things about *how* to re-check:

**Import the classifier's own functions; do not re-implement the criteria in the apply script.** An
apply script that hand-rolls "the close-out test" will drift from the sweep, and the drift is
invisible: both scripts look correct in isolation and disagree only on the records that matter. This
is the same failure mode as duplicating a threshold constant, one level up — the unit that drifts is
the *predicate*, not the number. Keep the sweep module import-safe (guard its entry point) so the
apply script can pull the real functions in.

⚠️ **A module global that is populated at runtime is EMPTY on import.** This is the trap that makes
the import approach backfire. A sweep typically resolves some state during its main run — an
exemption list queried by profile, an activity-date map built from a transaction pull — and stores it
in a module-level dict or set that the criteria functions read. Import the module from elsewhere and
those functions still run, but against empty state. The failure is **silent and directional**: every
record grades as missing whatever the empty structure was supposed to supply, so the apply script
blocks records it should have written and reports a clean "0 written, all blocked" run that looks
like a legitimate result. Enumerate the runtime-populated globals and repopulate them exactly as the
sweep's own entry point does.

### Diff a marked-up approval file against the sheet it came from

When approval comes back as an exported CSV of hand-marked rows, reconcile those rows against the
**tabs** of the source workbook before writing — do not trust the filename or the approval column to
tell you which route a row was on. An approver working across tabs can easily carry a surface-only /
flag-only row into the approved export alongside genuinely auto-fixable ones; the row still carries
its "not auto-fixed" note in a text column, but nothing structural stops the write. Gate those rows
behind an explicit opt-in flag in the apply script so the routing hold cannot be overridden by
accident, report them as *held* rather than dropping them silently, and put the question back to the
approver.

---

## Section 4b — Attendance-exempt corps — RETIRED

**This section described a second close pass that no longer exists.** It is kept because the way it
became obsolete is the reusable lesson.

**The original problem.** Some licensee / commercial operators are not held to the attendance-logging
policy and leave `LaborDaysActual__c` blank. The Section 4 candidate query required
`LaborDaysActual__c != 0` as a blanket "work happened" gate, so those WOs were **structurally
invisible** to it — not skipped with a reason, simply never returned. A parallel pass was built that
substituted `TotalPayoutsForLabor__c > 0` as the work-happened signal.

**What retired it.** Attendance was later scoped so it is graded **only for owners it actually
applies to**, and the blanket filter was dropped from the query. Once that landed, the main pass
handled these owners correctly with no exemption at all — the exempt-owner list had become a
description of who the rule already skipped, not a rule of its own.

**The trap: a superseded script that still runs.** The retirement step was not done when the filter
was dropped, so the parallel pass stayed executable for several days after it was redundant — and it
had drifted badly in the meantime. It was missing **two gates the main pass had gained**: the
quiet-period activity gate (it proposed closing records that had taken payments within five days,
one of them a five-figure payment the previous day) and the surface-only owner routing (it would
have auto-written records for an owner who had been moved to flag-only). Because closing is one-way,
either would have been unrecoverable.

**Generalisable rules:**
- When a filter is removed to fix scoping, **check what that filter was propping up.** A workaround
  built around a filter becomes dead the moment the filter goes — but it does not stop running.
- **Retire the workaround in the same change** that removes its reason to exist, or it silently
  ages out of policy while remaining runnable.
- A superseded script should **hard-exit**, not merely be documented as deprecated.
- Knowledge the workaround carried (here, which owners are licensee operators) belongs in the shared
  reference module, explicitly labelled as **descriptive context, not an active gate** — otherwise
  the next person re-implements the exemption it was meant to retire.

---

## Attendance completeness rule

Attendance is judged against the **day estimate**, not merely non-zero — but the bar is a **floor**, not a completeness standard.

```
denom = LaborDaysProjected__c            if projected is credible (QuotedSubtotal__c / projected <= $1,500 per projected day)
      = QuotedSubtotal__c / $572          otherwise
attendance complete  ⇔  LaborDaysActual__c >= 0.30 * denom      (0 logged is always incomplete)
```

**Why 30% and not a completeness bar.** The threshold was 80% until it was re-derived against the
data: the median crew logs ~92% of the day estimate, so an 80% bar flagged roughly a third of all
graded work orders — overwhelmingly jobs slightly under estimate, not jobs nobody logged. The
operational objection that settled it: a job *sold for ten crew and delivered with four* is a
legitimate outcome, and that is 40% — so any bar at or above 50% flags exactly the case the business
considers acceptable. 30% clears it with margin and still catches token logging (a handful of days
against a hundred-day estimate).

**What this knowingly gives up:** persistent partial-logging is no longer detected. A crew logging
three of ten days every time will pass indefinitely. That trade was accepted deliberately — a
near-binary test needs no per-case override system, which was the stated requirement. Below-bar
records are labelled **zero-vs-token** ("no attendance logged" / "partial attendance"), since at a 30%
bar an estimate being slightly high can no longer explain the gap.

⚠️ **Lowering an attendance bar does not simply reduce outreach — it reclassifies records.** Once a WO
stops counting as missing attendance it reads as *complete*, so it moves out of the field-ask
population and into the **auto-close candidate** population. Re-check the auto-close queue after any
change to this threshold; the volume that leaves one list arrives on the other.

**Why the fallback:** `LaborDaysProjected__c` is a reliable denominator most of the time, but on a small share of WOs it's left as a 1–2-day placeholder on large-dollar jobs (a high-value job "projected" at 1 day). When `subtotal / projected` exceeds the credibility cap, projected is not trusted and a subtotal-implied day estimate is used instead. The constants are calibrated from the historical median of subtotal-per-actual-labor-day on cleanly-logged, closed WOs; recalibrate if job mix shifts.

**Not a hard no-close for the field list** — below the bar becomes a quantified email line ("attendance is X% below your projected labor days — logged A of D"). The same rule governs the field list and the auto-close pass so triage and close stay consistent. Note this is now a *floor*: a work order logging 30–80% of its estimate is treated as complete and **is** eligible to auto-close.

⚠️ **Scope the attendance test to the owners actually on the policy.** Attendance logging is a
requirement for one field organisation, not the whole company. A gate that applies it to every owner
holds back work orders that are genuinely closeable — this defect has appeared independently in two
separate scripts (the auto-close exporter and the pre-flight checker), each time as a hard
`LaborDaysActual__c != 0` filter with no owner scoping. Resolve the owner's team membership from the
live manager chain and apply the test only to that set.

**Scoping it is not only a relaxation — it also makes the gate bite.** Enforcing attendance as a
`!= 0` filter in the *query* means an on-policy work order with nothing logged is never returned at
all: it is invisible, not skipped. Move the test into classification and those records surface as
flagged instead of vanishing, which is the enforcement the policy actually wants. Expect the change
to move records in both directions and validate it that way — a read-only pass over one cycle,
classifying every candidate under both the old and new rule and diffing by record, is enough.

⚠️ **Put the roll-up in one module and import it — and check the copies before you consolidate.**
Team membership is consulted by the sweep, the field emails, the auto-close exporter and the
pre-flight. When these were finally compared, they did not agree: two walked the full manager chain
while a third matched **direct reports only**, so an owner two levels down counted as on-team for one
script and off-team for another. Nothing announced the divergence — both readings look correct in
isolation. Resolve membership transitively (walk `ManagerId` to the root, guarding against a
management cycle, which Salesforce does not prevent), resolve the root user live by name rather than
pinning an Id, and warn loudly if the roll-up ever resolves to nobody — that is what a broken
`ManagerId` looks like from the inside.

### Keep one implementation of a graded threshold

A threshold like this is consulted by every layer — the sweep, the field emails, the triage list and
the auto-close gate. Implemented once per script it *will* drift, and **the copy that misses a change
is the one gating production writes.** When four implementations were finally compared, three had
been lowered to the current bar and the fourth — the auto-close exporter — was still enforcing the
retired one, holding work orders back against a standard that no longer existed while the
documentation promised triage and close used the same rule. Twelve records on a single day's
candidate set; eleven were false flags, and one owner accounted for seven of them.

Two things make consolidating it safe rather than risky:

- **Diff old against new over the full historical population, not just today's candidates.** Doing
  that over ~8,800 closed records surfaced a divergence nobody had ever decided: a *negative*
  projected-day count passes a credibility test of the form `subtotal / projected <= cap` (a negative
  ratio is below any cap), becomes the denominator, and then fails a later `denominator > 0` guard —
  so those records escaped grading through an accidental interaction rather than a rule. Requiring a
  positive projected count sends them to the fallback denominator instead. Guard ratio tests with an
  explicit positivity check; a sign error hides inside any cap comparison.
- **Size every divergence against production before choosing a behaviour.** Each edge case here
  touched under 0.4% of records, which is what made picking one behaviour a refactor. Had one been
  material it would have been a business decision instead, and belonged with the business.

Then check the *direction*: here every divergence resolved toward grading records the copies had
skipped, so consolidation could only surface more, never hide anything. A consolidation that would
newly hide records needs the same scrutiny as a rule change, because that is what it is.

### Before calling something a coverage gap, check whether the population is dormant or active

When a broad rule engine replaces a set of hand-built report filters, the parity question is coverage:
does the engine surface everything the reports do? Read the reports' rows directly rather than
rebuilding their filters, and diff record by record.

But a record the engine misses is not automatically a gap. A worked example: work orders sitting in an
in-progress status with **no start and no end date** were invisible to the engine's close-out rule,
because that rule keys on the end date existing. The reports caught them immediately; the engine would
not look at them for three months. That reads like a blind spot covering dozens of live records.

It wasn't. **Twenty of the twenty-one had a transaction within the last thirty days** — money moving,
crews being paid, someone plainly working the job. And the shape that *would* be dangerous — the same
status, no dates, aged past the fallback window, and **no transactions at all** — returned **zero
records**. The state is transient by construction: when the job ends someone sets the end date, the
close-out rule starts applying, and the gaps surface then. It only becomes permanent under
abandonment, which shows up as an absence of transactions.

So the engine was not failing to see those records; it was declining to nag about a job still in
flight. The reports and the engine differed on **timing, not coverage** — one asks mid-job, the other
asks at close.

**The check worth running before you file a gap:**

- Is the missing population *dormant or active*? Transaction recency is usually the cleanest test.
- Is the state *transient or terminal*? If a normal downstream event (a date being filled, a status
  advancing) pulls the record into an existing rule, the engine has a latency, not a hole.
- Does the *terminal* version of the shape actually exist in the data? If it returns zero, the
  fallback window is working rather than failing.

If all three come back benign, what is left is a preference about when to ask — which belongs with the
business, not in a rule change.

### Payout floor — gate the auto-close, not the record after it closes

A work order can satisfy every close-out test and still not be finished being **paid out**. Because a
closed WO is edit-locked, a premature close is expensive to reverse — so the payout test belongs
*before* the close, as a condition on the auto-close rule rather than as a separate finding on already-closed records.

```
payout ratio = TotalPayoutsForLabor__c / (quoted value with change orders
                                          − materials cost, when materials are included in the contract)
auto-close allowed  ⇔  payout ratio >= 0.20      (below → route to human review)
```

**Net out materials before judging the ratio.** A material-heavy job legitimately shows low labor
content, and netting materials removed roughly **half** the non-zero exceptions at the same threshold —
they were artifacts of the denominator, not payout problems.

**Denominator caution:** use the quoted-subtotal-with-change-order field, **not** the plain quoted
subtotal. The latter is inflated on work orders carrying *denied* change orders (a known formula
defect), which understates the ratio on exactly the records most likely to look anomalous.

**Why a floor is defensible here** (unlike attendance, where the spread was too wide): labor runs a
tight share of quoted value — roughly p25 48% / median 56% / p75 64% net of materials, with per-entity
medians spanning only ~40–61% across 30+ operating accounts. Below 20% is a genuine empty zone. The
exceptions it surfaces cluster by **owner**, not by work type, so treat them as a payout-recording
conversation rather than a per-record field ask.

⚠️ If a shipped "job costing percent" style field computes this ratio **without** netting materials,
anything reporting on it understates labor share by several points.

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

### Building that close-gate validation rule — four traps

Moving the check from a script to a validation rule is the right call, but the rule is enforcement code
and fails in ways a report does not. All four below were hit on a single team-scoped attendance rule
that sat **inactive and silently broken for twelve days** before anyone noticed.

**1. A manager-chain clause is easy to write inside-out.** Scoping "owners who roll up to manager M"
across two levels needs `OR`, not `AND`:

```
OR(CONTAINS(Owner:User.Manager.Full_Name__c,        "<manager>"),
   CONTAINS(Owner:User.Manager.Manager.Full_Name__c, "<manager>"))
```

`AND`ed, it demands the owner's manager **and** grandmanager both be that person — which **nobody**
satisfies, because a direct report has the manager at level 1 and a skip-level report has them at
level 2, never both. The rule saves cleanly, activates cleanly, and never fires. **Before trusting any
manager-chain formula, enumerate the real reporting tree and confirm at least one live user evaluates
TRUE.** A rule that blocks nothing is indistinguishable from a rule nobody has tripped yet.

**2. Verify the depth of the tree, not just the formula.** A two-level clause is complete only while
the org chart is two levels deep. Compare the formula's matches against the **transitive** roll-up
computed from live `ManagerId` data and assert both directions — on-team-but-missed and matched-but-
off-team. Re-check whenever the org chart moves; a third level added later escapes silently.
Name-substring matching (`CONTAINS` on a full-name field) also needs a check that exactly one person
in the org matches that string.

**3. Enumerate who holds the bypass permission — including automation users.** A `NOT($Permission.X)`
clause exempts every holder, and permission sets grant it far more widely than expected. Two
consequences: an admin **cannot test their own rule as themselves** (use login-as, which keeps the
target user's permissions), and any **scheduled Apex or integration user** holding the permission
bypasses the rule entirely.

**4. Keep automation exempt on purpose, and write down why.** Where a scheduled job advances status in
bulk, check how it saves. A class ending in `Database.update(list, false)` that never inspects the
returned `SaveResult[]` swallows validation failures **silently** — no exception, no log entry, no
error to any human, and the affected records simply stop progressing. Gating such a job with a
validation rule produces an invisible stall, not an enforced policy. If the automation user already
holds the bypass permission, that is protective; leave it, and record the reason so nobody later
"fixes" it.

**Related — pick the enforcement bar separately from the reporting bar.** The gate and the report
answer different questions, so they should not be forced to share a threshold. A minimal
"something was logged" test is the right shape for prevention: it is unambiguous at the point of
save, and it is the part a user can act on immediately. A proportional completeness bar (see
"Attendance completeness rule") stays in triage, where partial logging can be quantified and chased
without blocking work. Expect a small band that clears the gate but still gets flagged downstream —
that band is the design working, not a leak. Verify the cost of the looser bar by counting, over a
recent window, how many records each candidate threshold would have caught.

## A status-advance rule needs proof the job started — a date is not proof

Two rules advance a WO out of the pre-work statuses (Coordination / Scheduling) into Work In Progress.
They are written as a first-match-wins chain, so they are mutually exclusive, and that exclusivity is
what makes them safe to treat differently:

| | fires when | evidence it holds |
|---|---|---|
| **work-logged rule** | `LaborDaysActual__c > 0` **or** `TotalPayoutsForLabor__c > 0` | crew days or a labor payout exist — the job demonstrably started |
| **stale-date rule** | neither of the above, and `StartDate` passed by more than a small grace | **only** that a planned date came and went |

Because the chain is `elif`, the stale-date rule only ever sees records with **zero** attendance *and*
**zero** payouts. It has no evidence the work began — a start date is a plan, and plans slip.

**Therefore gate the stale-date rule on the schedule-confirmation checkbox
(`ScheduleConfirmedWithClient__c`), and do not gate the work-logged rule.** Gating the work-logged rule
would be a no-op by construction: it requires logged work to fire at all, and logged work overrides the
checkbox. The two rules already partition on exactly the axis the gate cares about.

**Unchecked must route to a field question, never a silent suppression.** Suppress the *ask*, not the
*row* — the review sheet keeps full visibility and only the outbound email is throttled. A gate that
removes rows teaches the process to hide its own backlog.

**Why this matters beyond the one rule:** the same cleanup can re-create, days later and through a
second door, the exact behaviour a real-time automation change was introduced to prevent. When an
automation rule changes, grep the batch/cleanup layer for anything that reaches the same end state.

### Size a gate on the population it can actually reach

Measuring the checkbox's adoption across *all* Coordination work orders gave **7.3%**, which made the
gate look like it would block nearly everything. That was the wrong denominator: the rule can only ever
touch WOs that **have a `StartDate`**, and most Coordination WOs have none. Among records the rule can
actually reach, adoption was **81%**.

**Generalise:** before rejecting a gate as too strict, compute adoption over the rows the rule can
reach, not over the whole status. A field that looks unused org-wide is often well-populated by the
time the record reaches the state the rule cares about.

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
