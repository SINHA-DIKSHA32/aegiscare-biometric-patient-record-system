import math
import re
from datetime import date, datetime


MODEL_VERSION = "AegisCare-Risk-v2"


def _safe_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_age(dob_text):
    if not dob_text:
        return None
    try:
        dob = datetime.strptime(dob_text, "%Y-%m-%d").date()
    except ValueError:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def _sigmoid(value):
    return 1.0 / (1.0 + math.exp(-value))


def _normalize_text(value):
    if not value:
        return ""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\s]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _history_keywords(records):
    if not records:
        return ""
    combined = " ".join(f"{item.get('diagnosis', '')} {item.get('doctor_notes', '')}" for item in records)
    return _normalize_text(combined)


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

    factors = []
    if systolic >= 140 or diastolic >= 90:
        factors.append("Elevated blood pressure trend")
    if glucose >= 126:
        factors.append("High glucose trend")
    if heart_rate >= 100:
        factors.append("Tachycardia signal")
    if spo2 <= 93:
        factors.append("Low oxygen saturation")
    if respiratory_rate >= 22:
        factors.append("High respiratory rate")
    if temperature >= 100.4:
        factors.append("Possible fever pattern")
    if not factors:
        factors.append("Vitals currently near expected range")

    if risk_level in ("critical", "high"):
        recommendation = "Urgent clinician review and close monitoring advised."
    elif risk_level == "moderate":
        recommendation = "Schedule follow-up and lifestyle intervention monitoring."
    else:
        recommendation = "Continue routine monitoring."

    return {
        "model_version": MODEL_VERSION,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "predicted_diseases": predicted_diseases,
        "probabilities": probabilities,
        "factors": factors,
        "recommendation": recommendation,
        "age": age,
    }
