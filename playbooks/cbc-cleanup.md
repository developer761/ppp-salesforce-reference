# Playbook — CBC / WhatConverts Lead Clean-Up

Bi-weekly process that pulls fresh data from Salesforce and WhatConverts, reconciles Lead Source / Lead Medium / Lead Group, assigns Ad Cost Detail (ACD) records, and produces output files for manual review and Data Loader upload.

---

## Configuration

The script calculates the date window automatically at runtime using a rolling 30-day window (today minus 30 days → today). No manual date changes are needed before running.

To override for a custom range, set these at the top of the script:

```python
DATE_START  = 'YYYY-MM-DD'   # start of date range (inclusive)
DATE_END    = 'YYYY-MM-DD'   # end of date range (inclusive)
DATE_STAMP  = 'YYYY-MM-DD'   # used in output filenames (usually = DATE_END)
```

---

## Excluded Sources

The following are intentionally excluded and require no processing:

| Excluded | Reason |
|----------|--------|
| `LeadGroup__c = 'Home Advisor'` | HA leads come in with correct source/medium pre-populated via the HA platform integration; they have no WhatConverts tracking and are already clean |
| `LeadSource = 'Angi Quote Request'` | Angi QR leads arrive directly from Angi (not through WC tracking), consistently land with `LG=Angi Ads, LM=ppl` already set, and have no WC match to update against |
| `LeadSource = 'Thumbtack'` | Same pattern as Angi QR — direct platform intake, no WC presence |

If any of these sources start showing up with ACD gaps or blank LM/LG, revisit the exclusion.

---

## Data Sources — pulled live each run

### Salesforce
Queried directly via SF CLI (`sf data query`). Main pull filters out leads with no Service Territory (those are handled in the ST Pre-Phase first):

```sql
SELECT [lead fields + converted opp fields]
FROM Lead
WHERE LeadGroup__c != 'Home Advisor'
  AND LeadSource NOT IN ('Angi Quote Request', 'Thumbtack')
  AND ServiceTerritory__c != null
  AND CreatedDate >= {DATE_START}T00:00:00Z
  AND CreatedDate <= {DATE_END}T23:59:59Z
```

Converted opportunities are pulled in a second query (joined via `ConvertedOpportunityId`) to populate opp-level LS/LG/ACD columns.

### WhatConverts
Pulled via the WhatConverts REST API (`app.whatconverts.com/api/v1/leads`) using stored credentials (token + secret), paginated. Returns: `Lead ID, Lead Type, Status, Date, Source, Medium, Campaign, Email, Phone Number, First Name, Last Name, Zip Code`.

---

## ST Pre-Phase (runs before main pull)

Find leads in the date range that have a zip code but no Service Territory, assign ST via `Zip_Code__c` lookup (or "Out of Area" if the zip isn't mapped), and bulk-upload to SF before the main pull runs.

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
       ACD_Checkover_Corp_Name__c, ACD_Checkover_ST__c, Notes__c
FROM AdCostDetail__c
WHERE Month_Start__c >= {fy_start} AND Month_Start__c <= {fy_end}

-- 4. Call center users (by role; specific Admin-role users who create CC leads added by name in config)
SELECT Name FROM User WHERE UserRole.Name = 'Call Center' AND IsActive = true

-- 5. Field users (by profile — unioned with hardcoded field creator names in config)
--    Field users whose profile differs from the standard field profile must be added
--    to the hardcoded config set; they won't be picked up by this query.
SELECT Name FROM User WHERE Profile.Name = '*Standard.Field' AND IsActive = true

-- 6. Lead_Gen_Account__c picklist values (via REST describe)
GET /services/data/v60.0/sobjects/Lead/describe

-- 7. Vendor relationship detection via downstream work order evidence
--    At startup, the script queries won opportunities linked to leads created by a
--    non-vendor-team login. For each candidate opp, it checks WorkOrderCrew__c
--    (crew attendance) and Transaction__c (Payment Out) records via
--    WorkOrder__r.Opportunity__c. Opps with matching evidence are flagged; their
--    leads receive vendor-team treatment (WC suppressed, vendor LS/LM/LG/ACD applied)
--    and are also routed to Quality Review for owner reassignment follow-up.
SELECT WorkOrder__r.Opportunity__c FROM WorkOrderCrew__c
WHERE CrewName__c LIKE '%[Vendor]%' AND WorkOrder__r.Opportunity__c IN (:candidate_opp_ids)

SELECT WorkOrder__r.Opportunity__c FROM Transaction__c
WHERE RecordType.Name = 'Payment Out'
  AND Payee__r.Name LIKE '%[Vendor]%'
  AND WorkOrder__r.Opportunity__c IN (:candidate_opp_ids)
```

---

## Output Files (6 per run)

| File | Purpose |
|------|---------|
| `{DATE} cbc clean-up LEAD REVIEW.xlsx` | Leads flagged for manual review by Lead Review Coordinator — pink Lead IDs |
| `{DATE} cbc clean-up QUALITY REVIEW.xlsx` | Leads routed for admin review: ACD gaps (no matching ACD in SF for territory + month + type), missing ACD after all processing, WC source accepted but no LG mapping exists, and leads where downstream WO evidence confirms a vendor relationship requiring owner reassignment |
| `{DATE} cbc clean-up DATALOAD.xlsx` | Full working file — pink=review, orange=ACD, yellow=changes, green=clean |
| `{DATE} dataload-leads.csv` | Lead upload: LS, LM, LG, ACD, ST, Lead Gen Account |
| `{DATE} dataload-opps.csv` | Opp upload: LS, LG, ACD |
| `{DATE} dataload-leads-lg.csv` | LG re-upload for all leads with any LS/LM/LG change |

---

## Data Loader Upload (3 jobs, in order)

```bash
sf data update bulk --sobject Lead        --file "{DATE} dataload-leads.csv"    --line-ending CRLF --target-org prod --wait 10
sf data update bulk --sobject Opportunity --file "{DATE} dataload-opps.csv"     --line-ending CRLF --target-org prod --wait 10
sf data update bulk --sobject Lead        --file "{DATE} dataload-leads-lg.csv" --line-ending CRLF --target-org prod --wait 10
```

**Why 3 jobs:** The LG re-upload (job 3) runs after LS/LM to prevent the LS+LM→LG automation from clearing LG on records that had any source/medium change.

**Data Loader setting:** Keep "Insert Null Values" **UNCHECKED** — empty cells mean no change.

---

## WC Match Blocking

WC match is suppressed entirely (treated as no-match) for:
- Any lead whose SF LS is in the **protected sources** list: `Field-Generated`, `Customer Referral`, `Walk Up`, `cold call`, `Pro Referral`
- Leads created by **Wallpaper Unlimited team creators** (configured by name in script) — their leads always get WU values regardless of WC
- Leads created by **field users** (Profile `*Standard.Field` + hardcoded names) where SF LS is blank — field users with a blank source get Rule 3 applied, not a WC override
- Leads where **downstream work order evidence** confirms a vendor relationship on the converted opportunity (crew attendance or Payment Out transaction) — these are detected via a startup query even when the creator login is not a designated vendor team account; WC is suppressed and vendor values are applied

Matching itself: normalize phone to 10-digit (strip +1 and non-digits), match by phone first then email, within **±2 days** of SF `CreatedDate`.

---

## WC-Match Tiered Logic (evaluated in order)

| Priority | Condition | Action |
|----------|-----------|--------|
| 1 | SF LS = Previous Customer + CC-created + WC LS ≠ `(direct)` | → Lead Review |
| 1 (exception) | SF LS = Previous Customer + CC-created + WC LS = `(direct)` | Apply Repeat fills (same as Tier 2); no review flag |
| 2 | SF LS = Previous Customer + non-CC | Fill SF LM→Repeat if blank, SF LG→Repeat if blank; do NOT auto-update from WC |
| 3 | CC-created + SF LS blank, OR CC-created + SF LS=Google with no SF LM/LG | Accept WC LS/LM/LG values |
| 4 | WC LS = GMB and (SF LS is GMB, OR SF LS is blank) | Set SF LS=GMB, SF LM=Organic, SF LG=GMB |
| 5 | SF LS is blank (non-CC, non-field-user — field users with blank LS have WC match blocked upstream and never reach this tier) | Set SF LS/LM/LG from WC |
| 5b | SF LS == WC LS AND (SF LM is blank OR SF LM == WC LM) | Update SF LM/LG from WC |
| 5b (conflict) | SF LS == WC LS but SF LM ≠ WC LM (both populated) | → Lead Review for medium conflict |
| 6 | Source conflict + creator is known Meta creator (either side says Meta) | Apply Meta values: SF LS=Meta, SF LM=CPC, SF LG=Social |
| 6 | All other source conflicts | → Lead Review |

---

## No-WC-Match Rules (evaluated in order)

| # | Condition | Action |
|---|-----------|--------|
| 1 | SF LS = Previous Customer | SF LM→Repeat if blank, SF LG→Repeat if blank. No review flag. |
| 2 | Wallpaper Unlimited creator, OR SF LS = `Wallpaper Unlimited` (any creator) | SF LS=Wallpaper Unlimited, SF LM=Referral, SF LG=Other Marketing |
| 3 | SF LS = Customer Referral + CC-created + no Referring Account | → Lead Review |
| 3b | SF LS = Customer Referral + Referring Account linked (field-gen referral) | Pass through; update SF LM→Referral if blank, SF LG→Referral if blank |
| 4 | SF LS = Field-Generated, OR field creator + SF LS blank | SF LS=Field-Generated if blank; SF LM→Self-Generated if blank, SF LG→Self-Generated if blank |
| 5 | SF LS in fixed-override sources (e.g. `chatgpt.com`) | Apply fixed SF LM/LG values for that source (e.g. chatgpt.com → LM=Referral, LG=AI) |
| 6 | SF LS = Meta, OR lead created by known Meta creator | SF LM→CPC if blank, SF LG→Social if blank |
| 7 | Lead created by known marketing creator + SF LS blank | → Lead Review |
| 7 | Lead created by known marketing creator + SF LS = Meta | SF LM→CPC, SF LG→Social |
| 7 | Lead created by known marketing creator + SF LS = Strategic Outreach | SF LM→Organic, SF LG→Other Marketing |
| 8 | CC-created or API-created (reached here with no prior rule matching) | → Lead Review (always, even if SF LM/LG are filled) |
| 9 | SF LS blank + no creator rule matched | → Lead Review |
| 10 | ACD gap (no matching ACD found in SF for territory + month + type) | → Quality Review |
| 11 | **Catch-all (runs after all rules):** any lead or opp still missing LS, LM, or LG after processing | → Lead Review with list of missing fields |
| 11b | **Catch-all:** any lead or opp still missing ACD after processing | → Quality Review with list of missing ACD fields |

---

## Source & Medium Canonicalization

### WC Source
WC source strings are normalized to their SF Lead Source picklist equivalents before comparison or update:

```python
WC_SOURCE_CANONICAL = {
    'google': 'Google', 'bing': 'Bing',
    'campaignmonitor': 'Campaign Monitor', 'campaign monitor': 'Campaign Monitor',
    'meta': 'Meta', 'gmb': 'GMB', 'angi ads': 'Angi Ads',
    'home advisor': 'Home Advisor', 'ha ppl': 'HA PPL',
    'vehicle wrap': 'Vehicle Wrap', 'vehiclewrap': 'Vehicle Wrap',
    # chatgpt.com passes through unchanged; LG=AI is set via fixed-override, not LS
    # Territory-named GMB: WC sends geographic names without 'GMB' in the string,
    # so the 'gmb' substring check misses them — hardcoded here:
    'dallas': 'GMB', 'dallas collin': 'GMB', 'dallas denton': 'GMB',
    'hudson essex': 'GMB', 'long island': 'GMB',
    'los_angeles': 'GMB', 'manhattan_north': 'GMB', 'miami': 'GMB',
    'middlesex_monmouth': 'GMB', 'orlando': 'GMB', 'queens': 'GMB',
    'san_diego': 'GMB', 'suffolk southwest': 'GMB', 'union middlesex': 'GMB',
    'bocaraton': 'GMB', 'garden-city': 'GMB',
}
```

GMB detection also uses: `'gmb' in source.lower()` to catch territory-prefixed names like "Miami GMB" or "Bergen GMB".

The same canonicalization is applied to the **SF LS value** when comparing it to WC LS. If the SF value and the canonical form differ beyond capitalization (e.g., `vehiclewrap` vs `Vehicle Wrap`), the SF LS is updated to the canonical form. Case-only differences (e.g., `gmb` vs `GMB`) are treated as equivalent and left unchanged.

### WC Lead Medium
Strip `-` and spaces, then:

| Raw value | Canonical |
|-----------|-----------|
| `brandcpc` / `nonbrandcpc` | `CPC` |
| `localservicescpl` | `CPL` |
| `cpl` | `CPL` |
| `ppl` | `PPL` |
| `organic` / `orgnaic` | `Organic` |
| `email` | `Email` |
| `(not set)` / `(none)` / blank | Keep existing SF LM (no change) |

### Fixed-Override Sources
Some SF Lead Sources have hardcoded LM/LG values applied regardless of WC data:

| SF LS | Fixed LM | Fixed LG |
|-------|----------|----------|
| `chatgpt.com` | `Referral` | `AI` |
| `duckduckgo.com` | `Referral` | `Other Marketing` |
| `paintersloc.com` | `Referral` | `Other Marketing` |
| `reddit.com` | `Referral` | `Other Marketing` |

---

## ACD Assignment Logic

### Lead ACD
Key: `{month_num} {year} {ServiceTerritory} {ACD_type}`

- ACD type from `System_Setting__mdt`: Lead Group → ACD type
- If no ACD found for that territory + month + type → **flag for Quality Review** (ACD gap)
- No fallback to Out of Area — an ACD gap always routes to review

### Opp ACD (for converted leads)
Converted opps are processed alongside their lead. The opp's LS/LG/ACD are synced to match the lead's effective (post-correction) values. Opp ACD routing follows the same priority as lead ACD:

1. PPP Commercial Division routing (see below)
2. Wallpapers Unlimited routing (WU corp name on opp, or WU team as opp owner)
3. Outside-territory: `{month} {year} {Opp Corp Name} {Owner Assigned ST Unique Code} {ACD_type}` — looked up via `ACD_Checkover_Corp_Name__c`
4. Inside-territory: `{month} {year} {Lead ST} {ACD_type}` — same key as lead ACD

### PPP Commercial Division Routing
Applies when the opp owner (or lead creator for unconverted leads) is a CD team member (configured by name in script):
- CD owner + lead ST starts with "CA" → route to CA San Diego ACD
- Other CD owners → `opp_corp = "PPP Commercial Division"` path, key against `ACD_Checkover_ST__c`

### Wallpapers Unlimited ACD
WU ACDs are identified by `Notes__c` containing `'WALLPAPERS UNLIMITED'` (stable across corp account renames). Key: `{month} {year} {ACD_type}` — no ST component.

---

## Lead Gen Account (Meta leads only)

For Meta leads where WC provides a campaign name, the script attempts to populate `Lead_Gen_Account__c` by fuzzy-matching the WC campaign string against the SF picklist values. If a close match is found, it's applied automatically; ambiguous cases prompt for manual confirmation at runtime.

---

## Known ACD Gaps

Territories that periodically have no ACD and always route to Lead Review:
- NY Suffolk East
- FL Tampa East
- A small number of newer territories (~5 or fewer) receive ACDs created month-by-month rather than in advance; these will surface as ACD gaps when the ACD hasn't been created yet for the current month. Check for these before each run and confirm with whoever manages ACDs if unexpected territories are missing.

---

## Gotchas

- **Inactive service territories route to Out of Area** — leads can exist in SF under a service territory that has since been deactivated. Because inactive STs are excluded from the zip code → territory mapping, those leads will never receive a valid ACD for their original territory. The script detects this at runtime by querying `ServiceTerritory WHERE IsActive = false` and automatically reroutes any such lead to the Out of Area territory and its corresponding ACD. The `*NEW ST` column is populated so the territory is corrected on upload.
- **LG re-upload is required** — the LS+LM→LG automation fires on any LS or LM change and can wipe a manually-set LG. Always run job 3 after jobs 1 and 2.
- **Catch-all fires last** — after all rules run, any lead or opp still missing LS, LM, LG, or ACD is flagged with a list of the missing fields. This catches edge cases no specific rule covers (e.g. a lead with a known LS but blank LM/LG that fell through uncorrected).
- **WU ACDs have no Service Territory** — they won't appear in by-state CBC breakdowns (by design). They appear in Full Company reports.
- **`ACD_Checkover__c` on Opp is a formula** that produces the same value as `ACD_Checkover_Corp_Name__c` on the ACD record. The outside-territory lookup already handles this matching correctly, so the field isn't needed for assignment — but comparing `Opp.ACD_Checkover__c` to the assigned ACD's `ACD_Checkover_Corp_Name__c` can serve as a post-assignment sanity check.
- **Opp upload batch conflicts on ACD** — a process (`Opportunity.AdCostDetailUpdate`) fires on ACD changes and SF limits updates to the same ACD record to 12 per batch. When many opps share the same ACD, some will fail with `DUPLICATE_VALUE`. Fix: extract the failed records from the SF bulk results file and retry them as a small standalone batch — the smaller batch stays within the limit.