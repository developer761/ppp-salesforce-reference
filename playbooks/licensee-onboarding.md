# Playbook — Onboarding a New PPP Licensee

Repeatable process for setting up a new Precision Painting Plus licensee in Salesforce. Conventions only — specific licensee names, contacts, and any per-licensee data live in the private admin records, not here.

> Some licensees are existing Service Territories converting to a licensee model; others are net-new. The steps are the same; conversions just reuse the existing Service Territory record.

## What you collect from the licensee first

An intake checklist (sent as a templated email) gathers the items needed before any Salesforce config:
- Legal/DBA business name and branding (logo, colors) for document templates.
- Primary contact + users who need Salesforce access.
- Service area / territory definition.
- Any licensee-specific document or email wording.

## Salesforce setup steps

1. **Custom permission + permission set** — a licensee-specific custom permission gates licensee-only behavior; a permission set assigns it (and any object/field access) to the licensee's users. PPP uses a granular permission-set model — see `salesforce/BUSINESS_RULES.md`.
2. **Branded document templates** — clone the standard S-Docs templates for **Quote, Work Order, Contract, and Invoice**, plus the **email variants** of each, and rebrand them for the licensee. See `sdocs-templates.md` for S-Docs conventions.
3. **Licensee-only Lightning App** — a dedicated app so licensee users see only their relevant tabs/objects.
4. **Email-flow branching** — outbound email flows branch on the licensee so the right branded template and sender are used. The licensee is identified on the User record (a licensee field on User); flows and document logic key off it.

## Conventions & gotchas

- **Licensee identity on User:** licensee membership is stored on the User record and is what email flows / document RENDER logic branch on. (S-Docs RENDER conditional syntax + the licensee payment-hide pattern are covered in `sdocs-templates.md`.)
- **Document templates are per-brand:** every licensee gets its own cloned + rebranded set rather than one conditional template, to keep branding clean.
- **Conversions reuse the Service Territory:** when an existing Service Territory becomes a licensee, keep the territory record and layer the licensee permission/app/templates on top.

For the field-level S-Docs mechanics (RENDER blocks, running-user fields, payment-section hiding), see `sdocs-templates.md`.
