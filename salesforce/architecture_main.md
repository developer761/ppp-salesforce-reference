# PPP Salesforce — Main Architecture Map

Visual map of regularly-used Salesforce objects and how they connect. Based on the 2026-05-11 production snapshot dictionary.

**Sub-maps:**
- [Compliance map](architecture_compliance.md) — Corporate Documents, Policy Documents, Legal, Audits, Association junction, Document Requirement
- [Marketing & Geography map](architecture_marketing_geo.md) — Ad spend, Marketing Profile, Zip Code, standalone profile records

---

## Overview

```mermaid
flowchart LR
    classDef sales fill:#dbeafe,stroke:#1e40af,color:#1e3a8a
    classDef ops fill:#dcfce7,stroke:#166534,color:#14532d
    classDef fq fill:#fef3c7,stroke:#a16207,color:#713f12
    classDef ext fill:#fde68a,stroke:#b45309,color:#7c2d12,stroke-dasharray: 4 3

    S[Sales Pipeline]:::sales
    O[Service Delivery]:::ops
    FQ[Fleet & Quota]:::fq
    C[Compliance Map]:::ext
    M[Marketing & Geo Map]:::ext

    S --> O
    O --> FQ
    S -.-> M
    O -.-> C
    FQ -.-> C
```

---

## Sales Pipeline

Lead converts into Account + Contact + Opportunity; quotes flow off the opportunity. Voice calls and cases hang off the customer-facing side.

```mermaid
flowchart TB
    classDef sales fill:#dbeafe,stroke:#1e40af,color:#1e3a8a

    Lead:::sales
    Account:::sales
    Contact:::sales
    Opportunity:::sales
    Quote:::sales
    QLI[Quote Line Item]:::sales
    Product2:::sales
    Pricebook2:::sales
    Case:::sales
    VoiceCall:::sales

    Lead --> Account
    Account --> Contact
    Account --> Opportunity
    Contact --> Opportunity
    Opportunity --> Quote
    Quote --> QLI
    Product2 --> QLI
    Pricebook2 --> Quote

    Lead --> VoiceCall
    Opportunity --> VoiceCall

    Account --> Case
    Contact --> Case
    Lead --> Case
    Opportunity --> Case
```

---

## Service Delivery

The Opportunity → Work Order spine. Service Appointment branches off early (near Opportunity); Work Order owns everything else — line items, crews, change orders, paint, transactions, payment terms, document requirements, reviews.

```mermaid
flowchart TB
    classDef ops fill:#dcfce7,stroke:#166534,color:#14532d
    classDef sales fill:#dbeafe,stroke:#1e40af,color:#1e3a8a

    Opportunity:::sales
    Quote:::sales
    Case:::sales

    subgraph Schedule[Scheduling]
        direction LR
        SA[Service Appointment]:::ops
        ST[Service Territory]:::ops
    end

    subgraph Execute[Execution]
        direction TB
        WO[Work Order]:::ops
        WOLI[Work Order Line Item]:::ops
        WOC[Work Order Crew]:::ops
        CO[Change Order]:::ops
        COLI[Change Order Line Item]:::ops
        PC[Paint Color]:::ops
        TX[Transaction]:::ops
        PT[Payment Term]:::ops
        DR[Document Requirement]:::ops
        RV[Review]:::ops

        WO --> WOLI
        WO --> WOC
        WO --> CO
        CO --> COLI
        WOLI --> COLI
        WOLI --> PC
        WO --> TX
        WO --> PT
        WO --> DR
        WO --> RV
    end

    Opportunity --> SA
    Opportunity --> WO
    Opportunity --> RV
    ST --> SA
    ST --> WO
    WO --> SA
    Quote --> PT
    WO --> Case
```

---

## Fleet & Quota

Two side-by-side neighborhoods that share `User` as the bridge: each User has Total Quota + Commission Rate (left), and an SFDC Staff record that owns their assigned Vehicle / Equipment / Software / Allocation (right). Quota Points are populated from won Opportunities and Work Orders.

```mermaid
flowchart LR
    classDef quota fill:#fef3c7,stroke:#a16207,color:#713f12
    classDef fleet fill:#f3e8ff,stroke:#6b21a8,color:#581c87
    classDef ext fill:#fde68a,stroke:#b45309,color:#7c2d12,stroke-dasharray: 4 3

    subgraph QC[Quota & Commissions]
        direction TB
        User:::quota
        TQ[Total Quota]:::quota
        SQ[Sub Quota]:::quota
        QP[Quota Points]:::quota
        CR[Commission Rate]:::quota

        User --> TQ
        User --> CR
        TQ --> SQ
        SQ --> QP
    end

    subgraph FE[Fleet & Equipment]
        direction TB
        Staff[SFDC Staff]:::fleet
        Vehicle:::fleet
        VM[Vehicle Maintenance]:::fleet
        Equipment:::fleet
        Software:::fleet
        Allocation:::fleet

        Staff --> Vehicle
        Staff --> Equipment
        Staff --> Software
        Staff --> Allocation
        Vehicle --> VM
    end

    User --> Staff

    Opp([Opportunity]):::ext --> QP
    WO([Work Order]):::ext --> QP
```

> **Schema trap:** `SubQuota__c.CurrentUserId__c` is the *viewer's* User Id, not the rep. Use `TotalQuota__r.User__c` for actual rep attribution.

---

## Cross-map links

| From | To |
|---|---|
| `Account` | [Compliance → Corporate_Document, Legal, Association](architecture_compliance.md) |
| `Vehicle__c` | [Compliance → Legal, Corporate_Document, Policy_Document, Association](architecture_compliance.md) |
| `Work Order` | [Compliance → Corporate_Document, Legal, DocumentRequirement](architecture_compliance.md) |
| `SFDC Staff` | [Compliance → Association](architecture_compliance.md) |
| `Review` | [Marketing → Marketing Profile](architecture_marketing_geo.md) (MP → Review) |
| `Lead`, `Opportunity` | [Marketing → AdCostDetail, Zip Code](architecture_marketing_geo.md) |
| `Account`, `Service Territory` | [Marketing → AdCostDetail, Zip Code](architecture_marketing_geo.md) |
