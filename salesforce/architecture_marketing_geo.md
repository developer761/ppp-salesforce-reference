# PPP Salesforce — Marketing & Geography Architecture

Single combined map: Account is the root. Ad spend roll-up (with Zip Code between Service Territory and Lead/Opportunity) is the main branch; Marketing Profile → Review is the side branch.

← Back to [main map](architecture_main.md) · sibling: [Compliance](architecture_compliance.md)

---

## Marketing & Geography map

```mermaid
flowchart TB
    classDef mkt fill:#fce7f3,stroke:#9d174d,color:#831843
    classDef ext fill:#fde68a,stroke:#b45309,color:#7c2d12,stroke-dasharray: 4 3

    Account([Account]):::ext
    ST([Service Territory]):::ext
    Lead([Lead]):::ext
    Opportunity([Opportunity]):::ext
    WO([Work Order]):::ext

    subgraph AdSpend[Ad Spend & Geography]
        direction TB
        ACS[Ad Cost Summary]:::mkt
        MS[Master Spend]:::mkt
        ACD[Ad Cost Detail]:::mkt
        Zip[Zip Code]:::mkt

        ACS --> MS
        ACS --> ACD
        MS --> ACD
    end

    subgraph MpBranch[Marketing Profile & Reviews]
        direction TB
        MP[Marketing Profile]:::mkt
        Review:::mkt
        MP --> Review
    end

    Account --> ST
    Account --> ACD
    Account --> MP
    Account --> Review

    ST --> ACD
    ST --> Zip
    ST --> Lead
    ST --> Opportunity

    Zip --> Opportunity
    ACD --> Lead
    ACD --> Opportunity

    Opportunity --> Review
    WO --> Review
```

---

## Standalone reference records

These have no FK relationships in the dictionary — they're reference tables joined by Name or referenced via reporting, not lookups:
- `Angi_Profile__c` — Angi lead-source profile (id + name)
- `HomeAdvisor_Profile__c` — HomeAdvisor lead-source profile (id + name)
- `Region__c` — region master list

---

## Cross-map links

Everything dashed/amber on the chart lives on the [main map](architecture_main.md):
- `Account`, `Lead`, `Opportunity` → Sales Pipeline
- `Service Territory`, `Work Order` → Service Delivery cluster
