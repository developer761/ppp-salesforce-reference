# PPP Salesforce — Business Rules & Field Gotchas

Conventions and traps for querying Precision Painting Plus's Salesforce org correctly. These are the rules behind PPP's existing reporting; following them keeps the Command Center's numbers matching the org's own reports. Schema details (every field, picklist, flow) are in `DATA_DICTIONARY.md`.

> Salesforce is the source of truth. Read it live (with caching); don't mirror it.

## Fiscal year

- **FY starts February 1, ends January 31.** FY name = the start year. **FY26 = 2026-02-01 → 2027-01-31.**
- Fiscal quarters: **Q1** Feb–Apr · **Q2** May–Jul · **Q3** Aug–Oct · **Q4** Nov–Jan.

## Primary sales metric

- **`Opportunity.QuotedSubtotalWithChangeOrder__c`** (Currency) is *the* sales number.
- "Realized sales" = filter `IsWon = true`; anchor on `CloseDate`.
- Attribute by **`Opportunity.OwnerId`** (not Account owner, not Quote owner).

## ⚠️ Field-name trap — "Quoted Subtotal with Change Order" differs by object

The same business concept has **two different API names**:

| Object | API name |
|---|---|
| Opportunity | `QuotedSubtotalWithChangeOrder__c` (no underscores) |
| WorkOrder | `Quoted_Subtotal_with_Change_Order__c` (underscores) |

A SOQL written for one fails on the other. Sales metrics use the Opportunity version; gross-margin / pricing metrics use the WorkOrder version.

## Quota & points

- **`QuotaPoints__c`** custom object: filter **`QuotaType__c = 'Field_Member'`** for real rep-attributable rows (other types are internal/placeholder).
- **1:1 points-to-dollars:** `SUM(QuotaPoints__c.Points__c)` per Opportunity equals `Opportunity.QuotedSubtotalWithChangeOrder__c`. A quota stored as `750000` points = $750k.
- **Annual goal — `TotalQuota__c`:** `QuotaAssigned__c` where `User__c = <rep>`, `Allocation__c = 'Owner'`, `Status__c = 'Active'`, `FY__c = <year>`. **Exclude `Allocation__c = 'CatchAll'`** (placeholders).
- **Monthly goal — `SubQuota__c`:** `Assigned__c` (goal) / `Attained__c` (rolling Closed-Won sum); parent is `TotalQuota__c`.
- **⚠️ Trap:** `SubQuota__c.CurrentUserId__c` is a `$User.Id` formula = the *viewing* user, **not** the rep. Use **`TotalQuota__r.User__c`** for rep attribution.

## Rep universe

- Field reps = active `User` records with **Profile name `*Standard.Field`** (~26 active).
- The sales manager's team is tagged by the **`Sales_Team_Member`** permission set (membership tag only — no FLS on it). Read it dynamically; don't hardcode names.

## ⚠️ License-type trap — counting Full Salesforce license users

**Do not use `UserType = 'Standard'`** to count Full license users. It over-counts: it includes non-human integration users (e.g. Analytics Cloud Integration User, Sales Insights Integration User) that carry a different license type but share the `Standard` UserType.

**Correct filter:** `Profile.UserLicense.Name = 'Salesforce'`

```sql
SELECT COUNT(Id) FROM User
WHERE IsActive = true
AND Profile.UserLicense.Name = 'Salesforce'
```

Similarly, **do not use the `SDocs_User` permission set** to count SDocs license holders — the perm set membership can diverge from the actual package license. Use `UserPackageLicense` filtered by the SDocs package ID instead.

## Work orders & "completed job" definition

- **⚠️ Do not rely on `WorkOrder.IsClosed`.** It only flips true for `Status = 'Closed'` and misses `'Complete Paid in Full'` and `'Complete Balance Owed'`. **Filter on `Status` directly.**
- Completed job = `Status IN ('Closed', 'Complete Paid in Full', 'Complete Balance Owed')`. (~99% are `Closed`.)
- `Opportunity.WO_Complete__c` may have a similar lag — sanity-check before relying on it.

## ⚠️ WorkOrder save behaviors (block writes, fire customer emails)

Two active flows materially affect when a WorkOrder can be safely modified from external tools (Command Center, integrations, scripts, data loads).

**`WorkOrder_DisallowEditWhenClosed`** — RecordBeforeSave on Create+Update; entry filter `ISPICKVAL(Status, 'Closed')`. **Blocks ALL field updates** when WO Status is `Closed`, even single-field writes from external tools. WO must be in an open status for any write to land.

**`WorkOrder_SendLetsGetStartedEmail`** — RecordAfterSave on Insert. Sends a customer-facing email to the Opp's Primary Contact when **all** of the following are true:
- Opportunity `StageName = 'Closed Won'`
- `WorkType.Name` is NOT `Estimate Appointment`, `Phone Estimate Appointment`, or `Partner Estimate Appointment`
- A subsidiary-scoped exclusion permission set is NOT held
- The user creating the WO is not in the alias exclusion list

Inserting a new WO from a Closed Won opp with a real (non-Estimate-Appointment) WorkType WILL fire this email. Relevant for any test data setup, sandbox-to-prod data load, or external WO creation. Mitigation when seeding test data: use a test Account whose Primary Contact email is a controlled inbox.

## ⚠️ WorkOrder money — the metric that matters is not on the page

A WorkOrder carries the job's value twice, and the two are separated by a discount applied inside a
formula:

```
QuotedSubtotal__c = (OriginalSubtotal__c + Canceled_Line_Items__c)
                  - Discount_Amount__c
                  - (NULLVALUE(DiscountPercentageLabor__c,0) * (OriginalSubtotal__c + Canceled_Line_Items__c))
                  + IF(Materials_Included__c, CostMaterials__c, 0)
DiscountAmountCalculated__c = NULLVALUE(DiscountPercentageLabor__c,0) * NULLVALUE(OriginalSubtotal__c,0)
```

**It is not a live sum of the line items** — the base is a stored subtotal, so editing a line item
lets `Subtotal` and `QuotedSubtotal__c` drift apart with nothing flagging it.

**Layout visibility (verified 2026-08-21 against both WorkOrder layouts):**

| Field | On layout |
|---|---|
| `Subtotal` (standard), `TotalPrice`, `TotalDiscount__c` | **No** |
| **`Quoted_Subtotal_with_Change_Order__c`** — the canonical sales metric | **No** |
| `Subtotal__c`, `QuotedSubtotal__c`, `DiscountAmountCalculated__c` | Yes, readonly |
| `DiscountPercentageLabor__c` | Yes, **editable** |

Two consequences. The number the business is measured by is reachable only by report or query, so
any instruction of the form "open the work order and read X" must be checked against the layout
first. And the discount percentage that moves that number sits on the page in an editable field —
no approval step, no trail beyond field history.

**Related field-name trap:** `Subtotal` (standard) and `Subtotal__c` (custom) are not the same
value. They agree on some records and diverge on others (observed: standard $14,325 against custom
$16,000 on one WO). Testing on a single record will not reveal this.

## Opportunity financial fields are sourced from the WorkOrder (not a rollup)

`WorkOrder.SetOpportunityFinancialFields` (RecordAfterSave, Create+Update) copies the triggering WO's values up to its parent Opportunity when the Opp is `Closed Won` and the WO Status ≠ `Canceled`:
- Opp `NetValue__c` ← WO `NetValue__c`
- Opp `OriginalQuotedSubtotal__c` ← WO `Original_Quoted_Subtotal__c`
- Opp `QuotedSubtotalWithChangeOrder__c` and `TotalAmount__c` ← WO `Quoted_Subtotal_with_Change_Order__c`

**It is last-writer-wins, not a sum** — the most recent qualifying WO save overwrites the Opp fields. **As of v3 (2026-07-21), estimate-appointment WOs (`Estimate Appointment`, `Phone Estimate Appointment`, `Partner Estimate Appointment`) are excluded** from writing these fields. Before v3, a $0 estimate-appointment WO saving after the real WO would zero out the Opp's financials — so on an opp with a real WO worth money, `TotalAmount__c = 0` is a corruption signature. Re-saving the real (non-appointment) WO re-fires the flow and repopulates the Opp.

## Gross margin (lives on WorkOrder, not Opportunity)

- **Canonical GM% = `WorkOrder.Gross_Margin_Percent__c`** = `GrossProfit__c / Quoted_Subtotal_with_Change_Order__c`.
- `WorkOrder.GrossProfit__c` = `Quoted_Subtotal_with_Change_Order__c − TotalCostsWithoutSales__c`.
- **⚠️ Do NOT use `WorkOrder.GrossProfitPercent__c`** for GM — its denominator is `NetValue__c` (settled value), which inflates the % when a job didn't collect the full quote. Anchor GM on `WorkOrder.EndDate`.

## Lead source classification

- **`Opportunity.LeadGroup__c`** *(self-gen bucket, updated 2026-05-21)*: `LeadGroup__c` ∈ {`'Self-Generated'`, `'Trade Show'`, `'Repeat'`, `'Referral'`} → **self-gen**; **every other value (and null) → marketing** (so self-gen + marketing always reconciles to the total).
- The previously-flagged split is now in effect: `Repeat`, `Referral`, and `Trade Show` are counted as **self-gen** (relationship/earned leads), no longer marketing.

## ⚠️ Bulk Lead updates — what fires, and what doesn't

Re-saving Leads in bulk (backfills, imports, mass field updates) runs every active Lead automation.
Audited against production 2026-08-25.

**Does NOT fire on an update — safe:**

| Automation | Why |
|---|---|
| `LEAD_Auto_Assigment` (`assignTargetToSalesCadence`) | Create-only |
| `Lead_NotifyMetaLeadCreated` (`emailAlert`) | Create-only |
| `LEAD_Update_Cadence_Assignee` (`changeSalesCadenceTargetAssignee`) | triggers on **AgentWork**, not Lead |
| `Lead_SetAdCostDetail` | `doesRequireRecordChangedToMeetCriteria = true` — fires only when a record *newly* meets its gate (`LeadGroup__c` set, `AdCostDetail__c` null, `ServiceTerritory__c` set) |
| `Lead_AdCostDetailUpdate` | `filterFormula` requires `AdCostDetail__c` to actually change |

Those last two gates are load-bearing: **manually corrected ad-cost-detail assignments survive a bulk
re-save untouched.** Confirm they are still gated before trusting that on any future backfill.

**Fires, but harmless:** the other active record-triggered Lead flows that run on update have **zero
action calls** between them — pure field-setters, no email/SMS/callout/cadence enrolment.

**⚠️ One real side effect.** `LeadTrigger` → `LeadTriggerHandler.beforeUpdate` calls
`LeadService.enforceTwoLetterState`, which silently rewrites any non-two-letter `State` value on
every re-saved record. Count that population before a large backfill rather than discovering it after.
The same path calls `addErrorOnConversionWhenMissingRequiredFields`, so use
`Database.update(records, false)` for partial success instead of all-or-nothing.

**⚠️ Do not classify these flows by name prefix.** The `LEAD_` / `Lead_` prefix is a naming
convention, not the trigger object — at least one `LEAD_`-prefixed flow triggers on a different
object entirely. Read `<object>` inside `<start>` in the flow metadata. An inventory grouped by name
will mis-state the blast radius of a bulk operation.

### Before-save flows and where a field's value comes from

A before-save flow runs **ahead of** before-triggers, so it sees values that arrive on the **insert
payload** but not values written by Apex. Whether a derived-value flow can be before-save (cheap, no
extra DML) or must be after-save therefore depends on what populates its source field.

Worked example: `Lead.AdSetName__c` is referenced by no Apex class and no flow — it arrives on the
payload from the web-to-lead site endpoint and from bulk loads. A before-save flow can read it.
By contrast `Lead.Lead_Gen_Category__c` **is** Apex-written: `LeadIncomingProcessor` maps the lead
vendor's own category string into it on insert for the Angi and HomeAdvisor paths, which is why that
field is heavily populated for those sources and empty for others. Any automation writing to it
should guard on the field being blank so vendor-supplied values are never overwritten.

## Call Center hours

- **Mon–Fri:** 9am – 8pm ET
- **Sat/Sun:** 9am – 5:30pm ET
- Timezone: America/New_York (DST-aware). All CC staff work in ET.
- The org's `BusinessHours` "Default" record (9am–10pm weekday, 9am–7:30pm weekend) is **not** the CC schedule — don't rely on it as a proxy.
- For after-hours analysis: `Lead.CreatedDate` is UTC. Filtering against these ET boundaries requires DST-aware conversion. `Lead.Created_Hour__c` alone is not sufficient — see its ⚠️ note in `DATA_DICTIONARY.md`.

## Transactions (money flow)

- **`Transaction__c`** record types: `Payment_In`, `Payment_Out`, `Purchase`.
- Key fields: `Amount__c`, `Date__c` (period anchor), `PayeeType__c` (`Labor_Company` / `Reimbursement` / `Customer_Refund` / `Merchant_Fee`), `Payee__c` (Account lookup), `WorkOrder__c`, `Opportunity__c`.
- **Label convention:** in any UI, expand to **"Payments / Payouts / Purchases"** — never abbreviate "transaction" to "tx".

## Reviews

- **`Review__c`**: `GoodReview__c = true` (ratings 4–5), `BadReview__c = true` (ratings 1–3). Exclude `Removed__c = true`.
- Attribute reviews via **`Account__r.OwnerId`** (different from the Opportunity/WorkOrder owner used elsewhere).

## Cases (complaints)

- Customer-facing `Case.Type` values only (6): `Estimator No Show`, `Waiting for Estimate`, `Dissatisfied Customer`, `Balance Owed`, `Service Call`, `Other`. Other types are deprecated IT-internal.
- Link a case to a rep via **`Case.Opportunity__r.OwnerId`** (covers both no-show and service-call cases).

## Scheduling — Service Appointments and rep calendars

The booking chain is **Lead → convert → Opportunity → WorkOrder → ServiceAppointment → AssignedResource → ServiceResource → User**. Service Appointments are parented to the **WorkOrder**, never directly to the Opportunity — FSL does not permit an SA→Opportunity link, so the work order exists purely to carry that relationship.

Assignment is **territory-and-availability driven, not owner-driven**. The SA's Service Territory is derived from the job's zip code; eligible resources come from Service Territory membership, work type, and skills. Do not infer the assigned estimator from the Opportunity or Lead owner.

### ⚠️ Field reps read an Event, not the FSL calendar

Reps struggled with the native FSL calendar, so a standard **`Event` is replicated onto the rep's Salesforce calendar** by the active flow `ServiceAppointment_CalendarEvent` (record-triggered, after-save, create + update). That Event is the rep's entire mobile workflow: open app → Event → click through to the Opportunity.

**Entry gate — all three must be non-null, or no Event is created at all:**

```
!ISNULL(FSSK__FSK_Assigned_Service_Resource__c) &&
!ISNULL(SchedStartTime) &&
!ISNULL(SchedEndTime)
```

An SA with no assigned service resource produces **no Event** — not a degraded one. The appointment is invisible to the rep.

**Field sources:**

```
Event.WhatId  = FSSK__FSK_Work_Order__r.Opportunity__c
Event.OwnerId = FSSK__FSK_Assigned_Service_Resource__r.RelatedRecordId
```

`Inquiry_Notes__c` and `Primary_Contact__c` are pulled through the same work-order path.

**`WhatId` has no Account fallback.** It resolves *only* through WorkOrder → Opportunity. No work order means a null `WhatId` and an Event that links to nothing — there is no "navigate from the Account instead" path.

Two kinds of Event exist — one owned by a **territory public calendar**, one owned by the
**individual rep User** — but **not every SA produces both.** Measured 2026-08-21 over a 30-day
window: 1,388 rep-owned against 964 calendar-owned estimate-appointment Events, and sampled SAs are
found with only the rep's. Do not assume a public-calendar twin exists for a given appointment.

### ⚠️ Field-name trap — ServiceAppointment carries two work-order links

| Field | Type |
|---|---|
| `ParentRecordId` | Standard FSL polymorphic parent |
| `FSSK__FSK_Work_Order__c` | Field Service **Starter Kit** custom lookup |

They hold the same Id in practice but are **not interchangeable** — the calendar flow reads `FSSK__FSK_Work_Order__c`. An SA correctly parented via `ParentRecordId` alone still yields no usable calendar Event.

For an externally created SA to produce a working rep calendar event it must populate `FSSK__FSK_Work_Order__c` (→ a WorkOrder with `Opportunity__c` set), `FSSK__FSK_Assigned_Service_Resource__c` (→ a ServiceResource with a `RelatedRecordId`), `SchedStartTime`, and `SchedEndTime`. Relevant when scoping any external system that writes Service Appointments.

The Starter Kit namespace also appears on `User` as `FSSK__FSK_FSL_Resource_Type__c`.

### Estimate work types

Three distinct estimate work types with different durations — `Estimate Appointment` (1 hr), `Phone Estimate Appointment` (0.25 hr), `Partner Estimate Appointment` (1 hr). "Book an estimate" is not a single operation. Multiple FSL **scheduling policies** are configured; the same resource returns different availability depending on which policy runs.

### ⚠️ WorkType is not a reliable interior/exterior signal — read the line items

Deriving a job's scope from `WorkOrder.WorkType.Name` looks obvious and is wrong often enough to
break anything built on it. Measured in production 2026-08-21:

- Of a 300-work-order sample typed **Interior** but carrying an **exterior** paint product line,
  **55% had line items that were exclusively exterior** — the work type was the incorrect field,
  not the product line. A further 30% were genuinely mixed jobs.
- Mixed jobs are common and carry a **single** work type, so an interior-typed work order routinely
  contains `Exterior Painting: …` line items.

**Use the line items.** `WorkOrderLineItem.ProductName__c` begins with the product family
(`Interior Painting: …` / `Exterior Painting: …`), so scope should be derived from the set of line
items and treated as *both* when they disagree. A work type may be used as a fallback only when
there are no line items to read.

⚠️ **Do not auto-derive a single scope for a write.** A mixed or mis-typed job has no correct single
answer, and picking a default silently records a scope nobody chose. Where a field demands one value
(see `MaterialType__c` in the data dictionary), leave it alone rather than guessing.

Separately, and reassuringly: the estimator's product-line pick is accurate. Only **2.8%** of
exterior work orders carrying an interior line were genuinely wrong once checked against their line
items, and the reverse direction was under **0.5%**.

## Geography / sales tax

- Sales-tax rate is **`ServiceTerritory.TaxRate__c`** (geographic). There is no per-licensee/brand rate and no separate tax object.

## Corporate-name attribution (territory → billing entity)

Which corporate entity an Opportunity / WorkOrder belongs to is derived from its **Service Territory**, by rule — **not** from a single field.

- **⚠️ Do not use `ServiceTerritory.Company_Name__c` for corp attribution.** It holds the insurance / legal-entity name and can differ from the billing corp (some territories show a distinct legal entity but bill under the corporate parent). It's the right value for the invoice "legal entity" line, the wrong one for attribution.
- **Corporate-owned territories:**
  - **NY → `Blue Chip Painting and Contracting Inc. 2026`**
  - **Non-NY → `PPP of Long Island` (`PPP of Long Island INC 2026`)**
- **Fiscal-year suffix:** the trailing year (`2026`) marks the current-FY corp setup; the **legal entity** is the same name without the year. When matching, treat `… Inc.` and `… Inc. 2026` as the **same entity** (a year-only difference is not a real mismatch). Likewise fold known legal-vs-brand and suffix aliases (a brand name and its legal entity are one billable corp).
- **Licensee territories are the exception** — they attribute to the **licensee's own corporate entity**, not the two above. The specific territory→licensee-corp mapping lives in the private admin records (per `playbooks/licensee-onboarding.md`, licensee names are kept out of this repo).
- **`WorkOrder.Corporate_Name__c` is the authority** when it disagrees with `Opportunity.Corporate_Name__c` (the WO reflects who actually does the work). In the ad-cost model the same entity appears as `AdCostDetail__r.CorpAccount__r.Alternate_Corp_Name__c`.
- **Sentinel values are expected, not errors:** some Opportunities carry `Corporate_Name__c = 'Needs validation'` (or `'Ask Alex'`) as a placeholder until a WorkOrder sets the real corp — common for cross-territory / phone-estimator Opps. Treat these as "not yet set", not as a corp.

## Brand

- Colors: Orange `#EE662E`, Blue `#2BAAE1`, Green `#8DC442`, Navy `#172B4D` (primary text). Fonts: Roboto (body), Roboto Condensed (display/numbers).

## Record ownership — you cannot assign to an inactive user

Salesforce rejects any write that makes an **inactive** user the owner of a record:
`operation performed with inactive user [005…] as owner of workOrder`. This has a practical consequence
for data cleanup: where **both** sides of an owner mismatch are inactive (e.g. a WorkOrder and its
Opportunity both owned by departed users), **neither direction can be written** — the mismatch is
unfixable in place. Options are to assign an **active** owner to both sides, or to accept the mismatch.
Temporarily reactivating a departed user works but leaves you with two inactive owners that merely match.

A second, independent blocker returns `The new owner must have read permission`: the prospective owner's
**profile or permission sets grant no read on the object**. This is *not* a portal/partner-licence limit —
partner (`PowerPartner`) users own records routinely. Check the profile's `ObjectPermissions` for the
object rather than assuming a licence-type restriction.

⚠️ **Do not test either condition with a write on a live record.** Assigning an active owner succeeds and
then **cannot be reverted**, because restoring the original inactive owner hits the first block. Check
`User.IsActive` and `ObjectPermissions` first — both are queryable.

## Field history — retention caps what is knowable

Field history is retained on a **rolling ~18-month window**, so the horizon **moves forward over time**.
Verified 2026-08-05: the earliest `OpportunityFieldHistory` row of any kind is **2025-02-04** — zero rows
for 2023 or 2024. `WorkOrderHistory` has the same horizon. Not every field is tracked
(`Opportunity.Amount` has no history at all).

**The trap: absence of history is not evidence of no change.** For any record whose activity predates the
horizon, "no edit recorded" means *unknowable*, not *unedited*. Before quoting any rate derived from
history, **split the population into covered and uncovered**, quote the rate only over the covered set,
and label any extension to the uncovered set as an inference.

## ⚠️ Validation-rule formula traps — an Active rule is not an enforcing rule

**`ISNULL()` on a Text field is ALWAYS FALSE.** Text fields are *blank*, never null — the null test is
`ISBLANK()`. Any rule whose `AND()` opens with `ISNULL(<some text field>)` can therefore **never fire**,
while still showing as Active in Setup and appearing in every rule inventory.

Found in production 2026-08-06 on `WorkOrder.RequestReview_If_Complete`:

```
IF(AND(ISNULL(LegacyId__c),
       OR(ISPICKVAL(Status,"Complete Paid in Full"), ISPICKVAL(Status,"Complete Balance Owed")),
       ISPICKVAL(RequestReview__c,"")), true, false)
```

`LegacyId__c` is Text, so the rule had never fired since its creation in 2023. It was widely believed to
be what enforced Request Review on Complete statuses; a separately-authored rule was doing that work.

**Diagnostic:** a record saved that the rule should have blocked. Don't stop at the rule list — pull the
formula (`SELECT Metadata FROM ValidationRule … --use-tooling-api`) **and** check the referenced field's
`type` in the object describe. Compile-check any candidate fix with a **check-only deploy**
(`sf project deploy start --dry-run`), which validates the formula without committing it.

⚠️ **Repairing a long-dead rule is usually the wrong move.** The record population has drifted for years
under no enforcement. If the rule also lacks `ISCHANGED(...)` and a `$Permission` bypass, correcting the
null test will start blocking **every save** on that entire backlog — including automation and integration
writes — not just new transitions. Prefer deactivating it and folding the intent into a rule that already
works and is properly gated.

**Related trap — `$Profile.Name` is the RUNNING USER's profile, not the record owner's.** For an
owner-based carve-out on an object with a polymorphic owner, use `Owner:User.Profile.Name`. Mixing the two
fails in both directions: it exempts anyone *with* that profile editing *any* record, and still blocks
another user editing a record *owned* by that profile. `Owner:User.Profile.Name` is valid in a WorkOrder
validation rule (confirmed by check-only deploy); it evaluates to null on a queue-owned record, which
makes a `NOT(CONTAINS(...))` carve-out fail safe (the rule still fires).

**Prefer profile over free-text `CompanyName` for entity carve-outs.** `CompanyName` is a free-text User
field: a new user with it blank or misspelled is silently *not* carved out, and anyone who happens to type
the matching string silently *is*. Profile names are controlled values. This matters most where an entity
has been renamed — a carve-out matching the old trading name quietly matches nobody.

## SOQL / CLI traps

- **`sf data query` silently caps at 50,000 rows, and under `--json` there is no warning at all.** The
  result set simply contains 50,000 records and looks complete. Always chunk by date range and assert the
  total against a matching `SELECT COUNT()`; a round 50,000 in a result set is a red flag, never a
  coincidence.
- **`NOT LIKE` is not a valid operator.** `NOT (field LIKE '...')` is.
- **Aggregate queries cannot page** (`queryMore` is unsupported) — invert to a filtered non-aggregate
  query or chunk by date.
- **History objects:** `NewValue` is not filterable — filter in the client. Long text areas can be neither
  filtered nor counted in SOQL.
- **SOQL cannot compare two fields to each other** (e.g. work order owner ≠ opportunity owner) — fetch
  both and compare client-side.
- **`CreatedDate = LAST_N_MONTHS:n` is a BOUNDED range that ends on the last day of the *previous*
  month — it excludes the current month entirely.** On a field whose history tracking was switched on
  earlier the same month, every row sits in the excluded window and the query returns **0**. That reads
  as "no data" rather than as an error, so a report built on it can state "no history yet" indefinitely
  while the rows sit there. Use `LAST_N_DAYS:365` for a rolling year, or `>= LAST_N_MONTHS:n`, which is
  open-ended and does include the current month. The `=` / `>=` distinction is the whole trap.
- **Positive-control every zero from a date-filtered history query.** Re-run without the date filter
  before believing it. An empty result proves the filter matched nothing, not that nothing happened.

## ⚠️ AM role reassignment — scope, the picklist trap, and what fires

Moving an Account Manager (or Project Manager / Estimator / Partner Manager) from one person to
another across a rep's book. Distinct from an **owner** change, which must go through the Account's
"Reassign Records" button so Work Orders and Service Appointments cascade.

**`User.AM_Services__c` is an enrollment switch, not a job description.** The active Opportunity flow
that enrolls quotes into the Hatch follow-up campaign gates first on
`Owner.AM_Services__c IN ('Followups','All')`. Fail that gate and the flow dead-ends: the campaign
field is never stamped and the rep's automated follow-ups stop entirely. So a request of the form
*"the new AM handles coordination but not follow-ups"* resolves to leaving the value on `All` —
selecting `Coordination` reads correctly and silently breaks the follow-ups. Never pick a value for
this field from its label; find the consumers first.

**What removes an opp from an AM follow-up report is the Hatch campaign field, not `AM_Services__c`.**
The live AM follow-up reports AND-filter unconditionally on campaign = blank or `AM F/U`, so an opp
enrolled in Hatch is already excluded. Their `AM_Services__c` filter reads the **Opportunity Owner**,
not the Account Manager.

**Scope is two disjoint sets.** `IsClosed = false` is not the whole job — active Work Orders sit on
**Closed Won** opportunities, which that filter excludes. Pull open opps *and* Closed Won opps with a
WO in `Coordination` / `Scheduling` / `Work In Progress` / `On Hold`, then confirm no overlap.
Exclude `Pending`: it is the WorkOrder default status and accumulates on lost and long-finished
records, so it dwarfs the live set without representing work.

**WorkOrder needs zero writes.** It has no writable Account Manager field —
`AccountManagerName__c` / `AccountManagerPhone__c` / `AccountManagerEmail__c` are formulas over
`Opportunity__r.AccountManager__r.*`. Updating the parent Opportunity moves them.

**What the update fires.** Changing `AccountManager__c` triggers the team-member sync flow, which
**deletes the outgoing person's team row for the changed role and creates the incoming one**. Confirm
the outgoing person retains access another way (record owner, or another role lookup on the same
record) before loading. The primary-contact and record-defaults flows are Create-only and do not fire
on update. Flows with `doesRequireRecordChangedToMeetCriteria = true` do not re-fire when their
criteria field is untouched.

**Verify from the org, not the bulk job result.** The Hatch campaign distribution must be identical
before and after; if it moved, the reassignment re-enrolled or dropped records. Note two traps while
checking: aggregates must be pulled with `--result-format json` (CSV blanks the values), and
`OpportunityTeamMember.TeamMemberRole` stores abbreviated values — `Account Mgr`, `Project Mgr`,
`Partner Mgr` — so querying the spelled-out form returns zero rows silently, which is
indistinguishable from a failed load.
