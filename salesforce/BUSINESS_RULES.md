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
- The Wallpapers Unlimited permission is NOT held
- The user creating the WO is not in the alias exclusion list

Inserting a new WO from a Closed Won opp with a real (non-Estimate-Appointment) WorkType WILL fire this email. Relevant for any test data setup, sandbox-to-prod data load, or external WO creation. Mitigation when seeding test data: use a test Account whose Primary Contact email is a controlled inbox.

## Gross margin (lives on WorkOrder, not Opportunity)

- **Canonical GM% = `WorkOrder.Gross_Margin_Percent__c`** = `GrossProfit__c / Quoted_Subtotal_with_Change_Order__c`.
- `WorkOrder.GrossProfit__c` = `Quoted_Subtotal_with_Change_Order__c − TotalCostsWithoutSales__c`.
- **⚠️ Do NOT use `WorkOrder.GrossProfitPercent__c`** for GM — its denominator is `NetValue__c` (settled value), which inflates the % when a job didn't collect the full quote. Anchor GM on `WorkOrder.EndDate`.

## Lead source classification

- **`Opportunity.LeadGroup__c`** *(self-gen bucket, updated 2026-05-21)*: `LeadGroup__c` ∈ {`'Self-Generated'`, `'Trade Show'`, `'Repeat'`, `'Referral'`} → **self-gen**; **every other value (and null) → marketing** (so self-gen + marketing always reconciles to the total).
- The previously-flagged split is now in effect: `Repeat`, `Referral`, and `Trade Show` are counted as **self-gen** (relationship/earned leads), no longer marketing.

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

## Geography / sales tax

- Sales-tax rate is **`ServiceTerritory.TaxRate__c`** (geographic). There is no per-licensee/brand rate and no separate tax object.

## Brand

- Colors: Orange `#EE662E`, Blue `#2BAAE1`, Green `#8DC442`, Navy `#172B4D` (primary text). Fonts: Roboto (body), Roboto Condensed (display/numbers).
