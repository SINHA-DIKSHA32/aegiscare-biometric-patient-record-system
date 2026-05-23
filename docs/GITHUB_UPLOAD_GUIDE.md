# GitHub Upload Guide

## Recommended Repository Name

```text
aegiscare-ai-biometric-healthcare-platform
```

## Suggested GitHub Description

```text
MCA final-year Flask + OpenCV project for biometric patient record retrieval with AI disease-risk prediction, blockchain audit ledger, and FHIR-style interoperability.
```

## Suggested Topics

```text
python flask opencv sqlite healthcare biometrics face-recognition fingerprint-recognition ai-risk-prediction blockchain-audit fhir mca-project final-year-project
```

## Manual Push Commands

After creating an empty GitHub repository, run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/aegiscare-ai-biometric-healthcare-platform.git
git branch -M main
git push -u origin main
```

## Before Final Submission

1. Add your final report to `reports/`.
2. Add screenshots to `docs/screenshots/`.
3. Update the repository URL in your college submission form.
4. Make sure GitHub shows a clean README on the first page.

## Files That Should Not Be Uploaded

The `.gitignore` already excludes:

- `.venv/`
- `.deps/`
- `instance/`
- `report_output/`
- server logs
- cache files

These files are local runtime outputs and make the repository look messy if committed.
