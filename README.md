# Bulk Certificate Generator

A backend service built with **FastAPI** for generating certificates in bulk from a predefined certificate template.

The system accepts a list of recipients, creates a certificate generation job, processes certificates in the background, tracks individual certificate status and overall job progress, and provides an API to download successfully generated certificates.

## Features

- Bulk certificate generation
- Recipient name and email validation
- Background job processing
- Job status tracking
- Real-time progress calculation
- Individual certificate status tracking
- Failure isolation — one failed certificate does not stop the remaining certificates
- PDF certificate generation
- Certificate download API
- Relational database using SQLite and SQLAlchemy
- Automated tests using pytest
- Interactive API documentation through Swagger UI

## Tech Stack

- **Python 3.14**
- **FastAPI** — REST API framework
- **SQLAlchemy** — ORM and database access
- **SQLite** — relational database
- **Pydantic** — request validation
- **ReportLab** — PDF generation
- **Pytest** — automated testing
- **Uvicorn** — ASGI server

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── jobs.py
│   │   └── certificates.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── certificate_generator.py
│       └── job_processor.py
│
├── tests/
│   ├── conftest.py
│   ├── test_certificates.py
│   ├── test_failure.py
│   ├── test_generation.py
│   └── test_jobs.py
│
├── generated_certificates/
├── certificates.db
├── pytest.ini
├── requirements.txt
├── .gitignore
└── README.md
```

## Architecture

```text
Client
  │
  ▼
FastAPI Routes
  │
  ├── Request Validation
  │
  ▼
Job Creation
  │
  ├── GenerationJob
  └── Certificate records
  │
  ▼
Background Task
  │
  ▼
Job Processor
  │
  ├── Generate PDF
  ├── Update certificate status
  ├── Record failures
  └── Update job progress
  │
  ▼
SQLite Database
  │
  ▼
Certificate Download API
```

## Database Design

The application uses two main tables.

### GenerationJob

Stores information about the overall bulk generation request.

Important fields:

- `id`
- `event_name`
- `certificate_title`
- `status`
- `total_count`
- `success_count`
- `failed_count`
- `created_at`
- `completed_at`

### Certificate

Stores the status and output information for each recipient.

Important fields:

- `id`
- `job_id`
- `recipient_name`
- `recipient_email`
- `status`
- `file_path`
- `error_message`
- `created_at`
- `completed_at`

Relationship:

```text
GenerationJob 1 ─────────── N Certificate
```

A single generation job can contain many certificates.

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd bulk-certificate-generator
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## Run the Application

Start the development server:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Swagger UI:

`http://127.0.0.1:8000/docs`

ReDoc:

`http://127.0.0.1:8000/redoc`

## API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

### Create Certificate Generation Job

```http
POST /api/v1/certificate-jobs
```

Example request:

```json
{
  "event_name": "Python Workshop 2026",
  "certificate_title": "Certificate of Completion",
  "recipients": [
    {
      "name": "Rahul Sharma",
      "email": "rahul@example.com"
    },
    {
      "name": "Priya Patil",
      "email": "priya@example.com"
    },
    {
      "name": "Amit Joshi",
      "email": "amit@example.com"
    }
  ]
}
```

Example response:

```json
{
  "id": "job-uuid",
  "event_name": "Python Workshop 2026",
  "certificate_title": "Certificate of Completion",
  "status": "PENDING",
  "total_count": 3,
  "success_count": 0,
  "failed_count": 0
}
```

The job is processed in the background after the request is accepted.

### Get Job Status

```http
GET /api/v1/certificate-jobs/{job_id}
```

Example response:

```json
{
  "id": "job-uuid",
  "event_name": "Python Workshop 2026",
  "certificate_title": "Certificate of Completion",
  "status": "COMPLETED",
  "total_count": 3,
  "success_count": 3,
  "failed_count": 0,
  "progress_percentage": 100.0,
  "certificates": [
    {
      "id": "certificate-uuid",
      "recipient_name": "Rahul Sharma",
      "recipient_email": "rahul@example.com",
      "status": "SUCCESS",
      "file_path": "generated_certificates/certificate-uuid.pdf",
      "error_message": null
    }
  ]
}
```

Possible job statuses:

- `PENDING`
- `PROCESSING`
- `COMPLETED`
- `COMPLETED_WITH_ERRORS`

Possible certificate statuses:

- `PENDING`
- `PROCESSING`
- `SUCCESS`
- `FAILED`

### Download Certificate

```http
GET /api/v1/certificates/{certificate_id}
```

A successfully generated certificate is returned as a PDF file.

If the certificate is not available yet, the API returns an appropriate error response.

## Failure Isolation

Each certificate is processed independently.

For example, if a job contains 100 recipients and one certificate fails:

```text
Total:     100
Success:    99
Failed:      1
```

The remaining 99 certificates continue processing.

The job is marked:

```text
COMPLETED_WITH_ERRORS
```

This prevents a single certificate-generation problem from stopping the entire bulk operation.

## Validation

The API validates:

- Recipient name length
- Recipient email format
- Event name length
- Certificate title length
- At least one recipient
- Maximum recipient count

Invalid requests are rejected before certificate processing starts.

## Testing

Run all tests:

```powershell
pytest
```

The project contains tests covering:

- PDF certificate generation
- Certificate download
- Bulk job creation
- Input validation
- Empty recipient validation
- Job status retrieval
- Missing job handling
- Individual certificate failure isolation

Current test result:

```text
8 passed
```

## Design Decisions

### Why FastAPI?

FastAPI provides request validation through Pydantic, automatic OpenAPI documentation, simple REST API development, and background task integration.

### Why SQLite?

SQLite keeps the project simple and requires no separate database server while still providing a relational database.

For production deployment, PostgreSQL would be a more appropriate choice.

### Why SQLAlchemy?

SQLAlchemy provides a clean ORM layer and keeps database operations separated from API logic.

### Why BackgroundTasks?

The assignment requires background processing but does not require a distributed job queue.

FastAPI `BackgroundTasks` is sufficient for this implementation.

For a production system with large workloads, a distributed task queue such as Celery or RQ with Redis/RabbitMQ would be more appropriate.

### Why ReportLab?

ReportLab provides programmatic PDF generation using Python and allows the certificate layout to remain consistent for every recipient.

### Why UUIDs?

UUIDs are used for jobs and certificates to provide unique identifiers and avoid filename collisions.

## Production Considerations

For a production-scale implementation, the following improvements could be made:

- PostgreSQL instead of SQLite
- Celery/RQ with Redis or RabbitMQ for durable background jobs
- Object storage such as S3 for generated certificates
- Authentication and authorization
- API rate limiting
- Retry policies for transient failures
- Structured application logging
- Monitoring and metrics
- Database migrations using Alembic
- Multiple application workers
- Distributed processing for very large batches

The current implementation intentionally keeps the architecture simple and focused on the assignment requirements.

## License

This project was developed as a technical assignment.
