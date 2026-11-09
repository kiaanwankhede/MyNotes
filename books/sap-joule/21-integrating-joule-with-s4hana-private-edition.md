# Chapter 21: Integrating Joule with SAP S/4HANA Cloud Private Edition

*The on-premise-style route: Cloud Connector, ABAP content exposure, three destinations, an IPS source that reads users and roles over RFC, and a Fiori launchpad plug-in that makes the Joule icon appear.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the eleven integration steps, the Cloud Connector paths to expose, every destination value, the IPS configuration and the target mapping that activates the plug-in
> - **Level:** advanced · **Time:** about 30 minutes of reading
> - **Source:** SJ022, the Joule Onboarding Guide PDF, section 4.3, pages 56 to 74 (read in full); read 9 November 2026
> - **Builds on:** [Chapter 18](18-onboarding-guide-customer-managed-provisioning.md) and [Chapter 5](05-setting-up-joule-by-product.md) §5.4

**After this chapter you can:**
- list the prerequisites and the eleven steps in order
- expose the right paths in the Cloud Connector and the right content from `/UI2/CDM3_EXP_SCOPE`
- create the design-time, runtime, nomination and SSO destinations
- configure IPS source and target systems with the right properties
- create the `Shell-plugin` target mapping, and know the release and UI5 constraints

---

## 21.1 Prerequisites

- Customer-managed provisioning (Chapter 18) is done; the Joule security information has been read
- S/4HANA Private Edition is integrated with **Identity Authentication**
- A Work Zone, standard edition **service instance and service key** exist (**foundation plan**)
- The **connectivity plan of Cloud Identity services** is entitled in the subaccount

## 21.2 The eleven steps, in order

1. Configure trust to the IAS tenant
2. Configure the trusted domain in BTP
3. Configure user attributes from the identity directory
4. Configure trusted domains in IAS
5. Set up S/4HANA Private Edition as a content provider (Cloud Connector)
6. Expose Fiori launchpad content to BTP
7. SAP Build Work Zone and SAP Start
8. Run the Joule booster
9. Configure destinations
10. Configure Identity Provisioning
11. Configure and activate the Joule plug-in in a target mapping

### Map the system name in the Joule Admin Center (single system only)
- Only for a **single** Private Edition system or client; not needed for additional systems (see the multi-system chapter)
- Joule tenant admin roles must be assigned first so you can open the **Joule Admin Center**
- Steps: select the **Digital Assistant** (`sap_digital_assistant`), Edit, Destination; for the system type **`sap.s4pce`** choose **Custom Destination** and the destination **`S4HANA_PCE_SSO`**; Save

## 21.3 Content provider through the Cloud Connector

- **Security warning:** Work Zone uses the Cloud Connector as a proxy to any connected system, and **every path you configure is reachable through the public internet**; configure only what is needed and secure the system
- **Trust:** establish trust between the subaccount and the system; for principal propagation and basic authentication, **disable the "System Certificate for Logon" setting**

### Paths to expose (Cloud To On-Premise, HTTPS)

| Path | Purpose |
|---|---|
| `/sap/bc/lrep/` | card manifests and i18n files |
| `/sap/bc/ui2/app_index/` | UI5 app index |
| `/sap/bc/ui2/cdm3/` | CDM3 content |
| `/sap/bc/http/ui2/flp_content_exposure/` | CDM2 content |
| `/sap/opu/odata/` | data from OData services |
| `/sap/opu/odata4/` | data from OData V4 services |

- These are defaults; **restrict them further** to the services you actually use

### A second mapping for Identity Provisioning (RFC)

| Field | Value |
|---|---|
| Back-end type | ABAP System |
| Protocol | RFC or RFC SNC |
| Connection type | With load balancing (system ID and message server) |
| Message server | your host (example `ldcsuct`) |
| System ID | your SID (example `UCT`) |
| SAProuter | empty |
| Virtual message server / system ID | `ldcsuct` / `UCT` |
| Internal host result | `ldcsuct:sapmsUCT` |

- With the IPS **Naming Policy = Exact Name**, allow access to **`BAPI_USER_GETLIST`**, **`BAPI_USER_GET_DETAIL`**, **`PRGN_ACTIVITY_GROUPS_LOAD_RFC`**, **`PRGN_ROLE_GETLIST`**

### Check that exposure works
- **Version 2** (Private Edition 2023 onwards): in `/IWFND/GW_CLIENT` send a GET to `/sap/bc/http/ui2/flp_content_exposure/`; expect **200**
- **Version 1** (all releases): GET `/sap/bc/ui2/cdm3/`; expect **200**
- Create a **technical service user** in `SU01` (type **Service**) that meets the "Manage Launchpad Content for Exposure" prerequisites
- In **My Home settings**, business users must have the value **Insights Cards**

## 21.4 Expose launchpad content (`/UI2/CDM3_EXP_SCOPE`)

- Choose the **exposure version**; each version has its own repository, so you can run **both at once**
- Choose roles: **all roles with launchpad content** (default) or **selected roles in areas**
  - all roles in all areas are exposed together; add or remove a role in the selection and run again
  - **derived roles are not supported directly**: add the **leading role** and the derived role is exposed as a related assignment
- Optional: **Preview Content** or **Preview Area Content**
- **Save Selected Roles before exposing**, or the last saved selection is used
- Check the log: **only content without errors can be exposed**
- Then **Schedule** a regular job or **Expose Content** manually

## 21.5 Destinations

### Design-time destination

| Property | Value |
|---|---|
| Name | suffix `dt`; **lowercase letters only** |
| Type | HTTP |
| URL | `https://<host>:<port>/sap/bc/ui2/cdm3/entities` (version 1) or `https://<host>:<port>/sap/bc/http/ui2/flp_content_exposure/entities` (version 2) |
| Proxy type | OnPremise |
| Authentication | Basic, with a technical user that can read the CDM; **principal propagation is not supported** |
| Additional | `sap-client` (for example `120`) |

### Runtime destination

| Property | Value |
|---|---|
| Name | suffix `rt`; **lowercase only, no underscore** (example `sxw920rt`) |
| Type | HTTP |
| URL | base URL of the Fiori launchpad |
| Proxy type | direct access: Internet; tunnelled: OnPremise |
| Authentication | NoAuthentication |
| `HTML5.DynamicDestination` | `true` for dynamic tiles |
| `CEP.EnableCsrfProtection` | `true` when the back end does not protect against CSRF |
| `sap-platform` | `ABAP` |
| `sap-client`, `sap-sysid` | for example `920`, `SXW` |
| `launchpad.wa.productId`, `launchpad.wa.productVersion` | to enable **SAP Companion** on-screen help |
| `sap-provider-label` | friendly system name (shown on tiles, in search results, default values and App Finder) |
| `sap-service` | four characters: `32` plus the two-digit instance number (example `3200`) |
| `sap-start` | `true` |

### Runtime destination for dynamic data
- Defaults to the same as the runtime destination; choose another if needed

### Nominations destination `privatecloud` (via Cloud Connector)

| Field | Value |
|---|---|
| Type / ProxyType | HTTP / OnPremise |
| URL | virtual host and port from the Cloud Connector |
| Authentication | **PrincipalPropagation** |
| Location ID | the Cloud Connector ID, if set |
| `HTML5.DynamicDestination` | `true` |
| `nameIdFormat` | `tc:SAML:1.1:nameid-format:emailAddress` |
| `sap-card-nominations-path` | `/sap/opu/odata4/ui2/insights_srv/srvd/ui2/insights_cards_read_srv/0001/CEP_Cards?$expand=DescriptorResources` |

### Content provider (Work Zone Channel Manager)
- Fields: title, a **unique ID**, design-time and runtime destinations, dynamic-data destination (default), **Automatically add all content items = true**, **Use IPS = true**, and **Include group and catalog assignments to roles**:
  - off: all groups and catalogs are included, regardless of role
  - on: only groups and catalogs directly assigned to roles
- Status goes from "Creating…" to "Created"; the **Report** link counts roles, apps, groups, catalogs, spaces, pages and URL templates

### Single sign-on destination `S4HANA_PCE_SSO` (in the Joule subaccount)

| Property | Value |
|---|---|
| Name | `S4HANA_PCE_SSO` |
| Type | HTTP |
| URL | virtual host of the Cloud Connector, `https://<host>:<port>` |
| Proxy type | OnPremise |
| Authentication | principal propagation supported |
| Additional | `sap-client` |

## 21.6 Identity Provisioning

1. In `SU01`, add the role **`SAP_BC_JSF_COMMUNICATION_RO`** to the technical service user
2. Subscribe to **Cloud Identity Services, plan connectivity** (in the Joule subaccount if its region matches the CIS tenant; otherwise in another subaccount in the matching region)
3. Create a **destination of type RFC** for IPS:

| Field | Value |
|---|---|
| Name / Type | your name / RFC |
| ProxyType | OnPremise |
| User / Password | the technical service user |
| Authorization type | `CONFIGURED_USER` |
| Location ID | Cloud Connector ID, if used |
| `jco.client.client` | client (example `950`) |
| `jco.client.mshost` | virtual host, up to the colon (example `uctclnt950rfc`) |
| `jco.client.r3name` | system ID (example `UCT`) |

4. **Source system** in IAS admin (`<IAS domain>/admin`): type **SAP Application Server ABAP**; paste the **standard transformation**:
   - user: `USERNAME` becomes `userName` (correlation attribute); `ALIAS.USERALIAS` becomes `externalId`; `SAPUSER_UUID.SAP_UID` becomes the SAP extension `userUuid`; `ADDRESS.E_MAIL` becomes the primary work email; first, last, middle name, nickname, title, country, phone map across; `DEFAULTS.LANGU` and `LANGUP_ISO` become `locale` and `preferredLanguage`; `LOGONDATA.TZONE` becomes `timezone`; **`active` is true unless the user is locked** (local, global or wrong-logon lock); `ACTIVITYGROUPS[*].AGR_NAME` becomes `groups`
   - group: `ROLE_NAME` becomes `displayName`, optionally prefixed by `%abap.role.prefix%`; `USERLIST[*].USERNAME` becomes `members`
5. **Target system** of type Work Zone, standard edition; pick the source; paste the standard transformation:
   - user: only if the user has **email and userUuid**; `update` is skipped; sets `providerId` to `%cflp.providerId%`; email primary; `userUuid` becomes `externalId`; groups resolved by `resolveEntityIds`
   - group: `displayName` becomes `externalId`; the role `externalId` is cleaned (remove a leading `pcd:`, replace `/` with `:`, `(` with `@`, `)` with `+`); members resolved
6. Target properties:

| Property | Value |
|---|---|
| Authentication | BasicAuthentication |
| `cflp.group.unique.attribute` | `externalId`, `['urn:ietf:params:scim:schemas:extension:2.0:mapping']['providerId']` |
| `cflp.patch.group.members.above.threshold` | `5000` |
| `cflp.providerId` | the content provider ID (example `S4_PC_UCT950`) |
| `cflp.user.unique.attribute` | `emails[0].value`, `…['providerId']`, `externalId` |
| `ips.trace.failed.entity.content` | `false` |
| `OAuth2TokenServiceURL` | the service key's UAA URL plus `/oauth/token` |
| User / Password / URL | `clientid` / `clientsecret` / `portal-service` from the service key |
| ProxyType / Type | Internet / HTTP |

7. Source system, Jobs: **Run Now** on the **Read Job**; check **Provisioning Logs**
- **Result:** users who made Insights cards visible in **My Home** now see them in Work Zone

## 21.7 The Joule plug-in target mapping

- **Prerequisite:** a **business catalog**
- In the launchpad app manager create a target mapping with the intent **`Shell-plugin`**:

| Field | Value |
|---|---|
| Semantic object / Action | `Shell` / `plugin` |
| Application type | SAP UI5 Fiori App |
| Title | Joule |
| URL | the Joule application URL plus `/resources/public/webclient/s4` |
| ID | `sap.das.webclientplugin.s4` |
| Device types | desktop, phone, as needed |
| Parameters | optional name/default value pairs for the plug-in |

- `Shell-plugin` mappings are special: they **do not appear** in TargetMappings feeds, `resolveLink` or `getLinksForSemanticObjects`
- Then assign the **catalog to a role** in the launchpad content manager, and the **role to users**

## 21.8 Constraints for Private Edition

- Available from **release 2021**, but not every capability from 2021 (see release-specific capabilities and note 3523238)
- Only **within RISE with SAP**, and only in an **SAP-managed data centre**
- **Add your system to a Joule formation** when you already have a formation without it, or after you **upgrade** the system; if you have Joule but no formation, run the booster or create the formation
- **Minimum UI5 version:**

| Release | Minimum UI5 |
|---|---|
| 2021 | 1.96.33 |
| 2022 | 1.108.33 |
| 2023 | 1.120.0 or latest |

- **2021:** some navigation does not work as expected, and some Fiori navigations open in a **new window**

## 21.9 Added by Claude, not from the sources
- The section order merges the guide's integration-steps list with its sections
- The JSON transformations are summarised, not copied; use the guide's text when you paste them
- The remark that the guide's numbering of steps jumps in places (for example the IPS source-system procedure) is mine

---

## Screenshots and figures from the sources
- Pages 56 to 74 contain only tables, code blocks and text; there is no screenshot to save

---

## Recap
- Eleven steps; the booster comes **after** content exposure and Work Zone
- Cloud Connector exposes six paths (restrict further) and an RFC mapping with four BAPIs
- Three kinds of destination: design time (`dt`), runtime (`rt`) and SSO (`S4HANA_PCE_SSO`), plus `privatecloud` for nominations
- IPS: ABAP source over RFC, Work Zone target; `cflp.providerId` equals the content provider ID
- The plug-in is a `Shell-plugin` target mapping with ID `sap.das.webclientplugin.s4`
- Minimum UI5 depends on release; RISE and SAP-managed data centres only

## Practice
- Which four function modules must the Cloud Connector allow for IPS?
- What do version 1 and version 2 of content exposure check with `/IWFND/GW_CLIENT`?
- Why does a `Shell-plugin` mapping not show in normal target-mapping lists?

---

## How this chapter was checked
- All 19 pages were read in full; destination and property tables were copied field by field

## Sources and further reading
- SAP Help Portal, *Integrating Joule with SAP Solutions* (PDF, pages 56 to 74): https://help.sap.com/doc/de3af3c0f81642dbaa4d36172ed57a72/CLOUD/en-US/79bfc83ab386450c8cd9c7937ce26a3a.pdf
- SAP Discovery Center, Joule missions: https://discovery-center.cloud.sap/missiondetail/4538/

---

*Previous: [Chapter 20: Integrating Joule with SAP SuccessFactors](20-integrating-joule-with-successfactors.md)*

*Next: [Chapter 22: Integrating Joule with SAP S/4HANA Cloud Public Edition](22-integrating-joule-with-s4hana-public-edition.md)*
