# Enabling Joule for other SAP products

*Six products, the same architecture every time — what actually changes per product is narrow enough to fit in one table.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** what's specific to activating Joule in SAP Concur, Ariba, Signavio, Integrated Business Planning, Integrated Product Development, and Digital Manufacturing
> - **You will build:** nothing — activation prerequisites and scope, not a code tutorial
> - **Level:** beginner · **Time:** about 10 minutes
> - **Builds on:** [Enabling Joule for SAP SuccessFactors](enabling-successfactors.md) (the architecture pattern). **Leads to:** nothing specific — this closes out the product-by-product activation chapters

**After this chapter you can:**

- Activate-level recognize what's common vs. product-specific across six more SAP products
- Name each product's distinguishing Joule capability in one sentence
- Spot the one product in this set with a notably different grounding mechanism (official docs, not live data)

## 1. What's common, stated once

Every product below follows the same architecture from [the SuccessFactors chapter](enabling-successfactors.md): Joule is embedded in the product's UI, runs as a BTP service, augments rather than replaces the product's own functionality, and every action is governed by the product's existing authorizations. None of that is repeated per product below — only what's actually distinct.

Common prerequisite, repeated across all six: a **Joule entitlement in the same SAP BTP global account** as the product's own entitlement, plus SAP Cloud Identity Services configured.

## 2. Product by product

| Product | What Joule does there | Distinguishing detail |
|---|---|---|
| **SAP Concur** | Conversational spend management — create/edit expense reports, view expense details, work with attendees | Pure transactional/informational scope — no unique identity wrinkle |
| **SAP Ariba** | Embedded conversational experience in procurement workflows | Needs SAP Ariba **Realms**-level identity: Cloud Identity Services should be configured with Ariba for logon, or a third-party Ariba Realm user is required as a workaround |
| **SAP Signavio Process Transformation Suite** | Conversational access to process content and insights — informational, navigational, and transactional patterns | SAP Build Work Zone is **not required yet** here — planned for a future release |
| **SAP Integrated Business Planning (IBP)** | Conversational access to planning documentation and selected system interactions | Scope is explicitly described as **still evolving** — don't assume today's capability set is final |
| **SAP Integrated Product Development (IPD)** | Conversational Q&A grounded in **SAP Help Portal documentation** for IPD applications and processes | The one product here where grounding is against official docs, not live product data; also requires subscribing to the **Common Functions SaaS application** and assigning the **EPD Admin role template** |
| **SAP Digital Manufacturing** | Conversational access to manufacturing execution and shop-floor-adjacent information | Digital Manufacturing stays system of record for production data; Joule is purely an interaction layer on top |

> [!WARNING]
> **⚠️ Pitfall: SAP Integrated Product Development requires OIDC, explicitly**
> IPD's own prerequisites restate the OIDC requirement from [the identity foundation chapter](btp-identity-foundation.md) directly: *"Your identity provider uses the OpenID Connect protocol. If you currently use a SAML protocol,"* a linked migration guide is the next step. This isn't a generic platform note here — it's called out per-product because IPD activation will simply fail on a SAML-only identity provider.

## 3. Reading the pattern itself

Notice what's **not** in this table: UI screenshots, step-by-step configuration, or code. That's accurate to the source — each of these six lessons is a short prerequisites-and-references page pointing to a SAP Discovery Center mission or SAP Community setup guide for the actual configuration steps. The teaching value here is the *pattern recognition*: once you've internalized "embedded UI, BTP service, local authorizations, same-global-account entitlement," evaluating a seventh product SAP adds tomorrow is mostly a matter of checking which of the distinguishing details above (if any) applies to it.

## 4. Added by Claude, not from the sources

- The "what's common, stated once" structure in section 1 is this book's own compression of six repetitive lessons into one table — the underlying facts are the source's.
- The closing observation in section 3 (why this chapter stays a table instead of six full write-ups) is editorial, reflecting what the source actually contains rather than padding it out.
- Not run: this chapter is prerequisite/scope guidance; nothing was independently executed.

## 5. Interview corner

<details class="qa"><summary>1. What's the one shared prerequisite across all six products in this chapter?</summary>

- A Joule entitlement in the same SAP BTP global account as the product's own entitlement, plus SAP Cloud Identity Services configured

</details>

<details class="qa"><summary>2. Which product in this set grounds Joule against documentation rather than live application data?</summary>

- SAP Integrated Product Development (IPD) — grounded against SAP Help Portal content for IPD applications and processes

</details>

<details class="qa"><summary>3. A SAP Ariba activation is failing at the identity step. What's the Ariba-specific thing to check?</summary>

- Whether Cloud Identity Services is actually configured with Ariba for user logon at the Realm level — if not, a third-party user in that Ariba Realm is required as the workaround
- *Stronger answer:* this is more granular than the general "same IAS tenant" rule from the platform chapter — Ariba's Realm concept is a product-specific identity layer on top of that

</details>

<details class="qa"><summary>4. Why might SAP Build Work Zone not be a blocking prerequisite for a Signavio activation today?</summary>

- Because the Signavio lesson explicitly states Work Zone integration is planned for a future release, not required now — a detail that could easily be wrongly assumed required by analogy with every other product in this book

</details>

> [!TIP]
> **🧩 Design question**
> *"A customer wants to roll out Joule to Concur, Ariba, and IPD in one project, in that order."* Talk about: Concur as the lowest-friction one to start with (no unusual identity wrinkle), Ariba needing the Realm-level identity check before activation can even begin, and IPD needing both the Common Functions SaaS subscription and explicit OIDC confirmation — sequencing the project around whichever product's prerequisites take longest to clear, not necessarily the order requested.

## Cheat sheet

| Product | One thing to remember |
|---|---|
| Concur | Spend management, straightforward |
| Ariba | Realm-level identity config required |
| Signavio | Work Zone not required yet |
| IBP | Scope still evolving |
| IPD | Grounds on docs, not live data; needs Common Functions SaaS + EPD Admin role; OIDC mandatory |
| Digital Manufacturing | Pure interaction layer over shop-floor data |

## Recap

- All six products share one architecture (embedded UI, BTP service, local authorizations) and one entitlement rule (Joule + product entitlement, same global account)
- What differs is narrow: Ariba's Realm-level identity requirement, Signavio's not-yet-required Work Zone, IBP's evolving scope, IPD's documentation-based grounding plus Common Functions SaaS + EPD Admin role, and an explicit OIDC requirement called out specifically for IPD
- Recognizing the shared pattern matters more than memorizing six separate setups — it's what lets you evaluate the next product SAP adds

## Practice

1. Without looking back, name which of these six products needs Realm-level identity configuration
2. Explain in one sentence why IPD's grounding mechanism differs from every other product in this chapter
3. Pick two of these six and compare their activation prerequisites side by side

## How this chapter was checked

- The remaining 6 lessons of Unit 3 (SAP Concur, SAP Ariba, SAP Signavio Process Transformation Suite, SAP Integrated Business Planning, SAP Integrated Product Development, SAP Digital Manufacturing) from "Setting Up Joule Across your Organizational System Landscapes" were read in full, 10 Nov 2026 (SuccessFactors, the 7th lesson in this unit, has its own chapter).
- No images appeared in any of these 6 lessons — none were skipped.
- Nothing in this chapter is code; nothing was run.

## Sources and further reading

- SAP Learning, *Setting Up Joule Across your Organizational System Landscapes* — https://learning.sap.com/courses/setting-up-joule-across-your-organizational-system-landscapes, Unit 3 (SAP Concur, SAP Ariba, SAP Signavio, SAP IBP, SAP IPD, SAP Digital Manufacturing lessons; read in full 10 Nov 2026)

Previous: [Enabling Joule for SAP S/4HANA Cloud Public Edition](enabling-s4hana-public-edition.md)
