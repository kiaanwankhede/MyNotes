# Tutorial: Run an automated process from a Joule skill

*Let a Joule skill start an SAP Build Process Automation process, here an email to security when a badge is lost or stolen.*

> [!NOTE]
> **📍 At a glance**
> - **SAP tutorial:** [Consume an Automated Process in a Joule Skill](https://developers.sap.com/tutorials/joulestudio-skill-process.html) (part 5 of 5)
> - **You will build:** a process *SendEmailToSecurity*, published to the library, and the skill *BadgeSecurity* that runs it
> - **You need:** email configured for SAP Build Process Automation; the environment from [tutorial 5](tutorial-joule-skill-setup.md)
> - **Level:** beginner · **Time:** about 30 minutes (SAP's estimate)
> - **Not done in class:** the lecturer skipped it as mostly Process Automation, and left it as optional practice
> - **Concepts:** [Joule Studio Classic](joule-studio-classic.md), 3.8
> - **Last checked:** 21 Nov 2026

**After this tutorial you can:**

- Build and publish a simple automated process with inputs
- Call it from a Joule skill and pass values to it
- Check in monitoring that the process ran

## 9.1 What you build

```mermaid
flowchart LR
    U["'The old badge of John Doe<br/>has status LOST'"] --> SK["Skill BadgeSecurity<br/>inputs: Employee ID, BadgeStatus, names"]
    SK --> RP["Run Process<br/>SendEmailToSecurity"]
    RP --> EM["Email to security<br/>'Lost Badge'"]
    SK --> M["Send Message<br/>'Security has been informed'"]
```

## 9.2 Steps

*Steps and screenshots adapted from SAP's tutorial (© SAP SE, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)). Steps reworded; screenshots resized; a user's name blurred in one of them.*

- **Before you start:** an admin must have set up email for SAP Build Process Automation; the process sends a real email.
- The scenario extends the badge story from tutorials 6 to 8, but this skill does not depend on the other skills.

### Step 1: Create a project for the process

1. Open the **SAP Build lobby** and choose **Create**.

    ![SAP Build lobby with the two skills from earlier tutorials, and the Create button](images/t25-01-process-create1.png)

2. Choose the **Automated Process** tile, then **Next**.

    ![Create Project, Objective: the Automated Process tile selected, then Next](images/t25-02-process-create2.png)

3. Under *Type*, choose **Process** (not *Automation*), then **Next**.

    ![Create Project, Type: Process selected; Automation is the other choice](images/t25-03-process-create3.png)

4. Enter the name `InitiateSecurityChecksViaEmail` and the description "When a badge is reported as lost or stolen, contact security via email". Choose **Review**.

    ![Create Project, Name: InitiateSecurityChecksViaEmail and its description, then Review](images/t25-04-process-create4.png)

5. Check the summary and choose **Create**.

    ![Create Project, Summary: Automated Process, type Process, the name and description, then Create](images/t25-05-process-create5.png)

### Step 2: Build the process

1. In the Process Automation editor, choose **Create** (the process option). Enter the name `SendEmailToSecurity` and the description "Report stolen or lost badge to security via email", then **Create**.

    ![Project overview with no artifacts; Create Process dialog with name, identifier and description fields](images/t25-06-process-create6.png)

2. Choose **<<** at the right to open the side panel.

    ![Close-up of the editor's top right: Release, settings, Saved, zoom, and the << button marked](images/t25-07-process-create7.png)

3. In *Process Details*, open the **Variables** tab.

    ![Process Details side panel: General tab with name and subject; the Variables tab is marked](images/t25-08-process-create8.png)

4. Choose **Configure** next to *Process Inputs*, then **Add Input** four times. All four are type *String* and required:

    | Name | Description |
    |---|---|
    | `EmployeeID` | Employee ID |
    | `BadgeStatus` | Badge status |
    | `FirstName` | First name |
    | `LastName` | Last name |

    ![Configure Process Inputs: EmployeeID, FirstName, LastName and BadgeStatus, all String and required, then Apply](images/t25-09-process-create9.png)

5. Choose **Apply**. Close the side panel and choose **Save**. Then choose the **+** before *End*.

    ![The Variables tab listing the four process inputs; the + before End and the Save button are marked](images/t25-10-process-create10.png)

6. Choose **Email**.

    ![Choose what happens next in a process: Form, Approval, Email (marked), Notification, Decision and more](images/t25-11-process-create11.png)

7. In the *Send Mail* panel:
   - **To:** an email address you can check (SAP's screenshot blurs its own)
   - **Subject:** `Lost Badge`
   - Then choose **Open Mail Body Editor**.

    ![Send Mail step: To (blurred), Subject Lost Badge, and Open Mail Body Editor; the body is still empty](images/t25-12-process-create13.png)

8. Under **Value Binding**, expand **Process Inputs**. Write the mail text and insert the inputs from the list. SAP's example:
   - "Hello Security colleagues, [FirstName] [LastName] with ID [EmployeeID] has reported that their badge is [BadgeStatus]. Please take the appropriate measures. Best regards, Front Desk"
   - Choose **Apply**.

    ![Edit Mail Body: Process Inputs under Value Binding, and the mail text with the four inputs inserted](images/t25-13-process-create14b.png)

9. The panel now says the mail body has content. Close the side panel and choose **Save**.

    ![The finished process: Trigger, Send Mail, End; the mail body has content](images/t25-14-process-create15.png)

### Step 3: Release, deploy and publish the process

1. Choose **Release**, then **Release** in the dialog (version 1.0.0).

    ![Release Project dialog for the process: version 1.0.0, then Release](images/t25-15-process-release1.png)

2. Choose **Show project version**. Then choose **Deploy**, select your environment, and **Deploy**.

    ![Released version 1.0.0: Deploy, then Choose an Environment with tutorial selected, then Deploy](images/t25-16-process-release3.png)

3. The project now shows **Deployed** and **Active**.

    ![Process project overview: 1.0.0 Deployed and Active, with the SendEmailToSecurity process listed](images/t25-17-process-release4.png)

4. Go to the **lobby**, select the project, and open its **Versions** tab.
5. Choose **…** next to the deployed version, then **Publish to Library**. Confirm with **Publish**.

    ![Lobby: the process project selected, Versions tab, and Publish to Library in the menu of version 1.0.0](images/t25-18-process-publish1.png)

6. The version now shows *Published to Library* as well as *Deployed*.
   - **Without this step, Joule Studio cannot find the process.** Release and deploy alone are not enough.

    ![Versions tab: version 1.0.0 marked Published to Library and Deployed; message The project has been published](images/t25-19-process-publish3.png)

### Step 4: Create the Joule skill project

1. In the **lobby**, choose **Create**.

    ![SAP Build lobby now listing the process project and two skill projects; Create marked](images/t25-20-process-skill1.png)

2. Choose the **Joule Skill** tile, then **Next**.

    ![Create Project, Objective: the Joule Skill tile selected, then Next](images/t25-21-process-skill2.png)

3. Enter the name `BadgeSecurity` and the description "Contact security when a badge is reported lost or stolen." Choose **Review**.

    ![Create Project, Name: BadgeSecurity and its description, then Review](images/t25-22-process-skill3.png)

4. Check the summary and choose **Create**.

    ![Create Project, Summary: objective Joule Skill, project name and description, then Create](images/t25-23-process-skill4.png)

### Step 5: Create the skill and its inputs

1. In Joule Studio, choose **Create → Joule Skill**.

    ![The BadgeSecurity project overview with no entries; Create menu with Joule Skill marked](images/t25-24-process-skill5.png)

2. Enter the name `BadgeSecurity` and the description "Contact security when a badge is lost or stolen", then **Create**.

    ![Create Joule Skill dialog: name BadgeSecurity, identifier badgeSecurity, description, then Create](images/t25-25-process-skill6.png)

3. Click **Trigger** and switch off **Allow Joule to generate a response**. This skill sends its own message.

    ![Trigger side panel: Allow Joule to generate a response switched off](images/t25-26-process-skill7.png)

4. Open **Parameters** and choose **Configure** next to *Skill Inputs*.

    ![Parameters tab: no inputs yet, and Configure next to Skill Inputs](images/t25-27-process-skill7b.png)

5. Choose **Add Input** four times and fill in the rows, then **Apply**:

    | Name | Description | Required |
    |---|---|---|
    | `Employee ID` | Employee ID | yes |
    | `BadgeStatus` | Badge status | yes |
    | `First Name` | First name | yes |
    | `Last Name` | Last name | no |

    ![Configure Skill Inputs: Employee ID, BadgeStatus and First Name required; Last Name optional](images/t25-28-process-skill8.png)

    ![Parameters tab listing the four skill inputs, three marked required](images/t25-29-process-skill9.png)

6. Expand **Skill Outputs**: there are none.
   - A skill cannot read a process's results, so there is nothing to return.

    ![Skill Outputs expanded: No Outputs added yet](images/t25-30-process-skill10.png)

7. Close the side panel and choose **Save**.

### Step 6: Add the process to the skill

1. Choose the **+** between *Trigger* and *End*, then **Run Process**.

    ![Choose what happens next, with Run Process marked](images/t25-31-process-skill11.png)

2. Choose **Browse All Processes**.

    ![The Process panel: Browse All Processes marked; no process added yet](images/t25-32-process-skill12.png)

3. Find **SendEmailToSecurity** and choose **Add**.

    ![Browse library: SendEmailToSecurity from the InitiateSecurityChecksViaEmail project, with Add marked](images/t25-33-process-skill13.png)

4. Open the **Inputs** tab. All four process inputs are required and still empty.

    ![The process step's Inputs tab: BadgeStatus, EmployeeID, FirstName and LastName, all empty](images/t25-34-process-skill14.png)

5. Click **BadgeStatus**, and in *Skill Content* choose the skill input **BadgeStatus**. Map the other three the same way:
   - `EmployeeID` ← `Employee ID`, `FirstName` ← `First Name`, `LastName` ← `Last Name`
6. Close the side panel and choose **Save**.

    ![All four process inputs mapped to the matching skill inputs from Skill Content](images/t25-35-process-skill15.png)

### Step 7: Add the confirmation message

1. Choose the **+** before *End*, then **Send Message**.

    ![Choose what happens next after the process step, with Send Message marked](images/t25-36-process-skill16.png)

2. Choose **Open Message Editor**.

    ![Send Message step selected; Open Message Editor in its side panel](images/t25-37-process-skill17.png)

3. **Title:** `Security has been Informed`.
4. **Text:** "Badge status [BadgeStatus] for employee [Employee ID] has been reported to security".
   - Insert the two values with **<>** (data mapping), under `context → startEvent`.

    ![Message editor: the title, and Data Mapping open under startEvent with BadgeStatus marked](images/t25-38-process-skill18.png)

5. Choose **Save**, close the side panel, and choose **Save** again.

    ![The finished message: title, text with badge status and employee ID, and its preview](images/t25-39-process-skill19.png)

6. Click **End**: the skill has no outputs to map.

### Step 8: Release and deploy the skill

1. Choose **Release**, then **Release** in the dialog.

    ![Release Project dialog over the BadgeSecurity skill: version 1.0.0, then Release](images/t25-40-process-skill20.png)

2. Choose **Show project version** to switch to the released version.

    ![Message: BadgeSecurity 1.0.0 released, with Show project version](images/t25-41-process-skill21.png)

3. Choose **Deploy**, select your environment, and choose **Deploy**.

    ![Deploy: Choose an Environment with tutorial selected, then Deploy](images/t25-42-process-skill22.png)

### Step 9: Test the skill

1. In the lobby choose **Control Tower → Environments**, open your environment and its **Joule** tab.
   - `BadgeSecurity` is now listed with the two earlier skills. Choose **Launch**, then **New Conversation**.

    ![The environment's Joule tab listing BadgeSecurity, SearchWithName and CreateBadge; Launch marked](images/t25-43-process-test3.png)

2. Send: *"Please report to security that the old badge of John Doe 1003764 has the status LOST"*.

    ![Standalone Joule with the lost-badge request typed in (the user's name is blurred)](images/t25-44-process-test4.png)

3. Joule runs the skill, which starts the process, and shows your message card.

    ![Joule's reply: Security has been Informed, Badge status LOST for employee 1003764 has been reported](images/t25-45-process-test5.png)

4. **Check that the process ran:** lobby → **Monitoring → Process and Workflow Instances**. The run of `SendEmailToSecurity` shows *Completed*.
   - The "Lost Badge" email goes to the address in the process's *To* field.

    ![Monitoring, Process and Workflow Instances: SendEmailToSecurity, status Completed, environment tutorial](images/t25-46-process-test6.png)

## 9.3 Why it works

- **Fire and forget:** a skill can pass values into a process, but in the current release it cannot read the process's outputs back. Hence a skill with no outputs and its own message.
- **Publish to Library** is what makes a process visible to Joule Studio. Release and deploy alone are not enough (3.8).
- Existing Process Automation content can be reused the same way, without rebuilding it as a skill.

## 9.4 Things to watch

- The email step needs email set up for Process Automation by an admin; without it the process fails.
- Because the skill cannot see the result, check failures in *Monitoring*, not in the chat.

> [!IMPORTANT]
> **🏭 In production**
> - Use this pattern for actions that must happen in a fixed order, such as approvals and notifications; let agents decide only what to trigger.
> - Add an approval step in the process for anything with financial or security impact.
>
> *Added by Claude*

## Check yourself

<details class="qa"><summary>Where do you publish a process so a Joule skill can use it?</summary>

- In the Lobby, on the project's *Versions* tab: **…** beside the deployed version → *Publish to Library*

</details>

<details class="qa"><summary>Can the skill use the process's result in its reply?</summary>

- Not in the current release: the call is fire and forget
- The skill only passes inputs; check the outcome in monitoring

</details>

## How this page was checked

- **SAP tutorial read in full on 21 Nov 2026** (last updated by SAP on 21 Aug 2026).
- **Steps rebuilt on 21 Nov 2026** from the tutorial's source file, with all 46 of its screenshots.
  - Every screenshot was checked for personal data. One was blurred: a user's first name on the Joule start screen. SAP had already blurred the email recipient and the *Started By* user.
  - SAP's page has a *Test yourself* heading, but its public source contains no questions, so none were taken over.
- **Lecture 12 recording:** caption 2:11 (the lecturer skips this part and recommends it as optional practice).
- Not run by me: there is no SAP Build tenant in this workspace.

## Sources

- SAP Developer Center, *Consume an Automated Process in a Joule Skill*: https://developers.sap.com/tutorials/joulestudio-skill-process.html
- Tutorial source and screenshots: https://github.com/sap-tutorials/sap-build-process-automation (© SAP SE, licensed CC BY 4.0)
- BTPAI course, Lecture 12 recording (BT025)

Previous: [Tutorial: Filter an action and let Joule write the reply](tutorial-joule-action-filter.md) · Next: [Tutorial: Create a Joule agent in Joule Studio Classic](tutorial-joule-agent-create.md)
