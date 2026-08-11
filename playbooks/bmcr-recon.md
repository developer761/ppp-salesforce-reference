# Playbook — BMCR Monthly Reconciliation

Monthly reconciliation of PPP's BM Contractor Rewards (BMCR) 365-report against Salesforce transactions. Automates matching, classification, SF updates, and review packet generation.

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

1. **Step 0** — Auto-fetches the latest `BM Products_*.xlsx` from the designated Drive folder
2. Fetches the current month's BMCR 365 Report CSV from Drive folder "BMCR YTD Reports" (Gmail fallback)
3. Pulls all BMCR-eligible `Transaction__c` records from SF production via SOQL
4. Matches BMCR rows to SF transactions via six priority paths (each row labeled with its tier):
   - Confirmation number
   - Reference ID / invoice number (with W↔VV mis-OCR variant)
   - Exact Amount + Date + Vendor
   - Amount + Date + fuzzy Vendor (**gated at ≥90% string similarity**; score shown in review)
   - Vendor + Amount (1-day date guard)
   - Submission ID + Amount (last resort — unique amount only)
5. Routes each row to *reconcile* or *review* (see "Reconciliation decision tree"), then classifies the reconcile rows through the decision-rule tree. Captures the statement's **gallons awarded** on every matched row (see "Capturing gallons awarded")
6. Phase 3a: searches the receipts inbox for manual_research rows by invoice number
7. Phase 3b: processes unmatched BMCR rows — pass-through-retailer / national-wholesale rows use SOSL document lookup (identifies both the wholesale tx and the matching pass-through-retailer tx); all other vendors use SOQL (full vendor name, exact amount, date ±1 day); prior-month carry-forwards annotated NTA
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
| BMCR Gallons Awarded | `BMCR_Gallons_Awarded__c` |
| BMCR Date Submitted | `BMCR_DateSubmitted__c` |
| BMCR Notes | `BMCR_Notes__c` |

> ⚠️ **`BMCR_Gallons_Awarded__c` must be scale ≥ 4** (it was widened from `Number(10,0)`
> to `Number(14,4)`). The manufacturer awards in **1/16 increments** — quarts, pints and
> half-pints — so an integer field silently rounds ~13% of rows and turns everything
> below 0.5 into a hard zero. See "Capturing gallons awarded" below.

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
| `python3 bmcr_recon.py --apply-gallons reviewed.xlsx` | Write ONLY the Approve==yes rows from the packet's "Gallons Backfill" tab. Hard-scoped to the gallons field; same state-change safety. `--dry-run` supported |
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

## Scorer disposition (verified → Approved / No_Paint)

After `--scores` re-scores live SF, each scored row (`BMCR_Status__c IN ('Dbl_Check','No Points Awarded')`) gets an automated end-state disposition based on the scorer output in `results.csv` (`our_eligible_points`, `bm_credited_points`, `pdf_count`, `eligible_skus`, `notes`):

- **Dbl_Check → `Approved`**, appending `BMCR_Notes__c = "Verified MM/DD/YYYY"`, when `our_eligible_points <= bm_credited_points` (the manufacturer credited at least what our invoice supports → accept, nothing more is owed). When `our_eligible_points > bm_credited_points` the purchase is **under-credited** → hold as a dispute (do not auto-approve).
- **No Points Awarded → `No_Paint`** when the scorer note is clean **and** `our_eligible_points = 0` (invoice genuinely has no eligible product).

**Verification guard — never auto-write a "0" that came from a failed read.** Hold (route to the reviewer review tab, not SF) any row whose scorer note is `UNKNOWN_VENDOR` (vendor not in the SKU map), `MULTI_INVOICE_PDF_FILTERED (1/N)` (only 1 of N bundled invoices scored — the rest unread), or `NO_PDF_ATTACHED` / `pdf_count = 0`, plus any No-Points row that still has `eligible_skus` populated (scorer found product on a zero-award → possible under-credit). A `0` from any of these is *unverified*, not *verified zero* — auto-writing `No_Paint` there would both mislabel the row and risk writing off points the retailer may still owe.

**Pass-through-retailer lines → `No_Paint`** via the No-Points path — this is the established reviewer standard, no special hook needed. The pass-through-retailer line earns nothing because the reward is submitted through the national wholesale account and lands on a **separate wholesale `Transaction__c`** (matched by invoice/Work-Order linkage, never by amount — the wholesale account is a wholesale channel). The credit is not lost; it's on the twin. See "Wholesale-account and pass-through-retailer transactions" below.

**Held rows** go to a review tab in the scores workbook in the same column format as the `(scores)` tabs plus a `hold_reason` column, for a reviewer to copy into their review sheet.

> **OAuth scope note (corrected 2026-08-07):** this step was originally documented as "copy by hand, because the pipeline holds only `drive.file` scope and cannot write an existing external Google Sheet." That constraint **no longer holds** — the pipeline's OAuth token now carries the broad `drive` scope plus `spreadsheets`, so writing an existing external Sheet directly is possible. The manual copy is now a convention, not a technical limit.
>
> ⚠️ **Related trap:** the broad `drive` scope is a strict superset of `drive.file`, but code that checks for the narrow scope with a literal substring test (`if "drive.file" not in token_scope: raise`) will **hard-fail on a token that is actually more privileged**. This blocked an entire monthly run at step 0. Fix the guard to accept either scope — do **not** re-consent back down to `drive.file`, which would drop the `spreadsheets`/`documents` scopes other tooling depends on.

> ⚠️ **`sf data update bulk` line-ending gotcha:** on macOS the CLI can reject a payload with `JobFailedError: LineEnding is invalid on user data. Current LineEnding setting is LF` when the file's line endings don't match. Normalize the payload to LF and pass `--line-ending LF` explicitly. **Nothing is written on this failure** (safe), but any code calling `sf data update bulk` should set the flag rather than rely on the default.

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
4. **Gallons Backfill** — the awarded-gallons capture batch, with its own Approve column; applied by `--apply-gallons`, separate from the reconciliation writes
5. **All Transactions** — full view with all classifications
6. Plus legacy tabs (reviewer tab, Uploaded Changes, Needs Manual Research) for continuity

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

## BM Products file

An updated `BM Products_*.xlsx` is uploaded to the designated Drive folder periodically (no fixed schedule). The script auto-fetches the most recently modified file from this folder on each run (Step 0). Falls back gracefully to the last-downloaded local copy if Drive is unreachable.

Used by the PDF scorer to evaluate Dbl_Check rows for point eligibility.

---

## BMCR CSV source

Monthly BMCR 365 Report CSVs live in the shared Drive folder **"BMCR YTD Reports"**. Structure: year subfolders (2024/2025/2026), files named `YYYY-MM Precision_Painting_365_MMM-YYYY.csv`.

Script auto-derives the prior month from the current filename and downloads both for carry-forward suppression.

**Gmail fallback:** If Drive is unavailable, fetches from the biworldwide 365-report email attachment.

---

## Capturing gallons awarded

The rewards programme reports a **gallons awarded** figure per statement line, and that —
not points — is the number the manufacturer measures the contractor on. Points exist only
inside the rewards programme, and the dollar-amount-awarded column carries tax so it never
ties back to a receipt total. Gallons compares like for like.

The reconciliation therefore captures gallons onto the transaction, and a later phase will
compare it against what the invoice says *should* have been awarded.

**The eligibility sheet already supports both halves.** Every SKU on it carries a gallon
equivalent alongside its points value — and notably, **a large minority of SKUs carry a
gallon equivalent but zero points**. Reconciling on points is structurally blind to that
volume, which is the substantive argument for the change, not just a preference.

### A new statement column has no history behind it

The first statement to carry the column is the first month of a *feed*, not a backlog.
Prior statements have no such column at all, so replaying them yields nothing — there is
no historical backfill available, and expecting one wastes a cycle. Coverage grows forward
one statement at a time.

Two consequences worth planning around:

- **Coverage is capped by the statement window**, which is rolling ~365 days. Transactions
  older than that will never receive a value.
- **Inside the window, expect well short of 100%.** On the first month, roughly a third of
  matched rows had the field left blank by the manufacturer. That is their ceiling, not a
  matching failure — but confirm with the programme contact whether blank means "zero
  eligible" or "not yet computed", because that decides whether the metric can carry
  volume reporting at all.

### Precision: never int-coerce a quantity you did not define

Awards come in **1/16 increments**. Any int coercion — in the SF field, in the row builder,
or in the spreadsheet writer's numeric-cast set — silently rounds, and values below 0.5
become a hard zero with no error. Points is an integer field and gallons sits next to it in
every one of those code paths, so the int treatment is very easy to inherit by accident.

Equally: **a blank statement value must stay blank, never 0.** Blank means the manufacturer
reported nothing for that row; zero is a positive claim they did not make. On the first
month roughly a third of statement rows were blank, so this distinction covers a large
slice of the data.

### Mirror the statement; don't reconcile against it here

Gallons has no "reduction → review" branch, unlike points and dollars. It is the fact of
record rather than a negotiated credit, so the statement always wins — including on a
decrease. Disputes belong to the invoice-scoring phase, which compares *invoice vs
statement*; comparing *SF vs statement* here would only be re-litigating what the
manufacturer already told us.

### Capture before routing, but hold the write for rows under review

Compute the value **before** the classifier's early-exit rules, because a row can be under
review for a points dispute — or suppressed by a disregard token — and still have an
undisputed gallons figure that the review tab needs to display.

Then clear the staged *write* for anything sitting on a human review pile, so reviewers
confirm the number rather than finding the record pre-filled underneath an open review.
Two mechanisms are needed, because the two review surfaces differ:

- **By route** — the packet's own review tabs. Automatic, no maintenance.
- **By explicit id list** — the separate scoring workbook, whose open/closed state the
  pipeline cannot infer because the scorer decides it after the run. Re-cut this list each
  month; do not let it accumulate.

⚠️ **Cut the hold list from the live review sheet, not from a recompute.** The two diverge
as soon as any matcher change ships mid-cycle or a reviewer vetoes a row by hand — neither
is reproducible from code. A recompute silently missed rows that a human had already
pulled onto the review pile.

⚠️ **Most "rows under review" may not be writable at all.** On the first month, two of the
review tabs consisted entirely of statement-side rows with **no SF transaction behind
them** — nothing to write, nothing to hold. Check for a record id before treating a review
count as a hold count; the real hold set was a fraction of the apparent one.

### Treat it as a first-class value, not an add-on

A new value only behaves predictably if it passes through **every** stage the existing
values do. Worth checking each one explicitly rather than assuming, because several are
easy to miss and fail silently:

| Stage | What it needs |
|---|---|
| SOQL pull | the field in the select list — which also puts it in the pre-run snapshot the revert and write-guard depend on |
| Match / carry | on both the main matched row and any synthetic rows built by the research phase |
| Comparison | its own comparison column, alongside the status/dollar/points ones |
| Proposed write | a `*NEW` column registered in the writeback field map |
| Reviewer notes | a note when the value changes, at parity with the others — otherwise a reviewer reading the notes column cannot see it moved |
| Packet | its columns on every tab, in a block shaped like the existing value blocks |
| Post-upload check | the verifier's field list, or a write cannot be confirmed to have landed |
| Revert | usually automatic if the revert derives from the writeback map — confirm rather than assume |
| Refresh / run summary | reported beside the existing totals |

**Placement carries meaning.** Put the block where its priority says it belongs — here,
immediately after the status columns and *before* the dollar columns, because the volume
figure is what the manufacturer measures on and the money columns are downstream of it.
Mirror the existing block shape (source value, statement value, comparison, proposed
write) so it scans the same way.

**Number format: prefer automatic over an explicit decimal pattern.** A literal decimal
point in a spreadsheet pattern prints a whole number as `20.`

### Keep the backfill out of the reconciliation review

Month one stages a year of history at once — roughly seven times a normal month's write
volume. Put it in its **own gate tab with its own apply command**, and exclude the rows
that already ride the normal payload so nothing is written twice. From month two the same
rows compare equal and stage nothing, leaving a small monthly trickle.

⚠️ **Scope the backfill apply to the one field.** Reusing the full writeback map means the
gate tab inherits every other `*NEW` column that happens to be populated on those rows —
and those rows were routed *away* from the normal write precisely because nobody approved
them. This was caught staging confirmation-number writes onto rows the classifier had
settled as no-change.

## Known edge cases

### Wholesale-account and pass-through-retailer transactions (Phase 3b)
All pass-through-retailer and national-wholesale rows in the BMCR that don't match via the main join are handled by Phase 3b using a SOSL document lookup. The vendor is identified upfront from the BMCR distributor field (the manufacturer, the national wholesale account, or the pass-through retailer).

Phase 3b searches SF by invoice number and discriminates results by document title:
- **`Inv_5500` in title** → wholesale invoice PDF → follow ContentDocumentLink → wholesale `Transaction__c`
- **`Invoices` title** → pass-through-retailer combined invoice file (same file linked to multiple transactions) → match the correct pass-through-retailer tx by `ReferenceId__c`

Both transactions are identified in one pass and reported in the Update Notes annotation.

Additional notes:
- National-wholesale rows do **not** get sent to the PDF scorer (wholesale ZWB SKUs not in the BM retail sheet)
- Pass-through-retailer $0/$0 rows (BM-submitted, not retailer-direct) are a common sub-case of the above — handled by the same path
- **End-state disposition:** a real-amount pass-through-retailer line that earns nothing on its own submission is set to `No_Paint` (established reviewer standard). The reward is on the wholesale twin, not the retailer line — `No_Paint` on the retailer line is correct, not a lost credit. `$0` retailer placeholders instead sit at `None`/`Submitted` until the wholesale account processes them.

### Excluded non-BM retailer
`VendorBMRetailer__c = false` on this retailer's SF vendor record → excluded from SOQL pull entirely. BMCR rows for it will always appear unmatched. If the SF transaction is otherwise correct and Approved, no action needed.

### Customer-charge receipts
Some retailers issue a separate "customer charges" invoice type. If a receipt in the receipts inbox is labeled that way, do **not** create a `Transaction__c` in SF. Customer charge invoices are not tracked in SF. Receipt is sufficient documentation.

### Submission ID
Submission ID is **not** used as a standalone match key — the same submission ID can appear on multiple invoices (batch submissions). The sub+amt path uses it only when paired with a unique amount.

### Vendor + Amount match path
The vendor_amt path has a 1-day date window guard. A BMCR row is only matched via vendor+amount if `|BMCR invoice date − SF transaction date| ≤ 1 day`. This prevents cross-month false positives where the same vendor and amount appear in different periods.

### Make transaction references clickable on the review tabs
Reviewers open records constantly, and every transaction name on a review tab is otherwise a copy-paste-into-search round trip. Hyperlink them — including names that appear **inside note text**, not just the dedicated name column. Scope it to the review tabs; links on the bulk data tabs are noise.

A spreadsheet formula is the wrong tool here for two reasons: notes reference a transaction mid-sentence, so the link must attach to a substring rather than the whole cell; and the review tab is a live working surface carrying the reviewer's own highlighting, so replacing values or writing whole-cell formatting would destroy their work. Use rich-text runs with a field mask naming **only** the text-run field — values, fills, borders and number formats then survive untouched. Verify that on a copy before touching the real sheet.

⚠️ **Two API behaviours will silently cost you links:**
- A text run starting at the very end of a string is rejected outright. A transaction name is very often the last thing in a note, so only emit a closing run when text actually follows.
- A run spanning an entire cell is **silently collapsed** — cells containing nothing but a transaction name come back unlinked with no error at all. Those need a cell-level text-format link instead, with the mask scoped to just the link and its styling.

The second failure returns a successful API response, so **verify by re-reading the sheet and counting links, not by trusting the write call**. A stronger check is to assert that each link's visible text matches the name of the record its URL targets — that catches misdirected links as well as missing ones.

Style links explicitly (underline and colour). A run-level link renders identically to surrounding text, so without styling the reviewer cannot tell what is clickable. Resolve record ids in bulk, since a record URL needs the id and the sheet carries only the name.

Finally: coordinates are read and written moments apart, so do not run this while someone is actively restructuring the sheet — a row moved in between lands a link on the wrong cell. Re-running is idempotent and repairs any drift.

### A write guard keyed to a pre-run snapshot silently drops rows the snapshot never had
The write step compares each record against a snapshot taken before the run and skips anything that changed since — sound protection against double-applying. But the source query is filtered (here, positive amounts only), so credits and returns are **never in the snapshot**, and the reconciliation's own research step finds them later by reference.

For those rows the guard defaulted the baseline to blank, which made any populated live value look like an edit. **They were skipped on every run, silently** — no error, just a quietly smaller write count than the approved count.

Two lessons worth carrying to any snapshot-based guard:

- **Absent from the baseline is not the same as blank.** Handle "no baseline" as its own case rather than letting empty-string comparison decide it.
- **The review packet is itself a valid baseline.** It records the values observed when the row was built, so "does live still match the packet?" preserves the guard's real question — has someone edited this since we looked? — for rows the snapshot cannot cover.

Also compare numerically where the two sources render differently (`0` vs `0.00`), or format drift alone will cause false skips. And reconcile **approved count vs submitted count** after every write: a silent gap between them is the only symptom this failure produces.

### SKU normalization can invent matches — punctuation is sometimes meaningful

Vendor SKUs are matched to the eligibility sheet by stripping every non-alphanumeric
character, so the matcher forgives formatting differences (`T5351X005` for `T5351X-005`).
But a large part of the manufacturer's catalogue is numbered `NNN.NN.N`, and stripping
those dots turns such a SKU into an ordinary 5-digit string — which is exactly what a
store's own internal SKUs look like.

The result is a **silent false positive**: a drywall joint-compound line and a paint-roller
line each collided with a real coating SKU and scored full points. Both are sundries the
eligibility sheet deliberately excludes, so every point they earned was invented. This was
logged as a one-off for months; it was not. It reached 11 transactions and 470 points in a
single month.

**Guard:** when the matched catalogue SKU contains dots and the vendor's does not, require
a **distinctive** word from the catalogue product name to appear in the invoice line's
description. Distinctive means rare across the catalogue — compute document frequency over
all product names and treat anything under ~5% as identifying. "GALLON" and "WHITE" prove
nothing; a product-line name does. Where a product name has no distinctive words, let it
pass rather than blocking on absent evidence.

Two blunter fixes are tempting and both are wrong:

- **Excluding dot-formatted catalogue SKUs** blinds the scorer to over a third of the
  catalogue.
- **Requiring the vendor SKU to carry dots too** kills the genuine matches from vendors who
  *do* write them.

**How to know the guard is right rather than merely plausible:** after the fix, every
affected transaction reconciled to the manufacturer's credited figure *exactly*. An
approximately-correct rule does not land on their number to the point. Before the fix, the
inflated scores had produced apparent under-credit disputes worth raising with the
manufacturer — the largest of which was entirely phantom.

⚠️ **Fix this before reconciling on gallons.** An overstated "what we should have been
awarded" turns directly into a false dispute raised with the manufacturer, which costs
credibility in a way an internal miscount does not.

Pin it with a test that runs against the **real** eligibility sheet and asserts the
catalogue still contains dot-formatted SKUs — so it fails loudly if the numbering scheme
changes, rather than passing vacuously.

### Writing numbers into an existing spreadsheet column

Two traps, both of which return a **successful API response** while producing wrong cells.

**Appending a column inherits the formatting of the column to its left.** If that neighbour
is a date column, the new column arrives date-formatted, and a values-API write with
user-entered parsing reads every number as a date serial — 19 becomes `1900-01-19`, 1
becomes `1899-12-31`.

**Clearing the number format does not reliably fix it.** After emptying the column,
verifying it empty, and clearing the format over its full depth, cells still came back as
dates on rewrite: the value parse and the cell format resolve together.

**Use the cell-update API with an explicit numeric value** rather than the values API. That
writes a true number with no parsing and no format dependency; clear the number format in
the same request so display falls back to automatic.

Also **do not set an explicit `0.####` pattern** to show optional decimals — the decimal
point in a spreadsheet pattern is literal, so a whole number renders as `20.`. Automatic
formatting renders `20` as `20` and `0.0625` as `0.0625`.

As with hyperlinking, **verify by reading the sheet back and cross-checking values against
the source**, never by trusting the write call. Reading back is the only thing that caught
either trap here.

### Reading line items from PDFs: extraction order is not row order
Invoice scoring depends on pulling SKUs and quantities off a PDF, and most point-of-sale templates extract row-major — one text line per line item — so a per-line pattern works. Some do not: they extract **column-major** (every SKU, then every description, then every price), and the grouping can be **inconsistent between invoices from the same store**. Three different shapes appeared across thirteen invoices from two stores, plus a varying header-label count and one template printing a column *after* the footer text.

Parse by **token shape and order** rather than fixed offsets: find one unambiguous block to establish the item count, then classify the rest by shape (money-like, unit words, percent-suffixed, identifier-shaped) reading in order.

⚠️ **Make the arithmetic reconciliation mandatory.** Quantity × unit price must equal the invoice's own extension column, or return nothing. An early version applied that check only when extensions happened to be present and, on a template where they were not, **silently returned unvalidated line items**. A mis-paired SKU and quantity does not raise an error — it produces a confident wrong score, which is worse than reporting nothing, because "could not read" is a state the downstream disposition already handles.

Two framing notes. Detect by **layout family, not brand** — many stores share one POS template, so new stores are then a one-line addition. And calibrate the payoff first: this work unblocked ten rows and recovered **zero points**, because unparsed invoices are often unparsed precisely because they are low-value. The gain was turning undecidable rows into decidable ones.

### Refresh the review pile before anyone sleuths it
The monthly run reads Salesforce once and freezes that answer into the packet. Salesforce then keeps moving: wholesale-account credit posts days to weeks after the purchase, and receipts are entered continuously. Reviews typically happen several days after the run, so part of the review pile is already stale before a human opens it.

Add a **refresh step between the run and the manual review**: re-check every row still on the manual-research pile against live Salesforce, move anything that has since resolved to No Action, and report exactly which rows can be cleared. Read-only against Salesforce.

**Ordering is the entire point.** Doing this at write time would be too late — by then the sleuthing has already happened, and avoided sleuthing is the cost the step exists to remove. The sequence is: run → **refresh** → manual sleuthing → apply → scoring → **gallons apply**. The write step should *warn* when no refresh was recorded rather than block, since the reviewed packet is still valid; the cost of skipping was already paid in wasted effort.

The gallons apply comes last because its hold list covers rows still open on the *scoring*
workbook, so it can only be cut accurately once scoring has run.

**This is measurable, not theoretical.** On one run, the pipeline finished at `15:56:48Z` and two wholesale transactions covering review rows were created at `17:10:12Z` and `17:14:03Z` — about 75 minutes later. Three days on, four review rows worth 300 points had resolved themselves and were found only by a manual Salesforce search.

Two implementation notes: do **not** seed the wholesale-lookup cache when refreshing — a cached miss is precisely the stale answer being overturned. And rewrite the working classified file in place (keeping the pre-refresh copy) so later steps read current truth rather than the frozen snapshot.

### Vendor aliases — when the same store trades under two names
The fuzzy-vendor gate is deliberately tight (0.90) so it only forgives formatting differences. It cannot bridge a genuinely different trading name for the same store: one retailer's statement name scored **0.455** against its Salesforce account name — nowhere near the gate, and lowering the gate to reach it would let real mismatches through.

Confirmed aliases therefore live in an explicit config (`config/vendor_aliases.yaml`), keyed statement-distributor → SF account name, and score 1.0. This unlocks every fuzzy-gated path at once (`amt_date_fuzzy`, `vendor_amt`, `ref_prefix`) without loosening the rule for any other vendor. An alias never matches anything on its own — amount and date still have to agree.

Before adding one, check whether plain fuzzy already handles it: substring containment already scores 1.0, so many apparent aliases need no entry. A redundant alias is one more thing to keep true.

### Repeat submissions of one invoice must not block matching
The fuzzy paths require a *unique* candidate so a transaction can't bind to the wrong purchase. But when every candidate carries the **same invoice number**, there is only one purchase — the extra rows are the vendor re-submitting it, each with its own confirmation number. Refusing to match there protects nothing and strands real credit.

Candidates sharing one invoice number are collapsed to a single best row — **Approved before Rejected, then the lowest confirmation number** (the original submission) — before the uniqueness check. Candidates that are genuinely different invoices still leave the tie in place and go unmatched, which is the correct conservative outcome.

### Successful resubmissions hide behind the failed original
When a submission is rejected and then resubmitted, the resubmission carries a **new invoice number and a new confirmation number** — nothing in the data links it to the original. Salesforce keeps the original's confirmation number, so confirmation-number matching (the first tier) binds the record to the *failed* row and short-circuits before any tier that could find the successful twin. The record then sits at error/0 points indefinitely while the statement shows the purchase was approved and paid.

Detection keys on the only attributes the two rows share — **vendor + amount + invoice date** — and requires the candidate to be approved with points under **both a different confirmation number and a different invoice number**. Same confirmation number or same invoice number means an ordinary duplicate, which is a different case handled elsewhere.

⚠️ **This flags for review; it must never rebind automatically.** Rebinding a record that already has a confirmation-number match would undermine the confirmation-first rule that prevents approved records being downgraded to rejected. Vendor+amount+date agreement is suggestive, not proof — a human confirms. Make the review note earn its keep: name the transaction and include a direct record link so the reviewer can act without hunting.

**Expect this to be rare, and expect most near-misses to be correctly excluded.** On one month's data the funnel ran 2,554 records matched to a rejected/0-point row → 14 sharing an amount and date with an approved row → **1 genuine resubmission**. Of the 13 exclusions, 11 were same-invoice approved/rejected duplicate pairs and 2 were coincidental amount+date collisions between unrelated vendors. A statement-side scan that ignores those two distinctions will badly overstate the opportunity.

### Truncated invoice stems (`ref_prefix` path) and the double-approval trap
Some distributors' invoice numbers reach Salesforce truncated to a short stem — SF `ReferenceId__c` holds `ABC12` where the statement carries `ABC12-07291NM-S`. Exact reference matching misses these entirely, so they surface as unmatched statement rows that look like lost credit.

The `ref_prefix` path handles them: if the SF reference is at least 5 characters and is a strict prefix of the statement invoice, it counts as a reference match — **gated on fuzzy vendor agreement, a ≤1-day invoice/transaction date gap, and a unique candidate.** All three guards are required; a bare 5-character stem is weak evidence on its own, and short numeric stems collide across years (a 5-digit stem routinely hits transactions from several years earlier).

**The reason this path runs only after exact reference matching is the more important half.** When a distributor both emails receipts and runs an automatic invoice feed, the same purchase is submitted twice — once under the stem, once under the full invoice number. Because the rewards program de-duplicates on the invoice *string*, the two forms read as different purchases and **both are approved at full points.** Running exact-first means the SF record binds to whichever form matches exactly, leaving the other form unmatched and available to be recognised as a duplicate rather than double-counted.

Unmatched statement rows are then checked against the approved-invoice keys for a truncated-stem twin: if an already-credited invoice is a strict prefix of this row's invoice under a *different* confirmation number, the row routes to **No Action Needed** with a note naming the transaction and confirmation number that already hold the credit.

⚠️ **Every such pair is logged at WARNING with its point value.** A purchase approved twice is an over-credit the program may later reverse, so it must never be silently absorbed into "No Action" — the routing keeps the review pile honest, and the log is what surfaces the exposure for a human decision. Raise the pairs with the rewards contact, and check whether the duplicate submissions can be stopped at the source.

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
