# Precision Painting Plus — Salesforce Data Dictionary
**Org:** Production
**Generated:** 2026-05-11
**Scope:** Custom fields on core standard objects + all PPP-owned custom objects + flows, apex, validation rules, record types

---

## Table of Contents
1. [Objects Overview](#objects-overview)
2. [Account — Custom Fields](#account--custom-fields)
3. [Contact — Custom Fields](#contact--custom-fields)
4. [Opportunity — Custom Fields](#opportunity--custom-fields)
5. [Lead — Custom Fields](#lead--custom-fields)
6. [Case — Custom Fields](#case--custom-fields)
7. [Quote — Custom Fields](#quote--custom-fields)
8. [QuoteLineItem — Custom Fields](#quotelineitem--custom-fields)
9. [WorkOrder — Custom Fields](#workorder--custom-fields)
10. [WorkOrderLineItem — Custom Fields](#workorderlineitem--custom-fields)
11. [Task — Custom Fields](#task--custom-fields)
12. [Event — Custom Fields](#event--custom-fields)
13. [User — Custom Fields](#user--custom-fields)
14. [Order — Custom Fields](#order--custom-fields)
15. [Contract — Custom Fields](#contract--custom-fields)
16. [Campaign — Custom Fields](#campaign--custom-fields)
17. [Asset — Custom Fields](#asset--custom-fields)
18. [Product2 — Custom Fields](#product2--custom-fields)
19. [Pricebook2 — Custom Fields](#pricebook2--custom-fields)
20. [ServiceAppointment — Custom Fields](#serviceappointment--custom-fields)
21. [ServiceTerritory — Custom Fields](#serviceterritory--custom-fields)
22. [Custom Objects](#custom-objects)
23. [Automations — Flows](#automations--flows)
24. [Apex Triggers](#apex-triggers)
25. [Apex Classes](#apex-classes)
26. [Validation Rules](#validation-rules)
27. [Record Types](#record-types)

---

## Objects Overview

| Object | Type | Custom Fields |
|--------|------|---------------|
| Account | Standard | 125 |
| Contact | Standard | 25 |
| Opportunity | Standard | 103 |
| Lead | Standard | 89 |
| Case | Standard | 17 |
| Quote | Standard | 17 |
| QuoteLineItem | Standard | 23 |
| WorkOrder | Standard | 96 |
| WorkOrderLineItem | Standard | 41 |
| Task | Standard | 8 |
| Event | Standard | 8 |
| User | Standard | 11 |
| Order | Standard | 0 |
| Contract | Standard | 0 |
| Campaign | Standard | 0 |
| Asset | Standard | 0 |
| Product2 | Standard | 0 |
| Pricebook2 | Standard | 0 |
| ServiceAppointment | Standard | 14 |
| ServiceTerritory | Standard | 13 |
| AdCostDetail__c | Custom | 22 |
| AdCostSummary__c | Custom | 12 |
| Allocation__c | Custom | 22 |
| Angi_Profile__c | Custom | 2 |
| Association__c | Custom | 7 |
| Audit__c | Custom | 21 |
| CEMActivity__c | Custom | 2 |
| ChangeOrderLineItem__c | Custom | 7 |
| ChangeOrder__c | Custom | 7 |
| CommissionRate__c | Custom | 7 |
| Corporate_Document__c | Custom | 77 |
| DocumentRequirement__c | Custom | 5 |
| Equipment__c | Custom | 28 |
| ErrorLog__c | Custom | 4 |
| FlowPersonalConfiguration__c | Custom | 20 |
| FlowScaffold__c | Custom | 1 |
| FlowTableViewDefinition__c | Custom | 16 |
| HomeAdvisor_Profile__c | Custom | 2 |
| Legal__c | Custom | 57 |
| MarketingProfile__c | Custom | 27 |
| MasterSpend__c | Custom | 5 |
| PaintColor__c | Custom | 6 |
| Payment_Term__c | Custom | 15 |
| Policy_Document__c | Custom | 44 |
| ProcessLog__c | Custom | 5 |
| QuotaPoints__c | Custom | 13 |
| Region__c | Custom | 4 |
| Review__c | Custom | 18 |
| SFDC_Benefit__c | Custom | 7 |
| SFDC_Job_Function__c | Custom | 4 |
| SFDC_PTO_Request__c | Custom | 6 |
| SFDC_Performance_Review__c | Custom | 34 |
| SFDC_Salary_History__c | Custom | 5 |
| SFDC_Staff__c | Custom | 105 |
| Software__c | Custom | 14 |
| SubQuota__c | Custom | 14 |
| TotalQuota__c | Custom | 12 |
| Transaction__c | Custom | 54 |
| Vehicle_Maintenance__c | Custom | 6 |
| Vehicle__c | Custom | 44 |
| VoiceDirectPhone__c | Custom | 6 |
| WorkOrderCrew__c | Custom | 19 |
| Zip_Analysis__c | Custom | 10 |
| Zip_Code__c | Custom | 14 |

**Totals:** 20 core standard objects, 44 PPP-owned custom objects, 186 package-namespaced custom objects (not detailed below).

---

## Account — Custom Fields

> Custom fields on `Account` (and Person Account `__pc` fields where applicable). Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Account_Manager__c | Account Manager | Lookup(User) | No | — |
| Alternate_Corp_Name__c | Alternate Corp Name | Text(60) | No | — |
| Approved_LD__c | Approved LD | Formula (Checkbox) | No | Formula: `IF(OR(LD_Access__c="LC BCRD",LD_Access__c="LC Expert",LD_Access__c="LC JNG",LD_Access__c="LC RJK"...` |
| Billing_Address__pc | Billing Address | Text(1300) | No | Formula: `Billing_Street__pc &BR()& Billing_City__pc &", "& text(Billing_State__pc) &" "& Billing_Zip__pc` |
| Billing_City__pc | Billing City | Text(255) | No | — |
| Billing_Email__c | Billing Email | Email | No | — |
| Billing_Email__pc | Billing Email Contact | Email | No | — |
| Billing_First_Name__c | Billing First Name | Text(255) | No | — |
| Billing_First_Name__pc | Billing First Name | Text(255) | No | — |
| Billing_Last_Name__c | Billing Last Name | Text(255) | No | — |
| Billing_Last_Name__pc | Billing Last Name | Text(255) | No | — |
| Billing_Mobile__c | Billing Mobile | Phone | No | — |
| Billing_Mobile__pc | Billing Mobile | Phone | No | — |
| Billing_Name__pc | Billing Name | Text(1300) | No | Formula: `Billing_First_Name__pc &" "& Billing_Last_Name__pc` |
| Billing_Notes__pc | Billing Notes | Text(255) | No | — |
| Billing_Phone__c | Billing Phone | Phone | No | — |
| Billing_Phone__pc | Billing Phone | Phone | No | — |
| Billing_State__pc | Billing State | Picklist | No | — |
| Billing_Street__pc | Billing Street | Text(255) | No | — |
| Billing_Zip__pc | Billing Zip | Text(11) | No | — |
| Comm_Exempt__c | Comm Exempt | Checkbox | Yes | — |
| Company_Name__c | Company Name | Text(255) | No | — |
| Company_Name__pc | Company Name | Text(255) | No | — |
| Compliance_Status__c | Compliance Status | Picklist | No | — |
| Contractor_Application__c | Contractor Application | Checkbox | Yes | — |
| Corp_Paying__c | Corp Paying | Lookup(Account) | No | — |
| Corporate_Document__c | Corporate Document | Lookup(Corporate_Document) | No | — |
| County__c | County | Text(100) | No | — |
| Direct_Deposit__c | Direct Deposit | Checkbox | Yes | — |
| DNC_Notes__pc | DNC Notes | Text(255) | No | — |
| dupcheck__dc3DisableDuplicateCheck__pc | Disable Deduplicate | Checkbox | Yes | — |
| dupcheck__dc3Index__pc | Deduplicate Index | Text Area(32768) | No | — |
| EIN__c | EIN | Text(10) | No | — |
| Email_Opt_In__c | Email Opt-In | Checkbox | Yes | — |
| Email_Opt_In__pc | Email Opt-In | Picklist | No | — |
| First_Name__c | First Name | Text(255) | No | — |
| First_Opportunity_Created__c | First Opportunity Created | Date/Time | No | — |
| First_Won_Oppty__c | First Won Oppty | Date | No | — |
| FullName__pc | Full Name | Text(1300) | No | Formula: `FirstName +' '+ LastName` |
| Geo_Zone__c | Geo Zone | Text(30) | No | from old org and not needed for new process. |
| GL_Policy__c | GL Policy | Lookup(Corporate_Document) | No | — |
| HasCase__c | Has Case | Checkbox | Yes | — |
| Home_Improvement_License__c | Home Improvement License | Text(30) | No | — |
| Identification__c | Identification # | Text(30) | No | — |
| Identification_Type__c | Identification Type | Picklist | No | — |
| Identification_Yes_No__c | Identification | Checkbox | Yes | — |
| Key_Relationship__c | Key Relationship | Checkbox | Yes | — |
| Labor_Division__c | Labor Division % | Number(3, 2) | No | — |
| Last_1099__c | Last 1099 | Text(4) | No | Four digits allowed. |
| Last_Appointment__c | Last Appointment | Date/Time | No | — |
| Last_Attendance_Date__c | Last Attendance Date | Date | No | — |
| Last_Labor_Payout_Date__c | Last Labor Payout Date | Date | No | — |
| Last_Name__c | Last Name | Text(255) | No | — |
| Last_Transaction_Date__c | Last Transaction Date | Date | No | Updates when Purchases are above $0 and Xero Entered is checked. |
| LastWorkOrderCompleted__c | Last Work Order Completed | Date | No | — |
| LD_Access__c | LD Access | Text(50) | No | — |
| LeadGroup__c | Lead Group | Picklist | No | — |
| Lease_Expiration__c | Lease Expiration | Date | No | — |
| Lease_Start__c | Lease Start | Date | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| LegacyId__pc | LegacyId | Text(18) | No | — |
| LegacyId_Merged__c | LegacyId (Merged) | Text(250) | No | — |
| Login_Password__c | Login Password | Text(30) | No | — |
| Login_Site__c | Login Site | URL | No | — |
| Login_Username__c | Login Username | Text(100) | No | — |
| Mail_Forward__c | Mail Forward | Checkbox | Yes | — |
| Main_Campaign__c | Main Campaign | Text(50) | No | — |
| ManuallyAssigned__c | Manually Assigned | Checkbox | Yes | — |
| Messaging_Session__c | Messaging Session | Lookup(MessagingSession) | No | — |
| Messaging_Session__pc | Messaging Session | Lookup(MessagingSession) | No | — |
| Messaging_User__pc | Messaging User | Lookup(MessagingEndUser) | No | — |
| Mobile_Phone__c | Mobile Phone | Phone | No | — |
| MobilePhoneSearchable__pc | Mobile Phone (Searchable) | Text(10) | No | — |
| Monthly_Cost__c | Monthly Cost | Currency | No | — |
| Non_Labor__c | Non-Labor | Checkbox | Yes | — |
| Number_Open_Oppties__c | Number Open Oppties | Number(18, 0) | No | — |
| Operating_State__c | Operating State | Multi-Select Picklist | No | — |
| Original_Lead_ID__c | Original Lead ID | Text(15) | No | — |
| Payment_Terms__c | Payment Terms | Picklist | No | — |
| PFY_Territory__c | PFY Territory | Text(30) | No | — |
| Phone_Formatted__c | Phone Formatted | Checkbox | Yes | — |
| Phone_Formatted__pc | Phone Formatted | Checkbox | Yes | — |
| PhoneSearchable__pc | Phone (Searchable) | Text(10) | No | — |
| POC_Mobile__pc | POC Mobile | Phone | No | — |
| POC_Phone__pc | POC Phone | Phone | No | — |
| Portal_Notes__c | Portal Notes | Text Area(20000) | No | — |
| Portal_Password__c | Portal Password | Text(30) | No | — |
| Portal_URL__c | Portal URL | URL | No | — |
| Portal_Username__c | Portal Username | Text(30) | No | — |
| Primary_Contact__c | Primary Contact | Text(100) | No | — |
| Profile_Verified__c | Profile Verified | Text(30) | No | — |
| Purchase_Type__c | Purchase Type | Text(20) | No | 20 characters allowed. |
| Region__c | Region | Text(60) | No | — |
| Renewal_Deadline__c | Renewal Deadline | Date | No | — |
| rh2__Currency_Test__pc | Currency Test | Currency | No | Test Description |
| rh2__Describe__pc | Describe | Lookup(rh2__PS_Describe) | No | — |
| rh2__Formula_Test__pc | Formula Test | Formula (Currency) | No | Formula: `rh2__Currency_Test__pc` |
| rh2__Integer_Test__pc | Integer Test | Number(3, 0) | No | — |
| Safety_Acknowledgement_Form__c | Safety Acknowledgement Form | Checkbox | Yes | — |
| Safety_Agreement_Signed__c | Safety Agreement Signed | Date | No | — |
| Service_Territory__c | Service Territory | Lookup(ServiceTerritory) | No | — |
| Services_Provided__c | Services Provided | Text(30) | No | — |
| SMS_Opt_In__pc | SMS Opt-In | Picklist | No | — |
| SS__c | SS# | Text(11) | No | — |
| Subcontractor_Agreement_Signed__c | Subcontractor Agreement Signed | Date | No | — |
| SystemUpdating__c | SystemUpdating | Checkbox | Yes | — |
| Tax_Filing_Legal_Name__c | Tax Filing Legal Name | Text(100) | No | — |
| Tax_Status__c | Tax Status | Picklist | No | — |
| Timezone__c | Timezone | Text(60) | No | — |
| Total_Lifetime_Revenue__c | Total Lifetime Revenue | Currency | No | — |
| Total_Lost_Oppties__c | Total Lost Oppties | Number(18, 0) | No | — |
| Total_Opportunities__c | Total Opportunities | Number(18, 0) | No | — |
| Total_Rev_3FY__c | Total Rev 3FY | Currency | No | — |
| Total_Revenue_CFY__c | Total Revenue CFY | Currency | No | — |
| Total_Revenue_PFY__c | Total Revenue PFY | Currency | No | — |
| Total_Won_Oppties__c | Total Won Oppties | Number(18, 0) | No | — |
| Vendor_Documents__c | Vendor Documents | Multi-Select Picklist | No | — |
| Vendor_Preferred_Payment__c | Vendor Preferred Payment | Picklist | No | — |
| VendorBMAutoSubmit__c | Vendor BM AutoSubmit | Checkbox | Yes | — |
| VendorBMRetailer__c | Vendor BM Retailer | Checkbox | Yes | — |
| VendorStatus__c | Vendor Status | Picklist | No | — |
| Voided_Check__c | Voided Check | Checkbox | Yes | — |
| W9__c | W9 | Checkbox | Yes | — |
| WC_Policy__c | WC Policy | Lookup(Corporate_Document) | No | — |
| X18IDAcct__c | 18IDAcct | Text(1300) | No | Formula: `CASESAFEID(Id)` |


<details><summary>Package fields on Account (6)</summary>

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| dupcheck__dc3DisableDuplicateCheck__c | Disable Deduplicate | Checkbox | Yes | — |
| dupcheck__dc3Index__c | Deduplicate Index | Text Area(32768) | No | — |
| dupcheck__dc3UltimateParent__c | Ultimate Parent | Lookup(Account) | No | — |
| maps__AssignmentRule__c | Maps Assignment Rule | Lookup(maps__AssignmentRule) | No | — |
| rh2__Describe__c | Describe | Lookup(rh2__PS_Describe) | No | — |
| rh2__testCurrency__c | Currency Test | Currency | No | — |


</details>

---

## Contact — Custom Fields

> Custom fields on `Contact` (and Person Account `__pc` fields where applicable). Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Billing_Address__c | Billing Address | Text(1300) | No | Formula: `Billing_Street__c &BR()& Billing_City__c &", "& text(Billing_State__c) &" "& Billing_Zip__c` |
| Billing_City__c | Billing City | Text(255) | No | — |
| Billing_Email__c | Billing Email Contact | Email | No | — |
| Billing_First_Name__c | Billing First Name | Text(255) | No | — |
| Billing_Last_Name__c | Billing Last Name | Text(255) | No | — |
| Billing_Mobile__c | Billing Mobile | Phone | No | — |
| Billing_Name__c | Billing Name | Text(1300) | No | Formula: `Billing_First_Name__c &" "& Billing_Last_Name__c` |
| Billing_Notes__c | Billing Notes | Text(255) | No | — |
| Billing_Phone__c | Billing Phone | Phone | No | — |
| Billing_State__c | Billing State | Picklist | No | — |
| Billing_Street__c | Billing Street | Text(255) | No | — |
| Billing_Zip__c | Billing Zip | Text(11) | No | — |
| Company_Name__c | Company Name | Text(255) | No | — |
| DNC_Notes__c | DNC Notes | Text(255) | No | — |
| Email_Opt_In__c | Email Opt-In | Picklist | No | — |
| FullName__c | Full Name | Text(1300) | No | Formula: `FirstName +' '+ LastName` |
| LegacyId__c | LegacyId | Text(18) | No | — |
| Messaging_Session__c | Messaging Session | Lookup(MessagingSession) | No | — |
| Messaging_User__c | Messaging User | Lookup(MessagingEndUser) | No | — |
| MobilePhoneSearchable__c | Mobile Phone (Searchable) | Text(10) | No | — |
| Phone_Formatted__c | Phone Formatted | Checkbox | Yes | — |
| PhoneSearchable__c | Phone (Searchable) | Text(10) | No | — |
| POC_Mobile__c | POC Mobile | Phone | No | — |
| POC_Phone__c | POC Phone | Phone | No | — |
| SMS_Opt_In__c | SMS Opt-In | Picklist | No | — |


<details><summary>Package fields on Contact (6)</summary>

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| dupcheck__dc3DisableDuplicateCheck__c | Disable Deduplicate | Checkbox | Yes | — |
| dupcheck__dc3Index__c | Deduplicate Index | Text Area(32768) | No | — |
| rh2__Currency_Test__c | Currency Test | Currency | No | Test Description |
| rh2__Describe__c | Describe | Lookup(rh2__PS_Describe) | No | — |
| rh2__Formula_Test__c | Formula Test | Formula (Currency) | No | Formula: `rh2__Currency_Test__c` |
| rh2__Integer_Test__c | Integer Test | Number(3, 0) | No | — |


</details>

---

## Opportunity — Custom Fields

> Custom fields on `Opportunity`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| AccountManager__c | Account Manager | Lookup(User) | No | — |
| AccountName__c | Account Name | Text(1300) | No | Formula: `Account.Name` |
| ACD_Checkover__c | ACD Checkover | Text(1300) | No | Formula: `TEXT( MONTH( datevalue(Lead_Created_Date__c ))) & " " & TEXT(YEAR( DATEVALUE(Lead_Created_Date__c...` |
| ACD_Type__c | ACD Type | Text(1300) | No | Formula: `if(ISPICKVAL(LeadGroup__c,"Google Paid"),"Google Search Ads", if(ISPICKVAL(LeadGroup__c,"GLSA"),"...` |
| Ad_Cost_Detail_Name__c | Ad Cost Detail Name | Text(1300) | No | Formula: `AdCostDetail__r.ACD_Checkover_Corp_Name__c` |
| AdCostDetail__c | Ad Cost Detail | Lookup(AdCostDetail) | No | — |
| AM_Status__c | AM Status | Text(1300) | No | Formula: `IF(and(AccountManager__r.Id <> Estimator__r.Id,not(ISBLANK(AccountManager__r.Id))), "Different Ac...` |
| AppointmentDate__c | Appointment Date | Date | No | — |
| Appt_Scheduled__c | Appt Scheduled | Formula (Checkbox) | No | Formula: `IF( ISNULL(AppointmentDate__c),FALSE,TRUE)` |
| Bid_Deadline__c | Bid Deadline | Date | No | — |
| Bid_Request_Date__c | Bid Request Date | Date | No | — |
| Booked__c | Booked | Checkbox | Yes | — |
| Cancelled_Appointment__c | Cancelled Appointment | Formula (Checkbox) | No | Formula: `IF(NOT(ISNULL( AppointmentDate__c )) && ISNULL(Date_Estimate_Sent__c ) && ISNULL( Date_Contract_S...` |
| CapitalImprovement__c | Capital Improvement | Checkbox | Yes | — |
| Closed_Month__c | Closed Month | Text(1300) | No | Formula: `RIGHT("0" & TEXT(MONTH(CloseDate)), 2)` |
| Contact_First_Name__c | Contact First Name | Text(1300) | No | Formula: `Primary_Contact__r.FirstName` |
| Contractor_Balance__c | Contractor Balance | Formula (Currency) | No | Formula: `Contractor_Cost__c - Contractor_Paid__c` |
| Contractor_Cost__c | Contractor Cost | Currency | No | — |
| Contractor_Paid__c | Contractor Paid | Currency | No | — |
| Corporate_Name__c | Corporate Name | Text(200) | No | — |
| Created_Hour__c | Created Hour | Formula (Number) | No | Formula: `MOD( FLOOR( (CreatedDate - DATETIMEVALUE("1980-01-01 00:00:00")) * 24 ) - 5, 24 )` |
| Created_Month__c | Created Month | Text(1300) | No | Formula: `Text(Month( DATEVALUE(CreatedDate)))` |
| Created_Weekday__c | Created Weekday | Text(1300) | No | Formula: `CASE(WEEKDAY(DATEVALUE(CreatedDate)), 1, "7 Sunday", 2, "1 Monday", 3, "2 Tuesday", 4, "3 Wednesd...` |
| CreatedDate__c | Created Date | Date/Time | No | — |
| Current_Hatch_Campaign__c | Current Hatch Campaign | Picklist | No | — |
| Customer_Balance__c | Customer Balance | Formula (Currency) | No | Formula: `TotalContractAmount__c - Customer_Payments__c` |
| Customer_Payments__c | Customer Payments | Currency | No | — |
| Date_Contract_Sent__c | Date Contract Sent | Date | No | — |
| Date_Estimate_Sent__c | Date Estimate Sent | Date | No | — |
| Desired_Start__c | Desired Start | Date | No | — |
| Discount__c | Discount % | Formula (Percent) | No | Formula: `IF(ISBLANK(Discount_Given__c),0,(Discount_Given__c/QuotedSubtotalWithChangeOrder__c))` |
| Discount_Given__c | Discount Given | Currency | No | — |
| End_Date__c | End Date | Date | No | — |
| Estimate_Sent__c | Estimate Sent | Formula (Checkbox) | No | Formula: `IF( ISNULL(Date_Estimate_Sent__c),FALSE,TRUE)` |
| Estimate_Type__c | Estimate Type | Picklist | No | — |
| Estimation_Address__c | Estimation Address | Address (compound) | No | — |
| Estimator__c | Estimator | Lookup(User) | No | — |
| Estimator_Notes__c | Estimator Notes | Text Area(10000) | No | — |
| FollowUp_Notes__c | FollowUp Notes | Text Area(10000) | No | — |
| FollowupDate__c | Followup Date | Date | No | — |
| FollowupExempt__c | Followup Exempt | Checkbox | Yes | — |
| FY_Assigned__c | FY Assigned | Text(10) | No | — |
| FY_Status__c | FY Status | Text(1300) | No | Formula: `IF(FY_Assigned__c="2026","Current FY", (IF(FY_Assigned__c="2025","Previous FY", (IF(FY_Assigned__...` |
| Gross_Profit__c | Gross Profit | Formula (Currency) | No | Formula: `TotalContractAmount__c - Contractor_Cost__c` |
| Initial_Appointment_Date__c | Initial Appointment Date | Date/Time | No | — |
| Inquiry_Notes__c | Inquiry Notes | Text Area(32768) | No | — |
| Inquiry_of_Areas_Project_Size__c | # of Areas (Project Size) | Picklist | No | — |
| Inquiry_Project_Type__c | Project Type | Picklist | No | — |
| Inquiry_Service_Type__c | Inquiry Service Type | Multi-Select Picklist | No | — |
| Inquiry_Time_Frame__c | Inquiry Time Frame | Picklist | No | — |
| Insurance_Requests__c | Insurance Requests | Picklist | No | — |
| IsPhoneEstimate__c | Phone Estimate | Checkbox | Yes | — |
| Job_Notes__c | Job Notes | Text Area(5000) | No | — |
| Job_Status__c | Job Status | Picklist | No | — |
| Labor_Cost__c | Labor Cost % | Formula (Percent) | No | Formula: `Contractor_Cost__c /TotalContractAmount__c` |
| Labor_Crew__c | Labor Crew | Text(50) | No | — |
| Lead_Created_Date__c | Lead Created Date | Date/Time | No | — |
| Lead_Created_Month__c | Lead Created Month | Number(2, 0) | No | — |
| Lead_Fee__c | Lead Fee | Currency | No | — |
| Lead_Gen_Category__c | Lead Gen Category | Picklist | No | — |
| LeadGroup__c | Lead Group | Picklist | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| Lost_Notes__c | Lost Notes | Text(255) | No | — |
| Lost_Reason__c | Lost Reason | Picklist | No | — |
| ManuallyAssigned__c | Manually Assigned | Checkbox | Yes | — |
| Marketing_Main_Campaign__c | Main Campaign | Text(255) | No | — |
| Marketing_Opportunity_Source__c | Opportunity Source | Picklist | No | — |
| Messaging_Session__c | Messaging Session | Lookup(MessagingSession) | No | — |
| NeedsReschedule__c | Needs Reschedule | Checkbox | Yes | If true (checked) this Opportunity should most likely be rescheduled. |
| NetValue__c | Net Value | Currency | No | — |
| Original_Lead_Id__c | Original Lead Id | Text(15) | No | — |
| OriginalQuotedSubtotal__c | Original Quoted Subtotal | Currency | No | — |
| OriginatingAccountType__c | OriginatingAccountType | Text(255) | No | — |
| Outside_of_Assigned_Territory__c | Outside of Assigned Territory | Text(1300) | No | Formula: `IF(or( and(Owner.Full_Name__c <> Service_Territory__r.Estimator__r.Full_Name__c, Owner.Assigned_S...` |
| Owner_Name__c | Owner Name | Text(1300) | No | Formula: `Owner.Full_Name__c` |
| OwnerFirstName__c | OwnerFirstName | Text(1300) | No | Formula: `Owner.FirstName` |
| PartnerManager__c | Partner Manager | Lookup(User) | No | — |
| Paving__c | Paving | Checkbox | Yes | — |
| Phone_Pricing__c | Phone Pricing | Checkbox | Yes | — |
| Phone_Pricing_Only_Zip__c | Phone Pricing Only Zip | Checkbox | Yes | — |
| Preferred_Contact_Method__c | Preferred Contact Method | Picklist | No | — |
| Primary_Contact__c | Primary Contact | Lookup(Contact) | No | — |
| Primary_Contact_Phone__c | Phone | Text(1300) | No | Formula: `Primary_Contact__r.Phone` |
| Primary_Contact_Project_Address__c | Project Address | Text(1300) | No | Formula: `Account.ShippingStreet & BR() & Account.ShippingCity & ", " & Account.ShippingState & " " & Accou...` |
| Project_Manager_Name__c | Project Manager Name | Text(1300) | No | Formula: `ProjectManager__r.Full_Name__c` |
| ProjectManager__c | Project Manager | Lookup(User) | No | — |
| Quote_Subtotal__c | Quote Subtotal | Currency | No | — |
| QuotedSubtotalWithChangeOrder__c | Quoted Subtotal with Change Order | Currency | No | — |
| ReferringAccount__c | Referring Account | Lookup(Account) | No | — |
| Repeat_Referral__c | Repeat/Referral | Picklist | No | — |
| Request_Review__c | Request Review | Picklist | No | — |
| Rescheduling_Notes__c | Rescheduling Notes | Text Area(255) | No | — |
| ScheduleDateMinimum__c | Schedule Date Minimum | Formula (Date/Time) | No | Formula: `NOW()+0.05` |
| Self_Generated_Source__c | Self Generated Source | Text(255) | No | — |
| Service_Territory__c | Service Territory | Lookup(ServiceTerritory) | No | — |
| Start_Date__c | Start Date | Date | No | — |
| SystemUpdating__c | SystemUpdating | Checkbox | Yes | — |
| TotalAmount__c | Total Amount | Currency | No | Custom field to calculate the total amount of the related Work Order. Calculated by Flow: WorkOrder.SetOpportunityTotalAmount |
| TotalContractAmount__c | Total Contract Amount | Currency | No | — |
| WO_Complete__c | WO Complete | Checkbox | Yes | — |
| Work_Type1__c | Work Type | Lookup(WorkType) | No | — |
| X18IdOpp__c | 18IdOpp | Text(1300) | No | Formula: `CASESAFEID(Id)` |
| Zip_Code__c | Zip Code | Lookup(Zip_Code) | No | — |


---

## Lead — Custom Fields

> Custom fields on `Lead`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| ACD_Checkover__c | ACD Checkover | Text(1300) | No | Formula: `TEXT( MONTH(DATEVALUE(CreatedDate))) & " " & TEXT(YEAR( DATEVALUE(CreatedDate) ) ) & " " & Servic...` |
| ACD_Type__c | ACD Type | Text(1300) | No | Formula: `if(ISPICKVAL(LeadGroup__c,"Google Paid"),"Google Search Ads", if(ISPICKVAL(LeadGroup__c,"GLSA"),"...` |
| AdCostDetail__c | Ad Cost Detail | Lookup(AdCostDetail) | No | — |
| AdId__c | Ad Id | Text(255) | No | — |
| AdName__c | Ad Name | Text(255) | No | — |
| AdSetId__c | Ad Set Id | Text(255) | No | — |
| AdSetName__c | Ad Set Name | Text(255) | No | — |
| Agent__c | Agent | Text(60) | No | Agent responsible for unqualifying or converting the Lead. |
| Assigne_Id__c | Assignee Id | Text(18) | No | — |
| Cadence_Wait_Time__c | Cadence Wait Time | Date/Time | No | — |
| Count__c | Count | Formula (Number) | No | Formula: `1` |
| County__c | County | Text(40) | No | — |
| cps_Inquiry_Details_Notes__c | Inquiry Details/Notes | Text Area(32768) | No | — |
| Created_Date_Lead_Gen__c | Created Date (Lead Gen) | Formula (Date/Time) | No | Formula: `if( CreatedDate > Lead_Gen_Timestamp__c ,Lead_Gen_Timestamp__c,CreatedDate)` |
| Created_Hour__c | Created Hour | Formula (Number) | No | Formula: `MOD( FLOOR( (CreatedDate - DATETIMEVALUE("1980-01-01 00:00:00")) * 24 ) - 5, 24 )` |
| Created_Month__c | Created Month | Formula (Number) | No | Formula: `MONTH(DATEVALUE( CreatedDate ))` |
| Created_Weekday__c | Created Weekday | Text(1300) | No | Formula: `CASE(WEEKDAY(DATEVALUE(CreatedDate)), 1, "7 Sunday", 2, "1 Monday", 3, "2 Tuesday", 4, "3 Wednesd...` |
| CreatedDate__c | Created Date | Date/Time | No | — |
| Days_to_Convert__c | Days to Convert | Formula (Number) | No | Formula: `( ConvertedDate - DATEVALUE(CreatedDate))` |
| Email_Opt_In__c | Email Opt-In | Picklist | No | — |
| ExternalCampaignId__c | External Campaign Id | Text(255) | No | — |
| ExternalCampaignName__c | External Campaign Name | Text(255) | No | — |
| Financial_Year__c | Financial Year | Text(1300) | No | Formula: `if(OR(MONTH(DATEVALUE(CreatedDate))=2, MONTH(DATEVALUE(CreatedDate))=3, MONTH(DATEVALUE(CreatedDa...` |
| Followup_Date__c | Followup Date | Date | No | — |
| FormId__c | Form Id | Text(255) | No | — |
| Inquiry_Notes__c | Inquiry Notes | Text Area(32768) | No | — |
| Is_Assignee_Current_User__c | Is Assignee Current User | Formula (Checkbox) | No | Formula: `IF( CASESAFEID($User.Id) = Assigne_Id__c ,TRUE,FALSE)` |
| Is_Assignee_Owner__c | Is Assignee Owner | Formula (Checkbox) | No | Formula: `AND( CASESAFEID(Owner:User.Id) = Assigne_Id__c)` |
| IsPhoneEstimate__c | Phone Estimate | Checkbox | Yes | — |
| Job_Time_Frame__c | Job Time Frame | Picklist | No | — |
| Language__c | Language | Text(255) | No | — |
| Lead_Age__c | Lead Maturity Age | Formula (Number) | No | Formula: `if( ispickval(Status ,"Unqualified"),( DATEVALUE(LastModifiedDate )- DATEVALUE(CreatedDate) ), if...` |
| Lead_content__c | Lead content | Text(100) | No | — |
| Lead_Fee__c | Lead Fee | Currency | No | — |
| Lead_Gen_Account__c | Lead Gen Account | Picklist | No | — |
| Lead_Gen_Category__c | Lead Gen Category | Picklist | No | — |
| Lead_Gen_Timestamp__c | Lead Gen Timestamp | Date/Time | No | — |
| Lead_Landing_Page__c | Lead Landing Page | Text Area(2500) | No | — |
| Lead_Medium__c | Lead Medium | Picklist | No | — |
| Lead_Number__c | Lead Number | Text(255) | No | — |
| Lead_Timezone__c | Timezone | Text(60) | No | — |
| lead_url__c | lead url | Text Area(2500) | No | — |
| LeadAgeGroup__c | Lead Age Group | Picklist | No | — |
| LeadGroup__c | Lead Group | Picklist | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| Marketing_Main_Campaign__c | Main Campaign | Text(255) | No | — |
| Messaging_Session__c | Messaging Session | Lookup(MessagingSession) | No | — |
| Messaging_User__c | Messaging User | Lookup(MessagingEndUser) | No | — |
| MobilePhoneSearchable__c | Mobile Phone (Searchable) | Text(10) | No | — |
| No_of_Areas_Project_Size__c | # of Areas (Project Size) | Picklist | No | — |
| Of_Outbound_Calls__c | # Of Outbound Calls (Cadence) | Number(18, 0) | No | — |
| Opportunity_Owner__c | Opportunity Owner | Lookup(User) | No | — |
| Outbound_Voice_Calls__c | # Outbound Voice Calls | Number(18, 0) | No | — |
| PageId__c | Page Id | Text(255) | No | — |
| PageName__c | PageName | Text(255) | No | — |
| PartnerAccount__c | Partner Account | Lookup(Account) | No | — |
| Paving_Amount__c | Paving Amount | Currency | No | — |
| Paving_Followup_Date__c | Paving Followup Date | Date | No | — |
| Paving_Followup_Notes__c | Paving Followup Notes | Text Area(32768) | No | — |
| Paving_Lead__c | Paving Lead | Checkbox | Yes | — |
| Paving_Status__c | Paving Status | Picklist | No | — |
| Phone_Formatted__c | Phone Formatted | Checkbox | Yes | — |
| Phone_Number_Confirmed__c | Phone Number Confirmed | Picklist | No | — |
| Phone_Pricing__c | Phone Pricing | Checkbox | Yes | — |
| Phone_Pricing_Only_Zip__c | Phone Pricing Only Zip | Checkbox | Yes | This zip only accepts Phone Pricings. |
| PhoneSearchable__c | Phone (Searchable) | Text(10) | No | — |
| Preferred_Contact_Method__c | Preferred Contact Method | Picklist | No | — |
| Priority_Number__c | Priority Number | Number(4, 0) | No | — |
| Profile_ID__c | Profile ID | Text(150) | No | — |
| Profile_Name__c | Profile Name | Text(150) | No | — |
| Project_Type__c | Project Type | Picklist | Yes | — |
| Reach__c | Reach | Formula (Checkbox) | No | Formula: `IF( WEEKDAY(DATEVALUE(NOW()))=1, IF( TIMEVALUE(NOW())>=TIMEVALUE(DATETIMEVALUE( '1900-01-08 13:00...` |
| Reason_for_Call__c | Reason for Call | Picklist | No | Why is the customer calling? Example: Schedule an estimate appointment=Needs an Estimate; Inquiry on existing project=Customer Service; Telemarketer=Other |
| ReferringAccount__c | Referring Account | Lookup(Account) | No | — |
| Region__c | Region | Text(255) | No | — |
| Repeat_Referral__c | Repeat/Referral | Picklist | No | — |
| Service_Type__c | Service Type | Multi-Select Picklist | No | — |
| ServiceTerritory__c | Service Territory | Lookup(ServiceTerritory) | No | — |
| SMS_Opt_In__c | SMS Opt-In | Picklist | No | — |
| SourcePlatform__c | Source Platform | Picklist | No | For leads generated on an external service |
| Start__c | Start | Date/Time | No | — |
| SyncToContact__c | Sync to Contact | Lookup(Contact) | No | — |
| Time_Difference_Hours__c | Time Difference (Hours) | Number(18, 0) | No | — |
| Time_To_First_Call__c | Time To First Call (Minutes) | Formula (Number) | No | Time to First Call in Minutes |
| TimeNow__c | TimeNow | Formula (Date/Time) | No | Formula: `NOW()` |
| TZOffset__c | TZOffset | Text(10) | No | — |
| Unqualified_Reason__c | Unqualified Reason | Picklist | No | — |
| Voicemail__c | Voicemail | Lookup(VoiceCall) | No | — |
| Zipcode__c | Zipcode | Text(30) | No | — |


<details><summary>Package fields on Lead (5)</summary>

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| dupcheck__dc3DisableDuplicateCheck__c | Disable Deduplicate | Checkbox | Yes | — |
| dupcheck__dc3Index__c | Deduplicate Index | Text Area(32768) | No | — |
| dupcheck__dc3Web2Lead__c | is Web2Lead | Checkbox | Yes | — |
| maps__AssignmentRule__c | Maps Assignment Rule | Lookup(maps__AssignmentRule) | No | — |
| sfleadcaphfprod__External_Lead_ID__c | External Lead ID | Text(255) | No | — |


</details>

---

## Case — Custom Fields

> Custom fields on `Case`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| AdditionalContact__c | Additional Contact | Lookup(Contact) | No | — |
| Case_Team_Overwrite__c | Case Team Overwrite | Checkbox | Yes | — |
| DaysSinceLastUpdate__c | Days Since Last Update | Formula (Number) | No | Formula: `TODAY() - IF(DATEVALUE(LastModifiedDate)>MostRecentCommentDate__c, DATEVALUE(LastModifiedDate), M...` |
| Department__c | Department | Picklist | Yes | — |
| Desired_Resolution__c | Desired Resolution | Text Area(32768) | No | — |
| general_release__c | General Release | Picklist | No | — |
| General_Release_Type__c | General Release Type | Picklist | No | — |
| GeneralReleaseTerms__c | General Release Terms | Text Area(2000) | No | — |
| Lead__c | Lead | Lookup(Lead) | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| MostRecentCommentDate__c | Most Recent Comment Date | Date | No | — |
| Opportunity__c | Opportunity | Lookup(Opportunity) | No | — |
| Opportunity_Owner__c | Opportunity Owner | Text(1300) | No | Formula: `Opportunity__r.Owner_Name__c` |
| Partner_Manager__c | Partner Manager | Text(1300) | No | Formula: `Opportunity__r.PartnerManager__r.Full_Name__c` |
| RefundAmountRewarded__c | Amount Rewarded | Currency | No | — |
| SatisfactionGuaranteeInvoked__c | Satisfaction Guarantee Invoked | Checkbox | Yes | — |
| WorkOrder__c | Work Order | Lookup(WorkOrder) | No | — |


---

## Quote — Custom Fields

> Custom fields on `Quote`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Add_Warranty__c | Add Warranty | Checkbox | Yes | — |
| CapitalImprovement__c | Capital Improvement | Checkbox | Yes | If checked, this project is a capital improvement and therefore not subject to sales tax (will prevent calculation of Tax field). |
| CostMaterials__c | Materials Cost | Currency | No | — |
| Discount_Amount__c | Discount Amount | Currency | No | — |
| DiscountAmountCalculated__c | Discount Amount Calculated | Formula (Currency) | No | Formula: `(NULLVALUE(DiscountPercentageLabor__c, 0) * NULLVALUE(Subtotal__c, 0))` |
| DiscountPercentageLabor__c | Discount Percentage (Labor) | Percent | No | A percentage discount to apply to Labor costs only. |
| Display_Discount__c | Display Discount | Checkbox | Yes | — |
| Display_Material_Cost__c | Display Material Cost | Checkbox | Yes | — |
| GrandTotal__c | Grand Total | Formula (Currency) | No | Formula: `Subtotal__c - Discount_Amount__c + Tax - DiscountAmountCalculated__c + IF( Materials_Included__c ...` |
| LaborDaysProjected__c | Labor Days (Projected) | Number(10, 2) | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| Materials_Included__c | Materials Included | Checkbox | Yes | — |
| MaterialType__c | Material Type | Picklist | No | — |
| QuotedSubtotal__c | Quoted Subtotal | Formula (Currency) | No | Formula: `Subtotal__c - Discount_Amount__c - (NULLVALUE( DiscountPercentageLabor__c , 0)*Subtotal__c) + IF(...` |
| Subtotal__c | Subtotal | Currency | No | — |
| SubtotalPlusMaterials__c | Subtotal plus Materials | Formula (Currency) | No | Formula: `Subtotal__c + IF( Materials_Included__c =TRUE, CostMaterials__c ,0)` |
| Total_Discount__c | Total Discount | Formula (Currency) | No | Formula: `Discount_Amount__c + DiscountAmountCalculated__c` |


---

## QuoteLineItem — Custom Fields

> Custom fields on `QuoteLineItem`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| AreaLabel__c | Area Label | Text(255) | No | — |
| Description__c | Description | Text Area(32000) | No | — |
| Dimensions_Height__c | Dimensions Height | Number(3, 1) | No | — |
| Dimensions_Length__c | Dimensions Length | Number(3, 1) | No | — |
| Dimensions_Width__c | Dimensions Width | Number(3, 1) | No | — |
| DisposalCost__c | Disposal Cost | Currency | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| MaterialType__c | Material Type | Picklist | No | — |
| NumberClosets__c | Number of Closets | Number(16, 2) | No | — |
| NumberDoors__c | Number of Doors | Number(16, 2) | No | — |
| NumberWindows__c | Number of Windows | Number(16, 2) | No | — |
| of_Coats__c | # of Coats | Number(1, 0) | No | — |
| Prep_Level__c | Prep Level | Picklist | No | — |
| PrepLevelFloor__c | Floor Prep Level | Picklist | No | — |
| PriceOverride__c | Price Override? | Checkbox | Yes | If checked, a manual price must be entered and will supersede the unit price * quantity. |
| PriceOverrideAmount__c | Price Override Amount | Currency | No | — |
| Primer__c | Primer | Picklist | No | — |
| Product_Family__c | Product Family | Text(1300) | No | Formula: `TEXT(Product2.Family)` |
| ProductCode__c | Product Code | Text(1300) | No | Formula: `Product2.ProductCode` |
| Surface_Start__c | Surface Start | Picklist | No | — |
| Surfaces__c | Surfaces | Multi-Select Picklist | No | — |
| TotalPrice__c | Total Price | Formula (Currency) | No | Formula: `IF( PriceOverride__c , PriceOverrideAmount__c , (Quantity * UnitPrice)+DisposalCost__c)` |
| UnitOfMeasure__c | Unit of Measure | Picklist | No | — |


---

## WorkOrder — Custom Fields

> Custom fields on `WorkOrder`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| AccountManagerEmail__c | Account Manager Email | Text(1300) | No | Formula: `Opportunity__r.AccountManager__r.Email` |
| AccountManagerName__c | Account Manager Name | Text(1300) | No | Formula: `Opportunity__r.AccountManager__r.Full_Name__c` |
| AccountManagerPhone__c | Account Manager Phone | Text(1300) | No | Formula: `Opportunity__r.AccountManager__r.Phone` |
| BalanceOwed__c | Balance Owed | Formula (Currency) | No | Formula: `TotalCustomerCharges__c - TotalPaymentsIn__c + TotalCustomerAdjustments__c + Internal_Adjustments__c` |
| BalanceOwedNotes__c | Balance Owed Notes | Text Area(3000) | No | — |
| Canceled_Line_Items__c | Canceled Line Items | Currency | No | — |
| CapitalImprovement__c | Capital Improvement | Checkbox | Yes | If checked, this project is a capital improvement and therefore not subject to sales tax (will prevent calculation of Tax field). |
| COI_Needed__c | COI | Picklist | No | — |
| Collections__c | Collections | Checkbox | Yes | — |
| Collections_Status__c | Collections Status | Picklist | No | — |
| ColorsReceived__c | Colors Received | Checkbox | Yes | — |
| CommissionAmount__c | Commission Amount | Currency | No | — |
| Contractor__c | Assigned Labor Crew | Lookup(Account) | No | — |
| CoordinationCompleteDate__c | Coordination Complete Date | Date | No | — |
| Corporate_Name__c | Corporate Name | Text(200) | No | — |
| CostMaterials__c | Materials Cost | Currency | No | — |
| County__c | County | Text(1300) | No | Formula: `TEXT(Opportunity__r.Zip_Code__r.County__c)` |
| CreatedDate__c | Created Date | Date/Time | No | — |
| Current_Invoice_Amount__c | Current Invoice Amount | Currency | No | — |
| Customer_PO__c | Customer PO | Text(50) | No | — |
| Date_Review_Requested__c | Date Review Requested | Date | No | — |
| DateFlexibility__c | Date Flexibility | Text Area(255) | No | — |
| DateSentToCollections__c | Date Sent to Collections | Date | No | — |
| DayTimeRestrictions__c | Restrictions on Day / Time | Text Area(32768) | No | — |
| DepositReceived__c | Deposit Received | Checkbox | Yes | — |
| DesiredStart__c | Desired Start Date | Date | No | — |
| Discount_Amount__c | Discount Amount | Currency | No | — |
| DiscountAmountCalculated__c | Discount Amount Calculated | Formula (Currency) | No | Discount amount originally quoted to the customer |
| DiscountPercentageLabor__c | Discount Percentage (Labor) | Percent | No | A percentage discount to apply to Labor costs only. |
| Final_Balance_Aging__c | Final Balance Aging | Formula (Number) | No | Number of days past due. Negative number = days remaining until balance is due. |
| Final_Balance_Due__c | Final Balance Due | Date | No | — |
| FollowUpAge__c | Follow Up Age | Formula (Number) | No | If the FollowUpDate__c is today or in the past, the number of days between TODAY and the FollowUpDate__c. |
| FollowUpDate__c | Follow Up Date | Date | No | The Date by which this record should be followed up on. |
| FSL_Is_Linked_To_Maintenance_Plan__c | Is Linked To Maintenance Plan | Formula (Checkbox) | No | Formula: `NOT(ISBLANK(MaintenancePlanId))` |
| FSL_Is_Linked_To_Service_Contract__c | Is Linked To Service Contract | Formula (Checkbox) | No | Formula: `NOT( ISBLANK( ServiceContractId ))[disable]` |
| FullyAssigned__c | Fully Assigned | Checkbox | Yes | True if all needed crews have been assigned to this project. |
| GrandTotal__c | Grand Total | Formula (Currency) | No | Formula: `Quoted_Subtotal_with_Change_Order__c + Tax` |
| Gross_Margin_Percent__c | Gross Margin % | Formula (Percent) | No | Formula: `GrossProfit__c / Quoted_Subtotal_with_Change_Order__c` |
| GrossProfit__c | Gross Profit | Formula (Currency) | No | Formula: `Quoted_Subtotal_with_Change_Order__c - TotalCostsWithoutSales__c` |
| GrossProfitPercent__c | Gross Profit Percent | Formula (Percent) | No | Formula: `GrossProfit__c / NetValue__c` |
| InsuranceRequests__c | Insurance Requests | Text Area(10000) | No | — |
| Internal_Adjustments__c | Internal Adjustments | Currency | No | — |
| Job_Costing_Percent__c | Job Costing Percent | Formula (Percent) | No | Formula: `TotalPayoutsForLabor__c / Quoted_Subtotal_with_Change_Order__c` |
| Labor_Crew_Payout__c | Labor Crew Payout % | Formula (Percent) | No | Formula: `TotalPayoutsForLabor__c / NetValue__c` |
| LaborCrewRate__c | Labor Crew Rate | Currency | No | — |
| LaborDaysActual__c | Actual Labor Days | Number(2, 2) | No | Sum of Labor Days from related Work Order Crew records |
| LaborDaysProjected__c | Total Projected Labor Days | Number(10, 2) | No | Sum of Labor Days from related Work Order Line Item records with a Unit of Measure of Labor Days |
| LaborDaysRemaining__c | Labor Days Remaining | Formula (Number) | No | Formula: `LaborDaysProjected__c - LaborDaysActual__c` |
| LastPaymentIn__c | Last Payment In | Date | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| LegacyProjectNumber__c | Legacy Project Number | Text(25) | No | — |
| Materials_Included__c | Materials Included | Checkbox | Yes | — |
| MaterialType__c | Material Type | Picklist | No | — |
| Name__c | Name | Text(255) | No | — |
| NetValue__c | Net Value | Formula (Currency) | No | Formula: `Quoted_Subtotal_with_Change_Order__c - TotalNonBillablePurchases__c - TotalReferralPayouts__c - T...` |
| Opportunity__c | Opportunity | Lookup(Opportunity) | No | — |
| Original_Quoted_Subtotal__c | Original Quoted Subtotal | Currency | No | — |
| OriginalQuotedSubtotal__c | Original Quoted Subtotal | Formula (Currency) | No | Formula: `QuotedSubtotal__c + Canceled_Line_Items__c - TotalChangeOrder__c` |
| OtherContractors__c | Other Contractors | Text Area(10000) | No | — |
| Owner_Name__c | Owner Name | Text(1300) | No | Formula: `Owner:User.Full_Name__c` |
| Payment_Terms__c | Payment Terms | Text(1300) | No | Sourced from the related Account |
| Powerwash__c | Powerwash | Picklist | No | — |
| PreferredPaymentMethod__c | Preferred Payment Method | Picklist | No | — |
| Project_Manager_Notes__c | Project Manager Notes | Text Area(32768) | No | — |
| Quoted_Subtotal_with_Change_Order__c | Quoted Subtotal with Change Order | Formula (Currency) | No | Formula: `QuotedSubtotal__c + TotalChangeOrder__c` |
| QuotedSubtotal__c | Quoted Subtotal | Formula (Currency) | No | Formula: `(OriginalSubtotal__c + Canceled_Line_Items__c) - Discount_Amount__c - (NULLVALUE( DiscountPercent...` |
| Requested_By__c | Requested By | Picklist | No | — |
| RequestReview__c | Request Review | Picklist | No | — |
| RequiredCompletion__c | Required Completion Date | Date | No | — |
| RevenuePerLaborDay__c | Revenue Per Labor Day | Formula (Currency) | No | Formula: `NetValue__c / LaborDaysActual__c` |
| Review_Notes__c | Review Notes | Text Area(255) | No | — |
| Review_Platform__c | Review Platform | Picklist | No | — |
| SalesPayoutPercent__c | Sales Payout Percent | Formula (Percent) | No | Formula: `TotalSalesPayouts__c / GrossProfit__c` |
| ScheduleConfirmedWithClient__c | Schedule Confirmed with Client | Checkbox | Yes | True if the project schedule has been confirmed with the client. |
| Scheduling_Notes__c | Scheduling Notes | Text Area(25000) | No | — |
| ServiceAppointment__c | Service Appointment | Lookup(ServiceAppointment) | No | — |
| Subtotal__c | Subtotal | Currency | No | The total of all Work Order Line Items (UnitPrice * Quantity), if the Status Category is not 'Cannot Complete', 'Canceled', or 'Pending Approval - ADD'. |
| SubtotalPlusMaterials__c | Subtotal plus Materials | Formula (Currency) | No | Formula: `Subtotal__c + IF( Materials_Included__c =TRUE, CostMaterials__c ,0)` |
| Tax_Rate__c | Tax Rate | Formula (Percent) | No | Formula: `ServiceTerritory.TaxRate__c` |
| Total_Undeposited_Payments__c | Total Undeposited Payments | Currency | No | — |
| TotalBillablePurchases__c | Total Billable Purchases | Currency | No | — |
| TotalChangeOrder__c | Total Change Order | Currency | No | — |
| TotalCostsWithoutSales__c | Total Costs Without Sales | Formula (Currency) | No | Formula: `TotalReferralPayouts__c + TotalPayoutsForLabor__c + TotalNonBillablePurchases__c + TotalMerchantF...` |
| TotalCustomerAdjustments__c | Total Customer Adjustments | Currency | No | — |
| TotalCustomerCharges__c | Total Customer Charges | Formula (Currency) | No | Formula: `GrandTotal__c + TotalBillablePurchases__c` |
| TotalDiscount__c | Total Discount | Formula (Currency) | No | Formula: `DiscountAmountCalculated__c + Discount_Amount__c` |
| TotalMerchantFees__c | Total Merchant Fees | Currency | No | — |
| TotalNonBillablePurchases__c | Total Non-Billable Purchases | Currency | No | — |
| TotalPaymentsIn__c | Total Payments In | Currency | No | — |
| TotalPayoutsForLabor__c | Total Payouts for Labor | Currency | No | — |
| TotalPurchases__c | Total Purchases | Formula (Currency) | No | Formula: `TotalNonBillablePurchases__c + TotalBillablePurchases__c` |
| TotalReferralPayouts__c | Total Referral Payouts | Currency | No | — |
| TotalSalesPayouts__c | Total Sales Payouts | Currency | No | — |
| TotalWorkOrderCosts__c | Total Work Order Costs | Formula (Currency) | No | Formula: `TotalReferralPayouts__c + TotalPayoutsForLabor__c + TotalNonBillablePurchases__c + TotalSalesPayo...` |
| UndepositedTransactions__c | Undeposited Transactions | Currency | No | — |
| Unique_Invoice_No__c | Unique Invoice No | Text(15) | No | — |


<details><summary>Package fields on WorkOrder (4)</summary>

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| FSL__IsFillInCandidate__c | Is Fill In Candidate | Checkbox | Yes | — |
| FSL__Prevent_Geocoding_For_Chatter_Actions__c | Prevent Geocoding For Chatter Actions | Checkbox | Yes | — |
| FSL__Scheduling_Priority__c | Scheduling Priority | Formula (Number) | No | Formula: `CASE(TEXT(Priority), 'Critical' , 1 ,'High' ,2,'Medium' ,3 , 'Low', 4, null)` |
| FSL__VisitingHours__c | Visiting Hours | Lookup(OperatingHours) | No | — |


</details>

---

## WorkOrderLineItem — Custom Fields

> Custom fields on `WorkOrderLineItem`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| AreaLabel__c | Area Label | Text(255) | No | — |
| ChangeOrderRelated__c | Change Order Related | Checkbox | Yes | — |
| ColorCeiling__c | Ceiling Color | Lookup(PaintColor) | No | — |
| ColorFloor__c | Floor Color | Lookup(PaintColor) | No | — |
| ColorNotes__c | Color Notes | Text Area(32768) | No | — |
| ColorOther__c | Other Color | Lookup(PaintColor) | No | — |
| ColorTrim__c | Trim Color | Lookup(PaintColor) | No | — |
| ColorWall__c | Wall Color | Lookup(PaintColor) | No | — |
| Dimensions_Height__c | Dimensions Height | Number(3, 1) | No | — |
| Dimensions_Length__c | Dimensions Length | Number(3, 1) | No | — |
| Dimensions_Width__c | Dimensions Width | Number(3, 1) | No | — |
| DisposalCost__c | Disposal Cost | Currency | No | — |
| FinishCeiling__c | Ceiling Finish | Picklist | No | — |
| FinishFloor__c | Floor Finish | Picklist | No | — |
| FinishOther__c | Other Finish | Picklist | No | — |
| FinishTrim__c | Trim Finish | Picklist | No | — |
| FinishWall__c | Wall Finish | Picklist | No | — |
| Interior_Exterior__c | Interior/Exterior | Picklist | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| MaterialType__c | Material Type | Picklist | No | — |
| NumberClosets__c | Number of Closets | Number(16, 2) | No | — |
| NumberDoors__c | Number of Doors | Number(16, 2) | No | — |
| NumberWindows__c | Number of Windows | Number(16, 2) | No | — |
| of_Coats__c | # of Coats | Number(1, 0) | No | — |
| Perimeter__c | Perimeter | Formula (Number) | No | Formula: `(Dimensions_Width__c+Dimensions_Length__c)*2` |
| Prep_Level__c | Prep Level | Picklist | No | — |
| PrepLevelFloor__c | Floor Prep Level | Picklist | No | — |
| PriceOverride__c | Price Override? | Checkbox | Yes | If checked, a manual price must be entered and will supersede the unit price * quantity. |
| PriceOverrideAmount__c | Price Override Amount | Currency | No | — |
| Primer__c | Primer | Picklist | No | — |
| Product_Family__c | Product Family | Text(1300) | No | Formula: `TEXT(Product2.Family)` |
| ProductCode__c | Product Code | Text(1300) | No | Formula: `Product2.ProductCode` |
| ProductName__c | ProductName | Text(1300) | No | Formula: `Product_Family__c + ": " + PricebookEntry.Product2.Name + IF(AreaLabel__c<>'', ': ' + AreaLabel__...` |
| Quote_line_item_Id__c | Quote line item Id | Text(18) | No | — |
| SortOrder__c | Sort Order | Number(9, 0) | No | — |
| Sq_Footage__c | Sq Footage | Formula (Number) | No | Formula: `Dimensions_Length__c*Dimensions_Width__c` |
| Surface_Start__c | Surface Start | Picklist | No | — |
| Surfaces__c | Surfaces | Multi-Select Picklist | No | — |
| TotalPrice__c | Total Price | Formula (Currency) | No | Formula: `IF(PriceOverride__c , PriceOverrideAmount__c , (UnitPrice * Quantity)+DisposalCost__c)` |
| UnitOfMeasure__c | Unit of Measure | Picklist | No | — |
| Wall_Surface_Area__c | Wall Surface Area | Formula (Number) | No | Formula: `Dimensions_Height__c* ((Dimensions_Length__c+Dimensions_Width__c)*2)` |


<details><summary>Package fields on WorkOrderLineItem (2)</summary>

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| FSL__IsFillInCandidate__c | Is Fill In Candidate | Checkbox | Yes | — |
| FSL__VisitingHours__c | Visiting Hours | Lookup(OperatingHours) | No | — |


</details>

---

## Task — Custom Fields

> Custom fields on `Task`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Crew__c | Crew | Lookup(Account) | No | — |
| DueBy__c | Due By | Date/Time | No | — |
| Email__c | Email | Email | No | — |
| IsPublic__c | IsPublic | Checkbox | Yes | — |
| Natterbox_Call_Recording__c | Natterbox Call Recording | Text(1300) | No | Formula: `"Test"` |
| Phone__c | Phone | Phone | No | — |
| ServiceAppointment__c | Service Appointment | Lookup(ServiceAppointment) | No | — |
| WorkOrderCrew__c | Work Order Crew | Lookup(WorkOrderCrew) | No | — |


<details><summary>Package fields on Task (10)</summary>

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| FSL__Count_of_Events__c | Count of Events | Formula (Number) | No | Count of all events |
| FSL__Count_of_Tasks__c | Count of Tasks | Formula (Number) | No | Formula: `IF( IsTask,1,0)` |
| FSL__Event_Type__c | Event Type | Picklist | No | — |
| maps__BaseObjectId__c | Maps Base Object | Lookup(maps__BaseObject) | No | — |
| maps__LayerId__c | Layer Id | Text(255) | No | — |
| maps__WA_AdvRouteWaypoint__c | Maps Advanced Route Waypoint | Lookup(maps__AdvRouteWaypoint) | No | — |
| wbsendit__Smart_Email_Id__c | Smart Email Id | Text(40) | No | — |
| wbsendit__Smart_Email_Message_Id__c | Smart Email Message Id | Text(40) | No | — |
| wbsendit__Smart_Email_Recipient__c | Smart Email Recipient | Text(255) | No | The recipient of the email. |
| wbsendit__Smart_Email_Status__c | Smart Email Status | Text(255) | No | — |


</details>

---

## Event — Custom Fields

> Custom fields on `Event`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Crew__c | Crew | Lookup(Account) | No | — |
| DueBy__c | Due By | Date/Time | No | — |
| Email__c | Email | Email | No | — |
| IsPublic__c | IsPublic | Checkbox | Yes | — |
| Natterbox_Call_Recording__c | Natterbox Call Recording | Text(1300) | No | Formula: `"Test"` |
| Phone__c | Phone | Phone | No | — |
| ServiceAppointment__c | Service Appointment | Lookup(ServiceAppointment) | No | — |
| WorkOrderCrew__c | Work Order Crew | Lookup(WorkOrderCrew) | No | — |


<details><summary>Package fields on Event (10)</summary>

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| FSL__Count_of_Events__c | Count of Events | Formula (Number) | No | Count of all events |
| FSL__Count_of_Tasks__c | Count of Tasks | Formula (Number) | No | Formula: `IF( IsTask,1,0)` |
| FSL__Event_Type__c | Event Type | Picklist | No | — |
| maps__BaseObjectId__c | Maps Base Object | Lookup(maps__BaseObject) | No | — |
| maps__LayerId__c | Layer Id | Text(255) | No | — |
| maps__WA_AdvRouteWaypoint__c | Maps Advanced Route Waypoint | Lookup(maps__AdvRouteWaypoint) | No | — |
| wbsendit__Smart_Email_Id__c | Smart Email Id | Text(40) | No | — |
| wbsendit__Smart_Email_Message_Id__c | Smart Email Message Id | Text(40) | No | — |
| wbsendit__Smart_Email_Recipient__c | Smart Email Recipient | Text(255) | No | The recipient of the email. |
| wbsendit__Smart_Email_Status__c | Smart Email Status | Text(255) | No | — |


</details>

---

## User — Custom Fields

> Custom fields on `User`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| AM_Services__c | AM Services | Picklist | No | — |
| Assigned_ST_Unique_Code__c | Assigned ST Unique Code | Text(50) | No | — |
| Email__c | Email | Text(1300) | No | Formula: `Email` |
| Estimate_Custom_Notes__c | Estimate Custom Notes | Text Area(32768) | No | — |
| FIRST_NAME__c | FIRST_NAME | Text(1300) | No | Formula: `UPPER( FirstName )` |
| Full_Name__c | Full Name | Text(1300) | No | Formula: `FirstName & " " & LastName` |
| Gross_Margin_Goal_Percent__c | Gross Margin Goal % | Percent | No | — |
| LAST_NAME__c | LAST_NAME | Text(1300) | No | Formula: `UPPER( LastName )` |
| payout_approver__c | Payout Approver | Lookup(User) | No | — |
| Staff_ID__c | Staff ID | Text(18) | No | — |
| UserId_18__c | UserId(18) | Text(1300) | No | Formula: `CASESAFEID(Id)` |


<details><summary>Package fields on User (29)</summary>

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| dupcheck__dc3DisableDCTriggers__c | Disable All Deduplicate triggers | Checkbox | Yes | — |
| dupcheck__dc3DisableDuplicateCheck__c | Disable Deduplicate | Checkbox | Yes | — |
| FSSK__FSK_FSL_Resource_Type__c | SFS Resource Type | Picklist | No | A Field Service Starter Kit package field: 
When an admin creates or updates user records, the SFS Resource Type field on the user object allows the admin to assign permission sets to the user and determine whether a Service Resource record should be created and associated to the user as well. |
| maps__ActivityGenerationObjects__c | Activity Generation Object | Text(255) | No | — |
| maps__AllowMapsExports__c | Allow Maps Exports | Checkbox | Yes | — |
| maps__BetaTester__c | Maps Beta Tester | Checkbox | Yes | — |
| maps__DefaultLatitude__c | Maps Default Latitude | Number(3, 15) | No | — |
| maps__DefaultLongitude__c | Maps Default Longitude | Number(3, 15) | No | — |
| maps__DefaultProximityRadius__c | Default Proximity Radius | Number(5, 2) | No | — |
| maps__DefaultType__c | DefaultType | Text(255) | No | — |
| maps__DefaultZoomLevel__c | Maps Default Zoom Level | Number(2, 0) | No | — |
| maps__DeviceId__c | Device Id | Text(1300) | No | Formula: `"MALiveAvail-" + LEFT($Organization.Id, 15) + "-" + LEFT(Id, 15)` |
| maps__DeviceVendor__c | Device Vendor | Text(1300) | No | Formula: `"MapAnything"` |
| maps__DistanceCalculationRule__c | Distance Calculation Rules | Text(255) | No | — |
| maps__EditMapsOrgWideQueries__c | Edit Maps Org Wide Queries | Checkbox | Yes | — |
| maps__EditTimesheetEntries__c | Edit Timesheet entries | Checkbox | Yes | — |
| maps__FinishedAdvRouteSetup__c | Finished Maps Advanced Route Setup | Checkbox | Yes | — |
| maps__MapsSetting__c | Map Settings | Text Area(32768) | No | — |
| maps__MaxExportSize__c | Maps Max Export Size | Number(18, 0) | No | — |
| maps__MaxQuerySize__c | Maps Max Query Size | Number(6, 0) | No | — |
| maps__PreferredTypeOfMeasurement__c | Preferred Type of Measurement | Picklist | No | — |
| maps__ReceiveBatchExceptionEmails__c | Receive Batch Exception Emails | Checkbox | Yes | — |
| maps__RequireApprovalProcess__c | Require Approval Process | Checkbox | Yes | — |
| maps__TestUserLookup__c | TestUserLookup | Lookup(User) | No | — |
| maps__TimesheetPeriod__c | Timesheet Period | Text(255) | No | — |
| maps__TPApprover__c | Territory Planning Approver | Checkbox | Yes | — |
| maps__TPPublisher__c | Territory Planning Publisher | Checkbox | Yes | — |
| maps__Version__c | Maps Version | Picklist | No | — |
| wbsendit__Campaign_Monitor_User__c | Campaign Monitor User | Email | No | Used with the Campaign Monitor connector. Enter the users Campaign Monitor email address. |


</details>

---

## Order — Custom Fields

> Custom fields on `Order`. Package-namespaced fields listed separately at the bottom.

_No custom fields._


---

## Contract — Custom Fields

> Custom fields on `Contract`. Package-namespaced fields listed separately at the bottom.

_No custom fields._


---

## Campaign — Custom Fields

> Custom fields on `Campaign`. Package-namespaced fields listed separately at the bottom.

_No custom fields._


<details><summary>Package fields on Campaign (16)</summary>

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| wbsendit__Campaign_Monitor__c | Campaign Monitor | Text(1300) | No | Connect this Salesforce Campaign to sent campaigns in Campaign Monitor. Use this to manage campaign reports from within Salesforce. Send It will add any members it finds in Campaign Monitor to this campaign. |
| wbsendit__Campaign_Monitor_Id__c | Campaign Monitor Id | Text(255) | No | — |
| wbsendit__Email_Text_Version__c | Email Text Version | URL | No | Text version of the email sent. |
| wbsendit__Email_Web_Version__c | Email Web Version | URL | No | Web version of the email campaign. |
| wbsendit__Num_Bounced__c | Num Bounced | Number(18, 0) | No | Number of bounced emails for the Campaign Monitor campaign. |
| wbsendit__Num_Clicks__c | Num Clicks | Number(18, 0) | No | Number of clicks for the Campaign Monitor campaign. |
| wbsendit__Num_Forwards__c | Num Forwards | Number(18, 0) | No | Number of forwarded emails for the Campaign Monitor campaign. |
| wbsendit__Num_Likes__c | Num Likes | Number(18, 0) | No | Number of likes for the Campaign Monitor campaign. |
| wbsendit__Num_Mentions__c | Num Mentions | Number(18, 0) | No | Number of "Mentions" for the Campaign Monitor campaign. |
| wbsendit__Num_Opens__c | Num Opens | Number(18, 0) | No | Number of open emails for the associated Campaign Monitor campaign. |
| wbsendit__Num_Recipients__c | Num Recipients | Number(18, 0) | No | Number of recipients for the associated Campaign Monitor campaign. |
| wbsendit__Num_Spam_Complaints__c | Num Spam Complaints | Number(18, 0) | No | Number of Spam Complaints for the Campaign Monitor campaign. |
| wbsendit__Num_Unique_Opens__c | Num Unique Opens | Number(18, 0) | No | Number of unique open emails for the associated Campaign Monitor campaign. |
| wbsendit__Num_Unsubscribed__c | Num Unsubscribed | Number(18, 0) | No | Number of unsubscribes for the Campaign Monitor campaign. |
| wbsendit__Tags__c | Tags | Multi-Select Picklist | No | Campaign Monitor tags associated with a Campaign. |
| wbsendit__World_View_Email_Tracking__c | World View Email Tracking | URL | No | World view of the email campaign tracking. |


</details>

---

## Asset — Custom Fields

> Custom fields on `Asset`. Package-namespaced fields listed separately at the bottom.

_No custom fields._


---

## Product2 — Custom Fields

> Custom fields on `Product2`. Package-namespaced fields listed separately at the bottom.

_No custom fields._


---

## Pricebook2 — Custom Fields

> Custom fields on `Pricebook2`. Package-namespaced fields listed separately at the bottom.

_No custom fields._


---

## ServiceAppointment — Custom Fields

> Custom fields on `ServiceAppointment`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| CancellationReason__c | Cancellation Reason | Picklist | No | — |
| Contact_First_Name__c | Contact First Name | Text(1300) | No | Formula: `Contact.FirstName` |
| Contact_Phone__c | Contact Phone | Text(1300) | No | Formula: `HYPERLINK("tel://"+Contact.Phone,Contact.Phone)` |
| CustomerLocalStartTime__c | Customer Local Start Time | Text(50) | No | — |
| FSL_Compliance__c | Compliance | Formula (Number) | No | Formula: `If( ActualEndTime < DueDate , 1,0)` |
| FSL_FTFR_Count__c | FTFR Count | Formula (Number) | No | Formula: `IF(ISPICKVAL(Status,'Cannot Complete'),0,100)` |
| LegacyId__c | LegacyId | Text(18) | No | — |
| ManualAppointment__c | Manual Appointment | Checkbox | Yes | — |
| Owner_Email__c | Owner Email | Text(1300) | No | Formula: `Owner:User.Email` |
| Owner_Name__c | Owner Name | Text(1300) | No | Formula: `Owner:User.FirstName &" "& Owner:User.LastName` |
| Owner_Phone__c | Owner Phone | Text(1300) | No | Formula: `Owner:User.Phone` |
| ScheduledStartTime__c | ScheduledStartTime | Formula (Date/Time) | No | Formula: `SchedStartTime` |
| SchedulePolicyViolations__c | Schedule Policy Violations | Text Area(255) | No | — |
| WorkOrderName__c | Work Order Name | Text(1300) | No | Formula: `FSSK__FSK_Work_Order__r.Name__c` |


<details><summary>Package fields on ServiceAppointment (37)</summary>

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| FSL__Appointment_Grade__c | Appointment Grade | Number(3, 2) | No | — |
| FSL__Auto_Schedule__c | Auto Schedule | Checkbox | Yes | — |
| FSL__Duration_In_Minutes__c | Scheduled Duration | Formula (Number) | No | Formula: `IF (ISBLANK(SchedStartTime), 0, (SchedEndTime - SchedStartTime)*24*60)` |
| FSL__Emergency__c | Emergency | Checkbox | Yes | — |
| FSL__Gantt_Display_Date__c | Gantt Display Date | Date/Time | No | — |
| FSL__Gantt_Label_Details__c | Gantt Label Details | Text(255) | No | — |
| FSL__GanttColor__c | Gantt Color | Text(7) | No | — |
| FSL__GanttIcon__c | Gantt Icon | Text Area(2048) | No | Enter a URL for an icon. The URL must end in an image suffix, such as .png. |
| FSL__GanttLabel__c | Gantt Label | Text(255) | No | — |
| FSL__InJeopardy__c | In Jeopardy | Checkbox | Yes | — |
| FSL__InJeopardyReason__c | In Jeopardy Reason | Picklist | No | — |
| FSL__InternalSLRGeolocation__c | Internal SLR Geolocation | Geolocation | No | — |
| FSL__IsFillInCandidate__c | Is Fill In Candidate | Checkbox | Yes | — |
| FSL__IsMultiDay__c | Is MultiDay | Checkbox | Yes | — |
| FSL__Last_Updated_Epoch__c | Last Updated Epoch | Number(18, 0) | No | — |
| FSL__MDS_Calculated_length__c | Multiday Work Calculated length | Number(10, 0) | No | — |
| FSL__MDT_Operational_Time__c | Multiday Work Operational Time | Text Area(131072) | No | — |
| FSL__Pinned__c | Pinned | Checkbox | Yes | — |
| FSL__Prevent_Geocoding_For_Chatter_Actions__c | Prevent Geocoding For Chatter Actions | Checkbox | Yes | — |
| FSL__Related_Service__c | Related Service | Lookup(ServiceAppointment) | No | — |
| FSL__Same_Day__c | Same Day | Checkbox | Yes | — |
| FSL__Same_Resource__c | Same Resource | Checkbox | Yes | — |
| FSL__Schedule_Mode__c | Schedule Mode | Picklist | No | — |
| FSL__Schedule_over_lower_priority_appointment__c | Schedule Over Lower Priority Appointment | Checkbox | Yes | — |
| FSL__Scheduling_Policy_Used__c | Scheduling Policy Used | Lookup(FSL__Scheduling_Policy) | No | — |
| FSL__Time_Dependency__c | Time Dependency | Picklist | No | — |
| FSL__UpdatedByOptimization__c | UpdatedByOptimization | Checkbox | Yes | — |
| FSL__Use_Async_Logic__c | Use Async Logic | Checkbox | Yes | — |
| FSL__Virtual_Service_For_Chatter_Action__c | Virtual Service For Chatter Action (SLR) | Checkbox | Yes | — |
| FSSK__FSK_Add_Asset_to_Maintenance_Plan__c | Add Asset to Account Maintenance Plan | Checkbox | Yes | Add the installed Asset to the account maintenance plan upon completion |
| FSSK__FSK_Assigned_Service_Resource__c | Assigned Service Resource | Lookup(ServiceResource) | No | — |
| FSSK__FSK_Mobile_End_Time__c | Mobile End Time | Date/Time | No | — |
| FSSK__FSK_Mobile_Start_Time__c | Mobile Start Time | Date/Time | No | — |
| FSSK__FSK_Planned_Scheduled_End__c | Planned Scheduled End | Date/Time | No | — |
| FSSK__FSK_Planned_Scheduled_Start__c | Planned Scheduled Start | Date/Time | No | — |
| FSSK__FSK_Reject_Service_Appointment__c | Reject Service Appointment | Checkbox | Yes | — |
| FSSK__FSK_Work_Order__c | Work Order | Lookup(WorkOrder) | No | — |


</details>

---

## ServiceTerritory — Custom Fields

> Custom fields on `ServiceTerritory`. Package-namespaced fields listed separately at the bottom.

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Account_Manager__c | Account Manager | Lookup(User) | No | — |
| Company_Name__c | Company Name | Text(50) | No | — |
| Corp_Owned__c | Corp Owned | Checkbox | Yes | — |
| dbaName__c | dba Name | Text(75) | No | — |
| Estimator__c | Estimator | Lookup(User) | No | — |
| Licenses__c | License(s) | Text(75) | No | — |
| Partner_Manager__c | Partner/Manager | Lookup(User) | No | — |
| PhoneEstimator__c | Phone Estimator | Lookup(User) | No | — |
| PhonePricingOnly__c | Phone Pricing Only | Checkbox | Yes | — |
| PriceBook__c | Price Book | Lookup(Pricebook2) | No | — |
| Project_Manager__c | Project Manager | Lookup(User) | No | — |
| TaxRate__c | Tax Rate | Percent | Yes | — |
| Unique_Code__c | Unique Code | Text(10) | No | — |


<details><summary>Package fields on ServiceTerritory (8)</summary>

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| FSL__Hide_Emergency_Map__c | Hide Emergency Map | Checkbox | Yes | — |
| FSL__Internal_SLR_Geolocation__c | Internal SLR HomeAddress Geolocation | Geolocation | No | — |
| FSL__NumberOfServicesToDripFeed__c | Number Of Services To Drip Feed | Number(7, 0) | No | — |
| FSL__O2_Enabled__c | Use enhanced scheduling and optimization | Checkbox | Yes | — |
| FSL__Service_Cluster_Min_Size__c | Service Cluster Min Size (Closed Pilot) | Number(18, 0) | No | — |
| FSL__Service_Cluster_Proximity__c | Service Cluster Proximity (Closed Pilot) | Number(3, 3) | No | — |
| FSL__System_Jobs__c | System Jobs | Multi-Select Picklist | No | — |
| FSL__TerritoryLevel__c | Territory Level | Number(14, 0) | No | — |


</details>

---

## Custom Objects

> 44 PPP-owned custom objects. Each section lists custom fields on that object.

### AdCostDetail__c  
_Label: Ad Cost Detail_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| ACD_Checkover_Corp_Name__c | ACD Checkover (Corp Name) | Text(1300) | No | Formula: `TEXT( MONTH(Month_Start__c)) & " " & TEXT(YEAR(Month_Start__c) ) & " " & CorpAccount__r.Alternate...` |
| ACD_Checkover_ST__c | ACD Checkover (ST) | Text(1300) | No | Formula: `TEXT( MONTH(Month_Start__c)) & " " & TEXT(YEAR(Month_Start__c) ) & " " & ServiceTerritory__r.Name...` |
| AdCostSummary__c | Ad Cost Summary | Lookup(AdCostSummary) | Yes | — |
| AverageJobValue__c | Average Job Value | Formula (Currency) | No | Formula: `IF(Sales__c>0,Sales__c / ClosedWonCount__c,0)` |
| Budget__c | Budget | Currency | No | — |
| ClosedWonCount__c | Closed/Won Count | Number(18, 0) | No | — |
| CorpAccount__c | Corp (Account) | Lookup(Account) | No | — |
| Cost_per_Lead__c | Cost per Lead | Formula (Currency) | No | Formula: `IF(Spend__c=0,0,Spend__c / LeadCount__c)` |
| Cost_per_Sale__c | Cost per Sale | Formula (Currency) | No | Formula: `IF(OR(Spend__c=0,ClosedWonCount__c=0),0,Spend__c / ClosedWonCount__c)` |
| Lead_Created_Month__c | Lead Created Month | Formula (Number) | No | Formula: `MONTH( Month_Start__c )` |
| LeadCount__c | Lead Count | Number(18, 0) | No | — |
| MasterSpend__c | Master Spend | Lookup(MasterSpend) | No | — |
| Month_Start__c | Month Start | Date | No | From related Ad Cost Summary. Used for filtering reports by Month or FY. |
| Notes__c | Notes | Text Area(255) | No | — |
| OpportunityCount__c | Opportunity Count | Number(18, 0) | No | — |
| Sales__c | Sales | Currency | No | — |
| ServiceTerritory__c | Service Territory | Lookup(ServiceTerritory) | No | — |
| Spend__c | Spend | Currency | No | — |
| Subtype__c | Subtype | Text(255) | No | — |
| Title__c | Title | Text(255) | No | Leave blank for default |
| Type__c | Type | Picklist | Yes | — |
| WinRate__c | Win Rate | Formula (Percent) | No | Formula: `IF(ClosedWonCount__c>0,ClosedWonCount__c / LeadCount__c,0)` |


### AdCostSummary__c  
_Label: Ad Cost Summary_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| AverageJobValue__c | Average Job Value | Formula (Currency) | No | Formula: `IF( TotalSales__c>0, TotalSales__c / TotalClosedWonCount__c, 0)` |
| Month__c | Month | Picklist | Yes | — |
| Month_Start__c | Month Start | Date | No | Used for filtering reports by Month or FY. |
| OpportunityCount__c | Opportunity Count | Number(18, 0) | No | — |
| Title__c | Title | Text(1300) | No | Formula: `Year__c & " - " & TEXT(Month__c)` |
| TotalBudget__c | Total Budget | Currency | No | — |
| TotalClosedWonCount__c | Total Closed/Won Count | Number(18, 0) | No | — |
| TotalLeadCount__c | Total Lead Count | Number(18, 0) | No | — |
| TotalSales__c | Total Sales | Currency | No | — |
| TotalSpend__c | Total Spend | Currency | No | — |
| WinRate__c | Win Rate | Formula (Percent) | No | Formula: `IF(TotalClosedWonCount__c>0, TotalClosedWonCount__c / TotalLeadCount__c , 0)` |
| Year__c | Year | Text(4) | Yes | — |


### Allocation__c  
_Label: Allocation_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Allocated_Cost__c | Allocated Cost | Formula (Currency) | No | Formula: `Staff__r.Total_Software_Costs__c * Allocation__c` |
| Allocation__c | Allocation | Percent | No | — |
| April__c | April | Currency | No | — |
| August__c | August | Currency | No | — |
| Bill_To_Corp__c | Bill To Corp | Lookup(Account) | No | The corp that pays for software licenses, etc. |
| Checkover__c | Checkover | Text(1300) | No | Check = 
1) Month, Status, Corp, or Dates are blank, 
2) Status = Active, but End Date is less than today's date, 
3) if status = Active and this month's allocation <> allocated cost |
| December__c | December | Currency | No | — |
| Department__c | Department | Picklist | No | — |
| End_Date__c | End Date | Date | No | — |
| February__c | February | Currency | No | — |
| January__c | January | Currency | No | — |
| July__c | July | Currency | No | — |
| June__c | June | Currency | No | — |
| March__c | March | Currency | No | — |
| May__c | May | Currency | No | — |
| Notes__c | Notes | Text Area(10000) | No | — |
| November__c | November | Currency | No | — |
| October__c | October | Currency | No | — |
| September__c | September | Currency | No | — |
| Staff__c | Staff | Lookup(SFDC_Staff) | Yes | — |
| Start_Date__c | Start Date | Date | No | — |
| Status__c | Status | Picklist | No | — |


### Angi_Profile__c  
_Label: Angi Profile_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Profile_ID__c | Profile ID | Number(18, 0) | No | — |
| Profile_Name__c | Profile Name | Text(250) | No | — |


### Association__c  
_Label: Association_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Corporate_Document__c | Corporate Document | Lookup(Corporate_Document) | Yes | — |
| End_Date__c | End Date | Date | No | — |
| Legal__c | Legal | Lookup(Legal) | No | — |
| Regus_Office__c | Regus Office | Lookup(Account) | No | — |
| Staff__c | Staff | Lookup(SFDC_Staff) | No | — |
| Start_Date__c | Start Date | Date | No | — |
| Vehicle__c | Vehicle | Lookup(Vehicle) | No | — |


### Audit__c  
_Label: Audit_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Audit_Results__c | Audit Results | Picklist | No | — |
| Audit_Results_Amount__c | Audit Results Amount | Currency | No | — |
| Auditor__c | Auditor | Text Area(20000) | No | — |
| Broker__c | Broker | Text(30) | No | — |
| Broker_Email__c | Broker Email | Email | No | — |
| Broker_Fee__c | Broker Fee | Currency | No | — |
| Broker_Handling__c | Broker Handling | Text(30) | No | — |
| Broker_Phone__c | Broker Phone | Phone | No | — |
| Carrier__c | Carrier | Text(1300) | No | Formula: `Policy_Document__r.Carrier__c` |
| Completed_Worksheet__c | Completed Worksheet | Checkbox | Yes | — |
| Corporate_Document__c | Corporate Document | Lookup(Corporate_Document) | Yes | — |
| Date_Completed__c | Date Completed | Date | No | — |
| Date_Received__c | Date Received | Date | No | — |
| Notes__c | Notes | Text Area(20000) | No | — |
| Paid__c | Paid | Date | No | — |
| Policy_Document__c | Policy Document | Lookup(Policy_Document) | No | — |
| Policy_Number__c | Policy Number | Text(1300) | No | Formula: `Policy_Document__r.Policy_Number__c` |
| Policy_Period__c | Policy Period | Text(1300) | No | Formula: `TEXT(Policy_Document__r.Start_Date__c)+" - "+TEXT(Policy_Document__r.Expiration_Date__c)` |
| Refund_Received__c | Refund Received | Date | No | — |
| Status__c | Status | Picklist | No | — |
| Type__c | Type | Text(1300) | No | Formula: `TEXT( Corporate_Document__r.Type__c )` |


### CEMActivity__c  
_Label: CEM Activity_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Account__c | Account | Lookup(Account) | Yes | — |
| DateCompleted__c | Date Completed | Date | No | — |


### ChangeOrderLineItem__c  
_Label: Change Order Line Item_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| AreaName__c | AreaName | Text(1300) | No | Formula: `WorkOrderLineItem__r.AreaLabel__c` |
| ChangeOrder__c | Change Order | Lookup(ChangeOrder) | Yes | — |
| ProductCode__c | ProductCode | Text(1300) | No | Formula: `WorkOrderLineItem__r.ProductCode__c` |
| ProductName__c | ProductName | Text(1300) | No | Formula: `WorkOrderLineItem__r.ProductName__c` |
| TotalPrice__c | Total Price | Formula (Currency) | No | Formula: `WorkOrderLineItem__r.TotalPrice__c` |
| Type__c | Type | Picklist | Yes | — |
| WorkOrderLineItem__c | Work Order Line Item | Lookup(WorkOrderLineItem) | Yes | — |


### ChangeOrder__c  
_Label: Change Order_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| CostChange__c | CostChange | Currency | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| Notes__c | Notes | Text Area(32768) | No | — |
| ReasonForChange__c | Reason for Change | Picklist | Yes | — |
| ReasonForChangeOther__c | Other Reason for Change | Text(255) | No | — |
| Status__c | Status | Picklist | Yes | — |
| WorkOrder__c | Work Order | Lookup(WorkOrder) | Yes | — |


### CommissionRate__c  
_Label: Commission Rate_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Fiscal_Year__c | Fiscal Year | Multi-Select Picklist | No | — |
| Percentage__c | Percentage | Percent | No | — |
| Rate_Basis__c | Rate Basis | Picklist | No | — |
| RateBeginDate__c | Rate Begin Date | Date | No | — |
| RateEndDate__c | Rate End Date | Date | No | — |
| RateStatus__c | Rate Status | Picklist | No | — |
| User__c | User | Lookup(User) | No | — |


### Corporate_Document__c  
_Label: Corporate Document_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Account__c | Account | Lookup(Account) | No | — |
| Account_Closed__c | Account Closed | Date | No | — |
| Agent_Login_Password__c | Agent Login Password | Text(50) | No | — |
| Agent_Login_Site__c | Agent Login Site | URL | No | — |
| Agent_Login_Username__c | Agent Login Username | Text(50) | No | — |
| Application__c | Application | Checkbox | Yes | — |
| Based_on_Sales_Amount__c | Based on Sales Amount | Currency | No | — |
| Broker__c | Broker | Text(30) | No | — |
| Broker_Contact_Name__c | Broker Contact Name | Text(60) | No | — |
| Broker_Phone__c | Broker Phone | Phone | No | — |
| Cancelled_Date__c | Cancelled Date | Date | No | — |
| Carrier__c | Carrier | Text(50) | No | — |
| Color_Swatches__c | Color Swatches | Checkbox | Yes | — |
| Compliance_Status__c | Compliance Status | Picklist | No | — |
| Cost__c | Cost | Currency | No | — |
| Coverage_Included__c | Coverage Included | Multi-Select Picklist | No | — |
| Date_of_Incorporation__c | Date of Incorporation | Date | No | — |
| Denied_Missing_Docs__c | Denied/Missing Docs | Multi-Select Picklist | No | — |
| Discounts__c | Discounts | Multi-Select Picklist | No | — |
| Dissolved__c | Dissolved | Date | No | — |
| Driver_s_Listed__c | Driver(s) Listed | Text(50) | No | — |
| EIN__c | EIN | Text(18) | No | — |
| Exams__c | Exams | Text(50) | No | — |
| Expiration_Date__c | Expiration Date | Date | No | — |
| Fictitious_Name__c | Fictitious Name | Text(50) | No | — |
| File_Date__c | File Date | Date | No | — |
| Folio_Number__c | Folio Number | Text(16) | No | — |
| Formed_by__c | Formed by | Text(30) | No | — |
| Frequency__c | Frequency | Text(30) | No | — |
| Handling_Firm__c | Handling Firm | Text(30) | No | — |
| Images__c | Images | Checkbox | Yes | — |
| Last_Filed__c | Last Filed | Date | No | — |
| Latest_Expiration__c | Latest Expiration | Date | No | — |
| Licensee__c | Licensee | Lookup(User) | No | — |
| Licensee_Staff__c | Licensee | Lookup(SFDC_Staff) | No | — |
| Login_Password__c | Login Password | Text(55) | No | — |
| Login_Site__c | Login Site | Text Area(500) | No | — |
| Login_Username__c | Login Username | Text(60) | No | — |
| Named_Insured__c | Named Insured | Text(80) | No | — |
| Notes__c | Notes | Text Area(20000) | No | — |
| Number__c | Number | Text(25) | No | — |
| Operating_States__c | Operating States | Text(100) | No | — |
| Owner__c | Owner | Text(30) | No | — |
| Partner__c | Partner | Text(50) | No | — |
| Permit_Status__c | Permit Status | Picklist | No | — |
| Policy_Limits__c | Policy Limits | Text(100) | No | — |
| Policy_Type__c | Policy Type | Picklist | No | — |
| Premium_Base__c | Premium Base | Currency | No | — |
| Premium_Other__c | Premium Other | Currency | No | — |
| Premium_Surcharge__c | Premium Surcharge | Currency | No | — |
| Premium_Taxes__c | Premium Taxes | Currency | No | — |
| Premium_Terrorism__c | Premium Terrorism | Currency | No | — |
| Premium_Total__c | Premium Total (Formula) | Formula (Currency) | No | Formula: `Premium_Base__c + Premium_Other__c + Premium_Surcharge__c + Premium_Taxes__c + Premium_Terrorism__c` |
| Premium_Total_Rollup__c | Premium Total | Currency | No | — |
| Registered_Agent_Address__c | Registered Agent Address | Address (compound) | No | — |
| Registered_Agent_Exp_Date__c | Registered Agent Exp Date | Date | No | — |
| Registered_Agent_Fee__c | Registered Agent Fee | Currency | No | — |
| Registered_Agent_Name__c | Registered Agent Name | Text(50) | No | — |
| Registered_Agent_Phone__c | Registered Agent Phone | Phone | No | — |
| Registered_Name__c | Registered Name | Text(50) | No | — |
| Requested_By__c | Requested By | Text(30) | No | — |
| Sales_Tax_Rate__c | Sales Tax Rate | Percent | No | — |
| Sales_Tax_Registration__c | Sales Tax Registration | Text(50) | No | — |
| Scope_of_Work__c | Scope of Work | Checkbox | Yes | — |
| Security_Questions__c | Security Questions | Text Area(500) | No | — |
| SR__c | SR # | Text(10) | No | — |
| Start_Date__c | Start Date | Date | No | — |
| State__c | State | Picklist | No | — |
| Status__c | Status | Picklist | No | — |
| Structure__c | Structure | Text(10) | No | — |
| Tax_Period__c | Tax Period | Text(30) | No | — |
| Tax_Type__c | Tax Type | Picklist | No | — |
| Terms_of_Policy__c | Terms of Policy | Text(200) | No | — |
| Type__c | Type | Picklist | No | — |
| Vehicle__c | Vehicle | Lookup(Vehicle) | No | — |
| Withdrawal__c | Withdrawal | Date | No | — |
| Work_Order__c | Work Order | Lookup(WorkOrder) | No | — |


### DocumentRequirement__c  
_Label: Document Requirement_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| COI_Issued__c | COI Issued | Picklist | No | — |
| Description__c | Description | Text Area(32768) | No | — |
| Status__c | Status | Picklist | No | — |
| Type__c | Type | Multi-Select Picklist | No | — |
| WorkOrder__c | Work Order | Lookup(WorkOrder) | Yes | — |


### Equipment__c  
_Label: Equipment_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Agreement__c | Agreement | Date | No | The day of the handling agreement being signed. |
| Cost__c | Cost | Currency | No | — |
| HD_Space__c | HD Space | Text(18) | No | — |
| HD_Type__c | HD Type | Picklist | No | — |
| Inventoried__c | Inventoried | Date | No | — |
| Last_Distributed__c | Last Distributed | Date | No | — |
| Last_Inventoried_by__c | Last Inventoried by | Lookup(SFDC_Staff) | No | — |
| Location__c | Location | Text(18) | No | — |
| Make_Model__c | Make & Model | Text(25) | No | — |
| Monitor_Ports__c | Monitor Ports | Picklist | No | — |
| Monitors_Attached__c | Monitors Attached | Number(1, 0) | No | — |
| Notes__c | Notes | Text Area(10000) | No | — |
| Offirce_Installed__c | Office Installed | Picklist | No | — |
| OS__c | OS | Text(18) | No | — |
| OS_Type__c | OS Type | Picklist | No | — |
| Password__c | Password | Text(18) | No | — |
| Port_1_Type__c | Port 1 Type | Picklist | No | — |
| Port_2_Type__c | Port 2 Type | Picklist | No | — |
| Port_3_Type__c | Port 3 Type | Picklist | No | — |
| Port_4_Type__c | Port 4 Type | Picklist | No | — |
| Processor__c | Processor | Text(18) | No | — |
| Processor_Speed__c | Processor Speed | Text Area(255) | No | — |
| Purchased__c | Purchased | Date | No | — |
| RAM__c | RAM | Picklist | No | — |
| Staff__c | Staff | Lookup(SFDC_Staff) | Yes | — |
| Type__c | Type | Picklist | No | — |
| Webroot_Expiration__c | Webroot Expiration | Date | No | — |
| Webroot_License__c | Webroot License | Text(24) | No | — |


### ErrorLog__c  
_Label: Error Log_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Error__c | Error | Text Area(25000) | No | — |
| Payload__c | Payload | Text Area(25000) | No | — |
| Source__c | Source | Text(255) | No | — |
| Status__c | Status | Picklist | No | — |


### FlowPersonalConfiguration__c  
_Label: Flow Personal Configuration_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| ActorId__c | Actor Id | Text(18) | No | — |
| Config1Name__c | Config1Name | Text(255) | No | — |
| Config1Value__c | Config1Value | Text(255) | No | — |
| Config2Name__c | Config2Name | Text(255) | No | — |
| Config2Value__c | Config2Value | Text(255) | No | — |
| Config3Name__c | Config3Name | Text(255) | No | — |
| Config3Value__c | Config3Value | Text(255) | No | — |
| Config4Name__c | Config4Name | Text(255) | No | — |
| Config4Value__c | Config4Value | Text(255) | No | — |
| Config5Name__c | Config5Name | Text(255) | No | — |
| Config5Value__c | Config5Value | Text(255) | No | — |
| Config6Name__c | Config6Name | Text(255) | No | — |
| Config6Value__c | Config6Value | Text(255) | No | — |
| Config7Name__c | Config7Name | Text(255) | No | — |
| Config7Value__c | Config7Value | Text(255) | No | — |
| Config8Name__c | Config8Name | Text(255) | No | — |
| Config8Value__c | Config8Value | Text(255) | No | — |
| Config9Name__c | Config9Name | Text(255) | No | — |
| Config9Value__c | Config9Value | Text(255) | No | — |
| LocationId__c | Location Id | Text(18) | No | — |


### FlowScaffold__c  
_Label: FlowScaffold_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Contact__c | Contact | Lookup(Contact) | No | — |


### FlowTableViewDefinition__c  
_Label: FlowTableViewDefinition_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Active__c | Active | Checkbox | Yes | — |
| Alignments__c | Alignments | Text Area(2000) | No | — |
| Cell_Attributes__c | Cell Attributes | Text Area(2000) | No | — |
| Edits__c | Edits | Text Area(2000) | No | — |
| Field_API_Names__c | Field API Names | Text Area(2000) | No | — |
| Field_Sorting__c | Field Sorting | Text Area(2000) | No | — |
| Filters__c | Filters | Text Area(2000) | No | — |
| Icons__c | Icons | Text Area(2000) | No | — |
| Labels__c | Labels | Text Area(2000) | No | — |
| Object_API_Name__c | Object API Name | Text(120) | Yes | — |
| Other_Attributes__c | Other Attributes | Text Area(2000) | No | — |
| Selection_Method__c | Selection Method | Picklist | Yes | — |
| Type_Attributes__c | Type Attributes | Text Area(2000) | No | — |
| View_Name__c | View Name | Text(255) | Yes | — |
| Widths__c | Widths | Text Area(2000) | No | — |
| Wraps__c | Wraps | Text Area(2000) | No | — |


### HomeAdvisor_Profile__c  
_Label: HomeAdvisor Profile_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Profile_ID__c | Profile ID | Number(18, 0) | No | — |
| Profile_Name__c | Profile Name | Text(255) | No | — |


### Legal__c  
_Label: Legal_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Account__c | Account | Lookup(Account) | No | — |
| Account_Sub__c | Account- Sub | Lookup(Account) | No | — |
| Amount__c | Amount | Currency | No | — |
| Amount_Status__c | Amount Status | Picklist | No | — |
| Attorney_File_Number__c | Attorney File Number | Text(60) | No | — |
| Auto_Shop__c | Auto Shop | Text Area(500) | No | — |
| Broker__c | Broker | Text(60) | No | — |
| Carrier__c | Carrier | Text(30) | No | — |
| Case__c | Case | Lookup(Case) | No | — |
| Case_Owner__c | Case Owner | Text(60) | No | — |
| Claim__c | Claim # | Text(50) | No | — |
| Claim_Handler__c | Claim Handler | Text(30) | No | — |
| Claim_Handler_Email__c | Claim Handler Email | Email | No | — |
| Claim_Handler_Phone__c | Claim Handler Phone | Phone | No | — |
| Claim_Handler_Title__c | Claim Handler Title | Text(15) | No | — |
| Claim_Rep_Email__c | Claim Rep Email | Email | No | — |
| Claim_Rep_Phone__c | Claim Rep Phone | Phone | No | — |
| Claim_Status__c | Claim Status | Picklist | No | — |
| Claim_Type__c | Claim Type | Picklist | No | — |
| Compensation__c | Compensation | Currency | No | — |
| Contact__c | Contact | Text(60) | No | — |
| Customer_s_Address__c | Customer's Address | Text Area(500) | No | — |
| Customer_s_Email__c | Customer's Email | Email | No | — |
| Customer_s_Name__c | Customer’s Name | Lookup(Contact) | No | — |
| Customer_s_Phone__c | Customer’s Phone | Phone | No | — |
| Deadline__c | Deadline | Date | No | — |
| Deadline_to_Respond__c | Deadline to Respond | Date | No | — |
| Deductible__c | Deductible | Currency | No | — |
| Dispute_Amount__c | Dispute Amount | Currency | No | — |
| Dispute_Fee__c | Dispute Fee | Currency | No | — |
| Driver__c | Driver | Text(55) | No | — |
| Handling_Firm__c | Handling Firm | Text(30) | No | — |
| Hearing_Date__c | Hearing Date | Date | No | — |
| Installation_Date__c | Installation Date | Date | No | — |
| Last_Attendance_Date__c | Last Attendance Date | Date | No | — |
| Legal_Fee__c | Legal Fee | Currency | No | — |
| Legal_Notes__c | Legal Notes | Text Area(20000) | No | — |
| Lien_Filed__c | Lien Filed | Date | No | — |
| Non_PPP_Carrier__c | Non-PPP Carrier | Text(60) | No | — |
| Non_PPP_Legal_Notes__c | Non-PPP Legal Notes | Text Area(20000) | No | — |
| Non_PPP_Legal_Team__c | Non-PPP Legal Team | Text(60) | No | — |
| Notes__c | Notes | Text Area(30000) | No | — |
| Opportunity_Owner__c | Opportunity Owner | Lookup(User) | No | — |
| Partner_Owner__c | Partner Owner | Lookup(User) | No | — |
| Payment_Status__c | Payment Status | Picklist | No | — |
| Policy_Number__c | Policy Number | Text(50) | No | — |
| Policy_Type__c | Policy Type | Picklist | No | — |
| PPP_Legal_Team__c | PPP Legal Team | Text(60) | No | — |
| Reference_Number__c | Reference Number | Text(30) | No | — |
| Reported_Date__c | Reported Date | Date | No | — |
| Status__c | Status | Picklist | No | — |
| Subtype__c | Subtype | Text(50) | No | — |
| Total_Work_Order_Amount__c | Total Work Order Amount | Currency | No | — |
| Transaction_Date__c | Transaction Date | Date | No | — |
| Type__c | Type | Picklist | No | — |
| Vehicle__c | Vehicle | Lookup(Vehicle) | No | — |
| Work_Order__c | Work Order | Lookup(WorkOrder) | No | — |


### MarketingProfile__c  
_Label: Marketing Profile_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| AuditDate__c | Audit Date | Date | No | — |
| AuditedBy__c | Audited By | Text(30) | No | — |
| AverageRating__c | Average Rating | Formula (Number) | No | Formula: `TotalRatings__c / TotalReviews__c` |
| Completion__c | Completion % | Percent | No | — |
| LandingPage__c | Landing Page | URL | No | — |
| LastReview__c | Last Review | Date | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| Licenses__c | Licenses | Text(255) | No | — |
| LocalListingPhone__c | Local Listing Phone | Phone | No | — |
| LoginCredentials__c | Login Credentials | Text Area(1000) | No | — |
| MarketingAccount__c | Marketing Account | Lookup(Account) | Yes | — |
| NegativeReviews__c | Negative Reviews | Number(18, 0) | No | — |
| Notes__c | Notes | Text Area(30000) | No | — |
| Operating_State__c | Operating State | Picklist | No | — |
| Phone__c | Phone | Phone | No | — |
| PlatformTotalReviews__c | Platform Total Reviews | Number(5, 0) | No | — |
| PositiveReviews__c | Positive Reviews | Number(18, 0) | No | — |
| ProfileCreated__c | Profile Created | Date | No | — |
| ProfileURL__c | Profile URL | URL | No | — |
| Regus_Office__c | Regus Office | Lookup(Account) | No | — |
| RemovedReviews__c | Removed Reviews | Number(18, 0) | No | — |
| RequestReviewLink__c | Request Review Link | URL | No | — |
| Status__c | Status | Picklist | No | — |
| TotalRatings__c | Total Ratings | Number(18, 0) | No | — |
| TotalReviews__c | Total Reviews | Number(18, 0) | No | — |
| Type__c | Type | Picklist | No | — |
| UnrespondedReviews__c | Unresponded Reviews | Number(18, 0) | No | — |


### MasterSpend__c  
_Label: Master Spend_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| AdCostSummary__c | Ad Cost Summary | Lookup(AdCostSummary) | Yes | — |
| Description__c | Description | Text Area(32768) | No | — |
| Title__c | Title | Text(255) | Yes | — |
| TotalSpend__c | Total Spend | Currency | No | — |
| Type__c | Type | Picklist | No | — |


### PaintColor__c  
_Label: Paint Color_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Code__c | Code | Text(255) | No | — |
| Collection__c | Collection | Text(255) | No | — |
| FullName__c | Full Name | Text(1300) | No | Formula: `Code__c & " " & Name__c` |
| HexValue__c | Hex Value | Text(10) | No | — |
| Manufacturer__c | Manufacturer | Lookup(Account) | No | — |
| Name__c | Name | Text(255) | No | — |


### Payment_Term__c  
_Label: Payment Term_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Amount__c | Amount | Currency | No | — |
| Amount_Owed__c | Amount Owed | Currency | No | — |
| Deposit_Type_Order__c | Deposit Type Order | Formula (Number) | No | Formula: `IF( ISPICKVAL(Payment_Type__c,'Deposit'),1, IF( ISPICKVAL(Payment_Type__c,'Progress'),2, IF( ISPI...` |
| Due_Date__c | Due Date | Date | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| Notes__c | Notes | Text Area(255) | No | — |
| Order__c | Order | Number(2, 0) | No | — |
| Paid_In_Full__c | Paid In Full | Checkbox | Yes | — |
| Paid_In_Full_Date__c | Paid In Full Date | Date | No | — |
| Payment_Type__c | Payment Type | Picklist | No | — |
| Percent__c | Percent | Percent | No | — |
| Quote__c | Quote | Lookup(Quote) | No | — |
| Unpaid_Amount__c | Unpaid Amount | Currency | No | — |
| Value_Type__c | Value Type | Picklist | Yes | — |
| WorkOrder__c | Work Order | Lookup(WorkOrder) | No | — |


### Policy_Document__c  
_Label: Policy Document_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Audit_Result__c | Audit Result | Currency | No | — |
| Broker__c | Broker | Text(30) | No | — |
| Broker_Contact_Name__c | Broker Contact Name | Text(60) | No | — |
| Broker_Email__c | Broker Email | Email | No | — |
| Broker_Phone__c | Broker Phone | Phone | No | — |
| Brokerage_Fee__c | Brokerage Fee | Currency | No | — |
| Cancelled_Date__c | Cancelled Date | Date | No | — |
| Carrier__c | Carrier | Text(30) | No | — |
| COI_Issued_to__c | COI Issued to | Multi-Select Picklist | No | — |
| Compliance_Status__c | Compliance Status | Picklist | No | — |
| Corporate_Document__c | Corporate Document | Lookup(Corporate_Document) | Yes | — |
| Coverage_Included__c | Coverage Included | Multi-Select Picklist | No | — |
| Deductible__c | Deductible | Currency | No | — |
| Discount__c | Discount | Multi-Select Picklist | No | — |
| Driver_s_Listed__c | Driver(s) Listed | Text(50) | No | — |
| Expiration_Date__c | Expiration Date | Date | No | — |
| Is_Latest_Expired__c | Is Latest Expired | Text(1300) | No | Formula: `IF( Corporate_Document__r.Latest_Expiration__c = Expiration_Date__c , "Yes","No")` |
| Login_Password__c | Login Password | Text(55) | No | — |
| Login_Site__c | Login Site | Text Area(500) | No | — |
| Login_Username__c | Login Username | Text(60) | No | — |
| Named_Insured__c | Named Insured | Text(30) | No | — |
| Notes__c | Notes | Text Area(20000) | No | — |
| Operating_States__c | Operating States | Text(100) | No | — |
| Owner__c | Owner | Text(30) | No | — |
| Policy_Limits__c | Policy Limits | Text(100) | No | — |
| Policy_Number__c | Policy Number | Text(30) | No | — |
| Policy_Received__c | Policy Received | Checkbox | Yes | — |
| Policy_Type__c | Policy Type | Picklist | No | — |
| Premium_Base__c | Premium Base | Currency | No | — |
| Premium_Based_on_Quantity__c | Premium Based on Quantity | Text(30) | No | — |
| Premium_Criteria__c | Premium Criteria | Picklist | No | — |
| Premium_Other__c | Premium Other | Currency | No | — |
| Premium_Surcharge__c | Premium Surcharge | Currency | No | — |
| Premium_Taxes__c | Premium Taxes | Currency | No | — |
| Premium_Terrorism__c | Premium Terrorism | Currency | No | — |
| Premium_Total__c | Premium Total | Formula (Currency) | No | Formula: `Premium_Base__c + Premium_Taxes__c + Premium_Terrorism__c + Premium_Surcharge__c + Premium_Other_...` |
| Registered_Name__c | Registered Name | Text(50) | No | — |
| Renewal_Type__c | Renewal Type | Picklist | No | — |
| Security_Questions__c | Security Questions | Text Area(255) | No | — |
| Start_Date__c | Start Date | Date | No | — |
| Status__c | Status | Picklist | No | — |
| Terms_of_Policy__c | Terms of Policy | Text(200) | No | — |
| Type__c | Type | Text(1300) | No | Formula: `TEXT(Corporate_Document__r.Type__c)` |
| Vehicle__c | Vehicle | Lookup(Vehicle) | No | — |


### ProcessLog__c  
_Label: Process Log_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Details__c | Details | Text Area(32768) | No | — |
| End__c | End | Date/Time | No | — |
| Start__c | Start | Date/Time | No | — |
| TItle__c | TItle | Text(255) | No | — |
| Type__c | Type | Picklist | No | — |


### QuotaPoints__c  
_Label: Quota Points_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| DateAttained__c | Date Attained | Date | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| Notes__c | Notes | Text Area(255) | No | — |
| Opportunity__c | Opportunity | Lookup(Opportunity) | No | — |
| OpportunityType__c | Opportunity Type | Picklist | No | — |
| Points__c | Points | Number(16, 2) | No | — |
| QuotaType__c | Quota Type | Picklist | No | — |
| RepeatReferral__c | Repeat/Referral | Formula (Checkbox) | No | Formula: `if(ispickval(OpportunityType__c ,"Repeat/Referral"),TRUE,FALSE)` |
| ServiceTerritory__c | Service Territory | Lookup(ServiceTerritory) | No | — |
| Status__c | Status | Picklist | Yes | — |
| SubQuota__c | Sub Quota | Lookup(SubQuota) | Yes | — |
| WorkOrder__c | Work Order | Lookup(WorkOrder) | No | — |
| WorkOrderStatus__c | Work Order Status | Text(1300) | No | Formula: `text(WorkOrder__r.Status)` |


### Region__c  
_Label: Region_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Country__c | Country | Text(40) | No | — |
| EDT_Time_Diferens__c | EDT Time Deferens (Hours) | Formula (Number) | No | Formula: `4 + Time_Difference__c` |
| State__c | State | Text(40) | No | — |
| Time_Difference__c | Time Difference | Number(5, 0) | No | — |


### Review__c  
_Label: Review_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Account__c | Account | Lookup(Account) | No | — |
| BadReview__c | Bad Review | Formula (Checkbox) | No | Formula: `IF(ReviewType__c = "Bad Review", True, False)` |
| Comments__c | Comments | Text Area(50768) | No | — |
| GoodReview__c | Good Review | Formula (Checkbox) | No | Formula: `IF(ReviewType__c = "Good Review", True, False)` |
| LaborCrew__c | Labor Crew | Text(1300) | No | Formula: `WorkOrder__r.Contractor__r.Name` |
| LegacyId__c | LegacyId | Text(18) | No | — |
| MarketingProfile__c | Marketing Profile | Lookup(MarketingProfile) | Yes | — |
| Opportunity__c | Opportunity | Lookup(Opportunity) | No | — |
| Rating__c | Rating | Picklist | Yes | — |
| RatingNumber__c | Rating Number | Formula (Number) | No | Formula: `IF( TEXT(Rating__c)="5",5, IF( TEXT(Rating__c)="4",4, IF( TEXT(Rating__c)="3",3, IF( TEXT(Rating_...` |
| Removed__c | Removed | Checkbox | Yes | — |
| Replied__c | Replied | Checkbox | Yes | — |
| ReviewDate__c | Review Date | Date | No | — |
| ReviewType__c | Review Type | Text(1300) | No | Formula: `IF( OR( TEXT(Rating__c)="1", TEXT(Rating__c)="2", TEXT(Rating__c)="3"),'Bad Review', IF( OR( TEXT...` |
| Status__c | Status | Picklist | No | — |
| TransferStatus__c | Transfer Status | Picklist | No | — |
| WorkOrder__c | Work Order | Lookup(WorkOrder) | No | — |
| WorkOrderComplete__c | Work Order Complete | Date | No | Formula: `WorkOrder__r.EndDate` |


### SFDC_Benefit__c  
_Label: Benefit_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Benefit_Plan__c | Benefit Plan | Picklist | No | — |
| Benefit_Type__c | Benefit Type | Picklist | No | — |
| Employee__c | Employee | Lookup(SFDC_Staff) | No | — |
| Months_for_Plan__c | # Months for Plan | Number(2, 0) | No | — |
| Plan_End_Date__c | Plan End Date | Date | No | Formula: `Plan_Start_Date__c + Months_for_Plan__c` |
| Plan_Start_Date__c | Plan Start Date | Date | No | — |
| Request_Date__c | Request Date | Date | No | — |


### SFDC_Job_Function__c  
_Label: Job Function_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Benefit_Options__c | Benefit Options | Multi-Select Picklist | No | — |
| Core_Location__c | Core Location | Picklist | No | — |
| Department__c | Department | Picklist | No | — |
| Salary_Range__c | Salary Range | Picklist | No | — |


### SFDC_PTO_Request__c  
_Label: PTO Request_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Date_of_Request__c | Date of Request | Date | Yes | — |
| Hours_Off__c | Hours Off | Number(5, 2) | No | — |
| Request_End_Date__c | Request End Date | Date | Yes | — |
| Request_Start_Date__c | Request Start Date | Date | Yes | — |
| Request_Type__c | Request Type | Picklist | Yes | — |
| Staff__c | Staff | Lookup(SFDC_Staff) | Yes | — |


### SFDC_Performance_Review__c  
_Label: Performance Review_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Customer_Service_Internal_External__c | Customer Service (Internal & External) | Multi-Select Picklist | No | — |
| Customer_Service_Notes__c | Customer Service Notes | Text Area(255) | No | — |
| Customer_Service_Rating__c | Customer Service Rating | Picklist | No | — |
| Dependability__c | Dependability | Multi-Select Picklist | No | — |
| Dependability_Notes__c | Dependability Notes | Text Area(255) | No | — |
| Dependability_Rating__c | Dependability Rating | Picklist | No | — |
| Employee__c | Employee | Lookup(SFDC_Staff) | No | — |
| Employee_Comments__c | Employee Comments | Text Area(32000) | No | — |
| Employee_Review_Notes__c | Employee Review Notes | Text Area(32000) | No | — |
| Initiative__c | Initiative | Multi-Select Picklist | No | — |
| Initiative_Notes__c | Initiative Notes | Text Area(255) | No | — |
| Initiative_Rating__c | Initiative Rating | Picklist | No | — |
| Job_Knowledge__c | Job Knowledge | Multi-Select Picklist | No | — |
| Job_Knowledge_Notes__c | Job Knowledge Notes | Text Area(255) | No | — |
| Job_Knowledge_Rating__c | Job Knowledge Rating | Picklist | No | — |
| Manager_Status__c | Manager Status | Picklist | No | — |
| Period_Review__c | Period Review | Text(30) | No | — |
| Quality_of_Work__c | Quality of Work | Multi-Select Picklist | No | — |
| Quality_of_Work_Notes__c | Quality of Work Notes | Text Area(255) | No | — |
| Quality_of_Work_Rating__c | Quality of Work Rating | Picklist | No | — |
| Quantity_of_Work__c | Quantity of Work | Multi-Select Picklist | No | — |
| Quantity_of_Work_Notes__c | Quantity of Work Notes | Text Area(255) | No | — |
| Quantity_of_Work_Rating__c | Quantity of Work Rating | Picklist | No | — |
| Review_Date__c | Review Date | Date/Time | No | — |
| Review_Notes__c | Review Notes | Text Area(32000) | No | — |
| Review_Overall_Score__c | Review Overall Score | Picklist | No | — |
| Review_Type__c | Review Type | Picklist | No | — |
| Reviewer__c | Reviewer | Text(50) | No | — |
| Supervision__c | Supervision | Multi-Select Picklist | No | — |
| Supervision_Notes__c | Supervision Notes | Text Area(255) | No | — |
| Supervision_Rating__c | Supervision Rating | Picklist | No | — |
| Teamwork_and_Cooperation__c | Teamwork and Cooperation | Multi-Select Picklist | No | — |
| Teamwork_and_Cooperation_Notes__c | Teamwork and Cooperation Notes | Text Area(255) | No | — |
| Teamwork_Cooperation_Rating__c | Teamwork/Cooperation Rating | Picklist | No | — |


### SFDC_Salary_History__c  
_Label: Salary History_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Annual_OTE__c | Annual OTE | Currency | No | — |
| Base_Salary__c | Base Salary | Currency | No | — |
| Employee__c | Employee | Lookup(SFDC_Staff) | Yes | — |
| Quarterly_Bonus__c | Quarterly Bonus | Formula (Currency) | No | Formula: `(Annual_OTE__c - Base_Salary__c ) / 4` |
| Salary_End_Date__c | Salary End Date | Date | No | — |


### SFDC_Staff__c  
_Label: Staff_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Additional_Education__c | Additional Education | Text Area(32000) | No | — |
| Allergies__c | Allergies | Text Area(255) | No | — |
| Background_Check__c | Background Check | Checkbox | Yes | — |
| Background_Check_Date__c | Background Check Date | Date | No | — |
| Background_Check_Notes__c | Background Check Notes | Text Area(32768) | No | — |
| Background_Status__c | Background Status | Picklist | No | — |
| Bank_Account__c | Bank Account | Text Area(255) | No | — |
| Bill_To_Corp__c | Bill To Corp | Lookup(Account) | No | The corp that pays for software licenses, etc. |
| Bonus_Potential__c | Bonus (Potential) | Formula (Currency) | No | Formula: `Salary__c * 0.05` |
| BU_Description__c | BU Description | Text(70) | No | — |
| Business_Cards__c | Business Cards | Checkbox | Yes | — |
| Business_Unit__c | Business Unit | Text(60) | No | — |
| Call_Center__c | Call Center # | Phone | No | — |
| Code_of_Conduct_and_Ethics__c | Code of Conduct and Ethics | Text Area(255) | No | — |
| Corp_Name__c | Corp Name | Text(250) | No | — |
| Corp_Photo__c | Corp Photo | Text(1300) | No | Formula: `IMAGE("http://www.salesforceius.com/appx/staffpix/"& JPG__c , Name )` |
| Credit_Card__c | Credit Card | Picklist | No | — |
| Days_Employed__c | Days Employed | Formula (Number) | No | Formula: `TODAY () - Hire_Date__c` |
| Dental_Benefits__c | Dental Benefits | Checkbox | Yes | — |
| Department__c | Department | Multi-Select Picklist | No | — |
| Desk_Terminal__c | Desk Terminal | Text(5) | No | — |
| Diversity_Equity_and_Inclusion__c | Diversity, Equity, and Inclusion | Text Area(255) | No | — |
| DOB_Day__c | DOB Day | Picklist | No | — |
| DOB_Month__c | DOB Month | Picklist | No | — |
| Drivers_License__c | Driver's License | Checkbox | Yes | — |
| Education__c | Degrees | Multi-Select Picklist | No | — |
| EMERGENCY_CONTACT__c | Emergency Contact | Text(50) | No | — |
| Emergency_Contact_Phone__c | Emergency Contact Phone | Phone | No | — |
| Emergency_Contact_Relationship__c | Emergency Contact Relationship | Picklist | No | — |
| Emergency_Relationship__c | Emergency Relationship | Picklist | No | — |
| EMP_ID__c | EMP ID | Number(15, 0) | No | — |
| Employee_ID__c | Employee ID | Auto Number | Yes | — |
| Employee_Status__c | Employee Status | Picklist | Yes | — |
| Employee_Type__c | Employee Type | Picklist | No | — |
| Ethnicity__c | Ethnicity | Picklist | No | — |
| Field_Location__c | Field Location | Multi-Select Picklist | No | — |
| Former_Employer_1__c | Former Employer 1 | Text(50) | No | — |
| Former_Employer_3__c | Former Employer 3 | Text(50) | No | — |
| Former_Employer__c | Former Employer 2 | Text(50) | No | — |
| Gender__c | Gender | Picklist | No | — |
| Group__c | Group # | Number(4, 0) | No | — |
| Gym_Member__c | Gym Member | Checkbox | Yes | — |
| Happy_Anniversary__c | Happy Anniversary | Formula (Checkbox) | No | Checks if today is the staff's work anniversary. |
| Happy_Birthday__c | Happy Birthday | Formula (Checkbox) | No | Checks to see if today is staff's birthday. |
| Harassment_Prevention__c | Harassment Prevention | Text Area(255) | No | — |
| Headshot__c | Headshot | Checkbox | Yes | — |
| Hire_Date__c | Hire Date | Date | No | — |
| Home_Address__c | Home Address | Text Area(255) | No | — |
| Home_State__c | Home State | Picklist | No | — |
| Independent_Corp_Name__c | Independent Corp Name | Text(50) | No | — |
| IsAssistant__c | IsAssistant | Picklist | No | — |
| January_1st__c | January 1st | Formula (Checkbox) | No | Formula: `AND( DAY(TODAY()) = 1,MONTH(TODAY()) = 1)` |
| Job_Function__c | Job Function | Lookup(SFDC_Job_Function) | No | — |
| JPG__c | JPG | Text(20) | No | — |
| Last_Review_Date__c | Last Review Date | Date | No | — |
| Mail_Drop__c | Mail Drop | Text(10) | No | — |
| Marital_Status__c | Marital Status | Picklist | No | — |
| Med_Type__c | Med Type | Picklist | No | — |
| Medical_Benefits__c | Medical Benefits | Checkbox | Yes | — |
| Org__c | Org | Multi-Select Picklist | No | — |
| Paid_By_History__c | Paid By History | Text Area(4000) | No | — |
| Partnership_Dates__c | Partnership Dates | Text Area(255) | No | — |
| Payroll__c | Payroll | Picklist | No | — |
| Payroll_Account__c | Payroll Account | Picklist | No | — |
| Payroll_Notes__c | Payroll Notes | Text(100) | No | — |
| Payroll_Vendor__c | Payroll Vendor | Multi-Select Picklist | No | — |
| Personal_Email__c | Personal Email | Email | No | — |
| Personal_Info_Notes__c | Personal Info Notes | Text Area(255) | No | — |
| Personal_Phone__c | Personal Phone | Phone | No | — |
| Position_Date__c | Position Date | Date | No | — |
| Position_ID__c | Position ID | Number(6, 0) | No | — |
| Primary_Work_Email__c | Primary Work Email | Email | No | — |
| Primary_Work_Phone__c | Primary Work Phone | Phone | No | — |
| Profile_Verified__c | Profile Verified | Text(100) | No | — |
| PTO_Current__c | PTO Current | Number(5, 2) | No | — |
| PTO_Yearly_Addition__c | PTO Yearly Addition | Number(3, 0) | No | Number of hours added every New Year. |
| PTO_Yearly_Refresh__c | PTO Yearly Refresh | Number(3, 0) | No | Number of hours added every New Year. |
| Role__c | Role | Multi-Select Picklist | No | Placement in org hierarchy |
| Salary__c | Salary | Currency | No | — |
| Section_Sup__c | Section Sup | Number(5, 0) | No | — |
| Security_ID__c | Security ID | Text(20) | No | — |
| Service_Territory__c | Service Territory | Text Area(5000) | No | — |
| SF_User__c | SF User | Lookup(User) | No | — |
| Shirt_Size__c | Shirt Size | Picklist | No | — |
| Sick_Leave_Current__c | Sick Leave Current | Number(5, 2) | No | — |
| Sick_Leave_Yearly_Refresh__c | Sick Leave Yearly Refresh | Number(3, 0) | No | Number of Hours refreshed every New Year. |
| Special_Skills__c | Special Skills | Text Area(32000) | No | — |
| Start_Date__c | Start Date | Date | No | — |
| Stock_Options__c | Stock Options | Number(7, 0) | No | — |
| Stock_Value_Day_1__c | Stock Value (Day 1) | Currency | No | — |
| Supervisor__c | Supervisor | Lookup(SFDC_Staff) | No | — |
| Supervisor_Emp_ID__c | Supervisor Emp ID | Number(15, 0) | No | — |
| Supervisor_Name_Full__c | Supervisor Name (Full) | Text(80) | No | — |
| Termination_Date__c | Termination Date | Date | No | — |
| Title__c | Title | Text(70) | No | — |
| Total_Software_Costs__c | Total Software Costs | Currency | No | — |
| Total_Stock_Value__c | Total Stock Value | Formula (Currency) | No | Formula: `Stock_Value_Day_1__c * Stock_Options__c` |
| Type__c | Type | Multi-Select Picklist | No | — |
| Unit__c | Unit | Text(20) | No | — |
| User_ID__c | User ID | Text(10) | No | — |
| User_Name_Lookup__c | User Name | Lookup(User) | No | — |
| Website_Profile__c | Website Profile | Picklist | No | — |
| Work_Location__c | Work Location | Picklist | No | — |
| X401K__c | 401K | Checkbox | Yes | — |
| Yearly_Comp__c | Yearly Comp | Formula (Currency) | No | Formula: `Salary__c + Bonus_Potential__c + Total_Stock_Value__c` |


### Software__c  
_Label: Software_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Checkover__c | Checkover | Text(1300) | No | Formula: `if(and(not(isblank(Staff__r.Termination_Date__c )),TEXT(Status__c)="active"),"Check", if(and(not(...` |
| Corp_Name__c | Corp Name | Text(1300) | No | Sourced from Staff Corp Name field |
| Cost__c | Cost | Currency | No | — |
| Email__c | Email | Email | No | — |
| End_Date__c | End Date | Date | No | — |
| Hiya_Branded__c | Hiya Branded | Checkbox | Yes | — |
| License_Type__c | License Type | Picklist | No | — |
| Notes__c | Notes | Text Area(1000) | No | — |
| Phone_Number__c | Phone Number | Phone | No | xxx-xxx-xxxx |
| Previously_Assigned_To__c | Previously Assigned To | Lookup(SFDC_Staff) | No | — |
| Staff__c | Staff | Lookup(SFDC_Staff) | Yes | — |
| Start_Date__c | Start Date | Date | No | — |
| Status__c | Status | Picklist | No | — |
| Type__c | Type | Picklist | Yes | — |


### SubQuota__c  
_Label: Sub Quota_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Assigned__c | Assigned | Number(9, 0) | No | — |
| Attained__c | Attained | Number(16, 2) | No | — |
| CloseDate__c | Close Date | Date | No | Formula: `StartDate__c` |
| CurrentUserId__c | Current User Id | Text(20) | No | — |
| EndDate__c | End Date | Date | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| Month__c | Month | Picklist | Yes | — |
| PointsPending__c | Points Pending | Number(16, 2) | No | — |
| QuotaType__c | Quota Type | Picklist | No | — |
| StartDate__c | Start Date | Date | No | — |
| Status__c | Status | Picklist | No | — |
| TotalQuota__c | Total Quota | Lookup(TotalQuota) | Yes | — |
| TotalQuotaTerritory__c | Total Quota Territory | Lookup(TotalQuota) | No | — |
| UnattainedQuota__c | Unattained Quota | Formula (Number) | No | Formula: `Assigned__c - Attained__c` |


### TotalQuota__c  
_Label: Total Quota_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Allocation__c | Allocation | Picklist | Yes | — |
| EndDate__c | End Date | Date | No | — |
| FY__c | FY | Text(4) | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| Name__c | Name | Text(255) | No | — |
| OpportunityOwner__c | Opportunity Owner | Text(1300) | No | Formula: `Name__c` |
| OwnerIsActive__c | Owner Active | Formula (Checkbox) | No | Formula: `Owner:User.IsActive` |
| QuotaAssigned__c | Quota Assigned | Number(9, 0) | No | — |
| QuotaType__c | Quota Type | Picklist | No | — |
| StartDate__c | Start Date | Date | No | — |
| Status__c | Status | Picklist | No | — |
| User__c | User | Lookup(User) | No | — |


### Transaction__c  
_Label: Transaction_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Account__c | Account | Text(1300) | No | Formula: `IF( RecordTypeName__c ="Payment Out", Payee__r.Name&" "& TEXT( PayeeType__c ) ,IF(RecordTypeName_...` |
| Amount__c | Amount | Currency | No | — |
| Billable__c | Billable | Checkbox | Yes | — |
| BMCR_Confirmation_Number__c | BMCR Confirmation Number | Text(10) | No | — |
| BMCR_DateSubmitted__c | BMCR Date Submitted | Date | No | — |
| BMCR_DollarAmount__c | BMCR Dollar Amount | Currency | No | — |
| BMCR_Notes__c | BMCR Notes | Text(225) | No | — |
| BMCR_PointsEarned__c | BMCR Points Earned | Text(255) | No | — |
| BMCR_Status__c | BMCR Status | Picklist | No | — |
| BMCR_Submission_ID__c | BMCR Submission ID | Text(10) | No | — |
| Corporate_Name__c | Corporate Name | Text(1300) | No | Formula: `WorkOrder__r.Corporate_Name__c` |
| Created_Date_Time__c | Created Date Time | Formula (Date/Time) | No | Formula: `CreatedDate` |
| Date__c | Date | Date | No | — |
| Deposited__c | Deposited | Checkbox | Yes | — |
| Description__c | Description | Text(255) | No | — |
| IsAmexCharge__c | Amex Charge | Checkbox | Yes | — |
| LC_Amount_deprecate__c | LD Amount_deprecate | Formula (Currency) | No | Formula: `0` |
| LD_Access__c | LD Access | Text(1300) | No | Formula: `Payee__r.LD_Access__c` |
| LDAmount__c | LD Amount | Currency | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| Method__c | Method | Picklist | No | — |
| Opportunity__c | Opportunity | Lookup(Opportunity) | No | — |
| Paid_From_Stamp__c | Paid From Stamp | Text(255) | No | — |
| Partner_Stamp__c | Partner Stamp | Text(40) | No | — |
| Payee__c | Payee | Lookup(Account) | No | — |
| PayeeType__c | Payee Type | Picklist | No | — |
| PayoutApprovalStatus__c | Payout Approval Status | Picklist | No | — |
| PayrollNotes__c | Payroll Notes | Text(255) | No | — |
| PayrollPeriod__c | Payroll Period | Text(15) | No | — |
| PPP_Transfer_Date__c | PPP Transfer Date | Date | No | — |
| Reconciled__c | Reconciled | Checkbox | Yes | — |
| Record_Info__c | Record Info | Text(1300) | No | Formula: `RecordType.Name + " " + "-" + " " + "$" + TEXT(Amount__c)` |
| RecordTypeName__c | RecordType Name | Text(1300) | No | Formula: `RecordType.Name` |
| ReferenceId__c | Reference Id | Text(50) | No | — |
| Reimbursement__c | Reimbursement | Checkbox | Yes | — |
| Related_Work_Order_Name__c | Related Work Order Name | Text(1300) | No | Formula: `WorkOrder__r.Name__c` |
| RetailVendor__c | Retail Vendor | Lookup(Account) | No | — |
| Uploaded__c | Uploaded | Date | No | — |
| WorkOrder__c | Work Order | Lookup(WorkOrder) | Yes | — |
| Xero_Brand_Account__c | Xero Brand Account # | Text(1300) | No | Formula: `if(RecordTypeName__c="Payment In", "2803", "1404")` |
| Xero_Brand_Invoice__c | Xero Brand Invoice # | Text(1300) | No | Formula: `IF( Amount__c = 0, "Error - Zero Trans - " ,"") & Name & "-" & WorkOrder__r.Opportunity__r.Primar...` |
| Xero_ContactName__c | Xero Contact Name | Text(1300) | No | Formula: `if( RecordType.Name ="Payment Out", Payee__r.Name, if(Payee__r.Name="Aboffs","Aboffs", if(Payee__...` |
| Xero_Description__c | Xero Description | Text(1300) | No | Formula: `WorkOrder__r.Opportunity__r.AccountName__c&" -"& if( ISBLANK( PayrollNotes__c ), "",(" "&PayrollN...` |
| Xero_Due_Date__c | Xero Due Date | Date | No | Formula: `Date__c + 30` |
| Xero_Entered__c | Xero Entered | Checkbox | Yes | — |
| Xero_LD_Account__c | Xero LD Account # | Text(1300) | No | Formula: `"5401"` |
| Xero_LD_Bank_Account__c | Xero LD Bank Account | Text(1300) | No | Formula: `IF( contains(LD_Access__c, "LC " ), Case(LD_Access__c, "LC Expert", "Expert", "LC RJK", "RJK", "L...` |
| Xero_LD_Invoice__c | Xero LD Invoice # | Text(1300) | No | Formula: `IF( Amount__c = 0, "Error - Zero Trans - " ,"") & Xero_LD_Bank_Account__c & "-" & Name & "-" & RI...` |
| Xero_LD_Tracking_Name__c | Xero LD Tracking Name | Text(1300) | No | Formula: `"Bank Account"` |
| Xero_TP_Account__c | Xero TP Account # | Text(1300) | No | Formula: `if(RecordTypeName__c ="Payment In", "4000", if(IsAmexCharge__c = True,"5200", if( and(LC_Amount_d...` |
| Xero_TP_Feed_Date__c | Xero TP Feed Date | Date | No | Formula: `If(and(RecordTypeName__c ="Payment In",isnull(PPP_Transfer_Date__c)), Date__c-30, if(RecordTypeNa...` |
| Xero_TP_Invoice__c | Xero TP Invoice # | Text(1300) | No | Formula: `if(Amount__c =0,"Error - Zero Trans - ", if(AND( RecordTypeName__c ="Purchase",IsAmexCharge__c = ...` |
| Xero_Tracking_Name__c | Xero Tracking Name | Text(1300) | No | Formula: `"Tracking Name"` |
| XeroBillOrInv__c | Xero Bill or Inv | Text(1300) | No | Formula: `if(AND(IsAmexCharge__c = True,Amount__c >0),"PPP Bill", if(AND(IsAmexCharge__c = True,Amount__c <...` |


### Vehicle_Maintenance__c  
_Label: Vehicle Maintenance_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Cost__c | Cost | Currency | Yes | — |
| Date__c | Date | Date | Yes | — |
| Mileage__c | Mileage | Number(18, 0) | Yes | — |
| Repair_Notes__c | Repair Notes | Text Area(32768) | No | — |
| Type__c | Type | Picklist | Yes | — |
| Vehicle__c | Vehicle | Lookup(Vehicle) | Yes | — |


### Vehicle__c  
_Label: Vehicle_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Account__c | Account | Lookup(Account) | No | — |
| Agreement__c | Agreement | Date | No | — |
| Contact__c | Contact | Lookup(Contact) | No | — |
| DL_Expiration__c | DL Expiration | Date | No | — |
| Driver_Email__c | Driver Email | Email | No | — |
| Driver_Name__c | Driver Name | Text(36) | No | — |
| Driver_Notes__c | Driver Notes | Text Area(32768) | No | — |
| Driver_Relationship__c | Driver Relationship | Picklist | No | — |
| Inspection_Expiration__c | Inspection Expiration | Date | No | — |
| Insurance_Expiration__c | Insurance Expiration | Date | No | — |
| Insured_State__c | Insured State | Text(20) | No | — |
| Interim_Plate__c | Interim Plate | Text(18) | No | — |
| Last_Oil_Change__c | Last Oil Change | Date | No | — |
| Lien_Holder__c | Lien Holder | Text(50) | No | — |
| Lien_Release__c | Lien Release | Date | No | — |
| Make__c | Make | Text(18) | No | — |
| Mileage__c | Mileage | Number(18, 0) | No | — |
| Model__c | Model | Text(18) | No | — |
| Monthly_Payment__c | Monthly Payment | Currency | No | — |
| Monthly_Reimbursement__c | Monthly Reimbursement | Currency | No | — |
| Notes__c | Notes | Text Area(20000) | No | — |
| Operating_State__c | Operating State | Text(20) | No | — |
| Partner_Account__c | Partner Account | Lookup(Account) | No | — |
| Photo_Inspection__c | Photo Inspection | Date | No | — |
| Purchase_Date__c | Purchase Date | Date | No | — |
| Purchase_Notes__c | Purchase Notes | Text Area(32768) | No | — |
| Purchase_Price__c | Purchase Price | Currency | No | — |
| Refinanced__c | Refinanced | Text(200) | No | — |
| Registered_State__c | Registered State | Text(20) | No | — |
| Registration_Expiration__c | Registration Expiration | Date | No | — |
| Spare_Key__c | Spare Key | Picklist | No | — |
| Staff__c | Staff | Lookup(SFDC_Staff) | No | — |
| State__c | State | Text(3) | No | — |
| Status__c | Status | Picklist | No | — |
| Title__c | Title | Picklist | No | — |
| Title_Owner__c | Title Owner | Text(40) | No | — |
| Tracker__c | Tracker | Picklist | No | — |
| Tracker_ID__c | Tracker ID | Text(18) | No | — |
| Tracker_URL__c | Tracker URL | URL | No | — |
| Vehicle_Agreement__c | Vehicle Agreement | Picklist | No | — |
| Vehicle_Notes__c | Vehicle Notes | Text Area(32768) | No | — |
| VIN__c | VIN | Text(18) | No | — |
| Wrapped__c | Wrapped | Date | No | — |
| Year__c | Year | Text(4) | No | — |


### VoiceDirectPhone__c  
_Label: VoiceDirectPhone_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Name__c | ﻿Name | Text(255) | No | — |
| Number_type__c | Legacy Number type | Text(255) | No | — |
| OwnerId__c | OwnerId | Lookup(User) | No | Call will be routed to User: |
| Phone_Numbers__c | Phone Numbers: | Phone | No | Format +1XXXXXXXXXX |
| State__c | State | Text(255) | No | — |
| Voice_Call__c | Voice Call | Lookup(VoiceCall) | No | — |


### WorkOrderCrew__c  
_Label: Crew Attendance_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| ActualLaborDays__c | Labor Days | Number(2, 2) | No | — |
| Crew__c | Labor Crew | Lookup(Account) | Yes | — |
| Crew_Worker__c | Crew Worker | Picklist | No | — |
| CrewName__c | Crew Name | Text(1300) | No | Formula: `Crew__r.Name` |
| EndDate__c | End Date | Date | No | — |
| Hours_Worked__c | Hours Worked | Number(2, 1) | No | — |
| LaborDays__c | Labor Days deprecate | Number(2, 1) | No | — |
| LegacyId__c | LegacyId | Text(18) | No | — |
| LengthofDay__c | Length of Day | Picklist | No | — |
| LengthValue__c | Length Value | Formula (Number) | No | Formula: `IF(ISPICKVAL(LengthofDay__c , 'Full') , 1, 0.5)` |
| Notes__c | Notes | Text(255) | No | — |
| OtherName__c | Other Name | Text(30) | No | — |
| Paid__c | Paid | Checkbox | Yes | — |
| PaidAmount__c | Paid Amount | Number(6, 2) | No | — |
| Related_Opportunity__c | Related Opportunity | Text(1300) | No | Formula: `WorkOrder__r.Opportunity__r.Name` |
| ScheduledLaborDays__c | Labor Days (Scheduled) | Number(2, 1) | No | — |
| StartDate__c | Date | Date | No | — |
| WO_Owner__c | WO Owner | Text(1300) | No | Formula: `WorkOrder__r.Owner_Name__c` |
| WorkOrder__c | Work Order | Lookup(WorkOrder) | Yes | — |


### Zip_Analysis__c  
_Label: Zip Analysis_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| AverageIncome__c | AverageIncome | Currency | No | — |
| AvgHouseValue__c | AvgHouseValue | Currency | No | — |
| City__c | City | Text(30) | No | — |
| County__c | County | Text(30) | No | — |
| MonthlyLeadsProjection__c | MonthlyLeadsProjection | Number(4, 0) | No | — |
| MonthlyOppsProjection__c | MonthlyOppsProjection | Number(4, 0) | No | — |
| MultiFamilyHomes__c | MultiFamilyHomes | Number(10, 0) | No | — |
| SingleFamilyHomes__c | SingleFamilyHomes | Number(10, 0) | No | — |
| State__c | State | Text(2) | No | — |
| ZipCode__c | Zip Code | Text(5) | No | — |


### Zip_Code__c  
_Label: Zip Code_

| API Name | Label | Data Type | Required | Description |
|----------|-------|-----------|----------|-------------|
| Avg_Home_Value__c | Avg Home Value | Currency | No | — |
| Avg_Household_Income__c | Avg Household Income | Currency | No | — |
| City__c | City | Text(50) | No | — |
| County__c | County | Picklist | No | — |
| Marketing_Active__c | Marketing Active | Checkbox | Yes | — |
| Phone_Pricing_Only__c | Phone Pricing Only | Checkbox | Yes | — |
| Service_Territory__c | Service Territory | Lookup(ServiceTerritory) | No | — |
| Service_Territory_Active__c | Service Territory Active | Formula (Checkbox) | No | Formula: `Service_Territory__r.IsActive` |
| State__c | State | Picklist | No | — |
| Tax_Rate__c | Tax Rate | Percent | No | — |
| TimeZoneOffset__c | Time Zone Offset | Number(2, 0) | No | — |
| UseDaylightSavings__c | Use Daylight Savings | Checkbox | Yes | — |
| Zip_Code__c | Zip Code | Text(5) | Yes | — |
| Zip_Code_Grade__c | Zip Code Grade | Picklist | No | — |


---

## Automations — Flows

> 292 unmanaged flows: **252 active**, 40 inactive/draft/no active version. Grouped by `[PREFIX]` parsed from MasterLabel/DeveloperName.

### ACCOUNT — 13 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Account_AddTeamMembersFromServiceTerritory | — | AutoLaunchedFlow | ✅ Active | 7 | — |
| Account_AddTeamMembersFromServiceTerritory_PortalUser | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| Account_ChangeOwner | — | Flow | ✅ Active | 7 | — |
| Account_FieldCannotCreateServiceVendorValidation | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Account_ResetSystemUpdating | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Account_RetailVendorLastTransactionDate | — | AutoLaunchedFlow | ✅ Active | 5 | — |
| Account_ServiceVendorAlerttoFinance | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Account_ServiceVendorLastAttendance | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Account_ServiceVendorLastPaymentDate | — | AutoLaunchedFlow | ✅ Active | 4 | — |
| Account_SetOwnerAndServiceTerritory | — | AutoLaunchedFlow | ✅ Active | 16 | — |
| Account_Update_VC_Records_from_Lead | — | — | — | — | — |
| Account_UpdateContactOwnerOnOwnerChange | — | — | — | — | — |
| Account_UpdateOpportunityAddress | — | — | — | — | — |

### ADCOSTDETAIL — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| AdCostDetail_SetTitle | — | AutoLaunchedFlow | ✅ Active | 1 | — |

### ADDATTENDANCE — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| AddAttendance | Attendance.Add | Flow | ✅ Active | 12 | — |

### CASE — 9 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Case_AddCaseTeamMembers | — | AutoLaunchedFlow | ✅ Active | 11 | — |
| Case_EmailNotificationIfNotUpdatedWithinTwoWeeks | — | AutoLaunchedFlow | ✅ Active | 9 | — |
| Case_EscalationEmailToCustomerExperienceManager | — | AutoLaunchedFlow | ✅ Active | 7 | — |
| Case_SendEmail_CaseCreated | — | AutoLaunchedFlow | ✅ Active | 7 | — |
| Case_SendEmail_CommentAdded | — | AutoLaunchedFlow | ✅ Active | 6 | — |
| Case_SetDefaults | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| Case_UpdateAccountHasCase | — | — | — | — | — |
| Case_UpdateAccountHasCase_System | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Case_ValidationFieldUsersUnableToClose | — | AutoLaunchedFlow | ✅ Active | 1 | — |

### CASECOMMENT — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| CaseComment_SetCaseMostRecentCommentDate | — | AutoLaunchedFlow | ✅ Active | 3 | — |

### CHANGEORDER — 5 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| ChangeOrder_AllowOnlyAuthorizedUsers | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| ChangeOrder_Approval_UpdateLineItems | — | AutoLaunchedFlow | ✅ Active | 6 | — |
| ChangeOrder_Create | — | Flow | ✅ Active | 16 | — |
| ChangeOrder_RouteToApproval | — | AutoLaunchedFlow | ✅ Active | 11 | — |
| ChangeOrder_Update | — | Flow | ✅ Active | 5 | — |

### CHANGEORDERLINEITEM — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| ChangeOrderLineItem_SetWOLIChangeOrderRelatedTrue | — | AutoLaunchedFlow | ✅ Active | 1 | — |

### CONTACT — 3 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Contact_NewLead | — | Flow | ✅ Active | 1 | — |
| Contact_SetDefaults | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| Contact_SetOwnerIdToAccountOwnerId | — | AutoLaunchedFlow | ✅ Active | 2 | — |

### CORPORATEDOCUMENT — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| CorporateDocument_Expiration_Notification_Emails | — | AutoLaunchedFlow | ✅ Active | 6 | — |

### CPS — 10 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Cadence_Autolaunched_Flow_Update_Lead_Path_Test | [CPS] Cadence Autolaunched Flow: Update Lead | ActionCadenceAutolaunchedFlow | ✅ Active | 19 | Removed the Cadence Target Assignee update CPS flow |
| CPS_Account_Region_and_TimeZone_Flow | — | AutoLaunchedFlow | ✅ Active | 4 | — |
| CPS_Auto_approve_absence | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| CPS_Lead_Region_and_TimeZone_Flow | — | AutoLaunchedFlow | ✅ Active | 7 | — |
| CPS_New_Task_Creation_for_SMS | — | ActionCadenceAutolaunchedFlow | ✅ Active | 2 | — |
| CPS_Region_and_TimeZone_Flow | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| CPS_Set_Acc_and_Opp_Owner_to_Assigned_SR | — | — | — | — | — |
| CPS_Set_Acc_Owner_to_correct_Sales_Rep | — | — | — | — | — |
| CPS_Set_Appointment_Owners | — | — | — | — | — |
| CPS_User_Presence_Flow | — | AutoLaunchedFlow | ✅ Active | 79 | — |

### DAILY — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Daily_Lead_Wait1DayThenRouteToOmni | — | AutoLaunchedFlow | ✅ Active | 7 | — |

### DEMOFLOW — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| DemoFlow_DeepClone | — | — | — | — | — |

### EVENT — 14 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Event_DeletePublicEvent | Event.DeletePublicEvent | — | — | — | **DEPRECATED** This is managed by the ServiceAppointmentTriggerHandler and the EventServiceWithoutSharing class to av... |
| Event_CreateUpdateResourceAbsence | — | AutoLaunchedFlow | ✅ Active | 4 | — |
| Event_DeleteResourceAbsence | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| Event_ResourceAbsenceEventUpdates | — | — | — | — | — |
| Event_RestoreLocationFromResourceAbsence | — | — | — | — | — |
| Event_SetPublicEvent | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| Event_SetResourceAbsence | — | — | — | — | — |
| Event_SetSubject | — | — | — | — | — |
| Event_UpdatePublicFlag | — | — | — | — | — |
| Event_UpdateResourceAbsence | — | — | — | — | — |
| Event_UpdateServiceAppointment | — | — | — | — | — |
| Event_UpdateServiceAppointment_IsPublicFalse | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Event_UpdateServiceAppointment_IsPublicTrue | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Event_UpdateWorkOrderCrew | — | AutoLaunchedFlow | ✅ Active | 2 | — |

### EXPENSE — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Expense_UpdateContractorPaidOnOpp | — | AutoLaunchedFlow | ✅ Active | 1 | — |

### FIND — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Find_Lead_Associated_with_Messaging_Session | — | IndividualObjectLinkingFlow | ✅ Active | 8 | — |

### FLOWLIB — 42 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| FlowLib_AddToSet | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_AssignMultipleRecords | — | AutoLaunchedFlow | ✅ Active | 48 | — |
| FlowLib_AsSystem_SetPublicEvent | — | AutoLaunchedFlow | ✅ Active | 13 | — |
| FlowLib_BuildQuoteFromTemplate | — | Flow | ✅ Active | 5 | — |
| FlowLib_CancelServiceAppointments | — | Flow | ✅ Active | 8 | — |
| FlowLib_ChangeOrder_GetApprovalThresholds | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| FlowLib_ChangeOrder_IsOverThreshold | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| FlowLib_ContentDocumentLinks_Clone | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_CreateOrUpdateAssignedResource | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| FlowLib_CreateQuotaPoints | — | AutoLaunchedFlow | ✅ Active | 7 | — |
| FlowLib_EditPaymentTerms | — | Flow | ✅ Active | 17 | — |
| FlowLib_GetActiveEmailTemplateByName | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| FlowLib_GetRecordTypeId | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_GetServiceTerritoryByZipCode | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| FlowLib_GetServiceTerritoryForOpportunity | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| FlowLib_GetStateAbbreviation | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_GetSystemSettings | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_GetWorkTypeIdByOpportunityInquiryServiceType | — | AutoLaunchedFlow | ✅ Active | 5 | — |
| FlowLib_IsZipCodeConfigured | — | Flow | ✅ Active | 3 | — |
| FlowLib_IsZipCodeConfigured_Autolaunched | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_LogEmail | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_ManualServiceAppointment | — | Flow | ✅ Active | 11 | — |
| FlowLib_Opportunity_AddTeamMembersFromServiceTerritory | — | AutoLaunchedFlow | ✅ Active | 16 | — |
| FlowLib_Opportunity_AddTeamMembersFromServiceTerritory_Bulk | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| FlowLib_OpportunityClone | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_PaymentTerms_Clone | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_ProductSelection | — | Flow | ✅ Active | 14 | — |
| FlowLib_ProductSelection_Tomco | — | Flow | ✅ Active | 1 | — |
| FlowLib_QuoteClone | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_QuoteLineItems_Clone | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_ReassignAccount | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| FlowLib_ReassignEvents | — | AutoLaunchedFlow | ✅ Active | 4 | — |
| FlowLib_ReassignOpportunities | — | AutoLaunchedFlow | ✅ Active | 6 | — |
| FlowLib_ReassignServiceAppointments | — | AutoLaunchedFlow | ✅ Active | 5 | — |
| FlowLib_ReassignServiceResources | — | AutoLaunchedFlow | ✅ Active | 4 | — |
| FlowLib_ReassignWorkOrders | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| FlowLib_RestoreServiceTerritoryMember | — | AutoLaunchedFlow | ✅ Active | 4 | — |
| FlowLib_SelectLeadRecordType | — | Flow | ✅ Active | 1 | — |
| FlowLib_SetAssignedResource | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| FlowLib_SetServiceTerritoryMemberActive | — | AutoLaunchedFlow | ✅ Active | 25 | — |
| FlowLib_Testing | — | — | — | — | — |
| FlowLib_WorkOrderCrew_BuildEventSubject | — | AutoLaunchedFlow | ✅ Active | 1 | — |

### FSSK — 2 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| FSSK_Clone_Assigned_Resource | — | Workflow | ✅ Active | 3 | — |
| FSSK_CLONE_Status_Transition | — | FieldServiceMobile | ✅ Active | 1 | — |

### LEAD — 27 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| TEST_Wait_Flow | [LEAD] Auto Routing CA Waiting Time- Part 1 | AutoLaunchedFlow | ✅ Active | 15 | Auto launched Wait Flow for CA Leads |
| LEAD_Auto_Assigment | [LEAD] Auto Routing Record Trigger - Main Trigger | AutoLaunchedFlow | ✅ Active | 39 | Triggered on Lead Creation |
| LEAD_Outbound_Auto_Assignment_Flow | [LEAD] Outbound Manual Assignment Flow | Flow | ✅ Active | 13 | v2.2.1 - Screen Component and Cadence Selection, Cadence Id pasted to another Subflow |
| Lead_ConvertCustom_beta | Lead.ConvertCustom_beta | — | — | — | — |
| Lead_AdCostDetailUpdate | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Lead_AgentFieldAutoUpdate | — | AutoLaunchedFlow | ✅ Active | 9 | — |
| Lead_Company_Name | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Lead_ConvertCustom | — | Flow | ✅ Active | 17 | — |
| Lead_ConvertLead | — | — | — | — | — |
| Lead_Count_Voice_Calls | — | AutoLaunchedFlow | ✅ Active | 13 | — |
| LEAD_NEW_CA_Routing | — | RoutingFlow | ✅ Active | 4 | — |
| LEAD_New_Omni_Routing | — | RoutingFlow | ✅ Active | 12 | — |
| Lead_NewLead | — | Flow | ✅ Active | 20 | — |
| Lead_NotifyMetaLeadCreated | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Lead_Offline_Reassignment | — | — | — | — | — |
| LEAD_Phone_Formatting_Trigger | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| LEAD_Rout_back_to_Queue_Admin_User | — | AutoLaunchedFlow | ✅ Active | 19 | — |
| LEAD_Scheduled_Routing_flow | — | AutoLaunchedFlow | ✅ Active | 11 | — |
| Lead_ServiceTerritoryInactiveWarning | — | Flow | ✅ Active | 1 | — |
| Lead_SetAdCostDetail | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Lead_SetCalculatedValues | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| Lead_SetLeadAgeGroup | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Lead_SetServiceTerritory | — | AutoLaunchedFlow | ✅ Active | 4 | — |
| Lead_Unqualify | — | Flow | ✅ Active | 1 | — |
| LEAD_Update_Cadence_Assignee | — | AutoLaunchedFlow | ✅ Active | 23 | — |
| LEAD_Update_Owner_for_Unqualified_Lead | — | — | — | — | — |
| Lead_UpdatePavingTrue | — | AutoLaunchedFlow | ✅ Active | 1 | — |

### OFFLINE — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Offline_Change_Owner | — | Flow | ✅ Active | 12 | — |

### OPPORTUNITY — 28 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Opportunity_SetServiceTerritoryAndOwner | Opportunity:SetServiceTerritoryAndOwner | AutoLaunchedFlow | ✅ Active | 50 | Set values based on the Service Territory, via Zip Code. Set on After Save because of how the Estimation Address is s... |
| Opportunity_AdCostDetailUpdate | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Opportunity_AddTeamMembersFromServiceTerritory_Create | — | AutoLaunchedFlow | ✅ Active | 5 | — |
| Opportunity_AddTeamMembersFromServiceTerritory_update | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| Opportunity_CancelServiceAppointments | — | Flow | ✅ Active | 1 | — |
| Opportunity_ChangeOwnerOnWOandSA_temp | — | — | — | — | — |
| Opportunity_CorporateNameAssignmentFromOwner | — | AutoLaunchedFlow | ✅ Active | 5 | — |
| Opportunity_CreateQuotaPointsForServiceTerritory | — | — | — | — | — |
| Opportunity_DeleteQuotaPoints | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| Opportunity_Hatch_Campaign_Initial_Trigger | — | AutoLaunchedFlow | ✅ Active | 32 | — |
| Opportunity_OnClosedLostSetNeedsRescheduleFalse | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Opportunity_OutsideofST_Experience_Site | — | — | — | — | — |
| Opportunity_PrimaryContactEmailMissing | — | Flow | ✅ Active | 2 | — |
| Opportunity_Quota_Points_Record_Creation | — | AutoLaunchedFlow | ✅ Active | 10 | — |
| Opportunity_ResetSystemUpdating | — | — | — | — | — |
| Opportunity_SetAccountTypeOnClosedWon | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Opportunity_SetAdCostDetail | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Opportunity_SetCloseDateOnClosedWon | — | AutoLaunchedFlow | ✅ Active | 4 | — |
| Opportunity_SetDefaults | — | AutoLaunchedFlow | ✅ Active | 7 | — |
| Opportunity_SetPrimaryContact | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Opportunity_SetServiceTerritoryAndOwner_PortalUser | — | AutoLaunchedFlow | ✅ Active | 9 | — |
| Opportunity_SetStageWhenQuoteSync | — | AutoLaunchedFlow | ✅ Active | 7 | — |
| Opportunity_SubQuotaSubFlow | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| Opportunity_SyncTeamMembersFromFields | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| Opportunity_TotalQuotaPointCheckSubFlow | — | AutoLaunchedFlow | ✅ Active | 4 | — |
| Opportunity_UpdateStageToEstimateSentWhenDateEstimateIsPopulated | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| Opportunity_WorkOrderWhenClosedWon | — | AutoLaunchedFlow | ✅ Active | 31 | — |
| Opportunity_WorkTypeSetDefault | — | AutoLaunchedFlow | ✅ Active | 7 | — |

### OPPORTUNITYLINEITEM — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| OpportunityLineItem_SetTotalPriceFromQuoteLineItem | — | AutoLaunchedFlow | ✅ Active | 1 | — |

### PAYMENTTERM — 2 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| PaymentTerm_SetAmountByPercent | — | AutoLaunchedFlow | ✅ Active | 17 | — |
| PaymentTerm_SetOwnerAsWorkOrderOrQuoteOwner | — | AutoLaunchedFlow | ✅ Active | 4 | — |

### POLICY — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Policy_Document_Expiration_Notification_Emails | — | AutoLaunchedFlow | ✅ Active | 7 | — |

### POLICYDOCUMENT — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| PolicyDocument_UpdateCorpDocComplianceStatus | PolicyDocument:UpdateRelatedCorpDoc | AutoLaunchedFlow | ✅ Active | 8 | — |

### QUOTE — 15 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Quote_CalculateTax | — | AutoLaunchedFlow | ✅ Active | 16 | — |
| Quote_CloneQuote | — | Flow | ✅ Active | 3 | — |
| Quote_CloneQuoteToOtherAccount | — | Flow | ✅ Active | 1 | — |
| Quote_CommunityPageWarnings | — | Flow | ✅ Active | 1 | — |
| Quote_CreateNewOrUseTemplate | — | Flow | ✅ Active | 5 | — |
| Quote_Default | — | Flow | ✅ Active | 10 | — |
| Quote_EditPaymentTerms | — | Flow | ✅ Active | 2 | — |
| Quote_ErrorWhenOpportunityLost | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| Quote_OpportunityPrimaryContactMissingEmail | — | Flow | ✅ Active | 1 | — |
| Quote_SetOpportunityStageClosedWonOnApproved | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Quote_SetOwnerToOpportunityOwner | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Quote_SetRecordType_Tomco | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Quote_UpdateContactEmail | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Quote_UpdateOppDateContractSent | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| Quote_UpdateOpptyQuoteFields | — | AutoLaunchedFlow | ✅ Active | 4 | — |

### QUOTECREATENEW — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| QuoteCreateNew | — | Flow | ✅ Active | 28 | — |

### QUOTELINEITEM — 5 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| QuoteLineItem_Default | — | AutoLaunchedFlow | ✅ Active | 11 | — |
| QuoteLineItem_NewRecord | — | Flow | ✅ Active | 12 | — |
| QuoteLineItem_NewRecordNoSave | — | Flow | ✅ Active | 28 | — |
| QuoteLineItem_SetDefaults | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| QuoteLineItem_SetValueOnOpportunityProduct | — | AutoLaunchedFlow | ✅ Active | 2 | — |

### RESOURCEABSENCE — 3 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| ResourceAbsence_CreateUpdateEvent | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| ResourceAbsence_DeleteWhenEventDeleted | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| ResourceAbsence_UpdateEventLocation | — | — | — | — | — |

### SCVCB — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| SCVCB_Voice_Actions | — | — | — | — | — |

### SDOCRELATIONSHIP — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| SDocRelationship_QuoteEmailed | — | AutoLaunchedFlow | ✅ Active | 1 | — |

### SEND — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Send_Case_Update_Notification_to_Case_Team | — | AutoLaunchedFlow | ✅ Active | 2 | — |

### SERVICEAPPOINTMENT — 16 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| ServiceAppointment_24hrReminder | — | AutoLaunchedFlow | ✅ Active | 10 | — |
| ServiceAppointment_AfterCancelOrCannotComplete | — | AutoLaunchedFlow | ✅ Active | 6 | — |
| ServiceAppointment_BeforeSave_SetContactFields | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| ServiceAppointment_Booked_Email_Notification | — | AutoLaunchedFlow | ✅ Active | 20 | — |
| ServiceAppointment_CalendarEvent | — | AutoLaunchedFlow | ✅ Active | 20 | — |
| ServiceAppointment_CancelledSetOpportunityNeedsReschedule | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| ServiceAppointment_OwnerChange_ReassignEvents | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| ServiceAppointment_PhoneAppt_SetIsOffsiteTrue | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| ServiceAppointment_ReassignResource | — | Flow | ✅ Active | 2 | — |
| ServiceAppointment_SetAssignedResourceOnServiceResourceChange | — | — | — | — | — |
| ServiceAppointment_SetCustomerLocalStartTime | — | AutoLaunchedFlow | ✅ Active | 8 | — |
| ServiceAppointment_SetDefaults | — | AutoLaunchedFlow | ✅ Active | 6 | — |
| ServiceAppointment_SetLookupOnWorkOrder | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| ServiceAppointment_SetOpportunityAppointmentDate | — | AutoLaunchedFlow | ✅ Active | 5 | — |
| ServiceAppointment_SetOpportunityNeedsRescheduleFalse | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| ServiceAppointment_UseArrivalTimesOverScheduledTimes | — | AutoLaunchedFlow | ✅ Active | 9 | — |

### SMS — 6 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| CPS_Account_Manager_Messages_Routed_to_Agents_and_Queues | [SMS]  Messages Routed to Lead Owners Agents or  Queues | RoutingFlow | ✅ Active | 14 | Route SMS Directly to Agent - Lead owner, who initiated it. |
| CC_Messages_Routed_to_Agents_and_Queues | [SMS] Messages Routed to Account Managers and Queues | RoutingFlow | ✅ Active | 16 | Routes each message to an Account Manager or queue based on conditions. v2 |
| CPS_Task_create_for_SMS | [SMS] Task create for SMS | AutoLaunchedFlow | ✅ Active | 1 | Create a Task to Send SMS on Lead Record. Used in Sales Engagement Lead Cadence. |
| SMS_Create_Messaging_User_For_Lead | — | Flow | ✅ Active | 28 | — |
| SMS_Link_LeadId_with_Messaging_Session | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| SMS_Screen_for_Lead_Search | — | Flow | ✅ Active | 4 | — |

### SOFTWARE — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Software_Cost | — | AutoLaunchedFlow | ✅ Active | 9 | — |

### SSIGNENVELOPE — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| SSignEnvelope_UpdateQuoteOnSent | — | AutoLaunchedFlow | ✅ Active | 2 | — |

### STAFF — 6 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Staff_Daily_Automations | Staff Daily Automations | — | — | — | A scheduled flow that executes happy birth & anniversary reminders and PTO refreshes on Jan 1st each year. |
| Staff_PTO_Request_Created | Staff PTO Request Created | AutoLaunchedFlow | ✅ Active | 3 | Subtract requested time off against prior accrued. |
| Staff_Fast_Field_Updates | — | — | — | — | — |
| Staff_PTO_Request_Deleted | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Staff_PTO_Request_Updated | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Staff_Record_Creation | — | — | — | — | — |

### SUBFLOW — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| SubFlow_Wait1DayThenRouteOmni | — | — | — | — | — |

### TEST — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Test_Convert_Lead | — | Flow | ✅ Active | 14 | — |

### TRANSACTION — 16 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Transaction_DisallowIfWorkOrderIsEstimate | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Transaction_DisallowUpdateIfXeroEntered | — | AutoLaunchedFlow | ✅ Active | 9 | — |
| Transaction_EnforceValidVendor | — | AutoLaunchedFlow | ✅ Active | 4 | — |
| Transaction_LDAmountPopulateforPayee | — | AutoLaunchedFlow | ✅ Active | 11 | — |
| Transaction_NewRecord | — | Flow | ✅ Active | 29 | — |
| Transaction_PaymentOut_AutoSubmitForApproval | — | AutoLaunchedFlow | ✅ Active | 4 | — |
| Transaction_SetOpportunity | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Transaction_SetOwnerAndOpportunity | — | — | — | — | — |
| Transaction_SetPaidFromStamp | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| Transaction_TotalsToWorkOrder_PaymentIn | — | AutoLaunchedFlow | ✅ Active | 11 | — |
| Transaction_TotalsToWorkOrder_PaymentIn_Delete | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| Transaction_TotalsToWorkOrder_PaymentOut | — | AutoLaunchedFlow | ✅ Active | 20 | — |
| Transaction_TotalsToWorkOrder_PaymentOut_Delete | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| Transaction_TotalsToWorkOrder_Purchase | — | AutoLaunchedFlow | ✅ Active | 15 | — |
| Transaction_TotalsToWorkOrder_Purchase_Delete | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| Transaction_UpdateStatusDateSubmittedwithSubmissionID | — | AutoLaunchedFlow | ✅ Active | 1 | — |

### USER — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| User_Creation_Automations | — | — | — | — | — |

### VEHICLE — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Vehicle_Maint_Update_Mileage_Last_Oil_Change | — | AutoLaunchedFlow | ✅ Active | 4 | — |

### VOICE — 9 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| CPS_Associate_Contact_and_Lead_with_Voice | [VOICE] Associate Contact and Lead with Voice | Flow | ✅ Active | 97 | v17.9 Version with contact and account Only. Create Lead - remove the update for vc lookup on lead |
| CPS_Assign_Five_Leads_To_Cadence | [VOICE] Outbound:  Assign Five Leads To Cadence | Flow | ✅ Active | 5 | — |
| PPP_Voice_Call_Routing_to_Agents_and_Queues | [VOICE] PPP Voice Call Routing to Agents and Queues | RoutingFlow | ✅ Active | 26 | Routes each call to an agent or queue based on conditions you define. v2 Updated Flow to fix the Flow Exceptions to r... |
| CPS_Voice_Mail_Owner_Assignment | [VOICE] Voice Mail Owner Assignment | AutoLaunchedFlow | ✅ Active | 1 | This flow is used to assign the voice mails to the respective owner |
| VOICE_AM_Routing_Direct | — | RoutingFlow | ✅ Active | 1 | — |
| VOICE_AM_Voicemail | — | AutoLaunchedFlow | ✅ Active | 6 | — |
| VOICE_AM_Voicemail_Notification | — | AutoLaunchedFlow | ✅ Active | 6 | — |
| VOICE_Direct_Account_Manager_Routing | — | RoutingFlow | ✅ Active | 1 | — |
| VOICE_VoiceMail_Drop_Selection | — | Flow | ✅ Active | 6 | — |

### WINTER — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| Winter_Promo_Form_Designation | — | AutoLaunchedFlow | ✅ Active | 15 | — |

### WORKORDER — 26 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| WorkOrder_AutomateStatus | WorkOrder.AutomateStatus | — | — | — | DEPRECATED in favor of WorkOrderStatusAutomation apex class |
| WorkOrder_SetOpportunityFinancialFields | WorkOrder.SetOpportunityFinancialFields | AutoLaunchedFlow | ✅ Active | 1 | — |
| WorkOrder_AddUpTransactions | — | AutoLaunchedFlow | ✅ Active | 8 | — |
| WorkOrder_AssignCrew | — | Flow | ✅ Active | 2 | — |
| WorkOrder_CalculateTax | — | AutoLaunchedFlow | ✅ Active | 18 | — |
| WorkOrder_CancelServiceAppointments | — | Flow | ✅ Active | 1 | — |
| WorkOrder_ClosedCalculateSalesCommission | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| WorkOrder_ClosedUpdateOppWOClosed | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| WorkOrder_DisallowEditWhenClosed | — | AutoLaunchedFlow | ✅ Active | 8 | — |
| WorkOrder_EditPaymentTerms | — | Flow | ✅ Active | 3 | — |
| WorkOrder_EnforceValidVendor | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| WorkOrder_FinalBalanceDueDate | — | AutoLaunchedFlow | ✅ Active | 6 | — |
| WorkOrder_OwnerChange_ReassignChildren | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| WorkOrder_QuestionnaireScreenFlow | — | Flow | ✅ Active | 8 | — |
| WorkOrder_QuotaPointsValueUpdate | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| WorkOrder_SendLetsGetStartedEmail | — | AutoLaunchedFlow | ✅ Active | 23 | — |
| WorkOrder_SetAccountLastWorkOrderCompletedDate | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| WorkOrder_SetContactId | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| WorkOrder_SetCoordinationCompleteDate | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| WorkOrder_SetDefaults | — | AutoLaunchedFlow | ✅ Active | 6 | — |
| WorkOrder_SetOpportunityTotalAmount | — | AutoLaunchedFlow | ✅ Active | 11 | — |
| WorkOrder_SetOwnerToOpportunityOwner | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| WorkOrder_SetQuotaPointsAttainedWhenClosed | — | AutoLaunchedFlow | ✅ Active | 2 | — |
| WorkOrder_SetStatus | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| WorkOrder_UpdatePaymentTermsAmountByPercent | — | — | — | — | — |
| WorkOrder_UpdateTotalsAndOpportunityTotal | — | — | — | — | — |

### WORKORDERCREW — 4 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| WorkOrderCrew_Attendance_DisallowIfWorkOrderIsEstimate | — | — | — | — | — |
| WorkOrderCrew_EnforceValidVendor | — | AutoLaunchedFlow | ✅ Active | 1 | — |
| WorkOrderCrew_SetWorkOrderStartDate | — | AutoLaunchedFlow | ✅ Active | 3 | — |
| WorkOrderCrew_UpdateEvent | — | AutoLaunchedFlow | ✅ Active | 2 | — |

### WORKORDERLINEITEM — 4 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| WorkOrderLineItem_Default | — | AutoLaunchedFlow | ✅ Active | 7 | — |
| WorkOrderLineItem_NewRecord | — | Flow | ✅ Active | 13 | — |
| WorkOrderLineItem_NewRecordNoSave | — | Flow | ✅ Active | 30 | — |
| WorkOrderLineItem_SetDefaults | — | AutoLaunchedFlow | ✅ Active | 2 | — |

### WORKSTEP — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| WorkStep_StatusNew | — | — | — | — | — |

### Z — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| z_test | — | — | — | — | — |

### ZIPCODE — 1 flow(s)

| Flow (DeveloperName) | Label | Process Type | Status | Version | Description |
|----------------------|-------|--------------|--------|---------|-------------|
| ZipCode_NameMustMatchValue | — | AutoLaunchedFlow | ✅ Active | 1 | — |

---

## Apex Triggers

> 21 unmanaged Apex Triggers.

| Trigger | Object | Status | API Ver | Events |
|---------|--------|--------|---------|--------|
| AccountTrigger | Account | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| CaseTrigger | Case | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| ChangeOrderTrigger | ChangeOrder__c | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| ContactTrigger | Contact | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| ContentDocumentLinkTrigger | ContentDocumentLink | Active | 58 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| EventTrigger | Event | Active | 58 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| LeadTrigger | Lead | Active | 58 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| OpportunityTrigger | Opportunity | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| PaymentTermTrigger | Payment_Term__c | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| QuoteLineItemTrigger | QuoteLineItem | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| QuoteTrigger | Quote | Active | 58 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| SDocTrigger | SDOC__SDoc__c | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| ServiceAppointmentTrigger | ServiceAppointment | Active | 58 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| SSignEnvelopeTrigger | SSign__SSEnvelope__c | Active | 58 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| SubQuotaTrigger | SubQuota__c | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| TotalQuotaTrigger | TotalQuota__c | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| TransactionTrigger | Transaction__c | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| WorkOrderCrewTrigger | WorkOrderCrew__c | Active | 58 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| WorkOrderLineItemTrigger | WorkOrderLineItem | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| WorkOrderTrigger | WorkOrder | Active | 58 | before insert, before update, before delete, after insert, after update, after delete, after undelete |
| WorkPlanTrigger | WorkPlan | Active | 59 | before insert, before update, before delete, after insert, after update, after delete, after undelete |

---

## Apex Classes

> 209 unmanaged Apex Classes (counts shown below; see source for implementation).

- **Non-test classes:** 127
- **Test classes:** 82

<details><summary>Full list (alphabetical)</summary>

| Class | Status | API Ver | Lines (no comments) |
|-------|--------|---------|---------------------|
| AddOrInsertRecord | Active | 48 | 1406 |
| AddressService | Active | 58 | 2277 |
| AddressServiceTest | Active | 58 | 3336 |
| AnyEventCalCtrl | Active | 39 | 6160 |
| AnyEventCalCtrlTest | Active | 39 | 1347 |
| AssertionIterators | Active | 48 | 13554 |
| AWSConnectHandler | Active | 59 | 411 |
| AWSConnectHandlerTest | Active | 59 | 1565 |
| Batch_UpdatingLeadOwner | Active | 58 | 5589 |
| Batch_UpdatingLeadOwner_Test | Active | 58 | 979 |
| CaseService | Active | 59 | 2493 |
| CaseServiceTest | Active | 59 | 11391 |
| CaseTriggerHandler | Active | 60 | 474 |
| ChangePasswordController | Active | 50 | 376 |
| ChangePasswordControllerTest | Active | 50 | 480 |
| CollectionCalculate | Active | 51 | 4458 |
| CollectionProcessorsUtils | Active | 49 | 2871 |
| CollectionService | Active | 59 | 703 |
| CollectionServiceTest | Active | 59 | 2721 |
| CommunitiesLandingController | Active | 57 | 203 |
| CommunitiesLandingControllerTest | Active | 57 | 502 |
| CommunitiesLoginController | Active | 57 | 393 |
| CommunitiesLoginControllerTest | Active | 57 | 320 |
| CommunitiesSelfRegConfirmController | Active | 57 | 118 |
| CommunitiesSelfRegConfirmControllerTest | Active | 57 | 282 |
| CommunitiesSelfRegController | Active | 57 | 2269 |
| CommunitiesSelfRegControllerTest | Active | 57 | 647 |
| ContactService | Active | 61 | 2283 |
| ContactServiceTest | Active | 61 | 8327 |
| ContactTriggerHandler | Active | 61 | 371 |
| ContactTriggerHandlerTest | Active | 61 | 3570 |
| ContentDocumentLinkService | Active | 58 | 5355 |
| ContentDocumentLinkServiceTest | Active | 58 | 7533 |
| ContentDocumentLinkTriggerHandler | Active | 58 | 474 |
| CopyCollection | Active | 48 | 938 |
| CountRecordsAndFields | Active | 48 | 1675 |
| CPS_Acc_PhoneNumbers | Active | 56 | 2686 |
| CPS_Con_PhoneNumbers | Active | 56 | 3629 |
| CPS_Lead_PhoneNumbers | Active | 56 | 1764 |
| CPS_PhoneNumbers_Test | Active | 56 | 2078 |
| CreatedDateService | Active | 59 | 780 |
| CreatedDateServiceTest | Active | 59 | 4568 |
| DedupeRecordCollection | Active | 49 | 1541 |
| DeepClone | Active | 48 | 5469 |
| EmailService | Active | 59 | 2704 |
| EmailServiceTest | Active | 59 | 1184 |
| ErrorLogService | Active | 62 | 561 |
| ErrorLogServiceTest | Active | 62 | 2954 |
| EvaluateFormula | Active | 48 | 1213 |
| EventService | Active | 58 | 2507 |
| EventServiceTest | Active | 58 | 9473 |
| EventServiceWithoutSharing | Active | 59 | 843 |
| EventServiceWithoutSharingTest | Active | 59 | 2743 |
| EventTriggerHandler | Active | 58 | 582 |
| ExecuteSOQL | Active | 55 | 9994 |
| ExecuteSOQLTest | Active | 47 | 9639 |
| ExportService | Active | 59 | 7454 |
| ExportServiceTest | Active | 59 | 1548 |
| ExtractStringsFromCollection | Active | 48 | 2725 |
| ExtractStringsFromCollectionTest | Active | 48 | 4047 |
| FieldPickerController | Active | 46 | 5855 |
| FieldPickerControllerTest | Active | 48 | 355 |
| FilterByCollection | Active | 48 | 2056 |
| FilterCollection | Active | 48 | 1742 |
| FindCommonAndUniqueRecords | Active | 50 | 7745 |
| FindCommonAndUniqueRecordsTest | Active | 50 | 5609 |
| FindRecordsInCollection | Active | 48 | 2382 |
| FlowLibCommit | Active | 59 | 834 |
| FlowLibCommitTest | Active | 59 | 539 |
| FlowLibGetStateAbbreviation | Active | 58 | 954 |
| FlowLibGetStateAbbreviationTest | Active | 58 | 2290 |
| FlowLibGetStateAbbrevTest | Active | 58 | 5869 |
| FlowLibGetUserLocalDateTime | Active | 58 | 1243 |
| FlowLibGetUserLocalDateTimeTest | Active | 58 | 1876 |
| FlowLibWOLIGetRecordTypeTest | Active | 57 | 1496 |
| FlowLibWorkOrderLineItemGetRecordType | Active | 58 | 857 |
| FlowService | Active | 58 | 452 |
| FlowServiceTest | Active | 58 | 1813 |
| ForgotPasswordController | Active | 50 | 379 |
| ForgotPasswordControllerTest | Active | 50 | 346 |
| GenerateCollectionReport | Active | 48 | 13005 |
| GetChildCollection | Active | 48 | 3519 |
| GetFirst | Active | 48 | 937 |
| GetFirstTest | Active | 48 | 103 |
| GetLookupCollection | Active | 48 | 3789 |
| GetRecordsFromIds | Active | 51 | 2077 |
| GetRecordsFromIdsTest | Active | 51 | 788 |
| ImportService | Active | 59 | 13527 |
| ImportServiceTest | Active | 59 | 11228 |
| JoinCollections | Active | 48 | 1178 |
| LeadIncomingALEndpoint | Active | 56 | 616 |
| LeadIncomingALEndpointTest | Active | 56 | 1661 |
| LeadIncomingALRequest | Active | 56 | 930 |
| LeadIncomingHAEndpoint | Active | 58 | 499 |
| LeadIncomingHAEndpointTest | Active | 58 | 806 |
| LeadIncomingHARequest | Active | 58 | 1249 |
| LeadIncomingMetaEndpoint | Active | 66 | 10135 |
| LeadIncomingMetaEndpointTest | Active | 56 | 9428 |
| LeadIncomingProcessor | Active | 56 | 13337 |
| LeadIncomingProcessorTest | Active | 56 | 7215 |
| LeadIncomingWCEndpoint | Active | 56 | 626 |
| LeadIncomingWCEndpointTest | Active | 56 | 810 |
| LeadIncomingWCRequest | Active | 56 | 2794 |
| LeadReassignmentBatch | Active | 60 | 928 |
| LeadReassignmentBatchTest | Active | 60 | 1891 |
| LeadReassignmentController | Active | 60 | 2404 |
| LeadReassignmentControllerTest | Active | 60 | 7250 |
| LeadService | Active | 58 | 4023 |
| LeadServiceTerritoryInactiveController | Active | 60 | 516 |
| LeadServiceTerritoryInactiveCtlrTest | Active | 61 | 4780 |
| LeadServiceTest | Active | 58 | 11744 |
| LeadTriggerHandler | Active | 58 | 746 |
| LeadTriggerHandlerTest | Active | 58 | 5413 |
| LeadWorkingHoursVFExtension | Active | 58 | 398 |
| LeadWorkingHoursVFExtensionTest | Active | 59 | 906 |
| ListActionsTest | Active | 48 | 22856 |
| MapCollection | Active | 48 | 4251 |
| MetaRegister | Active | 55 | 4061 |
| MetaRegisterTest | Active | 59 | 1892 |
| MicrobatchSelfRegController | Active | 57 | 1779 |
| MicrobatchSelfRegControllerTest | Active | 57 | 496 |
| MigratedRecordService | Active | 58 | 623 |
| MigratedRecordServiceTest | Active | 59 | 18601 |
| MigratedRecordTriggerHandler | Active | 59 | 230 |
| MockHttpResponseGenerator | Active | 59 | 1207 |
| MyCalendarButtonsPicklist | Active | 39 | 1272 |
| MyProfilePageController | Active | 50 | 1403 |
| MyProfilePageControllerTest | Active | 50 | 2507 |
| OpportunityService | Active | 60 | 1032 |
| OpportunityServiceTest | Active | 60 | 7996 |
| OpportunitySyncQuote | Active | 59 | 2825 |
| OpportunitySyncQuoteQueueable | Active | 59 | 412 |
| OpportunitySyncQuoteTest | Active | 59 | 7054 |
| OpportunityTriggerHandler | Active | 59 | 527 |
| OppOwnerServiceTerritoryEstimator_Test | Active | 57 | 2283 |
| OptOutHatchEndpoint | Active | 60 | 544 |
| OptOutHatchEndpointTest | Active | 61 | 1345 |
| OptOutHatchPayload | Active | 61 | 1172 |
| OptOutHatchPayloadTest | Active | 61 | 1448 |
| OptOutService | Active | 61 | 1171 |
| OptOutServiceTest | Active | 61 | 4550 |
| PermissionSetService | Active | 58 | 7340 |
| PermissionSetServiceTest | Active | 58 | 19011 |
| PlatformCacheService | Active | 60 | 745 |
| PlatformCacheServiceTest | Active | 60 | 933 |
| PostSandboxRefresh | Active | 60 | 157 |
| ProcessLogger | Active | 62 | 1305 |
| ProcessLoggerTest | Active | 62 | 3766 |
| ProcessLogService | Active | 62 | 781 |
| ProcessLogServiceTest | Active | 62 | 505 |
| PublicGroupService | Active | 58 | 3550 |
| PublicGroupServiceTest | Active | 58 | 9144 |
| QAIntegrationService | Active | 58 | 589 |
| QAIntegrationServiceTest | Active | 58 | 348 |
| QueryWithLimit | Active | 48 | 1493 |
| QueueService | Active | 58 | 3522 |
| QueueServiceTest | Active | 58 | 8788 |
| QuickLightningLookupController | Active | 55 | 5184 |
| QuickLightningLookupControllerTest | Active | 55 | 1782 |
| QuoteService | Active | 59 | 468 |
| QuoteServiceTest | Active | 60 | 2421 |
| RecordTypeService | Active | 58 | 1375 |
| RemoveRecordInCollection | Active | 48 | 1165 |
| ScheduleUpdatingLeadOwner | Active | 58 | 254 |
| ScheduleUpdatingLeadOwner_Test | Active | 58 | 1885 |
| SDocTriggerHandler | Active | 59 | 242 |
| SeedSandbox | Active | 60 | 373 |
| SeedSandbox2 | Active | 60 | 375 |
| SeedSandbox3 | Active | 60 | 304 |
| ServiceAppointmentService | Active | 58 | 1711 |
| ServiceAppointmentServiceTest | Active | 58 | 7168 |
| ServiceAppointmentTriggerHandler | Active | 58 | 749 |
| ServiceException | Active | 58 | 52 |
| SiteLoginController | Active | 50 | 352 |
| SiteLoginControllerTest | Active | 50 | 393 |
| SiteRegisterController | Active | 50 | 1524 |
| SiteRegisterControllerTest | Active | 50 | 559 |
| SObjectDeepClone | Active | 42 | 7566 |
| SObjectDeepCloneTests | Active | 42 | 1685 |
| SObjectService | Active | 58 | 225 |
| SortCollection | Active | 48 | 11387 |
| SortCollectionTest | Active | 48 | 36944 |
| SSignEnvelopeTriggerHandler | Active | 58 | 260 |
| StaticResourceProxy | Active | 59 | 967 |
| StaticResourceProxyTest | Active | 60 | 1205 |
| StaticResourceService | Active | 59 | 3817 |
| StaticResourceServiceTest | Active | 59 | 3488 |
| StringService | Active | 62 | 455 |
| StringServiceTest | Active | 62 | 485 |
| SystemSettingSelector | Active | 58 | 2893 |
| SystemSettingSelectorTest | Active | 58 | 4927 |
| TestFactory | Active | 57 | 21573 |
| TriggerHandler | Active | 58 | 1549 |
| TriggerHandlerTest | Active | 58 | 2205 |
| UpsertRecords | Active | 48 | 2798 |
| UpsertRecordsTest | Active | 48 | 2262 |
| UserService | Active | 58 | 594 |
| UserServiceTest | Active | 58 | 3999 |
| WorkingHoursService | Active | 59 | 6749 |
| WorkingHoursServiceTest | Active | 59 | 8350 |
| WorkOrderCrewService | Active | 58 | 363 |
| WorkOrderCrewServiceTest | Active | 58 | 2296 |
| WorkOrderCrewTriggerHandler | Active | 58 | 206 |
| WorkOrderStatusAutomation | Active | 59 | 3791 |
| WorkOrderStatusAutomationTest | Active | 59 | 7369 |
| WorkOrderTriggerHandler | Active | 59 | 416 |
| WorkPlanService | Active | 59 | 931 |
| WorkPlanServiceTest | Active | 59 | 2307 |
| WorkPlanTriggerHandler | Active | 59 | 199 |

</details>

---

## Validation Rules

> 79 validation rules across the org. Active rules block save when their formula evaluates true.

| Object | Rule | Active | Error Message |
|--------|------|--------|---------------|
| Account | Labor_Div_Percent_Must_be_Approve_LD_Acc | ⛔ | LD Access must have an approved value (LC BCRD, LC Brothers, LC Expert, LC JNG, LC RJK, LC KCP) if Labor Division % is entered. |
| Account | No_Special_Characters_Phone | ⛔ | Please make sure that all phone numbers have the correct format: +1RRRXXXXXXX (RRR - Region). |
| AdCostSummary__c | Year_Must_Be_4_Digits | ✅ | Please enter a valid 4-digit year |
| Case | GeneralRelease_ServiceCall_Require_Terms | ✅ | Please enter General Release Terms when the General Release Type is Service Call. |
| Case | Require_Subject | ✅ | Case Subject is Required |
| CMTD__EnhancedRelatedList__mdt | Colour_Populated_For_Badge | ✅ | Colour can only be populated for Checkbox Badge UI Type |
| Contact | No_Special_Characters_Phone | ⛔ | Please make sure that all phone numbers have the correct format: +1RRRXXXXXXX (RRR - Region). |
| edf__Form_Element__c | Field_API_Name_Mandatory_Scenario | ⛔ | Field API Name is Mandatory when Form Element is not an HTML Snippet |
| FSL__GanttPalette__c | Color_Level_validation | ✅ | Color level value cannot be less than 4 or greater than 15 |
| FSL__Polygon__c | Polygon_Color_HEX_Format | ✅ | Polygon color must be in hexadecimal format: (for example: #ffffff) |
| FSL__Scheduling_Policy__c | Deny_Objectives_Negative_Weight | ✅ | Policy objectives weight can not be negative |
| FSL__Scheduling_Policy_Goal__c | Not_Zero | ✅ | Weight can't have zero value |
| FSL__Service_Goal__c | Resource_Priority_Not_Null | ✅ | Resource Priority Field should not be empty |
| FSL__Time_Dependency__c | Dependency_Is_Required | ✅ | Select a dependency type. |
| FSL__Time_Dependency__c | Root_Is_Required | ✅ | We couldn't create a dependency between the service appointments. Ask your Salesforce admin to give you permissions for all of the Time D... |
| FSL__Time_Dependency__c | Same_Resource_Required | ✅ | Immediately Follow dependency requires Same Resource |
| FSL__Time_Dependency__c | Service_Appointment_2_Is_Required | ✅ | Service appointment 2 is required. |
| FSL__Time_Dependency__c | Service_Appointment_2_Not_Changed | ✅ | It is not allowed to change any of the service appointments in the relationship |
| FSL__Work_Rule__c | Check_time_rule | ✅ | Time Operator should be 'Before or Equal To' when Service Schedule Time Property is 'SchedEndTime' |
| FSL__Work_Rule__c | Greater_than_zero | ✅ | Duration must be positive |
| FSL__Work_Rule__c | Maximum_Travel_Must_Be_Positive | ✅ | Maximum Travel from Home must be positive. |
| FSL__Work_Rule__c | Minimum_Gap_Positive | ✅ | Minimum gap should not be negative |
| FSL__Work_Rule__c | Start_Of_Day_Time_Format | ✅ | Time must be in the following format: HH:MM |
| FSL__Work_Rule__c | Time_Format | ✅ | Time must be in the following format: HH:MM |
| Lead | No_Special_Characters_Phone | ⛔ | Please make sure that all phone numbers have the correct format: +1RRRXXXXXXX (RRR - Region). |
| Lead | PhoneNumberConfirmed | ⛔ | Confirm the phone number. |
| Lead | Require_Project_Size_When_Qualified | ✅ | The Project Size field must be completed when moving the Lead to Qualified. |
| Lead | Unqualified_Status_Requires_Reason | ✅ | If Status is Unqualified then Unqualified Reason must be entered. |
| Opportunity | Close_Date_Uneditable_after_Closed_Won_L | ✅ | Contact PPP Support for assistance. |
| Opportunity | OnlyLostAfterClosedWon | ✅ | Please contact Support for this error. Rule Name: OnlyLostAfterClosedWon |
| Quote | Material_Cost_Estimate_Required | ⛔ | When materials are included or will be displayed to the customer, the materials cost field is required. |
| ResourceAbsence | Absence_Color_HEX_Format | ✅ | Gantt color must be in hexadecimal format: (for example: #ffffff) |
| ResourceAbsence | startShouldPrecedeEnd | ✅ | The Start Time must be earlier than the End Time. |
| rh2__PS_Describe__c | Block_Test_Int_Changes | ✅ | You have been stopped from changing Test Integer by a validation rule. |
| rh2__PS_Describe__c | Test_Rollup_Exception_Error_1 | ✅ | Test error for PS_Error_Handler |
| rh2__PS_Describe__c | Test_Rollup_Exception_Error_2 | ✅ | Test error for PS_Error_Handler Second |
| rh2__RH_Job__c | Positive_Increment | ✅ | Must enter a value that is greater than or equal to 1. |
| SDOC__SDRelationship__c | GD_Link | ✅ | Before you are able to manually set the Docs Status to "Linked to Google Doc", you must first enter a valid URL to an existing Google Doc... |
| ServiceAppointment | Dont_allow_scheduled_or_dispatched | ✅ | New service appointment cannot be created in scheduled or  dispatched statuses. |
| ServiceAppointment | isDueDateExist | ⛔ | DueDate field is required |
| ServiceAppointment | isDurationExist | ✅ | Duration field is required |
| ServiceAppointment | isEarliestStartTimeExist | ⛔ | EarliestStartTime field is required |
| ServiceAppointment | Related_Service_with_time_dependency | ✅ | Select a valid dependency type. If the appointments must be assigned to the same resource, the dependency type can’t be Same Start. |
| ServiceAppointment | Same_Resource_Same_Start | ✅ | Resource dependency is invalid. Time Dependency can't be Same Start when same resource is required. |
| ServiceAppointment | Schedule_End_Required | ✅ | Both scheduled start and end are required |
| ServiceAppointment | Schedule_Start_Required | ✅ | Both scheduled start and end are required |
| ServiceAppointment | Service_Color_HEX_Format | ✅ | Gantt color must be in hexadecimal format: (for example: #ffffff) |
| ServiceAppointment | startTimeShouldPrecedeEndTime | ⛔ | The Scheduled Start must be earlier than the Scheduled End. |
| ServiceAppointment | Time_dependency_with_related_service | ✅ | Please select Related Service. |
| ServiceCrewMember | Prevent_Crew_Allocation_For_Contractors | ✅ | Capacity Based Service Resource Cannot Have Crew Member Allocations |
| ServiceResource | Capacity_Resource_of_Type_Crew | ✅ | Capacity Resource Can't Be of Type Crew |
| ServiceResource | Resource_travel | ✅ | Resource travel speed must be greater than 0. |
| ServiceTerritoryMember | Limit_STM_End_Date | ✅ | End Date must be within 3 years from today |
| ServiceTerritoryMember | Secondary_STM | ✅ | Cannot save Service Territory Member of type secondary with Operating Hours or Address |
| SFDC_PTO_Request__c | End_date_greater_than_start_date | ✅ | Request dates must be chronological. |
| SFDC_PTO_Request__c | Hours_Off_must_be_positive | ✅ | Hours Off can not be negative. |
| SFDC_PTO_Request__c | Must_have_enough_PTO_or_Sick_Leave | ✅ | Not enough PTO / SL available. |
| SFDC_Staff__c | Dont_Allow_Leap_Days | ✅ | Cannot be a leap day; move it by a day. |
| SFDC_Staff__c | Hire_Date_is_before_Start_Date | ✅ | Hire Date must be before Start Date |
| SFDC_Staff__c | PTO_no_lower_than_zero | ✅ | PTO can not be less than zero. |
| SFDC_Staff__c | PTO_Refresh_cant_be_lower_than_zero | ✅ | PTO Refresh can not be lower than zero. |
| SFDC_Staff__c | SL_no_lower_than_zero | ✅ | SL can not be less than zero. |
| SFDC_Staff__c | SL_refresh_no_lower_than_zero | ✅ | SL refresh can not be lower than zero. |
| SFDC_Staff__c | Start_Date_is_before_Termination_Date | ✅ | Start Date must be before the Termination Date. |
| SFDC_Staff__c | Termination_Status_must_have_date | ✅ | Date required if the status is set to Terminated. |
| Transaction__c | Deposited_Requires_Reference_ID | ✅ | You must enter a Reference ID if Deposited is True. |
| Transaction__c | No_Transactions_on_Estimates | ✅ | Transaction and Attendance records are not allowed to be added to Estimate Work Orders. |
| Transaction__c | only_allow_finance_team_in_final_status | ⛔ | Contact the finance team to make changes. |
| User | FSK_User_Creation_Feature_Inactive | ✅ | FSSK Package: SFS Resource Type should only be used when the Field Service users automation feature in the Field Service Starter Kit Pack... |
| User | FSK_User_Type_Is_Not_Community | ✅ | FSSK Package: This SFS Resource Type value should only be used for community user records |
| User | FSK_User_Type_Is_Not_Standard | ✅ | FSSK Package: This SFS Resource Type value should only be used for users with a Salesforce user license |
| WorkOrder | Add_Assigned_Labor_Crew | ✅ | Add a labor crew to the "Assigned Labor Crew" field before Complete Paid in Full or Closed. |
| WorkOrder | BalanceOwedCannotMarkPaidInFull | ✅ | The Balance Owed is >0, so this cannot be moved to a status of Complete Paid In Full or Closed. |
| WorkOrder | Internal_Adjustment_Cannot_OverUnder_100 | ✅ | Internal Adjustments cannot be greater than $100 or less than -$100. |
| WorkOrder | Request_Review_2 | ✅ | Select Yes or No on the "Request Review" field prior to moving the status. |
| WorkOrder | RequestReview_If_Complete | ✅ | Please indicate whether a review should be requested. |
| WorkOrder | Start_End_Dates_Required_to_Complete | ✅ | The Start and End Dates are required to be entered to move to a Complete Status. |
| WorkOrder | Undeposted_PaymentIn_Cannot_be_Complete | ✅ | There are Payments In which are not Deposited. Please deposit the funds to move to a status of Complete Paid In Full or Closed. |
| WorkOrderCrew__c | No_Attendance_on_Estimates | ✅ | Transaction and Attendance records are not allowed to be added to Estimate Work Orders. |

---

## Record Types

> 39 record types defined on standard and custom objects.

| Object | Record Type |
|--------|-------------|
| Account | Customer |
| Account | Partner |
| Account | PersonAccount |
| Account | Tomco |
| Account | Vendor |
| Case | Customer_Service |
| Case | Technical_Support |
| Corporate_Document__c | Filing |
| Corporate_Document__c | Formation |
| Corporate_Document__c | Insurance |
| Corporate_Document__c | LicenseBond |
| Corporate_Document__c | Permit |
| Corporate_Document__c | State_Registration |
| Lead | Partner_Created |
| Lead | PartnerBasic |
| Lead | Phone_Inquiry |
| Lead | Web_Inquiry |
| Legal__c | Chargeback |
| Legal__c | Customer_Related |
| Legal__c | Legal_Layout |
| Legal__c | Subcontractor_Employee |
| Legal__c | Vehicle_Claim |
| Opportunity | Change_Order |
| Opportunity | New |
| Opportunity | PartnerBasic |
| Opportunity | Tomco |
| Quote | Tomco_Quote |
| Software__c | Dialpad |
| Software__c | E_Document |
| Software__c | Google |
| Software__c | Hatch |
| Software__c | Other |
| Software__c | Salesforce |
| Software__c | Slack |
| Transaction__c | Payment_In |
| Transaction__c | Payment_Out |
| Transaction__c | Purchase |
| WorkOrder | Standard |
| WorkOrder | Tomco |
