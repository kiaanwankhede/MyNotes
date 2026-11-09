# Chapter 20: Integrating Joule with SAP SuccessFactors

*How a SuccessFactors tenant is connected to Joule: the booster, two destinations, a content provider, and an Identity Provisioning job that carries users and roles into Work Zone.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the six steps of the SuccessFactors integration, the destination and content-provider values, the IPS transformation rules, and the permission that gives a user access to Joule
> - **Level:** intermediate · **Time:** about 15 minutes of reading
> - **Source:** SJ022, the Joule Onboarding Guide PDF, section 4.2, pages 49 to 55 (read in full); read 9 November 2026
> - **Builds on:** [Chapter 18](18-onboarding-guide-customer-managed-provisioning.md) and [Chapter 5](05-setting-up-joule-by-product.md)

**After this chapter you can:**
- list the six steps and say which are automatic after 13 October
- fill in the design-time and runtime destinations and the `sfsf` content provider
- check the group mapping in the IPS source and target systems
- grant users access and avoid the 24 to 48 hour delay surprise

---

## 20.1 The two provisioning routes

- **SAP-managed provisioning:** SAP does the technical setup; also covers restrictions and the move from customer-managed
- **Customer-managed provisioning** (this chapter): you do it in BTP; six steps:
  1. Register the SuccessFactors system in the BTP global account (System Landscape)
  2. Run the Joule booster
  3. Integrate **SuccessFactors Work Zone** with SuccessFactors using the **Unified Customer Landscape**
  4. Configure Identity Provisioning
  5. Set up Joule in SuccessFactors **Mobile**
  6. Grant permission to users
- **Change on 13 October (the guide writes 2026):** after the booster, the destinations `LPS_SFSF_rt`, `LPS_SFSF_dt` and `SFSF_SSO` are **managed in the back end and do not appear** under Connectivity, Destinations; if you set Joule up **before** that date, the manual `LPS_SFSF_rt` and `LPS_SFSF_dt` remain and you maintain them as in 20.2
- (Chapter 18 says "13 October 2025" for the navigation-service destination; the guide uses 2025 there and 2026 here; check the date for your own tenant)

## 20.2 Consume content from SuccessFactors

- **Idea:** SuccessFactors exposes a **REST API that pushes CDM content to SAP Start**; you need a design-time destination, a runtime destination and a **content channel** in Work Zone Content Manager

### Design-time destination `LPS_SFSF_dt`
- **Basic authentication for SuccessFactors APIs is deprecated**; you can use **certificate-based** destinations instead

| Field | Value |
|---|---|
| Name | `LPS_SFSF_dt` |
| Type | HTTP |
| URL | `https://<tenant API URL>/rest/servicesfoundation/sfcdmcontentservice/v1/SFCDMContent` |
| Proxy type | Internet |
| Authentication | Basic (per the guide) |
| User | a SuccessFactors user with OData API access, as `username@COMPANY` |
| Password | that user's password |
| Additional | **Use default JDK trust store** on; `HTML5.Dynamic Destination` = `true` |

### Runtime destination `LPS_SFSF_rt` (created by the booster)

| Field | Value |
|---|---|
| Proxy type | Internet |
| Authentication | NoAuthentication |
| Type | HTTP |
| URL | your SuccessFactors tenant URL |
| Additional | `sfsf.companyID` = the SuccessFactors company |

- **Update it when:**
  - you use the Work Zone **foundation** plan (not standard): add `sap-start` = `true` (typed by hand; it is not in the drop-down)
  - the tenant has moved to the **cloud.sap super domain**: change the URL, for example `https://sfsf.cloud.sap`

### Content provider (Work Zone Site Manager, Channel Manager, New Content Provider)

| Field | Value |
|---|---|
| Title and ID | `sfsf` (recommended) |
| Design-time destination | `LPS_SFSF_dt` |
| Runtime destination | `LPS_SFSF_rt` |
| Runtime destination for dynamic data | use default runtime destination |
| Automatically add all content items to subaccount | True |
| Use the Identity Provisioning service to provision user authorisations | True |

## 20.3 Identity Provisioning (IPS)

- **Purpose:** the Work Zone navigation service uses IPS to carry identities and authorisations between source and target systems; for some customers the **Upgrade Center** has already set up SuccessFactors and IAS as source and target
- **Two things must be provisioned:**
  1. user details (email, **Global User ID**, group memberships) from SuccessFactors to Work Zone
  2. **user roles as groups**, with the **role ID as external ID** plus memberships
- **You need** admin access to the IPS tenant and the **Manage Identity Provisioning** role
- **Existing IAS customers must move from the OData API to the SCIM API** for IPS (the guide points to an upgrade note)

### Steps in the IAS admin console (Identity Provisioning)
1. **Source system** (SuccessFactors), Transformations tab (JSON editor available):
   - the **group entity**: `Ignore` = `false` (so groups are provisioned) and a mapping that sets `externalId` from the source `$.id`
2. Properties tab: set **`sf.user.filter`** so it fetches all required and valid users
3. **Optional:** if you do **not** want groups provisioned in IAS, open the IAS **target system** and set the group entity `Ignore` = `true`
4. **Create a new target system** of type **SAP Build Work Zone, standard edition**; name it (for example `Work Zone-Target`); pick the SuccessFactors source system
5. Target Transformations: add the group mapping `$.externalId` to `$.externalId`
6. Target Properties (values come from the Work Zone **service key**):

| Property | Value |
|---|---|
| URL | `portal-service` under `endpoints` |
| Authentication | BasicAuthentication |
| User / Password | `clientid` / `clientsecret` under `uaa` |
| ProxyType / Type | Internet / HTTP |
| OAuth2TokenServiceURL | `https://<uaa url>/oauth/token` |
| `ips.trace.failed.entity.content` | `false` |
| `cflp.user.unique.attribute` | `emails[0].value`, `['urn:ietf:params:scim:schemas:extension:2.0:mapping']['providerId']`, `externalId` |
| `cflp.group.unique.attribute` | `externalId`, `['urn:ietf:params:scim:schemas:extension:2.0:mapping']['providerId']` |
| `cflp.providerId` | the **ID of the SuccessFactors content channel** in Work Zone (`sfsf`) |
| `cflp.support.bulk.operation` | `false` (set `true` plus `cflp.bulk.operations.max.count` = `100` if you have very many entries) |

7. Back on the source system, **Jobs tab**: run a **Read** or **Resync** job

### Timing (important in practice)
- Schedule the IPS job at an interval of **24 hours or less**, so permissions land on time and overlap with SuccessFactors' **Refresh Synthetic Group Data** job
- Roles may take **24 to 48 hours** to show in the navigation service
- For an ad hoc sync, run **Refresh Synthetic Group Data** in SuccessFactors and then the IPS job

## 20.4 Grant permission to users

- **Joule acts with the permissions of the user who operates it**; audit user permissions **before** you give access
- **Grant:** User Permissions, General User Permission, **Access to Joule**
- **Recommended for Employee Central customers:** turn on **Employee Central Quick Actions** and configure the templates
- **Result:** Joule is ready to use

## 20.5 Added by Claude, not from the sources
- The note about the 2025 versus 2026 date is mine: the guide gives 13 October 2025 in the Work Zone section and 13 October 2026 in this one; I could not tell which is correct
- The six-step list is the guide's; the grouping into subsections is mine

---

## Screenshots and figures from the sources
- Pages 49 to 55 contain no screenshots worth saving; all settings are in tables, reproduced above

---

## Recap
- Six steps: register system, booster, Work Zone via Unified Customer Landscape, IPS, mobile, permissions
- Destinations: `LPS_SFSF_dt` (design time, SFCDMContent API) and `LPS_SFSF_rt` (runtime, tenant URL, `sfsf.companyID`); content provider `sfsf`
- IPS target property `cflp.providerId` must equal the content channel ID
- Roles arrive as groups with the role ID as external ID; allow 24 to 48 hours
- Permission **Access to Joule**; Joule uses the user's own permissions

## Practice
- Which URL path does the design-time destination call?
- Why must `cflp.providerId` match the content provider ID?
- What do you run in SuccessFactors before the IPS job when you need roles quickly?

---

## How this chapter was checked
- All seven pages were read in full; tables were copied field by field

## Sources and further reading
- SAP Help Portal, *Integrating Joule with SAP Solutions* (PDF, pages 49 to 55): https://help.sap.com/doc/de3af3c0f81642dbaa4d36172ed57a72/CLOUD/en-US/79bfc83ab386450c8cd9c7937ce26a3a.pdf
- SAP Discovery Center, Activate Joule for SAP SuccessFactors: https://discovery-center.cloud.sap/missiondetail/4451/4737/

---

*Previous: [Chapter 19: Analytical insights](19-analytical-insights-sap-analytics-cloud.md)*

*Next: [Chapter 21: Integrating Joule with SAP S/4HANA Cloud Private Edition](21-integrating-joule-with-s4hana-private-edition.md)*
