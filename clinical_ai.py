from datetime import datetime


def _to_float(value):
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_age(date_of_birth):
    if not date_of_birth:
        return None
    try:
        born = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    except ValueError:
        return None
    today = datetime.now().date()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def _risk_level(score):
    if score >= 70:
        return "Critical"
    if score >= 45:
        return "High"
    if score >= 25:
        return "Moderate"
    return "Low"


def _add_prediction(predictions, condition, confidence, reason):
    confidence = max(0, min(100, int(confidence)))
    predictions.append(
        {
            "condition": condition,
            "confidence": confidence,
            "reason": reason,
        }
    )


def analyze_patient_risk(patient, latest_record, vitals):
    """Explainable academic AI layer for patient risk screening.

    This is intentionally transparent and rule-based, so students can explain it in
    viva without claiming it is a production clinical diagnosis model.
    """
    age = calculate_age(patient.get("date_of_birth") if patient else None)
    diagnosis = (latest_record.get("diagnosis", "") if latest_record else "").lower()
    symptoms = (vitals.get("symptoms") or "").lower()

    systolic = _to_float(vitals.get("systolic_bp"))
    diastolic = _to_float(vitals.get("diastolic_bp"))
    pulse = _to_float(vitals.get("pulse_rate"))
    temperature = _to_float(vitals.get("temperature_c"))
    spo2 = _to_float(vitals.get("spo2"))
    fasting_glucose = _to_float(vitals.get("fasting_glucose"))
    random_glucose = _to_float(vitals.get("random_glucose"))
    bmi = _to_float(vitals.get("bmi"))

    score = 0
    findings = []
    recommendations = []
    predictions = []

    if age is not None and age >= 60:
        score += 10
        findings.append("Age is above 60, so baseline clinical risk is increased.")

    if systolic is not None and diastolic is not None:
        if systolic >= 180 or diastolic >= 120:
            score += 30
            findings.append("Blood pressure is in a crisis range.")
            _add_prediction(predictions, "Severe hypertension risk", 88, "Very high BP reading")
            recommendations.append("Immediate doctor review is recommended for very high BP.")
        elif systolic >= 140 or diastolic >= 90:
            score += 22
            findings.append("Blood pressure is above the normal range.")
            _add_prediction(predictions, "Hypertension risk", 76, "Elevated systolic or diastolic BP")
            recommendations.append("Repeat BP measurement and evaluate hypertension history.")
        elif systolic >= 130 or diastolic >= 80:
            score += 10
            findings.append("Blood pressure is slightly elevated.")
            _add_prediction(predictions, "Pre-hypertension tendency", 52, "Borderline BP reading")

    glucose_reason = None
    if fasting_glucose is not None and fasting_glucose >= 126:
        score += 24
        glucose_reason = "Fasting glucose is in diabetic range."
    elif random_glucose is not None and random_glucose >= 200:
        score += 24
        glucose_reason = "Random glucose is in diabetic range."
    elif (fasting_glucose is not None and fasting_glucose >= 100) or (
        random_glucose is not None and random_glucose >= 140
    ):
        score += 12
        glucose_reason = "Glucose level is above ideal range."
    if glucose_reason:
        findings.append(glucose_reason)
        confidence = 80 if "diabetic" in glucose_reason else 58
        _add_prediction(predictions, "Diabetes risk", confidence, glucose_reason)
        recommendations.append("Advise blood sugar follow-up and lifestyle counselling.")

    if temperature is not None and temperature >= 38:
        score += 9
        findings.append("Temperature indicates fever.")
        _add_prediction(predictions, "Infection or fever risk", 62, "Body temperature is high")
        recommendations.append("Monitor temperature and check infection-related symptoms.")

    if spo2 is not None:
        if spo2 < 92:
            score += 28
            findings.append("Oxygen saturation is critically low.")
            _add_prediction(predictions, "Respiratory risk", 86, "SpO2 below 92")
            recommendations.append("Urgent respiratory assessment is recommended.")
        elif spo2 < 95:
            score += 14
            findings.append("Oxygen saturation is below normal range.")
            _add_prediction(predictions, "Respiratory attention needed", 60, "SpO2 below 95")

    if pulse is not None and (pulse > 120 or pulse < 50):
        score += 13
        findings.append("Pulse rate is outside the expected resting range.")
        _add_prediction(predictions, "Cardiac observation risk", 55, "Pulse rate is abnormal")

    if bmi is not None:
        if bmi >= 30:
            score += 10
            findings.append("BMI indicates obesity.")
            _add_prediction(predictions, "Metabolic syndrome tendency", 58, "BMI is high")
        elif bmi < 18.5:
            score += 6
            findings.append("BMI is below normal range.")

    if "chest pain" in symptoms or "breath" in symptoms:
        score += 20
        findings.append("Symptoms include chest pain or breathing difficulty.")
        _add_prediction(predictions, "Cardio-respiratory risk", 78, "Symptom keywords indicate urgent review")
        recommendations.append("Prioritize clinical review because symptoms may be significant.")

    if "diabetes" in diagnosis:
        score += 8
        findings.append("Latest diagnosis mentions diabetes.")
    if "hypertension" in diagnosis or "bp" in diagnosis:
        score += 8
        findings.append("Latest diagnosis mentions BP or hypertension.")

    if not predictions:
        _add_prediction(predictions, "Routine follow-up", 35, "No strong abnormal pattern detected")
        findings.append("No major abnormal risk pattern was detected from available inputs.")

    score = max(0, min(100, int(score)))
    level = _risk_level(score)

    if level in ("High", "Critical") and not recommendations:
        recommendations.append("Doctor review is recommended because the AI risk level is elevated.")
    if not recommendations:
        recommendations.append("Continue routine monitoring and update vitals during each visit.")

    predictions = sorted(predictions, key=lambda item: item["confidence"], reverse=True)[:5]
    summary = f"{level} risk profile with score {score}/100. " + " ".join(findings[:3])

    return {
        "age": age,
        "risk_score": score,
        "risk_level": level,
        "summary": summary,
        "findings": findings,
        "recommendations": recommendations,
        "predictions": predictions,
    }
