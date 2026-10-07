from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Certificate, GenerationJob
from app.schemas import (
    CertificateJobCreate,
    CertificateJobResponse,
    CertificateJobStatusResponse,
)
from app.services.job_processor import process_certificate_job


router = APIRouter(
    prefix="/api/v1/certificate-jobs",
    tags=["Certificate Jobs"],
)


@router.post(
    "",
    response_model=CertificateJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_certificate_job(
    request: CertificateJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Create the generation job
    job = GenerationJob(
        event_name=request.event_name,
        certificate_title=request.certificate_title,
        status="PENDING",
        total_count=len(request.recipients),
        success_count=0,
        failed_count=0,
    )

    db.add(job)
    db.flush()

    # Create certificate records
    for recipient in request.recipients:
        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status="PENDING",
        )

        db.add(certificate)

    db.commit()
    db.refresh(job)

    # Start background processing
    background_tasks.add_task(
        process_certificate_job,
        job.id,
    )

    return job


@router.get(
    "/{job_id}",
    response_model=CertificateJobStatusResponse,
)
def get_certificate_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Certificate job not found",
        )

    completed_count = job.success_count + job.failed_count

    if job.total_count > 0:
        progress_percentage = (
            completed_count / job.total_count
        ) * 100
    else:
        progress_percentage = 0

    return {
        "id": job.id,
        "event_name": job.event_name,
        "certificate_title": job.certificate_title,
        "status": job.status,
        "total_count": job.total_count,
        "success_count": job.success_count,
        "failed_count": job.failed_count,
        "progress_percentage": progress_percentage,
        "certificates": job.certificates,
    }