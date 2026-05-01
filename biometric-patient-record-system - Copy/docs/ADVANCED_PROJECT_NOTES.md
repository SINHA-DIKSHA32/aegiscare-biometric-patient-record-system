# AegisCare: Advanced Biometric Patient Record Retrieval System with AI Risk Prediction

## 1) Upgraded Scope

This upgraded version transforms a basic biometric patient lookup app into an MCA-level intelligent health platform with:

- predictive AI risk scoring,
- face/fingerprint biometric authentication,
- blockchain-style integrity chain,
- smart clinical dashboard and priority alerts.

## 2) Core Modules

1. `app.py`:
   - Extended schema (`health_metrics`, `risk_assessments`, `priority_alerts`, `integrity_chain`)
   - Smart dashboard endpoints and workflow orchestration
   - Automatic AI risk refresh on metric/record updates
2. `ai_risk_engine.py`:
   - Feature-based disease-risk prediction model
   - Risk score + level generation
   - Explainable factors and recommendations
3. `biometric_engine.py`:
   - Face + fingerprint matching
   - Encrypted storage for biometric image templates
4. `integrity_chain.py`:
   - Linked hash blocks for tamper-evident event logs
   - Full chain verification utility

## 3) Smart Dashboard Features

- Risk distribution (low/moderate/high/critical)
- Average risk trend graph
- Priority patient queue sorted by risk score
- Open critical alerts for doctor intervention
- Real-time integrity status indicator

## 4) AI Layer Design

- Inputs: vitals + age + recent diagnosis history
- Outputs:
  - overall risk score (0-100)
  - risk level class
  - predicted disease-risk profile
  - intervention recommendation
- Auto-alert generation for high/critical cases

## 5) Blockchain Integrity Design

- Every critical action writes one block:
  - patient registration
  - biometric enrollment
  - metric capture
  - medical record updates
  - AI risk assessment
  - alert resolution
- Block structure:
  - `data_hash`
  - `previous_hash`
  - `block_hash`
- Verification can detect data/hash continuity mismatch.

## 6) Academic Value

This project demonstrates integrated application of:

- secure data lifecycle,
- biometric authentication,
- predictive analytics,
- event integrity assurance,
- role-based healthcare workflows.

This is suitable for MCA final year demonstration, viva, architecture discussion, and module-wise evaluation.
