# Enabling Joule for SAP SuccessFactors

*SuccessFactors is the reference scenario SAP uses to teach how any Line of Business gets Joule — learn the pattern here once.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how Joule actually relates to SuccessFactors architecturally, and the specific prerequisites for activation
> - **You will build:** nothing — this is activation/architecture knowledge, not a code tutorial
> - **Level:** beginner · **Time:** about 6 minutes
> - **Builds on:** [Joule's identity and platform foundation](btp-identity-foundation.md). **Leads to:** [Extending an SAP-delivered agent](03-extending-a-standard-agent.md), the first of the Joule Tutorials

**After this chapter you can:**

- Explain why Joule "feels native" in SuccessFactors despite running on BTP
- State SuccessFactors' specific entitlement and licensing prerequisites for Joule
- Recognize this as the template every other LoB-specific enablement follows

## 1. Why SuccessFactors is the reference scenario

Activating Joule for a Line-of-Business solution is **not** a repeat of the platform setup from the previous two chapters. Joule is provisioned centrally — but its *behavior* is defined locally, by the business system it operates in.

SAP SuccessFactors was one of the first SAP solutions to support Joule, so SAP uses it to teach the general pattern: how Joule integrates with a SaaS application, uses identity and authorizations at runtime, and executes navigational and transactional interactions in a real business context.

## 2. The architecture, stated precisely

Joule is embedded within the SuccessFactors UI — it looks native, but it isn't running inside SuccessFactors itself.

- **SuccessFactors remains the system of record** for HR data and processes.
- **Joule is a service on SAP BTP** acting as an interaction and orchestration layer — it interprets intent and invokes SuccessFactors capabilities, it doesn't replace them.
- **All data access and actions Joule performs are governed by existing SuccessFactors authorizations.** Joule never operates with privileges a human user in that role wouldn't already have.

This separation is the point: Joule adds usability without bypassing SAP's existing security or business logic. It's worth internalizing this exact framing, because every other LoB chapter (and the extension boundary from the previous chapter) repeats the same shape: *embedded UI, BTP-hosted service, local system's authorizations govern everything.*

## 3. Prerequisites specific to SuccessFactors

| Prerequisite | Note |
|---|---|
| **SAP BTP account with Joule entitlement** (`das-application`) | Check this specific entitlement in your Global Account. If you hold a SuccessFactors license but this entitlement is missing, contact your SAP Account Executive — it's a licensing gap, not a configuration one |
| **SAP Build Work Zone, standard edition / SAP Start** | The navigation layer from the previous chapter |
| **SuccessFactors license and Joule Data Center availability** | Not every data center supports Joule yet — availability is a real constraint to check, not an assumption |
| **SAP Cloud Identity Services with active tenants** | Same identity foundation from [Joule's identity and platform foundation](btp-identity-foundation.md) |

SAP provides step-by-step activation guidance through **SAP Discovery Center missions**, specifically "Activate Joule for SAP SuccessFactors" — these translate the high-level model above into concrete configuration steps and automate parts of it through BTP tooling.

## 4. Added by Claude, not from the sources

- Framing this chapter as "the template every other LoB chapter follows" is this book's own observation, made explicit because the next chapter (covering six more products) deliberately doesn't repeat this architectural explanation in full.
- Not run: this chapter is architecture and prerequisite guidance; nothing was independently executed.

## 5. Interview corner

<details class="qa"><summary>1. Does Joule run inside SuccessFactors?</summary>

- No — it's embedded in the SuccessFactors UI but runs as a separate service on SAP BTP; SuccessFactors stays the system of record

</details>

<details class="qa"><summary>2. What governs what Joule is allowed to do in SuccessFactors?</summary>

- Existing SuccessFactors authorizations — Joule never bypasses them or operates with elevated privileges

</details>

<details class="qa"><summary>3. A customer has a SuccessFactors license but can't find the Joule entitlement in their BTP account. What's the likely cause?</summary>

- A missing `das-application` entitlement — this requires contacting the SAP Account Executive, it's not something fixable through self-service configuration
- *Stronger answer:* also check Joule Data Center availability for their region — SuccessFactors licensing alone doesn't guarantee Joule is available in their specific data center yet

</details>

> [!TIP]
> **🧩 Design question**
> *"An HR admin asks why Joule can show them one employee's salary but refuses to show them another's."* Talk about: this is authorization working as designed, not a bug — Joule inherits the admin's existing SuccessFactors permissions exactly, so if the admin couldn't see that employee's salary through the normal SuccessFactors UI, Joule won't surface it either.

## Cheat sheet

| Fact | Detail |
|---|---|
| Where Joule runs | SAP BTP (not inside SuccessFactors) |
| Who governs its actions | Existing SuccessFactors authorizations |
| Key entitlement | `das-application` in the BTP Global Account |
| Availability gate | Joule Data Center availability per region |
| Guided setup | SAP Discovery Center mission: "Activate Joule for SAP SuccessFactors" |

## Recap

- Joule in SuccessFactors is a BTP-hosted orchestration layer, not a SuccessFactors-native feature — SuccessFactors stays the system of record
- Every action Joule takes is bound by the acting user's existing SuccessFactors authorizations
- The specific entitlement to check is `das-application`; a missing one means contacting your Account Executive, not debugging configuration
- This architecture (embedded UI, BTP service, local authorizations govern everything) is the pattern every other Line-of-Business enablement repeats

## Practice

1. Explain out loud why "Joule feels native in SuccessFactors" is true even though it's architecturally a separate BTP service
2. Name the specific entitlement to check first when SuccessFactors Joule access is missing

## How this chapter was checked

- "Setting Up Joule for SAP SuccessFactors" (Unit 3, lesson 1 of 7) from "Setting Up Joule Across your Organizational System Landscapes" was read in full, 10 Nov 2026.
- No images appeared in this lesson — none were skipped.
- Nothing in this chapter is code; nothing was run.

## Sources and further reading

- SAP Learning, *Setting Up Joule Across your Organizational System Landscapes* — https://learning.sap.com/courses/setting-up-joule-across-your-organizational-system-landscapes, "Setting Up Joule for SAP SuccessFactors" (read in full 10 Nov 2026)

Previous: [How business users actually use Joule](05-how-business-users-use-joule.md) · Next: [Extending an SAP-delivered agent](03-extending-a-standard-agent.md)
