def test_create_certificate_job(client):
    response = client.post(
        "/api/v1/certificate-jobs",
        json={
            "event_name": "Python Workshop 2026",
            "certificate_title": "Certificate of Completion",
            "recipients": [
                {
                    "name": "Rahul Sharma",
                    "email": "rahul@example.com",
                },
                {
                    "name": "Priya Patil",
                    "email": "priya@example.com",
                },
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event_name"] == "Python Workshop 2026"
    assert data["certificate_title"] == "Certificate of Completion"
    assert data["status"] == "PENDING"
    assert data["total_count"] == 2
    assert data["success_count"] == 0
    assert data["failed_count"] == 0
    assert data["id"]

def test_invalid_recipient_data(client):
    response = client.post(
        "/api/v1/certificate-jobs",
        json={
            "event_name": "Python Workshop 2026",
            "certificate_title": "Certificate of Completion",
            "recipients": [
                {
                    "name": "A",
                    "email": "invalid-email",
                }
            ],
        },
    )

    assert response.status_code == 422

def test_empty_recipients(client):
    response = client.post(
        "/api/v1/certificate-jobs",
        json={
            "event_name": "Python Workshop 2026",
            "certificate_title": "Certificate of Completion",
            "recipients": [],
        },
    )

    assert response.status_code == 422

def test_get_certificate_job_status(client, db_session):
    from app.models import Certificate, GenerationJob

    job = GenerationJob(
        event_name="Python Workshop 2026",
        certificate_title="Certificate of Completion",
        status="COMPLETED",
        total_count=2,
        success_count=2,
        failed_count=0,
    )

    db_session.add(job)
    db_session.flush()

    certificates = [
        Certificate(
            job_id=job.id,
            recipient_name="Rahul Sharma",
            recipient_email="rahul@example.com",
            status="SUCCESS",
            file_path=f"generated_certificates/{job.id}-1.pdf",
        ),
        Certificate(
            job_id=job.id,
            recipient_name="Priya Patil",
            recipient_email="priya@example.com",
            status="SUCCESS",
            file_path=f"generated_certificates/{job.id}-2.pdf",
        ),
    ]

    db_session.add_all(certificates)
    db_session.commit()

    response = client.get(
        f"/api/v1/certificate-jobs/{job.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "COMPLETED"
    assert data["total_count"] == 2
    assert data["success_count"] == 2
    assert data["failed_count"] == 0
    assert data["progress_percentage"] == 100.0
    assert len(data["certificates"]) == 2

def test_get_nonexistent_certificate_job(client):
    response = client.get(
        "/api/v1/certificate-jobs/"
        "00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Certificate job not found"