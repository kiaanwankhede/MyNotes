# Chapter 27: Document grounding, part 2: metadata, status, access control, pricing and regions

*Everything after the first pipeline: tagging pipelines with metadata, searching and updating them, reading statuses down to a single document, mirroring SharePoint permissions into the index, the metadata-configuration API, and how the bill is calculated.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the metadata destination and its source-of-truth behaviour, the pipeline and document statuses, the API endpoints, SharePoint access control and its limits, the metadata-configuration API, the 0.005 AI-unit record and the supported regions
> - **Level:** advanced · **Time:** about 30 minutes of reading
> - **Source:** SJ022, the Joule Onboarding Guide PDF, sections 5.4.1 to 5.7, pages 199 to 221 (read in full); read 9 November 2026
> - **Builds on:** [Chapter 26](26-document-grounding-setup-and-pipelines.md)

**After this chapter you can:**
- create a pipeline with metadata and search pipelines by metadata
- trigger, patch, monitor and delete pipelines through the API
- turn on SharePoint access control and know it cannot be turned off
- create a metadata configuration, label documents, and build a pipeline from it
- compute the monthly cost in AI units and find supported regions

---

## 27.1 Pipelines with metadata

### Step 1: a metadata destination (Joule subaccount, Connectivity, Destinations)

| Field | Value |
|---|---|
| Type / Proxy | HTTP / Internet |
| URL | the metadata server URL, for example `https://<API_HOST>/rest/foundation/intelligence/generativeai/explainpay/v1/dg-pipeline/metadata?aiUseCase=HR%20Policy%20QA` |
| Authentication | `OAuth2ClientCredentials` |
| Client ID / Secret | from the Identity Authentication tenant |
| Token Service URL type / URL | Dedicated / the tenant token URL, `https://<IAS tenant>/oauth2/token` |
| Additional properties | `tokenService.body.resource` = `urn:sap:identity:application:provider:name:<DEPENDENCY_NAME>` (the dependency created in IAS); `pageSize` = `100` |

- Save, then **Check Connection**

### Step 2: create the pipeline with a `metadata` block
- **Rules for `dataRepositoryMetadata`:** no duplicate parameters; no null or empty item; the `value` array cannot be empty; **a value is at most 1024 characters; at most 20 key-value pairs; at most 20 items per value array**
- **Example:** a SharePoint pipeline body (type `MSSharePoint`, destination, site, includePaths, `cronExpression`, `isCronEnabled`) plus
  `"metadata":{"dataRepositoryMetadata":[{"key":"pipeline/agent-id","value":["dispute-agent"]},{"key":"pipeline/sf.lms.key","value":["Course1","Course5"]},{"key":"pipeline/ariba.test.key","value":["ariba1"]}],"destination":"<METADATA_DESTINATION>"}`
- Response `201` with the pipeline ID
- **`isCronEnabled`:** `true` runs the pipeline on a user-defined or system-calculated cron; `false` allows **manual triggering only**
- **Two destinations:** `configuration.destination` is the **repository** destination; `metadata.destination` is the **metadata server**
- **Source-of-truth rule (important):** once a metadata destination is set, **the metadata server is the source of truth**; keep it in sync with the repository:
  - in the metadata server but **not in the repository**: status **FAILED**
  - in the repository but **not returned by the metadata server**: **not processed**
  - in both: processed

### Step 3: search pipelines by metadata
- `POST <url>/pipeline/api/v1/pipeline/search` with a body of `dataRepositoryMetadata` key-value pairs; paging with the optional parameters `$top`, `$skip`, `$count`
- Response `200` with `count` and `resources`, each with `id`, `status` (for example `INPROGRESS`, `FINISHED`), `type` (the sample shows `SDM`, `MSSharePoint`, `S3`, `WorkZone`, `SFTP`), configuration and a `metadata` flag

## 27.2 Update pipelines

- **Trigger an update:** `POST <url>/pipeline/api/v1/pipeline/trigger` with `{"pipelineId":"<id>","metadataOnly":true}`; if `metadataOnly` is missing or `false`, **both content and metadata** are updated; response **202 Accepted**; the endpoint allows **5 calls per minute per tenant**
- **Change schedule or metadata:** `PATCH <url>/pipeline/api/v1/pipeline/{pipelineId}` with a body containing `configuration.cronExpression` and/or `metadata.dataRepositoryMetadata`; response **200**

## 27.3 Statuses and monitoring

| Level | Statuses |
|---|---|
| Pipeline | `NEW`, `UNKNOWN`, `INPROGRESS`, `FINISHED`, `FINISHEDWITHERRORS`, `TIMEOUT` |
| Execution | the same six |
| Document | `TO_BE_PROCESSED`, `INDEXED`, `REINDEXED`, `DEINDEXED`, `FAILED`, `FAILED_TO_BE_RETRIED`, `TO_BE_SCHEDULED` |

| Endpoint (all `GET`, under `<url>/pipeline/api/v1/pipeline/`) | Returns |
|---|---|
| `{pipelineId}/status` | `lastStarted`, `status`, `createdAt`, `lastCompletedAt` |
| `{pipelineId}/executions` (optional header `lastExecution`) | all executions: `id`, `status`, `createdAt`, `modifiedAt` |
| `{pipelineId}/executions/{executionId}` | one execution |
| `{pipelineId}/executions/{executionId}/documents` | document statuses in that execution |
| `{pipelineId}/executions/{executionId}/documents/{documentId}` | one document: `viewLocation`, `downloadLocation`, `status`, `absoluteUrl`, `title`, `metadataId`, timestamps |
| `{pipelineId}/documents` and `{pipelineId}/documents/{documentId}` | the same across the whole pipeline |

- Lists support `$top`, `$skip`, `$count`
- **For a developer:** when retrieval returns nothing, check the **document status** first (`FAILED` and `FAILED_TO_BE_RETRIED` explain missing content)

## 27.4 Delete a pipeline
- `DELETE <url>/pipeline/api/v1/pipeline/{pipelineId}` returns **202**; the pipeline, **its index content and its configuration are removed irreversibly**; do this when a pipeline is no longer needed or must be re-created with other settings

## 27.5 Document access control for SharePoint

- **What it does:** the index **mirrors the permissions of the repository**; when someone asks Joule, grounding returns **only the documents that person may see** in SharePoint
- **Only for SharePoint SaaS** (not on premise); only on **AWS `eu10`** and **Google Cloud `eu30`**
- **Extra Microsoft Graph permissions** (application type, admin consent, on top of the standard `Sites.Read.All`): **`Group.Read.All`** (security groups on documents) and **`User.Read.All`** (resolve group membership)
- **Switch:** `"accessControlEnabled": true` in the pipeline `configuration`
  - **default is `false`**, which means all indexed documents are **publicly accessible to any authenticated user**
  - **once `true` it can never be set back to `false`**
- **Permission refresh:** on **every pipeline run**; a daily pipeline reflects a SharePoint change within a day; shorten the cron to sync faster
- **Authorisation:** the signed-in user's identity is checked against the synced permissions; a user with no documents gets an **empty result, no error**
- **The user's IAS email must equal the email in Entra**, otherwise they cannot get documents they are allowed to see
- **Supported permission types:** Entra ID security groups, direct user assignments, inherited permissions; **not supported:** classic SharePoint groups, default sensitivity labels, conditional access policies
- **Technical limits:**

| Variable | Maximum |
|---|---|
| Documents per pipeline run | 1000 (the rest are not ingested in that run) |
| Direct viewers per document | 50 |
| Viewer groups per document | 50 |
| Total viewer groups per collection | 50 |
| Total viewers per collection (direct viewers plus group members) | 10,000 |
| Members per viewer group | 1000 |

## 27.6 Metadata configurations (SharePoint only, for now)

- **Purpose:** manage a repository configuration and add **custom metadata to individual documents**; the documents are stored with that metadata in the vector database
- **Base path:** `<url>/pipeline/metadata/api/v1/configurations`

| Action | Call | Result |
|---|---|---|
| Create | `POST …/configurations` with `id`, `name`, `destinationName`, `dataRepositoryType` (`MSSharePoint`), `includePaths`, optional `labels` (key/value) | **202** (the new ID is in the `Location` header), 400 on a bad spec |
| List | `GET …/configurations` with `$top`, `$skip`, `$count` | 200, including `enumerationStatus` (for example `IN_PROGRESS`) |
| Get one | `GET …/configurations/{metadataConfigId}` | 200, 400 or 404 |
| Delete | `DELETE …/configurations/{metadataConfigId}` | 202; **409 if pipelines still use it** (delete the pipelines first); 404; 500 |
| List its documents | `GET …/configurations/{id}/documents` (filter `absolutePath`, `$top`, `$skip`, `$count`) | the documents found in the repository |
| Get a document | `GET …/configurations/{id}/documents/{documentId}` | `id`, `title`, `absoluteFilePath`, `createdTimestamp`, `type`, `metadata` |
| Add custom metadata | `PATCH …/configurations/{id}/documents` with the header **`Content-Type: application/merge-patch+json`** and a body listing document `id` plus `metadata` entries (`key`, `value` array, `matchMode` such as `ANY`) | 200 batch patch applied |

- **Create the pipeline from it:** `POST <url>/pipeline/api/v1/pipeline` with `{"type":"metadata","configuration":{"metadataConfigId":"<id>","cronExpression":"0 */23 * * *"}}` (cron optional); response **201** with the pipeline ID
- **Effect:** the custom metadata added per document is attached when the document is **indexed, vectorised and stored in the vector database**

## 27.7 Metering and pricing

- **Applies to** users of the **`data-manager` service plan** for enterprise accounts
- **Metric:** **records per month**; **one record is one 50 MB block** uploaded; **one record equals 0.005 AI units**
- **Examples:** 45 MB is 1 record; 80 MB is 2; 105 MB is 3
- **ServiceNow:** each article in HTML under 50 MB is **1 record**
- **Formula:** `records this month × 0.005 × price per AI unit`
- **Carry-over:** records still in the service at month end **carry into the next month**; **deleting documents does not reduce the current month's records**, but deleted documents are not carried forward
- **Worked example (from the guide):** June, 10 records added, 5 deleted: June charge uses **10**; **5** are carried to July; July adds 10 and deletes 5: July charge uses **15** (5 + 10); 10 remain to August

| Documents uploaded | Size each | Deleted | Records charged |
|---|---|---|---|
| 1 | 50 MB | 0 | 1 |
| 1 | 52 MB | 0 | 2 |
| 10 | 5 MB | 0 | 10 |
| 25 | 50 MB | 10 | 25 |
| 25 | 51 MB | 10 | 50 |

- **Tip in the guide:** use the **AI Estimate** tool; related references are the SAP AI Services list and Discovery Center

## 27.8 Supported regions

- **SAP Help Portal content is not available** in document grounding for **SAP Sovereign Cloud** regions

| Provider | Regions |
|---|---|
| AWS | `ap10` Sydney, `ap11` Singapore, `br10` São Paulo, `eu10` Frankfurt, `eu11` Frankfurt EU Access, `jp10` Tokyo, `us10` US East (VA) |
| Google Cloud | `ap30` Sydney, `eu30` Frankfurt, `in30` Mumbai, `jp31` Tokyo, `sa30` KSA (Dammam), `us30` US Central (IA) |
| Azure | `ap20` Sydney, `ap21` Singapore, `eu20` Netherlands, `us21` US East (VA) |
| SAP Cloud Infrastructure | `eu01` Frankfurt, EU Access only |

- **Caution:** in `sa30` the **language models are deployed outside** the region

## 27.9 Added by Claude, not from the sources
- The status-debugging tip in 27.3 is my suggestion
- The guide's examples show `type` values such as `SDM`, `S3` and `SFTP` in the search response; I did not find those repositories listed as supported elsewhere, so I only repeated them as shown
- I did not run any of the calls

---

## Screenshots and figures from the sources
- Pages 199 to 221 contain no screenshots

---

## Recap
- With a **metadata destination**, the metadata server is the **source of truth**; keep it in sync or documents fail or drop out
- Status tracking exists at pipeline, execution and document level; `FAILED` explains missing answers
- **Access control** (SharePoint SaaS, `eu10` and `eu30` only) mirrors permissions, **default off**, **cannot be turned off again**, and has hard limits
- Metadata configurations add per-document labels that end up in the vector database
- Cost: **records of 50 MB, 0.005 AI units each**, deletions do not refund the current month, remaining records carry over

## Practice
- What happens to a document that the metadata server lists but the repository lacks?
- Why must you consider access control **before** creating a SharePoint pipeline?
- Compute the charge in records for 25 documents of 51 MB with 10 deleted.

---

## How this chapter was checked
- All 23 pages were read in full; the example table values were recomputed against the formula (a 51 MB document takes 2 records, so 25 of them take 50)

## Sources and further reading
- SAP Help Portal, *Integrating Joule with SAP Solutions* (PDF, pages 199 to 221): https://help.sap.com/doc/de3af3c0f81642dbaa4d36172ed57a72/CLOUD/en-US/79bfc83ab386450c8cd9c7937ce26a3a.pdf
- SAP Discovery Center, Joule missions: https://discovery-center.cloud.sap/missiondetail/4538/

---

*Previous: [Chapter 26: Document grounding, part 1](26-document-grounding-setup-and-pipelines.md)*

*Next: [Chapter 28: Multi-system support, troubleshooting and constraints](28-multi-system-support-troubleshooting-and-constraints.md)*
