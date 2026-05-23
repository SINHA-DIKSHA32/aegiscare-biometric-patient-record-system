# AegisCare - AI Powered Biometric Healthcare Identity Platform

An MCA final-year healthcare project that retrieves patient records using multimodal biometric authentication and adds advanced layers such as AI disease-risk prediction, blockchain-style audit integrity, smart dashboards, and FHIR-like interoperability.

> Academic prototype: built for project demonstration and viva. It is not intended for real hospital deployment without professional clinical, legal, and security review.

## Why This Project Stands Out

- Goes beyond a normal patient CRUD system.
- Uses OpenCV-based face and fingerprint verification before opening records.
- Adds explainable AI risk scoring from vitals such as BP, sugar, SpO2, pulse, BMI, temperature, symptoms, and diagnosis.
- Maintains a blockchain-style tamper-evident ledger for important system events.
- Provides a smart dashboard for high-risk patient alerts.
- Exports FHIR-like JSON to demonstrate healthcare interoperability.

## Core Features

| Area | Feature |
| --- | --- |
| Authentication | Role-based login for Admin, Doctor, Receptionist, and Patient |
| Biometrics | Face + fingerprint enrollment and retrieval using OpenCV |
| Security | Password hashing, encrypted biometric files, audit logs |
| AI Layer | Explainable patient risk score and predicted disease focus areas |
| Blockchain Layer | Hash-linked ledger for tamper-evident audit events |
| Healthcare Records | Diagnosis, prescription, notes, vitals, allergies, emergency contact |
| Dashboard | Patient counts, AI risk alerts, ledger status, recent activity |
| Interoperability | FHIR-like JSON export for patient profile and observations |

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | HTML, CSS, Jinja templates |
| Backend | Python, Flask |
| Database | SQLite |
| Computer Vision | OpenCV, NumPy |
| AI Logic | Explainable rule-based clinical risk engine |
| Security Logic | Password hashing, encrypted files, SHA-256 hash chain |
| Testing | Pytest smoke tests |

## Repository Structure

```text
.
|-- app.py                       # Flask routes, database schema, RBAC, ledger, API export
|-- biometric_engine.py          # OpenCV preprocessing, matching, encrypted biometric storage
|-- clinical_ai.py               # Explainable AI disease-risk prediction
|-- seed_demo_data.py            # Demo patient and biometric sample generator
|-- requirements.txt             # Python dependencies
|-- templates/                   # Web pages
|-- static/css/style.css         # UI styling
|-- demo_samples/                # Demo face and fingerprint samples
|-- docs/                        # Architecture, demo guide, project documentation
|-- reports/                     # Place final project report PDF/DOCX here
|-- tests/                       # Smoke tests for GitHub CI
|-- .github/workflows/ci.yml     # GitHub Actions test workflow
`-- .env.example                 # Example environment settings
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python seed_demo_data.py
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Demo Login

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| Doctor | `doctor` | `doctor123` |
| Receptionist | `reception` | `reception123` |
| Patient | `patient` | `patient123` |

## Recommended Viva Demo Flow

1. Login as `doctor / doctor123`.
2. Open **Biometric Retrieval**.
3. Select **Multimodal: Face + Fingerprint**.
4. Upload `demo_samples/demo_face.png` and `demo_samples/demo_fingerprint.png`.
5. Show that the system opens `DEMO-001 Aarav Sharma`.
6. Add vitals and generate AI disease-risk prediction.
7. Login as `admin / admin123`.
8. Open **Smart Dashboard** and show high-risk alerts.
9. Open **Blockchain Ledger** and show chain verified status.
10. Open patient profile and click **FHIR JSON** to show interoperability.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Full Working Demo Guide](docs/FULL_WORKING_DEMO.md)
- [Project Documentation](docs/PROJECT_DOCUMENTATION.md)
- [GitHub Upload Guide](docs/GITHUB_UPLOAD_GUIDE.md)
- [Report Folder Instructions](reports/README.md)

## Testing

```bash
pytest -q
```

The repository also includes a GitHub Actions workflow that runs smoke tests on every push to `main`.

## Project Report

Upload your final report in the `reports/` folder before final submission. Recommended file names:

```text
reports/AegisCare_Project_Report.pdf
reports/AegisCare_Project_Report.docx
```

## Important Note

The encryption, biometric matching, AI predictions, and blockchain ledger are designed for academic demonstration. A production healthcare product would require certified biometric devices, stronger AI validation, consent management, HTTPS deployment, secure key management, and healthcare compliance review.
