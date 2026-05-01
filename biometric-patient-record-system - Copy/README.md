# AegisCare: Advanced Biometric Patient Record Retrieval System with AI Risk Prediction

MCA-level final-year project using Python, Flask, SQLite, OpenCV, and an AI-assisted clinical risk layer.

## Advanced Highlights

- Biometric patient record retrieval:
  - Face recognition
  - Fingerprint recognition
- AI risk prediction engine:
  - Generates patient risk score
  - Predicts disease-risk profile (Hypertension, Diabetes, Cardio, Respiratory)
  - Creates priority alerts for high/critical risk patients
- Blockchain-style integrity chain:
  - Every major clinical/security event is hashed into linked blocks
  - Integrity verification page detects chain mismatch/tampering
- Smart doctor dashboard:
  - Risk distribution
  - Average risk trend graph
  - Priority patients queue
  - Open alert list
- Emergency care module:
  - Face/fingerprint emergency scan
  - Critical allergies, blood group, latest vitals, and risk snapshot
  - Family emergency alert message log
  - Printable ICU handover summary

## Tech Stack

- Backend: Flask + SQLite
- AI logic: Python risk model (feature scoring + probabilistic risk estimation)
- Biometric processing: OpenCV + encrypted template storage
- Security integrity: SHA-256 linked chain blocks

## Demo Login

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| Doctor | `doctor` | `doctor123` |
| Receptionist | `reception` | `reception123` |
| Patient | `patient` | `patient123` |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Quick Demo Flow

1. Login as `doctor` or `admin`.
2. Register patient with biometrics and baseline vitals.
3. Open the patient profile and add vitals or medical records.
4. Observe auto-updated AI risk score and priority alerts.
5. Test biometric retrieval from **Biometric Retrieval** page.
6. Use **Emergency Scan** with demo face/fingerprint to load ICU-critical details.
7. Send a demo family alert and print the ICU handover summary.
8. Open **Integrity Chain** page to verify hash-linked audit blocks.

## Key Files

- `app.py`: routes, schema, risk + alert workflow, dashboard integration
- `biometric_engine.py`: biometric encryption and face/fingerprint matching
- `ai_risk_engine.py`: risk scoring model and disease-risk inference
- `integrity_chain.py`: hash-chain block append and verification
- `templates/`: UI views for dashboard, emergency scan, patient profile, integrity, retrieval
- `static/css/style.css`: UI styles

## Academic Note

This project is designed for MCA demonstration and architecture-level understanding.  
For real hospital deployment, production hardening is required: compliance, stronger cryptographic key management, enterprise IAM, device-grade biometric pipelines, and validated clinical ML.
