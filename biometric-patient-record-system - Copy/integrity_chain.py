import hashlib
import json
from datetime import datetime


GENESIS_PREVIOUS_HASH = "0" * 64


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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
        (block_index, patient_id, event_type, actor, payload_json, data_hash, previous_hash, block_hash, created_at)
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


def verify_chain(db):
    rows = db.execute(
        """
        SELECT block_index, patient_id, event_type, actor, payload_json, data_hash, previous_hash, block_hash, created_at
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
