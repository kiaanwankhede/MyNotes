# Tutorial: Filter an action and let Joule write the reply

*Add a filter to an action so a skill can search employees by first name, and let Joule compose the answer instead of a fixed message.*

> [!NOTE]
> **📍 At a glance**
> - **SAP tutorial:** [Create a Filter in an Action Project](https://developers.sap.com/tutorials/joulestudio-skill-action-filter.html) (part 4 of 5)
> - **You will build:** a copy of the business partner action project with a `FirstName` filter, and the skill *SearchWithFirstName*
> - **You need:** tutorials [21](tutorial-joule-skill-setup.md) and [22](tutorial-joule-action-projects.md)
> - **Level:** beginner · **Time:** about 20 minutes (SAP's estimate)
> - **Concepts:** [Joule Studio Classic](joule-studio-classic.md), 19.4 and 19.4a

**After this tutorial you can:**

- Copy a published action project into a new one
- Add an input field to an action and use it in an OData `$filter`
- Build a skill whose reply Joule writes itself from the outputs

## 24.1 What you build

```mermaid
flowchart LR
    U["'Is Jane in the system?'"] --> SK["Skill SearchWithFirstName<br/>input FirstName*"]
    SK --> A["Action: business partners<br/>$filter = FirstName eq ${FirstName}"]
    A --> E["End<br/>output Employees (list)"]
    E --> J["Joule writes the answer<br/>and lists the matches"]
```

## 24.2 Steps

*Steps and screenshots adapted from SAP's tutorial (© SAP SE, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)). Steps reworded; screenshots resized; a user's name blurred in one of them.*

### Step 1: Copy the business partner action project and add a filter

1. Open the **SAP Build lobby** and choose **Connectors → Actions**.
2. Select your business partner action project from tutorial 22 and open its **Versions** tab.
3. Choose **…** next to the version marked *Published to Library*, then **Save As New Project**.

    ![Actions list: the business partner project selected, its Versions tab, and Save As New Project in the menu of the published version](images/t24-01-action1.png)

4. Enter the project name `FilterBusinessPartners` and a description, then choose **Save As New**.
   - SAP's description: "This is to give Joule access to information about business partners. An extra input field is added to simplify the use of the filter."

    ![Save As New Project dialog: project name FilterBusinessPartners and its description, then Save As New](images/t24-02-action2.png)

5. Open the new project from the list.

    ![Actions list now showing three projects, with the new FilterBusinessPartners project marked](images/t24-03-action3.png)

6. Select the action **GET Retrieves business partner general data**. On the **Input** tab, choose **Add**.
   - The action already has the standard OData query options: `$top`, `$skip`, `$filter`, `$orderby` and `$inlinecount`.

    ![Input tab of the list action: the five OData query parameters, and the Add button marked](images/t24-04-action4.png)

7. Choose **New Field**. Enter `FirstName` as the **Key** and as the **Label**, then choose **Add**.
   - Leave the other settings: *Parameter* custom, *Type* string, *Mandatory* and *Static* off.

    ![Add New Field: New Field tab, key FirstName, parameter custom, type string, label FirstName, then Add](images/t24-05-action5.png)

8. Click the **Value** cell of `$filter`. In the `$filter` side panel, click the **Value** field to open the filter editor.

    ![The parameter list with the new FirstName row; the $filter value cell and the Value field in its side panel are marked](images/t24-06-action7.png)

9. In *Apply Filters* (*Condition Editor* tab), set:
   - **Column:** `FirstName`
   - **Condition:** `equal to`
   - **Criteria:** `${FirstName}`, the new input field
   - Choose **OK**.

    ![Apply Filters, Condition Editor: FirstName, equal to, ${FirstName}](images/t24-07-action9.png)

10. Open the **Test** tab, enter `Jane` in **FirstName**, and choose **Test**.
    - Only Jane Roe (business partner 1003765) comes back, instead of the whole list.

    ![Test tab: destination S4HANA_MOCK, FirstName Jane, Test; the response holds one result, Jane Roe 1003765](images/t24-08-action12.png)

11. Choose **Save**, then **Release**, then **Publish**.
    - The published project shows `$filter` with the value *Conditions Applied*.

    ![The published FilterBusinessPartners project: $filter now shows Conditions Applied, and FirstName is a custom input](images/t24-09-action13.png)

### Step 2: Create the skill

1. Go back to the **SAP Build lobby** and choose **Create**.

    ![SAP Build lobby listing the CreateBadge project from tutorial 23, with the Create button marked](images/t24-10-skill1.png)

2. Choose the **Joule Skill** tile, then **Next**.

    ![Create Project, Objective: the Joule Skill tile selected, then Next](images/t24-11-skill2.png)

3. Enter the project name `SearchWithName` and the description "Uses an Action containing a mapped condition to filter on the FirstName." Choose **Review**, then **Create**.

    ![Create Project, Name: project SearchWithName and its description, then Review](images/t24-12-skill3.png)

4. In Joule Studio, choose **Create → Joule Skill**.

    ![The SearchWithName project overview: Create menu open with Joule Skill marked](images/t24-13-skill6.png)

5. Enter the name `SearchWithFirstName` and the description "Retrieve information about employees with a given first name. Usually John or Jane is used". Choose **Create**.

    ![Create Joule Skill dialog: name SearchWithFirstName, identifier, description, then Create](images/t24-14-skill7.png)

6. Click **Trigger** to open the side panel, and switch **on** *Allow Joule to generate a response*.
   - This is the opposite of tutorial 23: Joule writes the reply, so no *Send Message* step is needed.

    ![Trigger side panel: name and description filled in, Allow Joule to generate a response switched on](images/t24-15-skill10.png)

7. Open **Parameters** and choose **Configure** next to *Skill Inputs*.

    ![Parameters tab: Configure next to Skill Inputs marked](images/t24-16-skill10c.png)

8. Choose **Add Input**: name `FirstName`, description "First name of employee", **Required** ticked. Choose **Apply**.

    ![Configure Skill Inputs: FirstName, First name of employee, Required ticked, then Apply](images/t24-17-skill12.png)

9. Choose **Configure** next to *Skill Outputs*.

    ![Parameters tab: Configure next to Skill Outputs marked](images/t24-18-skill12c.png)

10. Choose **Add Output** and enter:
    - **Name** and **Description:** `Employees`
    - **Type:** `Any`
    - **List:** ticked, because the search can find several people
    - Choose **Apply**, close the side panel, and choose **Save**.

    ![Configure Skill Outputs: Employees, type Any, List ticked, Required not ticked](images/t24-19-skill12b.png)

### Step 3: Add the filtered action

1. Choose the **+** between *Trigger* and *End*, then the action option.
   - SAP's text says *Action*; the screen shows **Call Action**.

    ![Choose what happens next, with Call Action marked](images/t24-20-skill14.png)

2. Choose **Browse All Actions**.

    ![The Action panel with Browse All Actions marked](images/t24-21-skill15.png)

3. Find **GET Retrieves business partner general data** from the project **FilterBusinessPartners** and choose **Add**.
   - Check the project name under each entry: the same action also exists in the original project.

    ![Browse library: two general-data actions; the one from FilterBusinessPartners is marked](images/t24-22-skill16.png)

4. Open **Destination Variable**, choose **+ Create Destination Variable**, enter `S4HANA_MOCK` and "BusinessPartner API", then **Create**. Select the variable.

    ![The action step: Destination Variable S4HANA_MOCK selected](images/t24-23-skill17.png)

5. Open the **Inputs** tab and click the **FirstName** field. In *Skill Content*, choose the skill input **FirstName**.
   - The other inputs (`$filter`, `$top` and so on) stay empty; the filter is built from `FirstName`.

    ![Inputs tab of the action: FirstName mapped to the skill input FirstName; the OData parameters left empty](images/t24-24-skill20.png)

6. Open the **Outputs** tab to see the result: a `list - results` with `BusinessPartner`, `FirstName` and `LastName`.
7. Close the panel and choose **Save**.

    ![Outputs tab: result > Collection of A_BusinessPartnerType > list - results with the three fields](images/t24-25-skill21.png)

### Step 4: Map the output at End

1. Click **End**, then click the **Employees** field.
2. In *Skill Content*, choose **list - results** from the action's result.
3. Choose **Save**.

    ![End step: Employees mapped to list - results from the action's result](images/t24-26-skill22.png)

### Step 5: Release and deploy

1. Choose **Release**, then **Release** in the dialog.

    ![Release Project dialog over SearchWithFirstName: version 1.0.0, then Release](images/t24-27-release2.png)

2. Choose **Show project version** to switch to the released version.

    ![Message: SearchWithName 1.0.0 released, with the Show project version link](images/t24-28-release3.png)

3. Choose **Deploy**, select your environment, and choose **Deploy**.

    ![Deploy: Choose an Environment with tutorial selected, then Deploy](images/t24-29-deploy1.png)

4. Choose your `S4HANA_MOCK` destination for the variable and choose **Deploy**. The project shows **Deployed** and **Active**.

    ![SearchWithName 1.0.0 Deployed and Active, with the SearchWithFirstName skill listed](images/t24-30-deploy2.png)

### Step 6: Test the skill

1. In the lobby choose **Control Tower → Environments**, open your environment and its **Joule** tab.
   - Both skills are listed now: `SearchWithName` and `CreateBadge`. Choose **Launch**.

    ![The environment's Joule tab listing SearchWithName and CreateBadge, version 1.0.0 each; Launch marked](images/t24-31-test5.png)

2. Joule opens on your last conversation. Choose **New Conversation**.

    ![Standalone Joule showing the earlier badge conversation, now expired, with New Conversation](images/t24-32-test6.png)

3. Send: *"I am at the front desk in the reception area. A person claiming to be an employee is here. Can you check if Jane is in the system?"*

    ![A new conversation with the reception question typed in (the user's name is blurred)](images/t24-33-test8.png)

4. Joule calls the skill and writes the answer itself: an *Employee Information* card for Jane Roe, business partner 1003765.

    ![Joule's reply: Employee Information, verification of employee Jane Roe, business partner 1003765](images/t24-34-test9.png)

5. Send: *"Thanks, I meant you to check if John is in the system."*
   - This time there are several matches, so Joule shows an *Employee List*. Select any name to see the details.

    ![Follow-up question about John: an Employee List (John Doe, Smith, Lara, Price) and details of John Doe, 1003764](images/t24-35-test10.png)

## 24.3 Why it works

- The new input becomes part of the OData query: `$filter=FirstName eq 'Jane'`. The service returns only matches, instead of every record (19.4a).
- **Generated response on:** Joule reads the output and writes the reply itself, so no message card is needed. Data mapping now happens in the End step, not in a message.
- The skill's **description** lets Joule match an indirect request ("a visitor says she is Jane") to it.

## 24.4 Common mistakes and notes

- **Copy, do not edit, the original project** if other skills already use it. A changed action changes every skill that uses it.
- **Filtering in the action vs in the agent:** an agent can filter results itself, but a filter in the API returns less data, costs fewer steps and avoids timeouts (19.6).

## 24.5 The same idea with Northwind (Lecture 11)

- An optional skill input "number of orders to return" mapped to `$top`, with a string-to-number formula, so "show me the top five orders" sent `$top=5`.
- The timeline showed the value 5 filled in during *resolving input slots*.

> [!IMPORTANT]
> **🏭 In production**
> - Filter on fields that the backend indexes, and set a sensible `$top` default, so a vague question cannot pull thousands of records.
> - Log which filters users actually ask for; they show which skills to add next.
>
> *Added by Claude*

## Check yourself

<details class="qa"><summary>Where do you map data when Joule writes the reply?</summary>

- In the End step, into the skill outputs
- Joule composes the message from those outputs

</details>

<details class="qa"><summary>Why put the filter in the action instead of asking the agent to filter?</summary>

- The backend returns only matching records: less data, fewer agent steps, fewer timeouts
- The behaviour is the same every time

</details>

## How this page was checked

- **SAP tutorial read in full on 21 Nov 2026** (last updated by SAP on 21 Aug 2026).
- **Steps rebuilt on 21 Nov 2026** from the tutorial's source file, with all 35 of its screenshots.
  - Every screenshot was checked for personal data. One was blurred: a user's first name on the Joule start screen.
  - SAP's page has a *Test yourself* heading, but its public source contains no questions, so none were taken over.
- **Lecture 12 recording:** captions 1:45 to 1:50 (the lecturer walks through it and sets it as practice). **Lecture 11:** 1:31 to 1:43 (`$top` from an input).
- Not run by me: there is no SAP Build tenant in this workspace.

## Sources

- SAP Developer Center, *Create a Filter in an Action Project*: https://developers.sap.com/tutorials/joulestudio-skill-action-filter.html
- Tutorial source and screenshots: https://github.com/sap-tutorials/sap-build-process-automation (© SAP SE, licensed CC BY 4.0)
- BTPAI course, Lecture 11 Part A (BT023) and Lecture 12 (BT025) recordings

Previous: [Tutorial: Create and deploy a Joule skill](tutorial-joule-skill-create.md) · Next: [Tutorial: Run an automated process from a Joule skill](tutorial-joule-skill-process.md)
