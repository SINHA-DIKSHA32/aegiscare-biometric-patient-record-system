# AegisCare: Advanced Biometric Patient Record Retrieval System with AI Risk Prediction

## Face/Fingerprint Biometric Retrieval, Emergency Scan, Family Alert, and Blockchain-Based Data Integrity

---

# ABSTRACT

AegisCare is a healthcare-focused web application designed to improve patient identification, medical record retrieval, emergency treatment support, and clinical risk monitoring. In many hospitals, patient records are retrieved using registration numbers, phone numbers, ID cards, or manual search. These approaches may work in normal conditions, but they become unreliable during emergency situations, especially when a patient is unconscious, injured, or unable to provide identity details.

The proposed system solves this problem by using biometric authentication. It supports face image matching and fingerprint image matching. After successful biometric identification, the system retrieves the patient's medical profile, allergies, blood group, emergency contact, medical history, prescriptions, and latest health vitals. This makes the system especially useful in accident and ICU-related cases where doctors need critical information immediately.

The project also includes an AI-based risk prediction layer. The AI module uses patient vitals such as blood pressure, heart rate, SpO2, glucose level, body temperature, respiratory rate, age, and medical history to generate a risk score. It predicts possible risk categories such as hypertension risk, diabetes risk, cardio risk, and respiratory risk. If a patient is categorized as high or critical risk, the system generates a priority alert for doctors.

To improve security, biometric files are encrypted before storage. The application also includes a blockchain-style data integrity module that creates linked hash blocks for important events such as patient registration, biometric enrollment, medical record updates, AI risk assessment, emergency scan, family alert, and alert resolution. This helps demonstrate tamper-evident healthcare data management.

The system includes a smart doctor dashboard that displays patient statistics, open alerts, risk distribution, recent activities, and integrity status. A dedicated emergency scan module allows staff to scan a face or fingerprint and instantly view allergy information, blood group, latest vitals, AI risk, open alerts, and latest diagnosis. It also provides a family emergency alert workflow and a printable ICU handover summary.

The system is implemented using Python Flask, SQLite, OpenCV, NumPy, HTML, CSS, and JavaScript. It is suitable for an MCA final-year project because it integrates web development, database management, biometric authentication, AI-based prediction, cybersecurity concepts, emergency response workflow, and healthcare record management into one practical application.

---

# TABLE OF CONTENTS

| Chapter No. | Title | Page No. |
| --- | --- | --- |
| Abstract | Abstract | i |
| Chapter 1 | Introduction | 1 |
| 1.1 | Background of the Project | 1 |
| 1.2 | Motivation | 2 |
| 1.3 | Problem Statement | 3 |
| 1.4 | Objectives of the Project | 4 |
| 1.5 | Scope of the Project | 5 |
| 1.6 | Significance of the Project | 6 |
| Chapter 2 | Requirement Analysis | 7 |
| 2.1 | Functional Requirements | 7 |
| 2.2 | Non-Functional Requirements | 11 |
| 2.3 | Hardware and Software Requirements | 13 |
| 2.4 | Feasibility Study | 14 |
| Chapter 3 | Software / Project Design | 16 |
| 3.1 | System Architecture | 16 |
| 3.2 | Module Design | 18 |
| 3.3 | Database Design | 23 |
| 3.4 | Data Flow Design | 26 |
| 3.5 | Security Design | 28 |
| Chapter 4 | Implementation and Testing | 30 |
| 4.1 | Implementation Overview | 30 |
| 4.2 | Patient Registration Implementation | 31 |
| 4.3 | Biometric Matching Implementation | 32 |
| 4.4 | AI Risk Prediction Implementation | 34 |
| 4.5 | Emergency Module Implementation | 36 |
| 4.6 | Family Alert Implementation | 38 |
| 4.7 | Integrity Chain Implementation | 39 |
| 4.8 | Testing Methodology | 41 |
| 4.9 | Result Summary | 43 |
| Chapter 5 | Conclusion and Future Scope | 45 |
| 5.1 | Conclusion | 45 |
| 5.2 | Achievements | 46 |
| 5.3 | Limitations | 47 |
| 5.4 | Future Scope | 48 |
| Appendix A | Important Code Snippets with Labels | 50 |

---

# CHAPTER 1: INTRODUCTION

## 1.1 Background of the Project

Hospitals and healthcare centers handle a large number of patients every day. For each patient, important information such as name, age, phone number, address, blood group, allergies, previous diagnosis, prescription, and emergency contact must be stored safely. Traditionally, hospitals retrieve this information using patient ID cards, registration numbers, mobile numbers, or manual search.

Although these methods are common, they are not always reliable. A patient may forget the registration number, lose the ID card, or provide incorrect contact information. In emergency cases, the situation becomes more serious because the patient may be unconscious or unable to communicate. In such cases, doctors may not know the patient's allergies, previous disease history, or blood group.

A biometric-based record retrieval system can solve this issue by identifying the patient through unique physical traits such as face and fingerprint. These traits are more reliable than manual identifiers because they are difficult to forget, lose, or duplicate. By connecting biometric identification with medical records, hospitals can retrieve patient data quickly and securely.

AegisCare extends this idea further by adding AI-based risk prediction, blockchain-style data integrity, smart dashboard, emergency scan, family alert, and ICU handover support.

## 1.2 Motivation

The motivation behind this project is the need for fast and reliable healthcare data access. In accident or ICU situations, a few seconds can be very important. If a doctor quickly knows that a patient is allergic to a medicine, has high cardiac risk, or has a specific blood group, treatment decisions can be safer and faster.

The project is also motivated by the growing use of digital healthcare systems. Modern hospitals require not only record storage but also intelligent decision support. Doctors need dashboards, alerts, risk scores, and quick access to patient history. Security is also important because medical records and biometric data are sensitive.

Therefore, this project combines multiple technologies to create a practical healthcare solution:

- Biometric authentication for identity verification.
- AI risk prediction for clinical decision support.
- Encrypted biometric storage for privacy.
- Blockchain-style integrity chain for tamper detection.
- Emergency scan for accident and ICU workflows.
- Family alert message logging for emergency communication.

## 1.3 Problem Statement

In many healthcare institutions, patient identification and record retrieval still depend on manual or semi-digital methods. These methods create several problems:

- Patient records may be difficult to retrieve quickly.
- Duplicate records may be created due to manual entry mistakes.
- Emergency cases may suffer because the patient cannot provide identity details.
- Allergy and blood group information may not be available at the time of treatment.
- Medical staff may not know the patient's latest risk condition.
- Sensitive biometric and medical data may not be protected properly.
- Important events may not be traceable.
- Family members may not be alerted quickly during emergency admission.

The problem addressed by this project is:

How can a hospital securely identify a patient using biometrics, retrieve critical medical information quickly, predict health risk, maintain data integrity, and support emergency communication from one integrated system?

## 1.4 Objectives of the Project

The main objectives of AegisCare are:

- To develop a web-based patient record management system.
- To provide role-based login for Admin, Doctor, Receptionist, and Patient Demo User.
- To register patients with personal details, medical details, photo, biometrics, and health vitals.
- To support face and fingerprint based biometric authentication.
- To encrypt biometric templates before storing them.
- To retrieve patient records using biometric matching.
- To calculate patient risk score using an AI-based risk engine.
- To generate priority alerts for high and critical risk patients.
- To provide a smart doctor dashboard.
- To provide an emergency scan module for accident and ICU cases.
- To show allergy, blood group, vitals, and latest diagnosis immediately after emergency scan.
- To provide a family emergency alert message workflow.
- To provide a printable ICU handover summary.
- To maintain a blockchain-style integrity chain for important events.

## 1.5 Scope of the Project

The scope of the project includes patient registration, biometric enrollment, biometric retrieval, medical record management, AI risk assessment, emergency scan, family alert logging, dashboard visualization, audit logging, and integrity verification.

The project is designed as an academic prototype. It uses uploaded face and fingerprint images instead of physical biometric hardware. This makes the project easy to demonstrate in college while still showing the actual biometric workflow.

The system can be used by:

- Receptionist for patient registration.
- Doctor for medical record and risk monitoring.
- Admin for audit and integrity checking.
- Emergency staff for quick patient identification.

## 1.6 Significance of the Project

This project is significant because it solves a real healthcare problem. It reduces patient identification delays and makes emergency care safer. It also demonstrates advanced MCA-level concepts such as image processing, AI prediction, secure storage, role-based access, data integrity, and dashboard design.

The emergency scan module is one of the most important parts of the project because it directly supports accident and ICU scenarios. If the patient is unconscious, staff can scan face or fingerprint and instantly view treatment-critical details.

---

# CHAPTER 2: REQUIREMENT ANALYSIS

## 2.1 Functional Requirements

Functional requirements describe the operations that the system must perform.

## 2.1.1 Login and Role Management

The system must provide a login page where users can enter username and password. After successful login, the system must store session information. Different roles must have different access permissions.

Roles used in the system:

- Admin
- Doctor
- Receptionist
- Patient Demo User

Admin can access audit logs and integrity chain. Doctor can access patient profiles, add records, add vitals, resolve alerts, and use emergency scan. Receptionist can register patients and use emergency scan. Patient demo user has limited access.

## 2.1.2 Patient Registration

The registration module must collect patient information:

- Full name
- Gender
- Date of birth
- Phone number
- Blood group
- Emergency contact
- Address
- Allergies
- Patient photo
- Face image
- Fingerprint image
- Baseline health vitals

After submission, the system must generate a unique patient code and save the record in the database.

## 2.1.3 Patient Photo Management

The system must allow uploading a patient profile photo during registration. The photo must be stored in a protected folder and displayed on the patient profile and emergency scan result page. This helps staff visually confirm the patient's identity.

## 2.1.4 Biometric Enrollment

The system must allow face image and fingerprint image enrollment. Face and fingerprint images are stored as encrypted files before storage.

## 2.1.5 Biometric Patient Retrieval

The system must provide a biometric retrieval page where staff can upload face image or fingerprint image. The system compares the uploaded input with stored templates and opens the matching patient profile if a valid match is found.

## 2.1.6 Medical Record Management

Doctors must be able to add medical records containing diagnosis, prescription, and doctor notes. Records must be displayed in descending order so that the latest record appears first.

## 2.1.7 Health Metrics Capture

The system must allow recording vitals:

- Systolic blood pressure
- Diastolic blood pressure
- Heart rate
- SpO2
- Glucose
- Temperature
- Respiratory rate
- Notes

These values are used by the AI risk engine.

## 2.1.8 AI Risk Prediction

The system must calculate a risk score and risk level using patient vitals and medical history. It must predict risk categories such as:

- Hypertension Risk
- Diabetes Risk
- Cardio Risk
- Respiratory Risk

The risk level can be low, moderate, high, or critical.

## 2.1.9 Smart Doctor Dashboard

The dashboard must show:

- Total patients
- Total medical records
- Total biometric templates
- Open risk alerts
- AI risk distribution
- Average risk trend
- Priority patients
- Recent activity
- Integrity chain status

## 2.1.10 Emergency Scan Module

The emergency scan module must support face or fingerprint based patient lookup. It must quickly display:

- Patient photo
- Patient name and code
- Allergies
- Blood group
- Emergency contact
- Phone number
- Latest vitals
- AI risk score
- Latest diagnosis
- Open alerts
- Family alert section
- ICU handover print button
- Emergency triage checklist

## 2.1.11 Family Alert Module

The emergency page must allow staff to send an alert message to the patient's family contact number. The message should be auto-generated but editable. Since no real SMS gateway is configured in the academic version, the system stores the alert with `sent-demo` status.

## 2.1.12 Integrity Chain Module

The system must create linked hash records for important events. This includes patient registration, biometric enrollment, medical record update, health metric capture, AI risk assessment, emergency lookup, family alert, and alert resolution.

## 2.2 Non-Functional Requirements

## 2.2.1 Security

The system must protect medical and biometric data. It uses password hashing, role-based access, encrypted biometric templates, protected patient photo route, audit logs, and integrity chain.

## 2.2.2 Usability

The interface must be simple and clear. Emergency data must be shown in a direct format so doctors do not waste time searching through many pages.

## 2.2.3 Performance

The system must respond quickly during patient lookup. SQLite and local file storage are used for fast academic demonstration.

## 2.2.4 Maintainability

The system is divided into separate files:

- `app.py`
- `biometric_engine.py`
- `ai_risk_engine.py`
- `integrity_chain.py`
- `templates/`
- `static/css/style.css`

This makes the project easier to understand and maintain.

## 2.2.5 Reliability

The system must handle missing images, missing vitals, missing emergency contact, and no-match biometric cases safely.

## 2.3 Hardware and Software Requirements

## 2.3.1 Hardware Requirements

- Laptop or desktop
- Minimum 4 GB RAM
- Minimum 1 GB free disk space
- Webcam or image upload support
- Sample fingerprint image for demonstration

## 2.3.2 Software Requirements

- Python
- Flask
- SQLite
- OpenCV
- NumPy
- HTML
- CSS
- JavaScript
- Web browser

## 2.4 Feasibility Study

## 2.4.1 Technical Feasibility

The project is technically feasible because it uses open-source and lightweight technologies. Flask is simple for web application development, SQLite does not require a separate server, and OpenCV supports image processing.

## 2.4.2 Operational Feasibility

The project is operationally feasible because hospital staff can use forms and buttons without technical knowledge. Emergency scan is designed for quick use.

## 2.4.3 Economic Feasibility

The project is economically feasible because it does not require paid infrastructure for demonstration. The SMS feature is implemented in demo mode and can later be connected to an SMS provider.

---

# CHAPTER 3: SOFTWARE / PROJECT DESIGN

## 3.1 System Architecture

The system follows a three-layer architecture:

## 3.1.1 Presentation Layer

This layer contains HTML templates and CSS. It displays pages such as login, dashboard, patient registration, biometric retrieval, emergency scan, patient profile, audit log, and integrity chain.

## 3.1.2 Application Layer

This layer is implemented using Python Flask. It handles routing, sessions, role checking, form submissions, biometric matching, AI risk calculation, emergency alert workflow, and integrity logging.

## 3.1.3 Data Layer

This layer uses SQLite. It stores users, patients, biometrics, medical records, vitals, AI risk assessments, emergency notifications, alerts, audit logs, and integrity blocks.

## 3.2 Module Design

## 3.2.1 Authentication Module

This module verifies username and password. Passwords are stored using hashing. After login, the user role is stored in session and used for access control.

## 3.2.2 Patient Registration Module

This module collects patient details, photo, face/fingerprint biometric files, and baseline vitals. It generates a patient code and stores all data in the database.

## 3.2.3 Biometric Engine Module

The biometric module handles:

- Face preprocessing
- Fingerprint preprocessing
- ORB feature extraction
- Histogram comparison
- Biometric encryption
- Biometric matching

## 3.2.4 AI Risk Engine Module

The AI module calculates disease-risk probabilities. It uses vitals and medical history indicators. It then generates a weighted risk score and clinical recommendation.

## 3.2.5 Dashboard Module

The dashboard module displays clinical overview. It helps doctors identify priority patients and monitor high-risk cases.

## 3.2.6 Emergency Scan Module

The emergency module is designed for accident and ICU workflow. It identifies the patient from face or fingerprint and displays only the most critical treatment details first.

## 3.2.7 Family Alert Module

This module creates an emergency message for family members. It extracts the family phone number, prepares a message, allows editing, stores the alert, and logs the action.

## 3.2.8 Integrity Chain Module

This module stores important events as hash-linked blocks. Each block depends on the previous block hash. If any record is modified, the chain verification can detect mismatch.

## 3.3 Database Design

Main database tables:

| Table Name | Purpose |
| --- | --- |
| `users` | Stores user login details and role |
| `patients` | Stores patient personal details, allergies, photo path, emergency contact |
| `biometrics` | Stores encrypted biometric file paths |
| `medical_records` | Stores diagnosis, prescription, and doctor notes |
| `health_metrics` | Stores patient vitals |
| `risk_assessments` | Stores AI risk output |
| `priority_alerts` | Stores high/critical alerts |
| `emergency_notifications` | Stores family alert message logs |
| `audit_logs` | Stores user actions |
| `integrity_chain` | Stores hash-linked event blocks |

## 3.4 Data Flow Design

## 3.4.1 Patient Registration Flow

1. Staff logs in.
2. Staff opens registration page.
3. Patient details, photo, biometrics, and vitals are entered.
4. System creates patient code.
5. Patient data is saved.
6. Biometric data is encrypted and stored.
7. AI risk assessment is generated.
8. Integrity event is added.

## 3.4.2 Biometric Retrieval Flow

1. Staff opens biometric retrieval page.
2. Staff uploads face or fingerprint image.
3. System decrypts stored templates.
4. Matching score is calculated.
5. If match is successful, patient profile opens.

## 3.4.3 Emergency Scan Flow

1. Staff opens emergency scan.
2. Face or fingerprint image is uploaded.
3. System matches biometric data.
4. Emergency snapshot is displayed.
5. Staff can send family alert.
6. Staff can print ICU handover.
7. Action is saved in audit and integrity logs.

## 3.5 Security Design

Security controls:

- Login authentication
- Role-based access
- Encrypted biometric templates
- Protected patient photo route
- Audit logs
- Integrity chain verification
- Form validation for uploads

---

# CHAPTER 4: IMPLEMENTATION AND TESTING

## 4.1 Implementation Overview

The system is implemented as a Flask web application. Flask routes connect frontend forms with backend logic. SQLite stores data. OpenCV handles image processing. The AI module calculates risk score. The emergency module supports ICU-related workflow.

## 4.2 Patient Registration Implementation

Patient registration is implemented in `/patients/register`. It collects patient information, validates required fields, saves patient photo, stores biometric samples, records vitals, creates AI risk assessment, and logs integrity events.

## 4.3 Biometric Matching Implementation

Face and fingerprint images are processed using OpenCV. The system uses grayscale conversion, histogram equalization, resizing, ORB feature detection, and histogram similarity to calculate biometric match scores.

## 4.4 AI Risk Prediction Implementation

The AI risk engine uses vitals such as BP, heart rate, SpO2, glucose, temperature, and respiratory rate. It calculates disease probabilities and weighted risk score. Risk level is categorized as low, moderate, high, or critical.

## 4.5 Emergency Module Implementation

The emergency scan module is implemented through `/emergency-scan`. It accepts face or fingerprint image. After successful matching, it loads emergency data such as allergy, blood group, latest vitals, risk score, latest diagnosis, and emergency contact.

## 4.6 Family Alert Implementation

The family alert module is implemented using `/patients/<patient_id>/family-alert/send`. It takes phone number and message from the emergency page. The message is saved with demo sent status. It is also logged in audit and integrity chain.

## 4.7 ICU Handover Implementation

The ICU handover tool uses a print button on the emergency page. The print stylesheet hides navigation and unnecessary controls, showing only emergency-critical patient information.

## 4.8 Integrity Chain Implementation

The integrity module creates linked blocks using SHA-256 hash. Each block stores:

- Block index
- Patient ID
- Event type
- Actor
- Payload hash
- Previous hash
- Current block hash
- Timestamp

## 4.9 Testing Methodology

Testing was performed using route checks and functional flow checks.

## 4.9.1 Test Cases

| Test Case ID | Scenario | Expected Result | Status |
| --- | --- | --- | --- |
| TC-01 | Login as doctor | Dashboard opens | Pass |
| TC-02 | Open registration page | Form displays | Pass |
| TC-03 | Register patient | Patient created | Pass |
| TC-04 | Upload patient photo | Photo visible on profile | Pass |
| TC-05 | Use biometric retrieval | Matching profile opens | Pass |
| TC-06 | Use emergency scan | Emergency snapshot opens | Pass |
| TC-07 | Send family alert | Alert history saved | Pass |
| TC-08 | Print ICU handover | Printable summary opens | Pass |
| TC-09 | Add vitals | Risk recalculated | Pass |
| TC-10 | Open integrity page | Chain status displayed | Pass |

## 4.10 Result Summary

The project successfully performs patient registration, biometric authentication, AI risk prediction, emergency scan, family alert logging, dashboard monitoring, and integrity verification. The emergency module improves the practical value of the system because it provides quick access to allergy and blood group details during critical treatment.

---

# CHAPTER 5: CONCLUSION AND FUTURE SCOPE

## 5.1 Conclusion

AegisCare is a complete healthcare record retrieval and emergency support system. It improves patient identification through face/fingerprint biometrics and helps doctors access records quickly. The AI risk engine adds intelligent decision support by calculating patient risk score and predicted risk categories.

The system also improves emergency workflow. If a patient is brought to the hospital after an accident, staff can scan face or fingerprint and immediately access allergies, blood group, latest vitals, and latest diagnosis. The family alert module and ICU handover print feature make the emergency module more useful in real hospital scenarios.

From an academic perspective, the project demonstrates web development, database design, image processing, biometric security, AI prediction, data integrity, and healthcare workflow automation.

## 5.2 Achievements

The project achieved:

- Role-based login
- Patient registration with photo
- Face and fingerprint biometric matching
- Encrypted biometric storage
- AI risk prediction
- Smart doctor dashboard
- Emergency scan module
- Family alert logging
- ICU handover print
- Blockchain-style integrity chain

## 5.3 Limitations

Current limitations:

- Real biometric hardware is not connected.
- SMS sending works in demo mode.
- AI model is academic and not clinically certified.
- SQLite is used for demo instead of enterprise database.
- Production deployment requires stronger security and compliance.

## 5.4 Future Scope

Future improvements:

- Real fingerprint scanner integration
- Real SMS API integration
- Doctor mobile app
- QR wristband support
- Cloud deployment
- PostgreSQL database migration
- Clinically trained machine learning model
- PDF export of reports
- Hospital ERP integration
- Advanced audit and compliance module

---

# APPENDIX A: IMPORTANT CODE SNIPPETS WITH LABELS

## Code A.1: Application Configuration

```python
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DB_PATH = INSTANCE_DIR / "patients.db"
KEY_PATH = INSTANCE_DIR / "biometric.key"
BIOMETRIC_DIR = INSTANCE_DIR / "encrypted_biometrics"
PHOTO_DIR = INSTANCE_DIR / "patient_photos"
```

Label: Defines important storage paths for the database, encrypted biometrics, and patient photos.

## Code A.2: Patient Photo Upload

```python
def save_patient_photo(upload, patient_id):
    if not upload or not upload.filename:
        return None
    filename = secure_filename(upload.filename)
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_PHOTO_EXTENSIONS:
        return None
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    destination = PHOTO_DIR / f"{patient_id}_{uuid4().hex}{extension}"
    upload.save(destination)
    return str(destination)
```

Label: Saves patient photo securely after validating file extension.

## Code A.3: Protected Patient Photo Route

```python
@app.route("/patients/<int:patient_id>/photo")
@login_required
def patient_photo(patient_id):
    if not can_view_patient(patient_id):
        abort(403)
    patient = get_db().execute(
        "SELECT profile_photo_path FROM patients WHERE id = ?",
        (patient_id,),
    ).fetchone()
    if not patient or not patient["profile_photo_path"]:
        abort(404)
    return send_file(Path(patient["profile_photo_path"]))
```

Label: Displays patient photo only to authorized users.

## Code A.4: Biometric Encryption

```python
def encrypt_and_save(upload, destination: Path, key_path: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = upload.read()
    encrypted = _encrypt_bytes(data, ensure_key(key_path))
    destination.write_bytes(encrypted)
```

Label: Encrypts biometric data before saving to disk.

## Code A.5: Biometric Matching Function

```python
def match_patient(face_image, fingerprint_image, biometric_rows, key_path):
    scores = {}
    for row in biometric_rows:
        if row["biometric_type"] not in {"face", "fingerprint"}:
            continue
        patient_id = row["patient_id"]
        scores.setdefault(patient_id, {
            "patient_id": patient_id,
            "patient_code": row["patient_code"],
            "full_name": row["full_name"],
            "face_score": None,
            "fingerprint_score": None,
            "combined_score": 0.0,
        })
```

Label: Starts biometric matching for face and fingerprint.

## Code A.6: AI Risk Prediction Inputs

```python
def predict_risk(patient_row, metric_row, recent_records):
    age = calculate_age(patient_row.get("date_of_birth"))
    systolic = _safe_float(metric_row.get("systolic_bp")) or 122.0
    diastolic = _safe_float(metric_row.get("diastolic_bp")) or 79.0
    heart_rate = _safe_float(metric_row.get("heart_rate")) or 78.0
    spo2 = _safe_float(metric_row.get("spo2")) or 97.0
    glucose = _safe_float(metric_row.get("glucose")) or 102.0
```

Label: Takes patient vitals and age as AI risk prediction inputs.

## Code A.7: Emergency Snapshot

```python
def fetch_emergency_snapshot(db, patient_id):
    patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    latest_metric = db.execute(
        "SELECT * FROM health_metrics WHERE patient_id = ? ORDER BY id DESC LIMIT 1",
        (patient_id,),
    ).fetchone()
    latest_record = db.execute(
        "SELECT * FROM medical_records WHERE patient_id = ? ORDER BY id DESC LIMIT 1",
        (patient_id,),
    ).fetchone()
```

Label: Collects critical emergency data after biometric match.

## Code A.8: Family Alert Message Builder

```python
def build_family_alert_message(patient, latest_risk=None):
    blood_group = patient["blood_group"] or "not recorded"
    allergies = patient["allergies"] or "no allergy recorded"
    risk_text = ""
    if latest_risk:
        risk_text = f" AI risk: {latest_risk['risk_level'].title()} ({latest_risk['risk_score']})."
    return (
        f"Emergency Alert: {patient['full_name']} ({patient['patient_code']}) has been identified "
        f"in hospital emergency. Blood group: {blood_group}. Allergies: {allergies}.{risk_text} "
        "Please contact the hospital immediately."
    )
```

Label: Generates an editable family emergency alert message.

## Code A.9: Integrity Chain Block

```python
def append_block(db, event_type, payload, actor="system", patient_id=None):
    payload_json = _canonical_json(payload or {})
    data_hash = _sha256(payload_json)
    previous = db.execute(
        "SELECT block_index, block_hash FROM integrity_chain ORDER BY block_index DESC LIMIT 1"
    ).fetchone()
```

Label: Creates tamper-evident block for important events.

## Code A.10: ICU Handover Print Button

```html
<section class="panel emergency-actions no-print">
  <div>
    <h2>ICU Handover Tools</h2>
    <p class="muted-line">Emergency summary print karke ICU team ko handover kar sakte hain.</p>
  </div>
  <button type="button" class="danger-button" onclick="window.print()">Print ICU Handover</button>
</section>
```

Label: Allows staff to print emergency summary for ICU handover.

---

# END OF REPORT
