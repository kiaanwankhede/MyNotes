# Reference: Current facts to re-check

*Prices, SKUs, counts, free offers and release changes go out of date fast. This page lists every one the book relies on, with the date it was last checked and the chapter that uses it, so a re-check means opening one page.*

> [!NOTE]
> **📍 At a glance**
> - **Use it for:** checking before you quote a number to a customer or in an exam answer
> - **What it is:** a summary of facts already in the chapters; each was web-checked when its chapter was written
> - **Level:** reference
> - **Last checked:** 21 Nov 2026

## 35.1 How to re-check

1. Open the chapter's source for the fact (listed in that chapter's *Sources*).
2. If the value changed, update the chapter first, then the row here.
3. Update the chapter's *Last checked* line in its at-a-glance box.

> [!TIP]
> **When to re-check**
> - Before quoting any price, SKU or limit to a customer.
> - After SAP Sapphire (May) and TechEd (autumn), when SAP announces most changes.
> - At each AI-unit or BTP contract renewal.

## 35.2 Prices and SKUs

| Fact | Value | Checked | Chapter |
|---|---|---|---|
| AI units: SKU and purchase | SKU 8019164; yearly, in blocks of 100 (minimum 100); unused units expire after 12 months | 20 Nov 2026 | [16.6](joule-for-consultants.md), [18.8](joule-family.md) |
| AI unit price | SAP's list example €7; contracts can differ | 20 Nov 2026 | [16.6](joule-for-consultants.md) |
| Joule for Consultants | 35 AI units per user per month; 22,900 pooled requests per user; overage 2 AI units per 1,000 requests | 20 Nov 2026 | [16.6](joule-for-consultants.md) |
| Joule agents | 0.02 AI units per action (standard), 0.05 (advanced) | 20 Nov 2026 | [18.8](joule-family.md) |
| Document grounding | 0.005 AI units per record; one record is a started 50-MB block | 21 Nov 2026 | [32.5](joule-integration-other-sap-solutions.md) |
| Joule Base | USD 0 with an integrating SAP cloud subscription; SKU 8019544 | 20 Nov 2026 | [18.8](joule-family.md) |
| Partner test licence | TDD Joule Base, SKU 8020592 | 21 Nov 2026 | [19.2](joule-studio-classic.md) |
| Joule for Developers, ABAP | free licence on request: SKU 8019124 (customers), 8019541 (partners) | 20 Nov 2026 | [18.8](joule-family.md) |
| Business Application Studio, standard | EUR 28 per user per month (BTPEA list price) | 20 Nov 2026 | [9.6](btp-directories-tiers-commercial-models.md) |
| Cloud Foundry in consumption accounts | default runtime-memory quota of 200 GB per subaccount; you pay for memory used | 20 Nov 2026 | [8.3](btp-subaccount-walkthrough.md), [9.6](btp-directories-tiers-commercial-models.md) |

## 35.3 Free offers and end dates

| Fact | Value | Checked | Chapter |
|---|---|---|---|
| Joule Studio | authoring free with no end date; production runtime billed on consumption (the course handbook said runtime free until 31 Dec 2026) | 20 Nov 2026 | [18.8](joule-family.md) |
| Joule for Developers | free offer; SAP's page shows no end date (the course handbook said Q3 2026) | 20 Nov 2026 | [18.8](joule-family.md) |
| AI quota in Business Application Studio | free quota in SAP Build Code and SAP Build ends 31 Dec 2026; bring your own key from 1 Jan 2027 | 21 Nov 2026 | [30](tutorial-joule-bas-full-stack-cap.md) |
| Generative AI features in Joule Studio | deprecated; no longer available from January 2027 | 21 Nov 2026 | [19.1](joule-studio-classic.md) |

## 35.4 Counts and quotas

| Fact | Value | Checked | Chapter |
|---|---|---|---|
| Released Joule Assistants and Agents | 44 assistants, 327 agents (SAP Discovery Center) | 21 Nov 2026 | [18.5](joule-family.md), [11.1a](sap-ai-landscape.md) |
| Deployed capabilities in Joule Studio | 100, seen in the course tenant; not stated in SAP Help | 21 Nov 2026 | [19.3](joule-studio-classic.md) |
| SuccessFactors registration token | valid 7 days, for one system | 21 Nov 2026 | [31.2](joule-integration-successfactors.md) |
| Document grounding certificate | service key valid 365 days | 21 Nov 2026 | [32.5](joule-integration-other-sap-solutions.md) |
| S/4HANA Public Edition rate limit | 3,000 Joule requests per minute per tenant (SAP's 2024 guide) | 21 Nov 2026 | [32.3](joule-integration-other-sap-solutions.md) |
| SAP certifications | valid 12 months; *Stay Certified* in the 90 days before expiry adds 12 months | 21 Nov 2026 | [12.2](sap-ai-careers-certifications.md) |
| Refresh token in a subaccount | default 7 days (604,800 s) | 20 Nov 2026 | [7.5a](btp-users-role-collections.md) |

## 35.5 Release changes that alter the steps

| Change | Effect | Checked | Chapter |
|---|---|---|---|
| Joule 2506 | SAP Build Work Zone required for SAC analytical insights; older setups redone | 21 Nov 2026 | [29](tutorial-joule-sac-analytical-insights.md) |
| SAC 2026.4 / Q2 2026 | Joule-privilege role and team changes re-imported automatically (after one manual refresh) | 21 Nov 2026 | [29](tutorial-joule-sac-analytical-insights.md) |
| Joule setups after 13 Oct 2025 | no manual NavigationService destination | 21 Nov 2026 | [29](tutorial-joule-sac-analytical-insights.md) |
| Joule setups after 13 Oct 2026 (SuccessFactors) | `LPS_SFSF_*` and `SFSF_SSO` destinations managed in the backend | 21 Nov 2026 | [31](joule-integration-successfactors.md) |
| S/4HANA Public Edition 2602 SP06 | Joule icon role-based by default for new arrangements | 21 Nov 2026 | [32.3](joule-integration-other-sap-solutions.md) |
| SAML trust in BTP | SAP strongly recommends OIDC; some services refuse SAML | 20 Nov 2026 | [10.5](btp-identity-trust-federation.md) |
| SuccessFactors API Basic Authentication | deprecated; move to certificates | 21 Nov 2026 | [31.2](joule-integration-successfactors.md) |

## How this page was built

- Compiled on 21 Nov 2026 by scanning all 32 chapters for prices, SKUs, counts, dates and limits, outside the interview sections.
- No new sources: every value is copied from its chapter, with the date that chapter checked it.

## Sources

- The chapters linked in each row, and their *Sources* sections.

Previous: [Reference: Glossary](reference-glossary.md) · Next: [BTPAI book introduction](README.md)
