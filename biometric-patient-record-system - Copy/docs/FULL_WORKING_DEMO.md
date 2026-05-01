# Full Working Demo Guide

## Access URL

Open this URL in your browser:

```text

``` http://127.0.0.1:5000

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

## Working Flow 1: Biometric Retrieval

1. Login as `doctor`.
2. Open **Biometric Retrieval** from the sidebar.
3. In **Face Image**, upload:

```text
demo_samples/demo_face.png
```

4. In **Fingerprint Image**, upload:

```text
demo_samples/demo_fingerprint.png
```

5. Click **Find Patient Record**.
6. Expected result: the system opens `DEMO-001 Aarav Sharma`.
7. You should see patient details, enrolled biometrics, and medical history.

## Working Flow 2: New Patient Registration

1. Login as `admin` or `reception`.
2. Open **Register Patient**.
3. Fill patient details:

```text
Full Name, Gender, DOB, Phone, Blood Group, Emergency Contact, Address, Allergies
```

4. Upload one face image and one fingerprint image.
5. Click **Register Patient**.
6. Expected result: new patient profile opens and biometric samples are enrolled.

## Working Flow 3: No-Match Case

1. Open **Biometric Retrieval**.
2. Upload any unrelated image.
3. Click **Find Patient Record**.
4. Expected result: system shows no matching patient and suggests new registration.

## Working Flow 4: Add Medical Record

1. Login as `doctor` or `admin`.
2. Open any patient record.
3. Fill **Diagnosis**, **Prescription**, and **Doctor Notes**.
4. Click **Save Record**.
5. Expected result: new medical entry appears in patient history.

## Working Flow 5: Audit Log

1. Login as `admin`.
2. Open **Audit Log**.
3. You can see login, registration, match, no-match, and medical record actions.

## Viva Explanation

This project retrieves patient records using biometric identity. During registration, patient details and biometric images are stored. The biometric images are encrypted before saving. During retrieval, the uploaded biometric is processed by OpenCV and compared with stored encrypted biometric samples after internal decryption. If the match score crosses the threshold, the patient record opens. If it fails, the system suggests new registration.
