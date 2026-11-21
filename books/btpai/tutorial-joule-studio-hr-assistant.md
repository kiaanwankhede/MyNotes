# Tutorial: Build an HR assistant with intent-based development

*In the new Joule Studio, a one-sentence intent becomes a tested HR agent: intent, requirements, specification, code, tests and an optional deployment.*

> [!NOTE]
> **📍 At a glance**
> - **SAP tutorial:** [Use Joule Studio to Create an HR Onboarding Assistant](https://developers.sap.com/tutorials/joule-studio-hr-onboarding-assistant.html)
> - **You will build:** an *HR Virtual Assistant* agent that answers HR questions, analyses simulated workforce data and flags attrition risks
> - **You need:** Joule Work and the new Joule Studio. SAP's page says it is written for its pre-release Agent Lab, so screens may differ
> - **Level:** beginner · **Time:** about 20 minutes (SAP's estimate)
> - **Course use:** reference only. The class used the C_JSD practice system, and access to the new Studio was limited (Lecture 10)
> - **Concepts:** [The new Joule Studio](joule-studio-intent-based.md), 20.2 to 20.4

**After this tutorial you can:**

- Start an agent with Quick Create from an intent statement
- Follow and review each phase's output
- Try the agent, read its test results and deploy it

## 27.1 What you build

```mermaid
flowchart LR
    I["Intent statement<br/>+ Quick Create"] --> IN["Intent<br/>Idea Board, intent fit"]
    IN --> R["Requirements (PRD)"]
    R --> S["Specification<br/>specification.md files"]
    S --> SO["Solution<br/>code · Try tab"]
    SO --> T["Testing<br/>automated suite"]
    T --> D["Deploy to SAP BTP<br/>Try now via A2A (optional)"]
```

## 27.2 Steps

*Steps and screenshots adapted from SAP's tutorial (© SAP SE, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)). Steps reworded; screenshots resized; an email address and an endpoint address blurred.*

> [!WARNING]
> **Pre-release screens**
> - SAP wrote this tutorial for a pre-release Joule Studio in its Agent Lab: screens, names and features may change, and it is for learning only.
> - The tool generates new text and code on every run, so your questions, documents, file names and scores will differ from the screenshots.

- **Two ways through.** SAP's page offers two paths; each step below shows both:
  - **Quick Create:** the tool runs from intent to tested agent without stopping.
  - **Ideate and Plan:** it asks clarifying questions first and waits for your go-ahead at each phase.

### Step 1: Get started

1. Open **Joule Work** and choose the **Develop** area.
2. On the **Agent** tile, choose **Create**.

    ![Joule Studio's Create a new solution page: Agent, n8n Workflow, Application and Extension tiles; Develop and Agent's Create marked](images/t27-01-010bis-create-solution.png)

3. Keep **New Solution** and fill in:
   - **Name:** `HR Virtual Assistant`
   - **Intent Statement**, SAP's text to paste:

     ```text
     Create an AI agent that acts as an HR virtual assistant, answers employee HR questions,
     analyzes workforce data, predicts attrition risks, and generates actionable insights and
     development recommendations using simulated HCM data.
     ```
4. **Quick Create path:** tick **Quick Create**, then choose **Create**.

    ![Create Agent dialog: New Solution, name, intent statement, Quick Create ticked, then Create](images/t27-02-030-define-solution-details.png)

5. **Ideate and Plan path:** leave **Quick Create** unticked, then choose **Create**.

    ![The same dialog with Quick Create unticked](images/t27-03-03iap-define-solution-details.png)

### Step 2: Intent

- In this phase the tool works out your intent and maps it to SAP's **Reference Business Architecture**.
- It uses **SAP Knowledge Graph**, **SAP LeanIX** and **SAP Domain Models**. *Intent fit* shows how well the proposed solution matches your goal.

**Quick Create path**

1. The tool skips questions and calls its tools straight away: mapping to the reference architecture, discovering APIs and a fit-gap analysis.

    ![Quick Create chat: Called 4 tools (reference architecture mapping, API discovery, metadata update, fit-gap analysis)](images/t27-04-040-intent-tools.png)

2. The intent document is written and the requirements phase starts by itself. Meanwhile, look at the intent on the **Idea Board**.

    ![Idea Board, Intent phase: intent, problem statement, goals, business context, and the recommended solution with intent fit 92%](images/t27-05-040-intent-ready.png)

**Ideate and Plan path**

1. The tool asks a few clarifying questions, such as who the main users are. Answer them with your own judgement.
   - The questions differ each run. A more complex scenario takes longer to generate.

    ![Clarifying question after three tool calls: who are the primary users of this HR virtual assistant?](images/t27-06-041iap-clarifying-questions.png)

2. It then writes the intent document: who it is for, what it does, how it is built, and which gaps it fills in SAP's standard.

    ![The last clarifying question, then intent.md saved with a table of five capabilities](images/t27-07-042iap-intent-created.png)

3. Review the intent on the **Idea Board** (*Intent* tab). To change something, say so in the chat.

    ![Idea Board in Ideate and Plan: intent, goals, the business process tree, and the recommended solution](images/t27-08-040iap-intent-ready.png)

### Step 3: Requirements

**Quick Create path**

1. The tool writes the **product requirements document** (PRD) on its own and moves on to the specification. SAP's tutorial accepts the PRD unchanged.

    ![Idea Board at the Requirement phase; the chat reports product-requirements-document.md saved](images/t27-09-060-create-prd.png)

2. The PRD is markdown. To change it, click the text in the view or edit the file in the **Code** tab.
   - You could stop here and hand the PRD to another team.

    ![The generated PRD: title, purpose and value proposition, and the first must-have requirements](images/t27-10-060-prd-ready.png)

**Ideate and Plan path**

1. When the tool asks, type `Create requirements` in the chat and send it.

    ![Chat: intent summary, then Create requirements typed in and the send button marked](images/t27-11-045iap-ideate-create-requirement.png)

2. Review the PRD as above, edit it if needed, then continue.

### Step 4: Specification

**Quick Create path**

1. The technical **specification** is generated next.

    ![Idea Board at the Specification phase; the chat says all spec files are generated and being executed](images/t27-12-070-create-spec.png)

2. While the solution is being built, open the **Code** tab: the `specification` folder and its sub-folders hold `specification.md` files.

    ![The Specification view: the spec's steps (basic setup, data layer, tools, wiring, instrumentation, testing)](images/t27-13-070-spec-ready.png)

3. The tool works through the tasks in the specification and ticks each one off as done.

    ![Code tab: specification.md for hr-assistant-agent with its task list and file tree](images/t27-14-070a-spec-implemented.png)

**Ideate and Plan path**

1. When the tool asks, type `Create specification` and send it.

    ![Chat: PRD summary table, then Create specification typed in](images/t27-15-065iap-ideate-create-specification.png)

2. Wait until the specification summary appears.

    ![Specification view with steps, and the chat's specification summary of what will be built](images/t27-16-070iap-create-spec.png)

3. Review the `specification.md` files in the **Code** tab, edit them if needed, then continue to the build.

    ![Code tab: specification folder and specification.md opened](images/t27-17-070iap-spec-ready.png)

### Step 5: Solution

**Quick Create path**

1. Wait until the implementation finishes successfully.

    ![Solution phase: Test your Agent, and the chat's summary of the architecture, capabilities and test results](images/t27-18-085-solution-ready.png)

2. Explore the generated code in the **Code** tab if you want to.

    ![Code tab of hr-assistant-agent: the app folder and agent.py](images/t27-19-085iap-solution-code.png)

3. Open the **Try** tab and type in the box that says "Can I help with anything else?".

    ![Try Your Agent: the prompt box marked, with Traces below and the build summary on the right](images/t27-20-085-solution-test.png)

4. Start with *"How can I test this agent?"* for example prompts, then try one, for example *"Show me the profile for employee E001"*.
   - What works depends on what was built in your run.

    ![Try tab: the profile of a simulated employee, E001, flagged as simulated data; traces below](images/t27-21-085-solution-test-2.png)

**Ideate and Plan path**

1. Choose **Build** at the top right, or type `Build solution for this project` when the tool asks.
   - The tool sets up the agent, creates the data and tools, and writes the tests. Follow it on the right.

    ![Chat after Build solution for this project: skills activated, files written, step 1 bootstrapping the agent](images/t27-22-085iap-solution-creation.png)

2. Explore the code in the **Code** tab, as above.
3. On the **Try** tab, ask *"How can I test this agent?"*, then try a prompt such as *"How many vacation days do I get?"*.
   - The right-hand panel summarises what the agent can do; the **Traces** panel at the bottom shows how it handled each request.

    ![Try Your Agent with How can I test this agent? typed in; the build summary on the right](images/t27-23-090iap-try-your-agent.png)

    ![The agent's answer about annual leave days, with suggested prompts above and traces below](images/t27-24-091iap-agent-response.png)

### Step 6: Testing

1. Nothing to do: after the build, Joule Studio runs an automated test suite against the agent.
2. Open the **Testing** tab: total tests, passed and failed, code coverage, an overall score, and results per artifact.
   - If all tests pass, the agent is ready to deploy.

    ![Testing Overview: 58 tests, 58 passed, 0 failed, score 100%, and the hr-assistant-agent artifact at 100%](images/t27-25-092-testing-overview.png)

### Step 7: Deployment (optional)

1. Choose **Deploy** at the top right, then **Deploy** in *Deploy Solution*.
   - SAP's screenshot shows a *Development* sandbox as the target.

    ![Deploy Solution: the Development environment (a sandbox for testing), then Deploy](images/t27-26-08-deploy.png)

2. The tool deploys the agent to SAP BTP. The **Deployment** tab shows the current deployment, its status, and the history.

    ![Deployment tab: HR Virtual Assistant in Development, progressing; deployment history (user email blurred)](images/t27-27-09a-deployment-complete.png)

3. Expand the deployment record and choose **Try now** to talk to the deployed agent over the **A2A** protocol.

    ![Deployment running; Try now marked next to hr-assistant-agent (user email blurred)](images/t27-28-10-try-now.png)

4. Suggested prompts appear; try one of them.

    ![The deployed agent's card: description, endpoint (blurred) and four suggested prompts](images/t27-29-10-try-now-prompts.png)

## 27.3 Why it works

- Each phase writes a document the next one builds on: intent, then requirements, then specification, then code (20.3).
- **Quick Create** chains the phases without stopping; without it you confirm each one.
- **Stopping after the PRD or specification** is a supported hand-over point to another team (20.4).

## 27.4 Things to watch

- **Review the intent and PRD** even in Quick Create; a wrong goal flows into the code (20.4).
- **Simulated data:** the tutorial uses simulated HCM data; a real agent needs real SuccessFactors APIs and HR-grade access control.

> [!IMPORTANT]
> **🏭 In production**
> - HR agents touch personal data: mask what the model does not need, and keep people in decisions about people (chapter 17).
> - Add your own test cases with edge cases before deploying; generated tests check what the tool understood.
>
> *Added by Claude*

## Check yourself

<details class="qa"><summary>What does Quick Create change?</summary>

- It skips clarifying questions and runs from intent to tests without stopping
- You can still review and edit every document afterwards

</details>

<details class="qa"><summary>Where do you see whether the generated agent passed its tests?</summary>

- On the *Testing* tab: tests passed and failed, coverage and an overall score

</details>

## How this page was checked

- **SAP tutorial read in full on 21 Nov 2026** (created May 2026, updated by SAP on 21 Sep 2026; marked pre-release).
- **Steps rebuilt on 21 Nov 2026** from the tutorial's source file, with all 29 of its screenshots (SAP uses three of them twice).
  - SAP's source now has two paths, *Quick Create* and *Ideate and Plan*; both are covered.
  - Every screenshot was checked for personal data. Blurred: a user's email address (two screenshots) and the deployed agent's endpoint address.
- **Lecture 10 Part B recording:** the live build in the C_JSD practice system (0:39 to 1:00) followed the same phases.
- Not run by me: there is no Joule Studio access in this workspace.

## Sources

- SAP Developer Center, *Use Joule Studio to Create an HR Onboarding Assistant*: https://developers.sap.com/tutorials/joule-studio-hr-onboarding-assistant.html
- Tutorial source and screenshots: https://github.com/sap-tutorials/sap-build-process-automation (© SAP SE, licensed CC BY 4.0)
- BTPAI course, Lecture 10 Part B recording (BT022)

Previous: [Tutorial: Create a Joule agent in Joule Studio Classic](tutorial-joule-agent-create.md) · Next: [Tutorial: Extend SAP's AP Invoice Agent](tutorial-joule-studio-agent-extension.md)
