# Playbook — BMCR Monthly Reconciliation

Monthly reconciliation of PPP's Benjamin Moore Contractor Rewards (BMCR) 365-report against Salesforce transactions. Automates matching, classification, SF updates, and review packet generation.

**Status:** Live (first production run 2026-06)  
**Process doc (source of truth for business rules):** Internal Google Drive — "BMCR Process" doc

> **Updated 2026-07-10 — reconciliation + write flow rebuilt.** Each transaction now routes to
> *reconcile* (increases only) or *review* (with a flag); nothing is silently dropped. Fuzzy-vendor
> matches are gated at **≥90% string similarity**. The monthly run **never auto-writes to Salesforce** —
> it produces a review packet with an Approve column, and writes happen only via an explicit apply step.
> See "Reconciliation decision tree" and "Audit gate" below.

---

## What it does

On the 5th of each month (±4 days), a launchd job fires the reconciliation script. The script:

1. **Step 0** — Auto-fetches the latest `BMC Products_*.xlsx` from the designated Drive folder
2. Fetches the current month's BMCR 365 Report CSV from Drive folder "BMCR YTD Reports" (Gmail fallback)
3. Pulls all BMCR-eligible `Transaction__c` records from SF production via SOQL
4. Matches BMCR rows to SF transactions via six priority paths (each row labeled with its tier):
   - Confirmation number
   - Reference ID / invoice number (with W↔VV mis-OCR variant)
   - Exact Amount + Date + Vendor
   - Amount + Date + fuzzy Vendor (**gated at ≥90% string similarity**; score shown in review)
   - Vendor + Amount (1-day date guard)
   - Submission ID + Amount (last resort — unique amount only)
5. Routes each row to *reconcile* or *review* (see "Reconciliation decision tree"), then classifies the reconcile rows through the decision-rule tree
6. Phase 3a: searches the receipts inbox for manual_research rows by invoice number
7. Phase 3b: processes unmatched BMCR rows — Stein Paint / BM National rows use SOSL document lookup (identifies both the BM National tx and the matching Stein tx); all other vendors use SOQL (full vendor name, exact amount, date ±1 day); prior-month carry-forwards annotated NTA
8. Invokes the PDF scorer for Dbl_Check rows
9. Generates the review packet xlsx (incl. the audit-gate tabs) + uploads to Drive `/BMCR Recon/` (sf_tx_before.csv snapshot taken first)
10. **Does not write to SF** — the run stages proposed writes only; a human reviews the packet and runs the apply step to write approved rows (see "Audit gate")
11. Posts run summary via Slack

---

## Salesforce object

**Object:** `Transaction__c`  
**Report:** "BMCR All Transactions for Reconciliation"  
**SOQL date range:** Feb 1 of prior FY – Jan 31 of next FY end (current + prior PPP fiscal year)  
**Filter:** `RetailVendor__r.VendorBMRetailer__c = true` AND `Amount__c > 0` AND `RecordType.Name = 'Purchase'`

### Key BMCR fields on Transaction__c

| Field | API Name |
|---|---|
| BMCR Confirmation Number | `BMCR_Confirmation_Number__c` |
| BMCR Submission ID | `BMCR_Submission_ID__c` |
| BMCR Status | `BMCR_Status__c` |
| BMCR Dollar Amount | `BMCR_DollarAmount__c` |
| BMCR Points Earned | `BMCR_PointsEarned__c` |
| BMCR Date Submitted | `BMCR_DateSubmitted__c` |
| BMCR Notes | `BMCR_Notes__c` |

### BMCR_Status__c picklist values (SF API names — exact casing required)

| Value | Meaning |
|---|---|
| `Approved` | Confirmed, fully processed |
| `Submitted` | Pending BM processing |
| `Dbl_Check` | Needs secondary review |
| `No Points Awarded` | BM denied points (spaces, not underscores) |
| `Rejected` | Rejected submission |
| `No_Paint` | Not a qualifying paint purchase |
| `No_Receipt` | No receipt on file |

> **Critical:** `No Points Awarded` uses spaces. Using underscores (`No_Points_Awarded`) will cause bulk write failures — SF restricted picklist rejects the value.

---

## Reconciliation decision tree (2026-07-10)

Every SF transaction routes to **reconcile** or **review** — nothing is silently dropped. Date basis
is the **SF transaction date**; age thresholds: old = ≥ 350 days, very recent = ≤ 14 days.

```
Match (conf# → ref/invoice → amt/vendor tiers):
├─ BMCR row NOT rejected                     → reconcile (usual checks; increases only)
└─ BMCR row = Rejected:
     ├─ SF = Submitted                       → reconcile (record the rejection)
     └─ SF ≠ Submitted:
          ├─ age ≥ 350d                       → review "Potential drop - SF [status] + ≥350d …"
          └─ age < 350d                       → review "recent rejection match …"
No match (#N/A):
├─ SF No_Paint / No_Receipt                  → review "Drop - no receipt/no paint"
├─ age ≥ 350d                                → review "Potential drop - no match, ≥350d"
├─ age ≤ 14d                                 → review "Potential drop - will show on next statement"
└─ else (15–349d)                            → review "Review - not found with conf or ref"
```

**Why:** a rejection can only downgrade, and the clawback scan (14 mo) proved an approved conf# is
never genuinely re-rejected — so a fallback-matched rejection against an approved SF record is always a
duplicate. Surfacing (not auto-downgrading) preserves the approval while keeping a genuine reversal visible.

**Top-priority suppressor — disregard tokens.** Before any row surfaces to review, SF BMCR Notes are
checked for a disregard token (`per ron`, `verified`, `confirmed`, `handled`; fuzzy-matched). A row
already carrying one is human-verified → `no_change`, never surfaced, regardless of what the statement says.

**Confirmation # writes are add-only-when-missing** — the process only writes a conf# to SF when SF's is
blank; it **never overwrites** an existing conf# (a fallback match can carry a duplicate's conf#, and a
human-entered/verified conf# must stand).

## Reconcile "usual checks" (increases only)

For rows that reconcile, the decision-rule tree only ever *increases* PPP credit or self-flags:
- Rules that *increase* $ awarded or points
- Self-flagging status transitions: `Approved`, `Dbl_Check`, `No Points Awarded`
- Confirmation # propagation only when SF's is blank

A *reduction* in points/$ is never auto-applied; `BMCR_Error` routes to manual review; disregard-token
rows stay `no_change`.

---

## Decision rules (key)

Configured in `config/decision_rules.yaml`.

| Config key | Value | Purpose |
|---|---|---|
| `half_amount_fraction` | 0.5 | BMCR $ < 50% of SF amount → Dbl_Check |
| `sf_submitted_statuses` | `['Submitted']` | SF "not yet processed" |
| `sf_no_credit_statuses` | `['No_Paint', 'No_Receipt']` | Compared case-insensitively |
| `sf_manual_status_substrings` | `['BMCR_Error']` | Routes to manual review |
| `new_status_values.no_points_award` | `'No Points Awarded'` | Spaces — must match SF picklist exactly |

### Classifier rule notes (updated 2026-06-09)

**Rule 0b** — SF=Rejected + VLOOKUP=Rejected + SF BMCR Notes matches VLOOKUP Notes → `no_change`. Fires after the disregard-token check (Rule 1) and the `#N/A` exit (Rule 0a), before BMCR_Error routing. Notes are normalized (strip punctuation, lowercase) before comparison. This handles BMCR portal cases where a rejected duplicate entry is the only entry in the current CSV while SF correctly holds the original approved record.

**Rule 2/3 (No_Paint / No_Receipt)** — When SF status is `No_Paint` or `No_Receipt`, the rule checks both points **and** dollar amount for increases. If VLOOKUP offers more of either, the field(s) are auto-updated. Status is never changed by this rule — VLOOKUP status is irrelevant.

**Rule 3b** — SF=Approved + VLOOKUP=Approved + both pts=0 → `auto_update` with `*NEW STATUS = No Points Awarded`. Also writes VLOOKUP dollar amount if the comparison column is "Update". Fires between Rule 3 (Submitted) and Rule 4 (BMCR_Error). Consistent with auto-update principle: self-flagging status, no reduction to PPP credit. Audit of affected rows via SF needs-review report by designated reviewer.

**Rule 11b** — SF=Submitted + BMCR=Rejected → `auto_update` with `*NEW STATUS = Rejected`, `*NEW BMCR AMT = VLOOKUP $` (what BMCR reported for the transaction), `*NEW POINTS = 0`. Dollar amount is written from VLOOKUP — not zeroed — because the transaction occurred, it was simply rejected. BMCR Notes copied to SF Notes when SF Notes are blank.

---

## CLI commands

| Command | Purpose |
|---|---|
| `python3 bmcr_recon.py` | Normal run — Gmail-driven |
| `python3 bmcr_recon.py --manual` | Force run regardless of date window |
| `python3 bmcr_recon.py --csv path.csv` | Skip Gmail fetch, use local BMCR CSV |
| `python3 bmcr_recon.py --sf-csv path.csv` | Skip SOQL pull, use local SF export CSV |
| `python3 bmcr_recon.py --dry-run` | Produce the packet without Slack posts (the run never writes to SF regardless) |
| `python3 bmcr_recon.py --apply reviewed.xlsx` | **Audit gate:** write ONLY the Approve==yes rows from a reviewed packet's "Proposed Writes" tab (state-change safety). Add `--dry-run` to build the payload without writing |
| `python3 bmcr_recon.py --force` | Bypass already-ran-this-month guard |
| `python3 bmcr_recon.py --revert YYYY-MM-DD --reason "…"` | Restore SF for that run (reason required) |
| `python3 bmcr_recon.py --write-supplemental path.csv` | Apply a supplemental write CSV with state-change safety check |

---

## Supplemental writes

Used when a second batch of rows needs to be written after the main run has already executed — for example, correcting rows that were missed or need a different value after the live run completed.

```bash
python3 bmcr_recon.py --write-supplemental path/to/payload.csv
```

**How it works:**
1. Reads `state/last_run.json` automatically to find the reference run — no date argument needed
2. Loads the pre-run SF snapshot (`sf_tx_before.csv`) from that run
3. Queries current SF state for every Id in the payload
4. Skips any row whose SF values have already changed since the pre-run snapshot (already written by something else)
5. Applies only the safe (unchanged) rows via bulk update
6. Writes `applied/supplemental_payload.csv` + `applied/supplemental_result.json` to the reference run's folder

**Safety guarantee:** Prevents the pattern where a second write overwrites rows already correctly written by the main run. Any row touched by the main live run will be detected as "already modified" and skipped.

**Payload format:** CSV with `Id` column plus SF field API names as headers (same format as the main writeback payload). Never use a dry-run output file as a supplemental payload after a live run has executed for the same rows.

---

## Output artifacts

Per-run output in `BMCR Recon/<YYYY-MM-DD>/`:
- `inputs/sf_tx_before.csv` — pre-run SF snapshot (revert safety net)
- `inputs/bmcr_365_raw_<MMM-YYYY>.csv` — BMCR source CSV
- `working/classified.csv` — full classification output
- `outputs/BMCR Clean-up YYYY-MM-DD.xlsx` — 4-tab review packet
- `applied/sf_bulk_update_payload.csv` — rows written to SF
- `logs/run.log` — full run log

Review packet tabs:
1. **Proposed Writes** — reconcile rows staged for SF, with an **Approve** column (default `yes`), sortable by change-category. `--apply` writes only Approve==yes rows.
2. **Review – Actionable** — surfaced rows needing a human decision (potential drops, recent rejection matches, not-found)
3. **Review – Low Priority** — high-volume, low-value surfacing (old orphans, no-paint/no-receipt, "will show next statement")
4. **All Transactions** — full view with all classifications
5. Plus legacy tabs (Carey Review, Uploaded Changes, Needs Manual Research) for continuity

Each audit-gate tab also carries **Match Tier**, **Fuzzy %**, and **Stmt Row** provenance columns.

---

## Audit gate

The monthly run **never writes to Salesforce**. It stages proposed writes in the packet and stops. A
human reviews the **Proposed Writes** tab (default `Approve = yes`; strike/clear a cell to veto, batch by
change-category), then applies:

```bash
python3 bmcr_recon.py --apply "path/to/reviewed.xlsx"          # writes Approve==yes rows
python3 bmcr_recon.py --apply "path/to/reviewed.xlsx" --dry-run  # build payload, write nothing
```

Apply reads the reviewed values as-is (no re-run / re-classify), builds the payload from the `*NEW`
columns, and writes via the same state-change safety check as `--write-supplemental` — any row whose live
SF values changed since the run snapshot is skipped. This is what prevents a stale write from clobbering a
value a human already corrected.

---

## Revert procedure

If auto-updates need to be rolled back:

```bash
python3 bmcr_recon.py --revert YYYY-MM-DD --reason "reason for revert"
```

Reads `inputs/sf_tx_before.csv` for that date and restores original field values via bulk update. `--reason` is required — no revert without a documented reason.

Manual revert (if `--revert` is unavailable): retrieve `sf_tx_before.csv` from Drive `BMCR Recon/<date>/inputs/` and restore via Data Loader or bulk API directly.

**Null-clearing revert** (when fields need to be blanked, not just overwritten): the `--revert` command and bulk CSV cannot null existing values — empty cells are treated as no-ops. Use the Salesforce composite REST API instead, with explicit `null` values in the PATCH body:

```python
import subprocess, json, requests
org = json.loads(subprocess.run(["sf", "org", "display", "--target-org", "prod", "--json"],
    capture_output=True, text=True).stdout)['result']
headers = {"Authorization": f"Bearer {org['accessToken']}", "Content-Type": "application/json"}
requests.post(f"{org['instanceUrl']}/services/data/v{org['apiVersion']}/composite",
    headers=headers,
    json={"allOrNone": False, "compositeRequest": [
        {"method": "PATCH",
         "url": f"/services/data/v{org['apiVersion']}/sobjects/Transaction__c/<SF_ID>",
         "referenceId": "ref1",
         "body": {"BMCR_Status__c": "Submitted",
                  "BMCR_Confirmation_Number__c": None,
                  "BMCR_DollarAmount__c": None,
                  "BMCR_PointsEarned__c": None}},
    ]})
```
Up to 25 records per composite request. HTTP 204 per record = success.

---

## BMC Products file

An updated `BMC Products_*.xlsx` is uploaded to the designated Drive folder periodically (no fixed schedule). The script auto-fetches the most recently modified file from this folder on each run (Step 0). Falls back gracefully to the last-downloaded local copy if Drive is unreachable.

Used by the PDF scorer to evaluate Dbl_Check rows for point eligibility.

---

## BMCR CSV source

Monthly BMCR 365 Report CSVs live in the shared Drive folder **"BMCR YTD Reports"**. Structure: year subfolders (2024/2025/2026), files named `YYYY-MM Precision_Painting_365_MMM-YYYY.csv`.

Script auto-derives the prior month from the current filename and downloads both for carry-forward suppression.

**Gmail fallback:** If Drive is unavailable, fetches from the biworldwide 365-report email attachment.

---

## Known edge cases

### BM National Account and Stein Paint transactions (Phase 3b)
All Stein Paint and BM National rows in the BMCR that don't match via the main join are handled by Phase 3b using a SOSL document lookup. The vendor is identified upfront from the BMCR distributor field ("BENJAMIN MOORE", "BM National Account", or "stein").

Phase 3b searches SF by invoice number and discriminates results by document title:
- **`Inv_5500` in title** → BM National invoice PDF → follow ContentDocumentLink → BM National `Transaction__c`
- **`Invoices` title** → Stein combined invoice file (same file linked to multiple transactions) → match correct Stein tx by `ReferenceId__c`

Both transactions are identified in one pass and reported in the Update Notes annotation.

Additional notes:
- BM National rows do **not** get sent to the PDF scorer (wholesale ZWB SKUs not in BMC retail sheet)
- Stein $0/$0 rows (BM submitted, not Stein direct) are a common sub-case of the above — handled by the same path

### Ponderosa Paint Center
`VendorBMRetailer__c = false` on Ponderosa's SF vendor record → excluded from SOQL pull entirely. BMCR rows for Ponderosa will always appear unmatched. If the SF transaction is otherwise correct and Approved, no action needed.

### Customer charges receipts (Ring's End type)
If a receipt in the receipts inbox is labeled "customer charges," do **not** create a `Transaction__c` in SF. Customer charge invoices are not tracked in SF. Receipt is sufficient documentation.

### Submission ID
Submission ID is **not** used as a standalone match key — the same submission ID can appear on multiple invoices (batch submissions). The sub+amt path uses it only when paired with a unique amount.

### Vendor + Amount match path
The vendor_amt path has a 1-day date window guard. A BMCR row is only matched via vendor+amount if `|BMCR invoice date − SF transaction date| ≤ 1 day`. This prevents cross-month false positives where the same vendor and amount appear in different periods.

---

## Slack notification

Run summaries DM the admin account directly. Group channel posts are disabled by default — to enable, add `chat:write` to the Slack app's user token scopes and reinstall the app.

---

## Schedule

launchd job (`com.ppp.bmcr-recon.plist`):
- Fires daily at 8:00 AM
- Self-gates: only proceeds on days 1–9 of the month
- "Already ran this month" guard prevents duplicate runs
- If no BMCR email found by day 9 → notifies admin via DM, exits
