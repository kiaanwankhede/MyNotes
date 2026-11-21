# Tutorial: Extend SAP's AP Invoice Agent

*Add your own rules and follow-up steps to an agent that SAP delivers, without changing it: a post-hook, an instruction and an extra MCP server.*

> [!NOTE]
> **📍 At a glance**
> - **SAP tutorial:** [Use Joule Studio to Extend the AP Invoice Agent using Agent Extensions](https://developers.sap.com/tutorials/joule-studio-agent-extension.html)
> - **You will build:** the extension *AP Notification* for SAP's AP Invoice Agent: a post-hook n8n workflow, a tax-validation instruction and an added MCP server
> - **You need:** Joule Work and the new Joule Studio. SAP built the tutorial for the Sapphire 2026 Agent Lab, a pre-release version
> - **Level:** beginner · **Time:** about 20 minutes (SAP's estimate)
> - **Course use:** reference only. The class extended a different SAP assistant in the C_JSD practice system (Lecture 10)
> - **Concepts:** [The new Joule Studio](joule-studio-intent-based.md), 20.6

**After this tutorial you can:**

- Start an agent extension from an intent
- Add a hook, an instruction and an MCP server to an SAP agent
- Explain why an extension keeps SAP's agent upgradeable

## 28.1 What you build

```mermaid
flowchart LR
    AP["SAP's AP Invoice Agent<br/>(unchanged)"] --> X["Extension: AP Notification"]
    X --> H["Post-hook (n8n)<br/>unmatched invoice →<br/>Task Center task + notification"]
    X --> IN["Instruction<br/>validate tax before approval"]
    X --> M["Extra MCP server<br/>tools the agent may call"]
```

## 28.2 Steps

*Steps and screenshots adapted from SAP's tutorial (© SAP SE, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)). Steps reworded; screenshots resized.*

> [!WARNING]
> **Pre-release screens**
> - SAP wrote this tutorial for the Sapphire 2026 Agent Lab, a pre-release Joule Studio: screens, names and features may change, and it is for learning only.
> - The tool generates new text and code on every run, so your questions, documents and file names will differ from the screenshots.

- **The agent being extended:** SAP's *AP Invoice Agent* automates accounts payable invoices that arrive through EDI, with 2-way, 3-way and ERS matching.

### Step 1: Getting started

1. Go to **Joule Work**. If you do not see the tiles, choose **<> Develop**.
2. On the **Agent Extension** tile, choose **Create**.

    ![Create a new solution: Agent, n8n Workflow, Application and Agent Extension tiles; Agent Extension's Create marked](images/t28-01-joule-work-01.png)

3. In *Create Extension*, choose **Agent Extension**.
   - The other types are *Agent Skill* and *Custom Data Fields*.

    ![Create Extension dialog: Agent Extension marked; Agent Skill and Custom Data Fields are the other choices](images/t28-02-joule-work-01a.png)

4. Keep **New Solution** and fill in:
   - **Name:** `AP Notification`
   - **Intent Statement**, SAP's text to paste:

     ```text
     Create an extension to the AP Invoice Agent. Add a post-hook n8n workflow.
     For any invoice that cannot be matched: Create a SAP Task Center task.
     Send a notification to the responsible AP team member via SAP Task Center.
     ```

    ![Create Agent Extension dialog: name AP Notification, the intent statement, Quick create unticked, then OK](images/t28-03-joule-work-02.png)

5. Choose **OK**. Your intent statement becomes the first prompt in the chat on the right.
   - The tool finds the AP Invoice Agent by itself and starts creating the extension.

    ![Solutions list with Ap notification; the chat maps the request to SAP's reference architecture and finds the AP Invoice Agent](images/t28-04-joule-work-03.png)

### Step 2: Intent

- The tool tries to understand your goal and will likely ask clarifying questions.
- Then it maps the goal to SAP's **Reference Business Architecture** and runs a **fit-gap analysis**, using SAP Knowledge Graph, SAP LeanIX and SAP Domain Models. *Intent fit* shows how well the solution matches the goal.

1. Answer the tool's questions with your own judgement. It may offer answers to pick from.
   - The questions cannot be predicted.
   - The landscape has **S/4HANA** as its backend, so answer with that in mind.
   - A more complex scenario takes longer to generate and test.

    ![The tool asks how the responsible AP team member should be identified; By company code is selected](images/t28-05-joule-work-04.png)

2. When the intent document is ready, requirements come next. If the tool waits for you, type **Create Requirement** or similar.
3. While the requirements are generated, look at the intent on the **Idea Board**.

    ![Idea Board for Ap notification: intent, problem statement, goals, business context, and the recommended extension (intent fit 92%)](images/t28-06-idea-board-01.png)

### Step 3: Requirement

1. Review the **PRD**, shown as markdown. SAP's tutorial accepts it unchanged.
   - To change it, click the text in the view or edit the file in the **Code** tab.
   - You could stop here and hand the PRD to another team.

    ![The PRD for the AP Invoice Agent extension: title, purpose and value proposition, business need, expected value](images/t28-07-requirement-01.png)

### Step 4: Solution

1. Wait until the build finishes. The **Solution** tab shows the extension, built as a **post-hook n8n workflow**.

    ![Solution tab: the n8n workflow diagram, and the chat's summary of the extension with its post-hook settings](images/t28-08-solution-01.png)

2. Open the n8n workflow's code if you want to (**Code** tab, under `workflows`).
   - The post-hook extension is now complete.

    ![Code tab: the generated files, with the n8n workflow JSON for unmatched invoices opened](images/t28-09-solution-02.png)

**Add an instruction**

3. Open the **Design** tab and choose **Edit** under **Instructions and Context**.
   - Here you add your own context, rules and guidance to the agent's prompt.

    ![Design tab: AP Invoice Agent, Instructions and Context with Edit marked, Extensions (MCP Servers) and Hooks (1 hook)](images/t28-10-solution-03.png)

4. Add SAP's tax-validation instruction (exact text on SAP's page). In short:
   - Always validate tax on pending invoices with the `validate-tax` tool before recommending approval.
   - ERROR or BLOCK: flag as not approvable. WARNING: note the discrepancy and allow with a warning. OK: safe to approve.
   - Watch for international vendors charging domestic tax rates on cross-border shipments.

    ![The instruction editor with the five-line tax-validation policy entered](images/t28-11-solution-04.png)

**Add an MCP server**

5. On the **Design** tab, under **Extensions → MCP Servers**, choose **Add Server**.

    ![Design tab: MCP Servers (0 servers) with Add Server marked](images/t28-12-solution-05.png)

6. The *MCP Server Catalog* lists the available servers. On **Tax Validator MCP Server**, choose **View Details**.

    ![MCP Server Catalog, SAP Catalog tab: Tax Validator MCP Server with View Details marked](images/t28-13-solution-06.png)

7. The details list its three tools and what they do: `validate-tax`, `lookup-tax-rate` and `compare-invoices`. Choose **Add MCP Server**.

    ![Tax Validator MCP Server: three tools (validate-tax, lookup-tax-rate, compare-invoices), then Add MCP Server](images/t28-14-solution-07.png)

8. The extension now has all three parts: the instruction, the MCP server and the post-hook.

    ![Design tab: Additional Context with the tax policy, one MCP server, and one post-hook](images/t28-15-solution-08.png)

**Deploy**

9. In the Agent Lab the extension is not deployed. In a normal tenant, **Deploy** would send it to the runtime.

## 28.3 Why it works

- An **extension** sits on top of SAP's agent, so SAP can still update the agent underneath (20.6).
- A **post-hook** runs after the agent, in a fixed order: right for a step that must always happen. An **MCP tool** is something the agent may choose to call.
- **Instructions and context** change how the agent decides, without code.

## 28.4 Things to watch

- **Which extension points exist** depends on the agent; the dialog shows them for the agent you pick.
- **Keep the intent small.** SAP's tutorial warns that a more complex scenario takes longer to generate and test.

> [!IMPORTANT]
> **🏭 In production**
> - Test the extension with matched, unmatched and borderline invoices, and with tax errors and warnings, before go-live.
> - Review an added MCP server like any integration: which user it calls with, and what it can change.
>
> *Added by Claude*

## Check yourself

<details class="qa"><summary>Why a post-hook rather than an extra tool for the Task Center task?</summary>

- A hook runs every time, after the agent, in a fixed order
- A tool runs only when the agent decides to call it

</details>

<details class="qa"><summary>What does an extension leave untouched?</summary>

- SAP's agent itself; your changes sit in the extension, so SAP updates still apply

</details>

## How this page was checked

- **SAP tutorial read in full on 21 Nov 2026** (created May 2026, updated by SAP on 21 Aug 2026; marked pre-release).
- **Steps rebuilt on 21 Nov 2026** from the tutorial's source file, with all 15 of its screenshots.
  - Every screenshot was checked for personal data; none needed blurring. The address `ap-team@company.com` in them is a generated placeholder.
- **Lecture 10 Part B recording:** the extension demo in the C_JSD practice system (1:04 to 1:12) used the same dialog.
- Not run by me: there is no Joule Studio access in this workspace.

## Sources

- SAP Developer Center, *Use Joule Studio to Extend the AP Invoice Agent using Agent Extensions*: https://developers.sap.com/tutorials/joule-studio-agent-extension.html
- Tutorial source and screenshots: https://github.com/sap-tutorials/sap-build-process-automation (© SAP SE, licensed CC BY 4.0)
- BTPAI course, Lecture 10 Part B recording (BT022)

Previous: [Tutorial: Build an HR assistant with intent-based development](tutorial-joule-studio-hr-assistant.md) · Next: [Tutorial: Bring SAP Analytics Cloud insights into Joule](tutorial-joule-sac-analytical-insights.md)
