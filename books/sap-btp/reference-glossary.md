# Reference: Glossary

*The acronyms and terms used in this book, in one line each, with the chapter that explains them.*

> [!NOTE]
> **📍 At a glance**
> - **Use it for:** looking up a term while you read; the chapter number links to the full explanation
> - **What it is:** a summary of what the book already says; no new sources
> - **Level:** reference
> - **Last checked:** 21 Nov 2026

## 11.1 Acronyms

| Term | Meaning | Chapter |
|---|---|---|
| **ABAP** | SAP's programming language; on BTP also an environment (SAP BTP, ABAP environment) | [8](btp-subaccount-walkthrough.md) |
| **BDC** | SAP Business Data Cloud: SAP's data offering (Datasphere, SAC and more) | [2](sap-cloud-journey-btp-landscape.md), [SAP AI 1](../sap-ai/sap-ai-landscape.md) |
| **BTP** | SAP Business Technology Platform, SAP's PaaS | [1](cloud-computing-service-models.md), [2](sap-cloud-journey-btp-landscape.md) |
| **BTPEA / CPEA** | Prepaid consumption contracts for BTP: you buy credits upfront | [9](btp-directories-tiers-commercial-models.md) |
| **ECC** | SAP ERP Central Component, the on-premise ERP before S/4HANA | [2](sap-cloud-journey-btp-landscape.md) |
| **IaaS / PaaS / SaaS** | Rent the hardware / also the platform / the finished application | [1](cloud-computing-service-models.md) |
| **IAS** | Identity Authentication: SAP's login service in Cloud Identity Services | [10](btp-identity-trust-federation.md) |
| **IDS** | Identity Directory: the user store in Cloud Identity Services | [10](btp-identity-trust-federation.md) |
| **IPS** | Identity Provisioning: copies users and groups from a source system to a target | [10](btp-identity-trust-federation.md), [SAP Joule 19.5](../sap-joule/reference-joule-setup-building-blocks.md) |
| **OIDC** | OpenID Connect: the token-based trust protocol, preferred over SAML for BTP trust | [10](btp-identity-trust-federation.md) |
| **PAYG** | Pay-As-You-Go: BTP billed monthly for what you use, no upfront commitment | [9](btp-directories-tiers-commercial-models.md) |
| **RISE / GROW** | SAP's cloud offers: RISE for existing ERP customers moving to S/4HANA Cloud (usually Private Edition); GROW for new customers starting on Public Edition | [2](sap-cloud-journey-btp-landscape.md), [SAP AI 1](../sap-ai/sap-ai-landscape.md) |
| **SAML** | Older XML-based trust protocol between an app and an identity provider | [10](btp-identity-trust-federation.md) |
| **SCIM** | A standard API for users and groups; IPS uses it, for example with SuccessFactors | [10](btp-identity-trust-federation.md), [SAP Joule 15](../sap-joule/joule-integration-successfactors.md) |
| **SSO** | Single sign-on: one login for many systems | [10](btp-identity-trust-federation.md) |
| **XSUAA** | SAP Authorization and Trust Management service: issues the tokens that carry a user's roles in a subaccount | [7](btp-users-role-collections.md), [8](btp-subaccount-walkthrough.md) |

## 11.2 Terms

| Term | Meaning | Chapter |
|---|---|---|
| **Booster** | A guided setup wizard in the global account | [6](btp-global-account-tools.md) |
| **Cloud Connector** | On-premise software that opens a secure tunnel to BTP | [8](btp-subaccount-walkthrough.md) |
| **Destination** | Stored connection details for another system, used by name | [8](btp-subaccount-walkthrough.md), [SAP Joule 19.2](../sap-joule/reference-joule-setup-building-blocks.md) |
| **Directory** | A folder of subaccounts in a global account, with its own licences and admins | [9](btp-directories-tiers-commercial-models.md) |
| **Entitlement** | Permission to use a service plan, assigned to a subaccount | [4](btp-account-model-first-subscription.md) |
| **Environment (BTP)** | A runtime for your own code: Cloud Foundry, Kyma or ABAP | [8](btp-subaccount-walkthrough.md) |
| **Formation** | A group of SAP systems for one scenario, with baseline trust set up by SAP | [6](btp-global-account-tools.md) |
| **Global account** | Your contract with SAP; holds subaccounts and licences | [4](btp-account-model-first-subscription.md) |
| **Kyma** | BTP's Kubernetes-based runtime environment | [8](btp-subaccount-walkthrough.md) |
| **Role collection** | A bundle of roles you assign to users in BTP | [7](btp-users-role-collections.md) |
| **Shadow user** | BTP's local copy of a user who logs on through a trusted identity provider | [10](btp-identity-trust-federation.md) |
| **Subaccount** | Your working area in one region, inside a global account | [4](btp-account-model-first-subscription.md), [8](btp-subaccount-walkthrough.md) |
| **Subscription** | Using a SaaS app in a subaccount after it is entitled | [4](btp-account-model-first-subscription.md) |
| **Trust configuration** | The link between a subaccount and an identity provider | [10](btp-identity-trust-federation.md) |

## How this page was built

- Compiled on 21 Nov 2026 from the book's chapters: every term with two or more uses was considered, and meaningful ones were kept.
- No new sources; definitions follow the linked chapters.
- Split on 21 Nov 2026 from the single BTPAI glossary/facts page: this page keeps the rows whose main chapter is in this book. Links to the other SAP books name the book.

## Sources

- The chapters linked in each row.

Previous: [Identity: Cloud Identity Services, trust and federated authorization](btp-identity-trust-federation.md) · Next: [Reference: Current facts to re-check](reference-current-facts.md)
