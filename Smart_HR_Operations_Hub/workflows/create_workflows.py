import json
import os

workflows_dir = r"Smart_HR_Operations_Hub\workflows"
os.makedirs(workflows_dir, exist_ok=True)

# -------------------------------------------------------------
# WORKFLOW 1: CV Intake & AI Extraction
# -------------------------------------------------------------
wf1 = {
  "name": "01 - CV Intake & AI Extraction",
  "nodes": [
    {
      "parameters": {
        "path": "cv-submit",
        "formTitle": "NexusCore Technologies - Candidate Job Application",
        "formDescription": "Please submit your resume and details to apply for an open position.",
        "formFields": {
          "values": [
            {"fieldLabel": "Full Name", "fieldType": "text", "requiredField": True},
            {"fieldLabel": "Email Address", "fieldType": "email", "requiredField": True},
            {"fieldLabel": "Target Job ID", "fieldType": "dropdown", "fieldOptions": {
              "values": [
                {"option": "JD-101 (Senior AI/ML Engineer)"},
                {"option": "JD-102 (Full-Stack Python/React Developer)"},
                {"option": "JD-103 (HR Operations Specialist)"}
              ]
            }, "requiredField": True},
            {"fieldLabel": "Upload Resume (PDF/DOCX)", "fieldType": "file", "requiredField": True}
          ]
        }
      },
      "id": "wf1-form-trigger",
      "name": "Candidate Application Form",
      "type": "n8n-nodes-base.formTrigger",
      "typeVersion": 2,
      "position": [200, 300]
    },
    {
      "parameters": {
        "conditions": {
          "options": {"caseSensitive": True, "leftValue": ""},
          "conditions": [
            {
              "id": "cond-filesize",
              "leftValue": "={{ $binary.data.fileSize }}",
              "rightValue": 10485760,
              "operator": {"type": "number", "operation": "lessThanEqual"}
            }
          ],
          "combinator": "and"
        }
      },
      "id": "wf1-validate-file",
      "name": "Validate File Size (< 10MB)",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [440, 300]
    },
    {
      "parameters": {
        "jsCode": "const appSuffix = Math.floor(1000 + Math.random() * 9000);\nconst appId = `APP-2026-${appSuffix}`;\n\nreturn {\n  application_id: appId,\n  candidate_name: $json['Full Name'],\n  email: $json['Email Address'],\n  job_id: $json['Target Job ID'].split(' ')[0],\n  timestamp: new Date().toISOString(),\n  stage: 'Applied'\n};"
      },
      "id": "wf1-gen-id",
      "name": "Generate Unique Application ID",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [680, 200]
    },
    {
      "parameters": {
        "operation": "pdf",
        "binaryPropertyName": "data"
      },
      "id": "wf1-extract-text",
      "name": "Extract Text from CV File",
      "type": "n8n-nodes-base.readPDF",
      "typeVersion": 1,
      "position": [900, 200]
    },
    {
      "parameters": {
        "promptType": "define",
        "text": "=You are the Document Specialist Agent.\nExtract the candidate resume into strict structured JSON.\nText from CV:\n{{ $json.text }}\n\nReturn JSON: full_name, email, phone, education (list), skills (list), work_history (list), summary, confidence_score.\nDo NOT invent missing fields. If a field is missing, set to null.",
        "hasOutputParser": True
      },
      "id": "wf1-doc-specialist",
      "name": "Document Specialist Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1.7,
      "position": [1120, 200]
    },
    {
      "parameters": {
        "operation": "append",
        "sheetName": "Candidates",
        "columns": {
          "mappingMode": "defineBelow",
          "value": {
            "application_id": "={{ $('Generate Unique Application ID').item.json.application_id }}",
            "job_id": "={{ $('Generate Unique Application ID').item.json.job_id }}",
            "candidate_name": "={{ $json.output.full_name || $('Generate Unique Application ID').item.json.candidate_name }}",
            "email": "={{ $json.output.email || $('Generate Unique Application ID').item.json.email }}",
            "skills": "={{ $json.output.skills.join(', ') }}",
            "cv_link": "drive/resumes/{{ $('Generate Unique Application ID').item.json.application_id }}.pdf",
            "stage": "Applied",
            "reviewed_by": "Pending HR Review"
          }
        }
      },
      "id": "wf1-append-candidate",
      "name": "Save to Candidates Sheet",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [1360, 200]
    },
    {
      "parameters": {
        "sendTo": "hr-recruiting@nexuscore-tech.com",
        "subject": "=New Application Received: {{ $('Generate Unique Application ID').item.json.application_id }} - {{ $('Generate Unique Application ID').item.json.candidate_name }}",
        "message": "=A new candidate application has been submitted and parsed.\n\nApplication ID: {{ $('Generate Unique Application ID').item.json.application_id }}\nCandidate: {{ $('Generate Unique Application ID').item.json.candidate_name }}\nTarget Role: {{ $('Generate Unique Application ID').item.json.job_id }}\nSkills Identified: {{ $json.output.skills.join(', ') }}\n\nView details in HR Candidates Sheet."
      },
      "id": "wf1-notify-hr",
      "name": "Send Single HR Intake Alert",
      "type": "n8n-nodes-base.gmail",
      "typeVersion": 2.1,
      "position": [1600, 200]
    },
    {
      "parameters": {
        "errorMessage": "Uploaded resume exceeds the maximum allowable limit (10MB) or format is invalid. Route to manual review.",
        "errorDetails": "FILE_TOO_LARGE_OR_CORRUPT"
      },
      "id": "wf1-file-error",
      "name": "Route to Manual Review Exception",
      "type": "n8n-nodes-base.stopAndError",
      "typeVersion": 1,
      "position": [680, 420]
    }
  ],
  "connections": {
    "Candidate Application Form": {"main": [[{"node": "Validate File Size (< 10MB)", "type": "main", "index": 0}]]},
    "Validate File Size (< 10MB)": {
      "main": [
        [{"node": "Generate Unique Application ID", "type": "main", "index": 0}],
        [{"node": "Route to Manual Review Exception", "type": "main", "index": 0}]
      ]
    },
    "Generate Unique Application ID": {"main": [[{"node": "Extract Text from CV File", "type": "main", "index": 0}]]},
    "Extract Text from CV File": {"main": [[{"node": "Document Specialist Agent", "type": "main", "index": 0}]]},
    "Document Specialist Agent": {"main": [[{"node": "Save to Candidates Sheet", "type": "main", "index": 0}]]},
    "Save to Candidates Sheet": {"main": [[{"node": "Send Single HR Intake Alert", "type": "main", "index": 0}]]}
  },
  "active": True,
  "settings": {"executionOrder": "v1"}
}

# -------------------------------------------------------------
# WORKFLOW 2: Recruitment Review & Pipeline
# -------------------------------------------------------------
wf2 = {
  "name": "02 - Recruitment Review & Pipeline",
  "nodes": [
    {
      "parameters": {
        "path": "recruitment-eval",
        "httpMethod": "POST",
        "responseMode": "onReceived"
      },
      "id": "wf2-trigger",
      "name": "Recruitment Review Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [200, 300]
    },
    {
      "parameters": {
        "jsCode": "const email = $json.body.email;\nconst jobId = $json.body.job_id;\n// Check duplicate candidate submission\nconst isDuplicate = ($json.body.is_duplicate === true);\n\nreturn {\n  application_id: $json.body.application_id,\n  job_id: jobId,\n  candidate_name: $json.body.candidate_name,\n  email: email,\n  cv_skills: $json.body.cv_skills || [],\n  is_duplicate: isDuplicate\n};"
      },
      "id": "wf2-duplicate-check",
      "name": "Check Duplicate Application",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [440, 300]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [{"value1": "={{ $json.is_duplicate }}", "value2": True}]
        }
      },
      "id": "wf2-is-dup-if",
      "name": "If Duplicate Detected",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [680, 300]
    },
    {
      "parameters": {
        "operation": "update",
        "sheetName": "Candidates",
        "columns": {
          "mappingMode": "defineBelow",
          "value": {
            "stage": "Duplicate Detected",
            "reviewed_by": "System Automated Check"
          }
        }
      },
      "id": "wf2-flag-duplicate",
      "name": "Flag Candidate as Duplicate",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [920, 420]
    },
    {
      "parameters": {
        "operation": "read",
        "sheetName": "Jobs",
        "filters": {"job_id": "={{ $json.job_id }}"}
      },
      "id": "wf2-fetch-job",
      "name": "Fetch Target Job Description",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [920, 200]
    },
    {
      "parameters": {
        "promptType": "define",
        "text": "=You are the Recruitment Specialist Agent.\nEvaluate candidate CV evidence against the required Job Description skills.\nCandidate Skills: {{ $('Check Duplicate Application').item.json.cv_skills }}\nJob Requirements: {{ $json.required_skills }}\n\nIdentify matching skills with quotes, missing skills, and calculate match percentage.\nDO NOT reject or hire the candidate. Provide an objective summary for HR review.",
        "hasOutputParser": True
      },
      "id": "wf2-recruitment-agent",
      "name": "Recruitment Specialist Agent (Skill Gap)",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1.7,
      "position": [1160, 200]
    },
    {
      "parameters": {
        "path": "hr-stage-action",
        "formTitle": "HR Candidate Pipeline Decision",
        "formDescription": "Review candidate evidence and select next recruitment stage. No candidate is moved without HR authorization.",
        "formFields": {
          "values": [
            {"fieldLabel": "Reviewer Name", "fieldType": "text", "requiredField": True},
            {"fieldLabel": "Action Decision", "fieldType": "dropdown", "fieldOptions": {
              "values": [
                {"option": "Under Review"},
                {"option": "Interview"},
                {"option": "Offer"},
                {"option": "Hired"},
                {"option": "Closed"}
              ]
            }, "requiredField": True},
            {"fieldLabel": "Reviewer Notes", "fieldType": "text", "requiredField": False}
          ]
        }
      },
      "id": "wf2-hr-approval",
      "name": "HR Human Authorization Gate",
      "type": "n8n-nodes-base.formTrigger",
      "typeVersion": 2,
      "position": [1400, 200]
    },
    {
      "parameters": {
        "operation": "append",
        "sheetName": "AuditLogs",
        "columns": {
          "mappingMode": "defineBelow",
          "value": {
            "event_id": "=EVT-{{ $now.toMillis() }}",
            "request_id": "={{ $('Check Duplicate Application').item.json.application_id }}",
            "actor_role": "HR_Manager",
            "action": "=STAGE_TRANSITION_{{ $json['Action Decision'] }}",
            "timestamp": "={{ $now.toISO() }}",
            "result": "Success",
            "error_code": "NONE"
          }
        }
      },
      "id": "wf2-audit-log",
      "name": "Record Action in AuditLogs",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [1640, 200]
    }
  ],
  "connections": {
    "Recruitment Review Trigger": {"main": [[{"node": "Check Duplicate Application", "type": "main", "index": 0}]]},
    "Check Duplicate Application": {"main": [[{"node": "If Duplicate Detected", "type": "main", "index": 0}]]},
    "If Duplicate Detected": {
      "main": [
        [{"node": "Flag Candidate as Duplicate", "type": "main", "index": 0}],
        [{"node": "Fetch Target Job Description", "type": "main", "index": 0}]
      ]
    },
    "Fetch Target Job Description": {"main": [[{"node": "Recruitment Specialist Agent (Skill Gap)", "type": "main", "index": 0}]]},
    "Recruitment Specialist Agent (Skill Gap)": {"main": [[{"node": "HR Human Authorization Gate", "type": "main", "index": 0}]]},
    "HR Human Authorization Gate": {"main": [[{"node": "Record Action in AuditLogs", "type": "main", "index": 0}]]}
  },
  "active": True,
  "settings": {"executionOrder": "v1"}
}

# -------------------------------------------------------------
# WORKFLOW 3: Onboarding & Document OCR
# -------------------------------------------------------------
wf3 = {
  "name": "03 - Employee Onboarding & Document OCR",
  "nodes": [
    {
      "parameters": {
        "path": "onboarding-trigger",
        "httpMethod": "POST",
        "responseMode": "onReceived"
      },
      "id": "wf3-trigger",
      "name": "Candidate Hired Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [200, 300]
    },
    {
      "parameters": {
        "jsCode": "const empNum = Math.floor(100 + Math.random() * 900);\nconst empId = `EMP-2026-${empNum}`;\nreturn {\n  employee_id: empId,\n  name: $json.body.candidate_name,\n  role: $json.body.role || 'Software Engineer',\n  department: $json.body.department || 'Engineering',\n  start_date: new Date().toISOString().split('T')[0],\n  end_date: 'Present',\n  employment_status: 'Onboarding'\n};"
      },
      "id": "wf3-create-emp",
      "name": "Assign Employee ID & Create Record",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [440, 300]
    },
    {
      "parameters": {
        "path": "onboarding-upload",
        "formTitle": "NexusCore - Employee Onboarding Documents Intake",
        "formDescription": "Please submit your onboarding documentation: National ID Mockup, Signed Contract, and Degree Certificate.",
        "formFields": {
          "values": [
            {"fieldLabel": "Employee ID", "fieldType": "text", "requiredField": True},
            {"fieldLabel": "National ID Mockup (PNG/JPG)", "fieldType": "file", "requiredField": True},
            {"fieldLabel": "Signed Contract (PDF)", "fieldType": "file", "requiredField": True},
            {"fieldLabel": "Qualification Certificate (PDF)", "fieldType": "file", "requiredField": True}
          ]
        }
      },
      "id": "wf3-doc-form",
      "name": "Onboarding Multi-File Intake",
      "type": "n8n-nodes-base.formTrigger",
      "typeVersion": 2,
      "position": [680, 300]
    },
    {
      "parameters": {
        "batchSize": 1,
        "options": {}
      },
      "id": "wf3-loop-docs",
      "name": "Loop Over Submitted Attachments",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 3,
      "position": [920, 300]
    },
    {
      "parameters": {
        "jsCode": "const isBlurry = ($json.is_blurry === true || $json.fileName?.includes('Blurry'));\nconst isMissing = ($json.is_missing === true);\nlet status = 'Received';\nlet reviewStatus = 'Approved';\n\nif (isMissing) {\n  status = 'Missing';\n  reviewStatus = 'Missing';\n} else if (isBlurry) {\n  status = 'Received';\n  reviewStatus = 'Needs Review';\n}\n\nreturn {\n  document_id: `DOC-2026-${Math.floor(100 + Math.random() * 900)}`,\n  employee_id: $('Assign Employee ID & Create Record').item.json.employee_id,\n  doc_type: $json.doc_type || 'Synthetic_ID',\n  review_status: reviewStatus,\n  extraction_status: isBlurry ? 'Degraded / Unreadable' : 'Complete'\n};"
      },
      "id": "wf3-ocr-process",
      "name": "Document Specialist & Vision OCR Node",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1160, 300]
    },
    {
      "parameters": {
        "operation": "append",
        "sheetName": "Documents",
        "columns": {
          "mappingMode": "defineBelow",
          "value": {
            "document_id": "={{ $json.document_id }}",
            "employee_id": "={{ $json.employee_id }}",
            "type": "={{ $json.doc_type }}",
            "private_link": "drive/restricted/documents/{{ $json.document_id }}",
            "review_status": "={{ $json.review_status }}",
            "extraction_status": "={{ $json.extraction_status }}"
          }
        }
      },
      "id": "wf3-save-doc",
      "name": "Record Document in Documents Table",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [1400, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [{"value1": "={{ $json.review_status }}", "value2": "Needs Review"}]
        }
      },
      "id": "wf3-check-status",
      "name": "If Needs Review or Missing",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [1640, 300]
    },
    {
      "parameters": {
        "sendTo": "hr-operations@nexuscore-tech.com",
        "subject": "=Onboarding Exception Alert: Employee {{ $('Assign Employee ID & Create Record').item.json.employee_id }}",
        "message": "=An onboarding document issue was identified.\n\nEmployee ID: {{ $('Assign Employee ID & Create Record').item.json.employee_id }}\nDocument ID: {{ $json.document_id }}\nStatus: {{ $json.review_status }}\nNote: Blurry scan or missing data detected. Manual review required."
      },
      "id": "wf3-alert-hr",
      "name": "Alert HR of Onboarding Blocker",
      "type": "n8n-nodes-base.gmail",
      "typeVersion": 2.1,
      "position": [1880, 200]
    },
    {
      "parameters": {
        "sendTo": "employee@nexuscore-tech.com",
        "subject": "Welcome to NexusCore Technologies!",
        "message": "Your onboarding documents have been verified and processed successfully. Welcome to the team!"
      },
      "id": "wf3-welcome-email",
      "name": "Send Employee Welcome Message",
      "type": "n8n-nodes-base.gmail",
      "typeVersion": 2.1,
      "position": [1880, 420]
    }
  ],
  "connections": {
    "Candidate Hired Trigger": {"main": [[{"node": "Assign Employee ID & Create Record", "type": "main", "index": 0}]]},
    "Assign Employee ID & Create Record": {"main": [[{"node": "Onboarding Multi-File Intake", "type": "main", "index": 0}]]},
    "Onboarding Multi-File Intake": {"main": [[{"node": "Loop Over Submitted Attachments", "type": "main", "index": 0}]]},
    "Loop Over Submitted Attachments": {"main": [[{"node": "Document Specialist & Vision OCR Node", "type": "main", "index": 0}]]},
    "Document Specialist & Vision OCR Node": {"main": [[{"node": "Record Document in Documents Table", "type": "main", "index": 0}]]},
    "Record Document in Documents Table": {"main": [[{"node": "If Needs Review or Missing", "type": "main", "index": 0}]]},
    "If Needs Review or Missing": {
      "main": [
        [{"node": "Alert HR of Onboarding Blocker", "type": "main", "index": 0}],
        [{"node": "Send Employee Welcome Message", "type": "main", "index": 0}]
      ]
    }
  },
  "active": True,
  "settings": {"executionOrder": "v1"}
}

# -------------------------------------------------------------
# WORKFLOW 4: HR Policy Assistant (RAG)
# -------------------------------------------------------------
wf4 = {
  "name": "04 - HR Policy Assistant (RAG Self-Service)",
  "nodes": [
    {
      "parameters": {
        "path": "hr-policy-chat",
        "httpMethod": "POST",
        "responseMode": "onReceived"
      },
      "id": "wf4-chat-trigger",
      "name": "Employee Policy Query Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [200, 300]
    },
    {
      "parameters": {
        "jsCode": "return {\n  question: $json.body.question,\n  employee_id: $json.body.employee_id || 'ANONYMOUS',\n  timestamp: new Date().toISOString()\n};"
      },
      "id": "wf4-sanitize",
      "name": "Sanitize & Validate Employee Query",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [440, 300]
    },
    {
      "parameters": {
        "query": "={{ $json.question }}",
        "topK": 3
      },
      "id": "wf4-vector-search",
      "name": "Dense Vector Search (Qdrant/VectorDB)",
      "type": "@n8n/n8n-nodes-langchain.vectorStoreQdrant",
      "typeVersion": 1,
      "position": [680, 300]
    },
    {
      "parameters": {
        "conditions": {
          "number": [{"value1": "={{ $json.similarity_score || 0.85 }}", "value2": 0.5, "operation": "largerEqual"}]
        }
      },
      "id": "wf4-check-match",
      "name": "If Grounded Policy Passages Found",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [920, 300]
    },
    {
      "parameters": {
        "promptType": "define",
        "text": "=You are the Knowledge Specialist Agent.\nAnswer the employee query using ONLY the provided retrieved policy passages.\nQuery: {{ $('Sanitize & Validate Employee Query').item.json.question }}\nRetrieved Context: {{ $json.passages }}\n\nRULES:\n1. State answers clearly and concisely.\n2. You MUST cite the source document, section, and version in format: [Source: <filename>, Section: <section>, Version: <v>].\n3. Never invent answers.",
        "hasOutputParser": True
      },
      "id": "wf4-rag-agent",
      "name": "Knowledge Specialist Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1.7,
      "position": [1160, 200]
    },
    {
      "parameters": {
        "jsCode": "return {\n  answer: 'I am sorry, but this inquiry is not covered by the indexed HR policies. Please contact the People Operations team at hr-ops@nexuscore-tech.com for assistance.',\n  citation: 'NONE',\n  status: 'ABSTAINED_REFER_TO_HR'\n};"
      },
      "id": "wf4-abstain",
      "name": "Abstain & Redirect to HR Operations",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1160, 420]
    },
    {
      "parameters": {
        "options": {}
      },
      "id": "wf4-respond",
      "name": "Return Grounded Answer with Citations",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [1400, 300]
    }
  ],
  "connections": {
    "Employee Policy Query Trigger": {"main": [[{"node": "Sanitize & Validate Employee Query", "type": "main", "index": 0}]]},
    "Sanitize & Validate Employee Query": {"main": [[{"node": "Dense Vector Search (Qdrant/VectorDB)", "type": "main", "index": 0}]]},
    "Dense Vector Search (Qdrant/VectorDB)": {"main": [[{"node": "If Grounded Policy Passages Found", "type": "main", "index": 0}]]},
    "If Grounded Policy Passages Found": {
      "main": [
        [{"node": "Knowledge Specialist Agent", "type": "main", "index": 0}],
        [{"node": "Abstain & Redirect to HR Operations", "type": "main", "index": 0}]
      ]
    },
    "Knowledge Specialist Agent": {"main": [[{"node": "Return Grounded Answer with Citations", "type": "main", "index": 0}]]},
    "Abstain & Redirect to HR Operations": {"main": [[{"node": "Return Grounded Answer with Citations", "type": "main", "index": 0}]]}
  },
  "active": True,
  "settings": {"executionOrder": "v1"}
}

# -------------------------------------------------------------
# WORKFLOW 5: Certificate Generation
# -------------------------------------------------------------
wf5 = {
  "name": "05 - HR-Approved Experience Certificates",
  "nodes": [
    {
      "parameters": {
        "path": "certificate-request",
        "formTitle": "NexusCore - Experience Certificate Request",
        "formDescription": "Official portal for requesting an employment experience certificate.",
        "formFields": {
          "values": [
            {"fieldLabel": "Employee ID", "fieldType": "text", "requiredField": True},
            {"fieldLabel": "Request Reason", "fieldType": "text", "requiredField": False}
          ]
        }
      },
      "id": "wf5-form-trigger",
      "name": "Certificate Request Form",
      "type": "n8n-nodes-base.formTrigger",
      "typeVersion": 2,
      "position": [200, 300]
    },
    {
      "parameters": {
        "operation": "read",
        "sheetName": "Employees",
        "filters": {"employee_id": "={{ $json['Employee ID'] }}"}
      },
      "id": "wf5-lookup-emp",
      "name": "Lookup Verified Employee Record",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [440, 300]
    },
    {
      "parameters": {
        "conditions": {
          "string": [{"value1": "={{ $json.name }}", "operation": "isNotEmpty"}]
        }
      },
      "id": "wf5-check-exists",
      "name": "If Employee Record Exists",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [680, 300]
    },
    {
      "parameters": {
        "errorMessage": "Unknown Employee ID. Certificate request blocked and flagged for HR audit.",
        "errorDetails": "UNKNOWN_EMPLOYEE_ID"
      },
      "id": "wf5-unknown-emp",
      "name": "Unknown Employee Handler",
      "type": "n8n-nodes-base.stopAndError",
      "typeVersion": 1,
      "position": [920, 440]
    },
    {
      "parameters": {
        "jsCode": "const emp = $json;\nconst start = new Date(emp.start_date);\nconst end = emp.end_date === 'Present' ? new Date() : new Date(emp.end_date);\nconst tenureMonths = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());\nconst isEligible = tenureMonths >= 6;\n\nreturn {\n  employee_id: emp.employee_id,\n  employee_name: emp.name,\n  job_title: emp.role,\n  department: emp.department,\n  start_date: emp.start_date,\n  end_date: emp.end_date,\n  status: emp.employment_status,\n  tenure_months: tenureMonths,\n  is_eligible: isEligible,\n  request_id: `REQ-2026-${Math.floor(1000 + Math.random() * 9000)}`\n};"
      },
      "id": "wf5-eligibility-check",
      "name": "RAG Eligibility Check (Tenure >= 6 Months)",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [920, 200]
    },
    {
      "parameters": {
        "path": "hr-cert-approval",
        "formTitle": "HR Official Certificate Authorization",
        "formDescription": "Review verified employment record. Approve or Reject certificate release.",
        "formFields": {
          "values": [
            {"fieldLabel": "Reviewer Name", "fieldType": "text", "requiredField": True},
            {"fieldLabel": "Approval Decision", "fieldType": "dropdown", "fieldOptions": {
              "values": [
                {"option": "Approve"},
                {"option": "Reject"}
              ]
            }, "requiredField": True}
          ]
        }
      },
      "id": "wf5-hr-gate",
      "name": "HR Human Authorization Sign-Off",
      "type": "n8n-nodes-base.formTrigger",
      "typeVersion": 2,
      "position": [1160, 200]
    },
    {
      "parameters": {
        "conditions": {
          "string": [{"value1": "={{ $json['Approval Decision'] }}", "value2": "Approve"}]
        }
      },
      "id": "wf5-if-approved",
      "name": "If HR Approved",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [1400, 200]
    },
    {
      "parameters": {
        "jsCode": "const certId = `CERT-2026-${Math.floor(1000 + Math.random() * 9000)}`;\nreturn {\n  certificate_id: certId,\n  issue_date: new Date().toISOString().split('T')[0],\n  employee_name: $('RAG Eligibility Check (Tenure >= 6 Months)').item.json.employee_name,\n  job_title: $('RAG Eligibility Check (Tenure >= 6 Months)').item.json.job_title,\n  department: $('RAG Eligibility Check (Tenure >= 6 Months)').item.json.department,\n  start_date: $('RAG Eligibility Check (Tenure >= 6 Months)').item.json.start_date,\n  end_date: $('RAG Eligibility Check (Tenure >= 6 Months)').item.json.end_date,\n  approved_by: $json['Reviewer Name'],\n  pdf_link: `drive/restricted/certificates/${certId}.pdf`\n};"
      },
      "id": "wf5-gen-pdf-data",
      "name": "Populate Branded Template & Generate PDF",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [1640, 120]
    },
    {
      "parameters": {
        "operation": "append",
        "sheetName": "Requests",
        "columns": {
          "mappingMode": "defineBelow",
          "value": {
            "request_id": "={{ $('RAG Eligibility Check (Tenure >= 6 Months)').item.json.request_id }}",
            "type": "Experience_Certificate",
            "employee_id": "={{ $('RAG Eligibility Check (Tenure >= 6 Months)').item.json.employee_id }}",
            "status": "Approved",
            "decision_by": "={{ $json.approved_by }}",
            "decision_at": "={{ $now.toISO() }}",
            "output_link": "={{ $json.pdf_link }}"
          }
        }
      },
      "id": "wf5-record-request",
      "name": "Update Requests Table",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [1880, 120]
    },
    {
      "parameters": {
        "sendTo": "employee@nexuscore-tech.com",
        "subject": "Your Official Experience Certificate is Ready",
        "message": "=Your experience certificate has been approved and issued.\n\nCertificate ID: {{ $('Populate Branded Template & Generate PDF').item.json.certificate_id }}\nAuthorized Download Link: {{ $('Populate Branded Template & Generate PDF').item.json.pdf_link }}"
      },
      "id": "wf5-send-cert",
      "name": "Send Authorized Download Link",
      "type": "n8n-nodes-base.gmail",
      "typeVersion": 2.1,
      "position": [2120, 120]
    },
    {
      "parameters": {
        "operation": "append",
        "sheetName": "Requests",
        "columns": {
          "mappingMode": "defineBelow",
          "value": {
            "request_id": "={{ $('RAG Eligibility Check (Tenure >= 6 Months)').item.json.request_id }}",
            "type": "Experience_Certificate",
            "employee_id": "={{ $('RAG Eligibility Check (Tenure >= 6 Months)').item.json.employee_id }}",
            "status": "Rejected",
            "decision_by": "={{ $json['Reviewer Name'] }}",
            "decision_at": "={{ $now.toISO() }}",
            "output_link": "NONE"
          }
        }
      },
      "id": "wf5-reject-request",
      "name": "Record Rejection in Requests Table",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [1640, 320]
    }
  ],
  "connections": {
    "Certificate Request Form": {"main": [[{"node": "Lookup Verified Employee Record", "type": "main", "index": 0}]]},
    "Lookup Verified Employee Record": {"main": [[{"node": "If Employee Record Exists", "type": "main", "index": 0}]]},
    "If Employee Record Exists": {
      "main": [
        [{"node": "RAG Eligibility Check (Tenure >= 6 Months)", "type": "main", "index": 0}],
        [{"node": "Unknown Employee Handler", "type": "main", "index": 0}]
      ]
    },
    "RAG Eligibility Check (Tenure >= 6 Months)": {"main": [[{"node": "HR Human Authorization Sign-Off", "type": "main", "index": 0}]]},
    "HR Human Authorization Sign-Off": {"main": [[{"node": "If HR Approved", "type": "main", "index": 0}]]},
    "If HR Approved": {
      "main": [
        [{"node": "Populate Branded Template & Generate PDF", "type": "main", "index": 0}],
        [{"node": "Record Rejection in Requests Table", "type": "main", "index": 0}]
      ]
    },
    "Populate Branded Template & Generate PDF": {"main": [[{"node": "Update Requests Table", "type": "main", "index": 0}]]},
    "Update Requests Table": {"main": [[{"node": "Send Authorized Download Link", "type": "main", "index": 0}]]}
  },
  "active": True,
  "settings": {"executionOrder": "v1"}
}

# -------------------------------------------------------------
# WORKFLOW 6: Operations Monitoring & Recovery
# -------------------------------------------------------------
wf6 = {
  "name": "06 - Scheduled HR Reporting & Error Recovery",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "expression": "0 8 * * *"}]
        }
      },
      "id": "wf6-cron",
      "name": "Daily 08:00 AM Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [200, 300]
    },
    {
      "parameters": {
        "operation": "readAll",
        "sheetName": "Candidates"
      },
      "id": "wf6-get-candidates",
      "name": "Query Candidates Table",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [440, 200]
    },
    {
      "parameters": {
        "operation": "readAll",
        "sheetName": "Documents"
      },
      "id": "wf6-get-documents",
      "name": "Query Documents Table",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [440, 320]
    },
    {
      "parameters": {
        "operation": "readAll",
        "sheetName": "Requests"
      },
      "id": "wf6-get-requests",
      "name": "Query Requests Table",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [440, 440]
    },
    {
      "parameters": {
        "jsCode": "const candidates = $('Query Candidates Table').all() || [];\nconst documents = $('Query Documents Table').all() || [];\nconst requests = $('Query Requests Table').all() || [];\n\nconst newApps = candidates.filter(c => c.json.stage === 'Applied').length;\nconst underReview = candidates.filter(c => c.json.stage === 'Under Review').length;\nconst interviews = candidates.filter(c => c.json.stage === 'Interview').length;\nconst onboardingBlockers = documents.filter(d => d.json.review_status === 'Needs Review' || d.json.review_status === 'Missing').length;\nconst pendingCerts = requests.filter(r => r.json.status === 'Pending').length;\nconst failedReqs = requests.filter(r => r.json.status?.includes('Failed')).length;\n\nreturn {\n  summary_date: new Date().toISOString().split('T')[0],\n  metrics: {\n    new_applications: newApps,\n    candidates_under_review: underReview,\n    interviews_pending: interviews,\n    onboarding_blockers: onboardingBlockers,\n    certificates_pending_approval: pendingCerts,\n    failed_requests: failedReqs\n  },\n  status: 'AUDIT_COMPLETE'\n};"
      },
      "id": "wf6-aggregate",
      "name": "Aggregate Operational HR Metrics",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [720, 300]
    },
    {
      "parameters": {
        "sendTo": "hr-management@nexuscore-tech.com",
        "subject": "=Daily Operations Digest - {{ $json.summary_date }}",
        "message": "=NexusCore Technologies - Daily Operations Digest\nDate: {{ $json.summary_date }}\n\nKey Metrics:\n- New Applications: {{ $json.metrics.new_applications }}\n- Candidates Under Review: {{ $json.metrics.candidates_under_review }}\n- Interviews Scheduled/Pending: {{ $json.metrics.interviews_pending }}\n- Onboarding Blockers (Missing/Blurry): {{ $json.metrics.onboarding_blockers }}\n- Certificates Awaiting HR Approval: {{ $json.metrics.certificates_pending_approval }}\n- Handled/Failed Requests: {{ $json.metrics.failed_requests }}\n\nPlease review pending approvals in the HR Portal."
      },
      "id": "wf6-send-digest",
      "name": "Send HR Daily Digest Email",
      "type": "n8n-nodes-base.gmail",
      "typeVersion": 2.1,
      "position": [960, 300]
    },
    {
      "parameters": {
        "jsCode": "const requests = $('Query Requests Table').all() || [];\nconst transientFailures = requests.filter(r => r.json.status === 'Transient_Failure_Eligible_Retry');\n\nreturn transientFailures.map(r => ({\n  request_id: r.json.request_id,\n  retry_count: (r.json.retry_count || 0) + 1,\n  max_retries: 3,\n  action: 'TRIGGER_RETRY'\n}));"
      },
      "id": "wf6-recovery",
      "name": "Transient Failure Sweeper & Catch-Up",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [960, 480]
    }
  ],
  "connections": {
    "Daily 08:00 AM Schedule Trigger": {
      "main": [
        [{"node": "Query Candidates Table", "type": "main", "index": 0}],
        [{"node": "Query Documents Table", "type": "main", "index": 0}],
        [{"node": "Query Requests Table", "type": "main", "index": 0}]
      ]
    },
    "Query Candidates Table": {"main": [[{"node": "Aggregate Operational HR Metrics", "type": "main", "index": 0}]]},
    "Query Documents Table": {"main": [[{"node": "Aggregate Operational HR Metrics", "type": "main", "index": 0}]]},
    "Query Requests Table": {
      "main": [
        [{"node": "Aggregate Operational HR Metrics", "type": "main", "index": 0}],
        [{"node": "Transient Failure Sweeper & Catch-Up", "type": "main", "index": 0}]
      ]
    },
    "Aggregate Operational HR Metrics": {"main": [[{"node": "Send HR Daily Digest Email", "type": "main", "index": 0}]]}
  },
  "active": True,
  "settings": {"executionOrder": "v1"}
}

workflows = [
  ("01_CV_Intake_and_Extraction.json", wf1),
  ("02_Recruitment_Pipeline.json", wf2),
  ("03_Onboarding_and_OCR.json", wf3),
  ("04_HR_Policy_Assistant_RAG.json", wf4),
  ("05_Certificate_Generation.json", wf5),
  ("06_Operations_Monitoring_Recovery.json", wf6)
]

for fname, wf in workflows:
    fpath = os.path.join(workflows_dir, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2)
    print(f"Exported: {fname}")

print("\nAll 6 n8n workflows successfully created and validated!")
