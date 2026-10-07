from datetime import datetime, UTC

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Certificate, GenerationJob
from app.services.certificate_generator import generate_certificate


def _process_certificate_job(
    job_id: str,
    db: Session,
) -> None:
    """
    Process all certificates belonging to a job.

    Each certificate is processed independently so that
    one failure does not stop the remaining certificates.
    """

    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if not job:
        return

    job.status = "PROCESSING"
    db.commit()

    certificates = db.query(Certificate).filter(
        Certificate.job_id == job_id
    ).all()

    for certificate in certificates:
        certificate.status = "PROCESSING"
        db.commit()

        try:
            file_path = generate_certificate(
                certificate_id=certificate.id,
                recipient_name=certificate.recipient_name,
                event_name=job.event_name,
                certificate_title=job.certificate_title,
            )

            certificate.status = "SUCCESS"
            certificate.file_path = file_path
            certificate.completed_at = datetime.now(UTC)

            job.success_count += 1

        except Exception as exc:
            certificate.status = "FAILED"
            certificate.error_message = str(exc)
            certificate.completed_at = datetime.now(UTC)

            job.failed_count += 1

        db.commit()

    if job.failed_count == 0:
        job.status = "COMPLETED"
    else:
        job.status = "COMPLETED_WITH_ERRORS"

    job.completed_at = datetime.now(UTC)

    db.commit()


def process_certificate_job(job_id: str) -> None:
    """
    Entry point used by FastAPI background processing.

    Creates its own database session because the HTTP request
    session should not be reused by the background task.
    """

    db = SessionLocal()

    try:
        _process_certificate_job(job_id, db)
    finally:
        db.close()