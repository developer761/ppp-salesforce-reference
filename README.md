# PPP Salesforce — Shared Knowledge Base

Shared reference for Precision Painting Plus Salesforce work — schema, business rules, KPI definitions, and process playbooks — used across PPP's internal admin work and the Command Center engagement. Salesforce is the source of truth; this is a curated reference layer.

**For AI assistants:** see [`CLAUDE.md`](./CLAUDE.md) — it's the index + conventions and auto-loads in Claude Code sessions.

## 🔒 This repo is public — curated content only

No compensation data, no PII (names/emails/IDs tied to performance), no customer/account data, no secrets, no unrelated projects. Schema, conventions, and *logic* only. Full rules in [`CLAUDE.md`](./CLAUDE.md). The sensitive/detailed versions of this knowledge stay in private admin notes.

## Layout

| Path | What |
|---|---|
| `CLAUDE.md` | Shared-memory hub: index, core conventions, curation rules. |
| `salesforce/` | Schema & metric definitions. |
| `salesforce/BUSINESS_RULES.md` | Conventions + field gotchas — **start here for SOQL.** |
| `salesforce/DATA_DICTIONARY.md` | Full schema snapshot (fields, objects, flows, rules). Production, 2026-05-11. |
| `salesforce/REP_PERFORMANCE_KPIS.md` | Rep-scorecard KPI definitions (sanitized). |
| `salesforce/architecture_*.md` | Object-relationship maps (Mermaid). |
| `salesforce/reference-code/` | Example SOQL + aggregation (Python, no real data). |
| `command-center/` | PPP Command Center app docs. |
| `command-center/REP_PROFILES_INTEGRATION_GUIDE.md` | Wiring PPP KPIs into the Command Center Rep Profiles. |
| `playbooks/` | Repeatable PPP Salesforce processes (licensee onboarding, sandbox update testing, S-Docs templates). |

## Using it as shared memory

- **Command Center / app work:** clone this repo alongside the app (or reference it from the app's `CLAUDE.md`) so AI sessions read these definitions automatically.
- **PPP admin work:** clone to a fixed path and point to it from your `~/.claude/CLAUDE.md`.
- **Updating:** edit the relevant doc (sanitized), add a one-line pointer in `CLAUDE.md`, commit.
