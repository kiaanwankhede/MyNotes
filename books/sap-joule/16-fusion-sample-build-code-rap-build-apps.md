# Chapter 16: The fusion sample: Build Code with Joule, a RAP service and SAP Build Apps

*A hands-on walkthrough of SAP's sample "Mastering SAP S/4HANA Extension with SAP Build": three modules that join a CAP backend made with Joule, an ABAP RAP geo service and two no-code apps.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how a professional developer and a citizen developer build one solution together: a CAP service generated with Joule prompts, an ABAP RESTful service with a geo function, and two SAP Build Apps front ends joined by BTP destinations
> - **Level:** intermediate · **Time:** about 60 minutes of reading (the build itself is several hours)
> - **Source:** SJ057, the GitHub repository SAP-samples/btp-s4hana-buildcode-rap-buildapps (documentation folders for Modules 1 to 3 and the destination pages); read 9 November 2026
> - **Builds on:** [Chapter 11](11-joule-build-code-and-developers.md) (Joule in Build Code) and [Chapter 5](05-setting-up-joule-by-product.md) (destinations)

**After this chapter you can:**
- describe the sample's scenario and its three modules
- reproduce the Joule prompts used to generate a CAP data model, sample data and logic
- explain how the RAP service finds partners within a radius
- connect SAP Build Apps to a CAP service and a RAP service through destinations

---

## 16.1 The scenario (README)

- **Story:** a technician (Suzan) finds a fault in medical equipment and reports it from the **Service Hub** mobile app; the incident is stored by a **CAP** service built with Joule; a service admin (Alex) assigns a processor; a **RAP** service works out which processors are near the device; Suzan follows the assignment
- **Three parts:** CAP service (Build Code with Joule), RAP service (ABAP environment), and SAP Build Apps front ends
- **Focus:** a **fusion application**, where professional and citizen developers work together
- **Licence:** Apache 2.0; copyright 2024 SAP
- The repository now sits in the SAP-archive organisation (see [Chapter 11](11-joule-build-code-and-developers.md) §11.6)

| Module | What you build |
|---|---|
| 1 | Full-stack CAP app on Cloud Foundry, generated with Joule |
| 2 | Full-stack RESTful ABAP service |
| 3 | Two SAP Build Apps web apps: client and admin |

## 16.2 Module 1: Build Code with Joule

### Step 0: set up Build Code
- Need a BTP global account (trial or enterprise)
- In the cockpit open **Boosters**, find the **SAP Build Code** booster for your plan, run it, then **Navigate to Subaccount**
  - The booster checks authorisations, providers and regions first
- Verify under **Services > Instances and Subscriptions** that you are subscribed to **SAP Business Application Studio** and **SAP Build Code**; open Build Code to reach the lobby

### Step 1: introduction and new project
- Build Code is a turnkey environment: runtime and design time, DevOps and lifecycle management built in
- Benefits listed: clean core through side-by-side extensions, generative AI for developer efficiency, language of choice, interoperability between classic and low-code tools
- Create the project: Lobby > **Create** > **Application** > **Full-Stack** > **Full-Stack Node.JS**; name it **equipmentmaintenance**; choose the dev space; **Review** and **Create**; open it (it opens in Business Application Studio)

### Step 2: data entities with Joule
- Open **Joule** in the activity bar and pick **/cap-gen-model (Generate CAP Data Model)**
- Paste one detailed prompt. Its content (paraphrased):
  - Entities: **Incidents, Medicaldevice, Conversation**, plus code lists **Status** and **Urgency**
  - Each incident has title, description, createdAt, processor, company, latitude, longitude, all strings
  - Incidents hold a **composition** of Conversation; Conversation has a message string
  - Medicaldevice has code and description
  - Status: code (single character, key), description, criticality (integer); Urgency: code (key), description
  - Each incident has associations to Medicaldevice, Status and Urgency
- Accept the code; the **Storyboard** tab shows the schema
- **Note from the sample:** Joule generates different code every run; yours may differ and that is fine if it does the same job

> [!TIP]
> The more detailed the prompt, the closer the result. This prompt names every entity, field type, key and relationship.

### Step 3: adapt the schema for Status and Urgency
- In the graphical modeler open Status, **Include Aspects**, untick **cuid** (removes the ID key), then tick **Key** on **code**
- Repeat for Urgency

### Step 4: sample data with Joule
- **/cap-gen-data (Generate CAP sample data)** with a prompt asking for at least 5 incidents and 5 devices; Status limited to New (N), Assigned (A), Closed (C); Urgency limited to Low (L), Medium (M), High (H)
- Accept, open the **Data Editor**, check the codes and descriptions, correct if needed
- Move the 5 CSV files from **test/data** to **db/data** so they deploy as initial data (fine for a demo; production should use proper initial data)

### Step 5: application logic with Joule
- Goal: block changes to a closed incident
- In the graphical modeler select **Incidents** > **Add Logic**; phase **Before**, event **Update**; open the code editor and ask Joule to throw the error "Can't modify a closed incident" when status is 'C'
- Second handler named **incidents-status-logic**: phase **Before**, event **Create**; prompt: always set the status code to 'N' before creating an incident
- If the code looks wrong, use **Regenerate**

### Step 6: adapt the service
- In **service.cds** open the **CDS Graphical Modeler**
- Turn off **Draft Editing** for Incidents, Medicaldevice, Status and Urgency (the app is read-mode)
- Add a projection of **Conversation** (entity `equipmentmaintenance.Conversation`, draft off) if it is missing; this keeps the composition with incidents

### Step 7: add a UI
- Storyboard > add UI: display name **Incidents**, description **Equipment Maintenance**
- Type **Template-Based Responsive Application**, template **List Report Page**, main entity **Incidents**
- **Preview (Run and Debug)** to see the list and an object page

### Step 8: one-click deployment
- **Prerequisites:** a Cloud Foundry space; entitlements for SAP HANA Cloud (`hana`, `tools`), HDI containers (`hdi-shared`), Cloud Foundry (`MEMORIES`), and Authorization and Trust Management (`application`); a SAP HANA Cloud instance that is mapped to your CF space (the CF Org ID is in the subaccount overview)
- Task Explorer > run **Enable Discovery and Deploy equipmentmaintenance**; an MTA build starts; sign in to Cloud Foundry with the SSO passcode; pick org and space
- Check the deployed app under **HTML5 Applications** (you may need to subscribe to Build Work Zone to see it)
- Check the destination **equipmentmaintenance-equipmentmaintenanceSrv** under **Connectivity > Destinations**; Build Apps will use it

### Images: Module 1 screenshots from the sample
![Booster and subscription, figure 1](images/ch16-b1-setup-01.png)
![Booster and subscription, figure 2](images/ch16-b1-setup-02.png)
![Booster and subscription, figure 3](images/ch16-b1-setup-03.png)
![Booster and subscription, figure 4](images/ch16-b1-setup-04.png)
![Booster and subscription, figure 5](images/ch16-b1-setup-05.png)
![Booster and subscription, figure 6](images/ch16-b1-setup-06.png)

![New project, figure 1](images/ch16-b1-intro-01.png)
![New project, figure 2](images/ch16-b1-intro-02.png)
![New project, figure 3](images/ch16-b1-intro-03.png)
![New project, figure 4](images/ch16-b1-intro-04.png)
![New project, figure 5](images/ch16-b1-intro-05.png)
![New project, figure 6](images/ch16-b1-intro-06.png)
![New project, figure 7](images/ch16-b1-intro-07.png)

![Data model with Joule, figure 1](images/ch16-b1-data-01.png)
![Data model with Joule, figure 2](images/ch16-b1-data-02.png)
![Data model with Joule, figure 3](images/ch16-b1-data-03.png)
![Data model with Joule, figure 4](images/ch16-b1-data-04.png)
![Data model with Joule, figure 5](images/ch16-b1-data-05.png)

![Status and Urgency schema, figure 1](images/ch16-b1-schema-01.png)
![Status and Urgency schema, figure 2](images/ch16-b1-schema-02.png)
![Status and Urgency schema, figure 3](images/ch16-b1-schema-03.png)
![Status and Urgency schema, figure 4](images/ch16-b1-schema-04.png)
![Status and Urgency schema, figure 5](images/ch16-b1-schema-05.png)
![Status and Urgency schema, figure 6](images/ch16-b1-schema-06.png)

![Sample data, figure 1](images/ch16-b1-sample-01.png)
![Sample data, figure 2](images/ch16-b1-sample-02.png)
![Sample data, figure 3](images/ch16-b1-sample-03.png)
![Sample data, figure 4](images/ch16-b1-sample-04.png)
![Sample data, figure 5](images/ch16-b1-sample-05.png)
![Sample data, figure 6](images/ch16-b1-sample-06.png)
![Sample data, figure 7](images/ch16-b1-sample-07.png)
![Sample data, figure 8](images/ch16-b1-sample-08.png)

![Application logic, figure 1](images/ch16-b1-logic-01.png)
![Application logic, figure 2](images/ch16-b1-logic-02.png)
![Application logic, figure 3](images/ch16-b1-logic-03.png)
![Application logic, figure 4](images/ch16-b1-logic-04.png)
![Application logic, figure 5](images/ch16-b1-logic-05.png)
![Application logic, figure 6](images/ch16-b1-logic-06.png)
![Application logic, figure 7](images/ch16-b1-logic-07.png)
![Application logic, figure 8](images/ch16-b1-logic-08.png)
![Application logic, figure 9](images/ch16-b1-logic-09.png)
![Application logic, figure 10](images/ch16-b1-logic-10.png)
![Application logic, figure 11](images/ch16-b1-logic-11.png)

![Service domain, figure 1](images/ch16-b1-service-01.png)
![Service domain, figure 2](images/ch16-b1-service-02.png)
![Service domain, figure 3](images/ch16-b1-service-03.png)
![Service domain, figure 4](images/ch16-b1-service-04.png)
![Service domain, figure 5](images/ch16-b1-service-05.png)
![Service domain, figure 6](images/ch16-b1-service-06.png)
![Service domain, figure 7](images/ch16-b1-service-07.png)
![Service domain, figure 8](images/ch16-b1-service-08.png)
![Service domain, figure 9](images/ch16-b1-service-09.png)

![List report UI, figure 1](images/ch16-b1-ui-01.png)
![List report UI, figure 2](images/ch16-b1-ui-02.png)
![List report UI, figure 3](images/ch16-b1-ui-03.png)
![List report UI, figure 4](images/ch16-b1-ui-04.png)
![List report UI, figure 5](images/ch16-b1-ui-05.png)
![List report UI, figure 6](images/ch16-b1-ui-06.png)
![List report UI, figure 7](images/ch16-b1-ui-07.png)
![List report UI, figure 8](images/ch16-b1-ui-08.png)
![List report UI, figure 9](images/ch16-b1-ui-09.png)
![List report UI, figure 10](images/ch16-b1-ui-10.png)

![Deployment, figure 1](images/ch16-b1-deploy-01.png)
![Deployment, figure 2](images/ch16-b1-deploy-02.png)
![Deployment, figure 3](images/ch16-b1-deploy-03.png)
![Deployment, figure 4](images/ch16-b1-deploy-04.png)
![Deployment, figure 5](images/ch16-b1-deploy-05.png)
![Deployment, figure 6](images/ch16-b1-deploy-06.png)
![Deployment, figure 7](images/ch16-b1-deploy-07.png)
![Deployment, figure 8](images/ch16-b1-deploy-08.png)
![Deployment, figure 9](images/ch16-b1-deploy-09.png)
![Deployment, figure 10](images/ch16-b1-deploy-10.png)
![Deployment, figure 11](images/ch16-b1-deploy-11.png)


## 16.3 Module 2: RESTful ABAP service

*Purpose: an API that returns incident processors (ID, name, location) and can find those within a radius.*

- **Assumption:** processor master data (ID and name) comes from SAP S/4HANA Cloud business partners and is loaded once; geo coordinates are assigned at random
- **Landscape:** a BTP subaccount with the **ABAP environment** (trial works); your user needs the developer role `SAP_BR_DEVELOPER`; ABAP Development Tools in Eclipse are required
- **Trial limitation:** no communication management, so you build a destination with your own credentials

### 16.3.1 Introduction: the build2abap destination
- Take the ABAP Environment **service key** and create destination **build2abap**: type HTTP, URL from the key, proxy Internet, authentication **OAuth2Password**, your BTP user, client ID and secret from the key's `uaa` part, token URL = the `uaa` URL + `/oauth/token`
- Additional properties: `abap_enabled=true`, `HTML5.DynamicDestination=abap_true_destination`, `HTML5.Timeout=60000`, `WebIDEEnabled=true`, `WebIDEUsage=odata_abap, dev_abap`

### 16.3.2 Create the project
- Build lobby > Create > Application > Full-Stack > **Full-Stack ABAP**; system **build2abap**; new package **ZGEO** under **ZLOCAL**; project name **zgeo** (description GEO ABAP)
- Eclipse opens an ABAP Cloud project; log in through the browser; name it **TRIAL_ENV**

### 16.3.3 Database tables
- **ZBUPA** (business partners): client, partner (10 characters), first and last name
- **ZBUPAGEO** (geo data): partner, latitude and longitude as decimals, and a **location** field of type `abap.geom_ewkb` with spatial reference system 4326
- Why both: plain coordinates are easy in requests; the spatial type is what HANA's spatial engine uses

### 16.3.4 Data definitions (root and child views)
- **ZI_BusinessPartner** (root view entity) with a 0..1 **composition** to **ZI_BusinessPartnerGeo**
- **ZI_BusinessPartnerGeo** is the child (association to parent); activate both together (the first shows errors until the second exists)

### 16.3.5 Projections
- **ZC_BusinessPartner** (root projection, provider contract `transactional_query`) and **ZC_BusinessPartnerGeo**
- The spatial field is hidden in the projection because that type is not yet fully supported for consumers

### 16.3.6 Expose the service
- Service definition **ZGEO** exposing BusinessPartner and BusinessPartnerGeo
- Service binding **ZAPI_GEO_O2**, binding type **OData V2 - Web API**; **Activate**, then **Publish**

### 16.3.7 Geo logic with AMDP
- Helper class **ZCL_GEO_HELPER** implements `if_amdp_marker_hdb` (ABAP Managed Database Procedures, written in ABAP, run in HANA)
- Two methods: **get_geo_point** (coordinates to `geom_ewkb`) and **get_partners_around** (partners within a radius of a point)

### 16.3.8 Behavior artifacts
- Abstract entities **ZD_GEO_PARAMETERS** (radius, longitude, latitude) and **ZD_GETINRADIUS_RESULT** (partner, name, latitude, longitude, distance)
- **Managed** behavior definition for ZI_BusinessPartner: create, update, delete, composition create for the geo data, and a static function **getInRadius**
- Behavior implementation class: the **setGEOPoint** determination converts coordinates on every modify, and getInRadius calls the helper; the class uses EML (Entity Manipulation Language)
- A projection behavior definition on ZC_BusinessPartner

### 16.3.9 Fill in the test data
- Download the **Business Partners** API EDMX and copy an API key from the **SAP Business Accelerator Hub** (api.sap.com; sign-in needed)
- Create a **Service Consumption Model** `ZBUPA_CLOUD`
- Run console class **ZCL_FILL_BUPA_TABLES** (implements `if_oo_adt_classrun`; paste your API key into the marked line); it loads partners through the business object so geo data stays consistent; the log shows 459 partners found
- Geo data comes from an open list of the biggest city of each country

> [!WARNING]
> Never commit your API key or service-key values. Keep them in the cockpit or a local file that is not in Git.

### 16.3.10 Test
- Open the service URL from the binding, then try:
  - `/BusinessPartner?$expand=to_GeoData&$top=3` for three partners with geo data
  - `/getInRadius?radius=500&point_lat='49.2896256'&point_lon='8.6409216'` for partners within 500 km of Walldorf

### 16.3.11 Destination for Build Apps
- Destination **RAP-Geo**: URL = the ABAP environment URL plus `/sap/opu/odata/sap/ZAPI_GEO_O2`; OAuth2Password with your user; client ID, secret and token URL from the service key
- Additional properties: `HTML5.DynamicDestination=true`, `WebIDEEnabled=true`, `WebIDEUsage=odata_gen`, `sap-client` (normally 100 on trial)

### Images: Module 2 screenshots from the sample
![Intro and destination, figure 1](images/ch16-b2-intro-01.png)
![Intro and destination, figure 2](images/ch16-b2-intro-02.png)
![Intro and destination, figure 3](images/ch16-b2-intro-03.png)
![Intro and destination, figure 4](images/ch16-b2-intro-04.png)

![Project, figure 1](images/ch16-b2-project-01.png)
![Project, figure 2](images/ch16-b2-project-02.png)
![Project, figure 3](images/ch16-b2-project-03.png)
![Project, figure 4](images/ch16-b2-project-04.png)
![Project, figure 5](images/ch16-b2-project-05.png)
![Project, figure 6](images/ch16-b2-project-06.png)
![Project, figure 7](images/ch16-b2-project-07.png)
![Project, figure 8](images/ch16-b2-project-08.png)
![Project, figure 9](images/ch16-b2-project-09.png)
![Project, figure 10](images/ch16-b2-project-10.png)
![Project, figure 11](images/ch16-b2-project-11.png)
![Project, figure 12](images/ch16-b2-project-12.png)

![Tables, figure 1](images/ch16-b2-tables-01.png)
![Tables, figure 2](images/ch16-b2-tables-02.png)
![Tables, figure 3](images/ch16-b2-tables-03.png)
![Tables, figure 4](images/ch16-b2-tables-04.png)

![Data definitions, figure 1](images/ch16-b2-bo-01.png)
![Data definitions, figure 2](images/ch16-b2-bo-02.png)
![Data definitions, figure 3](images/ch16-b2-bo-03.png)
![Data definitions, figure 4](images/ch16-b2-bo-04.png)
![Data definitions, figure 5](images/ch16-b2-bo-05.png)
![Data definitions, figure 6](images/ch16-b2-bo-06.png)
![Data definitions, figure 7](images/ch16-b2-bo-07.png)
![Data definitions, figure 8](images/ch16-b2-bo-08.png)
![Data definitions, figure 9](images/ch16-b2-bo-09.png)

![Projections, figure 1](images/ch16-b2-proj-01.png)
![Projections, figure 2](images/ch16-b2-proj-02.png)
![Projections, figure 3](images/ch16-b2-proj-03.png)
![Projections, figure 4](images/ch16-b2-proj-04.png)
![Projections, figure 5](images/ch16-b2-proj-05.png)
![Projections, figure 6](images/ch16-b2-proj-06.png)
![Projections, figure 7](images/ch16-b2-proj-07.png)
![Projections, figure 8](images/ch16-b2-proj-08.png)

![Service, figure 1](images/ch16-b2-service-01.png)
![Service, figure 2](images/ch16-b2-service-02.png)
![Service, figure 3](images/ch16-b2-service-03.png)
![Service, figure 4](images/ch16-b2-service-04.png)
![Service, figure 5](images/ch16-b2-service-05.png)
![Service, figure 6](images/ch16-b2-service-06.png)
![Service, figure 7](images/ch16-b2-service-07.png)

![Geo class, figure 1](images/ch16-b2-geo-01.png)
![Geo class, figure 2](images/ch16-b2-geo-02.png)
![Geo class, figure 3](images/ch16-b2-geo-03.png)
![Geo class, figure 4](images/ch16-b2-geo-04.png)
![Geo class, figure 5](images/ch16-b2-geo-05.png)

![Behavior, figure 1](images/ch16-b2-behav-01.png)
![Behavior, figure 2](images/ch16-b2-behav-02.png)
![Behavior, figure 3](images/ch16-b2-behav-03.png)
![Behavior, figure 4](images/ch16-b2-behav-04.png)
![Behavior, figure 5](images/ch16-b2-behav-05.png)
![Behavior, figure 6](images/ch16-b2-behav-06.png)
![Behavior, figure 7](images/ch16-b2-behav-07.png)
![Behavior, figure 8](images/ch16-b2-behav-08.png)
![Behavior, figure 9](images/ch16-b2-behav-09.png)
![Behavior, figure 10](images/ch16-b2-behav-10.png)
![Behavior, figure 11](images/ch16-b2-behav-11.png)
![Behavior, figure 12](images/ch16-b2-behav-12.png)

![Test data, figure 1](images/ch16-b2-fill-01.png)
![Test data, figure 2](images/ch16-b2-fill-02.png)
![Test data, figure 3](images/ch16-b2-fill-03.png)
![Test data, figure 4](images/ch16-b2-fill-04.png)
![Test data, figure 5](images/ch16-b2-fill-05.png)
![Test data, figure 6](images/ch16-b2-fill-06.png)
![Test data, figure 7](images/ch16-b2-fill-07.png)
![Test data, figure 8](images/ch16-b2-fill-08.png)
![Test data, figure 9](images/ch16-b2-fill-09.png)
![Test data, figure 10](images/ch16-b2-fill-10.png)
![Test data, figure 11](images/ch16-b2-fill-11.png)
![Test data, figure 12](images/ch16-b2-fill-12.png)
![Test data, figure 13](images/ch16-b2-fill-13.png)
![Test data, figure 14](images/ch16-b2-fill-14.png)
![Test data, figure 15](images/ch16-b2-fill-15.png)

![Test, figure 1](images/ch16-b2-test-01.png)
![Test, figure 2](images/ch16-b2-test-02.png)
![Test, figure 3](images/ch16-b2-test-03.png)
![Test, figure 4](images/ch16-b2-test-04.png)

![Destination, figure 1](images/ch16-b2-dest-01.png)
![Destination, figure 2](images/ch16-b2-dest-02.png)
![Destination, figure 3](images/ch16-b2-dest-03.png)
![Destination, figure 4](images/ch16-b2-dest-04.png)
![Destination, figure 5](images/ch16-b2-dest-05.png)
![Destination, figure 6](images/ch16-b2-dest-06.png)


## 16.4 Module 3: SAP Build Apps

*Two web apps. Both start from a downloadable template (`.mtar`), imported through the Build lobby with Import, then renamed and opened full-screen.*

### 16.4.1 Client app: report an incident
- **Data connection:** enable BTP authentication; add integration **BTP Destinations** > `equipmentmaintenance-equipmentmaintenanceSrv`; enable data entities **Incidents** and **Medicaldevice**; browse real data to confirm
- **Variables:** a data variable for **Incidents** (type: new data record) and for **Medicaldevice** (collection); keep the name `Medicaldevice1` exactly, because a formula uses it
- **Logic on the "Create a new incident" button:** spinner, **Create record** into Incidents, hide spinner, alert, then clear the form
  - ID: `GENERATE_UUID()`; createdAt: `NOW()`
  - Latitude and longitude come from the phone's geolocation sensor variables, converted with `STRING(...)`
  - Title, company, description and device come from the form's data variable; urgency comes from an app variable
  - First output of a logic node is success, the later one is failure
- **Test:** Preview > Open web preview > fill the form > create

### 16.4.2 Admin app: assign a processor
- **Data connection:** same CAP destination (enable all entities with Expand); then create a **REST API data entity `BPData`** on the **RAP-Geo** destination with a `list` method on `/getInRadius?...`
  - Run the test until status 200, autodetect the schema, then replace the path with a formula that builds the URL from three **additional inputs**: `radius` (number), `point_lat` and `point_lon` (text)
- **Overview page:** data variables for Medicaldevice and Incidents; the list repeats over incidents; primary label shows title and ID, secondary label shows company; the Open Page logic passes the selected `IncidentID`
- **Detail page variables:** Incidents (single record bound to the page parameter), Conversation (filter `incident_ID` equals the page parameter), and `BPData1`
  - A logic flow reacts when the page variable **SelectedRadius** changes: delay 1 s, get the record collection with radius and the incident's coordinates, save to `BPData1`
  - If the result is empty (`IS_EMPTY(data.BPData1.d.results)`), alert "No Business Partner can be listed within the given range" and reset the radius to 9999 so all partners show
- **Detail page UI and logic:**
  - Page variables set one second after load: urgency and processor from the incident
  - The drop-down lists partners with their distance in km; the map shows markers for the incident and each partner
  - **Set Status** buttons call one custom flow function with a status input: Update record on Incidents (processor from `SelectedPartner`, status from the input, urgency from `SelectedUrgency`)
  - Message sending creates a **Conversation** record with `incident_ID` and the message
  - The conversation container shows only when `NOT(IS_EMPTY(data.Conversation1))`
- **Test:** preview, open incidents, change details

### Images: Module 3 screenshots from the sample
![Client: import, figure 1](images/ch16-b3-client-import-01.png)
![Client: import, figure 2](images/ch16-b3-client-import-02.png)
![Client: import, figure 3](images/ch16-b3-client-import-03.png)
![Client: import, figure 4](images/ch16-b3-client-import-04.png)
![Client: import, figure 5](images/ch16-b3-client-import-05.png)

![Client: data, figure 1](images/ch16-b3-client-data-01.png)
![Client: data, figure 2](images/ch16-b3-client-data-02.png)
![Client: data, figure 3](images/ch16-b3-client-data-03.png)
![Client: data, figure 4](images/ch16-b3-client-data-04.png)
![Client: data, figure 5](images/ch16-b3-client-data-05.png)
![Client: data, figure 6](images/ch16-b3-client-data-06.png)
![Client: data, figure 7](images/ch16-b3-client-data-07.png)
![Client: data, figure 8](images/ch16-b3-client-data-08.png)
![Client: data, figure 9](images/ch16-b3-client-data-09.png)
![Client: data, figure 10](images/ch16-b3-client-data-10.png)
![Client: data, figure 11](images/ch16-b3-client-data-11.png)
![Client: data, figure 12](images/ch16-b3-client-data-12.png)
![Client: data, figure 13](images/ch16-b3-client-data-13.png)
![Client: data, figure 14](images/ch16-b3-client-data-14.png)
![Client: data, figure 15](images/ch16-b3-client-data-15.png)
![Client: data, figure 16](images/ch16-b3-client-data-16.png)

![Client: logic, figure 1](images/ch16-b3-client-logic-01.png)
![Client: logic, figure 2](images/ch16-b3-client-logic-02.png)
![Client: logic, figure 3](images/ch16-b3-client-logic-03.png)
![Client: logic, figure 4](images/ch16-b3-client-logic-04.png)
![Client: logic, figure 5](images/ch16-b3-client-logic-05.png)
![Client: logic, figure 6](images/ch16-b3-client-logic-06.png)
![Client: logic, figure 7](images/ch16-b3-client-logic-07.png)
![Client: logic, figure 8](images/ch16-b3-client-logic-08.png)
![Client: logic, figure 9](images/ch16-b3-client-logic-09.png)
![Client: logic, figure 10](images/ch16-b3-client-logic-10.png)
![Client: logic, figure 11](images/ch16-b3-client-logic-11.png)
![Client: logic, figure 12](images/ch16-b3-client-logic-12.png)
![Client: logic, figure 13](images/ch16-b3-client-logic-13.png)
![Client: logic, figure 14](images/ch16-b3-client-logic-14.png)
![Client: logic, figure 15](images/ch16-b3-client-logic-15.png)
![Client: logic, figure 16](images/ch16-b3-client-logic-16.png)
![Client: logic, figure 17](images/ch16-b3-client-logic-17.png)
![Client: logic, figure 18](images/ch16-b3-client-logic-18.png)
![Client: logic, figure 19](images/ch16-b3-client-logic-19.png)
![Client: logic, figure 20](images/ch16-b3-client-logic-20.png)
![Client: logic, figure 21](images/ch16-b3-client-logic-21.png)
![Client: logic, figure 22](images/ch16-b3-client-logic-22.png)
![Client: logic, figure 23](images/ch16-b3-client-logic-23.png)
![Client: logic, figure 24](images/ch16-b3-client-logic-24.png)
![Client: logic, figure 25](images/ch16-b3-client-logic-25.png)
![Client: logic, figure 26](images/ch16-b3-client-logic-26.png)
![Client: logic, figure 27](images/ch16-b3-client-logic-27.png)
![Client: logic, figure 28](images/ch16-b3-client-logic-28.png)
![Client: logic, figure 29](images/ch16-b3-client-logic-29.png)
![Client: logic, figure 30](images/ch16-b3-client-logic-30.png)
![Client: logic, figure 31](images/ch16-b3-client-logic-31.png)
![Client: logic, figure 32](images/ch16-b3-client-logic-32.png)
![Client: logic, figure 33](images/ch16-b3-client-logic-33.png)
![Client: logic, figure 34](images/ch16-b3-client-logic-34.png)

![Client: test, figure 1](images/ch16-b3-client-test-01.png)
![Client: test, figure 2](images/ch16-b3-client-test-02.png)
![Client: test, figure 3](images/ch16-b3-client-test-03.png)
![Client: test, figure 4](images/ch16-b3-client-test-04.png)
![Client: test, figure 5](images/ch16-b3-client-test-05.png)

![Admin: import, figure 1](images/ch16-b3-admin-import-01.png)
![Admin: import, figure 2](images/ch16-b3-admin-import-02.png)
![Admin: import, figure 3](images/ch16-b3-admin-import-03.png)
![Admin: import, figure 4](images/ch16-b3-admin-import-04.png)
![Admin: import, figure 5](images/ch16-b3-admin-import-05.png)
![Admin: import, figure 6](images/ch16-b3-admin-import-06.png)
![Admin: import, figure 7](images/ch16-b3-admin-import-07.png)

![Admin: data, figure 1](images/ch16-b3-admin-data-01.png)
![Admin: data, figure 2](images/ch16-b3-admin-data-02.png)
![Admin: data, figure 3](images/ch16-b3-admin-data-03.png)
![Admin: data, figure 4](images/ch16-b3-admin-data-04.png)
![Admin: data, figure 5](images/ch16-b3-admin-data-05.png)
![Admin: data, figure 6](images/ch16-b3-admin-data-06.png)
![Admin: data, figure 7](images/ch16-b3-admin-data-07.png)
![Admin: data, figure 8](images/ch16-b3-admin-data-08.png)
![Admin: data, figure 9](images/ch16-b3-admin-data-09.png)
![Admin: data, figure 10](images/ch16-b3-admin-data-10.png)
![Admin: data, figure 11](images/ch16-b3-admin-data-11.png)
![Admin: data, figure 12](images/ch16-b3-admin-data-12.png)
![Admin: data, figure 13](images/ch16-b3-admin-data-13.png)
![Admin: data, figure 14](images/ch16-b3-admin-data-14.png)
![Admin: data, figure 15](images/ch16-b3-admin-data-15.png)
![Admin: data, figure 16](images/ch16-b3-admin-data-16.png)
![Admin: data, figure 17](images/ch16-b3-admin-data-17.png)
![Admin: data, figure 18](images/ch16-b3-admin-data-18.png)
![Admin: data, figure 19](images/ch16-b3-admin-data-19.png)
![Admin: data, figure 20](images/ch16-b3-admin-data-20.png)

![Admin: overview page, figure 1](images/ch16-b3-admin-list-01.png)
![Admin: overview page, figure 2](images/ch16-b3-admin-list-02.png)
![Admin: overview page, figure 3](images/ch16-b3-admin-list-03.png)
![Admin: overview page, figure 4](images/ch16-b3-admin-list-04.png)
![Admin: overview page, figure 5](images/ch16-b3-admin-list-05.png)
![Admin: overview page, figure 6](images/ch16-b3-admin-list-06.png)
![Admin: overview page, figure 7](images/ch16-b3-admin-list-07.png)
![Admin: overview page, figure 8](images/ch16-b3-admin-list-08.png)
![Admin: overview page, figure 9](images/ch16-b3-admin-list-09.png)
![Admin: overview page, figure 10](images/ch16-b3-admin-list-10.png)
![Admin: overview page, figure 11](images/ch16-b3-admin-list-11.png)
![Admin: overview page, figure 12](images/ch16-b3-admin-list-12.png)
![Admin: overview page, figure 13](images/ch16-b3-admin-list-13.png)
![Admin: overview page, figure 14](images/ch16-b3-admin-list-14.png)
![Admin: overview page, figure 15](images/ch16-b3-admin-list-15.png)

![Admin: detail variables, figure 1](images/ch16-b3-admin-vars-01.png)
![Admin: detail variables, figure 2](images/ch16-b3-admin-vars-02.png)
![Admin: detail variables, figure 3](images/ch16-b3-admin-vars-03.png)
![Admin: detail variables, figure 4](images/ch16-b3-admin-vars-04.png)
![Admin: detail variables, figure 5](images/ch16-b3-admin-vars-05.png)
![Admin: detail variables, figure 6](images/ch16-b3-admin-vars-06.png)
![Admin: detail variables, figure 7](images/ch16-b3-admin-vars-07.png)
![Admin: detail variables, figure 8](images/ch16-b3-admin-vars-08.png)
![Admin: detail variables, figure 9](images/ch16-b3-admin-vars-09.png)
![Admin: detail variables, figure 10](images/ch16-b3-admin-vars-10.png)
![Admin: detail variables, figure 11](images/ch16-b3-admin-vars-11.png)
![Admin: detail variables, figure 12](images/ch16-b3-admin-vars-12.png)
![Admin: detail variables, figure 13](images/ch16-b3-admin-vars-13.png)
![Admin: detail variables, figure 14](images/ch16-b3-admin-vars-14.png)
![Admin: detail variables, figure 15](images/ch16-b3-admin-vars-15.png)
![Admin: detail variables, figure 16](images/ch16-b3-admin-vars-16.png)
![Admin: detail variables, figure 17](images/ch16-b3-admin-vars-17.png)
![Admin: detail variables, figure 18](images/ch16-b3-admin-vars-18.png)
![Admin: detail variables, figure 19](images/ch16-b3-admin-vars-19.png)
![Admin: detail variables, figure 20](images/ch16-b3-admin-vars-20.png)
![Admin: detail variables, figure 21](images/ch16-b3-admin-vars-21.png)
![Admin: detail variables, figure 22](images/ch16-b3-admin-vars-22.png)
![Admin: detail variables, figure 23](images/ch16-b3-admin-vars-23.png)
![Admin: detail variables, figure 24](images/ch16-b3-admin-vars-24.png)
![Admin: detail variables, figure 25](images/ch16-b3-admin-vars-25.png)
![Admin: detail variables, figure 26](images/ch16-b3-admin-vars-26.png)
![Admin: detail variables, figure 27](images/ch16-b3-admin-vars-27.png)
![Admin: detail variables, figure 28](images/ch16-b3-admin-vars-28.png)
![Admin: detail variables, figure 29](images/ch16-b3-admin-vars-29.png)

![Admin: detail UI and logic, figure 1](images/ch16-b3-admin-detail-01.png)
![Admin: detail UI and logic, figure 2](images/ch16-b3-admin-detail-02.png)
![Admin: detail UI and logic, figure 3](images/ch16-b3-admin-detail-03.png)
![Admin: detail UI and logic, figure 4](images/ch16-b3-admin-detail-04.png)
![Admin: detail UI and logic, figure 5](images/ch16-b3-admin-detail-05.png)
![Admin: detail UI and logic, figure 6](images/ch16-b3-admin-detail-06.png)
![Admin: detail UI and logic, figure 7](images/ch16-b3-admin-detail-07.png)
![Admin: detail UI and logic, figure 8](images/ch16-b3-admin-detail-08.png)
![Admin: detail UI and logic, figure 9](images/ch16-b3-admin-detail-09.png)
![Admin: detail UI and logic, figure 10](images/ch16-b3-admin-detail-10.png)
![Admin: detail UI and logic, figure 11](images/ch16-b3-admin-detail-11.png)
![Admin: detail UI and logic, figure 12](images/ch16-b3-admin-detail-12.png)
![Admin: detail UI and logic, figure 13](images/ch16-b3-admin-detail-13.png)
![Admin: detail UI and logic, figure 14](images/ch16-b3-admin-detail-14.png)
![Admin: detail UI and logic, figure 15](images/ch16-b3-admin-detail-15.png)
![Admin: detail UI and logic, figure 16](images/ch16-b3-admin-detail-16.png)
![Admin: detail UI and logic, figure 17](images/ch16-b3-admin-detail-17.png)
![Admin: detail UI and logic, figure 18](images/ch16-b3-admin-detail-18.png)
![Admin: detail UI and logic, figure 19](images/ch16-b3-admin-detail-19.png)
![Admin: detail UI and logic, figure 20](images/ch16-b3-admin-detail-20.png)
![Admin: detail UI and logic, figure 21](images/ch16-b3-admin-detail-21.png)
![Admin: detail UI and logic, figure 22](images/ch16-b3-admin-detail-22.png)
![Admin: detail UI and logic, figure 23](images/ch16-b3-admin-detail-23.png)
![Admin: detail UI and logic, figure 24](images/ch16-b3-admin-detail-24.png)
![Admin: detail UI and logic, figure 25](images/ch16-b3-admin-detail-25.png)
![Admin: detail UI and logic, figure 26](images/ch16-b3-admin-detail-26.png)
![Admin: detail UI and logic, figure 27](images/ch16-b3-admin-detail-27.png)
![Admin: detail UI and logic, figure 28](images/ch16-b3-admin-detail-28.png)
![Admin: detail UI and logic, figure 29](images/ch16-b3-admin-detail-29.png)
![Admin: detail UI and logic, figure 30](images/ch16-b3-admin-detail-30.png)
![Admin: detail UI and logic, figure 31](images/ch16-b3-admin-detail-31.png)
![Admin: detail UI and logic, figure 32](images/ch16-b3-admin-detail-32.png)
![Admin: detail UI and logic, figure 33](images/ch16-b3-admin-detail-33.png)
![Admin: detail UI and logic, figure 34](images/ch16-b3-admin-detail-34.png)
![Admin: detail UI and logic, figure 35](images/ch16-b3-admin-detail-35.png)
![Admin: detail UI and logic, figure 36](images/ch16-b3-admin-detail-36.png)
![Admin: detail UI and logic, figure 37](images/ch16-b3-admin-detail-37.png)

![Admin: test, figure 1](images/ch16-b3-admin-test-01.png)
![Admin: test, figure 2](images/ch16-b3-admin-test-02.png)
![Admin: test, figure 3](images/ch16-b3-admin-test-03.png)
![Admin: test, figure 4](images/ch16-b3-admin-test-04.png)


## 16.5 Destination for the CAP app
- Destination **Build-Code**: type HTTP, URL of the service (for example `.../service/incidentManagement`), proxy Internet, authentication **OAuth2ClientCredentials**, client ID and secret from the **xsuaa** service credentials (`uaa` section), token URL = `uaa url + /oauth/token`
- Additional properties: `AppgyverEnabled=true`, `HTML5.DynamicDestination=true`, `WebIDEEnabled=true`; save, then **Check Connection**
- The **RAP-Geo** destination is described in 16.3.11 (the same steps appear in the repo's integration folder)

### Images: Destination screenshots
![CAP destination, figure 1](images/ch16-b4-buildcode-01.png)

![RAP destination, figure 1](images/ch16-b4-rap-01.png)
![RAP destination, figure 2](images/ch16-b4-rap-02.png)
![RAP destination, figure 3](images/ch16-b4-rap-03.png)
![RAP destination, figure 4](images/ch16-b4-rap-04.png)
![RAP destination, figure 5](images/ch16-b4-rap-05.png)
![RAP destination, figure 6](images/ch16-b4-rap-06.png)


## 16.6 Not covered in these notes
- **ABAP and CAP code bodies:** the long listings (the RAP behavior implementation, the AMDP helper, the 9,000-word test-data console class) were read as steps, not copied; open the repository to see them
- The `.mtar` templates and the draw.io diagram in the repo were not opened

## 16.7 Added by Claude, not from the sources
- The reading order and the tip about prompt detail are my own comments
- Screenshots were saved as the sample provides them; large ones were scaled down to at most 1500 pixels wide to keep the repo small, and I did not view each one individually

---

## Recap
- The sample joins three tools: Joule-generated CAP, a hand-written RAP geo service, and no-code Build Apps front ends
- Joule prompts used: `/cap-gen-model`, `/cap-gen-data`, and logic prompts in the graphical modeler
- RAP stores both plain and spatial coordinates; `getInRadius` runs in HANA through an AMDP
- Destinations (`equipmentmaintenance-equipmentmaintenanceSrv`, `RAP-Geo`, `Build-Code`) are the glue between Build Apps and the backends

---


*Previous: [Chapter 15: Keeping current: Q2 2026 release news, pricing and the golden path](15-release-news-pricing-golden-path.md)*

---

*Next: [Chapter 17: SAP Joule for Consultants: the full course](17-joule-for-consultants-course.md)*
