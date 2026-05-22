# MedSync

**A healthcare coordination backend for patients, doctors, and hospitals.**

MedSync is a Django REST Framework API built around a real clinical workflow: hospitals onboard patients, assign doctors, doctors manage diagnosis cases and visits, and patients can track their medical history and scheduled appointments. The project focuses on role-aware access, structured medical records, secure JWT-based APIs, document handling, and deployment-ready infrastructure.

This is not a generic CRUD demo or an ecommerce-style catalog. It models a domain where authorization, data relationships, and workflow boundaries matter.

## Why This Project Stands Out

- **Role-based healthcare workflows** for patients, doctors, and hospitals.
- **Custom Django user model** with domain-specific roles instead of bolted-on profile flags.
- **JWT authentication** using access and refresh tokens for API-first clients.
- **Patient-doctor assignment rules** so doctors can only access patients assigned to them.
- **Diagnosis case management** with visit history, notes, medications, and uploaded documents.
- **Hospital-controlled patient and doctor lists** for real-world administrative flows.
- **Appointment scheduling and reminders** with email notification logic.
- **Cloudinary integration** for storing medical documents externally.
- **Dockerized PostgreSQL setup** for a closer-to-production local environment.

## Core Idea

In many healthcare systems, patient data is fragmented across hospitals, doctors, and visit records. MedSync centralizes that workflow into a structured backend where:

1. A patient creates and maintains their profile.
2. A hospital registers patients into its recent patient list.
3. A hospital assigns doctors to patients.
4. Assigned doctors create diagnosis cases and visit records.
5. Visit documents, medications, notes, and follow-up schedules stay linked to the patient journey.

The result is a backend that demonstrates more than endpoint creation: it shows how to design API boundaries around trust, ownership, and domain behavior.

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Backend | Django 5, Django REST Framework |
| Authentication | Simple JWT, Django custom user model |
| Database | PostgreSQL, Django ORM |
| File Storage | Cloudinary |
| Async / Background-ready Work | Celery-style task structure for appointment reminders |
| Email | Django SMTP email backend |
| DevOps | Docker, Docker Compose |
| API Style | RESTful endpoints with serializer-driven validation |
| Language | Python 3.12 |

## Main Modules

```text
MedSync
├── users/       # Authentication, user roles, patient/doctor/hospital profiles
├── medical/     # Diagnosis cases, visits, documents, scheduling, assignments
├── hospitals/   # Hospital app boundary for future hospital-specific expansion
├── config/      # Django project settings and root URL configuration
└── docker-compose.yml
```

## Key Features

### Authentication and Roles

MedSync uses a custom `CustomUser` model with three explicit roles:

- `PATIENT`
- `DOCTOR`
- `HOSPITAL`

Each role unlocks different API behavior. For example, hospitals can assign doctors, doctors can access only assigned patients, and patients can view their own records.

### Patient Profile Management

Patients can maintain medical profile details such as:

- Blood group
- Height and weight
- Date of birth
- Existing conditions
- Allergies

This gives the system a healthcare-specific data layer rather than a generic user profile.

### Hospital Workflow

Hospitals can:

- Register hospital accounts
- Create hospital profiles
- Add recent patients
- Add doctors to the hospital
- Assign doctors to patients
- View patient profiles and diagnosis history

### Doctor Workflow

Doctors can:

- Register with specialization and license number
- View assigned patients
- Access assigned patient profiles
- Create diagnosis cases
- Add visit records
- Add notes, medications, and documents
- Schedule patient visits

### Diagnosis and Visit Records

The medical module models the patient journey through:

- `DiagnosisCase`
- `DiagnosisVisit`
- `VisitDocument`
- `ScheduledVisit`
- `AssignedDoctor`

This keeps medical history organized by case, with multiple visits and documents attached to each case.

### Appointment Reminders

Scheduled visits include reminder logic that prepares patient email notifications before appointments. The project includes a Celery-style task function, making it ready to evolve into a fully asynchronous reminder pipeline.

### Document Handling

Doctor visit creation supports document uploads and stores file URLs through Cloudinary. This is useful for prescriptions, reports, scans, and other visit-related files.

## API Capabilities

The API supports registration, JWT login, profile management, hospital-patient linking, doctor assignment, diagnosis tracking, visit documentation, medical document uploads, and scheduled appointment reminders.

Instead of exposing every route in the README, the project keeps the focus on the backend design: role-specific access, serializer-level validation, relational medical records, and workflow-driven endpoints.

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd MedSync
```

### 2. Run with Docker

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:9000
```

PostgreSQL runs inside Docker, and pgAdmin is exposed at:

```text
http://localhost:8080
```

### 3. Run locally without Docker

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Environment Variables

For production or shared environments, move secrets and service credentials into environment variables:

```env
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

## Engineering Decisions

- **Custom user model early:** avoids painful migrations later and keeps role behavior central.
- **Serializer-driven validation:** keeps request validation close to API boundaries.
- **Explicit permission checks:** views enforce domain rules such as doctor-patient assignment.
- **Relational modeling:** diagnosis cases, visits, doctors, hospitals, and patients are represented as connected entities instead of flat records.
- **Dockerized database:** local development uses PostgreSQL instead of relying only on SQLite.
- **External document storage:** medical files are represented by URLs after upload, keeping the API database lean.

## What I Would Improve Next

- Add automated API tests for role-based access rules.
- Move secrets from settings into environment variables.
- Enable true Celery workers and broker-backed delayed reminders.
- Add OpenAPI/Swagger documentation.
- Add stricter file validation for medical document uploads.
- Introduce audit logs for sensitive medical record access.
- Add pagination and filtering for long diagnosis histories.

## Project Snapshot

MedSync demonstrates backend engineering through a practical healthcare domain:

- secure API authentication,
- role-aware authorization,
- normalized domain models,
- workflow-focused endpoint design,
- cloud document storage,
- email notification logic,
- and containerized infrastructure.

