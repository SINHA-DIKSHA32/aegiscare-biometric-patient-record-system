import sqlite3
import shutil
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEPS_DIR = BASE_DIR / ".deps"
if DEPS_DIR.exists():
    sys.path.insert(0, str(DEPS_DIR))

import cv2
import numpy as np

from app import BIOMETRIC_DIR, DB_PATH, KEY_PATH, PHOTO_DIR, create_risk_assessment, init_db, app
from biometric_engine import encrypt_and_save


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


def seed_patient():
    with app.app_context():
        init_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        patient = conn.execute("SELECT id FROM patients WHERE patient_code = ?", ("DEMO-001",)).fetchone()
        if patient:
            patient_id = patient["id"]
            print("Demo patient exists. Refreshing advanced demo artifacts.")
        else:
            cursor = conn.execute(
                """
                INSERT INTO patients
                (patient_code, full_name, gender, date_of_birth, phone, address, blood_group, allergies, emergency_contact, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    now(),
                ),
            )
            patient_id = cursor.lastrowid

        photo_path = PHOTO_DIR / f"{patient_id}_demo_profile.png"
        if not photo_path.exists():
            PHOTO_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(FACE_SAMPLE, photo_path)
        conn.execute(
            "UPDATE patients SET profile_photo_path = ? WHERE id = ?",
            (str(photo_path), patient_id),
        )

        for biometric_type, sample_path in [("face", FACE_SAMPLE), ("fingerprint", FINGERPRINT_SAMPLE)]:
            exists = conn.execute(
                "SELECT id FROM biometrics WHERE patient_id = ? AND biometric_type = ?",
                (patient_id, biometric_type),
            ).fetchone()
            if not exists:
                destination = BIOMETRIC_DIR / f"{patient_id}_{biometric_type}_demo.png.enc"
                encrypt_and_save(UploadBytes(sample_path), destination, KEY_PATH)
                conn.execute(
                    "INSERT INTO biometrics (patient_id, biometric_type, encrypted_path, created_at) VALUES (?, ?, ?, ?)",
                    (patient_id, biometric_type, str(destination), now()),
                )

        metrics_exists = conn.execute("SELECT id FROM health_metrics WHERE patient_id = ? LIMIT 1", (patient_id,)).fetchone()
        if not metrics_exists:
            conn.execute(
                """
                INSERT INTO health_metrics
                (patient_id, systolic_bp, diastolic_bp, heart_rate, spo2, glucose, temperature, respiratory_rate, notes, recorded_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (patient_id, 138, 88, 94, 95.8, 132, 99.2, 21, "Demo baseline vitals", "doctor", now()),
            )

        record_exists = conn.execute("SELECT id FROM medical_records WHERE patient_id = ? LIMIT 1", (patient_id,)).fetchone()
        if not record_exists:
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
        conn.commit()
        risk_exists = conn.execute("SELECT id FROM risk_assessments WHERE patient_id = ? LIMIT 1", (patient_id,)).fetchone()
        if not risk_exists:
            patient_row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
            create_risk_assessment(conn, patient_row, patient_id, "doctor")
            conn.commit()
        conn.close()
        print("Demo patient ready: DEMO-001 Aarav Sharma")
        print(f"Face sample: {FACE_SAMPLE}")
        print(f"Fingerprint sample: {FINGERPRINT_SAMPLE}")


if __name__ == "__main__":
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    create_demo_face()
    create_demo_fingerprint()
    seed_patient()
