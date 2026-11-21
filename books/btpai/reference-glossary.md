# Reference: Glossary

*The acronyms and terms used in this book, in one line each, with the chapter that explains them.*

> [!NOTE]
> **📍 At a glance**
> - **Use it for:** looking up a term while you read; the chapter number links to the full explanation
> - **What it is:** a summary of what the book already says; no new sources
> - **Level:** reference
> - **Last checked:** 21 Nov 2026

## 40.1 Acronyms

| Term | Meaning | Chapter |
|---|---|---|
| **A2A** | Agent-to-Agent protocol: how agents call each other; the new Joule Studio's *Try now* uses it | [20](joule-studio-intent-based.md), [27](tutorial-joule-studio-hr-assistant.md) |
| **ABAP** | SAP's programming language; on BTP also an environment (SAP BTP, ABAP environment) | [8](btp-subaccount-walkthrough.md) |
| **AI units** | SAP's currency for Premium AI features, bought yearly into one pool | [16](joule-for-consultants.md), [18](joule-family.md) |
| **BAS** | SAP Business Application Studio, the cloud IDE on BTP | [30](tutorial-joule-bas-full-stack-cap.md) |
| **BDC** | SAP Business Data Cloud: SAP's data offering (Datasphere, SAC and more) | [2](sap-cloud-journey-btp-landscape.md), [11](sap-ai-landscape.md) |
| **BTP** | SAP Business Technology Platform, SAP's PaaS | [1](cloud-computing-service-models.md), [2](sap-cloud-journey-btp-landscape.md) |
| **BTPEA / CPEA** | Prepaid consumption contracts for BTP: you buy credits upfront | [9](btp-directories-tiers-commercial-models.md) |
| **CAP** | SAP Cloud Application Programming Model, for building services and apps on BTP | [30](tutorial-joule-bas-full-stack-cap.md) |
| **CDM** | Common Data Model: the format in which roles, apps and content reach SAP Build Work Zone | [29](tutorial-joule-sac-analytical-insights.md), [31](joule-integration-successfactors.md) |
| **C_JSD** | SAP certification for developing with Joule Studio | [12](sap-ai-careers-certifications.md) |
| **ECC** | SAP ERP Central Component, the on-premise ERP before S/4HANA | [2](sap-cloud-journey-btp-landscape.md) |
| **HITL / HOTL / HIC** | Human in the loop, on the loop, in command: three levels of human oversight of AI | [17](responsible-ai-ethics-governance.md) |
| **IaaS / PaaS / SaaS** | Rent the hardware / also the platform / the finished application | [1](cloud-computing-service-models.md) |
| **IAS** | Identity Authentication: SAP's login service in Cloud Identity Services | [10](btp-identity-trust-federation.md) |
| **IDS** | Identity Directory: the user store in Cloud Identity Services | [10](btp-identity-trust-federation.md) |
| **IPS** | Identity Provisioning: copies users and groups from a source system to a target | [10](btp-identity-trust-federation.md), [39.5](reference-joule-setup-building-blocks.md) |
| **J4C** | Joule for Consultants: answers SAP project questions from curated SAP knowledge | [16](joule-for-consultants.md) |
| **J4D** | Joule for Developers: Joule in development tools, for example ABAP | [16](joule-for-consultants.md), [18](joule-family.md) |
| **JWT** | JSON Web Token: the signed token a service returns after sign-in; some APIs need a user-specific one | [35](tutorial-translation-hub-python.md) |
| **LLM** | Large language model | [14](llm-prompt-to-answer.md) |
| **MCP** | Model Context Protocol: a standard way to give an AI model tools | [19](joule-studio-classic.md), [20](joule-studio-intent-based.md) |
| **OIDC** | OpenID Connect: the token-based trust protocol, preferred over SAML for BTP trust | [10](btp-identity-trust-federation.md) |
| **PAYG** | Pay-As-You-Go: BTP billed monthly for what you use, no upfront commitment | [9](btp-directories-tiers-commercial-models.md) |
| **PCE** | SAP S/4HANA Cloud Private Edition | [32](joule-integration-other-sap-solutions.md) |
| **PRD** | Product requirements document, one phase in the new Joule Studio | [20](joule-studio-intent-based.md) |
| **PUPM** | Per user per month, a pricing model (J4C) | [16](joule-for-consultants.md) |
| **RAG** | Retrieval-augmented generation: look up documents, then let the model answer from them | [15](prompt-engineering.md), [16](joule-for-consultants.md) |
| **RISE / GROW** | SAP's cloud offers: RISE for existing ERP customers moving to S/4HANA Cloud (usually Private Edition); GROW for new customers starting on Public Edition | [2](sap-cloud-journey-btp-landscape.md), [11](sap-ai-landscape.md) |
| **SAC** | SAP Analytics Cloud | [29](tutorial-joule-sac-analytical-insights.md) |
| **SAML** | Older XML-based trust protocol between an app and an identity provider | [10](btp-identity-trust-federation.md) |
| **SCIM** | A standard API for users and groups; IPS uses it, for example with SuccessFactors | [10](btp-identity-trust-federation.md), [31](joule-integration-successfactors.md) |
| **SKU** | SAP's order number for a product, for example AI units 8019164 | [16](joule-for-consultants.md), [18](joule-family.md) |
| **SSO** | Single sign-on: one login for many systems | [10](btp-identity-trust-federation.md) |
| **XSUAA** | SAP Authorization and Trust Management service: issues the tokens that carry a user's roles in a subaccount | [7](btp-users-role-collections.md), [8](btp-subaccount-walkthrough.md) |

## 40.2 Terms

| Term | Meaning | Chapter |
|---|---|---|
| **Action project** | A set of API calls (OData or REST) that Joule skills and processes can use | [19.4a](joule-studio-classic.md), [22](tutorial-joule-action-projects.md) |
| **Agent (Joule)** | Plans and calls tools (skills, other agents, MCP servers) until it can answer | [18](joule-family.md), [19](joule-studio-classic.md) |
| **AI Core** | SAP's BTP service for running AI workloads; its generative AI hub serves LLMs through deployments | [33](tutorial-genai-hub-python.md) |
| **AI Launchpad** | The web UI for SAP AI Core: chat, prompt editor, grounding management, orchestration | [36](tutorial-rag-grounding-genai-hub.md) |
| **Assistant (Joule)** | SAP's grouping of agents for one business area, for example Accounts Payable | [18](joule-family.md) |
| **Booster** | A guided setup wizard in the global account | [6](btp-global-account-tools.md) |
| **Cloud Connector** | On-premise software that opens a secure tunnel to BTP | [8](btp-subaccount-walkthrough.md) |
| **Content provider** | A Work Zone channel that imports a product's roles and apps | [39.4](reference-joule-setup-building-blocks.md) |
| **Control tower** | Joule Studio's admin area: environments, destinations, settings | [19](joule-studio-classic.md) |
| **Deployment (AI Core)** | One running instance of a model in SAP AI Core, with its own ID | [33](tutorial-genai-hub-python.md) |
| **Destination** | Stored connection details for another system, used by name | [8](btp-subaccount-walkthrough.md), [39.2](reference-joule-setup-building-blocks.md) |
| **Destination variable** | A placeholder in a skill; the real destination is chosen at test or deploy time | [19](joule-studio-classic.md), [23](tutorial-joule-skill-create.md) |
| **Directory** | A folder of subaccounts in a global account, with its own licences and admins | [9](btp-directories-tiers-commercial-models.md) |
| **Document AI** | SAP service that extracts fields from business documents; its API was called Document Information Extraction | [34](tutorial-document-ai-python.md) |
| **Document grounding** | Lets Joule answer from your own documents | [32.5](joule-integration-other-sap-solutions.md) |
| **Entitlement** | Permission to use a service plan, assigned to a subaccount | [4](btp-account-model-first-subscription.md) |
| **Environment (BTP)** | A runtime for your own code: Cloud Foundry, Kyma or ABAP | [8](btp-subaccount-walkthrough.md) |
| **Environment (Joule Studio)** | Where projects run: private, shared or public | [19.3](joule-studio-classic.md) |
| **Formation** | A group of SAP systems for one scenario, with baseline trust set up by SAP | [6](btp-global-account-tools.md) |
| **Generative AI hub** | The part of SAP AI Core that gives access to LLMs from several providers with one service key (extended plan) | [33](tutorial-genai-hub-python.md) |
| **Global account** | Your contract with SAP; holds subaccounts and licences | [4](btp-account-model-first-subscription.md) |
| **Intent fit** | How closely a proposed solution matches what you asked for, in the new Joule Studio | [20](joule-studio-intent-based.md) |
| **Just Ask** | SAC's natural-language feature; only models it indexes are visible to Joule | [29](tutorial-joule-sac-analytical-insights.md) |
| **Kyma** | BTP's Kubernetes-based runtime environment | [8](btp-subaccount-walkthrough.md) |
| **n8n** | A workflow tool; the new Joule Studio uses n8n workflows, for example as hooks | [20](joule-studio-intent-based.md), [28](tutorial-joule-studio-agent-extension.md) |
| **Orchestration (generative AI hub)** | One API call that runs grounding, templating, masking, filtering and the model as a pipeline | [36](tutorial-rag-grounding-genai-hub.md) |
| **Principal propagation** | Passing the signed-in user's identity to a backend instead of a technical user | [32.2](joule-integration-other-sap-solutions.md) |
| **Progressive disclosure** | Showing the model only the next level of choices (assistant, agent, skill) to keep context small | [18.4](joule-family.md) |
| **Resource group** | A partition of an SAP AI Core tenant that holds deployments; the course uses `default` | [33](tutorial-genai-hub-python.md) |
| **Role collection** | A bundle of roles you assign to users in BTP | [7](btp-users-role-collections.md) |
| **Service key** | Credentials for a service instance (URL, client ID, secret) | [29](tutorial-joule-sac-analytical-insights.md), [31](joule-integration-successfactors.md) |
| **Shadow user** | BTP's local copy of a user who logs on through a trusted identity provider | [10](btp-identity-trust-federation.md) |
| **Skill (Joule)** | A fixed flow of steps (actions, processes, messages) that Joule can run | [19](joule-studio-classic.md), [23](tutorial-joule-skill-create.md) |
| **Subaccount** | Your working area in one region, inside a global account | [4](btp-account-model-first-subscription.md), [8](btp-subaccount-walkthrough.md) |
| **Subscription** | Using a SaaS app in a subaccount after it is entitled | [4](btp-account-model-first-subscription.md) |
| **Token (LLM)** | The piece of text a language model reads and writes; also the unit of cost | [14](llm-prompt-to-answer.md) |
| **Translation Hub** | SAP service for translating application texts and documents by API | [35](tutorial-translation-hub-python.md) |
| **Trust configuration** | The link between a subaccount and an identity provider | [10](btp-identity-trust-federation.md) |
| **Vector engine** | SAP HANA Cloud's store for embeddings; finds the chunks nearest to a question | [36](tutorial-rag-grounding-genai-hub.md) |
| **Work Zone** | SAP Build Work Zone: the launchpad service that Joule uses for navigation and roles | [29](tutorial-joule-sac-analytical-insights.md), [39.4](reference-joule-setup-building-blocks.md) |

## How this page was built

- Compiled on 21 Nov 2026 from the book's chapters: every term with two or more uses was considered, and meaningful ones were kept.
- No new sources; definitions follow the linked chapters.

## Sources

- The chapters linked in each row.

Previous: [Reference: Joule setup building blocks](reference-joule-setup-building-blocks.md) · Next: [Reference: Current facts to re-check](reference-current-facts.md)
