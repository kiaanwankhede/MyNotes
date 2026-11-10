# Extending Joule beyond a single application

*There is no public API for Joule. If someone proposes calling it directly from a non-SAP app, this chapter is the correction.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how Joule reaches users outside a single SAP app (Work Zone, Mobile Start, Microsoft 365 Copilot), and the two supported ways to connect Joule to non-SAP systems — plus what's explicitly not supported
> - **You will build:** nothing — this is the architectural boundary every extension idea has to fit inside
> - **Level:** intermediate · **Time:** about 12 minutes
> - **Builds on:** [Joule's identity and platform foundation](btp-identity-foundation.md). **Leads to:** [What Joule actually is](01-what-is-joule.md)

**After this chapter you can:**

- Explain what SAP Build Work Zone and SAP Mobile Start add to Joule beyond a single app
- Describe the Joule ↔ Microsoft 365 Copilot integration and its one hard constraint
- State, correctly, why you can't call Joule as a public API — and what to build instead
- Choose between Joule Studio and the Joule Action Bar for a given non-SAP integration need

## 1. The experience layer: SAP Build Work Zone and SAP Mobile Start

Up to the identity/platform setup in the previous chapter, Joule is enabled *within* individual SAP applications. SAP Build Work Zone and SAP Mobile Start extend it into the **enterprise experience layer** — where users start their day, across systems, not inside one app.

- **SAP Build Work Zone** is a role-based launchpad aggregating applications, content, and navigation from multiple SAP systems.
- **SAP Mobile Start** extends the same experience to mobile, reusing the same Work Zone site and identity configuration — not a separate setup.

With Joule integrated here, it can resolve user intents across connected systems, navigate users to authorized applications and tasks, and stay available consistently across desktop and mobile — rather than being locked to a single application's context.

Prerequisites specific to this step: a unified Joule instance already provisioned (previous chapter), SAP Build Work Zone standard edition in the same subaccount, SAP applications already exposing navigation content, and consistent Cloud Identity Services configuration across systems.

## 2. Microsoft 365 Copilot: bi-directional, opt-in, Teams first

Many SAP customers live in Microsoft 365 day to day. SAP and Microsoft provide a **bi-directional integration** between Joule and Microsoft 365 Copilot so users can reach SAP-grounded AI without leaving Microsoft tools.

- Entry point: **Microsoft Teams**, first.
- **Transparency is explicit**: responses are labeled as coming from Joule or from Microsoft 365 Copilot — the two systems are connected, not merged into one.
- Prerequisites: a licensed Microsoft 365 Copilot environment, an already-activated Joule instance, identity alignment between SAP and Microsoft environments, and trust/network configuration for secure cross-platform communication.

> [!WARNING]
> **⚠️ Pitfall: this integration is opt-in on both sides**
> It is not enabled by default for either Joule or Microsoft 365 Copilot — someone has to explicitly activate it. Don't assume it's "just there" once both products are licensed.

## 3. Connecting Joule to non-SAP systems: the one rule to internalize

This is the single most important architectural fact in this chapter, stated plainly by SAP's own material:

> [!CAUTION]
> **🔒 Joule is not a public API**
> SAP does not provide a general-purpose API that lets a third-party application call Joule directly as a standalone AI service. No public REST API for arbitrary consumption, no native hosting of Joule inside a non-SAP app, no direct LLM access outside SAP-managed contexts, and identity/authorization are **never** delegated to a non-SAP system. If a design assumes "we'll just call Joule's API from our app," that design is wrong before you write a line of code.

Instead, Joule is **extended**, never embedded, into non-SAP environments — through two supported approaches:

### Approach 1 — Joule Studio

[Joule Studio](02-joule-studio-lifecycle.md) is the primary extensibility mechanism for both SAP and non-SAP integration. Through it you can:

- Extend Joule Skills that call non-SAP system APIs
- Build custom Joule Agents orchestrating workflows across SAP and non-SAP applications
- Use pro-code tools, including the **Joule Studio CLI**, to build, compile, and deploy
- Ground Joule responses in data retrieved from external systems
- Keep lifecycle management, security, and governance centralized

The key architectural point: **Joule Studio does not expose Joule externally.** It lets Joule invoke external systems securely from inside SAP BTP, through approved mechanisms like destinations and action projects — the non-SAP system is always a backend data or action provider, never a peer that calls Joule.

### Approach 2 — WalkMe and the Joule Action Bar

SAP's acquisition of **WalkMe** gave Joule a second extension path: the **Joule Action Bar**, an omnipresent AI overlay available across both SAP and non-SAP *web* applications.

- Uses **screen-level context** to determine user intent — it reads what's on screen, rather than needing code-level integration
- Delivers proactive assistance, summaries, and recommendations
- Routes all interactions through SAP-managed services, preserving SAP security and identity — nothing is embedded into the non-SAP app's own codebase

### Which approach, when

| Scenario | Use |
|---|---|
| Integrating APIs of non-SAP systems | Joule Studio |
| Cross-system workflow orchestration | Joule Studio (Agents) |
| AI assistance across multiple web apps, no code changes to those apps | WalkMe + Joule Action Bar |
| Unified experience without embedding | WalkMe |
| Backend automation and data retrieval | Joule Studio Skills |

## 4. Added by Claude, not from the sources

- The "Joule Studio vs. WalkMe" framing as two *architecturally distinct* extension mechanisms (API-integration vs. overlay) is this book's synthesis of the source's own decision table — the underlying facts are the source's, not inferred.
- Not run: this chapter is architecture and integration guidance, not code; nothing was independently executed.

## 5. Interview corner

**What interviewers listen for:** you state confidently (not hesitantly) that there's no public Joule API, and you can pick the right extension mechanism for a stated scenario without hedging.

### 🟢 Basic

<details class="qa"><summary>1. Can a third-party application call Joule directly as a standalone API?</summary>

- No. SAP does not provide a general-purpose public API for that; Joule is extended into non-SAP contexts through Joule Studio or the WalkMe-based Joule Action Bar, never exposed directly

</details>

<details class="qa"><summary>2. What's the first Microsoft tool through which the Joule/M365 Copilot integration is accessed?</summary>

- Microsoft Teams

</details>

### 🟡 Intermediate

<details class="qa"><summary>3. A team wants Joule to read data from a non-SAP CRM and take actions in it. Which extension approach fits, and why?</summary>

- Joule Studio — build a Skill or Agent that calls the CRM's API through a destination/action project; this is "integrating APIs of non-SAP systems," squarely Joule Studio's use case
- *Stronger answer:* the CRM remains a backend data/action provider; Joule itself is never embedded into or exposed to the CRM application

</details>

<details class="qa"><summary>4. A team wants AI assistance available inside a third-party web app they don't control the codebase of. What fits?</summary>

- WalkMe + the Joule Action Bar — it overlays via screen-level context without needing code-level access to the target app

</details>

### 🔴 Senior

<details class="qa"><summary>5. A vendor pitches a "Joule REST connector" for a non-SAP tool, claiming direct API access. How do you evaluate that claim?</summary>

- Treat it as incorrect by default — SAP explicitly does not expose Joule as a public API, and identity/authorization is never delegated to a non-SAP system
- *Stronger answer:* ask what the connector actually does under the hood — it's almost certainly either a Joule Studio-built Skill/Agent (legitimate) or a WalkMe-style overlay (legitimate), repackaged with misleading marketing; verify which, because the security and governance model differs

</details>

> [!TIP]
> **🧩 Design question**
> *"Leadership wants one consistent AI assistant experience across SAP S/4HANA, a non-SAP CRM, and a non-SAP ticketing tool, all from one overlay."* Talk about: the Joule Action Bar as the unifying surface across all three (it doesn't care which app is SAP vs. not), Joule Studio Skills underneath for any actual CRM/ticketing API calls the overlay needs to trigger, and why neither approach requires — or allows — exposing Joule as a callable API to those tools directly.

## Cheat sheet

| Need | Mechanism |
|---|---|
| Cross-app launchpad experience | SAP Build Work Zone + SAP Mobile Start |
| AI inside Microsoft Teams/365 | Joule ↔ M365 Copilot (opt-in, bi-directional) |
| Call a non-SAP API from an agent | Joule Studio (Skills/Agents, via destinations) |
| AI overlay on a non-SAP web app, no code access | WalkMe + Joule Action Bar |
| "Can I just call Joule's API?" | No — not supported, by design |

## Recap

- Work Zone + Mobile Start extend Joule into a cross-system, cross-device experience layer — not a new Joule instance, the same unified one
- Joule ↔ Microsoft 365 Copilot is bi-directional, opt-in on both sides, transparent about which system answered, and enters through Teams first
- **Joule has no public API** — this is a hard architectural boundary, not a current limitation waiting to be lifted
- Non-SAP integration happens through exactly two supported mechanisms: **Joule Studio** (API integration, agent orchestration, grounding) and **WalkMe's Joule Action Bar** (screen-context overlay, no code embedding)
- Identity and authorization are never delegated to a non-SAP system under either approach

## Practice

1. Without looking back, list the four things SAP explicitly says are *not* supported for non-SAP integration
2. Pick a non-SAP tool you use and decide: Joule Studio or Joule Action Bar — and justify it in one sentence
3. Explain out loud why "Joule Studio doesn't expose Joule externally" is true even though it integrates with non-SAP APIs

## How this chapter was checked

- All 3 lessons of Unit 5 ("Setting Up Joule for SAP Build Work Zone and SAP Mobile Start," "Setting Up Joule with Microsoft 365 Copilot," "Integrating Joule with Non-SAP Applications") and the unit quiz, from "Setting Up Joule Across your Organizational System Landscapes," were read in full, 10 Nov 2026.
- No images appeared in any of these 3 lessons — none were skipped.
- Nothing in this chapter is code; nothing was run.

## Sources and further reading

- SAP Learning, *Setting Up Joule Across your Organizational System Landscapes* — https://learning.sap.com/courses/setting-up-joule-across-your-organizational-system-landscapes, Unit 5 (read in full 10 Nov 2026)

Previous: [Joule's identity and platform foundation](btp-identity-foundation.md) · Next: [What Joule actually is](01-what-is-joule.md)
