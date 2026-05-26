# Playbook — CBC / WhatConverts Lead Clean-Up

Bi-weekly process that pulls fresh data from Salesforce and WhatConverts, reconciles Lead Source / Lead Medium / Lead Group, assigns Ad Cost Detail (ACD) records, and produces output files for review and Data Loader upload.

---

## Configuration (update each run)

```python
DATE_START  = 'YYYY-MM-DD'   # start of date range (inclusive)
DATE_END    = 'YYYY-MM-DD'   # end of date range (inclusive)
DATE_STAMP  = 'YYYY-MM-DD'   # used in output filenames (usually = DATE_END)
```

---

## Data Sources — pulled live each run

### Salesforce
Data is queried directly via the SF CLI (`sf data query`), not from a report export:

```sql
SELECT [lead fields]
FROM Lead
WHERE LeadGroup__c != 'Home Advisor'
  AND LeadSource NOT IN ('Angi Quote Request', 'Thumbtack')
  AND CreatedDate >= {DATE_START}T00:00:00Z
  AND CreatedDate <= {DATE_END}T23:59:59Z
```

A pre-phase runs first to assign Service Territories to leads that have a zip code but no ST (see ST Pre-Phase below).

### WhatConverts
Data is pulled via the WhatConverts REST API using stored credentials (token + secret). The API returns the same fields as the manual CSV export: `Lead ID, Lead Type, Status, Date, Source, Medium, Campaign, Email, PhoneNumber, First Name, Last Name, Zip Code`.

---

## ST Pre-Phase (runs before main pull)

Before pulling the main lead set, find leads in the date range that have a zip code but no assigned Service Territory, assign them via `Zip_Code__c` lookup (or "Out of Area" if the zip isn't mapped), and bulk-upload to SF. This ensures the main pull includes ST-enriched records.

```sql
SELECT Id, PostalCode FROM Lead
WHERE LeadGroup__c != 'Home Advisor'
  AND LeadSource NOT IN ('Angi Quote Request', 'Thumbtack')
  AND ServiceTerritory__c = null
  AND PostalCode != null
  AND CreatedDate >= {DATE_START}T00:00:00Z
  AND CreatedDate <= {DATE_END}T23:59:59Z
```

---

## SF Startup Queries (run once at script launch)

```sql
-- 1. Source → Lead Group mapping
SELECT Key__c, Value__c FROM System_Setting__mdt
WHERE Category__c = 'Lead Group Category' AND Active__c = true

-- 2. Lead Group → ACD Type mapping
SELECT Key__c, Value__c FROM System_Setting__mdt
WHERE Category__c = 'LeadGroup_AdCostDetailMapping'

-- 3. ACD records for current FY
SELECT Id, Name, ServiceTerritory__r.Name, Type__c, Month_Start__c,
       ACD_Checkover_Corp_Name__c, ACD_Checkover_ST__c
FROM AdCostDetail__c
WHERE Month_Start__c >= {fy_start} AND Month_Start__c <= {fy_end}

-- 4. Call center users (by role; any Admin-role users who create CC leads are added by name in config)
SELECT Name FROM User WHERE UserRole.Name = 'Call Center' AND IsActive = true

-- 5. Lead_Gen_Account__c picklist values (via REST describe)
GET /services/data/v60.0/sobjects/Lead/describe
```

---

## Output Files (6 per run)

| File | Purpose |
|------|---------|
| `{DATE} cbc clean-up LEAD REVIEW.xlsx` | Leads flagged for manual review by Lead Review Coordinator — pink Lead IDs |
| `{DATE} cbc clean-up QUALITY REVIEW.xlsx` | Medium-conflict leads for quality review |
| `{DATE} cbc clean-up DATALOAD.xlsx` | Full working file — pink=review, orange=ACD, yellow=changes, green=clean |
| `{DATE} dataload-leads.csv` | Lead upload: LS, LM, LG, ACD, ST, Lead Gen Account |
| `{DATE} dataload-opps.csv` | Opp upload: LS, LG, ACD |
| `{DATE} dataload-leads-lg.csv` | LG re-upload for all leads with any LS/LM/LG change |

---

## Data Loader Upload (3 jobs, in order)

```bash
sf data update bulk --sobject Lead     --file "{DATE} dataload-leads.csv"    --line-ending CRLF --target-org prod --wait 10
sf data update bulk --sobject Opportunity --file "{DATE} dataload-opps.csv"  --line-ending CRLF --target-org prod --wait 10
sf data update bulk --sobject Lead     --file "{DATE} dataload-leads-lg.csv" --line-ending CRLF --target-org prod --wait 10
```

**Why 3 jobs:** The LG re-upload (job 3) runs after LS/LM to prevent the LS+LM→LG automation from clearing LG on records that had any source/medium change.

**Data Loader setting:** Keep "Insert Null Values" **UNCHECKED** — empty cells mean no change.

---

## WC Matching Logic

- Normalize phone to 10-digit (strip +1 prefix and non-digits)
- Match SF lead → WC record by **phone first**, then **email**
- Date window: only accept a WC match within **±2 days** of SF `CreatedDate`
- **Protected sources** (skip WC match entirely):
  `Field-Generated`, `Customer Referral`, `Walk Up`, `cold call`, `Pro Referral`

### WC-Match Tiered Logic (evaluated in order)

| Priority | Condition | Action |
|----------|-----------|--------|
| 1 | Previous Customer + CC-created | → Lead Review |
| 2 | Previous Customer + non-CC | Apply Rule 1 (fill Repeat if blank); do NOT auto-update from WC |
| 3 | CC-created + blank source, OR CC-created + LS=Google with no LM/LG | Accept WC values |
| 4 | WC=GMB and SF is GMB or blank | Apply GMB logic: LS=GMB, LM=Organic, LG=GMB |
| 5 | SF source blank OR SF source == WC source | Update LM/LG from WC |
| 6 | Source conflict (SF has a real source ≠ WC) | → Lead Review |

### No-WC-Match Rules

| # | Condition | Action |
|---|-----------|--------|
| 1 | LS = Previous Customer | LM→Repeat if blank, LG→Repeat if blank. No review flag. |
| 2 | LS = Customer Referral + CC-created + no Referring Account | → Lead Review |
| 2b | LS = Customer Referral + Referring Account linked | Pass through |
| 3 | LS = Field-Generated | LM→Self-Generated if blank, LG→Self-Generated if blank |
| 4 | LS = Meta (any creator) | LM→CPC if blank, LG→Social if blank |
| 5 | CC-created or API-created (leftover after above rules) | → Lead Review (always, even if fields are filled) |
| 6 | ACD gap (no matching ACD found in SF) | → Lead Review |

---

## Source & Medium Canonicalization

### WC Source
```python
WC_SOURCE_CANONICAL = {
    'google': 'Google', 'bing': 'Bing',
    'campaignmonitor': 'Campaign Monitor', 'campaign monitor': 'Campaign Monitor',
    'meta': 'Meta', 'gmb': 'GMB', 'angi ads': 'Angi Ads',
    'home advisor': 'Home Advisor', 'ha ppl': 'HA PPL',
    'ai': 'AI', 'vehicle wrap': 'Vehicle Wrap', 'vehiclewrap': 'Vehicle Wrap',
}
# GMB detection: 'gmb' in source.lower() catches territory-prefixed names (e.g. "Miami GMB")
```

### WC Lead Medium
Strip `-` and spaces, then:

| Raw value | Canonical |
|-----------|-----------|
| `brandcpc` / `nonbrandcpc` | `CPC` |
| `cpl` | `CPL` |
| `ppl` | `PPL` |
| `organic` | `Organic` |
| `email` | `Email` |
| `(not set)` / `(none)` / blank | Keep existing SF LM (no change) |

---

## ACD Assignment Logic

ACD is matched by concatenating: `{month_num} {year} {ServiceTerritory} {ACD_type}`

- ACD type comes from `System_Setting__mdt` mapping: Lead Group → ACD type
- If no matching ACD exists → ACD gap → flag for Lead Review

### Outside-Territory Opportunities
Key: `{month} {year} {Opp Corporate Name} {Owner Assigned ST Unique Code} {ACD_type}`
- Uses `ACD_Checkover_Corp_Name__c` on ACD records
- Do NOT use `Opp.ACD_Checkover__c` formula — it uses a different unique code field

### PPP Commercial Division
Special routing for CD-owned opportunities (determined by owner name match in config):
- CD owner + ST starts with "CA" → route to CA San Diego ACD
- Other CD owners → `opp_corp = "PPP Commercial Division"` path, key against `ACD_Checkover_ST__c`

### Wallpapers Unlimited Override
WU leads are initially assigned to a PPP territorial ACD (WU ACDs have no Service Territory, so the standard key won't match). During clean-up: filter `Corporate_Name__c = 'Wallpapers Unlimited'` → allocate to WU-specific ACDs (`Notes__c = 'WALLPAPERS UNLIMITED'`).

---

## Known ACD Gaps

Territories that periodically have no ACD in SF and always route to Lead Review:
- NY Suffolk East
- FL Tampa East
- Check for new gaps before each run — new territories launching mid-month may be missing

---

## Gotchas

- **LG re-upload is required** — the LS+LM→LG automation fires on any LS or LM change and can wipe a manually-set LG. Always run job 3 after jobs 1 and 2.
- **Legacy raw SF values** (e.g. `vehiclewrap`) are treated as equivalent to their canonical picklist label — avoid re-uploading the same value to prevent no-op Data Loader rows.
- **WU ACDs have no Service Territory** — they won't appear in by-state CBC breakdowns (by design). They appear in Full Company reports.
- **`ACD_Checkover__c` on Opp is a formula** using a different unique code than the outside-territory lookup key — don't use it for ACD matching.
- **Meta leads always get CPC/Social** regardless of what WC medium says.
