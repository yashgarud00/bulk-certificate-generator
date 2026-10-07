from app.models import Certificate, GenerationJob


def test_download_certificate(
    client,
    db_session,
    tmp_path,
    monkeypatch,
):
    job = GenerationJob(
        event_name="Python Workshop 2026",
        certificate_title="Certificate of Completion",
        status="COMPLETED",
        total_count=1,
        success_count=1,
        failed_count=0,
    )

    db_session.add(job)
    db_session.flush()

    certificate = Certificate(
        job_id=job.id,
        recipient_name="Rahul Sharma",
        recipient_email="rahul@example.com",
        status="SUCCESS",
        file_path="test.pdf",
    )

    db_session.add(certificate)
    db_session.commit()
    db_session.refresh(certificate)

    pdf_file = tmp_path / f"{certificate.id}.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 test certificate")

    monkeypatch.setattr(
        "app.routes.certificates.CERTIFICATE_DIR",
        tmp_path,
    )

    response = client.get(
        f"/api/v1/certificates/{certificate.id}"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content == b"%PDF-1.4 test certificate"