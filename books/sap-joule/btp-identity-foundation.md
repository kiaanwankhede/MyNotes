# Joule's identity and platform foundation

*Before any agent, skill, or activation guide matters, Joule has to trust who's asking — and that trust lives entirely on SAP BTP.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the IAM architecture Joule depends on, why Joule onboarding requires OIDC specifically, what "a unified Joule instance" actually means, and how S/4HANA Private and Public Edition activation differ
> - **You will build:** nothing — this is the platform layer every later activation chapter assumes you already understand
> - **Level:** beginner · **Time:** about 15 minutes
> - **Builds on:** nothing — this is the first chapter in the book. **Leads to:** [Extending Joule beyond a single application](btp-extending-joule.md)

**After this chapter you can:**

- Name the three IAM pillars and the four SAP Cloud Identity Services that implement them
- Explain why Joule onboarding requires OIDC and rejects SAML-based trust
- Say what makes a Joule instance "unified" rather than per-application
- Walk through the four-step end-to-end setup flow
- Explain why SAP S/4HANA Cloud Private and Public Edition activation differ

## 1. IAM is the real dependency

Before anyone "turns on" Joule, implementation consultants have to verify identity and access management readiness — a unified Joule experience depends on a consistent IAM foundation, not a feature flag.

SAP's IAM model for SaaS rests on three pillars: **Authentication & SSO**, **Identity Lifecycle**, and **Authorization**, with **SAP Cloud Identity Services** as the central interface standardizing all three across SAP solutions.

![SAP IAM as the foundation for Joule: Application Clients authenticate through SAP Cloud Identity Services (Identity Authentication, Identity Directory, Identity Provisioning, Authorization Management), which connects to SuccessFactors, SAP BTP Applications (XSUAA-based and Cloud-Identity-based), Navigation Service, non-BTP SAP Cloud Products, and third-party identity providers](images/btp-1-iam-foundation.png)

SAP Cloud Identity Services bundles four services:

| Service | Role |
|---|---|
| **Identity Authentication (IAS)** | Authentication and SSO |
| **Identity Provisioning (IPS)** | Identity lifecycle management — provisioning/replication across apps |
| **Identity Directory** | Central user store |
| **Authorization Management** | Policies and authorization services |

> [!WARNING]
> **⚠️ Pitfall: Joule onboarding trust is OIDC-only**
> Enterprise SSO across a landscape can use SAML2 and/or OIDC broadly. The trust configuration for **Joule onboarding specifically** uses **OpenID Connect (OIDC)** — SAML-based trust is explicitly not supported for Joule trust setup. If your landscape is SAML-only, that's the first thing to fix, not a detail to discover mid-setup.

- **SAP BTP** is the platform layer: Joule is integrated and configured through BTP, including trust setup and running the **Joule Booster** (the provisioning tool), and managed via BTP's system landscape and formations.
- **SAP Build Work Zone** resolves intent-based navigation and consumes exposed content from SAP solutions, for navigational scenarios.
- The target **SAP product** must already be integrated with Identity Authentication, because Joule reuses that product's existing IAS setup for user login — it doesn't introduce a second one.

## 2. What makes a Joule instance "unified"

Joule setup offers one centralized, repeatable onboarding process instead of custom per-application setup. A **unified Joule setup** means:

- One Joule instance on SAP BTP (with dev/test/prod — or just test/prod if you don't need custom Joule Agents)
- Shared across multiple SAP cloud applications
- Backed by **one consistent** SAP Cloud Identity Services configuration

![Prerequisites for a unified Joule setup: SAP product and licensing prerequisites, SAP BTP prerequisites, identity prerequisites (mandatory for unified Joule)](images/btp-1-unified-prereqs.png)

Three prerequisite groups:

1. **SAP product and licensing** — a licensed SAP product that supports Joule (e.g. SuccessFactors, S/4HANA Cloud), running in an SAP data center, already integrated with Identity Authentication.
2. **SAP BTP** — an enterprise global account, with entitlements for **Joule and SAP Build Work Zone in the same global account**. Joule integrates with exactly one of three Work Zone editions: **Standard**, **Advanced**, or **SAP SuccessFactors Edition**.
3. **Identity (mandatory for unified Joule)** — every participating application must use the **same SAP Cloud Identity Services tenant**, with the **same Global User ID** (`user_uuid`) across all of them. Production systems share one production IAS tenant; non-production systems share one non-production tenant.

> [!IMPORTANT]
> **🏭 In production: different IAS tenants means different Joule instances, full stop**
> "Can I use different IAS tenants and still have unified Joule?" No. One IAS tenant per landscape tier (prod/non-prod) is the hard requirement — different tenants produce separate Joule instances, not a unified one. If your landscape isn't aligned yet, you *can* enable Joule per application anyway, but you've explicitly opted out of the unified model, not deferred it.

## 3. The end-to-end setup flow

The same four-step sequence applies across every Line of Business:

![End-to-end unified setup flow: 1) Prepare SAP BTP structure, 2) Verify identity setup, 3) Run the Joule onboarding (unified), 4) Enable Joule per line of business](images/btp-1-e2e-process.png)

```mermaid
flowchart LR
    S1["1. Prepare BTP structure\n(global account, subaccounts)"] --> S2["2. Verify identity\n(IAS, IPS, Global User ID)"]
    S2 --> S3["3. Run Joule onboarding\n(Joule Booster, central instance)"]
    S3 --> S4["4. Enable per LoB\n(SuccessFactors, S/4HANA, ...)"]
```

1. **Prepare SAP BTP structure** — a global account, optional directories for separation, one or more subaccounts where Joule will be provisioned.
2. **Verify identity setup** — confirm IAS integration, IPS availability, and consistent Global User ID mapping *before* onboarding, not after.
3. **Run the Joule onboarding (unified)** — provisioned once, creating a central Joule instance with associated integration systems. This is the prerequisite that every later LoB-specific enablement builds on top of — not a separate instance.
4. **Enable Joule per Line of Business** — SuccessFactors-, S/4HANA-, Concur-, etc.-specific steps, all building on the *same* instance from step 3.

Here's how that instance actually connects back to SAP systems once provisioned:

![Joule provisioning architecture: User via Application Clients, through Identity Authentication/Identity Provisioning (Trust/Annotation/Target), into the SAP BTP subaccount (Joule, Navigation Target Mapping, Capabilities, Destinations, Connectivity, SAP Build Work Zone), consuming SAP Solutions via OData API / CDM Provider (Content Exposure, Content Consumption, Back-end Data Access)](images/btp-1-provisioning-architecture.png)

- Inside the BTP subaccount, Joule reaches SAP Solutions through **Destinations and Connectivity** — the same secure-connectivity mechanism you'd use for any BTP app talking to a backend, not a Joule-specific channel.
- **Navigation Target Mapping** and **Capabilities** sit alongside Joule in the subaccount; **SAP Build Work Zone** is wired in for navigation resolution.
- Backend access flows through an **OData API** and a **CDM Provider** on the SAP Solutions side — content exposure and consumption are explicit, named flows, not implicit.

## 4. Private vs. Public Edition: why activation differs

Both S/4HANA Cloud editions need Joule + Build Work Zone entitlements in the global account and IAS configured — but how much of the setup is yours to manage differs sharply:

| | Private Edition | Public Edition |
|---|---|---|
| **Delivery model** | RISE with SAP, customer-managed infra | Multi-tenant SaaS, SAP-managed |
| **Network connectivity** | Customer sets up secure connectivity (e.g. **Cloud Connector**) | Not customer-configured |
| **Tenant/identity management** | Higher degree of customer-managed configuration | SAP manages tenant context and isolation — customers don't configure tenant identifiers |
| **Activation mechanism** | More manual: network, identity integration, content exposure, role design | Streamlined: relies heavily on the **Joule Booster** and SAP automation |
| **Role design** | Custom SAP Fiori roles needed: business catalogs, semantic objects, Fiori app IDs, target mappings | Largely handled by SAP's guided onboarding |

- If you're troubleshooting a Private Edition activation, the likely failure points are **trusted domains, Joule formations, Cloud Connector connectivity, or Identity Provisioning Service errors** — check those before anything else.

## 5. Added by Claude, not from the sources

- The "pick one of three Work Zone editions" framing is stated directly in the source; the observation that this is a hard one-to-one constraint (not "choose your favorite") is this book's emphasis.
- Not run: this chapter is architecture and setup guidance, not code — nothing here was independently executed.

## 6. Interview corner

**What interviewers listen for:** you know Joule's trust setup is OIDC-only (not a detail you'd guess), you can explain *why* a unified instance requires one IAS tenant rather than reciting it, and you know which edition of S/4HANA makes you own network connectivity.

### 🟢 Basic

<details class="qa"><summary>1. What are SAP Cloud Identity Services' four component services?</summary>

- Identity Authentication (IAS), Identity Provisioning (IPS), Identity Directory, Authorization Management

</details>

<details class="qa"><summary>2. Which protocol does Joule onboarding's trust configuration require?</summary>

- OpenID Connect (OIDC) — SAML-based trust is not supported for Joule trust setup specifically, even though the broader landscape may use SAML2 for other SSO

</details>

### 🟡 Intermediate

<details class="qa"><summary>3. A customer has two SuccessFactors tenants on two different IAS tenants and wants "one Joule" across both. What do you tell them?</summary>

- Not possible as stated — a unified Joule experience requires a single IAS tenant per landscape tier; two different IAS tenants produce two separate Joule instances
- *Stronger answer:* their options are to consolidate onto one IAS tenant, or accept two independent Joule instances (which is a valid but explicitly non-unified choice)

</details>

<details class="qa"><summary>4. What's the practical difference in setup effort between S/4HANA Private and Public Edition?</summary>

- Private Edition requires the customer to manage network connectivity (Cloud Connector), tenant-level configuration, and custom Fiori role design; Public Edition is SAP-managed for tenant/infrastructure and relies on the Joule Booster for a streamlined activation

</details>

### 🔴 Senior

<details class="qa"><summary>5. A Joule activation on S/4HANA Private Edition is failing intermittently. Where do you start investigating?</summary>

- The four named common failure areas: trusted domain configuration, Joule formations, Cloud Connector connectivity, and Identity Provisioning Service errors
- *Stronger answer:* verify the identity prerequisites first (same IAS tenant, correct Global User ID mapping) — a surprising number of "Joule bugs" are actually identity misconfiguration surfacing as functional issues, per the course's own emphasis on Global User ID correctness

</details>

> [!TIP]
> **🧩 Design question**
> *"A customer runs SuccessFactors (public cloud) and S/4HANA Private Edition on RISE, and wants one unified Joule experience across both."* Talk about: confirming both are on the same IAS tenant (not just "both use IAS"), consistent Global User ID mapping across both, the Private Edition's extra network/role-design burden (Cloud Connector, custom Fiori roles) that the Public-cloud SuccessFactors side won't need, and provisioning the unified instance once before doing either LoB-specific enablement.

## Cheat sheet

| Concept | One-line definition |
|---|---|
| SAP Cloud Identity Services | IAS + IPS + Identity Directory + Authorization Management |
| Joule trust protocol | OIDC only — never SAML |
| Unified Joule instance | One BTP-hosted instance, one IAS tenant per tier, same Global User ID everywhere |
| Joule Booster | SAP's provisioning automation for Joule onboarding |
| Private Edition burden | Network (Cloud Connector), tenant config, custom Fiori roles |
| Public Edition | SAP-managed tenant/infra, Joule Booster-driven |

## Recap

- Joule's real dependency is identity: three IAM pillars (Authentication/SSO, Identity Lifecycle, Authorization), standardized through SAP Cloud Identity Services
- Trust setup for Joule onboarding is **OIDC only** — SAML-based trust is explicitly unsupported there, even on SAML-capable landscapes
- A **unified** Joule instance requires one shared IAS tenant per tier and one consistent Global User ID — different tenants mean separate instances, not a design choice
- The setup flow is always: prepare BTP structure → verify identity → run Joule onboarding once → enable per LoB
- S/4HANA **Private** Edition pushes network, tenant, and role-design work onto the customer; **Public** Edition is SAP-managed and Joule-Booster-driven

## Practice

1. Without looking back, name the four SAP Cloud Identity Services and what each does
2. Explain out loud why "different IAS tenant per app" breaks the unified Joule model, using the Global User ID concept
3. Sketch the four-step end-to-end setup flow from memory

## How this chapter was checked

- Units 1 and 2 (4 lessons: Exploring Joule's Technical Architecture, Setting Up A Unified Joule Instance, Setting Up Joule for SAP S/4HANA Cloud Private Edition, Setting Up Joule for SAP S/4HANA Cloud Public Edition) and both unit quizzes of "Setting Up Joule Across your Organizational System Landscapes" were read in full, 10 Nov 2026.
- All 4 images across these lessons are used here (saved to `images/`, never hotlinked): the IAM foundation diagram, the unified-setup prerequisites diagram, the end-to-end process diagram, and the BTP provisioning architecture diagram. Nothing was left out.
- Nothing in this chapter is code; nothing was run.

## Sources and further reading

- SAP Learning, *Setting Up Joule Across your Organizational System Landscapes* — https://learning.sap.com/courses/setting-up-joule-across-your-organizational-system-landscapes, Units 1–2 (read in full 10 Nov 2026)

Previous: [SAP Joule book introduction](README.md) · Next: [Extending Joule beyond a single application](btp-extending-joule.md)
