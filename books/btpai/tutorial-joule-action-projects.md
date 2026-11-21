# Tutorial: Create action projects

*Turn two destinations into tested, published API calls that a Joule skill can use: one that reads business partners and one that creates badge requests.*

> [!NOTE]
> **📍 At a glance**
> - **SAP tutorial:** [Create Action Projects](https://developers.sap.com/tutorials/joulestudio-skill-action-create.html) (part 2 of 5)
> - **You will build:** an action project for business partners (read) and one for badge requests (read and create)
> - **You need:** the destinations from [tutorial 21](tutorial-joule-skill-setup.md); developer rights in SAP Build are enough
> - **Level:** beginner · **Time:** about 20 minutes (SAP's estimate)
> - **Concepts:** [Joule Studio Classic](joule-studio-classic.md), 19.4a

**After this tutorial you can:**

- Generate actions from an OData destination and keep only the ones you need
- Trim an action's inputs and outputs, and test it against a destination
- Release and publish an action project so Joule Studio can find it

## 22.1 What you build

```mermaid
flowchart LR
    S4["S4HANA_MOCK"] --> P1["Action project 1<br/>GET business partners<br/>GET business partner by number"]
    BS["Badge_Service"] --> P2["Action project 2<br/>five badge actions<br/>incl. POST createBadge"]
    P1 --> L["Published:<br/>visible in Joule Studio"]
    P2 --> L
```

## 22.2 Steps

*Steps and screenshots adapted from SAP's tutorial (© SAP SE, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)). Steps reworded; screenshots resized.*

- **Actions** are SAP Build's reusable API calls. SAP Build Process Automation uses them to reach SAP and non-SAP systems with GET, POST, PATCH and other calls.
- A Joule skill in Joule Studio Classic can call the same published actions directly.

### Step 1: Create the action project for business partners

1. Open the **SAP Build lobby**. In the left menu choose **Connectors → Actions**, then **Create**.

    ![SAP Build lobby: Connectors > Actions selected, an empty list, and the Create button](images/t22-01-actions-create.png)

2. In *Choose an API Source*, open **Live API** and choose **OData Destinations**.

    ![Choose an API Source: the Live API group, with the OData Destinations tile marked](images/t22-02-actions-choose-source.png)

3. In *Browse OData Destinations*, choose the **S4HANA_MOCK** tile.
   - The next page lists every operation the service offers, grouped by entity. Choose **Next**.

    ![Browse OData Destinations: the Badge_Service and S4HANA_MOCK tiles, with S4HANA_MOCK marked](images/t22-03-actions-browse.png)

    ![The operations of S4HANA_MOCK (OData V2), grouped by entity, and the Next button](images/t22-04-actions-browse-mock.png)

4. Give the project a **name** and a **description**, then choose **Create**.
   - SAP uses the description "This is to give a Joule skill access to information about business partners."

    ![Create an Action project: project name and description filled in, then Create](images/t22-05-actions-browse-name.png)

5. Select these two operations, then choose **Add**:
   - `GET /A_BusinessPartner('{BusinessPartner}')`: reads one business partner by number
   - `GET /A_BusinessPartner`: reads the list of business partners

    ![Add Actions: filtered to GET, the two business partner operations ticked (2 of 20 allowed), then Add](images/t22-06-actions-mock-select.png)

6. Select the action **Retrieves business partner data by using business partner number**.
   - Its **Input** tab shows one parameter, `BusinessPartner`, passed in the URL path.

    ![The new project's Actions tab: the single-partner action selected, with its one input parameter BusinessPartner](images/t22-07-actions-mock-input.png)

7. Open the **Output** tab. Under *Body*, remove every field except `BusinessPartner`, `FirstName` and `LastName`.

    ![Output tab of the single-partner action: only BusinessPartner, FirstName and LastName left in the body](images/t22-08-actions-mock-output.png)

8. Open the **Test** tab:
   - Check that the destination is `S4HANA_MOCK`.
   - Enter `1003764` for **BusinessPartner** and choose **Test**.

    ![Test tab: destination S4HANA_MOCK, BusinessPartner 1003764, and the Test button](images/t22-09-actions-mock-test.png)

9. The response shows John Doe with status 200. Choose **Save**.

    ![Test Preview response: 200 OK with LastName Doe, FirstName John and BusinessPartner 1003764](images/t22-10-actions-mock-response.png)

10. Select the second action, **Retrieves business partner general data**, and trim its output the same way.
    - Here the three fields sit under `d → results`, because this action returns a list.

    ![Output tab of the list action: d > results with only BusinessPartner, FirstName and LastName](images/t22-11-actions-mock-output-2.png)

11. On its **Test** tab, choose **Test** without any input. Check the list of partners in the response, then choose **Save**.

    ![Test of the list action: several business partners returned (John Doe, Jane Roe, John Smith and more), then Save](images/t22-12-actions-mock-response-2.png)

12. Choose **Release** and confirm with **Release** in the dialog. The first version is 1.0.0.

    ![Release Project dialog: version 1.0.0, optional release notes, and the Release button](images/t22-13-actions-mock-release.png)

13. Choose **Publish** and confirm with **Publish**. Only published projects can be found from Joule Studio.

    ![The released project (version 1.0.0) with the Publish button marked at the top right](images/t22-14-actions-mock-publish.png)

### Step 2: Create the action project for badge requests

1. In the lobby choose **Connectors → Actions → Create → Live API → OData Destinations** again, and this time choose **Badge_Service**.
   - It is an OData V4 service with one entity, `Badges`. Choose **Next**.

    ![Browse OData Destinations for Badge_Service (OData V4): six Badges operations, including POST Invoke action createBadge](images/t22-15-actions-browse-badge.png)

2. Give the project a name and description, then choose **Create**.
   - SAP uses "This is to give a Joule skill access to a third-party badge service."

    ![Create an Action project: name BadgeRequestsService and its description, then Create](images/t22-16-actions-browse-name-2.png)

3. Select these five operations, then choose **Add**:
   - `GET /Badges({ID})`: get one badge by key
   - `POST /createBadge`: the action that creates a badge
   - `GET /Badges`: list badges
   - `PATCH /Badges({ID})`: update a badge
   - `DELETE /Badges({ID})`: delete a badge
   - SAP's tutorial leaves `POST /Badges` unticked; the skill creates badges through `createBadge`.

    ![Add Actions: five of the Badges operations ticked (5 of 7 allowed), POST /Badges left out, then Add](images/t22-17-actions-badge-select.png)

4. Select **Invoke action createBadge** and open its **Output** tab.
   - Click `badgeId` and change its **Type** from string to **number**.
   - SAP Build warns that changing types can cause problems. Here it is intended: the skill in tutorial 23 expects a number.

    ![Output tab of createBadge: the badgeId field panel with Type changed to number, and the warning about changing types](images/t22-18-actions-badge-output-change.png)

5. Open the **Input** tab. Under *Body*, tick `processInstanceId` and choose **Remove**.
   - The skill in tutorial 23 does not fill this field.

    ![Input tab of createBadge: the body fields, with processInstanceId ticked and the Remove button marked](images/t22-19-actions-badge-input-change.png)

6. Choose **Save**, then **Release**, then **Publish** (confirm each dialog).
7. Select **Invoke action createBadge** again and open the **Test** tab.
   - Check that the destination is `Badge_Service`.
   - Enter these test values, then choose **Test**:

    | Field | Value |
    |---|---|
    | `status` | `NEW` |
    | `lastname` | `Doe` |
    | `firstname` | `John` |
    | `communityId` | `john.doe@bestrunsap.com` (SAP's sample address) |
    | `businesspartnerId` | `1003764` |

    ![Test tab of createBadge: destination Badge_Service, the five test values entered, then Test](images/t22-20-actions-badge-test.png)

8. Read the response: status 200, with a new `ID`, a numeric `badgeId`, timestamps and the values you sent.

    ![Test response of createBadge: 200 OK, a new ID, badgeId 633497 as a number, status NEW and the sent names](images/t22-21-actions-badge-response.png)

## 22.3 Why it works

- The destination gives the base URL; each action adds its endpoint (19.4a). Testing proves the combination works before any skill depends on it.
- **Trimming outputs** keeps what the skill and the model see small and clear.
- **Changing `badgeId` to number** matters later: Joule Studio maps a value only into a field of the same type.
- **Only published projects** appear in Joule Studio's *Browse All Actions*.

## 22.4 Common mistakes (seen in class)

| What you see | Why | Fix |
|---|---|---|
| *Create* does nothing, or the action list never opens | The browser blocks the new tab as a pop-up | Allow pop-ups for SAP Build, refresh, and start again |
| Too many operations to find the two you need | The generator lists every operation of every entity | Filter by method *GET*; the two business partner actions sit near the end of its list |
| Others' projects mixed with yours | Everyone uses the same tenant and names | Prefix your project name with your own name |
| POST, PATCH or DELETE fail | The mock service supports only GET for business partners | Keep only the operations the service supports |

## 22.5 The same steps with Northwind (Lecture 11)

- Action project from the `NORTHWIND_D` destination, with *get all customers*, *get customer by key*, *get all orders* and *get the customer of an order*.
- Each was tested on its own, for example the customer by key with `ANTON`, before release and publish.

> [!IMPORTANT]
> **🏭 In production**
> - Start from SAP Business Accelerator Hub for standard APIs; it lists each API's operations and status before you build on it.
> - Keep write operations (POST, PATCH, DELETE) in their own action project when you can, so read-only skills cannot reach them by mistake.
>
> *Added by Claude*

## Check yourself

<details class="qa"><summary>Why must an action project be published, not only released?</summary>

- Only published action projects appear in Joule Studio's *Browse All Actions*
- Release creates a version; publishing makes it available to consumers

</details>

<details class="qa"><summary>Can one action project use two destinations?</summary>

- No; an action project belongs to one destination
- It can hold many actions for that one system

</details>

## How this page was checked

- **SAP tutorial read in full on 21 Nov 2026** (last updated by SAP on 21 Aug 2026).
- **Steps rebuilt on 21 Nov 2026** from the tutorial's source file, with all 21 of its screenshots.
  - Every screenshot was checked for personal data; none needed blurring. The names and addresses shown are SAP's sample data.
  - SAP's page has a *Test yourself* heading, but its public source contains no questions, so none were taken over.
- **Lecture 12 recording:** captions 0:22 to 0:55 (the lecturer builds both projects; learners follow). **Lecture 11:** 0:24 to 0:34 (Northwind actions).
- Not run by me: there is no SAP Build tenant in this workspace.

## Sources

- SAP Developer Center, *Create Action Projects*: https://developers.sap.com/tutorials/joulestudio-skill-action-create.html
- Tutorial source and screenshots: https://github.com/sap-tutorials/sap-build-process-automation (© SAP SE, licensed CC BY 4.0)
- BTPAI course, Lecture 11 Part A (BT023) and Lecture 12 (BT025) recordings

Previous: [Tutorial: Set up environments and destinations for Joule skills](tutorial-joule-skill-setup.md) · Next: [Tutorial: Create and deploy a Joule skill](tutorial-joule-skill-create.md)
