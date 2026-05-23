import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parent
DEPS_DIR = BASE_DIR / ".deps"
if DEPS_DIR.exists():
    sys.path.insert(0, str(DEPS_DIR))

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from biometric_engine import encrypt_and_save, match_patient, read_upload_image
from clinical_ai import analyze_patient_risk


INSTANCE_DIR = BASE_DIR / "instance"
DB_PATH = INSTANCE_DIR / "patients.db"
KEY_PATH = INSTANCE_DIR / "biometric.key"
BIOMETRIC_DIR = INSTANCE_DIR / "encrypted_biometrics"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-before-production")
STAFF_ROLES = ("admin", "doctor", "receptionist")
RISK_LEVELS = ("Low", "Moderate", "High", "Critical")


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
            height_cm REAL,
            weight_kg REAL,
            chronic_conditions TEXT,
            insurance_id TEXT,
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

        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            diagnosis TEXT NOT NULL,
            prescription TEXT,
            doctor_notes TEXT,
            created_by TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS vitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            systolic_bp REAL,
            diastolic_bp REAL,
            pulse_rate REAL,
            temperature_c REAL,
            spo2 REAL,
            fasting_glucose REAL,
            random_glucose REAL,
            bmi REAL,
            symptoms TEXT,
            ai_risk_score INTEGER NOT NULL,
            ai_risk_level TEXT NOT NULL,
            ai_summary TEXT NOT NULL,
            ai_findings TEXT,
            disease_predictions TEXT,
            ai_recommendations TEXT,
            recorded_by TEXT NOT NULL,
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

        CREATE TABLE IF NOT EXISTS blockchain_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            actor TEXT NOT NULL,
            payload TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            block_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    migrate_db(db)
    seed_users()
    if not db.execute("SELECT id FROM blockchain_ledger LIMIT 1").fetchone():
        append_ledger_block(
            "GENESIS",
            {"project": "AegisCare", "message": "Tamper-evident audit ledger initialized"},
            actor="system",
        )
    db.commit()


def seed_users():
    db = get_db()
    users = [
        ("admin", "admin123", "admin", "System Admin"),
        ("doctor", "doctor123", "doctor", "Demo Doctor"),
        ("reception", "reception123", "receptionist", "Reception Desk"),
        ("patient", "patient123", "patient", "Patient Demo"),
    ]
    for username, password, role, full_name in users:
        exists = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if not exists:
            db.execute(
                "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                (username, generate_password_hash(password), role, full_name),
            )


def migrate_db(db):
    patient_columns = {row["name"] for row in db.execute("PRAGMA table_info(patients)").fetchall()}
    migrations = {
        "height_cm": "REAL",
        "weight_kg": "REAL",
        "chronic_conditions": "TEXT",
        "insurance_id": "TEXT",
    }
    for column, definition in migrations.items():
        if column not in patient_columns:
            db.execute(f"ALTER TABLE patients ADD COLUMN {column} {definition}")


def _hash_block(event_type, actor, payload, previous_hash, created_at):
    raw = json.dumps(
        {
            "event_type": event_type,
            "actor": actor,
            "payload": payload,
            "previous_hash": previous_hash,
            "created_at": created_at,
        },
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def append_ledger_block(event_type, payload, actor=None):
    db = get_db()
    actor = actor or session.get("username", "system")
    payload_text = json.dumps(payload, sort_keys=True, default=str)
    previous = db.execute("SELECT block_hash FROM blockchain_ledger ORDER BY id DESC LIMIT 1").fetchone()
    previous_hash = previous["block_hash"] if previous else "0" * 64
    created_at = now()
    block_hash = _hash_block(event_type, actor, payload_text, previous_hash, created_at)
    db.execute(
        """
        INSERT INTO blockchain_ledger
        (event_type, actor, payload, previous_hash, block_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (event_type, actor, payload_text, previous_hash, block_hash, created_at),
    )


def verify_ledger():
    rows = get_db().execute("SELECT * FROM blockchain_ledger ORDER BY id").fetchall()
    previous_hash = "0" * 64
    for row in rows:
        expected = _hash_block(
            row["event_type"],
            row["actor"],
            row["payload"],
            row["previous_hash"],
            row["created_at"],
        )
        if row["previous_hash"] != previous_hash or row["block_hash"] != expected:
            return {
                "valid": False,
                "total_blocks": len(rows),
                "broken_at": row["id"],
                "last_hash": rows[-1]["block_hash"] if rows else "",
            }
        previous_hash = row["block_hash"]
    return {
        "valid": True,
        "total_blocks": len(rows),
        "broken_at": None,
        "last_hash": rows[-1]["block_hash"] if rows else "",
    }


def log_action(action, details=""):
    actor = session.get("username", "system")
    db = get_db()
    db.execute(
        "INSERT INTO audit_logs (actor, action, details, created_at) VALUES (?, ?, ?, ?)",
        (actor, action, details, now()),
    )
    append_ledger_block(action, {"details": details}, actor=actor)
    db.commit()


def current_user():
    if "user_id" not in session:
        return None
    return {
        "id": session["user_id"],
        "username": session["username"],
        "role": session["role"],
        "full_name": session["full_name"],
    }


@app.context_processor
def inject_user():
    return {"current_user": current_user()}


def login_required(view):
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    wrapped.__name__ = view.__name__
    return wrapped


def roles_required(*roles):
    def decorator(view):
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first.", "warning")
                return redirect(url_for("login"))
            if session["role"] not in roles:
                flash("You do not have permission for this page.", "danger")
                return redirect(url_for("dashboard"))
            return view(*args, **kwargs)

        wrapped.__name__ = view.__name__
        return wrapped

    return decorator


def can_view_patient(patient_id):
    if session.get("role") in STAFF_ROLES:
        return True
    return session.get("verified_patient_id") == patient_id


def parse_float_field(name):
    value = request.form.get(name, "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def decode_json_list(value):
    if not value:
        return []
    try:
        data = json.loads(value)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def latest_medical_record(db, patient_id):
    return db.execute(
        "SELECT * FROM medical_records WHERE patient_id = ? ORDER BY id DESC LIMIT 1",
        (patient_id,),
    ).fetchone()


def latest_vital_record(db, patient_id):
    return db.execute(
        "SELECT * FROM vitals WHERE patient_id = ? ORDER BY id DESC LIMIT 1",
        (patient_id,),
    ).fetchone()


@app.before_request
def prepare_database():
    init_db()


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session.update(
                {
                    "user_id": user["id"],
                    "username": user["username"],
                    "role": user["role"],
                    "full_name": user["full_name"],
                }
            )
            log_action("LOGIN", f"{user['username']} logged in")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    log_action("LOGOUT", f"{session.get('username', 'unknown')} logged out")
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    stats = {
        "patients": db.execute("SELECT COUNT(*) FROM patients").fetchone()[0],
        "records": db.execute("SELECT COUNT(*) FROM medical_records").fetchone()[0],
        "biometrics": db.execute("SELECT COUNT(*) FROM biometrics").fetchone()[0],
        "logs": db.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0],
        "vitals": db.execute("SELECT COUNT(*) FROM vitals").fetchone()[0],
        "high_risk": db.execute(
            "SELECT COUNT(*) FROM vitals WHERE ai_risk_level IN ('High', 'Critical')"
        ).fetchone()[0],
    }
    recent_logs = db.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 8").fetchall()
    high_risk_patients = db.execute(
        """
        SELECT p.id, p.patient_code, p.full_name, v.ai_risk_score, v.ai_risk_level, v.ai_summary, v.created_at
        FROM vitals v
        JOIN patients p ON p.id = v.patient_id
        JOIN (
            SELECT patient_id, MAX(id) AS latest_id
            FROM vitals
            GROUP BY patient_id
        ) latest ON latest.latest_id = v.id
        WHERE v.ai_risk_level IN ('High', 'Critical')
        ORDER BY v.ai_risk_score DESC, v.id DESC
        LIMIT 6
        """
    ).fetchall()
    chain_status = verify_ledger()
    return render_template(
        "dashboard.html",
        stats=stats,
        recent_logs=recent_logs,
        high_risk_patients=high_risk_patients,
        chain_status=chain_status,
    )


@app.route("/patients")
@roles_required("admin", "doctor", "receptionist")
def patients():
    search = request.args.get("q", "").strip()
    db = get_db()
    if search:
        rows = db.execute(
            """
            SELECT p.*, v.ai_risk_level, v.ai_risk_score
            FROM patients p
            LEFT JOIN (
                SELECT v1.*
                FROM vitals v1
                JOIN (
                    SELECT patient_id, MAX(id) AS latest_id
                    FROM vitals
                    GROUP BY patient_id
                ) latest ON latest.latest_id = v1.id
            ) v ON v.patient_id = p.id
            WHERE p.full_name LIKE ? OR p.patient_code LIKE ? OR p.phone LIKE ?
            ORDER BY p.id DESC
            """,
            (f"%{search}%", f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT p.*, v.ai_risk_level, v.ai_risk_score
            FROM patients p
            LEFT JOIN (
                SELECT v1.*
                FROM vitals v1
                JOIN (
                    SELECT patient_id, MAX(id) AS latest_id
                    FROM vitals
                    GROUP BY patient_id
                ) latest ON latest.latest_id = v1.id
            ) v ON v.patient_id = p.id
            ORDER BY p.id DESC
            """
        ).fetchall()
    return render_template("patients.html", patients=rows, search=search)


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
            "height_cm": parse_float_field("height_cm"),
            "weight_kg": parse_float_field("weight_kg"),
            "chronic_conditions": request.form.get("chronic_conditions", "").strip(),
            "insurance_id": request.form.get("insurance_id", "").strip(),
        }
        if not values["full_name"]:
            flash("Patient name is required.", "danger")
            return render_template("register_patient.html")

        cursor = db.execute(
            """
            INSERT INTO patients
            (patient_code, full_name, gender, date_of_birth, phone, address, blood_group, allergies, emergency_contact, height_cm, weight_kg, chronic_conditions, insurance_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                values["height_cm"],
                values["weight_kg"],
                values["chronic_conditions"],
                values["insurance_id"],
                now(),
            ),
        )
        patient_id = cursor.lastrowid

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

        db.commit()
        log_action("PATIENT_REGISTERED", f"{patient_code} - {values['full_name']}")
        flash("Patient registered successfully.", "success")
        return redirect(url_for("patient_detail", patient_id=patient_id))

    return render_template("register_patient.html")


@app.route("/patients/<int:patient_id>")
@login_required
def patient_detail(patient_id):
    if not can_view_patient(patient_id):
        flash("Please verify biometric identity before opening this patient record.", "warning")
        return redirect(url_for("identify"))

    db = get_db()
    patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not patient:
        flash("Patient not found.", "warning")
        return redirect(url_for("patients"))
    records = db.execute(
        "SELECT * FROM medical_records WHERE patient_id = ? ORDER BY id DESC", (patient_id,)
    ).fetchall()
    biometrics = db.execute("SELECT * FROM biometrics WHERE patient_id = ?", (patient_id,)).fetchall()
    vitals = db.execute(
        "SELECT * FROM vitals WHERE patient_id = ? ORDER BY id DESC LIMIT 10", (patient_id,)
    ).fetchall()
    latest_vital = vitals[0] if vitals else None
    predictions = decode_json_list(latest_vital["disease_predictions"]) if latest_vital else []
    recommendations = decode_json_list(latest_vital["ai_recommendations"]) if latest_vital else []
    findings = decode_json_list(latest_vital["ai_findings"]) if latest_vital else []
    return render_template(
        "patient_detail.html",
        patient=patient,
        records=records,
        biometrics=biometrics,
        vitals=vitals,
        latest_vital=latest_vital,
        predictions=predictions,
        recommendations=recommendations,
        findings=findings,
    )


@app.route("/patients/<int:patient_id>/records/add", methods=["POST"])
@roles_required("admin", "doctor")
def add_record(patient_id):
    diagnosis = request.form.get("diagnosis", "").strip()
    prescription = request.form.get("prescription", "").strip()
    doctor_notes = request.form.get("doctor_notes", "").strip()
    if not diagnosis:
        flash("Diagnosis is required.", "danger")
        return redirect(url_for("patient_detail", patient_id=patient_id))

    get_db().execute(
        """
        INSERT INTO medical_records (patient_id, diagnosis, prescription, doctor_notes, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (patient_id, diagnosis, prescription, doctor_notes, session["username"], now()),
    )
    get_db().commit()
    log_action("MEDICAL_RECORD_ADDED", f"Patient ID {patient_id}")
    flash("Medical record added.", "success")
    return redirect(url_for("patient_detail", patient_id=patient_id))


@app.route("/patients/<int:patient_id>/vitals/add", methods=["POST"])
@roles_required("admin", "doctor")
def add_vitals(patient_id):
    db = get_db()
    patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not patient:
        flash("Patient not found.", "warning")
        return redirect(url_for("patients"))

    height_cm = patient["height_cm"]
    weight_kg = patient["weight_kg"]
    bmi = parse_float_field("bmi")
    if bmi is None and height_cm and weight_kg:
        height_m = float(height_cm) / 100
        if height_m > 0:
            bmi = round(float(weight_kg) / (height_m * height_m), 1)

    vitals = {
        "systolic_bp": parse_float_field("systolic_bp"),
        "diastolic_bp": parse_float_field("diastolic_bp"),
        "pulse_rate": parse_float_field("pulse_rate"),
        "temperature_c": parse_float_field("temperature_c"),
        "spo2": parse_float_field("spo2"),
        "fasting_glucose": parse_float_field("fasting_glucose"),
        "random_glucose": parse_float_field("random_glucose"),
        "bmi": bmi,
        "symptoms": request.form.get("symptoms", "").strip(),
    }
    latest_record = latest_medical_record(db, patient_id)
    analysis = analyze_patient_risk(dict(patient), dict(latest_record) if latest_record else None, vitals)
    db.execute(
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
            session["username"],
            now(),
        ),
    )
    log_action(
        "AI_RISK_ASSESSED",
        f"Patient ID {patient_id} risk={analysis['risk_level']} score={analysis['risk_score']}",
    )
    flash(f"AI risk generated: {analysis['risk_level']} ({analysis['risk_score']}/100).", "success")
    return redirect(url_for("patient_detail", patient_id=patient_id))


@app.route("/identify", methods=["GET", "POST"])
@login_required
def identify():
    match = None
    candidates = []
    auth_mode = request.form.get("auth_mode", "multimodal")
    if request.method == "POST":
        face_upload = request.files.get("face_image")
        fingerprint_upload = request.files.get("fingerprint_image")
        face_image = read_upload_image(face_upload)
        fingerprint_image = read_upload_image(fingerprint_upload)

        if auth_mode == "multimodal" and (face_image is None or fingerprint_image is None):
            flash("Multimodal verification needs both face and fingerprint samples.", "warning")
            return render_template("identify.html", match=match, candidates=candidates, auth_mode=auth_mode)

        if face_image is None and fingerprint_image is None:
            flash("Upload face image, fingerprint image, or both.", "warning")
            return render_template("identify.html", match=match, candidates=candidates, auth_mode=auth_mode)

        rows = get_db().execute(
            """
            SELECT b.patient_id, b.biometric_type, b.encrypted_path, p.full_name, p.patient_code
            FROM biometrics b
            JOIN patients p ON p.id = b.patient_id
            ORDER BY b.id DESC
            """
        ).fetchall()
        rows = [dict(row) for row in rows]
        match, candidates = match_patient(face_image, fingerprint_image, rows, KEY_PATH)
        if match:
            session["verified_patient_id"] = match["patient_id"]
            log_action(
                "MULTIMODAL_BIOMETRIC_MATCH",
                f"{match['patient_code']} mode={auth_mode} score={match['combined_score']}",
            )
            flash("Biometric match found. Patient record opened.", "success")
            return redirect(url_for("patient_detail", patient_id=match["patient_id"]))

        log_action("BIOMETRIC_NO_MATCH", f"No registered patient matched mode={auth_mode}")
        flash("No matching patient found. Please register as a new patient.", "warning")

    return render_template("identify.html", match=match, candidates=candidates, auth_mode=auth_mode)


@app.route("/audit")
@roles_required("admin")
def audit():
    rows = get_db().execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 100").fetchall()
    return render_template("audit.html", logs=rows)


@app.route("/blockchain")
@roles_required("admin")
def blockchain():
    rows = get_db().execute("SELECT * FROM blockchain_ledger ORDER BY id DESC LIMIT 100").fetchall()
    return render_template("blockchain.html", blocks=rows, status=verify_ledger())


@app.route("/patients/<int:patient_id>/fhir.json")
@login_required
def fhir_export(patient_id):
    if not can_view_patient(patient_id):
        flash("Please verify biometric identity before exporting this patient record.", "warning")
        return redirect(url_for("identify"))

    db = get_db()
    patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    records = db.execute(
        "SELECT diagnosis, prescription, doctor_notes, created_by, created_at FROM medical_records WHERE patient_id = ? ORDER BY id DESC",
        (patient_id,),
    ).fetchall()
    latest_vital = latest_vital_record(db, patient_id)
    payload = {
        "resourceType": "Bundle",
        "type": "collection",
        "identifier": {"system": "AegisCare", "value": patient["patient_code"]},
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": patient["patient_code"],
                    "name": [{"text": patient["full_name"]}],
                    "gender": (patient["gender"] or "").lower(),
                    "birthDate": patient["date_of_birth"],
                    "telecom": [{"system": "phone", "value": patient["phone"]}],
                    "bloodGroup": patient["blood_group"],
                    "chronicConditions": patient["chronic_conditions"],
                }
            }
        ],
    }
    if latest_vital:
        payload["entry"].append(
            {
                "resource": {
                    "resourceType": "Observation",
                    "code": {"text": "AI clinical risk summary"},
                    "valueString": latest_vital["ai_summary"],
                    "component": [
                        {"code": {"text": "Risk score"}, "valueInteger": latest_vital["ai_risk_score"]},
                        {"code": {"text": "Risk level"}, "valueString": latest_vital["ai_risk_level"]},
                    ],
                    "effectiveDateTime": latest_vital["created_at"],
                }
            }
        )
    for record in records:
        payload["entry"].append(
            {
                "resource": {
                    "resourceType": "Condition",
                    "code": {"text": record["diagnosis"]},
                    "note": [{"text": record["doctor_notes"] or ""}],
                    "recordedDate": record["created_at"],
                    "recorder": {"display": record["created_by"]},
                }
            }
        )
    log_action("FHIR_EXPORT", f"Patient ID {patient_id}")
    return jsonify(payload)


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
