# Tutorial: Setup Generative AI Hub in SAP AI Launchpad

*Set up Generative AI Hub in SAP AI Launchpad.*

> [!NOTE]
> **📍 At a glance**
> - **Source:** SAP Developer Center tutorial [Setup Generative AI Hub in SAP AI Launchpad](https://developers.sap.com/tutorials/ai-launchpad-provisioning) by Smita Naik · about 20 min
> - **Licence:** © 2026 SAP SE or an SAP affiliate company, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The text and screenshots are SAP's; source on GitHub: [sap-tutorials/Tutorials](https://github.com/sap-tutorials/Tutorials/blob/master/tutorials/ai-launchpad-provisioning/)
> - **Changes for this book:** page layout; steps numbered 57.1 to 57.7; screenshots wider than 1600 px shrunk and all recompressed; image and file paths changed
> - **Last checked:** 21 Nov 2026

## Prerequisites
- A BTP global account
If you are an SAP Developer or SAP employee, please refer to the following links ( **for internal SAP stakeholders only** ) - 
[How to create a BTP Account (internal)](https://me.sap.com/notes/3493139)
[SAP AI Core](https://help.sap.com/docs/sap-ai-core?version=INTERNAL&locale=en-US&state=PRODUCTION)
If you are an external developer or a customer or a partner kindly refer to this [tutorial](https://developers.sap.com/tutorials/btp-cockpit-entitlements.html)
- A BTP global account, For more details, refer to: [BTP global account](https://statics.teams.cdn.office.net/evergreen-assets/safelinks/1/atp-safelinks.html)
- To continue this tutorial, you should have a BTP subaccount

## You will learn
- In this tutorial, you’ll learn how to set up SAP AI Launchpad and connect it to SAP AI Core to get started with orchestration in the Generative AI Hub.

## Pre-read

In this tutorial, you’ll learn how to **set up SAP AI Launchpad** and connect it to SAP AI Core to get started with **orchestration** in the **Generative AI Hub**.

SAP AI Launchpad is a service which you can link to your BTP global account. The launchpad offers an easy-to-use interface to manage AI workflow administration, processes, and tasks. 
 
The **Generative AI Hub** incorporates generative AI into your AI activities in SAP AI Core. You can access Generative AI Hub via SAP AI Launchpad.

Boosters is available for SAP AI Launchpad. Boosters are a set of guided interactive steps that enable you to select, configure, and consume services on SAP BTP. In this tutorial, we'll use the SAP AI Launchpad booster to create the subscription for SAP AI Launchpad in your subaccount with the standard plans.

> **Note:** SAP AI Launchpad is optional, but is the recommended interface for use with SAP AI Core.

---

## 57.1 Add AI Launchpad Entitlements to your subaccount

> **Note:** SAP AI Launchpad is optional, but is the recommended interface for use with SAP AI Core.

Entitlements and quota are managed at the global account and directory levels, distributed to directories and subaccounts, and consumed by the subaccounts. See also [Entitlements and Quotas](https://help.sap.com/viewer/65de2977205c403bbc107264b8eccf4b/Cloud/en-US/00aa2c23479d42568b18882b1ca90d79.html).

- **Entitlements** are your right to provision and consume a resource. They refer to what you’re entitled to use (for example, which services and service plans).

- **Quota** is the numeric quantity that defines the maximum allowed consumption of that resource. In other words, how much of a service plan you’re entitled to use.

Open the SAP BTP cockpit, access your global account and go to your subaccount.

![BTP Cockpit](images/ai-launchpad-provisioning/img/btpcockpit.png)

Check the entitlements for your subaccount by clicking `Entitlements`.

Click `Configure Entitlements` > `Add Service Plans`.

![Set SAP AI Launchpad as an entitlement](images/ai-launchpad-provisioning/img/configureentitlements.png)
![Set SAP AI Launchpad as an entitlement](images/ai-launchpad-provisioning/img/addserviceplan.png)

Select SAP AI Launchpad and the `standard` service plan.

![Set SAP AI Launchpad as an entitlement](images/ai-launchpad-provisioning/img/ail_select_entitlement.png)

Save your new entitlement.

![Save](images/ai-launchpad-provisioning/img/ail_save_entitlement.png)

## 57.2 Run the booster for SAP AI Launchpad

Choose `Boosters` from the navigation pane, and then choose the booster for `SAP AI Launchpad` from the selection. 

![Locate the booster for SAP AI Launchpad](images/ai-launchpad-provisioning/img/boosterailp.png)

Click `Start` when you are ready.

![Start the booster](images/ai-launchpad-provisioning/img/lpboosterstart.png)

In the Scenario Section, choose `Select Subaccount` option and click `Next`.

![choose select subaccount scenario](images/ai-launchpad-provisioning/img/AIL_select_scenario.png)

In the Configure Subaccount, choose `standard` plan, your subaccount and space where you want to provision SAP AI Launchpad and click `Next`

![configure entitlement](images/ai-launchpad-provisioning/img/AIL_configure_subaccount_std_plan.png)

Review the subaccount and entitlement details you have selected previously and click `Finish`.

![review configuration](images/ai-launchpad-provisioning/img/AIL_review.png)

![execution in progress](images/ai-launchpad-provisioning/img/AIL_creation_inprogress.png)

wait until setup completes. Once completed, navigate to your subaccount.

## 57.3 View your instances

View your SAP AI Launchpad instance by navigating to `Instances and subscriptions`. To see the details of your new instance, click the chevron on the entry.

![Success screen](images/ai-launchpad-provisioning/img/ail_subscription_success.png)

## 57.4 Setup SAP AI Launchpad for usage with SAP AI Core
Click on the **Workspaces** app. Click **Add** to create connection to your SAP AI Core instance.

![image](images/ai-launchpad-provisioning/img/ail/add.png)

Enter the name `my-ai-core` for the connection . Fill other details from your SAP AI Core service key as marked in the image.

> **INFORMATION** If you find that a connection already exists in your SAP AI Launchpad then you may add your connection under a different name. You may add any number of connections to SAP AI Core instances in your SAP AI Launchpad (this may not be case if you are using Free Tier).

![image](images/ai-launchpad-provisioning/img/ail/key.png)

## 57.5 Connect with SAP AI Core

Click on `my-ai-core` under the **Workspaces** app. You will observe the connection name on the header. You can find new apps on the side navigation bar, like **Generative AI Hub**.

![image](images/ai-launchpad-provisioning/img/ail/connection.png)

Select `default` from the **Resource Groups** Pane. Again this selection is updated in the header.

![image](images/ai-launchpad-provisioning/img/ail/connection2.png)

## 57.6 Get started with Orchestration in Generative AI Hub

As part of the SAP AI Core onboarding process, an `orchestration deployment` is automatically created in the `default resource group`.

This means you can start using orchestration in the Generative AI Hub right away—no need to create a separate deployment.

Click on `Generative AI Hub` > `Orchestration`

![image](images/ai-launchpad-provisioning/img/ail/ail_generative_ai_hub_orch.png)

## 57.7 What's Next?

You can proceed to the [Orchestration Tutorial](https://developers.sap.com/tutorials/ai-core-orchestration-consumption.html) to learn `how to consume generative AI models using the orchestration capabilities available in the Generative AI Hub`.

Previous: [Tutorial: Enable the ADT MCP Server in ABAP Development Tools for VS Code](tutorial-abap-dev-adt-mcp-server-tools.md) · Next: [Tutorial: Setup SAP AI Core Basic Trial](tutorial-teched2026-aicore-basic-trial.md)
