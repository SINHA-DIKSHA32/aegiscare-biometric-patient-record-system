import hashlib
import hmac
import secrets
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np


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
