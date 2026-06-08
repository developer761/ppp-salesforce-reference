# BMCR Monthly Reconciliation — Playbook

**System:** BMCR (Benjamin Moore Contractor Rewards) automation  
**Status:** Live as of 2026-06-08 (first production run complete)  
**Owner:** Kaitlin Sutton  
**Code:** `~/claude/projects/bmcr/`  
**Process doc (source of truth for rules):** Google Doc `10f5g-fSwHDuGh_y2hJUfpPcUURKJT4SA_pgJatspSug`

---

## What it does

On the 5th of each month (±4 days), a launchd job fires `bmcr_recon.py`. The script:

1. **Step 0** — Auto-fetches the latest `BMC Products_*.xlsx` from Carey's Drive folder
2. Fetches the current month's BMCR 365 Report CSV from Drive folder "BMCR YTD Reports" (Gmail fallback)
3. Pulls all BMCR-eligible `Transaction__c` records from SF production via SOQL
4. Matches BMCR rows to SF transactions via six paths:
   - Confirmation number
   - Reference ID (with W↔VV mis-OCR variant)
   - Exact Amount + Date + Vendor
   - Amount + Date + fuzzy Vendor
   - Vendor + Amount (1-day date guard)
   - Submission ID + Amount (last resort — unique amount only)
5. Classifies each matched row through a 15-rule decision tree
6. Phase 3a: searches receipts@ppp for manual_research rows by invoice number
7. Phase 3b: targets SOQL for unmatched BMCR rows; prior-month carry-forwards annotated NTA
8. Invokes Katie's PDF scorer for Dbl_Check rows
9. Generates 4-tab review packet xlsx + uploads to Drive `/BMCR Recon/`
10. Bulk-updates SF for auto-update rows (sf_tx_before.csv snapshot taken first)
11. DMs Kate with run summary (group Slack pending chat:write scope)

---

## Salesforce object

**Object:** `Transaction__c`  
**Report:** "BMCR All Transactions for Reconciliation" (ID: `00O6g000006pxO3EAI`)  
**SOQL date range:** Feb 1, 2025 – Jan 31, 2027 (PPP FY current + prior)  
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

## Auto-update principle

**Auto-write to SF (no human review):**
- Any rule that *increases* PPP credit (more $ awarded, more points)
- Self-flagging status transitions: `Approved`, `Dbl_Check`, `No Points Awarded`
- Confirmation # propagation when BMCR knows it and SF doesn't

**Review only (human sheet, no SF write):**
- Any *reduction* in points or dollar amount
- `BMCR_Error` status (Carey handles manually)
- Notes containing disregard tokens (verified, confirmed, handled, ron)
- Rule 15 catch-all

---

## Decision rules (key)

Configured in `config/decision_rules.yaml`.

| Config key | Value | Purpose |
|---|---|---|
| `half_amount_fraction` | 0.5 | BMCR $ < 50% of SF amount → Dbl_Check |
| `sf_submitted_statuses` | `['Submitted']` | SF "not yet processed" |
| `sf_no_credit_statuses` | `['No_Paint', 'No_Receipt']` | Compared case-insensitively |
| `sf_manual_status_substrings` | `['BMCR_Error']` | Sends to Carey |
| `new_status_values.no_points_award` | `'No Points Awarded'` | Spaces — must match SF picklist exactly |

---

## CLI commands

| Command | Purpose |
|---|---|
| `python3 bmcr_recon.py` | Normal run — Gmail-driven |
| `python3 bmcr_recon.py --manual` | Force run regardless of date window |
| `python3 bmcr_recon.py --csv path.csv` | Skip Gmail fetch, use local BMCR CSV |
| `python3 bmcr_recon.py --sf-csv path.csv` | Skip SOQL pull, use local SF export CSV |
| `python3 bmcr_recon.py --dry-run` | Skip SF writeback + Slack posts |
| `python3 bmcr_recon.py --force` | Bypass already-ran-this-month guard |
| `python3 bmcr_recon.py --revert YYYY-MM-DD --reason "…"` | Restore SF for that run (reason required) |

---

## Output artifacts

Per-run output at `/Volumes/Extreme SSD/PPP Files/BMCR Recon/<YYYY-MM-DD>/`:
- `inputs/sf_tx_before.csv` — pre-run SF snapshot (revert safety net)
- `inputs/bmcr_365_raw_<MMM-YYYY>.csv` — BMCR source CSV
- `working/classified.csv` — full classification output
- `outputs/BMCR Clean-up YYYY-MM-DD.xlsx` — 4-tab review packet
- `applied/sf_bulk_update_payload.csv` — rows written to SF
- `logs/run.log` — full run log

Review packet tabs:
1. **Auto-Update** — rows written to SF; for audit trail
2. **Carey Review** — rows needing Carey or Niti action
3. **Needs Manual Research** — #N/A rows with receipts search results
4. **All Transactions** — full view with all classifications

---

## Revert procedure

If auto-updates need to be rolled back:

```bash
cd ~/claude/projects/bmcr
python3 bmcr_recon.py --revert 2026-06-08 --reason "False positives identified in vendor_amt path"
```

Reads `inputs/sf_tx_before.csv` for that date, restores original field values via bulk update.
`--reason` is required — no revert without a documented reason.

Manual revert (if `--revert` is unavailable): download `sf_tx_before.csv` from Drive `BMCR Recon/<date>/inputs/` and use Data Loader or bulk API directly.

---

## BMC Products file

Carey uploads an updated `BMC Products_*.xlsx` to her Drive folder when available (no fixed schedule):
- Folder: `189sGA2ZISKTLNtUcrukPorko1abPTmC_`
- Script auto-fetches the most recently modified file from this folder on each run (Step 0)
- Falls back to existing local copy in `~/claude/projects/bmcr/bmcr_share/` if Drive is unreachable
- Used by Katie's PDF scorer to score Dbl_Check rows

---

## BMCR CSV source

Monthly BMCR 365 Report CSVs live in shared Drive folder **"BMCR YTD Reports"** (ID: `1CFbHN1OT1sX_Qa5-yzpYA1kQ29C65ghz`). Structure: year subfolders (2024/2025/2026), files named `YYYY-MM Precision_Painting_365_MMM-YYYY.csv`.

Script auto-derives prior month from current filename and downloads both for carry-forward suppression.

**Gmail fallback:** If Drive is unavailable, fetches from `system@biworldwide.com` attachment.

---

## Known edge cases

### BM National Account transactions
Stein Paint invoices submitted through Benjamin Moore National Account appear in BMCR with `Dollar Amount Total = $0` (BM submitted, not Stein direct). The corresponding SF transaction is a `BM National Account` record with a BM invoice number (`5500xxxxxx`).

- These flow through Kaitlin's recon normally
- Do **not** get sent to Katie's PDF scorer (BM National uses wholesale ZWB SKUs not in BMC retail sheet)
- Look up via SOSL on the BM invoice number

### Ponderosa Paint Center
`VendorBMRetailer__c = false` on Ponderosa's SF vendor record → excluded from SOQL pull entirely. BMCR rows for Ponderosa will always appear unmatched. If the SF transaction is otherwise correct and Approved, no action needed.

### Customer charges receipts (Ring's End type)
If a receipt in receipts@ inbox is labeled "customer charges," do **not** create a `Transaction__c` in SF. Customer charge invoices are not tracked in SF. Receipt is sufficient documentation.

### Submission ID
Submission ID is **not** used as a standalone match key — the same submission ID can appear on multiple invoices (batch submissions). The sub+amt path uses it only when paired with a unique amount.

### Vendor + Amount match path
The vendor_amt path has a 1-day date window guard. A BMCR row is only matched via vendor+amount if `|BMCR invoice date − SF transaction date| ≤ 1 day`. This prevents cross-month false positives where the same vendor and amount appear in different periods.

---

## Slack notification

All run summaries DM Kate directly (`k.sutton@precisionpaintingplus.net`).

> **Note:** Group channel posts (`C07GR4Z3ZQS`) are disabled pending addition of `chat:write` scope to the "Kate Daily Briefing" Slack app. To enable: add `chat:write` to app user token scopes, reinstall app, update token in `~/.claude.json`.

---

## Schedule

launchd job at `~/Library/LaunchAgents/com.ppp.bmcr-recon.plist`:
- Fires daily at 8:00 AM
- Self-gates: only proceeds on days 1–9 of the month
- "Already ran this month" guard prevents duplicate runs
- If no BMCR email found by day 9 → DMs Kate, exits

---

## Run history

| Date | BMCR Month | Auto-Updates | Carey Review | Notes |
|---|---|---|---|---|
| 2026-06-08 | June 2026 | 873 (627 + 246 retry) | 14 | First live run. No Points Awarded picklist fix + vendor_amt date guard added mid-run. |
