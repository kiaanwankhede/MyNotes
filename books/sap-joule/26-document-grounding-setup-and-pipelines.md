# Chapter 26: Document grounding, part 1: setup, repositories and pipelines

*Document grounding is Joule's retrieval layer: you point it at Google Drive, SharePoint, Work Zone or ServiceNow, it ingests and indexes your documents (plus the SAP Help Portal), and Joule uses them to add context to its answers. For a Gen AI developer this is the closest thing in the guide to a RAG pipeline API.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** what content types and limits apply, how to get a token with an X.509 certificate, how to connect each repository (service account, Entra app, ServiceNow certificate), and how to register a pipeline with cron schedule, include paths and chunk size
> - **Level:** advanced · **Time:** about 35 minutes of reading
> - **Source:** SJ022, the Joule Onboarding Guide PDF, section 5 up to the pipeline registration, pages 177 to 198 (read in full); read 9 November 2026
> - **Builds on:** [Chapter 4](04-setting-up-joule.md) §4.4 (document grounding in the landscape) and [Chapter 18](18-onboarding-guide-customer-managed-provisioning.md)

**After this chapter you can:**
- state the prerequisites, supported repositories, file types, size and count limits
- create the document grounding and Cloud Identity Services instances and bindings, and call the API with a bearer token and a client certificate
- build the destination for Google Drive, SharePoint (two ways) and ServiceNow
- register a pipeline for each repository and choose `resourceType`, `resourceId` and `includePaths` correctly
- set the cron schedule and the chunk size

---

## 26.1 What it does and what to watch

- **Idea:** it uses information from **documents you upload** and from the **SAP Help Portal** to add context to Joule's answers; **optional**, but the guide calls it highly recommended for some products (for example Signavio)
- **Order:** first finish the integration of your SAP product with Joule, then set up grounding
- **Prerequisites:**
  - you bought the **AI Unit SKU 8019164** and AI units (the document grounding entitlements are then added to the global account automatically)
  - the entitlements are added **to the subaccount where Joule is subscribed**
  - **Identity Authentication** is enabled
- **Cautions (important for any data owner):**
  - the capability **cannot tell what type of data it processes**, so it cannot know about personal data
  - **every ingested document is available to all Joule business users in the tenant**; do **not** ingest confidential or privileged documents (unless you use the SharePoint access control in Chapter 27)
  - for now answers **do not take context such as user location or user permission into account**
- **The five parts of the setup:** user authentication (26.3), repository integration (26.4), access from BTP (26.5), content ingestion (26.6), metadata configurations (Chapter 27)

## 26.2 Scope: repositories and content types

| Repository | Content types |
|---|---|
| Google Drive | DOCX, HTML (static), JPEG, JPG, JSON, PDF, PNG, PPTX, TIFF, TXT (Google Docs are remapped to DOCX, Google Slides to PPTX) |
| Microsoft SharePoint | the same list |
| SAP Build Work Zone, advanced edition | blog posts, DOCX, JPEG, JPG, knowledge base articles, PDF, PNG, TIFF, TXT, wiki pages, workpages |
| ServiceNow (SNOW) | knowledge base articles in HTML |

- **JSON and PPTX** are supported only on: AWS `eu10`, `eu11`, `us10`; Google Cloud `eu30`, `us30`; Azure `eu20`, `us21`
- **Images and tables embedded in PPTX** (HEIC, HEIF, JPEG, JPG, PNG) are supported on the same providers and regions
- **Pipeline limits:** at most **8,000 documents per pipeline**; each DOCX, HTML, JSON, PDF or TXT file at most **40 MB**
- **Content update:** by default each pipeline refreshes **once a day**; you can trigger it by hand (a POST to `<url>/pipeline/api/v1/pipeline/trigger`) or set a `cronExpression`

## 26.3 Configure user authentication (the API access)

- **Create the document grounding instance:** BTP cockpit, the Joule subaccount, Service Marketplace, "document grounding", Create, runtime environment **Other**, an instance name (**write it down**); View Instance, create a **service binding**, and **copy the binding URL** (this is your `<url>` for every call)
- **Create a Cloud Identity Services instance:** plan **application**, runtime **Other**; in Parameters pass the document grounding instance name:
  `"consumed-services":[{"service-instance-name":"<doc-grounding-instance-name>"}]`
- **Binding with a certificate:** a binding for that instance with parameters `credential-type` = `X509_GENERATED`, `validity` = `365`, `validity-type` = `DAYS`
  - Cloud Identity Services sends an e-mail when the certificate is about to expire; to renew, **re-create the binding**
- **From the binding** copy `clientid` and `authorization_endpoint`, and **edit the endpoint** by replacing the ending `/oauth2/authorize` with `/oauth2/token`
- **Make the certificate and key files** (for example `doc-grounding.crt` and `doc-grounding.key`) from the binding's `certificate` and `key`; the values contain `\n` instead of real line breaks, so **convert them** (a `sed 's/\\n/\n/g'` command on macOS or a PowerShell replace on Windows)
- **Get a token** with a client-credentials request that also presents the certificate:
  - POST to the edited endpoint; headers `accept: application/json`, `content-type: application/x-www-form-urlencoded`; body `client_id=<clientid>` and `grant_type=client_credentials`; use `--cert` and `--key`
  - the answer is a bearer token with `expires_in` **3600** seconds
- **Test the API:** `GET <url>/pipeline/api/v1/pipeline` with the bearer token and the certificate; you should get an **empty list `[]`** because no pipeline exists yet
- **For a developer:** this is **mutual TLS plus OAuth client credentials**; every later call needs both the bearer token and the certificate

## 26.4 Set up the data repository

### Google Drive
1. Create a **service account** in Google Cloud IAM
2. Create a **key** (OAuth 2.0 JWT, certificate-based private key) and download the **service account key JSON**
3. In Drive open the shared folder or shared drive, View Details, Manage Access
4. Add the JSON's **`client_email`** as a member with **Viewer**
5. Save; the pipeline sees only what is shared with this service account

### Microsoft SharePoint (Microsoft Entra ID)
- You need a SharePoint site, an Azure application that can reach it, and admin rights on that application
1. Create a **technical user**
2. **Register an application**; API permissions depend on the destination type (26.5):
   - **OAuth2Password**: `Sites.Read.All`, type **Delegated**
   - **OAuth2ClientCredentials**: `Sites.Selected` for Graph, type **Application**
3. **Expose a web API** scope on the registered application

### SAP Build Work Zone, advanced edition
- Follow SAP's separate "Integration With Document Grounding" steps

### ServiceNow (SNOW)
1. Create a **service account user** with **no password** and read-only admin access
2. Minimal roles: `knowledge_admin`, `user_admin`, `user_criteria_admin`, `snc_read_only`, `web_service_admin`, `snc_internal`
3. Generate a **PFX certificate bundle** from your PKI policy, encrypted with a password, associated with the service account (intermediate certificates optional)
4. The instance must support **mTLS** and the **V2 Table API**
- **Result:** you can read all rows of the table **`kb_knowledge`** and its child tables, the central store of article HTML; if the table was renamed, ask your account executive

## 26.5 Configure access from BTP (destinations)

- **Where:** the Joule subaccount, Connectivity, Destinations; always finish with **Check Connection**

### Google Drive (OAuth2ClientCredentials)

| Field | Value |
|---|---|
| Type / Proxy | HTTP / Internet |
| URL | `https://googleapis.com/drive/v3` (as printed in the guide) |
| Authentication | `OAuth2ClientCredentials` |
| Client ID | the client ID in the key JSON |
| Client Secret | **leave empty** |
| Token Service URL | `https://oauth2.googleapis.com/token` |
| Additional properties | `private_key`, `client_email`, `auth_uri` from the key JSON |

### SharePoint with client credentials

| Field | Value |
|---|---|
| URL | `https://<SHAREPOINT_DOMAIN>/sites/<SITE_NAME>` |
| Authentication | `OAuth2ClientCredentials` |
| Client ID / Secret | the Entra application credentials |
| Token Service URL | `https://login.microsoftonline.com/<TENANT_ID>/oauth2/v2.0/token` (or `login.microsoft.com`) |
| Additional properties | `scope` = `https://graph.microsoft.com/.default`; `tokenService.body.grant_type` = `client_credentials`; `tokenServiceURL.headers.Content-Type` = `application/x-www-form-urlencoded` |

- **The site name must match exactly** the name you enter when you create the pipeline (the text after `/sites/`, for example `210295`); a mismatch gives a **404 "Site not found"**

### SharePoint with password (OAuth2Password)

| Field | Value |
|---|---|
| URL | `https://graph.microsoft.com` |
| Authentication | `OAuth2Password` |
| User / Password | the technical user from Entra |
| Client ID / Secret | the Entra application credentials |
| Token Service URL | as above |
| Additional property | `scope` = `https://graph.microsoft.com/.default` |

### ServiceNow
- First **upload the PFX** under Connectivity, **Destination Certificates**, Create, Import
- Destination: URL = the SNOW instance URL (**type the `https://` URL first**, only then `ClientCertificateAuthentication` appears in the list), Proxy Internet, **Use client provided certificate** left empty, **Key Store Location** = the uploaded certificate, **Key Store Password** = the certificate password, **Use default JDK truststore** ticked

## 26.6 Register a pipeline

- **Call:** `POST <url>/pipeline/api/v1/pipeline` with the bearer token and the certificate; body has a `type` and a `configuration`
- **Cost warning:** **charges start once documents are uploaded** (Chapter 27, section on pricing); use **`includePaths`** to ingest only what you need; leaving it out ingests everything until the 8,000-document limit

### Cron schedule (five fields)

| Expression | Meaning |
|---|---|
| `0 * * * *` | every hour |
| `0 0 * * *` | every day at 12:00 a.m. |
| `0 0 * * FRI` | every Friday at 12:00 a.m. |
| `0 0 1 * *` | the first day of each month at 12:00 a.m. |

- Fields: minute (0 to 59), hour (0 to 23), day of month (1 to 31), month (1 to 12), day of week (0 to 6)
- (the guide's table prints these without spaces; the spaced form above is the standard reading)

### Google Drive pipeline
- **Body:** `{"type":"GoogleDrive","configuration":{"destination":"<DEST>","googleDrive":{"resourceType":"SHARED_DRIVE","resourceId":"<id>","includePaths":["<path>"]}}}`

| Parameter | Required | Meaning |
|---|---|---|
| `destination` | yes | the destination created with the service account |
| `resourceType` | yes | `SHARED_DRIVE` (organisation-owned) or `SHARED_FOLDER` (user-owned, shared) |
| `resourceId` | no | a specific shared drive or folder; **empty means auto-discovery** of everything the service account can read |
| `includePaths` | no | restrict to subfolders; required when targeting a subfolder of a shared drive |

- **Folder depth: at most 5 levels**
- **Response:** `{"pipelineId":"<uuid>"}`; it starts ingesting and **updates daily**
- **Metadata extracted automatically:** `fileId`, `webUrl`, `filePath`, `mimeType`
- **Which `resourceType`?** `SHARED_DRIVE`: appears under **Shared drives**, ID usually begins with **`0A`**; `SHARED_FOLDER`: appears under **My Drive** or **Shared with me**, ID does not start with `0A`
- **`resourceId` rules:**
  - with `SHARED_DRIVE` it can only be the **drive**, never a subfolder; use `includePaths` for subfolders
  - with `SHARED_FOLDER` it can be the top folder **or any subfolder**
  - find the ID in the URL after `/folders/`
- **`includePaths` rules:** start from the **root drive or folder name**, **no leading slash**, each segment must match the Drive name exactly, for example `["CustomerSharedDrive/FolderA/FolderB"]`

| Goal | Approach |
|---|---|
| Whole shared drive | `SHARED_DRIVE`, no `resourceId` or `includePaths` |
| One of several drives | `SHARED_DRIVE`, `resourceId` = the drive ID (starts with `0A`) |
| A subfolder inside a shared drive | `SHARED_DRIVE`, `resourceId` = the **drive** ID, `includePaths` = `["DriveName/FolderA/FolderB"]` |
| A whole shared folder | `SHARED_FOLDER`, `resourceId` = folder ID |
| A subfolder inside a shared folder | Option A: `resourceId` = the subfolder ID; Option B: `resourceId` = the parent ID plus `includePaths` = `["Parent/SubFolder"]` |

### SharePoint pipeline
- **Body:** `{"type":"MSSharePoint","configuration":{"destination":"<DEST>","sharePoint":{"site":{"name":"<SITE>","includePaths":["/<FOLDER_1>","/<FOLDER_2>"]}},"cronExpression":"0 */23 * * *"}}`
- `includePaths` and `cronExpression` are optional; nested folders are allowed (`"/Folder1/Folder2"`), **depth 5**; use folder paths **only inside the site's default document folder** (not drives or other libraries)

### Work Zone pipeline
- **Body:** `{"type":"WorkZone","metadata":{"destination":"<DEST>","dataRepositoryMetadata":[{"key":"lob","value":["workzone"]}]},"configuration":{"cronExpression":"0 * * * *"}}`

### ServiceNow pipeline
- **Body:** `{"type":"ServiceNow","configuration":{"destination":"<DEST>","serviceNow":{"includePaths":["<valid_sysparm_query>"]},"cronExpression":"0 */23 * * *"}}`
- `includePaths` takes **valid `sysparm_query` strings**, combined with **AND**; by default all **published, active** articles under the root domain are ingested

### Chunk size
- **`chunkSize`** controls how documents are split: **smaller chunks give more precise retrieval, larger chunks keep more context**
- Allowed values: **100, 500, 1000, 1500, 2000, 2500**; **default 1000 tokens**
- Available for GoogleDrive, MSSharePoint, ServiceNow and WorkZone pipelines; goes **inside the `configuration` object**
- Other rules: an unsupported value (for example 5000) is rejected with **HTTP 400** (also for a non-integer); **overlap is fixed and cannot be configured**; changes apply **on the next pipeline run**
- (The guide's four sample payloads use slightly different shapes, for example `pipelineType` and `isCronEnabled`; follow the typed `type` form shown for registration)

## 26.7 Added by Claude, not from the sources
- The "for a developer" remark about mutual TLS and the "RAG pipeline" framing are my interpretation
- The cron table is respaced; the guide prints the expressions without spaces
- The two body shapes for pipelines (`type` versus `pipelineType`) are as printed; I did not test either
- I did not run any of the calls

---

## Screenshots and figures from the sources
- Pages 177 to 198 contain no screenshots; the content is text, tables and request examples

---

## Recap
- Prerequisites: AI Unit SKU 8019164, entitlements on the Joule subaccount, IAS on
- **Mutual TLS + OAuth client credentials**: a document grounding instance, a Cloud Identity Services instance with an X.509 binding (365 days), a token valid for 3600 seconds
- Repositories: Drive (service account with Viewer), SharePoint (Entra app, two destination types), Work Zone (separate guide), ServiceNow (mTLS certificate and `kb_knowledge`)
- Limits: 8,000 documents per pipeline, 40 MB per file, folder depth 5, daily refresh by default
- `includePaths` controls both scope and **cost**; `chunkSize` defaults to 1000 tokens

## Practice
- What do you replace in the `authorization_endpoint` before requesting a token?
- When must you use `includePaths` instead of `resourceId` for Google Drive?
- Which `chunkSize` values are allowed and what is the default?

---

## How this chapter was checked
- All 22 pages were read in full; destination and parameter tables were copied field by field

## Sources and further reading
- SAP Help Portal, *Integrating Joule with SAP Solutions* (PDF, pages 177 to 198): https://help.sap.com/doc/de3af3c0f81642dbaa4d36172ed57a72/CLOUD/en-US/79bfc83ab386450c8cd9c7937ce26a3a.pdf
- SAP Discovery Center, Joule missions: https://discovery-center.cloud.sap/missiondetail/4538/

---

*Previous: [Chapter 25: Integrating Joule with SAP Concur, Fieldglass and the smaller products](25-integrating-joule-with-concur-fieldglass-and-smaller-products.md)*

*Next: [Chapter 27: Document grounding, part 2: metadata, status, access control, pricing and regions](27-document-grounding-part-2-metadata-status-access-control-pricing.md)*
