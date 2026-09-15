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
11. Emails the run summary to the admin account

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
     └─ SF ≠ Submitted  (revised 2026-07-14: NO ACTION, was review-by-age):
          ├─ SF = Approved                    → no action, quoting the statement's own reason
          │                                     (see "Quote the source's reason …" below)
          └─ SF = Rejected/no-paint/no-receipt → no action, "both no-credit, confirmatory"
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
| `python3 bmcr_recon.py --dry-run` | Produce the packet without sending notifications (the run never writes to the CRM regardless) |
| `python3 bmcr_recon.py --apply` | **Audit gate:** write ONLY the Approve==yes rows from the reviewed packet's "Proposed Writes" tab (state-change safety). Reads the **live sheet** by default — see "the artifact a human reviews is the source of truth". A file path still works for replaying a historical apply. Add `--dry-run` to build the payload without writing |
| `python3 bmcr_recon.py --apply-gallons <packet>` | Write ONLY the Approve==yes rows from the packet's "Gallons Backfill" tab. Hard-scoped to the gallons field; same state-change safety. `--dry-run` supported |
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

**The disposition happens in the SAME write as the reconciliation, before anything reaches the system of record.** It used to run as a second pass after the status write, off a post-apply scorer workbook; that meant a row passed through an intermediate status and waited weeks for its real one, and the second-pass scripts drifted out of date between runs. Each scored row now gets its end-state proposed on the review packet itself, from the scorer output (`our_eligible_points`, `bm_credited_points`, `pdf_count`, `eligible_skus`, `notes`):

- **Dbl_Check → `Approved`**, appending `BMCR_Notes__c = "Verified MM/DD/YYYY"`, when `our_eligible_points <= bm_credited_points` (the manufacturer credited at least what our invoice supports → accept, nothing more is owed). When `our_eligible_points > bm_credited_points` the purchase is **under-credited** → hold as a dispute (do not auto-approve).
- **No Points Awarded → `No_Paint`** when the scorer note is clean **and** `our_eligible_points = 0` (invoice genuinely has no eligible product).

**Verification guard — never auto-write a "0" that came from a failed read.** Hold (route to the reviewer tab, not the system of record) any row whose scorer note says the parser could not READ the invoice — vendor not in the SKU map, no attachment, empty/scanned text, or **no invoice block matched the reference** — plus any zero-award row that still has eligible SKUs populated (product found on a zero award → possible under-credit). A `0` from any of these is *unverified*, not *verified zero*.

⚠️ **Do not hold a note that reports the parser SUCCEEDING.** A bundled PDF containing several invoices produces a "filtered N of M blocks" note, and that note means the parser found the right invoice among the others — the remaining blocks are *different invoices*, not unread parts of this one. It was on the hold list, and on one run it flagged 17 rows of which **16 had selected the correct block**; the real read-failure signal is "no block matched the reference" (1 row). Narrowing it cut the reviewer's queue from 27 rows to 11. The reviewer's rule: *"if it chose correctly, no need to flag that it chose correctly — only when it chooses incorrectly or can't find what it's looking for."* A review queue padded with successes trains people to skim it.

**Score BEFORE the write, not after — and when you move it earlier, move its INPUTS too.** Running the eligibility scorer only after the status write means the reviewer approves a batch without ever seeing whether the manufacturer actually credited what the invoices support. Moving it ahead of the write takes two changes, and skipping the second silently inverts the result:

1. **Drive the scorer off an explicit record-id list, not a live status filter.** Pre-write, the rows still carry their *old* status; the target status exists only as a proposed value on the staged row. A scorer filtering on live status matches none of them and returns a clean, entirely misleading zero.
2. **Take the AWARDED figures from the staged row too.** The awarded points/volume fields are precisely what the pending write is about to set, so pre-write they read 0 or blank. Comparing an invoice read against them makes *every* row look short-changed. Measured on a real batch: **74 rows staged as disputes, every one false** — the invoice read matched the statement exactly. Pass the statement's awarded values in alongside the id list, and make the classifier **refuse** (raise, not warn) if a staged row is ever classified against the live-system source.

The general rule: **pre-write, the system of record is not the source of truth for any field the run is about to write.** Anything read from it there is a *pre-image*, and comparing a computed value against a pre-image measures the pending change, not reality.

**Post values regardless; let the comparison route the review, not the write.** The cleanest division is that the reconciliation write proceeds on its own rules, and the owed-vs-awarded outcome decides only whether a row *additionally* lands on a shortfall tab for the rebate-program contact to chase. Two separate decisions, two separate outputs — collapsing them means a scoring uncertainty can block a write that was never in doubt.

**The two statuses are asymmetric, and that asymmetry is the whole design.** For a flagged-for-review row the manufacturer awarded *something*, so `gap = awarded − owed` and a positive gap is benign (they found eligible product the parser missed). For a zero-award row the award is zero *by definition* — so whatever the invoice read finds IS the gap. That status needs one "owed" column and **no gap column**; adding one invites a diff against a number that does not exist.

**Volume figures are fractional — never int-cast them.** Rebate volume is awarded in fractional increments (quarts, sixteenths). Casting to int silently zeroes every part-unit line, and the loss is invisible because the column still looks populated. Same trap that forced a numeric field's precision to be widened after the first write. Keep them float end to end, and remember **blank is not zero**: a blank awarded-volume field usually means "nothing was awarded", but it is not a number you may subtract from, so a row with no reported volume must not produce a shortfall.

**Check the artifact when the REVIEW ends, not when the write begins.** Gating only at write time is too late: the review effort has already been spent on an artifact that may have been broken the whole time. Every defect found in one bad day was present during the review, hours before anyone considered applying. Make the check a step of its own — *"the eval is complete, is this sound?"* — and let the write gate on it too, without a skip flag. A check that is wrong is a bug to fix, not a gate to step around.

**Group checks by WHO CONSUMES the artifact next, not by what changed.** Checks written around this run's changes can only catch errors already imagined; they are confirmations of intent. Asking instead what each downstream party requires — the bulk API needs every row keyable, the target system needs valid picklist values, a human needs numbers that render as numbers, the next regenerate must not blank a hand-typed column, the reviewer needs to know the review is finished — catches defects nobody anticipated, because the question does not depend on knowing what went wrong. And **replay the checks against a captured copy from before a known defect was fixed**: a pre-flight that has only ever passed is not evidence of anything.

**Prefer an equality between two independently-derived sets over any spot-test.** The strongest assertion available here is that *rows still carrying a non-settled status in the system of record* equals *rows on the review tab* — because a row only leaves its staged status by settling, and a row that did not settle is exactly what belongs on the tab. The same mistake cannot satisfy both sides, so one comparison catches disposition drift, missing verdicts, and rows silently dropped from the analysis, without knowing in advance which occurred. It found two drifted records immediately, where every per-row check had passed.

**Three ways a row gets wrongly recorded as a verified zero.** Each shipped before being caught: (1) **a broken reader's zero** — an OCR path that fails on a missing credential still returns 0, and the row reads as "we agree there was nothing on the invoice"; put the error marker in the unread list. (2) **A row excluded from the scorer entirely** — rows the catalogue cannot score are rightly skipped, but skipping them left them with no verdict, no label and no place on the review tab, so they vanished from the analysis instead of being reported as unevaluable. *"We cannot check this" is a finding; silence is not* — and such a row can carry a real award. (3) **A pass-through page scored against its own row** — a comparison of one record to one statement row knows nothing of the twin pattern where one purchase is recorded twice and the reward rides the other record. One row scored "owed 560 points"; the same work order held two twins already approved for more than that. **Check the work order for a credited twin before raising a zero-award row as a dispute.**

**A generated column that mirrors the system of record is a RENDERING, not an observation.** Three separate bugs in one day came from treating a packet's mirrored columns as fact: a lookup-error marker read as a value by the write guard (15 dropped writes), a scorer column read as absent, and blank vendor/amount copied onto a review tab for hand-resolved rows — whose mirrored columns are empty *precisely because* those rows had no match on that side. When a row's provenance is the other side of the join, source those fields live.

**Never hand-roll the bulk-write invocation.** A CSV writer emitting CRLF by default causes the bulk API to reject the job outright with nothing written; the project's own write helper normalises line endings for exactly that reason. Writing an ad-hoc payload rather than calling it reproduced the failure a second time. The pattern generalises past line endings: a guard that exists is only a guard if every path goes through it.

**When a step's batch form stops making sense, rebuild it as the thing people actually need.** A post-write re-scoring step that produced a batch workbook went near-empty once scoring moved before the write — and an empty result is indistinguishable from a clean one, which is the worst possible output. The capability worth keeping was never the batch: it was answering *"why does our read disagree with what was awarded?"* for one row. Rebuilt as a targeted per-row query, it is smaller, honest, and actually used. Note it reads awarded values from the system of record, which is correct **because** it runs after the write — the exact opposite of the pre-write rule above. Same field, opposite answer, depending which side of the write you are on.

**A success count is not a row count.** A bulk write reported `submitted=935 succeeded=935 failed=0` against a payload built from **969** rows. Nothing named the missing 34, and "0 failed" actively reassures — a *skipped* row is not a *failed* row, so it appears in no counter. All 34 were real writes that never happened. **Reconcile three numbers, not one: intended → submitted → succeeded**, and verify the end state by re-querying the target system rather than reading the job's own counters. Any `continue` that drops a row inside a write path must count and report what it dropped; a silent skip is indistinguishable from success at every layer above it.

**A row that cannot be keyed cannot be written — say so loudly.** Rows resolved by hand had the transaction identified only in a *name* column and a reviewer note; the payload builder keys on record id and skipped blanks with a bare `continue`. Six rows sat on the approved tab looking staged and wrote nothing, and they were the rows that had cost the most human effort. When binding such a row later, **require a to-the-cent amount agreement before accepting an id** — a name typed in a note is not proof — and record any override of that check together with the human reason, so a later run can tell a deliberate exception from a mistake.

**Prove an alert channel can send before trusting it.** A reconciliation's notifications had never worked: the API token the code actually read carried a purely read-only scope set (no write scope at all) while the module's own docstring claimed otherwise, it pointed at the wrong workspace, and an earlier incarnation had spent ~3 months posting to a decommissioned server. Nobody noticed through any of it, because **the symptom of a broken alerting path is silence — which is also the symptom of a healthy system**. Send a real message through the real credentials; config and documentation describe intent, not capability. And prefer one channel demonstrated to work over two assumed redundant: untested redundancy is a story, not a backup.

**The artifact a human reviews is the source of truth — not the file that generated it.** The apply step read a spreadsheet file exported at run time, while the review, the sleuthing, the vetoes and the notes all happened in the live shared sheet. By apply time the file held 950 rows with none of the final statuses; the sheet held 969 with them. Applying the file would have written intermediate statuses to ~347 records and silently reverted a week of review. Read the live artifact, and log which source was used on every run. Two corollaries: **back the sheet up somewhere durable before regenerating it** (a prior backup went to a session-scoped temp directory and did not survive), and if any reviewer-typed column is not populated by the pipeline, regenerating **erases it silently** — the column still exists and still looks normal.

**Widening a shared lookup tuple breaks every unpack site silently.** When a catalogue lookup returns a positional tuple consumed in several modules, add the new attribute as a **parallel dict keyed by the value the lookup already returns** rather than as a fifth tuple element. The parallel dict cannot break an existing caller; the wider tuple breaks each one at a different line.

**Pass-through-retailer lines → `No_Paint`** via the No-Points path — this is the established reviewer standard, no special hook needed. The pass-through-retailer line earns nothing because the reward is submitted through the national wholesale account and lands on a **separate wholesale `Transaction__c`** (matched by invoice/Work-Order linkage, never by amount — the wholesale account is a wholesale channel). The credit is not lost; it's on the twin. See "Wholesale-account and pass-through-retailer transactions" below.

**Held rows** go to an `Owed vs Awarded` tab on the review packet itself, carrying awarded vs owed side by side for both points and volume plus the reason each row is there. They are ALSO on the write-staging tab and still get written — the tab routes review, it does not gate the write.

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

Review packet tabs, in reading order — **review piles first, writes next, reference last**, because the tabs that need a human are the ones worth opening first:
1. **Reviewer tab** — rows escalated to the programme contact (reductions, known errors)
2. **Statement Rows – Review** — statement rows with no confident record match
3. **Record Rows – Review** — matched records needing a human decision
4. **Proposed Writes** — rows staged for the CRM, with an **Approve** column (default `yes`), sortable by change-category. The apply step writes only Approve==yes rows.
5. **Gallons Backfill** — residual gallons captures. **Should be empty** (see "A gallons-only difference is still a write"); rows here mean routing dropped something. Treat it as a canary, not a work queue.
6. **Review – Low Priority** — high-volume, low-value surfacing (old orphans, no-paint/no-receipt, "will show next statement")
7. **No Action Needed** — resolved without a write (statement rejections against already-approved purchases, confirmatory no-credit agreements, prior-period carry-forwards)
8. **All Transactions** — full view with all classifications

Each audit-gate tab also carries **Match Tier**, **Fuzzy %**, and **Stmt Row** provenance columns.

---

## Audit gate

The monthly run **never writes to Salesforce**. It stages proposed writes in the packet and stops. A
human reviews the **Proposed Writes** tab (default `Approve = yes`; strike/clear a cell to veto, batch by
change-category), then applies:

```bash
python3 bmcr_recon.py --apply                       # reads the LIVE SHEET, writes Approve==yes rows
python3 bmcr_recon.py --apply --dry-run             # build payload, write nothing
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

## Reviewing a staged batch: name the rows that do not fit

A link to a 900-row packet hides its own problems. Almost every staged write is the same dull
progression, and the rows worth a human's attention are the handful that deviate. So after the
packet builds, **profile it and report the exceptions in the channel where the reviewer
already is**, before handing over a link.

Report, every run:

- **Off-shape rows** — anything whose before/after status is not the dominant progression.
  Give the record, the match tier, the status change, and the note.
- **The safety invariants**, asserted rather than assumed: no reduction of points or volume,
  no identifier written over an existing one, a count of any status downgrade, and a count of
  human-annotated rows that would otherwise write anyway.
- **A month-over-month trend with driver breakdown.** A count moving sharply is how an
  upstream change announces itself — a new vendor feed, a bad submission batch, a filter
  quietly dropping rows. Flag at a multiple of the prior median with a noise floor, and show
  the **top reasons behind each flagged metric** so the spike points at its own cause. Normalise
  row-specific values (record names, identifiers, amounts) out of the reason text or nothing
  groups.

On one run this was 4 rows out of 922, and all four were real: a record type that could never
have earned the reward, a row that would have carried points under a contradictory status, and
a statement/CRM disagreement. None would have survived scrolling.

**Use plain language for every metric.** An internal term ("synthetic rows") is invisible to
the person reading the alert. Say what the number *is* — "statement rows with no matching
transaction, added as placeholders so they are visible" — and keep the label next to the count.

**Charts in email:** mail clients strip `<svg>` and block most external images. Build bars from
table cells with background colours, inline the critical styles, and assert at render time that
neither an `svg` tag nor an external `src` reaches the HTML.

## Running it unattended

Anything scheduled should survive the machine it was built on. Four failures, each of which
silently produced *nothing* rather than an error:

1. **A moved project folder.** The scheduler entry hardcoded a path; the project was
   reorganised and the job could no longer be spawned at all. It failed every morning for
   months, and because it never started, it never reached its own error handler.
2. **A writability probe that does not probe.** `mkdir(parents=True, exist_ok=True)` on an
   **already-existing** directory is a no-op — it never touches the filesystem and therefore
   cannot detect missing permission. The real failure then surfaces on the *next* write,
   outside the guard. Probe by creating and deleting an actual file.
3. **Storage the scheduler cannot reach.** A process spawned by the OS scheduler does not
   inherit the interactive shell's disk-access grants, so an external or removable volume that
   works by hand fails on a schedule. Treat cloud storage as the durable home and the local
   directory as scratch — upload everything needed to resume, re-run or revert, every run.
   Never fall back to the system temp directory: it gets reaped, so an unattended run's only
   local copy can evaporate.
4. **A notification channel nobody tested.** The failure alert pointed at a decommissioned
   chat workspace and every notice for months was swallowed. **Send failure notices on two
   independent channels**, and verify the alert path itself on a schedule — an alerting system
   that has never fired is untested, not healthy.

## Fix a bad join key at the join, not downstream

A reconciliation binds each record to one statement line and reads that line's status as the
purchase's outcome. So a wrong key is not a cosmetic data-quality issue — it silently decides the
answer.

The case: a **submission ID** entered into the confirmation-number field. Confirmation-tier matching
then fails, the record falls back to invoice-tier, and these invoices carry **two** statement lines —
an approval and a rejected duplicate. **18 of 27 records held the rejected duplicate's submission
ID**, collectively worth over 1,800 points. Left alone, the next reconciliation would have read every
one of those purchases as rejected.

**Resolution rule, two branches.** Exactly one *credited* candidate for the invoice → use it; the
other is the rejected duplicate. Both candidates credited → use the line whose **submission ID equals
the bad value in the key field**: that value is not noise, it names the exact submission the person
was recording, and with both lines credited neither choice can strip credit. Anything else stays for
a human. **Never store a rejected line's key.**

### Where the fix goes is the whole lesson

The first implementation corrected the key *after* classification, and had to choose between two bad
options: keep proposals computed against the wrong line, or clear them. It cleared them — and that
produced the worse failure. Records whose key had been corrected were left with blank status, points
and volume, on a tab labelled *"nothing further to write"*. **Over 2,100 points and 117 gallons sat
invisible behind a completion label.** It surfaced only because the reviewer asked whether that label
was actually true.

Correct the key **before matching**, on the extract, and the existing matcher and classifier then do
their normal work with no special-casing — including routing a few records to manual scoring that a
hand-written shortcut would have marked approved.

**Generalises past this process:** when a record is mis-joined, patching the *conclusions* leaves you
choosing between wrong answers and no answers. Repair the key at the join and let the pipeline re-derive
everything. And **never reimplement the decision rules for the affected subset** — feed those records
back through the real classifier with a minimal input. A hand-rolled subset is a second copy the moment
it is written, already missing the branches its author didn't think of.

**A completion label is a claim about the whole record**, not the field you touched. Before writing
*done* or *no action*, enumerate every field the process can set and check each one — especially where
an earlier guard CLEARED values, because that work still exists and is merely no longer visible.

## A coded column is not the column you think it is

A vendor statement's status column held single-letter codes, not words. A filter written
against the words returned **zero rows** — which reads as a clean result, not a broken filter.

**Run a positive control before reporting any null or surprising result:** apply the same
filter to a period where the answer is already known. If the control does not reproduce the
known figure, the filter is wrong, not the world. Here the control returned the documented
count exactly, which is the only reason the real number was trusted.

### When a join fails, enumerate every key both sides carry

A monthly reconciliation matched statement rows to CRM records on invoice number, then amount and
date. Rows the vendor had **transcribed wrong** could not match on any of them — and the same bad
read was usually why the vendor rejected the row in the first place ("missing information in
invoice", "distributor cannot be determined"). Those rows sat unmatched indefinitely.

They were recoverable the whole time. Both systems carried a **submission id** — a dedicated field
on the record, its own column on the statement — and that key survives a mis-transcribed invoice
number. It had never been used, because the pipeline's existing key set was inherited as if it were
the space of possibilities rather than one implementation's choices. A human found the first case
by hand.

**An existing matcher's keys are evidence of what someone once needed, not proof of what is
available.** Before calling anything unmatchable, list the fields both sides actually carry, and
try the lookup in the reverse direction too.

#### Recovering a mis-transcribed identifier — the composite, and why each step exists

1. **Shared submission id** — the candidate net, and *only* that. One submission covers many
   invoices, so it narrows to a batch, never to a row.
2. **Date within one day.** Calibrate the tolerance, don't guess it: on pairs whose identifiers are
   byte-identical, 93.6% were same-day and 100% fell within three.
3. **Amount agreement, where both sides have one — the discriminator.** Without it the method is
   actively harmful: **sequential identifiers inside one batch differ by one character**, exactly
   like a typo, and score identically on any string metric. Requiring amounts to agree cut 982
   candidate pairs to 36.
4. **String similarity for ranking only**, plus a mutual-best-with-margin check.
5. **A global exact-match guard**: if any record anywhere holds the exact statement identifier, skip
   — the row belongs to *that* record.

Step 5 was learned expensively. Four rows were proposed against the wrong record before it existed:
one where a sibling record held the identifier exactly, and three where the **correct** statement
row sat at **zero dollars** while another row in the same batch carried the money — so the amount
test in step 3 confidently picked the wrong sibling. **The discriminator that prevents one failure
mode created another**, which is the general hazard of scoring rules: each new signal fixes the
cases you were looking at and opens cases you were not.

**Output proposals, never bindings.** The recovered pairing is written onto the review row as a
suggestion naming both identifiers and the evidence, and read out for a human each run. Precision
is good, not perfect — two genuinely adjacent invoices that happen to share an amount are
indistinguishable from a typo, and no threshold fixes that.

Finally, **read the error pattern, not just the rows**. The recovered cases were systematically
OCR — `W` read as `VV`, `G` as `6`, dropped digits — which makes it a vendor-side scanning problem
worth raising upstream, not merely a matching gap to patch locally.

### Disqualifying one side of a match does not release the other

A statement row matched a record in the CRM, the match was judged not to qualify during
review, and the row settled on **No Action**. That reads as closed. It is not: the statement
row is still bound to the record it should never have matched, so it appears on no review
pile, and the purchase that actually earned the credit is never looked for. The credit was
**absorbed**, not resolved.

Two fixes, and they are not alternatives:

- **At the join.** The residual lookup that produced the bad pairing matched on invoice
  reference without filtering record type, so a nine-year-old *outgoing payment* was returned
  for a reused four-digit reference. Adding the record-type filter the main pull already used
  closed it. Verified by re-running the lookup: it now returns nothing for that reference.
- **As a backstop.** The join fix cannot catch the general case, where a legitimate match is
  disqualified by a *human* during review — that happens after the run, on judgement no filter
  encodes. So the run also reports credited statement rows whose bound record holds no credit.

**Make the backstop narrow or it will be ignored.** "Credited row on No Action" alone was ~85
rows a month, nearly all legitimate — a row whose note names the record already holding the
credit has lost nothing. What distinguishes a real absorption is that the credit is booked
**nowhere**: the statement side credited, a real record bound, and that record carrying no
reward status and no points. That is 1 row of 209. A *rejected* statement row sitting on No
Action is never an absorption — that is the duplicate branch, where no action is the answer.

The general shape: **when a reconciliation consumes a row from each side, invalidating one side
has to put the other side back.** A pile called "no action" will otherwise accumulate exactly
the items that most need one.

### Quote the source's reason; don't assert the common case

A no-action note explained a statement rejection as "the rejection is a duplicate" —
hardcoded, on every row taking that branch. The claim was *inferred* from a scan proving an
approved confirmation number is never genuinely re-rejected, so the rejection had to be a
resubmission.

It was right about the common case and wrong as a general statement. The statement carries
**six distinct rejection reasons**; the duplicate one is merely the most frequent. One row on
the branch had been rejected as an illegible invoice, and the note called it a duplicate —
a claim the source never made, in a packet a human signs off on.

The statement's own reason was already being carried through the pipeline, one column over.
**Cite it.** Three rules make that safe:

- **Fall back, never fabricate.** A blank reason renders as `0` by the source-doc convention.
  Treat `0` as absent and revert to the inferential wording rather than quoting an empty
  string — the note should say what is known and no more.
- **Show the evidence that makes the branch safe.** Where the statement's confirmation number
  differs from the one on the record, say so inline: that difference *is* the resubmission
  signature, and it turns the reviewer's check from trusting a rule into reading two values.
  Omit the clause when the two agree, rather than printing a non-difference.
- **A generated note is a claim.** Anything auto-written into a review packet carries the same
  burden as a sentence a person wrote. Prefer the source's words to your summary of them.

Reviewing the branch this way also confirmed the **disregard-token suppressor** is doing real
work: every row where the confirmation numbers *agreed* — where the record's own submission was
the rejected one — was already human-annotated (points awarded at the programme contact's
discretion, or the duplicate marking disputed and verified). None reached the tab. The
suppressor is not a convenience; it is what keeps adjudicated rows out of the pile.

### A gallons-only difference is still a write

Gallons was added to a reconciliation whose **routing predates it**. The route decision
defaults to *no change* and every branch below it keys on status, points and dollars only —
gallons is never consulted. So a row whose **only** difference is gallons can never reach the
proposed-writes tab, and a side tab has to catch it.

That side tab is a symptom, not a design. The fix is to treat a gallons difference as what it
is — a proposed write — and promote such rows into the normal write path. Afterwards the side
tab should be **empty every month**, which makes it a useful canary: anything landing there
means the router dropped something.

**Order matters, and getting it wrong is silent.** There is a separate rule that *holds*
gallons on any row sitting on a human review pile — reviewers confirm the figure from their
own sheet, so the CRM is not pre-filled underneath an open review. If that hold runs inside
the classifier, it runs **too early**: a later residual-matching pass re-routes rows, and
every row demoted to a review pile *after* the hold keeps a live staged gallons write. On one
run this was 32 rows re-routed and 22 that kept a write the hold existed to prevent — and they
surfaced on the side tab with Approve defaulting to `yes`.

Settle gallons **once, after routing is final**: promote first, then hold. Both steps belong
in a single function called from the orchestrator, not inside the classifier.

### Every residual lookup needs the main pull's filters

The main extract is scoped to purchase-type records. A residual "find the twin by invoice
reference" lookup is a *different query*, and if it is written without that same record-type
filter it will happily return non-purchase records — a **payout**, for instance, which cannot
earn rewards at all. One reached the proposed-writes tab staged as approved.

The lesson generalises beyond this field: **when a sleuth query exists to find what the main
pull missed, it must still inherit every correctness filter the main pull applies.** Only the
*reach* should widen, never the *eligibility*. Audit each residual query against the main
extract's WHERE clause.

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

**A pass-through pair shares a purchase, never its values.** A `$0` pass-through-retailer tx and its wholesale twin are ONE purchase recorded twice in SF. Tie them so the pair is visible, but write each record the values from **its own** statement row, matched on its own invoice number — retailer row values to the retailer tx, wholesale row values to the wholesale tx. Never stage a retailer statement row's conf / points / volume onto the wholesale record. The tie is a linkage, not a channel for moving values. Where both rows carry the same awarded volume the rewards program credited the purchase twice: that is a question for the program contact, not something the write logic should net out — inventing a correction to a vendor-side error hides the error.

**The `$0` retailer record stays empty — it is a linkage record.** Bring `$0` placeholders into scope so the resolver has an anchor, but write them nothing: the wholesale twin takes its own statement row's values and the `$0` retailer record routes to No Action. Writing both sides would record the same awarded volume twice, and volume is the metric the manufacturer measures the contractor on. This makes the long-standing "`$0` placeholders sit unset" behaviour a **deliberate end state rather than a waiting state**. The expected effect of widening the pull is therefore *fewer review rows, not more writes* — a useful prediction to check the change against. No Action here is conditional on the current-statement guard below.

**The Phase 3b blind spot is the anchor, not the dedupe.** The resolver already routes a matched retailer+wholesale pair to No Action. Both of its paths need a foothold in SF: the document path needs a wholesale invoice PDF findable by the retailer invoice number, and the Work-Order fallback needs an SF *retailer* transaction holding that invoice in order to reach the WO. A retailer invoice that exists **only on the statement** has neither and falls through as unmatched — which is literal, not a matching failure. The human recovery is the receipt: retailer invoice number → receipts inbox → the **ship-to name** on the page carrying that invoice → the Work Order → transactions on that WO near the invoice date → confirm by cross-referencing line items against the wholesale invoice. Screening candidates by awarded volume and date alone is **not** sufficient — it returns multiple candidates and can select one on the wrong Work Order.

**An open state is not evidence that credit is coming.** Routing a row to No Action because its wholesale twin is still `Submitted` assumes that submission will be processed. Confirm the twin's `ReferenceId__c` actually appears as a **credited row on the current statement** first; an entire submission batch can go unprocessed, and without this guard the whole batch reads as "no action" while its credit is stranded. Reconciliation is two-directional — what was submitted and never processed is as much a finding as what was processed and never recorded.

**Order the recovery steps by cost and certainty, and say which are last resorts.** A row settled from the statement alone must never pay for a document search, a mailbox search or a PDF download. A workable order: exact identifier match → same-distributor re-submission (statement-only) → document/Work-Order resolver → mailbox by invoice spellings → mailbox by **submission id** → exact identifier lookup in the CRM → the full receipt trace. The two cheapest steps resolve the most rows; the expensive ones exist for the residual.

**A vendor writes the invoice differently on the statement than on the receipt, and each vendor is wrong in its own way.** Keep per-vendor spelling rules in a table keyed by vendor, always try the exact number first, and scope every rule to the vendor that demonstrated it — these rules trim REAL characters, so a rule leaking across vendors manufactures searches for invoices that never existed. **Collect hits across ALL spellings before choosing one:** twice an *unlabelled* copy under the exact number masked the *labelled* copy under a stripped form, and the label was what decided the row. Rank your own automated summary emails last — a digest that enumerates every invoice it processed matches almost any search and will otherwise be reported as "receipt found" for an invoice that has none.

**A submission/batch identifier is a second, independent mailbox key.** It is not derived from the invoice, so it survives every transcription error — including invoices mangled beyond any spelling rule. Try it after the invoice spellings: an invoice hit is more specific, a submission covers a whole batch.

**Recovering a mis-transcribed identifier: the amount selects, the similarity only confirms.** Query by exact amount first, then filter by edit distance — never the reverse. Sequential invoices inside one batch differ by exactly one character and look identical to a typo, so similarity can never be the selector. Require a to-the-cent amount agreement, exactly one survivor, a minimum amount below which the figure is too common to be evidence, and abort entirely if any record holds the statement's identifier exactly. Known transcription classes seen in practice: letter→digit substitutions in both directions, one letter read as two, and a punctuation mark read as a digit.

**A last-resort lookup IDENTIFIES; it does not decide.** A lookup that deliberately ignores the pull's filters will reach records the pull excluded on purpose (zero-amount placeholders, credit memos, out-of-window rows, unflagged vendors). Naming the record is the whole value. Stress-tested at scale, allowing such a path to stage writes produced status **downgrades** on live records — the exact thing the auto-update rules forbid. Clear every proposed-change column on that path, require exactly one candidate, never bind onto a record already marked rejected, and never leave a row on the write tab with nothing to write.

**Two more shapes worth stating plainly.** *The bar for filing a pass-through row is that its twin is NOT REJECTED, not that it is credited* — a twin still awaiting processing accounts for the purchase and will land on a later statement; only a rejection kills the credit. And *a warning is a note, not a gate*: a row that resolves should leave the review pile carrying its warning, because holding a solved row to convey a message makes the reviewer re-solve it every cycle.

**Line items prove identity, not volume.** Matching SKU and quantity across two documents is strong evidence they describe the same purchase — far harder to fake than amount or date, which are exactly what fail on pass-through rows. It says nothing about how much was supplied: one validated pair matched perfectly on every SKU and quantity while the retailer shipped five-gallon units and the manufacturer billed single gallons, a 12-gallon gap on a 25-gallon purchase, in the one unit the manufacturer measures the contractor on. Compute volume separately, and compare only line pairs where **both** sides state a unit size — scoring an unstated size as zero inflates a real gap into a fictitious larger one, which is the same error class the check exists to catch.

**A real amount means it is NOT a pass-through.** A `$0` pass-through is either a `$0` transaction in the CRM or **no transaction at all** — so a retailer transaction carrying a real amount is a direct purchase, and it matches the statement row whose **awarded/total amount equals that amount**, even when its stored reference number says otherwise. A reference keyed one digit off is common; the amount is the physical fact. The corollary matters more: a statement row with a blank or `$0.00` total and real awarded volume is the pass-through half, and binding it to a real-dollar transaction stages volume and points onto a purchase that did not earn them. Three such bindings were staged on one cycle before this rule was written down.

⚠️ **A vendor's combined daily invoice PDF holds MANY invoices — parse only the page carrying yours.** Summing every page of one attachment produced a volume figure that reversed the conclusion twice: once against a prior correct note, once in favour of it. Both the `$0` pass-through page and the real-amount page live in the same file, and it is the per-page totals that separate them. Any helper that concatenates a whole document must not be used to judge a single invoice.

⚠️ **When a stored conclusion and today's data disagree, get the primary document before choosing.** A note from a prior cycle recorded the opposite verdict on these same records. It was not wrong when written — it predated knowing that the `$0` row is the one with no CRM transaction. Neither the old note nor a fresh inference settles it; the receipt page does, and it was one function call away the whole time.

**Read the destination before appending to it.** Moving reviewer-resolved rows onto a write-staging tab without first checking what that tab already held produced duplicate staged writes for a third of the batch, several of them a *second* confirmation number for a record that can hold one. Then deleting those duplicates — the rows having already been removed from the source tab — destroyed data outright, because a move is two operations and only the pair is safe. Related: a tab whose notes reference other rows **by row number** silently breaks when rows are removed; grep for such references before reordering.

**A `$0` amount filter silently removes the pass-through population.** Where the SF pull mirrors a source report filtered to `Amount__c > 0`, every `$0` pass-through placeholder is excluded from the reconciliation — so the retailer side of each pair can never be matched or written, and those rows return to the review pile every month. Check the pull's amount filter before treating a recurring unmatched pile as a matching problem.

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

## Run notifications

Run summaries, failures, reverts and apply confirmations are **emailed to the admin account**. There is no group post.

⚠️ This replaced a Slack path that **had never worked** — the token the code read carried a purely read-only scope set (no `chat:write` at all), it pointed at a different workspace than the app that was meant to send, and an earlier incarnation spent ~3 months posting to a decommissioned server. Every failure was silent. Do not reintroduce a channel without sending a real test message through the real credentials first; see "prove an alert channel can send before trusting it".

---

## Schedule

launchd job (`com.ppp.bmcr-recon.plist`):
- Fires daily at 8:00 AM
- Self-gates: only proceeds on days 1–9 of the month
- "Already ran this month" guard prevents duplicate runs
- If no BMCR email found by day 9 → notifies admin via DM, exits
