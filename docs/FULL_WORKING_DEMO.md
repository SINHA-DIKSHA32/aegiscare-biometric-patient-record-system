# Full Working Demo Guide

## Access URL

Open this URL in your browser:

```text
http://127.0.0.1:5000
```

If it does not open, run:

```text
start_server.cmd
```

## Demo Login

Use any of these accounts:

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| Doctor | `doctor` | `doctor123` |
| Receptionist | `reception` | `reception123` |
| Patient | `patient` | `patient123` |

Recommended demo login:

```text
doctor / doctor123
```

## Ready-Made Demo Patient

The demo seed creates this patient:

```text
Patient Code: DEMO-001
Name: Aarav Sharma
Diagnosis: Seasonal fever
Prescription: Paracetamol 500mg twice daily for 3 days
```

Sample biometric files:

```text
demo_samples/demo_face.png
demo_samples/demo_fingerprint.png
```

## Working Flow 1: Multimodal Biometric Retrieval

1. Login as `doctor`.
2. Open **Biometric Retrieval** from the sidebar.
3. Keep authentication mode as **Multimodal: Face + Fingerprint**.
4. In **Face Image**, upload:

```text
demo_samples/demo_face.png
```

5. In **Fingerprint Image**, upload:

```text
demo_samples/demo_fingerprint.png
```

6. Click **Find Patient Record**.
7. Expected result: the system opens `DEMO-001 Aarav Sharma`.
8. You should see patient details, enrolled biometrics, AI risk panel, vitals history, and medical history.

## Working Flow 2: AI Disease-Risk Prediction

1. Open the demo patient profile.
2. Fill **Add Vitals and Generate AI Risk**:

```text
BP: 160/96
Pulse: 104
Temperature: 37.8
SpO2: 96
Fasting Glucose: 145
BMI: 27
Symptoms: chest pain and dizziness
```

3. Click **Generate AI Risk**.
4. Expected result: the AI panel shows risk score, risk level, predicted focus areas, findings, and recommended action.

## Working Flow 3: Blockchain Audit Ledger

1. Login as `admin`.
2. Open **Blockchain Ledger**.
3. Show total blocks, latest hash prefix, and **Chain Verified** status.
4. Explain that each login, biometric match, AI risk check, FHIR export, and clinical action is linked with the previous hash.

## Working Flow 4: Interoperability Export

1. Open any patient profile.
2. Click **FHIR JSON**.
3. Expected result: browser returns a FHIR-like JSON bundle with patient, observation, and condition data.

## Working Flow 5: New Patient Registration

1. Login as `admin` or `reception`.
2. Open **Register Patient**.
3. Fill patient details:

```text
Full Name, Gender, DOB, Phone, Blood Group, Emergency Contact, Address, Allergies
```

4. Upload one face image and one fingerprint image.
5. Click **Register Patient**.
6. Expected result: new patient profile opens and biometric samples are enrolled.

## Working Flow 6: No-Match Case

1. Open **Biometric Retrieval**.
2. Upload any unrelated image.
3. Click **Find Patient Record**.
4. Expected result: system shows no matching patient and suggests new registration.

## Working Flow 7: Add Medical Record

1. Login as `doctor` or `admin`.
2. Open any patient record.
3. Fill **Diagnosis**, **Prescription**, and **Doctor Notes**.
4. Click **Save Record**.
5. Expected result: new medical entry appears in patient history.

## Working Flow 8: Audit Log

1. Login as `admin`.
2. Open **Audit Log**.
3. You can see login, registration, match, no-match, and medical record actions.

## Viva Explanation

This project retrieves patient records using biometric identity. During registration, patient details and biometric images are stored. The biometric images are encrypted before saving. During retrieval, the uploaded biometric is processed by OpenCV and compared with stored encrypted biometric samples after internal decryption. If the match score crosses the threshold, the patient record opens. If it fails, the system suggests new registration.

The upgraded version adds three examiner-friendly layers: an explainable AI health-risk engine, a blockchain-style ledger for tamper-evident audit history, and FHIR-like JSON interoperability. This makes the project look like a final-year healthcare platform rather than a normal patient CRUD application.
