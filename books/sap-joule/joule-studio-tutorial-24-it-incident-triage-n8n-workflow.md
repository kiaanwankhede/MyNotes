# Joule Studio tutorial 24: an IT Incident Triage & Auto-Routing workflow

*A 17-node n8n workflow that classifies, routes, and auto-resolves incidents end-to-end — then extended further through a "What happens next?" node-search box that inserts SAP-specific nodes directly into the canvas.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how a generated n8n workflow encodes a full severity-classification and routing pipeline, and how to extend a finished workflow afterward using Joule Studio's own node-search feature rather than editing JSON by hand
> - **You will build:** an IT Incident Triage & Auto-Routing workflow — normalizes incoming incidents, classifies severity (P1–P4) and root cause, routes to ServiceNow/PagerDuty/Slack, auto-resolves low-severity events, and inserts a manager-approval gate for P1/P2 escalations
> - **Level:** beginner · **Time:** about 20 minutes
> - **Builds on:** [Joule Studio tutorial 23: an HR Virtual Assistant](joule-studio-tutorial-23-hr-onboarding-assistant-agent.md). **Leads to:** [Joule Studio tutorial 25: an Equipment Troubleshooting agent](joule-studio-tutorial-25-equipment-troubleshooting-agent.md)

> [!WARNING]
> Pre-release Joule Studio — screens and exact flow may differ from general availability.

**After this tutorial you can:**

- Read a 17-node incident-triage workflow's architecture end-to-end, from webhook receipt to ITSM ticket
- Explain what the global error handler does differently from the main routing logic
- Use the "What happens next?" node-search box to insert a new node into a finished workflow, and read what Joule Studio reports changed

## 1. Create the workflow

![Create n8n Workflow dialog: Name "IT Incident Triage + Auto-Routing Agent," Intent Statement — "You are an IT operations AI agent built using N8N workflows to analyze incoming incident reports from multiple sources (webhook payloads, JSON logs) and classify them into severity levels (P1–P4), detect probable root cause category (application, infrastructure, integration, user error), and generate a structured incident ticket payload. You must: Normalize unstructured incident text into structured JSON; Identify urgency and impact based on keywords and patterns; Suggest next best action (restart service, escalate, ignore, collect logs); Route to appropriate team..." Quick create checked](images/sj219-02-define-solution-details.png)

![Create solution dialog, entry point](images/sj219-01-create-solution-dialog.png)
![Intent tools context](images/sj219-03-intent-tools.png)
![Intent ready](images/sj219-04-intent-ready-now.png)

## 2. The PRD

![PRD creation, requirement saved](images/sj219-05-create-prd-requirement-saved.png)

![PRD, technical overview: Title "IT Operations Incident Triage & Auto-Routing Agent," Date 2026-05-07, Owner "IT Operations Team," Solution Category "n8n Workflow." Business Need: incident reports arrive from heterogeneous sources in unstructured, inconsistent formats; manual triage is slow, inconsistent, and error-prone; critical P1/P2 incidents may be delayed, causing extended outages](images/sj219-06-prd-ready-technical-overview.png)

The PRD, read directly: Title "IT Operations Incident Triage & Auto-Routing Agent," Solution Category "n8n Workflow." Elevator Pitch — *"IT operations teams drown in unstructured incident noise. This solution automatically ingests webhook payloads and JSON log events, classifies every incident by severity (P1–P4) and root cause category, generates a structured ticket, and routes it instantly to the right automated handler — cutting triage time from minutes to milliseconds."*

Product Objectives (Prioritized): normalize 100% of incoming incident payloads into a canonical structured JSON schema; classify every incident with a severity level and root cause category; route incidents to the correct downstream handler within the same workflow execution; generate a complete, actionable incident ticket payload ready for ITSM submission.

> [!NOTE]
> The build log explicitly labels this "**Fast-track: proceeding directly to execution**" — the same Fast Track concept named in [Tutorial 19's](joule-studio-tutorial-19-billing-completeness-data-product.md) Data Product build, here applied to an n8n Workflow. It isn't unique to Data Products.

## 3. The generated workflow: 17 nodes, a full severity-routing pipeline

![Solution build summary: "A production-ready n8n workflow (assets/n8n/workflows/incident-triage-auto-routing.n8n.json) with 17 nodes implementing the full incident intelligence pipeline." Workflow Architecture — [Incident Webhook Receiver] POST /incident-ingest-{uuid} → [Normalize Incident Payload] maps any raw payload to canonical schema → [Classify Severity] keyword rules → P1/P2/P3/P4 → [Detect Root Cause] pattern matching → application/infrastructure/... → [Build Ticket Payload] structured incident ticket JSON → [Determine Next Action] rule matrix → escalate/restart_service/... → [Incident Router] Switch node: P1/P2 → [high-priority-escalation] → [Create ITSM Ticket (ServiceNow)]; auto_resolve → [auto-resolution] → [Close ITSM Ticket (ServiceNow)]; fallback → [log-analysis]; all branches → [Respond to Webhook] returns structured JSON response. [Global Error Handler] catches any execution error → [Escalate Error Ticket] ServiceNow P1 ticket → [Flag: Error Escalated]. Key Features Implemented table: Multi-source ingestion (webhook POST, manual trigger for JSON log batches), Normalization (code node maps 15+ field variants to canonical schema, missing fields → null), P1-P4 classification (keyword/pattern rules with 50+ terms per severity tier), Root cause detection (4 categories × 15+ keywords, defaults to unknown)](images/sj219-15-execute-workflow.png)

![Specification creation](images/sj219-07-create-spec.png)
![Specification ready](images/sj219-08-spec-ready.png)
![Generated solution code](images/sj219-09-generated-solution-code.png)
![Implementation complete](images/sj219-10-implementation-complete.png)

| Pipeline stage | What it does |
|---|---|
| Incident Webhook Receiver | Accepts `POST /incident-ingest-{uuid}` |
| Normalize Incident Payload | Maps any raw payload to a canonical schema |
| Classify Severity | Keyword rules → P1/P2/P3/P4 |
| Detect Root Cause | Pattern matching → application / infrastructure / integration / user error |
| Build Ticket Payload | Structured incident ticket JSON |
| Determine Next Action | Rule matrix → escalate / restart_service / ignore / collect logs |
| Incident Router | Switch node — P1/P2 → high-priority escalation; auto_resolve → auto-resolution; fallback → log-analysis |
| Respond to Webhook | Returns a structured JSON response on every branch |

> [!CAUTION]
> **🔒 Errors escalate to P1, not silently fail**
> The **Global Error Handler** doesn't just log a failure — it routes any execution error straight to **Escalate Error Ticket**, which creates a ServiceNow **P1** ticket, then flags it as error-escalated. A bug in the triage pipeline itself is treated with the same urgency as the most severe incident category it classifies, rather than failing quietly.

## 4. Extending a finished workflow: the "What happens next?" node search

Past the initial build, the workflow is extended further — not by editing the exported JSON by hand, but through a search box directly on the canvas:

![Workflow canvas, "What happens next?" search box: typed query "sap Agent," results list — SAP Agent, SAP Joule Content Agent, SAP AI Core Management](images/sj219-13-add-sap-agent-node.png)

![Workflow canvas after insertion: SAP Task Center - Manager Approval node now sits at the top of the high-priority escalation branch, before PagerDuty - Trigger Incident → Slack - Escalation Alert → ITSM - Create Escalation Ticket. Chat summary: "SAP Task Center — Manager Approval Node Added. What changed: A new SAP Task Center - Manager Approval node (CUSTOM.sapTaskCenter) was inserted into the high-priority escalation branch (P1/P2 incidents), between the router and PagerDuty." Updated flow: Route by Severity (P1/P2) → SAP Task Center - Manager Approval (NEW, manager approves) → PagerDuty - Trigger Incident → Slack - Escalation Alert → ITSM - Create Escalation Ticket. Node configuration table: Type CUSTOM.sapTaskCenter — Send Approval Task; Credential SAP Task Center|sap.taskcenter (globally available); Subject "[P1/P2] Manager Approval Required: <AI-generated summary>"; Description rich HTML with incident ID, severity, service, environment, root cause, suggested action, and summary; Priority HIGH; Recipient $vars.MANAGER_USER_ID; Task Definition "Incident Escalation Approval"; Custom Attributes auto-detected from incident JSON (incident_id, severity, root_cause_category, etc.). Required variable: set MANAGER_USER_ID in the n8n environment with the SAP user ID of the approving manager](images/sj219-12-manual-step-in-workflow.png)

![Add Task Center node, earlier step in this same sequence](images/sj219-11-add-task-center-node.png)
![SAP Agent node selection detail](images/sj219-14-sap-agent-node-selection.png)

> [!TIP]
> This changes what a P1/P2 escalation means: before this addition, a high-severity incident went straight to PagerDuty, Slack, and ServiceNow automatically. After it, the branch now **pauses for a manager's approval via SAP Task Center first** — the exact same node-based pattern this book has seen as a pre-hook or post-hook on an Agent extension, here applied as an inline approval gate inside an n8n workflow's own escalation branch.

## 5. Added by Claude, not from the sources

- The CAUTION in section 3 (errors escalate to P1 rather than fail silently) is this book's own reading of the Global Error Handler branch, transcribed directly from the build summary.
- The TIP in section 4 drawing the parallel between this inline approval gate and the pre-hook/post-hook pattern from [Tutorial 14](joule-studio-tutorial-14-journal-entry-agent-extension.md) and [Tutorial 18](joule-studio-tutorial-18-ap-invoice-agent-extension.md) is this book's own cross-reference across tutorials — the node configuration itself is transcribed directly from the source screenshot.
- Not run: the workflow described was built and tested by the tutorial's own author; nothing was independently re-executed for this book.

## 6. Interview corner

**What interviewers listen for:** you can trace a P1 incident through the full pipeline from webhook to ServiceNow ticket including the later-added approval gate, and you know what the Global Error Handler actually does differently from normal routing.

<details class="qa"><summary>1. What happens to a P1/P2 incident after the SAP Task Center node was added, that didn't happen before?</summary>

- It now pauses for a manager's approval via SAP Task Center before proceeding to PagerDuty, Slack, and ITSM — previously the branch went straight to those 3 steps automatically

</details>

<details class="qa"><summary>2. What does the Global Error Handler actually do when the workflow itself fails?</summary>

- It routes the execution error to "Escalate Error Ticket," which creates a ServiceNow P1 ticket and flags it as error-escalated — a pipeline failure is treated with P1 urgency, not logged and ignored

</details>

<details class="qa"><summary>3. How was the SAP Task Center node added to a workflow that was already fully built?</summary>

- Through the canvas's own "What happens next?" search box — typing "sap Agent" surfaced SAP-specific node types (SAP Agent, SAP Joule Content Agent, SAP AI Core Management) that could be inserted directly, without hand-editing the exported workflow JSON

</details>

> [!TIP]
> **🧩 Design question**
> *"An IT ops lead asks why the auto-resolution branch for low-severity incidents doesn't also get a manager-approval gate, the way the P1/P2 branch now does."* Talk about: the PRD's own stated value proposition — "reduced alert fatigue through intelligent routing and auto-resolution of low-severity events" — gating every auto-resolution behind manual approval would defeat the purpose of automating the low-risk case, whereas the P1/P2 branch's real-world consequences (paging someone, opening a high-priority ServiceNow ticket) justify the added approval step that was inserted later.

## Cheat sheet

| Thing | Detail |
|---|---|
| Workflow | 17 nodes, `incident-triage-auto-routing.n8n.json` |
| Severity classification | Keyword rules, 50+ terms per P1–P4 tier |
| Root cause detection | 4 categories × 15+ keywords each, defaults to `unknown` |
| Routing | P1/P2 → escalation; auto_resolve → auto-close; fallback → log-analysis |
| Error handling | Any execution error → ServiceNow P1 ticket, flagged error-escalated |
| Later addition | SAP Task Center manager-approval gate, inserted via "What happens next?" search |

## Recap

- This 17-node n8n workflow normalizes, classifies, and routes IT incidents end-to-end, generating ServiceNow tickets and PagerDuty/Slack alerts automatically
- The Global Error Handler treats a pipeline failure as a P1-severity event in its own right, escalating rather than silently logging it
- A finished workflow can be extended afterward through the canvas's own "What happens next?" node-search box, which inserted a SAP Task Center manager-approval node directly into the P1/P2 escalation branch
- That addition changed the escalation branch's behavior: high-severity incidents now pause for manager approval before PagerDuty, Slack, and ITSM fire

## Practice

1. Without looking back, walk through the full pipeline a P1 incident takes from webhook receipt to ServiceNow ticket
2. Explain what the Global Error Handler does differently from the main routing logic
3. Describe how the SAP Task Center approval node was added to an already-finished workflow

## How this chapter was checked

- The full tutorial "Build an IT Incident Triage and Auto-Routing Workflow" (developers.sap.com, Beginner, 20 min) was read in full, 13 Nov 2026.
- 15 images were found and downloaded, all used here; each was opened and visually verified against its caption before being written into this chapter, including the full workflow architecture summary and the later SAP Task Center node addition, both transcribed directly.
- Nothing in this chapter was independently re-executed — the workflow described was built and tested by the tutorial's own author.

## Sources and further reading

- SAP Developers, *Build an IT Incident Triage and Auto-Routing Workflow* — https://developers.sap.com/tutorials/it-incident-triage-n8n-workflow (read in full 13 Nov 2026)

Previous: [Joule Studio tutorial 23: an HR Virtual Assistant](joule-studio-tutorial-23-hr-onboarding-assistant-agent.md) · Next: [Joule Studio tutorial 25: an Equipment Troubleshooting agent](joule-studio-tutorial-25-equipment-troubleshooting-agent.md)
