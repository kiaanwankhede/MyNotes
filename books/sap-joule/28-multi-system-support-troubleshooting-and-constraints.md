# Chapter 28: Multi-system support, troubleshooting and constraints

*How Joule talks to several systems of the same type (dev, test, prod, regional), how it picks the right one, and the known problems and hard limits you should plan around.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the four configuration steps for multiple S/4HANA systems, how disambiguation works and how to help it with system metadata, three common problems, and the platform constraints
> - **Level:** advanced · **Time:** about 20 minutes of reading
> - **Source:** SJ022, the Joule Onboarding Guide PDF, sections 6 to 8, pages 222 to 234 (read in full); read 9 November 2026
> - **Builds on:** [Chapter 21](21-integrating-joule-with-s4hana-private-edition.md) and [Chapter 22](22-integrating-joule-with-s4hana-public-edition.md)

**After this chapter you can:**
- connect more than one S/4HANA system to one Joule
- write system descriptions that make automatic selection reliable
- fix a blank Joule screen, a missing navigation button and the multi-subaccount case
- list the constraints that affect design (OIDC only, rate limit, one Work Zone)

---

## 28.1 Multi-system support

- **What:** Joule connects to several systems of the **same type** (dev/test/prod, regional production systems, several clients) and offers disambiguation
- **Relies on:** formations, system information distribution, role and permission mapping, Work Zone CDM
- **Supported only for S/4HANA Cloud Private Edition and Public Edition**
- **Prerequisites:** all systems use the **same Identity Authentication tenant**, Work Zone is integrated, a destination exists per system, roles are assigned

### The four steps
1. **Include the systems in the formation**
2. **Create a destination per additional system**
3. **Map each system name to its content provider ID**
4. **Configure system metadata** (optional, strongly recommended)

### Private Edition
- **Do not re-run the booster** for extra systems; skip steps 8 (booster) and 9 (destinations) of the single-system chapter
- **Destinations:** rename `S4HANA_PCE_SSO` per system with the system name as suffix (example `S4HANA_PCE_SSO_QZ2002`); one destination for each system
- **Formation:** include every system
- **Content provider ID:** copy the CDM content provider ID from the Work Zone **Channel Manager**
- **Joule Admin Center:** Digital Assistant `sap_digital_assistant`, Edit; set **System Name** (system type `sap.s4pce`) to the content channel ID, and the **custom destination** for each system

### Public Edition
- Skip the booster step; include the systems in the formation
- In the Admin Center set the **System Name** (system type `sap.s4`) to the content channel ID
- If an error shows, set the custom destination to `S4HANA_PUB_SSO`

## 28.2 Disambiguation: how Joule picks a system

- **Automatic selection** uses conversation context and history, the user's permissions and the system metadata; Joule says something like "Using Orion Finance for this request"
- **If unsure**, it shows a **selection card** with System Title, Description and System ID
- **Order:** the scenario is disambiguated first, then the system, one after the other
- **Tips for users:** name a location or brand in the request ("Show my expenses for the Munich office"); the choice **persists within the conversation**; **start a new conversation** to reset
- **Troubleshooting:**

| Symptom | What to check |
|---|---|
| The needed system is not offered | the user's access to that system |
| The wrong system keeps being chosen | be more explicit in the request, or review the descriptions |
| No selection messages appear | the feature may not be enabled |

### System metadata
- **Fields:** System ID (automatic), **System Title**, **System Description**; configure in the **Joule Admin Center, Systems Configuration**
- **Best practice:** put geography, business purpose and organisational context into the description
  - good: "Financial system for EMEA region, handles accounts payable and receivable for the automotive brand. Located in Munich, Germany. Company code 1000."
  - poor: "Finance system"

## 28.3 Troubleshooting

| Problem | Fix |
|---|---|
| **Blank Joule screen** when a corporate IdP (Azure AD, Okta) is used | In Identity Authentication set the corporate IdP as the **default identity provider** of the Joule application |
| **Navigation button missing** after a job run or sync | In Work Zone open the content channel, set **Token Service URL Type** to **Dedicated**, then refresh Work Zone manually |
| **Joule and Work Zone in different subaccounts** | From **13 October 2025** no navigation destination is needed; if one already exists, see "User Propagation between Cloud Foundry Applications" |

## 28.4 Constraints

- **OIDC trust with Identity Authentication is required**; SAML is not supported
- The **IAS domain for the BTP trust must equal** the IAS domain of the SAP product
- **SAML and OIDC trust to the same IAS tenant cannot coexist**; create the Joule subscription in **another subaccount** with OIDC
- **Work Zone is used for navigation**, so **Identity Provisioning must be enabled**
- **Rate limit:** 3,000 requests per minute per user or tenant (the guide's wording says "per user/tenant")
- **One Joule instance per Work Zone instance**; to use standard and advanced editions, subscribe Joule again in another subaccount
- If both editions sit in one subaccount, the Joule site setting may look enabled on the other edition; **running Joule there is unsupported**
- **For a developer:** the 3,000 requests per minute limit matters for scripts, load tests and any custom client calling Joule APIs

## 28.5 Added by Claude, not from the sources
- The developer remark on the rate limit is my own
- I did not verify the "per user/tenant" wording beyond the printed sentence

---

## Screenshots and figures from the sources
- Pages 222 to 234 contain no kept screenshots (checked against the image list)

---

## Recap
- Multi-system: same IAS tenant, formation, one destination per system, content provider mapping, metadata
- Never re-run the booster for extra systems
- Good descriptions drive automatic selection
- Constraints: OIDC only, one Joule per Work Zone, 3,000 requests per minute

## Practice
- Which two steps of the single-system Private Edition setup do you skip for extra systems?
- Why does a blank screen appear with Okta and what fixes it?
- Why can't SAML and OIDC trust coexist on one IAS tenant, and what is the workaround?

---

## How this chapter was checked
- All 13 pages were read in full; names and values were compared with the page text

## Sources and further reading
- SAP Help Portal, *Integrating Joule with SAP Solutions* (PDF, pages 222 to 234): https://help.sap.com/doc/de3af3c0f81642dbaa4d36172ed57a72/CLOUD/en-US/79bfc83ab386450c8cd9c7937ce26a3a.pdf
- SAP Discovery Center, Joule missions: https://discovery-center.cloud.sap/missiondetail/4538/

---

*Previous: [Chapter 27: Document grounding, part 2](27-document-grounding-part-2-metadata-status-access-control-pricing.md)*
