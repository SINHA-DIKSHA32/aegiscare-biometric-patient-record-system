# Architecture

## High-Level Flow

```mermaid
flowchart LR
    User["Doctor / Admin / Receptionist / Patient"] --> UI["Flask Web UI"]
    UI --> Auth["Role-Based Authentication"]
    UI --> Bio["Biometric Retrieval"]
    Bio --> OpenCV["OpenCV Face + Fingerprint Matching"]
    OpenCV --> Store["Encrypted Biometric Storage"]
    Bio --> Records["Patient Record Access"]
    Records --> AI["AI Risk Engine"]
    Records --> FHIR["FHIR-like JSON Export"]
    Auth --> Ledger["Blockchain-style Audit Ledger"]
    Bio --> Ledger
    AI --> Ledger
    FHIR --> Ledger
```

## Main Modules

| Module | Responsibility |
| --- | --- |
| `app.py` | Flask routes, schema creation, login, RBAC, patient workflow, vitals, ledger, export |
| `biometric_engine.py` | Image decoding, OpenCV preprocessing, similarity scoring, encrypted file handling |
| `clinical_ai.py` | Explainable disease-risk scoring and recommendations |
| `templates/` | Web interface for dashboard, patients, retrieval, ledger, and reports |
| `static/css/style.css` | Responsive dashboard and clinical UI styling |
| `seed_demo_data.py` | Creates demo patient, biometric images, medical record, and AI vitals |

## Database Entities

```mermaid
erDiagram
    USERS ||--o{ AUDIT_LOGS : performs
    PATIENTS ||--o{ BIOMETRICS : has
    PATIENTS ||--o{ MEDICAL_RECORDS : has
    PATIENTS ||--o{ VITALS : has
    BLOCKCHAIN_LEDGER ||--|| BLOCKCHAIN_LEDGER : links_previous_hash

    PATIENTS {
        int id
        string patient_code
        string full_name
        string phone
        string blood_group
        float height_cm
        float weight_kg
        string chronic_conditions
    }

    VITALS {
        int id
        int patient_id
        float systolic_bp
        float fasting_glucose
        int ai_risk_score
        string ai_risk_level
    }

    BLOCKCHAIN_LEDGER {
        int id
        string event_type
        string previous_hash
        string block_hash
    }
```

## Security Layers

- Password hashing for login credentials.
- Role-based access control for admin, doctor, receptionist, and patient.
- Encrypted biometric file storage for demo-level privacy.
- Biometric session verification before patient self-access.
- SHA-256 hash-linked ledger for tamper-evident audit history.

## AI Layer

The AI layer is intentionally explainable for viva. It uses transparent clinical rules and gives:

- Risk score from `0` to `100`.
- Risk level: Low, Moderate, High, or Critical.
- Predicted disease focus areas.
- Findings that explain why the score was generated.
- Suggested follow-up action.

Inputs include BP, glucose, pulse, temperature, SpO2, BMI, symptoms, age, and latest diagnosis.
