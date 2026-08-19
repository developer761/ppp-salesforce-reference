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

## Post-Run QA (read before uploading)

A read-only QA step runs automatically at the end of the clean-up (and can be re-run standalone on any past run's output). It compares the current run's DATALOAD against the most recent prior runs (default: last 5) and surfaces anything out of the ordinary **before** the Data Loader upload.

**Checks:**
- **Change-rate table** — for every `*NEW …` change column, the count and per-1,000-leads rate this run, next to the median rate of the prior runs, flagged `SPIKE` (rate ≥ 1.5× median) or `drop` (≤ 0.5× median). A noise floor (minimum absolute count) suppresses flags on tiny columns.
- **Driver breakdown** — for each flagged column, the top old→new value transitions and the Lead Source distribution of the changed rows, so a spike points at its *cause*, not just its size.
- **No-op writes** — changes where the old value already equals the new (case-insensitive). Must be 0; anything else is a script bug (e.g. a case-only difference written needlessly).
- **Internal-record sanity** — records created by internal/admin test accounts must carry zero changes (they are ignored, and their ACD is cleared separately). Must be 0.
- **Verdict** — a flagged spike is usually an upstream data change, not a clean-up bug.

**Known limitation — the rate is normalised against the wrong denominator.** The per-1,000
rate divides by *every* lead in the window, not by the leads that still needed cleaning.
Because the window is a fixed rolling 30 days, running sooner than the usual interval means
most rows were already cleaned and uploaded on the previous run, so they legitimately produce
no changes — and every column reads as a `drop` even though nothing changed.

Worked example: a run made 6 days after the prior one had 78% of its window already cleaned.
The headline table showed drops of 0.1×–0.4× across every column. Splitting the window at the
prior run's end date showed leads created since then changing at 555.6 per 1,000 versus 566.2
per 1,000 on the prior run — flat. Nothing had dropped; the denominator had grown with
already-clean rows.

Before treating a broad drop as real, split the window at the prior run's end date and compare
the change rate of the *new* segment only. Uniform drops across every column point at cadence;
a genuine data change is almost never that even.

**Why it matters (worked example):** one run showed lead-medium changes at nearly double the usual rate. The driver breakdown pinned it to a large block of paid-social leads arriving with a blank Lead Medium and being backfilled to the paid-click medium — all from one source, no collateral on other sources. The clean-up was behaving correctly; the real signal was upstream — the ad-platform → CRM integration had stopped populating Lead Medium. Without the QA step this reads as a normal run; with it, the upstream issue is visible the same day.

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
- Leads created by **Vendor - WU team creators** (configured by name in script) — their leads always get WU values regardless of WC
- Leads created by a **second affiliate vendor team** (configured by name in script, separate from WU) — their leads always get their affiliate LS values regardless of WC
- Leads created by **field users** (Profile `*Standard.Field` + hardcoded names) — field-created leads get the field rule applied, not a WC override, **regardless of whether SF LS is already populated**

  > This suppression used to be conditional on SF LS being *blank*. That guard silently
  > stopped working once the native WC→CRM integration began back-filling
  > LS/LM/LG/ad-cost-detail within hours of lead creation: by the time the bi-weekly
  > clean-up ran, the source was never blank, so field-generated leads were being
  > attributed to paid and organic marketing channels and consuming that channel's ad-cost
  > record. The creator now wins outright — an automated back-fill does not outrank the
  > human who created the lead. Sources handled by earlier rules (Previous Customer,
  > the vendor/affiliate sources, Customer Referral) are unaffected, since those branches
  > are evaluated before the field rule.
- Leads where **downstream work order evidence** confirms a vendor relationship on the converted opportunity (crew attendance or Payment Out transaction) — these are detected via a startup query even when the login on the record is not a designated vendor team account; WC is suppressed and vendor values are applied. This detection runs for each configured affiliate vendor (currently two: WU and a second affiliate).

  > **Gate each vendor's detection behind its own switch rather than deleting it.** Whether this
  > detection is wanted is a business call, not a technical one, and it can be reversed by the
  > people who own the vendor relationship. One of the two configured vendors has had its
  > detection switched **off** by operational ruling while the other stays on — so the switch is
  > per-vendor, defaulted in code, and the retired branch is left intact behind it. Deleting the
  > branch instead would mean rebuilding it from scratch on reversal, and would silently drop the
  > accompanying attribution corrections along with the review flag.
  >
  > Note what a switch like this takes down with it. The same detection flag usually drives more
  > than the review queue — here it also forces the vendor `LeadSource`/medium/group, routes to the
  > vendor ACD, and suppresses the WhatConverts match. Turning it off returns those leads to
  > ordinary WC attribution, which **moves reported channel numbers**; it is not a review-noise
  > change. Confirm the requester means the attribution too, not just the follow-up flag.

  > **Key the detection on the opportunity OWNER, not the creator.** Reassignment is an
  > ownership action, and coordinators routinely create the lead on the vendor principal's
  > behalf — so creator-only detection goes blind exactly where the vendor principal did not
  > key the record in himself. Retain the creator as an additional trigger so nothing
  > previously detected regresses. Raise the owner-reassignment review flag **only when the
  > opportunity is still on the non-vendor login**; once it has been reassigned there is
  > nothing to action, and flagging it again is noise.
  >
  > Two limits worth stating plainly. First, **crew or payment evidence proves who performed
  > the work, not who sourced the lead** — a house lead subcontracted to a vendor crew looks
  > identical to a vendor-sourced one, so this is strong evidence rather than proof, and it is
  > a weaker claim for records carrying a real paid marketing source. Second, the clean-up
  > runs on a **rolling 30-day window**, so any backlog older than that window will never
  > surface in a routine run and has to be worked from a one-off query.

Matching itself: normalize phone to 10-digit (strip +1 and non-digits), match by phone first then email, within **±2 days** of SF `CreatedDate`.

---

## WC-Match Tiered Logic (evaluated in order)

| Priority | Condition | Action |
|----------|-----------|--------|
| 1 | SF LS = Previous Customer + CC-created + WC LS ≠ `(direct)` | → Lead Review |
| 1 (exception) | SF LS = Previous Customer + CC-created + WC LS = `(direct)` | Apply Repeat fills (same as Tier 2); no review flag |
| 2 | SF LS = Previous Customer + non-CC | Fill SF LM→Repeat if blank, SF LG→Repeat if blank; do NOT auto-update from WC |
| 3 | CC-created + SF LS blank, OR CC-created + SF LS=Google with no SF LM/LG | Accept WC LS/LM/LG values |
| 4 | WC LS is GMB **or a location name** (normalized — see below) AND WC LM = organic, and (SF LS is GMB-ish, OR SF LS is blank) | Set SF LS=GMB, SF LM=Organic, SF LG=GMB |
| 5 | SF LS is blank (non-CC, non-field-user — field-created leads have WC match blocked upstream and never reach any tier) | Set SF LS/LM/LG from WC |
| 5b | SF LS == WC LS AND (SF LM is blank OR SF LM == WC LM) | Update SF LM/LG from WC |
| 5b (conflict) | SF LS == WC LS but SF LM ≠ WC LM (both populated) | → Lead Review for medium conflict |
| 6 | Source conflict + creator is known Meta creator (either side says Meta) | Apply Meta values: SF LS=Meta, SF LM=CPC, SF LG=Social |
| 6 (legacy platform) | Source conflict + CC-created + SF LS is the legacy platform name (`Facebook` / `Instagram`) + WC LS = Meta | Accept WC: SF LS=Meta, SF LM=CPC, SF LG=Social. No review flag |
| 6 (web-form) | Source conflict + lead created by the web-to-lead API endpoint + SF LS is Meta or an Angi variant | Keep the SF source; correct SF LM/LG to match it. No review flag |
| 6 | All other source conflicts | → Lead Review |

**Why the legacy-platform exception:** the two social platforms were folded into a single
advertising brand, and WhatConverts reports the current brand name while coordinators still
type the older platform names by hand. Both labels describe the same channel, so this is a
naming lag rather than a genuine attribution disagreement — the WC value is applied.

⚠️ **The two "6" exceptions point in opposite directions and must not be merged.** The
legacy-platform rule *accepts* WC and is scoped to **CC-created** leads; the web-form rule
*keeps* the SF source and is scoped to **API-created** leads, where the legacy platform names
are explicitly excluded. Same source values, opposite handling, decided by creator type.

**Why the web-form exception:** a lead created by the web-to-lead API endpoint means the
customer submitted a form, and the endpoint stamps `LeadSource` from that form. That is
first-party, self-reported attribution and outranks WhatConverts' session/referrer
inference, so the SF value is kept rather than sent for review.

Scope is deliberately limited to Meta plus Angi-family sources (matched on an `angi`
prefix, which covers the several spelling variants in the picklist). It is **not** applied
to every API-created lead — the reasoning generalizes, but the approved scope does not.
`(direct)` is outside the exception by construction: it means the endpoint captured *no*
attribution, so there is nothing first-party to preserve, and those still go to review.

---

## No-WC-Match Rules (evaluated in order)

| # | Condition | Action |
|---|-----------|--------|
| 1 | SF LS = Previous Customer | SF LM→Repeat if blank, SF LG→Repeat if blank. No review flag. |
| 2 | Vendor - WU creator, OR SF LS = `Vendor - WU` (any creator) | SF LS=Vendor - WU, SF LM=Referral, SF LG=Other Marketing |
| 2b | Second affiliate vendor creator, OR downstream WO evidence confirms that affiliate's relationship, OR SF LS = that affiliate's LS value (any creator) | SF LS=[affiliate LS], SF LM=Referral, SF LG=Other Marketing. **No ACD assigned** — this affiliate is intentionally excluded from cost/corp reporting. |
| 3 | SF LS = Customer Referral + CC-created + no Referring Account | → Lead Review |
| 3b | SF LS = Customer Referral + Referring Account linked (field-gen referral) | Pass through; update SF LM→Referral if blank, SF LG→Referral if blank |
| 3c | Lead created by a known strategic-outreach creator + SF LS = Strategic Outreach | Keep SF LS = Strategic Outreach; SF LM→Organic, SF LG→Other Marketing. **Must be evaluated before rule 4** — see the ordering note below. |
| 4 | SF LS = Field-Generated, OR **any** lead created by a field user | Force SF LS=Field-Generated (overwriting a back-filled marketing source), SF LM→Self-Generated, SF LG→Self-Generated. The ad-cost-detail lookup then re-points to that territory/month's **self-gen/repeat** record instead of the paid or organic one. |
| 5 | SF LS in fixed-override sources (e.g. `chatgpt.com`) | Apply fixed SF LM/LG values for that source (e.g. chatgpt.com → LM=Referral, LG=AI) |
| 6 | SF LS = Meta, OR lead created by known Meta creator | SF LM→CPC if blank, SF LG→Social if blank |
| 7 | Lead created by known marketing creator + SF LS blank | → Lead Review |
| 7 | Lead created by known marketing creator + SF LS = Meta | SF LM→CPC, SF LG→Social |
| 8 | CC-created or API-created (reached here with no prior rule matching) | → Lead Review (always, even if SF LM/LG are filled) |
| 9 | SF LS blank + no creator rule matched | → Lead Review |
| 10 | ACD gap (no matching ACD found in SF for territory + month + type) | → Quality Review |
| 11 | **Catch-all (runs after all rules):** any lead or opp still missing LS, LM, or LG after processing | → Lead Review with list of missing fields |
| 11b | **Catch-all:** any lead or opp still missing ACD after processing | → Quality Review with list of missing ACD fields |

**Ordering note — rule 3c must precede rule 4.** The set of field users is built by unioning a
small hardcoded creator list with a live query for the field profile, and at least one
strategic-outreach creator also carries that profile. Rule 4 fires on *any* lead created by a
field user regardless of the existing source, so if 3c sits below it, rule 4 swallows every
Strategic Outreach lead that creator enters and rewrites it to Field-Generated /
Self-Generated. This is a real regression introduced when rule 4 dropped its "only if the source
is blank" guard — the two changes are safe individually and harmful together. Any future rule
that keys on *creator* rather than *source* has the same hazard: place it below every
source-specific rule it could shadow.

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
}
```

### Location-named GMB sources — normalize, don't enumerate

A Google Business Profile listing reaches the call-tracking platform under the **listing's location
name**, not as "GMB". The same listing arrives under four spellings — `San Diego`, `San_Diego`,
`san-diego`, `gmb-san-diego` — and both lookup tables (the canonical-source dict and the
`System_Setting__mdt` Lead-Group keys) are **exact-match**, so a table entry written with an
underscore silently misses the space form and vice versa.

**Normalize both sides before comparing:** lowercase → collapse every run of `_`, `-` and
whitespace to a single space → strip a leading `gmb ` or trailing ` gmb` → trim.

The rule, in full:

> **location name (or `gmb` anywhere in the source) AND medium = organic → `GMB` / `Organic` / `GMB`**

The Lead **Source** becomes `GMB` — not the location name. Every listing is the same channel; the
location is how the lead arrived, not what sourced it.

**Enforce the organic gate.** Measured across all GMB leads in production, 4,289 of 4,295 are
organic (the remainder are one each of `cpl` / `email` / `referral` plus three blanks). Gating on
organic therefore costs nothing and stops a paid medium being overwritten by the location rule. A
location source arriving with a non-organic medium should be **flagged**, not auto-applied.

**Flag unrecognized organic sources rather than dropping them.** The location roster cannot be
derived from Service Territory — many listings are finer-grained than a territory — so it has to be
maintained as listings are added. When the medium is organic and the source is neither a known
marketing channel nor a website domain, it is most likely a new listing: route it to review. Without
this catch-all, a new listing lands with a **blank Lead Group** and is invisible; that omission
produced a backlog of ~100 leads with a location source, organic medium and no Lead Group at all.

⚠️ **Use one shared GMB test everywhere.** The detection previously existed in three variants — a
substring check, a canonical-dict lookup, and a combination — and the *narrowest* one drove the
review flag. Because the open-items ledger increments a rule only when that flag fires, the defect
suppressed the evidence of its own recurrence: the item read "not seen in 4 runs — confirm before
closing" while it was still firing. **A detector narrower than the decision it reports on will
always under-count itself**, and a staleness signal computed from it is not independent
confirmation.

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
2. Vendor - WU routing (WU corp name on opp, or WU team as opp owner)
3. Outside-territory: `{month} {year} {Opp Corp Name} {Owner Assigned ST Unique Code} {ACD_type}` — looked up via `ACD_Checkover_Corp_Name__c`
4. Inside-territory: `{month} {year} {Lead ST} {ACD_type}` — same key as lead ACD

### PPP Commercial Division Routing
Applies when the opp owner (or lead creator for unconverted leads) is a CD team member (configured by name in script):
- CD owner + lead ST starts with "CA" → route to CA San Diego ACD
- Other CD owners → `opp_corp = "PPP Commercial Division"` path, key against `ACD_Checkover_ST__c`

### Vendor - WU ACD
Vendor - WU ACDs are identified by a stable tag in `Notes__c` (set directly on ACD records; stable across corp account renames). Key: `{month} {year} {ACD_type}` — no ST component.

### Second Affiliate Vendor — No ACD
Unlike WU, a second affiliate vendor is **intentionally excluded from ACD assignment and cost/corp reporting**. No ACD lookup is performed; no ACD gap flag is raised. Lead and opp ACD fields are left blank for all records flagged to this affiliate, regardless of creator or detection path.

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
- **The wallpaper subsidiary's ACDs are matched on a notes tag, not on territory** — the durable lookup key is a fixed marker string on the ACD's notes field, set by hand on each new monthly ACD. Historically these ACDs carried no Service Territory; they now do carry a dedicated one, so do **not** write logic that assumes the territory is empty. Match on the notes tag. Also do not match on the corporate account name — that entity has been renamed once already, which silently stranded leads on the wrong ACD until it was caught.
- **`ACD_Checkover__c` on Opp is a formula** that produces the same value as `ACD_Checkover_Corp_Name__c` on the ACD record. The outside-territory lookup already handles this matching correctly, so the field isn't needed for assignment — but comparing `Opp.ACD_Checkover__c` to the assigned ACD's `ACD_Checkover_Corp_Name__c` can serve as a post-assignment sanity check.
- **Opp upload batch conflicts on ACD** — a process (`Opportunity.AdCostDetailUpdate`) fires on ACD changes and SF limits updates to the same ACD record to 12 per batch. When many opps share the same ACD, some will fail with `DUPLICATE_VALUE`. Fix: extract the failed records from the SF bulk results file and retry them as a small standalone batch — the smaller batch stays within the limit.
- **`Lead_Medium__c` case-normalization on write** — SF silently lowercases values written to this picklist (e.g., a bulk update of `CPC` lands as `cpc`; `Referral` lands as `referral`). `LeadGroup__c` and `LeadSource` do **not** auto-normalize — they store exactly what you write. Not a bug — script output for LM can use any case; SF handles it. Just don't rely on LM case downstream (query filters, comparisons) — normalize to lowercase.