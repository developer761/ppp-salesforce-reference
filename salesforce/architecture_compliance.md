# PPP Salesforce — Compliance Architecture

Corporate documents, policy documents, audits, legal matters, and the Association junction that ties them to staff/vehicles/accounts.

← Back to [main map](architecture_main.md) · sibling: [Marketing & Geography](architecture_marketing_geo.md)

---

## Compliance objects & connections

`Corporate_Document__c` is the master library (insurance certs, contractor agreements, etc.). `Policy_Document__c` is an internal HR/safety policy parented to a Corporate Document. `Audit__c` is a periodic review of either. `Legal__c` is the master matter record with broad fan-in. `Association__c` is the junction that links Corporate Documents and Legal matters to the parties / assets they cover. `DocumentRequirement__c` flags required docs per Work Order.

```mermaid
flowchart TB
    classDef compl fill:#fee2e2,stroke:#991b1b,color:#7f1d1d
    classDef ext fill:#fde68a,stroke:#b45309,color:#7c2d12,stroke-dasharray: 4 3

    CD[Corporate Document]:::compl
    PD[Policy Document]:::compl
    Aud[Audit]:::compl
    Legal:::compl
    Assn[Association]:::compl
    DR[Document Requirement]:::compl

    CD --> PD
    CD --> Aud
    PD --> Aud
    CD --> Assn
    Legal --> Assn

    Account([Account]):::ext --> CD
    Account --> Legal
    Account --> Assn
    Vehicle([Vehicle]):::ext --> CD
    Vehicle --> PD
    Vehicle --> Legal
    Vehicle --> Assn
    WO([Work Order]):::ext --> CD
    WO --> Legal
    WO --> DR
    Contact([Contact]):::ext --> Legal
    Case([Case]):::ext --> Legal
    User([User]):::ext --> Legal
    Staff([SFDC Staff]):::ext --> Assn
```

---

## Cross-map links

Everything dashed/amber above lives on the [main map](architecture_main.md):
- `Account`, `Contact`, `User`, `Work Order`, `Case` → Sales Pipeline / Service Delivery clusters
- `Vehicle`, `SFDC Staff` → Fleet & Quota cluster
