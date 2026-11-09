# Chapter 22: Integrating Joule with SAP S/4HANA Cloud Public Edition

*Public Edition is the lighter integration: communication scenarios replace the Cloud Connector, and the booster does most of the work. What is left for you is the exposure roles, the system registration, an IPS source and target, a content security policy and the visibility of the Joule icon.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the twelve integration steps, how to register the system with a token, the IPS properties and transformation rules, the CSP entry, the language and rate-limit constraints, and the role-based icon switch
> - **Level:** intermediate · **Time:** about 25 minutes of reading
> - **Source:** SJ022, the Joule Onboarding Guide PDF, section 4.4, pages 74 to 92 (read in full); read 9 November 2026
> - **Builds on:** [Chapter 5](05-setting-up-joule-by-product.md) §5.4a (the setup blog) and [Chapter 18](18-onboarding-guide-customer-managed-provisioning.md)

**After this chapter you can:**
- run the twelve steps in order and know which are Public-Edition-specific
- register the system with a registration token
- fill in the IPS source and target properties and explain the transformation
- add the Joule URL to the content security policy
- control who sees the Joule icon with `SAP_COM_0882`

---

## 22.1 Context and warnings

- The integration is between Joule and the **technical product** S/4HANA Cloud Public Edition
- The booster, among other things, **enables the communication scenario `SAP_COM_0882` (Joule Integration)** in the background
- **Entitlement:** an extra entitlement and authorisation may be needed to use Joule in Public Edition; ask your account executive
- **Regional note:** some capabilities may process data in another geography; review the regional considerations first (SAP note 3799748)
- **Re-running the booster** fails with the "only one formation of type Integration with Joule" error (see Chapter 18); include systems instead

## 22.2 The twelve steps

1. **Expose the Fiori launchpad content to BTP** (specific)
2. Configure trust to the IAS tenant
3. Configure user attributes from the identity directory
4. **Register the Public Edition system** (specific)
5. Create the Work Zone application and instance
6. Run the Joule booster
7. **Configure Identity Provisioning** (specific)
8. Configure the trusted domain in BTP
9. Configure trusted domains in IAS
10. **Maintain a custom content security policy** (specific)
11. **Enable the Joule icon** on the launchpad (specific)
12. Set up document grounding ([Chapter 26](26-document-grounding-setup-and-pipelines.md))

## 22.3 Step 1: expose launchpad content

- The booster creates a **communication arrangement and a communication system** for scenario **`SAP_COM_0647`** (Launchpad Content Exposure to SAP BTP Integration)
- Usually **Exposure Role Selection = `ALL`** (all roles with launchpad content)
- If you set it to **`SELECTION`**: in **Maintain Business Roles**, open each business role and select **Exposed to SAP BTP**, confirm; check the log in the **Display Launchpad Content Exposure Logs** tile

## 22.4 Step 4: register the system

1. BTP cockpit, global account, System Landscape, Systems, **Add System**: name, type, Add
2. Communication Scenario Groups: **All Communication Scenarios**; **Get Token**; copy the **registration token**; close
3. In Public Edition open **Maintain BTP Extension**, New, paste the token
4. Status turns **Enabled** there and **Registered** in the cockpit

## 22.5 Step 7: Identity Provisioning

- **What moves:** user details (email, Global User ID, group memberships) and **roles as groups**, role ID as external ID
- **Prerequisites:** admin access to the IPS tenant and the Manage Identity Provisioning role; the communication scenario and users for **`SAP_COM_0193`** exist

### Source system (IAS, Identity Provisioning, Source Systems)

| Property | Value |
|---|---|
| Type / ProxyType | HTTP / Internet |
| URL | the API URL from the `SAP_COM_0193` arrangement (for example `https://my123456-api.s4hana.ondemand.com` or `.cloud.sap`) |
| Authentication | BasicAuthentication |
| User / Password | from the communication arrangement; **do not use a comma** in either |
| `s4hana.cloud.skip.read.archived` | on by default (skip disabled entities); set `false` or delete to always read them |
| `ips.date.variable.format` | `yyyy-MM-dd` |
| `s4hana.cloud.api.version` | `1` (means the system uses `SAP_COM_0193`) |
| `ips.trace.skipped.entity.content` / `ips.trace.failed.entity.content` | `true` / `true` |

### Default source transformation (what it does)
- A user is read only when the **validity period contains today**
- `personID` is the entity ID; first, last, middle and full name, `userName` (correlation attribute) and the work email map to the SCIM user
- `active` is true, **false when `lockedIndicator` is true**
- `logonLanguageCode` becomes `locale`; `globalUserID` becomes the SAP `userUuid`
- `user.role` becomes `groups`, optionally prefixed with `%s4hana.cloud.roles.prefix%`
- the time-zone code is mapped by a table to an IANA name (for example `WDFT` to `Europe/Berlin`, `EST` to `America/New_York`, `JAPAN` to `Asia/Tokyo`), default `Europe/Berlin`
- the business-partner role code sets `userType`: `BUP003` Employee, `BBP005` Contingent Worker, default Employee
- groups: `ID` becomes `displayName` (with optional prefix); `to_BusinessUserAssignment` becomes `members`

### Target system (Work Zone, standard edition)

| Property | Value |
|---|---|
| Type / ProxyType / Authentication | HTTP / Internet / BasicAuthentication |
| URL | `portal-service` from the Work Zone service key |
| User / Password | `uaa.clientid` / `uaa.clientsecret` |
| `OAuth2TokenServiceURL` | `<uaa.url>/oauth/token` |
| `cflp.providerId` | the provider ID set in Channel Manager |
| `ips.failed.request.retry.attempts` | `2` |
| `ips.failed.request.retry.attempts.interval` | `50` |
| `ips.trace.failed.entity.content` | `true` |
| `xsuaa.user.unique.attribute` | `userName,origin` |
| `xsuaa.origin` | `sap.custom` |

- **`cflp.user.unique.attribute`:** how a conflicting user is found; filled in automatically (`emails[0].value`, providerId, `externalId`); with `externalId` the conflict is resolved by `externalId` plus `providerId`, otherwise by email plus `providerId`; **both must match or user creation fails**; **do not change it**
- **`cflp.group.unique.attribute`:** the pair `externalId` and `providerId`; a match **overwrites** the existing group; a half match fails
- **`cflp.support.bulk.operation`:** default `false`; when `true`, create or delete many users, and create, update or delete many groups per request; **`cflp.bulk.operations.max.count`** default 20, maximum 100 (larger values become 20)
- **Delete guards:** `ips.delete.threshold.groups` and `ips.delete.threshold.users` stop a filter mistake from deleting many entities
- Default target transformation: users **skip update**; set `providerId` from `%cflp.providerId%`; primary email; `userUuid` becomes `externalId`; groups resolved; for groups, `displayName` becomes `externalId` and the `pcd:`, `/`, `(`, `)` clean-up used in Chapter 21

### Run replication
- Source Systems, your system, Jobs: **Read Job, Run Now**, then **Resync, Run Now**
- **Schedule the Read Job every 24 hours**

## 22.6 Step 10: custom content security policy

- Reason: the Joule plug-in script loads **cross-origin**
- App **Manage Content Security Policy**, tab Trusted Sites, details for **Resources Scripts**, **New** under Managed by Customer, enter your **Joule tenant URL**, Save

## 22.7 Constraints

- **Landscapes:** Joule works in **2-system (2SL) and 3-system (3SL)** landscapes
- **Languages:** English, German, French, Spanish, Polish, Portuguese, Greek, Korean, Japanese, Vietnamese, Chinese (not the full globalisation set of Public Edition)
- **No personal or sensitive data** may be entered into Joule
- **Single log-out (SLO)** needs to be configured separately
- **The booster enables Joule for all users**
- **Web client is embedded in an iFrame**, so:
  - blocking of iFrames from Joule domains (`*.cloud.sap`) and IAS domains must be off in the browser (by default or policy)
  - SSO needs a **shared IAS session**; if IAS is a proxy IdP it must **not force authentication with the corporate IdP each time**
- **Rate limit: 3000 requests per minute per tenant**; BTP rate limits also apply
- Work Zone, standard edition restrictions for Public Edition apply (note 3075638)
- If Work Zone standard is not used yet, Joule uses its **foundation plan** for navigation, so IPS is enabled and configured for user assignment

## 22.8 Step 11: the Joule icon (`SAP_COM_0882`)

- The booster (or including the system) enables **`SAP_COM_0882`** automatically
- The communication arrangement property **Plug-In Activation State** decides who sees the icon:

| Value | Who sees Joule |
|---|---|
| empty | all users of the system |
| `ROLE` | only users whose business roles contain the business catalog **User Interface - Joule Plugin** (`SAP_CORE_BC_UI_JOU_PC`) |

- From **Public Edition 2602 SP06**, role-based activation is the **default**, and the template role **`SAP_BR_EMPLOYEE`** contains that catalog
- **Existing arrangements are not changed automatically**; to restrict access, set `ROLE` and add the catalog to the users' roles
- **Never delete** the generated communication arrangement and system; Joule stops working

## 22.9 Added by Claude, not from the sources
- The "twelve steps" list is the guide's; the markings of "specific" steps follow its own labels
- The transformation bullets summarise the JSON and are not a copy
- The reference to Chapter 26 is my forward link

---

## Screenshots and figures from the sources
- Pages 74 to 92 contain no screenshot worth saving

---

## Recap
- Booster enables `SAP_COM_0882`; exposure uses `SAP_COM_0647`; IPS reads through `SAP_COM_0193`
- Register the system with a **token** pasted into Maintain BTP Extension
- IPS: Public Edition source, Work Zone target, same `cflp.providerId` rules as other products
- CSP entry for the Joule tenant URL under Resources Scripts
- 3000 requests per minute per tenant; iFrame and shared IAS session required
- From 2602 SP06 the icon is role-based by default

## Practice
- Which three communication scenarios appear in this chapter and what is each for?
- What happens if `cflp.user.unique.attribute` is changed?
- How do you give Joule to only some users?

---

## How this chapter was checked
- All 19 pages were read in full; property values were copied field by field

## Sources and further reading
- SAP Help Portal, *Integrating Joule with SAP Solutions* (PDF, pages 74 to 92): https://help.sap.com/doc/de3af3c0f81642dbaa4d36172ed57a72/CLOUD/en-US/79bfc83ab386450c8cd9c7937ce26a3a.pdf
- SAP Discovery Center, Activate Joule with SAP S/4HANA Cloud Public Edition: https://discovery-center.cloud.sap/missiondetail/4452/4738/

---

*Previous: [Chapter 21: Integrating Joule with SAP S/4HANA Cloud Private Edition](21-integrating-joule-with-s4hana-private-edition.md)*

*Next: [Chapter 23: Integrating Joule with IBP, Signavio, Ariba and the documentation-only products](23-integrating-joule-ibp-signavio-ariba-and-docs-only-products.md)*
