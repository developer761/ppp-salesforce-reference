# PPP Salesforce Reference (for the Command Center)

Salesforce schema + business-logic reference from PPP's internal admin work, shared to keep the Command Center aligned with how the org actually models and reports its data. Salesforce remains the source of truth.

## Contents

| File | What it is |
|---|---|
| `DATA_DICTIONARY.md` | Full schema reference — custom fields on core objects, all custom objects, flows, triggers, validation rules, record types. Snapshot from **production, 2026-05-11**. Schema only, no record data. |
| `architecture_main.md` | Visual map (Mermaid) of how the main objects connect: Sales Pipeline, Service Delivery (Opp→Work Order spine), Fleet & Quota. |
| `architecture_compliance.md` | Compliance/document object map. |
| `architecture_marketing_geo.md` | Marketing spend + geography (Service Territory / Zip Code) map. |
| `BUSINESS_RULES.md` | Conventions and field gotchas — fiscal year, the primary sales metric, quota=points, the GM/field-naming/`IsClosed` traps, etc. Read this before writing SOQL. |
| `REP_PERFORMANCE_KPIS.md` | Exact definitions of the rep scorecard KPIs (revenue, GM, close rate, pricing, money flow, commissions, …). Maps directly to the dashboard's leaderboard + rep profiles. |
| `reference-code/queries.py` | Clean example SOQL pulls (Python/`sf` CLI) for several KPIs. |
| `reference-code/aggregate.py` | Example per-rep aggregation of those query results. |

## How to use it

- **Wiring Salesforce in:** start with `BUSINESS_RULES.md`, then look up exact field API names in `DATA_DICTIONARY.md`. The naming traps there (e.g. `QuotedSubtotalWithChangeOrder__c` vs `Quoted_Subtotal_with_Change_Order__c`) cause real bugs.
- **Dashboard metrics:** `REP_PERFORMANCE_KPIS.md` is the spec for the rep numbers; `reference-code/` shows the query/aggregation shape (it's reference Python, not meant to run inside the Next.js app).

## Notes & boundaries

- **Schema/logic, not data.** The dictionary contains no customer records or live values. Pull actuals from Salesforce.
- **Deliberately excluded:** rep compensation figures (draws), individual GM targets, and internal recipient emails/User IDs. Ask PPP directly if any of those are needed.
- **Freshness:** schema snapshot is 2026-05-11; anything added since won't appear here. Regenerated from production by PPP's admin tooling.
