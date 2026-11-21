# Reference: Glossary

*The acronyms and terms used in this book, in one line each, with the chapter that explains them.*

> [!NOTE]
> **📍 At a glance**
> - **Use it for:** looking up a term while you read; the chapter number links to the full explanation
> - **What it is:** a summary of what the book already says; no new sources
> - **Level:** reference
> - **Last checked:** 21 Nov 2026

## 20.1 Acronyms

| Term | Meaning | Chapter |
|---|---|---|
| **A2A** | Agent-to-Agent protocol: how agents call each other; the new Joule Studio's *Try now* uses it | [4](joule-studio-intent-based.md), [11](tutorial-joule-studio-hr-assistant.md) |
| **AI units** | SAP's currency for Premium AI features, bought yearly into one pool | [1](joule-for-consultants.md), [2](joule-family.md) |
| **BAS** | SAP Business Application Studio, the cloud IDE on BTP | [14](tutorial-joule-bas-full-stack-cap.md) |
| **CAP** | SAP Cloud Application Programming Model, for building services and apps on BTP | [14](tutorial-joule-bas-full-stack-cap.md) |
| **CDM** | Common Data Model: the format in which roles, apps and content reach SAP Build Work Zone | [13](tutorial-joule-sac-analytical-insights.md), [15](joule-integration-successfactors.md) |
| **J4C** | Joule for Consultants: answers SAP project questions from curated SAP knowledge | [1](joule-for-consultants.md) |
| **J4D** | Joule for Developers: Joule in development tools, for example ABAP | [1](joule-for-consultants.md), [2](joule-family.md) |
| **MCP** | Model Context Protocol: a standard way to give an AI model tools | [3](joule-studio-classic.md), [4](joule-studio-intent-based.md) |
| **PCE** | SAP S/4HANA Cloud Private Edition | [16](joule-integration-other-sap-solutions.md) |
| **PRD** | Product requirements document, one phase in the new Joule Studio | [4](joule-studio-intent-based.md) |
| **PUPM** | Per user per month, a pricing model (J4C) | [1](joule-for-consultants.md) |
| **SAC** | SAP Analytics Cloud | [13](tutorial-joule-sac-analytical-insights.md) |
| **SKU** | SAP's order number for a product, for example AI units 8019164 | [1](joule-for-consultants.md), [2](joule-family.md) |

## 20.2 Terms

| Term | Meaning | Chapter |
|---|---|---|
| **Action project** | A set of API calls (OData or REST) that Joule skills and processes can use | [3.4a](joule-studio-classic.md), [6](tutorial-joule-action-projects.md) |
| **Agent (Joule)** | Plans and calls tools (skills, other agents, MCP servers) until it can answer | [2](joule-family.md), [3](joule-studio-classic.md) |
| **Assistant (Joule)** | SAP's grouping of agents for one business area, for example Accounts Payable | [2](joule-family.md) |
| **Content provider** | A Work Zone channel that imports a product's roles and apps | [19.4](reference-joule-setup-building-blocks.md) |
| **Control tower** | Joule Studio's admin area: environments, destinations, settings | [3](joule-studio-classic.md) |
| **Destination variable** | A placeholder in a skill; the real destination is chosen at test or deploy time | [3](joule-studio-classic.md), [7](tutorial-joule-skill-create.md) |
| **Document grounding** | Lets Joule answer from your own documents | [16.5](joule-integration-other-sap-solutions.md) |
| **Environment (Joule Studio)** | Where projects run: private, shared or public | [3.3](joule-studio-classic.md) |
| **Intent fit** | How closely a proposed solution matches what you asked for, in the new Joule Studio | [4](joule-studio-intent-based.md) |
| **Just Ask** | SAC's natural-language feature; only models it indexes are visible to Joule | [13](tutorial-joule-sac-analytical-insights.md) |
| **n8n** | A workflow tool; the new Joule Studio uses n8n workflows, for example as hooks | [4](joule-studio-intent-based.md), [12](tutorial-joule-studio-agent-extension.md) |
| **Principal propagation** | Passing the signed-in user's identity to a backend instead of a technical user | [16.2](joule-integration-other-sap-solutions.md) |
| **Progressive disclosure** | Showing the model only the next level of choices (assistant, agent, skill) to keep context small | [2.4](joule-family.md) |
| **Service key** | Credentials for a service instance (URL, client ID, secret) | [13](tutorial-joule-sac-analytical-insights.md), [15](joule-integration-successfactors.md) |
| **Skill (Joule)** | A fixed flow of steps (actions, processes, messages) that Joule can run | [3](joule-studio-classic.md), [7](tutorial-joule-skill-create.md) |
| **Work Zone** | SAP Build Work Zone: the launchpad service that Joule uses for navigation and roles | [13](tutorial-joule-sac-analytical-insights.md), [19.4](reference-joule-setup-building-blocks.md) |

## How this page was built

- Compiled on 21 Nov 2026 from the book's chapters: every term with two or more uses was considered, and meaningful ones were kept.
- No new sources; definitions follow the linked chapters.
- Split on 21 Nov 2026 from the single glossary/facts page of the former combined course book: this page keeps the rows whose main chapter is in this book. Links to the other SAP books name the book.

## Sources

- The chapters linked in each row.

Previous: [Reference: Joule setup building blocks](reference-joule-setup-building-blocks.md) · Next: [Reference: Current facts to re-check](reference-current-facts.md)
