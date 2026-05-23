import sqlite3
import sys
import json
from datetime import datetime
from io import BytesIO
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEPS_DIR = BASE_DIR / ".deps"
if DEPS_DIR.exists():
    sys.path.insert(0, str(DEPS_DIR))

import cv2
import numpy as np

from app import BIOMETRIC_DIR, DB_PATH, KEY_PATH, init_db, app
from biometric_engine import encrypt_and_save
from clinical_ai import analyze_patient_risk


DEMO_DIR = BASE_DIR / "demo_samples"
FACE_SAMPLE = DEMO_DIR / "demo_face.png"
FINGERPRINT_SAMPLE = DEMO_DIR / "demo_fingerprint.png"


class UploadBytes:
    def __init__(self, path: Path):
        self.path = path
        self.filename = path.name

    def read(self):
        return self.path.read_bytes()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_demo_face():
    image = np.full((360, 360, 3), 235, dtype=np.uint8)
    cv2.circle(image, (180, 175), 105, (188, 212, 229), -1)
    cv2.circle(image, (140, 150), 16, (35, 55, 75), -1)
    cv2.circle(image, (220, 150), 16, (35, 55, 75), -1)
    cv2.ellipse(image, (180, 205), (42, 18), 0, 0, 180, (35, 55, 75), 4)
    cv2.line(image, (180, 158), (166, 198), (50, 80, 95), 4)
    cv2.ellipse(image, (180, 92), (94, 52), 0, 180, 360, (33, 67, 92), -1)
    cv2.putText(image, "DEMO FACE", (78, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (15, 118, 110), 2)
    cv2.imwrite(str(FACE_SAMPLE), image)


def create_demo_fingerprint():
    image = np.full((420, 420, 3), 245, dtype=np.uint8)
    center = (210, 210)
    for radius in range(36, 178, 16):
        cv2.ellipse(image, center, (radius, int(radius * 1.24)), -8, 12, 342, (45, 76, 92), 3)
    for offset in range(-120, 130, 32):
        cv2.line(image, (88, 210 + offset), (332, 130 + offset // 2), (70, 96, 110), 2)
    cv2.putText(image, "DEMO FINGER", (75, 390), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (15, 118, 110), 2)
    cv2.imwrite(str(FINGERPRINT_SAMPLE), image)


def ensure_demo_vitals(conn, patient_id):
    exists = conn.execute("SELECT id FROM vitals WHERE patient_id = ?", (patient_id,)).fetchone()
    if exists:
        return

    patient = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    latest_record = conn.execute(
        "SELECT * FROM medical_records WHERE patient_id = ? ORDER BY id DESC LIMIT 1", (patient_id,)
    ).fetchone()
    vitals = {
        "systolic_bp": 148,
        "diastolic_bp": 92,
        "pulse_rate": 96,
        "temperature_c": 38.2,
        "spo2": 97,
        "fasting_glucose": 132,
        "random_glucose": 0,
        "bmi": 26.4,
        "symptoms": "fever, weakness, high BP reading",
    }
    analysis = analyze_patient_risk(dict(patient), dict(latest_record) if latest_record else None, vitals)
    conn.execute(
        """
        INSERT INTO vitals
        (patient_id, systolic_bp, diastolic_bp, pulse_rate, temperature_c, spo2, fasting_glucose, random_glucose, bmi,
         symptoms, ai_risk_score, ai_risk_level, ai_summary, ai_findings, disease_predictions, ai_recommendations,
         recorded_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            patient_id,
            vitals["systolic_bp"],
            vitals["diastolic_bp"],
            vitals["pulse_rate"],
            vitals["temperature_c"],
            vitals["spo2"],
            vitals["fasting_glucose"],
            vitals["random_glucose"],
            vitals["bmi"],
            vitals["symptoms"],
            analysis["risk_score"],
            analysis["risk_level"],
            analysis["summary"],
            json.dumps(analysis["findings"]),
            json.dumps(analysis["predictions"]),
            json.dumps(analysis["recommendations"]),
            "doctor",
            now(),
        ),
    )


def seed_patient():
    with app.app_context():
        init_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        patient = conn.execute("SELECT id FROM patients WHERE patient_code = ?", ("DEMO-001",)).fetchone()
        if patient:
            ensure_demo_vitals(conn, patient["id"])
            conn.commit()
            conn.close()
            print("Demo patient already exists.")
            return

        cursor = conn.execute(
            """
            INSERT INTO patients
            (patient_code, full_name, gender, date_of_birth, phone, address, blood_group, allergies, emergency_contact,
             height_cm, weight_kg, chronic_conditions, insurance_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "DEMO-001",
                "Aarav Sharma",
                "Male",
                "2001-08-12",
                "9876543210",
                "Demo Colony, Bhopal",
                "B+",
                "No known allergies",
                "Riya Sharma - 9876500000",
                172,
                78,
                "Borderline BP, family history of diabetes",
                "ABHA-DEMO-001",
                now(),
            ),
        )
        patient_id = cursor.lastrowid

        for biometric_type, sample_path in [("face", FACE_SAMPLE), ("fingerprint", FINGERPRINT_SAMPLE)]:
            destination = BIOMETRIC_DIR / f"{patient_id}_{biometric_type}_demo.png.enc"
            encrypt_and_save(UploadBytes(sample_path), destination, KEY_PATH)
            conn.execute(
                "INSERT INTO biometrics (patient_id, biometric_type, encrypted_path, created_at) VALUES (?, ?, ?, ?)",
                (patient_id, biometric_type, str(destination), now()),
            )

        conn.execute(
            """
            INSERT INTO medical_records (patient_id, diagnosis, prescription, doctor_notes, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                "Seasonal fever",
                "Paracetamol 500mg twice daily for 3 days",
                "Drink water, rest, and revisit if fever continues.",
                "doctor",
                now(),
            ),
        )
        ensure_demo_vitals(conn, patient_id)
        conn.commit()
        conn.close()
        print("Demo patient created: DEMO-001 Aarav Sharma")
        print(f"Face sample: {FACE_SAMPLE}")
        print(f"Fingerprint sample: {FINGERPRINT_SAMPLE}")


if __name__ == "__main__":
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    create_demo_face()
    create_demo_fingerprint()
    seed_patient()
