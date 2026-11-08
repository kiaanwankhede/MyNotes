# Chapter 11: Joule in SAP Build Code, for ABAP developers, and in Joule Work

*Set up SAP Build Code, generate a CAP app from a user story, switch Joule on for an existing CAP project, see what Joule does for ABAP developers, and meet Joule Work.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how to set up SAP Build Code on a BTP trial, how prompt-driven CAP development works, how to enable Joule in an existing CAP project, the list of Joule features for ABAP, what the consultant course and the fusion-app sample cover, and what Joule Work and Spaces are
> - **Level:** beginner to intermediate · **Time:** about 40 minutes of reading
> - **Sources:** two SAP Community blogs, one member blog, one SAP Community blog on ABAP, two SAP Developer tutorials, one course landing page and one GitHub README, read 8 November 2026
> - **Builds on:** [Chapter 10](10-pro-code-agents-a2a.md)

**After this chapter you can:**

- Run the Build Code booster and check the two subscriptions
- Generate a CAP application with `/cap-gen-app` from a user story
- Enable Joule in a CAP project made with `cds init`
- Name the Joule features for ABAP Cloud development
- Explain what a Space in Joule Work is

> [!WARNING]
> **What this chapter is**
> - Notes from tutorials and blogs; **I ran nothing**
> - **Licensing dates in the ABAP blog contradict each other** (see 11.4); check SAP Note 3571857 before you rely on them
> - SJ048, SJ051 and SJ052 could not be read (dead or redirected links); they are not in this chapter
> - Screenshots of SJ058 and of the SJ053 quiz were **not viewed**

> [!CAUTION]
> **Credentials**
> - Nothing here needs a secret in your notes. Use your own trial account and keep logins out of files

## 11.1 Set up SAP Build Code on a trial (SJ053)

*Source: SAP Developer tutorial "Setup SAP Build Code in SAP BTP", 10 minutes, 2 steps (text read).*

- **Before you start:** a BTP trial account in region **US10** (the trial is only offered there)
- **Step 1, run the booster:**
  - In the trial account, **unsubscribe from SAP Business Application Studio** first
  - Projects made in it are lost, so back them up
  - Open **Boosters**, search "SAP Build Code" (one booster per service plan) and run it
  - The booster checks authorizations, providers and regions; then choose **Navigate to Subaccount**
- **Step 2, verify:**
  - Go to **Services → Instances and Subscriptions**
  - Check you have subscriptions to **SAP Business Application Studio** and **SAP Build Code**
  - Open SAP Build Code to reach the **Build lobby**

> [!IMPORTANT]
> The booster adds roles in the **default IdP** only. With a custom IdP you may also need the roles **Build Code Administrator** and **Build Code Developer**.

## 11.2 Prompt-driven development of a CAP app (SJ050)

*Source: SAP Community blog "Prompt-driven development: full-stack CAP apps from a user story" (text read).*

- **Prerequisites:** free BTP trial plus SAP Build Code (11.1)
- **Create the project:**
  - In the Build lobby: Application → Full-Stack → **full-stack Node.js**
  - The blog names it "Contract Management"
- **Generate:**
  - Open the project in Business Application Studio and open **Joule** from the activity bar
  - Type the slash command **`/cap-gen-app`** and paste the **whole user story**
  - Joule splits the work into steps, each with a suggested prompt
  - Replace each step's text with the complete user story, run, and accept the code
- **Add a UI:** ask for a Fiori elements app, run it, open the contract list and then a contract
- **The sample story:**
  - A contract administrator manages contracts and "parties involved"
  - Two acceptance scenarios: list all contracts without pressing Go; view contract details
- **Claim in the blog:** days of work shrink to minutes (the author's claim, not measured here)

## 11.3 Joule in an existing CAP project (SJ054)

*Source: member blog "Enabling support for existing CAP projects in SAP Build Code", an English translation (text read).*

- **Problem:** in a project made with `cds init`, Joule shows **Not Available**; only lobby or low-code projects are supported
- **Fix:** add `"lcap": true` to `package.json`
  - Works for **CAP Node.js only**, not Java
- **Steps:**
  1. `cds init`
  2. Add the setting
  3. Install the low-code event handler module (the generated code uses it)
  4. Refresh the browser and open Joule
- **Checked in the blog** by adding `cds add tiny-sample`, generating logic with Joule and deploying to Cloud Foundry

> [!CAUTION]
> - Joule cannot be used with **existing `.js` event handler files** (it shows "Open Guide")
> - Adding logic from the Graphical Modeler **overwrites existing sources**: back them up first

## 11.4 Joule for ABAP developers (SJ055)

*Source: SAP Community blog "Joule for Developers" (text and one licensing diagram read; some text on the page is cut with "...").*

- **Where:** ABAP Cloud full-stack development, built into ABAP Development Tools for Eclipse (the blog links to VS Code as well)
- **Features listed:**

| Feature | What it does |
|---|---|
| Joule Chat | Ask questions in the IDE |
| Predictive code completion | Model fine-tuned from StarCoder 2 on SAP ABAP |
| Explain | Explains code, including ATC findings |
| Documentation chat | Answers from SAP Help |
| ABAP Unit generation | Tests with test doubles and dependency analysis |
| CDS unit tests | Same idea for CDS |
| OData UI service | Builds a RAP business object from scratch |
| RAP logic prediction | Determinations and validations via quick fix |
| Consume | Generates OData client proxy code |
| Embedded analytics | Star-schema generator |
| Extensibility assistant | GenAI-driven |
| Custom code migration | AI assistant in a Fiori app |

> [!WARNING]
> **Licensing: the blog contradicts itself**
> - It says a free promo runs "until October 2026", and also that the promo was **sunset on 1 June 2026**
> - After the promo it is a premium AI feature on a new **AI-unit** licence (parent SKUs: customer 8019164, partner 8019670)
> - It cites SAP Notes 3571857 and 3740750. **Verify there before you tell a customer anything**
> - The diagram (small text) shows commercial level "SAP for Me" and ABAP AI consumption, with benefits: cost efficiency, transparency and control, elastic usage, scalability

## 11.5 Joule Work and Spaces (SJ058)

*Source: SAP Developer tutorial "Get productive with Joule Work", 15 minutes, 6 steps, by DJ Adams (text read; screenshots not viewed).*

- **Platform:** the **SAP Business AI Platform (BAIP)** joins BTP and Business Data Cloud to build, run and scale agents and apps
- **Joule Work:** a central workspace where agents do the busywork
- **Needs:** a BTP global account, a subaccount with a Cloud Identity Services tenant, Joule Work Desktop access and an activated BAIP trial
- **The scenario:** a demand and supply planner compares production actuals (S/4HANA) with the IBP forecast; data is sample data
- **Steps:**
  1. Ask in plain language: "Show me production actuals vs IBP forecast for Q3". The forecast uses **SAP RPT 1.5**, a tabular AI model
  2. Save the result card to a **Space** (for example "Q3 Production Review"); Spaces are dashboards that persist between sessions
  3. Inside the Space, call an agent with `@planning-agent` and pin its output as a card
  4. Ask a follow-up ("live production rates on Line 4"): Joule says the data is **not available** instead of guessing
- **Takeaway:** a Space ties conversations and agent results to one business goal

## 11.6 The consultant course and the fusion-app sample (SJ056, SJ057)

- **SJ056, "Introducing SAP Joule for Consultants" (landing page only):**
  - 1 h 14 min, beginner, two units: "Discovering SAP Joule for Consultants" (5 lessons, 37 min) and "Applying SAP Joule for Consultants" (5 lessons, 37 min)
  - **The ten lessons were not opened**
- **SJ057, GitHub sample (README only):** now in the **SAP-archive** organisation
  - Scenario: a mobile app built in SAP Build Apps talks to a CAP backend (Build Code with Joule) and a RAP backend (ABAP environment)
  - Story: a technician reports a faulty device; an admin assigns a processor; RAP calculates the processor's location from latitude and longitude stored in CAP
  - Three modules: (1) Build Code with Joule, (2) RESTful ABAP service, (3) SAP Build Apps with a customer web app and an admin web app
  - **The module folders were not read**

## 11.7 Added by Claude, not from the sources

*My own reasoning; the sources do not say it.*

- **Paste the whole story each time:** the blog's trick (full story in every step) keeps the generated parts consistent
- **Commit before you let Joule write:** the overwrite warnings in 11.3 are a reason to use git first
- **Treat "days to minutes" as marketing** until you time it yourself
- **Joule saying "data not available"** is the behaviour you want from an agent; test for it on purpose

## 11.8 Interview corner

**What interviewers listen for:** you know the set-up, the slash command, the limits and the ABAP features.

<details class="qa">
<summary>🟢 Which command starts CAP generation in Joule?</summary>

- `/cap-gen-app`, in Joule inside Business Application Studio, with the full user story
</details>

<details class="qa">
<summary>🟡 Joule says "Not Available" in your CAP project. Why, and what do you do?</summary>

- The project was made with `cds init`; add `"lcap": true` to `package.json` (Node.js only) and install the low-code event handler module
</details>

<details class="qa">
<summary>🟡 Name four Joule features for ABAP developers.</summary>

- Chat, code completion, Explain, ABAP Unit generation (also RAP logic prediction, Consume, CDS tests)
</details>

<details class="qa">
<summary>🔴 A colleague says Joule for ABAP is free. How do you answer?</summary>

- The blog is inconsistent about the promo end date; after the promo it is an AI-unit licence. Check the SAP Notes
</details>

<details class="qa">
<summary>🔴 What is a Space and why use one?</summary>

- A persistent dashboard of cards from conversations and agents, tied to one business goal
</details>

**🧩 Design question:** a team has an existing CAP Node.js service with hand-written `.js` handlers and wants Joule help. What do you check, what do you back up, and what do you expect to fail?

## 11.9 Discovery Center missions (links, not read)

- [Build custom Joule skills for SAP and non-SAP systems](https://discovery-center.cloud.sap/missiondetail/4643/)

## 11.10 Cheat sheet

| Topic | Remember |
|---|---|
| Trial region | US10 |
| Set-up | Unsubscribe BAS, run the Build Code booster, check two subscriptions |
| Custom IdP | Add Build Code Administrator and Developer roles |
| Generate CAP | `/cap-gen-app` plus the full story |
| Existing CAP | `"lcap": true`, Node.js only |
| ABAP | Chat, completion, Explain, tests, RAP prediction |
| Joule Work | Conversation, Space, `@agent` |

## Recap

- Set up Build Code with the booster, then verify the two subscriptions
- Prompt-driven CAP: one slash command, one full user story
- Existing CAP projects need one flag and a module; back up first
- Joule for ABAP has many features, but check the licence
- Joule Work Spaces keep results together

## Practice

1. List the set-up steps from memory, including what you unsubscribe first.
2. Write a user story with two acceptance scenarios for a different app.
3. Fill the ABAP feature table without looking.
4. Describe a Space for a task of your own.

## How this chapter was checked

- **Read fully:** the text of SJ050, SJ053, SJ054, SJ055 and SJ058; the SJ057 README; the SJ056 landing page
- **Not read:**
  - SJ048, SJ051, SJ052 (dead or redirected links)
  - the ten lessons of SJ056
  - the module folders of SJ057
  - screenshots of SJ058 and the answer options of the SJ053 quiz
  - linked blogs, SAP Notes, Discovery Center missions
- **Not run:** nothing was built or deployed
- **Dated points:** the ABAP licensing dates in SJ055 contradict each other

## Sources and further reading

- SAP Community blog, *Prompt-driven development: full-stack CAP apps from a user story* (read): https://community.sap.com/t5/technology-blog-posts-by-sap/prompt-driven-development-building-full-stack-sap-cap-apps-from-user/ba-p/14288653
- SAP Developer tutorial, *Setup SAP Build Code in SAP BTP* (read): https://developers.sap.com/tutorials/build-code-setup
- Member blog, *Enabling support for existing CAP projects in SAP Build Code* (read): https://groups.community.sap.com/t5/technology-blogs-by-members/enabling-support-for-existing-cap-projects-in-sap-build-code/ba-p/13676571
- SAP Community blog, *Joule for Developers* (read): https://community.sap.com/t5/technology-blog-posts-by-sap/joule-for-developers/ba-p/14420721
- SAP Learning course, *Introducing SAP Joule for Consultants* (landing page read): https://learning.sap.com/courses/introducing-sap-joule-for-consultants
- GitHub, *btp-s4hana-buildcode-rap-buildapps* (README read): https://github.com/sap-samples/btp-s4hana-buildcode-rap-buildapps
- SAP Developer tutorial, *Get productive with Joule Work* (text read): https://developers.sap.com/tutorials/trial-get-productive-with-joule-work
- Discovery Center missions: see 11.9

---

*Previous: [Chapter 10: Pro-code agents and the A2A protocol](10-pro-code-agents-a2a.md)*
