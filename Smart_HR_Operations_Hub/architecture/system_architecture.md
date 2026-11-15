# System Architecture & Data Flow
**Project:** Smart HR Operations Hub  
**Platform:** n8n Workflow Automation Platform + AI Multi-Agent Network  

---

## 1. High-Level Architecture Diagram (Mermaid)

```mermaid
flowchart TD
    %% Input Layer
    subgraph Inputs ["1. Input Events & Triggers"]
        I1["Applicant Web Form (CV Upload)"]
        I2["Internal HR Pipeline Actions"]
        I3["Employee Onboarding Portal"]
        I4["Employee Policy Chat Query"]
        I5["Experience Certificate Form"]
        I6["Daily 08:00 AM Cron Schedule"]
    end

    %% Router Layer
    subgraph Routing ["2. Central Routing & Ingestion"]
        R1["Central Router Agent"]
        R2{"Classify & Route Request"}
    end

    %% Multi-Agent Specialists Layer
    subgraph Agents ["3. Multi-Agent Specialists"]
        A1["Document Specialist Agent (OCR / Normalization)"]
        A2["Recruitment Specialist Agent (Skill Gap Analysis)"]
        A3["Knowledge Specialist Agent (RAG Search)"]
        A4["Certificate Specialist Agent (Eligibility & Drafting)"]
    end

    %% Human Governance & Quality Control
    subgraph Governance ["4. Quality Control & Human-in-the-Loop"]
        G1["Supervisor Quality Agent"]
        G2{"HR Approval Required?"}
        G3["Human HR Reviewer Sign-off (Explicit Action)"]
        G4["Manual Exception / Anomaly Flag"]
    end

    %% Persistent State & Integration
    subgraph State ["5. Data Layer & Persistent Records"]
        D1[("Candidates Table")]
        D2[("Employees Table")]
        D3[("Documents Table")]
        D4[("Requests Table")]
        D5[("Jobs Table")]
        D6[("AuditLogs Table")]
        V1[("Vector Knowledge Store (Qdrant / PGVector)")]
    end

    %% Outputs & Side Effects
    subgraph Outputs ["6. Verified Outputs & Side Effects"]
        O1["Branded Experience Certificate PDF"]
        O2["HR Daily Monitoring Digest Email"]
        O3["Candidate Stage Notification"]
        O4["Grounded Policy Answer with Citations"]
        O5["Onboarding Welcome & Checklist Alert"]
    end

    %% Connections
    Inputs --> R1
    R1 --> R2
    
    R2 -- "CV Intake" --> A1
    R2 -- "Recruitment Evaluation" --> A2
    R2 -- "Onboarding Uploads" --> A1
    R2 -- "Policy Q&A" --> A3
    R2 -- "Certificate Issuance" --> A4
    R2 -- "Daily Sweep" --> G1

    A1 --> G1
    A2 --> G1
    A3 --> G1
    A4 --> G1

    G1 --> G2
    G2 -- "Yes (Hire / Certificate)" --> G3
    G2 -- "No (Read-Only / Digest)" --> State
    G2 -- "Quality Issue" --> G4

    G3 --> State
    State --> Outputs
    A3 <--> V1
```

---

## 2. Shared State & Request Life Cycle

Each event throughout the system adheres to a unified transaction schema:
- `request_id`: Deterministic UUID or formatted ID (e.g. `REQ-2026-0842`) to enforce idempotency.
- `actor_role`: Identity classification (`Applicant`, `Employee`, `HR_Manager`, `System`).
- `request_type`: Specific operational domain (`CV_INTAKE`, `RECRUITMENT`, `ONBOARDING`, `POLICY_RAG`, `CERTIFICATE`, `MONITORING`).
- `status`: Discrete lifecycle stage (`RECEIVED`, `EXTRACTED`, `PENDING_HR_APPROVAL`, `APPROVED`, `REJECTED`, `FAILED`, `COMPLETED`).
- `owner`: Assigned stakeholder or automated specialist agent.
- `next_action`: Clear subsequent step in the business process.
- `audit_timestamp`: ISO 8601 UTC timestamp tracking every mutation in `AuditLogs`.

---

## 3. Human-in-the-Loop Control Guarantees

As enforced by the project brief:
1. **Recruitment:** An applicant cannot be transitioned to `Hired` without an authorized HR officer recording the decision.
2. **Onboarding:** Uploaded national IDs and contracts undergo OCR validation, but authentication decisions require HR verification. Blurry images automatically transition to `Needs Review`.
3. **Certificates:** AI agents extract records and draft templates, but `PDF_GENERATION` and release links are strictly locked until an authorized manager executes an approval webhook.
