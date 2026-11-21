# Reference: Current facts to re-check

*Prices, SKUs, counts, free offers and release changes go out of date fast. This page lists every one the book relies on, with the date it was last checked and the chapter that uses it, so a re-check means opening one page.*

> [!NOTE]
> **📍 At a glance**
> - **Use it for:** checking before you quote a number to a customer or in an exam answer
> - **What it is:** a summary of facts already in the chapters; each was web-checked when its chapter was written
> - **Level:** reference
> - **Last checked:** 21 Nov 2026

## 59.1 How to re-check


1. Open the chapter's source for the fact (listed in that chapter's *Sources*).
2. If the value changed, update the chapter first, then the row here.
3. Update the chapter's *Last checked* line in its at-a-glance box.

> [!TIP]
> **When to re-check**
> - Before quoting any price, SKU or limit to a customer.
> - After SAP Sapphire (May) and TechEd (autumn), when SAP announces most changes.
> - At each AI-unit or BTP contract renewal.

## 59.2 Prices and SKUs

| Fact | Value | Checked | Chapter |
|---|---|---|---|
| SAP Document AI, premium edition | sold in blocks of 100 documents; price on request | 21 Nov 2026 | [8.1](tutorial-document-ai-python.md) |

## 59.3 Free offers and end dates

| Fact | Value | Checked | Chapter |
|---|---|---|---|
| Generative AI hub | only on the SAP AI Core **extended** plan; plans are standard and extended (enterprise accounts); a 30-day basic trial exists | 21 Nov 2026 | [7.1](tutorial-genai-hub-python.md), [10.1](tutorial-rag-grounding-genai-hub.md) |

## 59.4 Counts and quotas

| Fact | Value | Checked | Chapter |
|---|---|---|---|
| SAP certifications | valid 12 months; *Stay Certified* in the 90 days before expiry adds 12 months | 21 Nov 2026 | [2.2](sap-ai-careers-certifications.md) |
| Document Translation limits | sync: 500 MB and 40,000 characters (fewer for ja, zh, ko, th); async: 2,500,000 characters; job results kept 3 days | 21 Nov 2026 | [9.4](tutorial-translation-hub-python.md), [9.5](tutorial-translation-hub-python.md) |
| SAP AI Core quotas | at most 50 resource groups and 5 tenant-wide generic secrets per tenant | 21 Nov 2026 | [10.5](tutorial-rag-grounding-genai-hub.md) |

## 59.5 Release changes that alter the steps

| Change | Effect | Checked | Chapter |
|---|---|---|---|
| SAP Cloud SDK for AI (Python) | `sap-ai-sdk-gen` 7.4.1 installed; Responses API since 6.10.0; Gemini needs the `[google]` extra; its LangChain classes need `[all]` | 21 Nov 2026 | [7.2](tutorial-genai-hub-python.md), [7.4](tutorial-genai-hub-python.md) |

## How this page was built

- Compiled on 21 Nov 2026 by scanning all 32 chapters for prices, SKUs, counts, dates and limits, outside the interview sections.
- No new sources: every value is copied from its chapter, with the date that chapter checked it.
- Split on 21 Nov 2026 from the single glossary/facts page of the former combined course book: this page keeps the rows whose main chapter is in this book. Links to the other SAP books name the book.

## Sources

- The chapters linked in each row, and their *Sources* sections.

Previous: [Reference: Glossary](reference-glossary.md) · Next: [SAP AI book introduction](README.md)
