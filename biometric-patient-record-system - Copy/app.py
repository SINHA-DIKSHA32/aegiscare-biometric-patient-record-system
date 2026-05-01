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

from flask import Flask, abort, flash, g, has_request_context, redirect, render_template, request, send_file, session, url_for
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
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError:
        return None


def parse_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def ensure_column(db, table_name, column_name, column_definition):
    columns = db.execute(f"PRAGMA table_info({table_name})").fetchall()
    if column_name not in {column["name"] for column in columns}:
        db.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


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

        CREATE INDEX IF NOT EXISTS idx_biometrics_patient ON biometrics(patient_id);
        CREATE INDEX IF NOT EXISTS idx_records_patient ON medical_records(patient_id);
        CREATE INDEX IF NOT EXISTS idx_metrics_patient ON health_metrics(patient_id);
        CREATE INDEX IF NOT EXISTS idx_risk_patient ON risk_assessments(patient_id);
        CREATE INDEX IF NOT EXISTS idx_alert_status ON priority_alerts(status);
        CREATE INDEX IF NOT EXISTS idx_emergency_notifications_patient ON emergency_notifications(patient_id);
        CREATE INDEX IF NOT EXISTS idx_integrity_block ON integrity_chain(block_index);
        """
    )
    ensure_column(db, "patients", "profile_photo_path", "TEXT")
    seed_users()
    db.commit()


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


def log_action(action, details=""):
    actor = session.get("username", "system") if has_request_context() else "system"
    get_db().execute(
        "INSERT INTO audit_logs (actor, action, details, created_at) VALUES (?, ?, ?, ?)",
        (actor, action, details, now()),
    )
    get_db().commit()


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


def add_integrity_event(db, event_type, payload, patient_id=None):
    actor = session.get("username", "system") if has_request_context() else "system"
    return append_block(
        db=db,
        event_type=event_type,
        payload=payload,
        actor=actor,
        patient_id=patient_id,
    )


def fetch_latest_metric(db, patient_id):
    row = db.execute(
        """
        SELECT systolic_bp, diastolic_bp, heart_rate, spo2, glucose, temperature, respiratory_rate, notes, created_at
        FROM health_metrics
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (patient_id,),
    ).fetchone()
    return dict(row) if row else {}


def fetch_recent_records(db, patient_id, limit=12):
    rows = db.execute(
        """
        SELECT diagnosis, doctor_notes, created_at
        FROM medical_records
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (patient_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def extract_phone_number(value):
    if not value:
        return ""
    matches = re.findall(r"\+?\d[\d\s-]{8,}\d", value)
    if not matches:
        return ""
    return re.sub(r"[\s-]+", "", matches[0])


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


def create_risk_assessment(db, patient_row, patient_id, created_by):
    metric = fetch_latest_metric(db, patient_id)
    recent_records = fetch_recent_records(db, patient_id, limit=12)
    assessment = predict_risk(dict(patient_row), metric, recent_records)
    predicted_text = ", ".join(assessment["predicted_diseases"])
    cursor = db.execute(
        """
        INSERT INTO risk_assessments
        (patient_id, model_version, risk_score, risk_level, predicted_diseases, probabilities_json, factors_json, recommendation, created_by, created_at)
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
        "alerts_open": db.execute("SELECT COUNT(*) FROM priority_alerts WHERE status = 'open'").fetchone()[0],
    }

    latest_risks = db.execute(
        """
        SELECT ra.patient_id, ra.risk_score, ra.risk_level, ra.predicted_diseases, p.full_name, p.patient_code
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
        SELECT a.id, a.title, a.severity, a.details, a.created_at, p.full_name, p.patient_code, p.id AS patient_id
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

    risk_trend_rows = db.execute(
        """
        SELECT day, avg_risk
        FROM (
            SELECT substr(created_at, 1, 10) AS day, ROUND(AVG(risk_score), 2) AS avg_risk
            FROM risk_assessments
            GROUP BY substr(created_at, 1, 10)
            ORDER BY day DESC
            LIMIT 14
        )
        ORDER BY day ASC
        """
    ).fetchall()
    risk_trend = {
        "labels": [item["day"] for item in risk_trend_rows],
        "values": [item["avg_risk"] for item in risk_trend_rows],
    }

    chain_status = verify_chain(db)
    recent_logs = db.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 8").fetchall()

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_logs=recent_logs,
        priority_patients=priority_patients,
        open_alerts=open_alerts,
        risk_distribution=risk_distribution,
        risk_trend=risk_trend,
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
            SELECT * FROM patients
            WHERE full_name LIKE ? OR patient_code LIKE ? OR phone LIKE ?
            ORDER BY id DESC
            """,
            (f"%{search}%", f"%{search}%", f"%{search}%"),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM patients ORDER BY id DESC").fetchall()

    latest_risks = db.execute(
        """
        SELECT ra.patient_id, ra.risk_score, ra.risk_level
        FROM risk_assessments ra
        JOIN (
            SELECT patient_id, MAX(id) AS latest_id
            FROM risk_assessments
            GROUP BY patient_id
        ) latest ON latest.latest_id = ra.id
        """
    ).fetchall()
    risk_map = {row["patient_id"]: {"score": row["risk_score"], "level": row["risk_level"]} for row in latest_risks}
    return render_template("patients.html", patients=rows, search=search, risk_map=risk_map)


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

        photo_upload = request.files.get("patient_photo")
        if photo_upload and photo_upload.filename:
            photo_extension = Path(secure_filename(photo_upload.filename)).suffix.lower()
            if photo_extension not in ALLOWED_PHOTO_EXTENSIONS:
                flash("Patient photo must be JPG, PNG, or WEBP.", "danger")
                return render_template("register_patient.html")

        cursor = db.execute(
            """
            INSERT INTO patients
            (patient_code, full_name, gender, date_of_birth, phone, address, blood_group, allergies, emergency_contact, profile_photo_path, created_at)
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
        has_metric_data = any(
            metric_payload[key] is not None for key in metric_payload if key not in ("notes",)
        ) or bool(metric_payload["notes"])
        if has_metric_data:
            db.execute(
                """
                INSERT INTO health_metrics
                (patient_id, systolic_bp, diastolic_bp, heart_rate, spo2, glucose, temperature, respiratory_rate, notes, recorded_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    patient_id,
                    metric_payload["systolic_bp"],
                    metric_payload["diastolic_bp"],
                    metric_payload["heart_rate"],
                    metric_payload["spo2"],
                    metric_payload["glucose"],
                    metric_payload["temperature"],
                    metric_payload["respiratory_rate"],
                    metric_payload["notes"],
                    session["username"],
                    now(),
                ),
            )
            add_integrity_event(db, "HEALTH_METRIC_CAPTURED", metric_payload, patient_id=patient_id)

        patient_row = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
        create_risk_assessment(db, patient_row, patient_id, session["username"])

        db.commit()
        log_action("PATIENT_REGISTERED", f"{patient_code} - {values['full_name']}")
        flash("Patient registered. AI baseline risk profile generated.", "success")
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
    metrics = db.execute(
        """
        SELECT * FROM health_metrics
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT 12
        """,
        (patient_id,),
    ).fetchall()
    risk_history_rows = db.execute(
        """
        SELECT id, risk_score, risk_level, predicted_diseases, recommendation, created_at
        FROM risk_assessments
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT 12
        """,
        (patient_id,),
    ).fetchall()
    open_alerts = db.execute(
        """
        SELECT id, title, details, severity, created_at
        FROM priority_alerts
        WHERE patient_id = ? AND status = 'open'
        ORDER BY id DESC
        """,
        (patient_id,),
    ).fetchall()

    latest_risk = risk_history_rows[0] if risk_history_rows else None
    metrics_reversed = list(reversed(metrics))
    risk_reversed = list(reversed(risk_history_rows))
    chart_data = {
        "labels": [item["created_at"][5:16] for item in metrics_reversed],
        "systolic": [item["systolic_bp"] if item["systolic_bp"] is not None else None for item in metrics_reversed],
        "glucose": [item["glucose"] if item["glucose"] is not None else None for item in metrics_reversed],
        "spo2": [item["spo2"] if item["spo2"] is not None else None for item in metrics_reversed],
        "risk_labels": [item["created_at"][5:16] for item in risk_reversed],
        "risk_values": [item["risk_score"] for item in risk_reversed],
    }

    return render_template(
        "patient_detail.html",
        patient=patient,
        records=records,
        biometrics=biometrics,
        metrics=metrics,
        latest_risk=latest_risk,
        risk_history=risk_history_rows,
        open_alerts=open_alerts,
        chart_data=chart_data,
    )


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
        INSERT INTO medical_records (patient_id, diagnosis, prescription, doctor_notes, created_by, created_at)
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


@app.route("/patients/<int:patient_id>/metrics/add", methods=["POST"])
@roles_required("admin", "doctor", "receptionist")
def add_metrics(patient_id):
    db = get_db()
    payload = {
        "systolic_bp": parse_int(request.form.get("systolic_bp")),
        "diastolic_bp": parse_int(request.form.get("diastolic_bp")),
        "heart_rate": parse_int(request.form.get("heart_rate")),
        "spo2": parse_float(request.form.get("spo2")),
        "glucose": parse_float(request.form.get("glucose")),
        "temperature": parse_float(request.form.get("temperature")),
        "respiratory_rate": parse_int(request.form.get("respiratory_rate")),
        "notes": request.form.get("notes", "").strip(),
    }

    has_data = any(payload[key] is not None for key in payload if key != "notes") or bool(payload["notes"])
    if not has_data:
        flash("Add at least one health metric to continue.", "warning")
        return redirect(url_for("patient_detail", patient_id=patient_id))

    db.execute(
        """
        INSERT INTO health_metrics
        (patient_id, systolic_bp, diastolic_bp, heart_rate, spo2, glucose, temperature, respiratory_rate, notes, recorded_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            patient_id,
            payload["systolic_bp"],
            payload["diastolic_bp"],
            payload["heart_rate"],
            payload["spo2"],
            payload["glucose"],
            payload["temperature"],
            payload["respiratory_rate"],
            payload["notes"],
            session["username"],
            now(),
        ),
    )
    add_integrity_event(db, "HEALTH_METRIC_CAPTURED", payload, patient_id=patient_id)

    patient_row = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if patient_row:
        create_risk_assessment(db, patient_row, patient_id, session["username"])
    db.commit()

    log_action("HEALTH_METRICS_ADDED", f"Patient ID {patient_id}")
    flash("Health metrics captured and AI risk refreshed.", "success")
    return redirect(url_for("patient_detail", patient_id=patient_id))


@app.route("/alerts/<int:alert_id>/resolve", methods=["POST"])
@roles_required("admin", "doctor")
def resolve_alert(alert_id):
    db = get_db()
    alert = db.execute("SELECT * FROM priority_alerts WHERE id = ?", (alert_id,)).fetchone()
    if not alert:
        flash("Alert not found.", "warning")
        return redirect(url_for("dashboard"))

    db.execute(
        "UPDATE priority_alerts SET status = 'resolved', resolved_at = ? WHERE id = ?",
        (now(), alert_id),
    )
    add_integrity_event(
        db,
        "PRIORITY_ALERT_RESOLVED",
        {"alert_id": alert_id, "severity": alert["severity"], "title": alert["title"]},
        patient_id=alert["patient_id"],
    )
    db.commit()
    log_action("ALERT_RESOLVED", f"Alert ID {alert_id}")
    flash("Priority alert marked as resolved.", "success")
    return redirect(url_for("patient_detail", patient_id=alert["patient_id"]))


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
        {
            "recipient_phone": recipient_phone,
            "message": message,
            "status": status,
        },
        patient_id=patient_id,
    )
    db.commit()
    log_action("FAMILY_EMERGENCY_ALERT_SENT", f"Patient ID {patient_id} to {recipient_phone}")
    flash("Family emergency alert message sent.", "success")

    emergency_case = fetch_emergency_snapshot(db, patient_id)
    return render_template("emergency_scan.html", emergency_case=emergency_case, candidates=[], match=None)


@app.route("/audit")
@roles_required("admin")
def audit():
    rows = get_db().execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 200").fetchall()
    return render_template("audit.html", logs=rows)


@app.route("/integrity")
@roles_required("admin", "doctor")
def integrity():
    db = get_db()
    chain_status = verify_chain(db)
    blocks = db.execute(
        """
        SELECT block_index, event_type, actor, data_hash, block_hash, previous_hash, created_at, patient_id
        FROM integrity_chain
        ORDER BY block_index DESC
        LIMIT 80
        """
    ).fetchall()
    return render_template("integrity.html", chain_status=chain_status, blocks=blocks)


@app.route("/blockchain")
@roles_required("admin", "doctor")
def blockchain():
    return redirect(url_for("integrity"))


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
