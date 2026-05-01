# Appendix A: Important Source Code

## Project Title

AegisCare: Advanced Biometric Patient Record Retrieval System with AI Risk Prediction

## Note for Project Report

This appendix contains the most important code snippets from the project. These snippets can be attached with the final project report as the "Important Code" section. The selected code covers database design, role-based access, patient registration, biometric encryption, face/fingerprint matching, AI risk prediction, emergency scan, family alert, dashboard analytics, and blockchain-style data integrity.

---

## Code A.1: Application Configuration and Core Paths

**Source File:** `app.py`

**Purpose:** This code initializes project paths, database location, biometric storage folder, patient photo folder, and Flask application settings.

```python
import json
import re
import sqlite3
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parent
DEPS_DIR = BASE_DIR / ".deps"
if DEPS_DIR.exists():
    sys.path.insert(0, str(DEPS_DIR))

from flask import Flask, abort, flash, g, has_request_context, redirect
from flask import render_template, request, send_file, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from ai_risk_engine import predict_risk
from biometric_engine import encrypt_and_save, match_patient, read_upload_image
from integrity_chain import append_block, verify_chain

INSTANCE_DIR = BASE_DIR / "instance"
DB_PATH = INSTANCE_DIR / "patients.db"
KEY_PATH = INSTANCE_DIR / "biometric.key"
BIOMETRIC_DIR = INSTANCE_DIR / "encrypted_biometrics"
PHOTO_DIR = INSTANCE_DIR / "patient_photos"
ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-for-production"
STAFF_ROLES = ("admin", "doctor", "receptionist")
```

---

## Code A.2: Database Connection and Utility Functions

**Source File:** `app.py`

**Purpose:** This code creates a reusable SQLite connection for each request and provides common conversion helpers.

```python
def get_db():
    if "db" not in g:
        INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_int(value):
    try:
        return int(value) if value not in (None, "") else None
    except ValueError:
        return None


def parse_float(value):
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None
```

---

## Code A.3: Main Database Schema

**Source File:** `app.py`

**Purpose:** This code creates the major tables used in the project, including patients, biometrics, health metrics, risk assessments, alerts, emergency notifications, audit logs, and integrity chain.

```python
def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_code TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            gender TEXT,
            date_of_birth TEXT,
            phone TEXT,
            address TEXT,
            blood_group TEXT,
            allergies TEXT,
            emergency_contact TEXT,
            profile_photo_path TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS biometrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            biometric_type TEXT NOT NULL,
            encrypted_path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS health_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            systolic_bp INTEGER,
            diastolic_bp INTEGER,
            heart_rate INTEGER,
            spo2 REAL,
            glucose REAL,
            temperature REAL,
            respiratory_rate INTEGER,
            notes TEXT,
            recorded_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS risk_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            model_version TEXT NOT NULL,
            risk_score REAL NOT NULL,
            risk_level TEXT NOT NULL,
            predicted_diseases TEXT,
            probabilities_json TEXT,
            factors_json TEXT,
            recommendation TEXT,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS priority_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            risk_assessment_id INTEGER,
            title TEXT NOT NULL,
            details TEXT,
            severity TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TEXT NOT NULL,
            resolved_at TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(risk_assessment_id) REFERENCES risk_assessments(id)
        );

        CREATE TABLE IF NOT EXISTS emergency_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            recipient_phone TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            sent_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS integrity_chain (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_index INTEGER NOT NULL,
            patient_id INTEGER,
            event_type TEXT NOT NULL,
            actor TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            data_hash TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            block_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
```

---

## Code A.4: Login, Session, and Role-Based Access Control

**Source File:** `app.py`

**Purpose:** This code protects sensitive healthcare pages and allows access according to user roles.

```python
def current_user():
    if "user_id" not in session:
        return None
    return {
        "id": session["user_id"],
        "username": session["username"],
        "role": session["role"],
        "full_name": session["full_name"],
    }


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first.", "warning")
                return redirect(url_for("login"))
            if session["role"] not in roles:
                flash("You do not have permission for this page.", "danger")
                return redirect(url_for("dashboard"))
            return view(*args, **kwargs)

        return wrapped

    return decorator


def can_view_patient(patient_id):
    if session.get("role") in STAFF_ROLES:
        return True
    return session.get("verified_patient_id") == patient_id
```

---

## Code A.5: Patient Photo Upload and Protected Photo Access

**Source File:** `app.py`

**Purpose:** This code stores patient photos securely and serves them only to authorized users.

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

    photo_path = Path(patient["profile_photo_path"]).resolve()
    photo_root = PHOTO_DIR.resolve()
    if photo_root not in photo_path.parents or not photo_path.exists():
        abort(404)

    return send_file(photo_path)
```

---

## Code A.6: Patient Registration with Photo, Biometrics, Vitals, and AI Baseline

**Source File:** `app.py`

**Purpose:** This is one of the most important routes. It registers a patient, saves photo, encrypts face/fingerprint biometrics, stores baseline vitals, creates AI risk profile, and writes integrity events.

```python
@app.route("/patients/register", methods=["GET", "POST"])
@roles_required("admin", "doctor", "receptionist")
def register_patient():
    if request.method == "POST":
        db = get_db()
        patient_code = f"PAT-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}"
        values = {
            "patient_code": patient_code,
            "full_name": request.form.get("full_name", "").strip(),
            "gender": request.form.get("gender", "").strip(),
            "date_of_birth": request.form.get("date_of_birth", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "address": request.form.get("address", "").strip(),
            "blood_group": request.form.get("blood_group", "").strip(),
            "allergies": request.form.get("allergies", "").strip(),
            "emergency_contact": request.form.get("emergency_contact", "").strip(),
        }
        if not values["full_name"]:
            flash("Patient name is required.", "danger")
            return render_template("register_patient.html")

        cursor = db.execute(
            """
            INSERT INTO patients
            (patient_code, full_name, gender, date_of_birth, phone, address,
             blood_group, allergies, emergency_contact, profile_photo_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                values["patient_code"],
                values["full_name"],
                values["gender"],
                values["date_of_birth"],
                values["phone"],
                values["address"],
                values["blood_group"],
                values["allergies"],
                values["emergency_contact"],
                None,
                now(),
            ),
        )
        patient_id = cursor.lastrowid

        photo_upload = request.files.get("patient_photo")
        photo_path = save_patient_photo(photo_upload, patient_id)
        if photo_path:
            db.execute(
                "UPDATE patients SET profile_photo_path = ? WHERE id = ?",
                (photo_path, patient_id),
            )

        add_integrity_event(
            db,
            "PATIENT_REGISTERED",
            {
                "patient_code": patient_code,
                "full_name": values["full_name"],
                "phone": values["phone"],
                "has_profile_photo": bool(photo_path),
            },
            patient_id=patient_id,
        )

        for biometric_type, field in [("face", "face_image"), ("fingerprint", "fingerprint_image")]:
            upload = request.files.get(field)
            if upload and upload.filename:
                filename = secure_filename(upload.filename)
                extension = Path(filename).suffix or ".jpg"
                destination = BIOMETRIC_DIR / f"{patient_id}_{biometric_type}_{uuid4().hex}{extension}.enc"
                encrypt_and_save(upload, destination, KEY_PATH)
                db.execute(
                    "INSERT INTO biometrics (patient_id, biometric_type, encrypted_path, created_at) VALUES (?, ?, ?, ?)",
                    (patient_id, biometric_type, str(destination), now()),
                )
                add_integrity_event(
                    db,
                    "BIOMETRIC_ENROLLED",
                    {"biometric_type": biometric_type, "storage_path": str(destination)},
                    patient_id=patient_id,
                )

        metric_payload = {
            "systolic_bp": parse_int(request.form.get("systolic_bp")),
            "diastolic_bp": parse_int(request.form.get("diastolic_bp")),
            "heart_rate": parse_int(request.form.get("heart_rate")),
            "spo2": parse_float(request.form.get("spo2")),
            "glucose": parse_float(request.form.get("glucose")),
            "temperature": parse_float(request.form.get("temperature")),
            "respiratory_rate": parse_int(request.form.get("respiratory_rate")),
            "notes": request.form.get("metric_notes", "").strip(),
        }

        patient_row = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
        create_risk_assessment(db, patient_row, patient_id, session["username"])
        db.commit()

        log_action("PATIENT_REGISTERED", f"{patient_code} - {values['full_name']}")
        flash("Patient registered. AI baseline risk profile generated.", "success")
        return redirect(url_for("patient_detail", patient_id=patient_id))

    return render_template("register_patient.html")
```

---

## Code A.7: Biometric Encryption and Decryption

**Source File:** `biometric_engine.py`

**Purpose:** This code encrypts biometric image files before storage and decrypts them only during matching.

```python
FACE_THRESHOLD = 0.58
FINGERPRINT_THRESHOLD = 0.42
ENCRYPTION_MAGIC = b"BMR1"


def ensure_key(key_path: Path) -> bytes:
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        return key_path.read_bytes()
    key = secrets.token_bytes(32)
    key_path.write_bytes(key)
    return key


def _xor_with_key_stream(data: bytes, key: bytes, nonce: bytes) -> bytes:
    stream = bytearray()
    counter = 0
    while len(stream) < len(data):
        stream.extend(hashlib.sha256(key + nonce + counter.to_bytes(8, "big")).digest())
        counter += 1
    return bytes(value ^ stream[index] for index, value in enumerate(data))


def _encrypt_bytes(data: bytes, key: bytes) -> bytes:
    nonce = secrets.token_bytes(16)
    cipher_text = _xor_with_key_stream(data, key, nonce)
    tag = hmac.new(key, nonce + cipher_text, hashlib.sha256).digest()
    return ENCRYPTION_MAGIC + nonce + tag + cipher_text


def _decrypt_bytes(payload: bytes, key: bytes):
    if not payload.startswith(ENCRYPTION_MAGIC):
        return None
    nonce_start = len(ENCRYPTION_MAGIC)
    tag_start = nonce_start + 16
    cipher_start = tag_start + 32
    nonce = payload[nonce_start:tag_start]
    tag = payload[tag_start:cipher_start]
    cipher_text = payload[cipher_start:]
    expected = hmac.new(key, nonce + cipher_text, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected):
        return None
    return _xor_with_key_stream(cipher_text, key, nonce)


def encrypt_and_save(upload, destination: Path, key_path: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = upload.read()
    encrypted = _encrypt_bytes(data, ensure_key(key_path))
    destination.write_bytes(encrypted)


def decrypt_image(encrypted_path: Path, key_path: Path):
    try:
        decrypted = _decrypt_bytes(encrypted_path.read_bytes(), ensure_key(key_path))
    except FileNotFoundError:
        return None
    if decrypted is None:
        return None
    return decode_image(decrypted)
```

---

## Code A.8: Face and Fingerprint Image Processing

**Source File:** `biometric_engine.py`

**Purpose:** This code preprocesses face and fingerprint images and calculates feature-based similarity scores using OpenCV.

```python
def decode_image(data: bytes):
    array = np.frombuffer(data, dtype=np.uint8)
    return cv2.imdecode(array, cv2.IMREAD_COLOR)


def read_upload_image(upload):
    if not upload or upload.filename == "":
        return None
    data = upload.read()
    upload.stream.seek(0)
    return decode_image(data)


def _gray(image):
    if image is None:
        return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)


def _face_roi(image):
    gray = _gray(image)
    if gray is None:
        return None

    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    if cascade_path.exists():
        cascade = cv2.CascadeClassifier(str(cascade_path))
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(70, 70))
        if len(faces) > 0:
            x, y, w, h = sorted(faces, key=lambda item: item[2] * item[3], reverse=True)[0]
            gray = gray[y : y + h, x : x + w]

    return cv2.resize(gray, (180, 180), interpolation=cv2.INTER_AREA)


def _fingerprint_image(image):
    gray = _gray(image)
    if gray is None:
        return None
    gray = cv2.resize(gray, (320, 320), interpolation=cv2.INTER_AREA)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    return gray


def _orb_score(first, second) -> float:
    if first is None or second is None:
        return 0.0

    orb = cv2.ORB_create(nfeatures=900)
    keypoints_one, descriptors_one = orb.detectAndCompute(first, None)
    keypoints_two, descriptors_two = orb.detectAndCompute(second, None)

    if descriptors_one is None or descriptors_two is None:
        return 0.0
    if len(keypoints_one) < 6 or len(keypoints_two) < 6:
        return 0.0

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    pairs = matcher.knnMatch(descriptors_one, descriptors_two, k=2)
    good = []
    for pair in pairs:
        if len(pair) == 2:
            best, second_best = pair
            if best.distance < 0.75 * second_best.distance:
                good.append(best)

    return min(1.0, len(good) / max(12, min(len(keypoints_one), len(keypoints_two)) * 0.16))
```

---

## Code A.9: Face/Fingerprint Comparison and Patient Matching

**Source File:** `biometric_engine.py`

**Purpose:** This code calculates similarity scores for face and fingerprint and returns the best matching patient.

```python
def _histogram_score(first, second) -> float:
    if first is None or second is None:
        return 0.0
    hist_one = cv2.calcHist([first], [0], None, [64], [0, 256])
    hist_two = cv2.calcHist([second], [0], None, [64], [0, 256])
    cv2.normalize(hist_one, hist_one)
    cv2.normalize(hist_two, hist_two)
    score = cv2.compareHist(hist_one, hist_two, cv2.HISTCMP_CORREL)
    return float(max(0.0, min(1.0, score)))


def compare_face(uploaded_image, stored_image) -> float:
    uploaded = _face_roi(uploaded_image)
    stored = _face_roi(stored_image)
    hist = _histogram_score(uploaded, stored)
    orb = _orb_score(uploaded, stored)
    return round((hist * 0.65) + (orb * 0.35), 4)


def compare_fingerprint(uploaded_image, stored_image) -> float:
    uploaded = _fingerprint_image(uploaded_image)
    stored = _fingerprint_image(stored_image)
    return round((_orb_score(uploaded, stored) * 0.85) + (_histogram_score(uploaded, stored) * 0.15), 4)


def match_patient(face_image, fingerprint_image, biometric_rows: Iterable[dict], key_path: Path):
    scores = {}

    for row in biometric_rows:
        biometric_type = row["biometric_type"]
        if biometric_type == "face" and face_image is None:
            continue
        if biometric_type == "fingerprint" and fingerprint_image is None:
            continue
        if biometric_type not in {"face", "fingerprint"}:
            continue

        patient_id = row["patient_id"]
        scores.setdefault(
            patient_id,
            {
                "patient_id": patient_id,
                "patient_code": row["patient_code"],
                "full_name": row["full_name"],
                "face_score": None,
                "fingerprint_score": None,
                "combined_score": 0.0,
            },
        )

        encrypted_path = Path(row["encrypted_path"])

        if biometric_type == "face" and face_image is not None:
            stored_image = decrypt_image(encrypted_path, key_path)
            if stored_image is None:
                continue
            face_score = compare_face(face_image, stored_image)
            scores[patient_id]["face_score"] = max(scores[patient_id]["face_score"] or 0, face_score)

        if biometric_type == "fingerprint" and fingerprint_image is not None:
            stored_image = decrypt_image(encrypted_path, key_path)
            if stored_image is None:
                continue
            fingerprint_score = compare_fingerprint(fingerprint_image, stored_image)
            scores[patient_id]["fingerprint_score"] = max(
                scores[patient_id]["fingerprint_score"] or 0, fingerprint_score
            )

    for candidate in scores.values():
        present_scores = []
        if face_image is not None and candidate["face_score"] is not None:
            present_scores.append(candidate["face_score"])
        if fingerprint_image is not None and candidate["fingerprint_score"] is not None:
            present_scores.append(candidate["fingerprint_score"])
        if present_scores:
            candidate["combined_score"] = round(sum(present_scores) / len(present_scores), 4)

    candidates = sorted(scores.values(), key=lambda item: item["combined_score"], reverse=True)
    if not candidates:
        return None, []

    best = candidates[0]
    face_ok = face_image is None or (best["face_score"] is not None and best["face_score"] >= FACE_THRESHOLD)
    fingerprint_ok = fingerprint_image is None or (
        best["fingerprint_score"] is not None and best["fingerprint_score"] >= FINGERPRINT_THRESHOLD
    )

    if best["combined_score"] > 0 and face_ok and fingerprint_ok:
        return best, candidates[:5]

    return None, candidates[:5]
```

---

## Code A.10: Biometric Patient Retrieval Route

**Source File:** `app.py`

**Purpose:** This route accepts face or fingerprint input, compares it with stored encrypted biometric templates, and opens the matching patient record.

```python
@app.route("/identify", methods=["GET", "POST"])
@login_required
def identify():
    match = None
    candidates = []
    if request.method == "POST":
        face_upload = request.files.get("face_image")
        fingerprint_upload = request.files.get("fingerprint_image")
        face_image = read_upload_image(face_upload)
        fingerprint_image = read_upload_image(fingerprint_upload)

        if face_image is None and fingerprint_image is None:
            flash("Upload a face image or fingerprint image.", "warning")
            return render_template("identify.html", match=match, candidates=candidates)

        rows = get_db().execute(
            """
            SELECT b.patient_id, b.biometric_type, b.encrypted_path, p.full_name, p.patient_code
            FROM biometrics b
            JOIN patients p ON p.id = b.patient_id
            WHERE b.biometric_type IN ('face', 'fingerprint')
            ORDER BY b.id DESC
            """
        ).fetchall()
        rows = [dict(row) for row in rows]
        match, candidates = match_patient(face_image, fingerprint_image, rows, KEY_PATH)

        if match:
            session["verified_patient_id"] = match["patient_id"]
            add_integrity_event(
                get_db(),
                "BIOMETRIC_MATCH",
                {
                    "patient_code": match["patient_code"],
                    "combined_score": match["combined_score"],
                    "face_score": match["face_score"],
                    "fingerprint_score": match["fingerprint_score"],
                },
                patient_id=match["patient_id"],
            )
            get_db().commit()
            log_action("BIOMETRIC_MATCH", f"{match['patient_code']} score={match['combined_score']}")
            flash("Biometric match found. Patient record opened.", "success")
            return redirect(url_for("patient_detail", patient_id=match["patient_id"]))

        log_action("BIOMETRIC_NO_MATCH", "No registered patient matched")
        flash("No matching patient found. Please register as a new patient.", "warning")

    return render_template("identify.html", match=match, candidates=candidates)
```

---

## Code A.11: AI Risk Prediction Engine

**Source File:** `ai_risk_engine.py`

**Purpose:** This code calculates disease-risk probabilities and assigns a patient risk level using vitals and medical history.

```python
MODEL_VERSION = "AegisCare-Risk-v2"


def _risk_level(score):
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 35:
        return "moderate"
    return "low"


def predict_risk(patient_row, metric_row, recent_records):
    age = calculate_age(patient_row.get("date_of_birth"))
    age_factor = ((age or 35) - 35) / 25

    systolic = _safe_float(metric_row.get("systolic_bp")) or 122.0
    diastolic = _safe_float(metric_row.get("diastolic_bp")) or 79.0
    heart_rate = _safe_float(metric_row.get("heart_rate")) or 78.0
    spo2 = _safe_float(metric_row.get("spo2")) or 97.0
    glucose = _safe_float(metric_row.get("glucose")) or 102.0
    temperature = _safe_float(metric_row.get("temperature")) or 98.4
    respiratory_rate = _safe_float(metric_row.get("respiratory_rate")) or 17.0

    history = _history_keywords(recent_records)
    known_diabetes = "diabet" in history
    known_hypertension = "hypertens" in history or "bp" in history
    known_cardiac = "cardiac" in history or "chest pain" in history or "arrhythmia" in history
    known_respiratory = "asthma" in history or "copd" in history or "respirat" in history

    hypertension = _sigmoid(((systolic - 125) / 10) + ((diastolic - 82) / 8) + (0.5 * age_factor))
    diabetes = _sigmoid(((glucose - 108) / 13) + (0.4 * age_factor))
    cardio = _sigmoid(((heart_rate - 84) / 12) + ((systolic - 130) / 16) + (0.8 * age_factor))
    respiratory = _sigmoid(((95 - spo2) / 1.5) + ((respiratory_rate - 18) / 3) + ((temperature - 98.6) / 0.9))

    if known_diabetes:
        diabetes = min(0.99, diabetes + 0.14)
    if known_hypertension:
        hypertension = min(0.99, hypertension + 0.12)
    if known_cardiac:
        cardio = min(0.99, cardio + 0.16)
    if known_respiratory:
        respiratory = min(0.99, respiratory + 0.14)

    probabilities = {
        "Hypertension Risk": round(hypertension, 4),
        "Diabetes Risk": round(diabetes, 4),
        "Cardio Risk": round(cardio, 4),
        "Respiratory Risk": round(respiratory, 4),
    }

    weighted_score = (
        (hypertension * 0.28)
        + (diabetes * 0.24)
        + (cardio * 0.30)
        + (respiratory * 0.18)
    ) * 100.0
    risk_score = round(max(0.0, min(99.9, weighted_score)), 2)
    risk_level = _risk_level(risk_score)

    predicted_diseases = [name for name, value in probabilities.items() if value >= 0.55]
    if not predicted_diseases:
        highest = max(probabilities.items(), key=lambda item: item[1])
        if highest[1] >= 0.45:
            predicted_diseases = [highest[0]]
        else:
            predicted_diseases = ["Stable - Observation Mode"]

    return {
        "model_version": MODEL_VERSION,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "predicted_diseases": predicted_diseases,
        "probabilities": probabilities,
        "recommendation": "Urgent clinician review and close monitoring advised."
        if risk_level in ("critical", "high")
        else "Continue routine monitoring.",
        "age": age,
    }
```

---

## Code A.12: Saving AI Risk Assessment and Priority Alert

**Source File:** `app.py`

**Purpose:** This code stores AI output in the database and creates priority alerts for high-risk or critical-risk patients.

```python
def create_risk_assessment(db, patient_row, patient_id, created_by):
    metric = fetch_latest_metric(db, patient_id)
    recent_records = fetch_recent_records(db, patient_id, limit=12)
    assessment = predict_risk(dict(patient_row), metric, recent_records)
    predicted_text = ", ".join(assessment["predicted_diseases"])
    cursor = db.execute(
        """
        INSERT INTO risk_assessments
        (patient_id, model_version, risk_score, risk_level, predicted_diseases,
         probabilities_json, factors_json, recommendation, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            patient_id,
            assessment["model_version"],
            assessment["risk_score"],
            assessment["risk_level"],
            predicted_text,
            json.dumps(assessment["probabilities"], ensure_ascii=True),
            json.dumps(assessment["factors"], ensure_ascii=True),
            assessment["recommendation"],
            created_by,
            now(),
        ),
    )
    risk_assessment_id = cursor.lastrowid

    if assessment["risk_level"] in ("high", "critical"):
        db.execute(
            """
            INSERT INTO priority_alerts
            (patient_id, risk_assessment_id, title, details, severity, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'open', ?)
            """,
            (
                patient_id,
                risk_assessment_id,
                f"{assessment['risk_level'].title()} Risk Patient",
                f"Predicted: {predicted_text}. Recommendation: {assessment['recommendation']}",
                assessment["risk_level"],
                now(),
            ),
        )

    add_integrity_event(
        db,
        "AI_RISK_ASSESSMENT",
        {
            "patient_id": patient_id,
            "risk_score": assessment["risk_score"],
            "risk_level": assessment["risk_level"],
            "predicted_diseases": assessment["predicted_diseases"],
            "model_version": assessment["model_version"],
        },
        patient_id=patient_id,
    )
    return assessment
```

---

## Code A.13: Smart Doctor Dashboard

**Source File:** `app.py`

**Purpose:** This code prepares dashboard statistics, risk distribution, priority patient list, alerts, risk trend, audit logs, and integrity status.

```python
@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    stats = {
        "patients": db.execute("SELECT COUNT(*) FROM patients").fetchone()[0],
        "records": db.execute("SELECT COUNT(*) FROM medical_records").fetchone()[0],
        "biometrics": db.execute("SELECT COUNT(*) FROM biometrics").fetchone()[0],
        "alerts_open": db.execute("SELECT COUNT(*) FROM priority_alerts WHERE status = 'open'").fetchone()[0],
    }

    latest_risks = db.execute(
        """
        SELECT ra.patient_id, ra.risk_score, ra.risk_level, ra.predicted_diseases,
               p.full_name, p.patient_code
        FROM risk_assessments ra
        JOIN (
            SELECT patient_id, MAX(id) AS latest_id
            FROM risk_assessments
            GROUP BY patient_id
        ) latest ON latest.latest_id = ra.id
        JOIN patients p ON p.id = ra.patient_id
        ORDER BY ra.risk_score DESC
        """
    ).fetchall()

    risk_distribution = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
    for row in latest_risks:
        risk_distribution[row["risk_level"]] = risk_distribution.get(row["risk_level"], 0) + 1

    priority_patients = [dict(item) for item in latest_risks[:8]]
    open_alerts = db.execute(
        """
        SELECT a.id, a.title, a.severity, a.details, a.created_at,
               p.full_name, p.patient_code, p.id AS patient_id
        FROM priority_alerts a
        JOIN patients p ON p.id = a.patient_id
        WHERE a.status = 'open'
        ORDER BY
          CASE a.severity
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            ELSE 3
          END,
          a.id DESC
        LIMIT 10
        """
    ).fetchall()

    chain_status = verify_chain(db)
    recent_logs = db.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 8").fetchall()

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_logs=recent_logs,
        priority_patients=priority_patients,
        open_alerts=open_alerts,
        risk_distribution=risk_distribution,
        chain_status=chain_status,
    )
```

---

## Code A.14: Emergency Snapshot Collection

**Source File:** `app.py`

**Purpose:** This code collects all emergency-critical patient information after biometric matching.

```python
def fetch_emergency_snapshot(db, patient_id):
    patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not patient:
        return None

    latest_metric = db.execute(
        """
        SELECT * FROM health_metrics
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,),
    ).fetchone()
    latest_record = db.execute(
        """
        SELECT * FROM medical_records
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,),
    ).fetchone()
    latest_risk = db.execute(
        """
        SELECT * FROM risk_assessments
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,),
    ).fetchone()
    open_alerts = db.execute(
        """
        SELECT title, details, severity, created_at
        FROM priority_alerts
        WHERE patient_id = ? AND status = 'open'
        ORDER BY id DESC
        LIMIT 5
        """,
        (patient_id,),
    ).fetchall()
    notifications = db.execute(
        """
        SELECT recipient_phone, message, status, sent_by, created_at
        FROM emergency_notifications
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (patient_id,),
    ).fetchall()

    return {
        "patient": patient,
        "latest_metric": latest_metric,
        "latest_record": latest_record,
        "latest_risk": latest_risk,
        "open_alerts": open_alerts,
        "family_alert_phone": extract_phone_number(patient["emergency_contact"]) or extract_phone_number(patient["phone"]),
        "family_alert_message": build_family_alert_message(patient, latest_risk),
        "notifications": notifications,
    }
```

---

## Code A.15: Emergency Scan Route

**Source File:** `app.py`

**Purpose:** This route is used in accident or ICU situations. It scans face/fingerprint, retrieves the emergency snapshot, logs the lookup, and opens treatment-critical details.

```python
@app.route("/emergency-scan", methods=["GET", "POST"])
@roles_required("admin", "doctor", "receptionist")
def emergency_scan():
    emergency_case = None
    candidates = []
    match = None

    if request.method == "POST":
        face_upload = request.files.get("face_image")
        fingerprint_upload = request.files.get("fingerprint_image")
        face_image = read_upload_image(face_upload)
        fingerprint_image = read_upload_image(fingerprint_upload)

        if face_image is None and fingerprint_image is None:
            flash("Upload face image or fingerprint image for emergency lookup.", "warning")
            return render_template("emergency_scan.html", emergency_case=emergency_case, candidates=candidates)

        rows = get_db().execute(
            """
            SELECT b.patient_id, b.biometric_type, b.encrypted_path, p.full_name, p.patient_code
            FROM biometrics b
            JOIN patients p ON p.id = b.patient_id
            WHERE b.biometric_type IN ('face', 'fingerprint')
            ORDER BY b.id DESC
            """
        ).fetchall()
        rows = [dict(row) for row in rows]
        match, candidates = match_patient(face_image, fingerprint_image, rows, KEY_PATH)

        if match:
            db = get_db()
            session["verified_patient_id"] = match["patient_id"]
            emergency_case = fetch_emergency_snapshot(db, match["patient_id"])
            add_integrity_event(
                db,
                "EMERGENCY_LOOKUP",
                {
                    "patient_code": match["patient_code"],
                    "combined_score": match["combined_score"],
                    "face_score": match["face_score"],
                    "fingerprint_score": match["fingerprint_score"],
                },
                patient_id=match["patient_id"],
            )
            db.commit()
            log_action("EMERGENCY_LOOKUP", f"{match['patient_code']} score={match['combined_score']}")
            flash("Emergency patient match found. Critical care snapshot loaded.", "success")
        else:
            log_action("EMERGENCY_LOOKUP_NO_MATCH", "No emergency biometric match")
            flash("No matching patient found. Use manual registration or triage workflow.", "warning")

    return render_template(
        "emergency_scan.html",
        emergency_case=emergency_case,
        candidates=candidates,
        match=match,
    )
```

---

## Code A.16: Family Emergency Alert Module

**Source File:** `app.py`

**Purpose:** This code generates and logs emergency alert messages for the patient's family contact.

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


def send_family_alert_message(_phone, _message):
    # Academic demo mode: records the message as sent without requiring a paid SMS gateway.
    return "sent-demo"


@app.route("/patients/<int:patient_id>/family-alert/send", methods=["POST"])
@roles_required("admin", "doctor", "receptionist")
def send_family_alert(patient_id):
    db = get_db()
    patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not patient:
        flash("Patient not found for family alert.", "warning")
        return redirect(url_for("emergency_scan"))

    latest_risk = db.execute(
        """
        SELECT * FROM risk_assessments
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,),
    ).fetchone()
    recipient_phone = request.form.get("recipient_phone", "").strip()
    message = request.form.get("message", "").strip()

    if not recipient_phone:
        recipient_phone = extract_phone_number(patient["emergency_contact"]) or extract_phone_number(patient["phone"])
    if not message:
        message = build_family_alert_message(patient, latest_risk)

    if not recipient_phone:
        flash("Emergency contact number is missing. Add phone number before sending alert.", "warning")
        emergency_case = fetch_emergency_snapshot(db, patient_id)
        return render_template("emergency_scan.html", emergency_case=emergency_case, candidates=[], match=None)

    status = send_family_alert_message(recipient_phone, message)
    db.execute(
        """
        INSERT INTO emergency_notifications
        (patient_id, recipient_phone, message, status, sent_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (patient_id, recipient_phone, message, status, session["username"], now()),
    )
    add_integrity_event(
        db,
        "FAMILY_EMERGENCY_ALERT_SENT",
        {"recipient_phone": recipient_phone, "message": message, "status": status},
        patient_id=patient_id,
    )
    db.commit()
    log_action("FAMILY_EMERGENCY_ALERT_SENT", f"Patient ID {patient_id} to {recipient_phone}")
    flash("Family emergency alert message sent.", "success")

    emergency_case = fetch_emergency_snapshot(db, patient_id)
    return render_template("emergency_scan.html", emergency_case=emergency_case, candidates=[], match=None)
```

---

## Code A.17: Blockchain-Style Integrity Chain

**Source File:** `integrity_chain.py`

**Purpose:** This code creates tamper-evident linked hash blocks for important project events.

```python
GENESIS_PREVIOUS_HASH = "0" * 64


def _canonical_json(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def append_block(db, event_type, payload, actor="system", patient_id=None):
    payload_json = _canonical_json(payload or {})
    data_hash = _sha256(payload_json)
    timestamp = _now()

    previous = db.execute(
        "SELECT block_index, block_hash FROM integrity_chain ORDER BY block_index DESC LIMIT 1"
    ).fetchone()
    if previous:
        block_index = int(previous["block_index"]) + 1
        previous_hash = previous["block_hash"]
    else:
        block_index = 0
        previous_hash = GENESIS_PREVIOUS_HASH

    raw = f"{block_index}|{patient_id or 0}|{event_type}|{data_hash}|{previous_hash}|{timestamp}|{actor}"
    block_hash = _sha256(raw)

    db.execute(
        """
        INSERT INTO integrity_chain
        (block_index, patient_id, event_type, actor, payload_json,
         data_hash, previous_hash, block_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            block_index,
            patient_id,
            event_type,
            actor,
            payload_json,
            data_hash,
            previous_hash,
            block_hash,
            timestamp,
        ),
    )

    return {
        "block_index": block_index,
        "data_hash": data_hash,
        "block_hash": block_hash,
        "previous_hash": previous_hash,
    }
```

---

## Code A.18: Integrity Chain Verification

**Source File:** `integrity_chain.py`

**Purpose:** This code verifies the continuity of data hashes and block hashes to detect tampering.

```python
def verify_chain(db):
    rows = db.execute(
        """
        SELECT block_index, patient_id, event_type, actor, payload_json,
               data_hash, previous_hash, block_hash, created_at
        FROM integrity_chain
        ORDER BY block_index ASC
        """
    ).fetchall()
    if not rows:
        return {"ok": True, "checked_blocks": 0, "issues": []}

    issues = []
    expected_previous_hash = GENESIS_PREVIOUS_HASH
    expected_index = 0

    for row in rows:
        if row["block_index"] != expected_index:
            issues.append(f"Block index gap at {row['block_index']}")

        data_hash = _sha256(row["payload_json"])
        if data_hash != row["data_hash"]:
            issues.append(f"Payload hash mismatch at block {row['block_index']}")

        if row["previous_hash"] != expected_previous_hash:
            issues.append(f"Previous hash mismatch at block {row['block_index']}")

        raw = (
            f"{row['block_index']}|{row['patient_id'] or 0}|{row['event_type']}|{row['data_hash']}"
            f"|{row['previous_hash']}|{row['created_at']}|{row['actor']}"
        )
        computed_hash = _sha256(raw)
        if computed_hash != row["block_hash"]:
            issues.append(f"Block hash mismatch at block {row['block_index']}")

        expected_previous_hash = row["block_hash"]
        expected_index = row["block_index"] + 1

    return {"ok": len(issues) == 0, "checked_blocks": len(rows), "issues": issues}
```

---

## Code A.19: Patient Registration Form UI

**Source File:** `templates/register_patient.html`

**Purpose:** This frontend code collects patient details, photo, face image, fingerprint image, allergies, and baseline vitals.

```html
<form method="post" enctype="multipart/form-data" class="panel form-grid">
  <label>Full Name
    <input name="full_name" required>
  </label>
  <label>Patient Photo
    <input type="file" name="patient_photo" accept="image/*">
  </label>
  <label>Blood Group
    <input name="blood_group" placeholder="B+">
  </label>
  <label>Emergency Contact
    <input name="emergency_contact">
  </label>
  <label class="wide">Allergies / Clinical Notes
    <textarea name="allergies"></textarea>
  </label>

  <label>Face Image
    <input type="file" name="face_image" accept="image/*">
  </label>
  <label>Fingerprint Image
    <input type="file" name="fingerprint_image" accept="image/*">
  </label>

  <label>Systolic BP
    <input type="number" name="systolic_bp" placeholder="120">
  </label>
  <label>Heart Rate
    <input type="number" name="heart_rate" placeholder="76">
  </label>
  <label>SpO2
    <input type="number" step="0.1" name="spo2" placeholder="98">
  </label>
  <label>Glucose
    <input type="number" step="0.1" name="glucose" placeholder="102">
  </label>

  <div class="form-actions wide">
    <button type="submit">Register Patient</button>
  </div>
</form>
```

---

## Code A.20: Emergency Scan and ICU Handover UI

**Source File:** `templates/emergency_scan.html`

**Purpose:** This frontend code supports emergency face/fingerprint scan, ICU handover print, family alert, vitals display, and AI risk snapshot.

```html
<section class="emergency-hero panel">
  <div>
    <h2>Immediate Biometric Triage</h2>
    <p>Face or fingerprint scan se patient ki allergy, blood group, emergency contact,
       latest vitals aur treatment risk instantly open hota hai.</p>
  </div>
  <form method="post" enctype="multipart/form-data" class="emergency-scan-form">
    <label>Face Scan
      <input type="file" name="face_image" accept="image/*" capture="user">
    </label>
    <label>Fingerprint Scan
      <input type="file" name="fingerprint_image" accept="image/*">
    </label>
    <button type="submit" class="danger-button">Scan for Emergency</button>
  </form>
</section>

{% if emergency_case %}
<section class="panel emergency-actions no-print">
  <div>
    <h2>ICU Handover Tools</h2>
    <p class="muted-line">Emergency summary print karke ICU team ko allergy,
       blood group, vitals aur latest diagnosis handover kar sakte hain.</p>
  </div>
  <button type="button" class="danger-button" onclick="window.print()">Print ICU Handover</button>
</section>

<article class="panel emergency-critical">
  <h2>Critical Treatment Info</h2>
  <dl>
    <dt>Allergies</dt><dd class="critical-text">{{ patient.allergies or "No allergy recorded" }}</dd>
    <dt>Blood Group</dt><dd>{{ patient.blood_group or "-" }}</dd>
    <dt>Emergency Contact</dt><dd>{{ patient.emergency_contact or "-" }}</dd>
    <dt>Phone</dt><dd>{{ patient.phone or "-" }}</dd>
  </dl>
</article>

<section class="panel family-alert-panel">
  <div>
    <h2>Send Family Emergency Alert</h2>
    <p class="muted-line">Emergency contact ko patient status aur hospital contact request ka alert message send karein.</p>
  </div>
  <form method="post" action="{{ url_for('send_family_alert', patient_id=patient.id) }}" class="family-alert-form">
    <label>Family Contact Number
      <input name="recipient_phone" value="{{ emergency_case.family_alert_phone }}" required>
    </label>
    <label class="wide">Alert Message
      <textarea name="message" required>{{ emergency_case.family_alert_message }}</textarea>
    </label>
    <div class="form-actions wide">
      <button type="submit" class="danger-button">Send Alert Message</button>
    </div>
  </form>
</section>

<article class="panel">
  <h2>AI Risk Snapshot</h2>
  {% if risk %}
  <p><span class="level-tag {{ risk.risk_level }}">{{ risk.risk_level|title }}</span>
     Score {{ risk.risk_score }}</p>
  <p>{{ risk.predicted_diseases }}</p>
  <p class="muted-line">{{ risk.recommendation }}</p>
  {% else %}
  <p>No risk assessment recorded.</p>
  {% endif %}
</article>
{% endif %}
```

---

## Code A.21: Medical Record Addition and AI Re-Evaluation

**Source File:** `app.py`

**Purpose:** This code allows doctors to add diagnosis and prescription, then automatically re-evaluates AI patient risk.

```python
@app.route("/patients/<int:patient_id>/records/add", methods=["POST"])
@roles_required("admin", "doctor")
def add_record(patient_id):
    diagnosis = request.form.get("diagnosis", "").strip()
    prescription = request.form.get("prescription", "").strip()
    doctor_notes = request.form.get("doctor_notes", "").strip()
    if not diagnosis:
        flash("Diagnosis is required.", "danger")
        return redirect(url_for("patient_detail", patient_id=patient_id))

    db = get_db()
    db.execute(
        """
        INSERT INTO medical_records
        (patient_id, diagnosis, prescription, doctor_notes, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (patient_id, diagnosis, prescription, doctor_notes, session["username"], now()),
    )
    add_integrity_event(
        db,
        "MEDICAL_RECORD_ADDED",
        {"diagnosis": diagnosis, "prescription": prescription, "doctor_notes": doctor_notes},
        patient_id=patient_id,
    )

    patient_row = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if patient_row:
        create_risk_assessment(db, patient_row, patient_id, session["username"])
    db.commit()

    log_action("MEDICAL_RECORD_ADDED", f"Patient ID {patient_id}")
    flash("Medical record added and AI risk re-evaluated.", "success")
    return redirect(url_for("patient_detail", patient_id=patient_id))
```

---

## Code A.22: Important Project Entry Point

**Source File:** `app.py`

**Purpose:** This code starts the Flask development server for project demonstration.

```python
def prepare_database():
    init_db()
    seed_users()
    get_db().commit()


with app.app_context():
    prepare_database()


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
```

