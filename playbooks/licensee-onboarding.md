# Playbook — Onboarding a New PPP Licensee

Repeatable process for setting up a new Precision Painting Plus licensee in Salesforce. Conventions only — specific licensee names, contacts, addresses, and per-licensee Salesforce IDs live in the private admin records, not here.

> Some licensees are existing Service Territories converting to a licensee model; others are net-new. The territory steps differ, but everything else (metadata, document gating, LGS email, Closed-Won flow) is the same.

---

## 1. Decision tree — lightweight vs full branded

Two paths exist. Pick before building.

| Lightweight (the default) | Full branded build |
|---|---|
| Licensee operates under the PPP brand (uses PPP logo + assets) | Licensee has its own distinct brand identity |
| Identity gate (custom permission + permset + User flag) + **territory-based** document gating | Identity gate + per-licensee cloned branded templates + filtered Detail Buttons + Contract LWC + dedicated Lightning App + email-flow per-licensee branching |
| ~Hours of work per licensee | Days of work per licensee |
| Scales by adding territory names to existing RENDER conditions | Each new licensee = new template set |

Even on the heavier path, the lightweight metadata (custom permission + permset + User flag) is still the foundation — it's the identity gate the branded path also relies on.

---

## 2. Intake — what to collect from the licensee

Sent as a templated email before any Salesforce config. The canonical list:

- **Legal entity** + **dba** (separate fields).
- **Customer-facing company name** as it should appear on invoices/quotes.
- **Primary business address** — this is what prints on the licensee's "Mail payments to:" line.
- **Service area** — existing PPP Service Territory or net-new (city/county/region + ZIPs).
- **Sales tax rate(s)** for the service area (single number per territory — PPP has no per-licensee or per-brand tax mechanism; rate lives on the ServiceTerritory).
- **License number(s)** to print on customer-facing documents.
- **Primary contact + user(s)** who need Salesforce access.
- Logo + brand assets — **only if going branded**. Skip for the lightweight path.

---

## 3. Lightweight setup — the recommended path

### 3a. Metadata (4 components per licensee)

Author in sandbox, deploy to prod via `sf project deploy start --metadata …`.

- **`CustomPermission:<LicenseeName>`** — gates licensee-only behavior. Name = company in `Underscore_Format` (no spaces).
- **`CustomField:User.Licensee_<X>__c`** — Checkbox. Marker for licensee users. Boolean, defaultValue false. (Kept even though current gating is territory-based — see §5 — as the identity-gate convention.)
- **`PermissionSet:<LicenseeName>`** — enables the CustomPermission and grants Read FLS on the new User field. Assigned to licensee users.
- **`PermissionSet:Licensee_<X>_Field_Access`** — admin Read/Edit on the User flag. Does NOT grant the custom permission. Assigned to admins who need to maintain the flag.

The two permission sets and the User field are deployed together (the permsets reference both the custom permission and the field).

### 3b. ServiceTerritory — the must-set fields

Whether converting an existing territory or building a new one, **these fields must be set** for downstream automation and documents to work:

| Field | Why it matters |
|---|---|
| **`PriceBook__c`** (lookup to `Pricebook2`) ⚠️ | Required. The `Opportunity_SetServiceTerritoryAndOwner` flow stamps `Opportunity.Pricebook2Id = ServiceTerritory.PriceBook__c` on Lead/Opp conversion. Blank → no pricebook on the Opp → quotes can't add line items. Most common new-territory miss. |
| `Company_Name__c` (text) | The customer-facing company on document headers + the licensee "Mail payments to:" line. |
| `dbaName__c` (text) | The dba line under the company. Convention: `<Legal Entity> dba <Operating Brand>` (e.g. `<LegalEntity, LLC> dba <Operating Brand>`). |
| `Licenses__c` (text) | Renders in the header `Licenses:` line (gated to hide when blank — see §5b). |
| `TaxRate__c` (percent) | Geographic sales tax rate. PPP has no per-licensee tax mechanism. |
| Street / City / State / PostalCode / Country | Address used in routing and on doc footers. Should be the licensee's actual business address. |
| `OperatingHoursId`, `ParentTerritoryId`, `IsActive` | Standard FSL setup; mirror the regional convention. |

**FSL dependencies** (net-new territory only):
- `OperatingHours` (territory + member-level may differ).
- `ServiceResource` for the licensee user — `RelatedRecordId = User.Id`, `ResourceType = T`, `IsActive = true`.
- `ServiceTerritoryMember` linking the ServiceResource → territory, `TerritoryType = P` (Primary), active, with the appropriate `OperatingHoursId`.
- `Zip_Code__c` records (custom object) with `Service_Territory__c` set to the territory. Drives assignment (zip → territory).
- The `County` Global Value Set is restricted — if importing zips with new counties, ensure the GVS has those values before insert (deploy prod→sandbox if needed).

### 3c. Licensee user data

For each licensee user:
- **Assign** PermissionSet `<LicenseeName>` (`sf org assign permset --name <LicenseeName> --on-behalf-of <username>`).
- **Set** `User.Licensee_<X>__c = true`.
- **Set** `User.CompanyName` to the licensee's customer-facing company name (matches `ServiceTerritory.Company_Name__c`).
- **Set** `User` Street/City/State/PostalCode/Country to the licensee's business address (this is what the doc header pulls — see §5a).

For each admin who needs to maintain licensee flags:
- **Assign** `Licensee_<X>_Field_Access`.

---

## 4. Customer-facing data conventions

The licensee's identity appears on documents in three places. Set all three consistently:

| Source | Where it renders | Convention |
|---|---|---|
| `ServiceTerritory.Company_Name__c` | Doc header company line + the "Mail payments to:" company line on Invoice / Invoice Email | The customer-facing company / legal entity. |
| `ServiceTerritory.dbaName__c` | Doc header dba line (alongside `Company_Name__c`) | Often `<Legal Entity> dba <Operating Brand>` — but in payment-instructions we render `Company_Name__c` only to avoid redundancy. |
| `User.CompanyName` (on each licensee user) | Currently not directly rendered (templates source from the territory) — kept in sync for internal consistency. | Same as `Company_Name__c`. |

Address: the WO/Invoice header sources its address from **`WorkOrder.CreatedBy.*`** (the WO creator's user record), not from the ServiceTerritory. So the licensee user's `User.Street/City/State/PostalCode` is what prints. Caveat: if a non-licensee user creates the WO (e.g. an admin or CSR), payments would route to their address. Mirror the existing header behavior in the licensee "Mail payments to:" block so the two stay consistent.

---

## 5. SDocs document gating (territory-based)

### ⚠️ Pivotal lesson — S-Docs `RUNNINGUSER` does NOT merge in this org

`{{!RUNNINGUSER.<anything>}}` (even standard `CompanyName`) renders blank in this org. Confirmed via render test. **Do not try user-flag gating** (`{{!RUNNINGUSER.Licensee_<X>__c}}`). Use **record/territory-based** gating — record and relationship merges work fine.

The User flag + custom permission/permset are still deployed (§3a) as the identity-gate convention — but the actual document gating keys on the **territory**.

### 5a. Payment-hide + "Mail payments to:" — on the 2 payment-bearing templates

Two templates carry the PPP "make checks payable / cardknox / Zelle" payment block in their body (`SDOC__Template_XML__c`):
- `PPP Invoice`
- `PPP Invoice Email`

For each, two surgical edits:

1. **Wrap the existing PPP payment block** in a RENDER conditional keyed on the WO's ServiceTerritory `Name`:
   ```
   <!--RENDER=({{!WorkOrder.ServiceTerritory.Name}} != '<LicenseeTerritoryName1>'
            && {{!WorkOrder.ServiceTerritory.Name}} != '<LicenseeTerritoryName2>')-->
     …existing PPP payment block (Check + cardknox + Zelle)…
   <!--ENDRENDER-->
   ```
   Shows for everyone *except* licensee territories. Adding a new licensee = add their territory `Name` to the AND chain.

2. **Add an inverse-gated "Mail payments to:" block** immediately after:
   ```
   <!--RENDER=({{!WorkOrder.ServiceTerritory.Name}} == '<LicenseeTerritoryName1>'
            || {{!WorkOrder.ServiceTerritory.Name}} == '<LicenseeTerritoryName2>')-->
     <p><strong>Mail payments to:</strong></p>
     <p>{{!WorkOrder.Opportunity__r.Service_Territory__r.company_name__c}}<br>
        {{!WorkOrder.CreatedBy.street}},
        {{!WorkOrder.CreatedBy.city}},
        {{!WorkOrder.CreatedBy.state}}
        {{!WorkOrder.CreatedBy.postalcode}}</p>
   <!--ENDRENDER-->
   ```
   - **Company line** uses `company_name__c` only (no dba) — avoids redundancy.
   - **Address** uses `WorkOrder.CreatedBy.*` so the payment address matches the doc header's address. (See §4 caveat.)

`==` / `||` operators are supported in S-Docs RENDER expressions in this org.

### 5b. Header "Licenses:" — gate to hide when blank, on all 7 templates that carry it

The header (separate field `SDOC__Header__c`, **not** the body) contains a `<strong>Licenses:</strong> {{!<path>.licenses__c}}` line on these 7 templates:

| Template | Base object → path to `licenses__c` |
|---|---|
| Invoice / Work Order / Receipt | `WorkOrder.Opportunity__r.Service_Territory__r.licenses__c` |
| Quote / Contract | `Quote.Opportunity.Service_Territory__r.licenses__c` |
| Change Order | `ChangeOrder__c.WorkOrder__r.Opportunity__r.Service_Territory__r.licenses__c` |
| Warranty | `Case.Account.Service_Territory__r.licenses__c` |

Each template's base object dictates the path. Wrap the existing `<br />` + `<strong>Licenses:</strong> {{!…licenses__c}}` in a RENDER conditional that shows only when the value is non-empty:
```
<!--RENDER=({{!<that template's licenses__c path>}} != '')-->
   <br /><strong>Licenses:</strong> {{!<that path>}}
<!--ENDRENDER-->
```

**Scope note:** this affects **all** documents org-wide, not just licensees. A territory with blank `Licenses__c` no longer shows an empty "Licenses:" line. Cosmetic improvement; verify it's intended before rolling out.

### 5c. SDocs storage convention reminder

- Templates are **data** (records on `SDOC__SDTemplate__c`), not metadata. Move edits via direct REST PATCH, not `sf project deploy`.
- The body is in `SDOC__Template_XML__c`. The header / footer are in **separate fields** on the same record:
  - `SDOC__Header__c`, `SDOC__Header2__c`, `SDOC__HeaderSame__c`
  - `SDOC__Footer__c`, `SDOC__Footer2__c`, `SDOC__FooterSame__c`
  - MS Word variants: `SDOC__MS_FPHeader_Content__c`, `SDOC__MS_SPHeader_Content__c`, etc.

For the broader SDocs template prod↔sandbox sync workflow, see `sdocs-templates.md`.

---

## 6. "Let's Get Started" email — Closed Won flow branching

### Mechanism

Opportunity → Closed Won → `Opportunity_WorkOrderWhenClosedWon` flow creates the WorkOrder → **`WorkOrder_SendLetsGetStartedEmail`** flow (record-triggered on WorkOrder Create) sends the email.

Inside the LGS flow:
- Checks opt-out, primary-contact email, bounce.
- Branches on AM status (`AM_Status_is_Same_or_Different`).
- Each branch calls subflow `FlowLib_GetActiveEmailTemplateByName` with a hardcoded `varTemplateName` (`"NEW Let's Get Started"` on the AM path, `"Let's Get Started No AM"` on the No-AM path).
- Sends the resolved template via `emailSimple`.

### Licensee design

These are **custom HTML Lightning email templates** (`TemplateType=custom`, `IsBuilderContent=true`, `RelatedEntityType=WorkOrder`). HTML email templates have **no conditional block rendering** (RENDER conditionals only work in S-Docs templates), so the licensee variant must be a separate template — branching lives in the flow.

Decisions used:
- **For licensees, always route to the No-AM variant** (regardless of AM status). The No-AM source intro is AM-free already, which fits the licensee-shouldn't-show-AM-intro requirement. One licensee template covers both paths.
- **Strip the PPP "PAYMENT OPTIONS"** block (CardKnox + Zelle + Check).
- **Add a payment instruction line** before the Work Order # line, e.g. *"Payments can be mailed to the address listed on your contract."*

### Template creation — UI clone, then API patch

> Lightning email templates' image content and `IsBuilderContent=true` are managed by the builder's internal storage. **REST clones lose both** — clones render `{{{…}}}` merges literally and show broken images. UI clones preserve both.

1. **UI clone** the source `Let's Get Started No AM` in the Lightning Email Template Builder. Name it `Let's Get Started No AM (Licensee)` (or whichever Name the flow formula will return — see below).
2. **API PATCH** the new template's `HtmlValue` (and `Body`) to strip the PAYMENT OPTIONS block + insert the payment instruction line before the Work Order # line. `HtmlValue` is updatable on a UI-cloned template without disturbing `IsBuilderContent` or image content.

If the UI clone fails with **"Lightning Page ID"**, open the source and resave it first. If the resave fails with **`Attribute "src" on element <img> is not allowed`**, the source template has dangling image refs (sandbox-refresh artifact — see §8).

### Flow edit — formulas, not connector rewiring

Edit the flow **surgically**. Do NOT deploy a sandbox flow wholesale to prod — sandbox + prod versions may diverge.

1. Retrieve the prod flow (`sf project retrieve start --metadata "Flow:WorkOrder_SendLetsGetStartedEmail"`).
2. Add 2 `<formulas>` resources right before the first existing `<formulas>`:
   - **`fGetStartedTemplateName_AM`** (String): `IF(<licensee territory match>, "Let's Get Started No AM (Licensee)", "NEW Let's Get Started")`
   - **`fGetStartedTemplateName_NoAM`** (String): `IF(<licensee territory match>, "Let's Get Started No AM (Licensee)", "Let's Get Started No AM")`
   - Both formulas, for licensees, point to the **same** No-AM-Licensee template.
   - Licensee territory match uses the same key as the SDocs gating, e.g. `OR({!$Record.Opportunity__r.Service_Territory__r.Name} = "<TerritoryName1>", {!$Record.Opportunity__r.Service_Territory__r.Name} = "<TerritoryName2>")`.
   - XML-escape the expression: `"` → `&quot;`, `'` → `&apos;`.
3. **Repoint** both subflow `<inputAssignments>` for `varTemplateName` — change from `<stringValue>…</stringValue>` to `<elementReference>fGetStartedTemplateName_AM</elementReference>` / `…_NoAM`. The flow now resolves the template Name through the formula, which picks licensee vs standard per the territory.
4. Deploy.
5. **Verify Active.** Flow deploys can silently land Draft — see `[[reference_flow_deploy_draft_quirk]]`. Query the tooling API:
   ```sql
   SELECT VersionNumber, Status FROM Flow
   WHERE Definition.DeveloperName='WorkOrder_SendLetsGetStartedEmail'
   ORDER BY VersionNumber DESC
   ```
   If the new version is `Draft`, deploy a `FlowDefinition` with `<activeVersionNumber>N</activeVersionNumber>` to activate it.

Adding a future licensee = add their territory Name to both formulas' condition. No flow connector rewiring.

---

## 7. Production promotion — order of operations

Tested order (2026-06). Sequence matters because parts couple.

1. **Metadata deploy** — CustomPermissions + CustomFields + PermissionSets (4 components per licensee).
2. **LGS template** — admin UI-clones in prod (`Let's Get Started No AM` → `Let's Get Started No AM (Licensee)`). Then API PATCH the HtmlValue (strip + add line).
3. **LGS flow** — surgically edit the prod flow (add 2 formulas + repoint 2 subflow inputs). Deploy. **Verify Active** (activate via FlowDefinition deploy if it landed Draft).
4. **SDocs template edits** — REST PATCH the 9 edits (Invoice + Invoice Email body, plus the 7 templates with the header `Licenses:` line). Back up the original field values to disk first.
5. **Territory data** — set `Company_Name__c`, `dbaName__c`, `PriceBook__c`, address on each licensee's ServiceTerritory.
6. **User data** — set `CompanyName`, address, `Licensee_<X>__c = true` on each licensee user.
7. **Assignments** — `<LicenseeName>` permset → licensee users; `Licensee_<X>_Field_Access` → admins.
8. **Verification** — generate a real Invoice for a licensee WO; take a real licensee-territory opp to Closed Won; spot-check renders.

Coupling notes:
- Steps **4 + 5 are coupled** — without step 5, a licensee invoice would render "Mail payments to: <stale company name>". Run together.
- Steps **2 + 3 are coupled** — the flow formula references the new template by Name, so the template must exist with the correct Name when the flow deploys (deploy fails Name lookups at activation otherwise).

---

## 8. Common gotchas

### S-Docs RUNNINGUSER doesn't merge
`{{!RUNNINGUSER.<anything>}}` returns blank. Use territory-based gating instead. See §5.

### Lightning email template clones via REST lose IsBuilderContent + image content
`IsBuilderContent` is system-controlled (not writable via API). REST clones inherit `false` → `{{{…}}}` merges render literally and images are broken. **Always UI-clone** Lightning email templates; API can patch HtmlValue after.

### Flow deploys can land Draft
Even when the source XML has `<status>Active</status>`, the new version may activate as Draft and leave the previous version active. Always verify post-deploy; activate via `FlowDefinition` deploy if needed. See `[[reference_flow_deploy_draft_quirk]]`.

### ServiceTerritory.PriceBook__c is critical for conversion
The most common new-territory miss. Without it, `Opportunity_SetServiceTerritoryAndOwner` stamps `Opportunity.Pricebook2Id = null` on conversion, and downstream Quotes can't add line items ("there is no pricebook for the product"). Set it during territory build.

### ContentAsset can't be created via REST
`ContentDocumentId` rejects on insert. To replicate prod images into sandbox (when sandbox-refresh leaves dangling image refs):
1. Copy the prod `ContentVersion` binary → POST as a new sandbox `ContentVersion` (`VersionData` as base64).
2. POST a `ContentDistribution` for the new ContentVersion to get a stable, anonymous **public download URL** via the `ContentDownloadUrl` formula field.
3. Patch the Lightning email template `HtmlValue` `<img src="">` with the new URL (match by `alt=`).
- Prod doesn't need this fix — its image refs work natively.

### Field FLS may drift in sandbox
Field users (e.g. `Project_Estimator_full_license` permset members) may lack reads in sandbox on fields they have in prod, e.g. `WorkOrder.Total_Payment_Terms__c`. Symptom: SDocs render error `No such column 'total_payment_terms__c' on entity 'WorkOrder'`. Quick fix: assign the purpose-built `WorkOrder_Total_Payment_Terms_Edit` permset to the test user. See `[[reference_sf_field_deploy_fls_gotcha]]` for the broader FLS-on-deploy gotcha.

### Sandbox uses the same Pricebook2 IDs as prod
Pricebook2 IDs survive sandbox refresh. So you can set `ServiceTerritory.PriceBook__c` to the same Id in both orgs. Same for User IDs.

---

## 9. Rollback

For each edit type, the rollback path:

- **SDocs template edits** — back up the prod field value (body / header) to disk before each PATCH. To revert: PATCH the field back from the backup file.
- **Flow** — deploying a `FlowDefinition` with the previous `<activeVersionNumber>` re-activates the prior version. Old versions are kept as Obsolete, not deleted.
- **EmailTemplate (LGS Licensee) HtmlValue** — same backup-then-PATCH-back pattern as SDocs.
- **Metadata (custom permission / permset / User field)** — delete via Setup UI or `sf project deploy --pre-destructive-changes`. Permsets must be unassigned first.
- **Data (`ServiceTerritory` / `User`)** — query and save the original field values before update; restore via PATCH.

---

## Cross-references

- `sdocs-templates.md` — S-Docs / S-Sign mechanics, RENDER syntax, prod↔sandbox sync.
- `sandbox-update-testing.md` — broader sandbox testing workflow (managed-package upgrades, config changes).
- `salesforce/BUSINESS_RULES.md` — PPP conventions (sales metric, quota, sales tax, profile naming).
- The private admin's project doc captures the licensee-specific Salesforce IDs, addresses, permset names, and per-licensee values that are intentionally excluded here.
