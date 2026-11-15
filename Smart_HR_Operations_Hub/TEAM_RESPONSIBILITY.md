# Team Responsibility & Technical Ownership Document
**Module 6:** Expanded Capstone Assignment  
**Project:** Smart HR Operations Hub (AI-Powered Employee Lifecycle Automation)  
**Enterprise:** NexusCore Technologies Inc. (Enterprise People Operations Hub)  
**Team Composition:** 4 Students  

---

## Technical Ownership Matrix

| Student Name | Project Role | Workflows & Components Owned | Key Responsibilities & Deliverables |
| :--- | :--- | :--- | :--- |
| **Student 1 (Team Lead)** | System Architect & Workflow Orchestrator | Workflow 1 (CV Intake) & Workflow 6 (Operations Monitoring & Recovery) | - High-level architecture and n8n orchestration design.<br>- Intake Webhook/Form configuration, file validation, and error routing.<br>- Cron scheduling, operational metric aggregation, bounded retry logic, and idempotency control. |
| **Student 2** | AI Recruitment & Multi-Agent Specialist | Workflow 2 (Recruitment Pipeline & Review) & Multi-Agent Specifications | - Prompt engineering and JSON contracts for Router, Document Specialist, and Recruitment Specialist.<br>- Evidence-based skill-gap analysis algorithm (comparing CV quotes to JDs).<br>- Human-in-the-Loop stage gating (preventing autonomous LLM hiring/rejections). |
| **Student 3** | Knowledge Engineer & RAG Specialist | Workflow 4 (HR Policy Assistant RAG) & Vector Data Store | - Policy document drafting and structured markdown formatting.<br>- Document ingestion, chunking strategy, dense vector search, and citation generation.<br>- Implementing policy version update pipeline (v1.0 to v1.1 cache invalidation). |
| **Student 4** | Document Processing & Compliance Officer | Workflow 3 (Onboarding & OCR) & Workflow 5 (Certificate Generation) | - Synthetic dataset generation (fictional CVs, non-sensitive ID mockups, contracts).<br>- Document OCR parsing, blurriness/degradation detection, and onboarding checklist tracking.<br>- Branded HTML/CSS certificate template design, human HR authorization gate, and tamper-evident PDF issuance. |

---

## Collaborative Verification & Defense
All team members jointly participated in:
1. Executing and verifying the 18 acceptance test cases (**T01 through T18**).
2. Performing security and compliance auditing to guarantee zero PII or credentials in codebase commits.
3. Conducting rehearsal dry-runs for the 10–12 minute live capstone demonstration.
