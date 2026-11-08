# Chapter 5: Setting up Joule product by product

*The identity foundation, the unified instance, and what each SAP product adds on top.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** why identity is the real dependency, the unified-instance prerequisites and flow, and the per-product prerequisites (S/4HANA, SuccessFactors, Concur, Ariba, Signavio, IBP, IPD, Digital Manufacturing), plus Document Grounding, Analytical Insights, Joule for Developers, Work Zone and Mobile Start, Microsoft 365 Copilot and non-SAP apps
> - **You will build:** nothing yet; a prerequisite checklist per customer
> - **Level:** intermediate · **Time:** about 45 minutes
> - **Source:** SAP Learning course *Setting Up Joule Across your Organizational System Landscapes* (5 units, 17 lessons, 5 quizzes), read 8 November 2026 with all lesson images
> - **Builds on:** [Chapter 4](04-setting-up-joule.md) (landscape cases and services)

**After this chapter you can:**

- Name the three identity pillars and the four Cloud Identity Services parts
- Say which trust protocol Joule onboarding needs (and which it does not)
- List the prerequisites for a unified Joule instance
- Give the extra prerequisite that each product adds
- Explain how Joule reaches non-SAP applications, and what is not supported

> [!WARNING]
> **What this chapter is**
> - It is one SAP course plus one setup blog (5.4a). Most lessons are **short (prerequisites and links), not click-by-click steps**. The steps live in the linked Discovery Center missions and SAP Help pages.
> - No BTP account or Joule tenant was used.
> - Some points differ from [Chapter 4](04-setting-up-joule.md); see 5.8.

## 5.1 Identity is the real dependency

- Joule trusts your identity setup. If identity is not ready, onboarding fails or users are wrongly identified
- **Three IAM pillars:** authentication and single sign-on, identity lifecycle, authorization
- **SAP Cloud Identity Services has four parts:**
  - Identity Authentication (IAS)
  - Identity Provisioning (IPS)
  - Identity Directory
  - Authorization Management
- **Trust protocol:** Joule onboarding uses **OpenID Connect (OIDC). SAML-based trust is not supported** for it

> [!IMPORTANT]
> **Four components in every setup**
> - Cloud Identity Services, SAP BTP, SAP Build Work Zone (navigation service for intent-based targets and content), and the SAP solutions
> - The SAP solutions must **already be integrated with IAS**

**The architecture picture (lesson 1 image).**

- A user works in a mobile or desktop client
- Apps sit in different identity styles: SuccessFactors (customer-managed lifecycle), non-BTP SAP cloud products, BTP apps using XSUAA, BTP apps using IAS
- Cloud Identity Services sits in the middle, with authenticate, identity-lifecycle and group flows to each
- A third-party identity provider can sit in front of IAS
- The BTP navigation service receives role replicas

## 5.2 Readiness checks

- **One** Cloud Identity Services tenant for all products
- **One** Global User ID across all products in scope
- Identity lifecycle replicated with **SCIM2**
- `user_uuid` mapped to the Global User ID
- Trust: the IAS tenant domain matches the product's trust setup; trusted domains set for both IAS and BTP

**Onboarding order (lesson 1):**

1. Confirm prerequisites: licences, entitlements, IAS integration
2. Configure trust to IAS and the user attributes
3. Run the **Joule Booster** to create the formation
4. Configure trusted domains

## 5.3 A unified Joule instance

- **Unified Joule** = one instance on BTP, shared by many SAP cloud apps, on one consistent identity setup
- Landscape: dev, test and prod; **only test and prod if you have no custom agents**

**Prerequisites (lesson 2 image: three groups).**

| Group | What is needed |
|---|---|
| SAP product and licence | Licensed product, in an SAP data centre, already integrated with IAS |
| BTP | Enterprise global account; Joule and Build Work Zone entitlements **in the same global account** |
| Identity (mandatory for unified) | Same IAS tenant for all apps; Global User ID the same |

- **Work Zone editions:** one Joule can integrate with exactly **one** of Standard, Advanced or SuccessFactors Edition
- Production systems share one IAS **production** tenant; non-production systems share one non-production tenant
- A wrong Global User ID causes inconsistent user identification

```mermaid
flowchart LR
  A["1 Prepare BTP structure"] --> B["2 Verify identity setup"]
  B --> C["3 Run unified onboarding"]
  C --> D["4 Enable Joule per line of business"]
```

- **Step 1:** global account, optional directories, subaccounts
- **Step 2:** IAS, IPS, `user_uuid` mapped
- **Step 3:** provision once, then associate systems
- **Step 4:** each LoB builds on the same instance

**Course Q&A (lesson 2).**

- Different IAS tenants: separate Joule instances
- You can enable per application if tenants are not aligned, but that is not the unified model
- The core steps are common; each LoB has its own extras

**The architecture picture (lesson 2 image).**

- SAP solutions expose content (OData API, CDM provider) and Joule consumes it
- IAS and IPS sit between the solutions and the BTP subaccount (trust and assertion arrows)
- In the subaccount: Joule, navigation target mappings, capabilities, destinations, connectivity, Build Work Zone

## 5.4 SAP Cloud ERP

| | S/4HANA Cloud **Private** Edition | S/4HANA Cloud **Public** Edition |
|---|---|---|
| Who manages | Customer-managed config (RISE with SAP) | Multi-tenant SaaS; SAP manages lifecycle and isolation |
| Setup style | Network, identity, content exposure, role design done by the customer | Streamlined; relies on the **Joule Booster** |
| BTP | Global account with Joule and Build Work Zone entitlements | Enterprise global account, same entitlements, plus a prepared subaccount |
| Network | **Cloud Connector** (secure BTP link) | Not customer-managed |
| Admin access | BTP and S/4HANA | BTP |
| Tenant id | n/a | Customers do not configure tenant identifiers |

- Both need Build Work Zone **standard edition** in the BTP subaccount and IAS (IPS typically used)
- **Private Edition references:** SAP Community setup guide; common set-up issues (trusted domains, Joule formations, Cloud Connector, IPS errors); custom roles for Joule (business catalogs, semantic objects, Fiori app IDs, target mappings); SAP Note 3523238 (navigation and transaction features, enabled Fiori apps)
- **Public Edition references:** a Discovery Center mission and a setup guide (entitlements, trust, Booster, authorization propagation)

## 5.4a S/4HANA Cloud Public Edition: the setup steps

*Source: SAP Community blog *Joule in SAP S/4HANA Cloud Public Edition - Setup Guide* (SAP RIG team). It starts **after** the Joule Booster has run. Blog scope: a **greenfield** setup with new Joule activations.*

- **What Joule does in Public Edition:** quick navigation, instant insights on business data (for example purchase orders, outbound deliveries), and help that summarises enablement content
- **Setup is per tenant:** it cannot be transported, so repeat it on test, then on production (SAP recommends test first)
- **Blog prerequisites:** Joule service, Build Work Zone standard edition (foundation or standard plan), Cloud Foundry, an admin role, and Cloud Identity Services tenant linked to the subaccount
- **Support component** for problems: `CA-FLP-EXT-JOU`

**Step 1: check what the Booster created.**

- Work Zone **provider ID** (Channel Manager shows the S/4HANA content provider; note the ID for IPS later)
- **Destination certificates** in BTP Connectivity
- **Four destinations** made by the Booster: S/4HANA SSO, Joule design time, Joule run time (default), Joule run time (data)
- **One destination you create yourself:** `NavigationService` (name is case-sensitive)
  - Type HTTP, proxy Internet, authentication `OAuth2UserTokenExchange`
  - URL, client ID, client secret and token URL come from the Work Zone service key (`portal-service` URL, `uaa` values)
  - Token service URL type Dedicated; enable "Use default JDK trust store"
- **Communication arrangements** in S/4HANA: `SAP_COM_0882` and `SAP_COM_0647`, linked to the destination certificates
- **Cloud Identity Services:** applications `das-ias` and `document grounding` exist
  - If the system uses another identity provider (Entra, Okta), set the same conditional authentication for `das-ias` so Joule reuses the session

**Step 2: prepare S/4HANA content.**

- **Content exposure (`SAP_COM_0647`):** Exposure Role Selection is usually "All"
  - With "All", SAP advises **no more than 3000 apps per role, group or catalog** (SAP Note 3107801 covers refresh errors)
  - Or switch to selection and mark each role "Exposed to BTP" in *Maintain Business Roles*
- **`SAP_COM_0193` (for IPS to read users and role assignments):**
  1. Create a communication user (blog uses Basic authentication; certificates also work; password at least 20 characters)
  2. Create a communication system for the S/4HANA system (host name without `https://`)
  3. Add the user under inbound communication
  4. Create the arrangement (the blog names it `Joule_Communication_0193`)
  5. Link the system and user in the arrangement
- **Content Security Policy:** add the Joule service URL under *Manage Content Security Policy*, trusted sites, `UI_RESOURCE_SCRIPTS`, "Managed by Customer"

**Step 3: Identity Provisioning (IPS) in Cloud Identity Services.**

- Add the S/4HANA system as a **trusted domain** first
- Create a **source system** (S/4HANA) and a **target system** (Identity Authentication and Build Work Zone)
  - The blog attaches JSON templates (rename the `.txt` files to `.json`)
  - Source properties: API URL from the `SAP_COM_0193` arrangement, and the communication user
  - Add the filter `cFLGExposure eq true` **only** if role selection is set to selected roles
  - Target properties: `cflp.providerId`, token URL, `portal-service` URL, client ID as user, client secret as password
  - If you hit authorization problems, give the subaccount user the `Launchpad_admin` role
- Refresh the Work Zone content channel, then run the source system **Read Job** ("Run Now")
- Check **Provisioning Logs** for user and group statistics
- **Schedule the job**: users, groups and roles must stay in sync with Work Zone

**Step 4: test.** Open Joule with the diamond icon and ask, for example, "Show purchase orders". The blog also lists SAP Note 3545050 (business objects enabled for Joule).

**What the screenshots add (all 43 body images viewed).**

- **Landscape picture, 7 numbered steps at runtime:**
  1. User starts on the solution home page
  2. User authentication (Identity Authentication)
  3. User starts the Joule UI
  4. Joule dialog handling (Joule Assistant and capabilities)
  5. Transactional: data access (through destination and connectivity service to the OData service)
  6. Navigational: link resolving (through Build Work Zone and the content channel)
  7. Search: help and customer documents (Document Grounding, with Microsoft SharePoint shown as the document source)
  - Dashed lines are config and design time (content exposure, CDM design-time access); solid lines are end-user runtime
- **Five-box flow** for the `SAP_COM_0193` part: create communication user, create communication system, assign the user to the system, create the arrangement, activate it
- **Role collections** shown on the admin user: Connectivity and Destination Administrator, Destination Administrator, `Launchpad_Admin`, Subaccount Administrator
- **Subscriptions screen:** Joule and Build Work Zone standard edition both show plan "foundation"
- **Joule service URL:** opening it in a browser shows "The service is up and running"; this is the URL you paste into the content security policy
- **`SAP_COM_0193`** is labelled "Identity Provisioning Integration" in the scenario list
- **Final test:** Joule opens as a side panel with "How can I guide you?" and suggested prompts; "show purchase orders" returns a list of orders
- **Dated:** the screenshots come from a demo tenant created in **September 2024**; screens may look different now

> [!IMPORTANT]
> **Why this matters:** the course lesson (5.4) only says "use the Booster". This blog shows what the Booster leaves for you: the `NavigationService` destination, the `SAP_COM_0193` arrangement, the content security policy and the IPS source and target systems.

## 5.5 Lines of business

> [!TIP]
> **Rule from the course:** activating Joule for a LoB is **not** a repeat of platform setup. Joule is provisioned centrally; its behaviour is set locally by the business system. Joule always acts within the user's existing authorizations.

| Product | What Joule does there | Extra prerequisites |
|---|---|---|
| **SuccessFactors** | Embedded; BTP service; HR system of record unchanged | Joule (`das-application`) entitlement; Build Work Zone standard / SAP Start; licence and Joule data-centre availability; active Cloud Identity tenants |
| **Concur** | Conversational expense and travel (create and edit expense reports, view details, attendees) | Guide and SAP Help security-integration page (identity, trust, entitlement) |
| **Ariba** | Augments procurement workflows; does not replace the UI | Joule Base or Premium entitlement; BTP and Cloud Identity access; admin roles in BTP, Cloud Identity and Ariba Realms; Cloud Identity configured for Ariba logon (else a third-party user in the Realm) |
| **Signavio Process Transformation Suite** | Informational, navigational and transactional patterns over process content | Joule entitlements (a $0 order exists in SAP Store if you have no licence); Cloud Identity Services; Work Zone "planned for next release, not required" |
| **Integrated Business Planning (IBP)** | Answers from IBP documentation and selected interactions; scope depends on configuration and entitlement | Base or Premium entitlement; admin roles in BTP, Cloud Identity and IBP |
| **Integrated Product Development (IPD)** | Summarised answers grounded in IPD docs on SAP Help; navigation | Joule entitlement in the same global account (Cloud Foundry) as IPD; **Common Functions** SaaS subscribed; **OIDC** identity provider (migrate from SAML); `EPD Admin` role template for the admin |
| **Digital Manufacturing** | Manufacturing information inside the app; system of record unchanged | Joule entitlement in the same global account as Digital Manufacturing; subscription to it; all Joule onboarding requirements |

- SuccessFactors is the **reference scenario**: SaaS embedding, identity at runtime, navigation and transactions in a real context
- Guided help: Discovery Center missions (they automate parts of setup with BTP tooling)

## 5.6 Advanced capabilities

- **Document Grounding:**
  - Joule answers from your own documents (policies, manuals, procedures)
  - Documents are **not training data**; content is retrieved at runtime
  - Answers follow existing authorizations and the latest document version
- **Document Grounding with Contextualization:**
  - Adds **metadata** (application, business domain, classification)
  - Joule narrows retrieval to documents matching the user's context
  - Better precision at scale; access rules unchanged
- **Analytical Insights:**
  - Natural-language questions answered from governed analytical models
  - Setup integrates Joule with **SAP Analytics Cloud**
  - Results can be charts or key figures, not only text
- **Joule for Developers:**
  - Design-time AI for SAP Build (Build Code, Build Apps, Build Process Automation) and ABAP Cloud
  - Explains code, completes code, generates unit tests, chat assistance
  - Also available in S/4HANA Cloud Public Edition for ABAP Cloud, within released APIs and extension points
  - **Not** a runtime feature for end users
  - The course says it is a **promo SKU until Sep 2026**, so it does not show in BTP entitlements

## 5.7 Work Zone, Mobile Start, Microsoft 365 and non-SAP apps

- **Work Zone and Mobile Start:**
  - Work Zone = role-based launchpad across systems; Mobile Start reuses its site and identity setup
  - Joule can resolve intents across systems and navigate users to authorized apps
  - Prerequisites: unified Joule already on BTP; Work Zone standard in the same subaccount; systems already exposing navigation content; consistent Cloud Identity
- **Microsoft 365 Copilot (bi-directional):**
  - Access Joule from Copilot, starting with **Teams**
  - The answer says whether Joule or Copilot produced it
  - Prerequisites: licensed Copilot, Joule already active, identity alignment, secure network and trust
  - **Opt-in**; not on by default for either side
- **Non-SAP applications:**
  - Joule is embedded only in SAP apps that support it; for others it is **extended**
  - **Approach 1, Joule Studio:** skills call non-SAP APIs; agents orchestrate across systems; Joule Studio CLI for pro-code; Joule stays the interface and the non-SAP system is the back end (via destinations and action projects)
  - **Approach 2, WalkMe and the Joule Action Bar:** an overlay across SAP and non-SAP web apps using screen context; proactive help; routed through SAP-managed services
  - **Not supported:** a public Joule REST API; non-SAP apps hosting Joule; direct LLM access outside SAP-managed contexts; identity delegated to non-SAP systems

| Need | Use |
|---|---|
| Call a non-SAP API | Joule Studio |
| Cross-system workflow | Joule Studio agents |
| AI help across several web apps | WalkMe and Action Bar |
| Experience without embedding | WalkMe |
| Back-end automation | Joule Studio skills |

## 5.7a Discovery Center missions the lessons link to

*Links taken from the lesson pages. I did not open the missions (see "How this chapter was checked").*

| Topic | Mission |
|---|---|
| Unified Joule instance | [Mission 4538](https://discovery-center.cloud.sap/missiondetail/4538/) |
| S/4HANA Cloud Public Edition | [Activate Joule with SAP S/4HANA Cloud Public Edition](https://discovery-center.cloud.sap/missiondetail/4452/4738/) |
| SuccessFactors | [Activate Joule for SAP SuccessFactors](https://discovery-center.cloud.sap/missiondetail/4451/4737/) |
| Ariba | [Activate Joule with SAP Ariba](https://discovery-center.cloud.sap/missiondetail/4697/?tab=overview) |
| Integrated Business Planning | [Mission for SAP IBP](https://discovery-center.cloud.sap/missiondetail/4631/4920/) |
| Build Work Zone and Mobile Start | [Activate Joule with SAP Build Work Zone and SAP Mobile Start](https://discovery-center.cloud.sap/missiondetail/4649/4938/) |
| Microsoft 365 Copilot | [Activate Joule with Microsoft 365 Copilot](https://discovery-center.cloud.sap/missiondetail/4741/5025/) |
| Custom skills for SAP and non-SAP systems | [Mission 4643](https://discovery-center.cloud.sap/missiondetail/4643/) |

- The Private Edition, Concur, Signavio, IPD, Digital Manufacturing, Document Grounding, Analytical Insights and Joule for Developers lessons link to Community guides or SAP Help instead, not to a Discovery Center mission

## 5.8 Added by Claude, not from the sources

*My own reasoning; the course does not say it.*

- **Checklist order for a customer:** identity first (one IAS, one Global User ID, OIDC), then BTP (same global account, Work Zone edition), then product extras
- **Quick test:** open the Global User ID of one user in every product; if they differ, stop and fix identity before onboarding
- **Ask early:** "Is any product's identity provider SAML-only?" (it blocks IPD and Joule trust)
- **Differs from Chapter 4:** the Chapter 4 blog says Build Work Zone *foundation* edition is included with Joule; these lessons say *standard* edition (and SuccessFactors Edition or Advanced for unified). Confirm the edition with SAP before ordering
- **Plan around the missing steps:** keep a link list of the Discovery Center mission for each product, since this course gives only prerequisites

## 5.9 Interview corner

**What interviewers listen for:** you start with identity, you know the same-global-account rule, and you can say what is **not** supported.

<details class="qa"><summary>🟢 1. Which trust protocol does Joule onboarding need?</summary>

- OpenID Connect (OIDC); SAML-based trust is not supported

*Stronger answer:* mention IPD also needs an OIDC identity provider and offers a migration guide from SAML.
</details>

<details class="qa"><summary>🟢 2. What is the mandatory identity prerequisite for a unified Joule?</summary>

- All apps share the same Cloud Identity Services tenant, with the same Global User ID

*Stronger answer:* production systems share one production tenant, non-production share one non-production tenant.
</details>

<details class="qa"><summary>🟡 3. What does Joule do differently in Private and Public S/4HANA Cloud?</summary>

- Private: customer-managed network (Cloud Connector), identity, content exposure and role design
- Public: multi-tenant SaaS; the Joule Booster automates most of it

*Stronger answer:* in Public, tenant identifiers are not customer-configured.
</details>

<details class="qa"><summary>🟡 4. How do you keep Joule from exposing data users should not see?</summary>

- Joule runs inside the product's authorizations; it does not bypass them
- Identity and authorization are never delegated to non-SAP systems

*Stronger answer:* name Concur and Ariba as examples where Joule works "in the context of the user's existing permissions".
</details>

<details class="qa"><summary>🔴 5. A customer wants Joule inside a non-SAP web app. What can you offer?</summary>

- Joule Studio (skills and agents calling the app's APIs) or WalkMe with the Joule Action Bar (overlay)
- Say clearly: no public Joule API, no native hosting

*Stronger answer:* explain which approach changes the user's interface and which changes the back end.
</details>

<details class="qa"><summary>🔴 6. Two IAS tenants exist across the customer's systems. What happens?</summary>

- Separate Joule instances, not the unified model
- You may still enable Joule per application

*Stronger answer:* link back to [Chapter 4](04-setting-up-joule.md) Case 2 (no cross-instance answers).
</details>

> [!TIP]
> **🧩 Design question**
> A customer runs SuccessFactors, Ariba and IPD. SuccessFactors and Ariba use one IAS tenant; IPD's identity provider uses SAML.
> - **Sketch:** the identity path for each product and where Joule instances sit.
> - **Say out loud:** what must change before IPD joins the unified Joule.

## 5.10 Quiz review

*These are my reading of the answers; SAP gives no answer key in the text I read.*

| Unit | Pass mark | Answers (by my reading) |
|---|---|---|
| 1 Architecture and setup (3 questions) | 3 | OIDC; same Cloud Identity Services tenant; SAP Build Work Zone |
| 2 Cloud ERP (3) | 3 | Cloud Connector; SAP Joule and Build Work Zone standard edition; Public is multi-tenant SaaS managed by SAP |
| 3 Lines of business (8) | 7 | Runs on SAP BTP; operates within the user's existing permissions; conversational access to documentation and navigation; Discovery Center mission; Joule entitlement in the same global account; augments workflows conversationally; Cloud Identity Services and Joule entitlements; OpenID Connect |
| 4 Advanced capabilities (5) | 4 | Context-aware help in ABAP tools; unit test generation; metadata filtering; natural-language questions and insights inside workflows; content retrieved at runtime |
| 5 Extending Joule (4) | 3 | Explicit opt-in; unified Joule instance on BTP; Microsoft Teams; omnipresent overlay with screen-level context |

## 5.11 Cheat sheet

| Topic | Remember |
|---|---|
| Trust | OIDC only; no SAML for Joule onboarding |
| Identity | One Cloud Identity tenant, one Global User ID, SCIM2 lifecycle |
| Entitlements | Joule and Build Work Zone in the same global account as the product |
| Work Zone | One Joule per one edition (Standard, Advanced or SuccessFactors) |
| Private S/4HANA | Cloud Connector, customer-managed |
| Public S/4HANA | Joule Booster |
| IPD | Common Functions, OIDC, `EPD Admin` |
| Document Grounding | Retrieval at runtime; not training data |
| Non-SAP | Joule Studio or WalkMe; no public Joule API |
| Microsoft 365 | Opt-in; starts in Teams |

## Recap

- Identity decides whether setup works: OIDC, one tenant, one Global User ID
- Unified Joule is provisioned once and extended per product
- Each product adds a few prerequisites; Joule never bypasses its authorizations
- Document Grounding, Analytical Insights and Joule for Developers are separate add-ons
- Non-SAP apps are reached by extension, not embedding

## Practice

1. Write the identity checklist you would run before onboarding.
2. For SuccessFactors plus IPD, list every prerequisite from 5.5.
3. Explain Private versus Public S/4HANA setup in four bullets.
4. Choose Joule Studio or WalkMe for three customer requests.

## How this chapter was checked

- **Read fully:** all 17 lessons (text and every image: lesson 1 has 1, lesson 2 has 3, the other 15 have none) and all 5 unit quizzes
- **Not read:** the Discovery Center missions (links added in 5.7a, not opened), SAP Community guides, SAP Help pages, SAP Note 3523238, SAP Note 2791410, the Architecture Center page and the WalkMe page the lessons link to; the lesson-1 video and any demos on the course page
- **Setup blog (5.4a):** text and all 43 body images read (37 screenshots and diagrams, 6 small pointer icons or dialogs); the two attached JSON templates and the demo video are **not read**
- **Not run:** no BTP account or Joule tenant was used; quizzes not submitted
- **Dated points:** Joule for Developers "promo SKU until Sep 2026" is past that date today; Signavio's Work Zone note says "planned for next release"; check SAP Help

## Sources and further reading

- SAP Community blog, *Joule in SAP S/4HANA Cloud Public Edition - Setup Guide* (text and all screenshots read): https://community.sap.com/t5/technology-blog-posts-by-sap/joule-in-sap-s-4hana-cloud-public-edition-setup-guide/ba-p/13965333
- Discovery Center missions: see 5.7a
- SAP Learning, *Setting Up Joule Across your Organizational System Landscapes* (all lessons, images and quizzes read): https://learning.sap.com/courses/setting-up-joule-across-your-organizational-system-landscapes

---

*Previous: [Chapter 4: Setting up Joule](04-setting-up-joule.md)*
