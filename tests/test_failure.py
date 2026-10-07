from app.models import Certificate, GenerationJob
from app.services import job_processor


def test_one_certificate_failure_does_not_stop_job(
    db_session,
    monkeypatch,
):
    job = GenerationJob(
        event_name="Python Workshop 2026",
        certificate_title="Certificate of Completion",
        status="PENDING",
        total_count=3,
        success_count=0,
        failed_count=0,
    )

    db_session.add(job)
    db_session.flush()

    certificates = [
        Certificate(
            job_id=job.id,
            recipient_name="Rahul Sharma",
            recipient_email="rahul@example.com",
            status="PENDING",
        ),
        Certificate(
            job_id=job.id,
            recipient_name="Priya Patil",
            recipient_email="priya@example.com",
            status="PENDING",
        ),
        Certificate(
            job_id=job.id,
            recipient_name="Amit Joshi",
            recipient_email="amit@example.com",
            status="PENDING",
        ),
    ]

    db_session.add_all(certificates)
    db_session.commit()

    def mock_generate_certificate(
        certificate_id,
        recipient_name,
        event_name,
        certificate_title,
    ):
        if recipient_name == "Priya Patil":
            raise RuntimeError("Simulated certificate generation failure")

        return f"generated_certificates/{certificate_id}.pdf"

    monkeypatch.setattr(
        job_processor,
        "generate_certificate",
        mock_generate_certificate,
    )

    job_processor._process_certificate_job(
    job.id,
    db_session,
    )

    db_session.refresh(job)

    assert job.status == "COMPLETED_WITH_ERRORS"
    assert job.success_count == 2
    assert job.failed_count == 1

    results = db_session.query(Certificate).filter(
        Certificate.job_id == job.id
    ).all()

    statuses = {
        certificate.recipient_name: certificate.status
        for certificate in results
    }

    assert statuses["Rahul Sharma"] == "SUCCESS"
    assert statuses["Priya Patil"] == "FAILED"
    assert statuses["Amit Joshi"] == "SUCCESS"