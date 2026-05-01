# Viva Preparation: Basic Questions and Answers

## Project Title

**AegisCare: Advanced Biometric Patient Record Retrieval System with AI Risk Prediction**

---

## 1. Viva Me Project Kaise Introduce Karna Hai

Sir/Ma'am, my project title is **AegisCare: Advanced Biometric Patient Record Retrieval System with AI Risk Prediction**. This is a healthcare-based web application developed for hospitals and emergency care scenarios.

The main purpose of this project is to identify a patient using **face scan or fingerprint scan** and retrieve the patient's medical record quickly. In emergency cases, a patient may be unconscious or unable to tell their name, allergy, blood group, or medical history. In that situation, this system can help hospital staff scan the patient's face or fingerprint and immediately access critical information such as allergies, blood group, latest vitals, latest diagnosis, emergency contact, and AI risk score.

This project also includes an **AI risk prediction module**, which calculates patient risk level using vitals like blood pressure, heart rate, oxygen level, glucose, temperature, respiratory rate, age, and medical history. It also includes a **smart doctor dashboard**, **family alert module**, **patient photo**, and **blockchain-style integrity chain** for tamper detection.

---

## 2. Short Project Explanation in 30 Seconds

My project is an advanced patient record retrieval system. It uses face and fingerprint biometrics to identify patients and retrieve their medical records. It also predicts patient risk using an AI-based risk engine and helps doctors identify high-risk patients. In emergency cases, hospital staff can scan the patient and instantly view allergies, blood group, vitals, diagnosis, risk score, and family contact details.

---

## 3. Short Project Explanation in 1 Minute

AegisCare is a Flask-based healthcare web application. It stores patient details, photos, biometric templates, medical records, and health vitals in SQLite database. The system uses OpenCV for face and fingerprint image processing. When staff uploads a face or fingerprint image, the biometric engine compares it with encrypted stored templates and opens the matching patient profile.

The project also has an AI risk prediction module. It takes patient vitals and medical history as input and generates a risk score and risk level such as low, moderate, high, or critical. If the patient is high risk, the system creates priority alerts for doctors. The emergency scan module is useful in accident and ICU cases because it shows allergies, blood group, latest vitals, latest diagnosis, risk score, and family alert option immediately.

---

# Basic Viva Questions and Answers

## Q1. What is your project name?

My project name is **AegisCare: Advanced Biometric Patient Record Retrieval System with AI Risk Prediction**.

## Q2. What is the main objective of your project?

The main objective is to identify patients using face or fingerprint biometrics and retrieve their medical records quickly. It also predicts patient health risk using vitals and medical history. The system is useful in emergency cases where the patient cannot provide identity details.

## Q3. Why did you choose this project?

I chose this project because healthcare record retrieval is a real-world problem. In accident or ICU cases, doctors need allergy, blood group, and medical history immediately. This project solves that problem using biometric identification and AI-based risk prediction.

## Q4. What problem does your project solve?

It solves delayed patient identification and slow medical record retrieval. If a patient is unconscious or does not have an ID card, staff can scan face or fingerprint and retrieve critical information quickly.

## Q5. Who are the users of this system?

The users are:

- Admin
- Doctor
- Receptionist
- Patient demo user
- Emergency staff

## Q6. What are the main modules of your project?

The main modules are:

- Login and role-based access
- Patient registration
- Patient photo upload
- Face and fingerprint biometric enrollment
- Biometric patient retrieval
- AI risk prediction
- Smart doctor dashboard
- Emergency scan
- Family alert
- Medical records and vitals
- Audit log
- Integrity chain

## Q7. Which programming language did you use?

I used **Python** as the main programming language because it is easy to use, supports Flask for web development, and has libraries like OpenCV and NumPy for image processing.

## Q8. Which framework did you use?

I used **Flask**, which is a Python web framework. Flask is lightweight and suitable for building web applications with routes, templates, sessions, authentication, and database integration.

## Q9. Why did you use Flask?

I used Flask because it is simple, flexible, and easy to explain in viva. It allows us to create routes like login, dashboard, patient registration, biometric retrieval, and emergency scan. It also supports Jinja templates for frontend pages.

## Q10. Which database did you use?

I used **SQLite** database.

## Q11. Why did you use SQLite?

SQLite is lightweight, file-based, and does not require a separate database server. It is suitable for academic projects and local demonstration. It stores all patient data, biometric metadata, health metrics, risk assessments, alerts, audit logs, and integrity chain records.

## Q12. What is the use of database in your project?

The database stores:

- User login details
- Patient profile
- Patient photo path
- Biometric file metadata
- Health vitals
- Medical records
- AI risk results
- Priority alerts
- Emergency notification history
- Audit logs
- Integrity chain blocks

## Q13. What are the important tables in your database?

Important tables are:

- `users`
- `patients`
- `biometrics`
- `health_metrics`
- `medical_records`
- `risk_assessments`
- `priority_alerts`
- `emergency_notifications`
- `audit_logs`
- `integrity_chain`

## Q14. What is stored in the patients table?

The patients table stores patient code, full name, gender, date of birth, phone, address, blood group, allergies, emergency contact, profile photo path, and creation date.

## Q15. What is stored in the biometrics table?

The biometrics table stores patient ID, biometric type, encrypted file path, and created time. The biometric type can be face or fingerprint.

## Q16. Do you store raw biometric images directly in the database?

No. The actual biometric image is encrypted and saved in a folder. The database stores only the encrypted file path and metadata. This is better for security and organization.

## Q17. Which technology is used for biometric processing?

I used **OpenCV** for image processing and biometric comparison. OpenCV helps in reading images, grayscale conversion, resizing, face region processing, feature extraction, and similarity comparison.

## Q18. What is OpenCV?

OpenCV means Open Source Computer Vision Library. It is used for image processing, object detection, face detection, feature matching, and computer vision applications.

## Q19. What is NumPy used for?

NumPy is used for handling image data as arrays. OpenCV reads images as NumPy arrays, so NumPy helps in image processing and numerical operations.

## Q20. How does face matching work in your project?

The system reads the uploaded face image and compares it with encrypted stored face templates. It converts images to grayscale, improves contrast, detects face region, resizes the image, and calculates similarity using histogram comparison and ORB feature matching.

## Q21. How does fingerprint matching work?

The system reads the fingerprint image, converts it to grayscale, resizes it, applies slight blur, and compares it with stored fingerprint templates using ORB feature matching and histogram similarity.

## Q22. What is ORB?

ORB stands for Oriented FAST and Rotated BRIEF. It is a feature detection and description algorithm used in computer vision. In this project, it helps compare two biometric images by matching key points.

## Q23. What is histogram comparison?

Histogram comparison checks the distribution of pixel intensities in two images. It helps calculate similarity between uploaded and stored images.

## Q24. Why did you use both ORB and histogram comparison?

ORB helps compare image features and key points, while histogram comparison checks overall image similarity. Combining both gives a better matching score than using only one technique.

## Q25. What happens when a biometric match is found?

When a match is found, the system stores the verified patient ID in session and redirects the user to the patient profile. The patient profile displays photo, personal information, allergies, blood group, medical records, vitals, and risk score.

## Q26. What happens if no match is found?

If no matching patient is found, the system displays a warning message. Staff can try another image, use manual workflow, or register the patient as a new patient.

## Q27. What is AI risk prediction in your project?

AI risk prediction is a module that calculates patient risk score using vitals and medical history. It predicts risk categories like hypertension risk, diabetes risk, cardiac risk, and respiratory risk.

## Q28. Which inputs are used for AI risk prediction?

The inputs are:

- Age
- Systolic BP
- Diastolic BP
- Heart rate
- SpO2
- Glucose
- Temperature
- Respiratory rate
- Recent diagnosis history

## Q29. What is the output of AI risk prediction?

The output includes:

- Risk score
- Risk level
- Predicted disease risks
- Risk factors
- Recommendation

## Q30. What are the risk levels?

The risk levels are:

- Low
- Moderate
- High
- Critical

## Q31. How is AI risk useful for doctors?

It helps doctors quickly identify high-risk patients. Instead of checking every record manually, doctors can see the risk score and priority alerts on the dashboard.

## Q32. What are priority alerts?

Priority alerts are generated when a patient has high or critical risk. They help doctors focus on patients who need urgent care.

## Q33. What is the smart dashboard?

The smart dashboard shows total patients, total records, biometric count, open alerts, risk distribution, priority patients, recent activities, and integrity status.

## Q34. Why is dashboard important?

The dashboard gives doctors a quick overview of patient risk and hospital activity. It saves time and helps in better decision-making.

## Q35. What is the emergency scan module?

Emergency scan is a separate module where staff can upload patient face or fingerprint in emergency cases. If a match is found, the system shows critical treatment information immediately.

## Q36. What information is shown in emergency scan result?

It shows:

- Patient photo
- Patient name and code
- Blood group
- Allergies
- Emergency contact
- Latest vitals
- Latest diagnosis
- AI risk score
- Open alerts
- Family alert option
- ICU handover print option

## Q37. Why is emergency scan useful?

It is useful when a patient is unconscious or unable to speak. Doctors can quickly know allergies, blood group, and health risk before starting treatment.

## Q38. What is the family alert module?

The family alert module generates and logs an emergency message for the patient's emergency contact. It is useful to inform family members during accident or ICU cases.

## Q39. Does the family alert send real SMS?

In this academic project, it works in demo mode and logs the message as sent. In future, it can be connected with SMS gateway, WhatsApp API, or email service.

## Q40. What is ICU handover print?

ICU handover print is a printable emergency summary containing patient details, allergies, blood group, vitals, diagnosis, and risk score. It can be handed over to ICU staff.

## Q41. What is blockchain-style integrity chain?

It is a hash-based integrity system. Important events are stored as linked blocks. Each block contains data hash, previous hash, and block hash. If data is changed manually, the chain verification detects mismatch.

## Q42. Is it a real cryptocurrency blockchain?

No. It is not a cryptocurrency blockchain. It is a blockchain-style hash chain used for tamper detection in healthcare records.

## Q43. Which hashing algorithm is used?

The project uses **SHA-256 hashing**.

## Q44. What is SHA-256?

SHA-256 is a cryptographic hash algorithm. It converts data into a fixed-length hash value. If the input data changes even slightly, the hash also changes.

## Q45. Which events are stored in the integrity chain?

Events include:

- Patient registration
- Biometric enrollment
- Biometric match
- Emergency lookup
- Health metric capture
- Medical record addition
- AI risk assessment
- Family alert sent
- Alert resolution

## Q46. What is audit log?

Audit log stores user activities such as login, patient registration, biometric match, emergency scan, and family alert. It helps track who performed which action and when.

## Q47. Difference between audit log and integrity chain?

Audit log records activities for tracking. Integrity chain verifies whether important data has been tampered with using hash verification.

## Q48. How is security handled in your project?

Security is handled using:

- Login authentication
- Password hashing
- Role-based access control
- Encrypted biometric storage
- Protected patient photo route
- Audit logs
- Integrity chain

## Q49. What is password hashing?

Password hashing means storing passwords in encrypted hash form instead of plain text. In this project, Werkzeug password hashing is used.

## Q50. Why did you not store passwords directly?

Storing plain passwords is unsafe. If database is leaked, user passwords can be exposed. Hashing improves password security.

## Q51. What is Jinja template?

Jinja is the template engine used by Flask. It helps display dynamic data from backend to frontend HTML pages.

## Q52. Where is frontend written?

Frontend is written in HTML templates inside the `templates` folder and CSS inside the `static/css/style.css` file.

## Q53. What is the use of CSS?

CSS is used for designing the user interface, dashboard layout, forms, buttons, panels, patient cards, alerts, and emergency scan screen.

## Q54. Which file is the main backend file?

The main backend file is `app.py`. It contains Flask routes, database initialization, registration logic, login logic, dashboard logic, emergency scan, family alert, and patient management.

## Q55. Which file handles biometric logic?

`biometric_engine.py` handles encryption, decryption, image reading, face processing, fingerprint processing, and biometric matching.

## Q56. Which file handles AI logic?

`ai_risk_engine.py` handles AI risk score calculation, disease-risk probability, risk level, and recommendation.

## Q57. Which file handles integrity chain?

`integrity_chain.py` handles blockchain-style block creation and verification.

## Q58. What is patient code?

Patient code is a unique ID generated for every patient, such as `PAT-20260429-ABC123`. It helps identify patients internally.

## Q59. What is session used for?

Session stores logged-in user information and verified patient ID. It helps maintain login state and access control.

## Q60. What are decorators in Flask?

Decorators are used to attach routes or security checks to functions. For example, `@app.route` defines URL routes, and `@login_required` protects pages from unauthorized access.

## Q61. What is route in Flask?

A route is a URL endpoint connected to a Python function. For example, `/dashboard` displays the dashboard, and `/patients/register` displays patient registration page.

## Q62. What are GET and POST methods?

GET is used to display pages or fetch data. POST is used to submit form data, such as login form, patient registration form, biometric scan form, and family alert form.

## Q63. How is patient registration flow working?

Receptionist or doctor fills patient details, uploads patient photo, face image, fingerprint image, and vitals. The system stores patient details, saves photo, encrypts biometrics, records vitals, generates AI risk assessment, and adds integrity events.

## Q64. How is biometric retrieval flow working?

Staff uploads face or fingerprint image. The system reads the image, fetches stored biometric templates, decrypts templates, compares images, calculates score, and opens the matching patient profile.

## Q65. How is emergency scan flow working?

Staff uploads face or fingerprint in emergency scan. If a match is found, the system loads emergency snapshot with allergies, blood group, vitals, diagnosis, AI risk score, and family alert option.

## Q66. What is the use of encrypted biometric templates?

Encrypted templates protect sensitive biometric files. Even if someone accesses the storage folder, they cannot directly view the biometric images without the key.

## Q67. What is the limitation of this project?

This is an academic prototype. It uses uploaded face/fingerprint images instead of real biometric scanner hardware. The AI model is rule-based and not medically certified. Family alert is demo mode, not real SMS.

## Q68. What future improvements can be added?

Future improvements include:

- Real fingerprint scanner integration
- Live camera face recognition
- Real SMS/WhatsApp alert
- Cloud deployment
- PostgreSQL or MySQL database
- Advanced machine learning model
- Doctor appointment module
- Patient mobile app
- FHIR healthcare standard support

## Q69. Why is this project suitable for MCA final year?

It is suitable because it combines web development, database design, authentication, image processing, AI prediction, security, emergency workflow, dashboard analytics, and integrity verification. It is more advanced than a simple CRUD project.

## Q70. What makes your project advanced?

The advanced features are:

- Face and fingerprint biometric retrieval
- AI risk prediction
- Smart doctor dashboard
- Emergency scan module
- Family alert workflow
- Patient photo support
- Encrypted biometric storage
- Blockchain-style integrity chain
- Role-based access control

---

# Technology Summary for Viva

## Python

Python is used as the main backend language. It is used for Flask routes, database operations, AI risk logic, biometric image processing, and integrity chain.

## Flask

Flask is used to build the web application. It handles routing, templates, forms, session, login, and backend workflow.

## SQLite

SQLite is used as the database. It stores patient records, users, biometrics metadata, medical records, health metrics, risk assessments, alerts, audit logs, and integrity chain.

## OpenCV

OpenCV is used for face and fingerprint image processing. It helps in reading images, converting to grayscale, detecting face region, resizing, feature matching, and similarity scoring.

## NumPy

NumPy is used for array operations because images are processed as arrays in OpenCV.

## HTML and CSS

HTML and CSS are used for frontend pages, forms, dashboard, patient profile, emergency scan screen, and styling.

## Jinja

Jinja is Flask's template engine. It is used to display dynamic data such as patient name, vitals, alerts, and risk score in HTML.

## SHA-256

SHA-256 is used for blockchain-style integrity chain hashing. It helps detect tampering in important event logs.

## Werkzeug Security

Werkzeug is used for password hashing and password verification during login.

---

# Database Explanation for Viva

## Why SQLite?

SQLite is easy to set up and does not need a separate server. For a final-year project demo, it is simple and portable. All data is stored in one local database file.

## Database Use

The database is used to store patient information, biometric metadata, medical records, health vitals, risk prediction results, priority alerts, emergency alerts, audit logs, and integrity chain blocks.

## Main Tables

`users`: Stores login users and roles.

`patients`: Stores patient profile, blood group, allergies, emergency contact, and photo path.

`biometrics`: Stores biometric type and encrypted file path.

`health_metrics`: Stores vitals like BP, heart rate, SpO2, glucose, temperature, and respiratory rate.

`medical_records`: Stores diagnosis, prescription, and doctor notes.

`risk_assessments`: Stores AI risk score, risk level, predicted diseases, and recommendation.

`priority_alerts`: Stores high-risk and critical-risk alerts.

`emergency_notifications`: Stores family alert message history.

`audit_logs`: Stores user activity logs.

`integrity_chain`: Stores hash-linked blocks for tamper detection.

---

# Final Viva Closing Statement

In conclusion, my project is not only a patient record system. It is an intelligent healthcare support system that combines biometric identification, AI risk prediction, emergency care workflow, family alert, and data integrity. It can help hospital staff retrieve patient records faster, especially in emergency situations, and it demonstrates multiple MCA-level concepts in one practical application.

