from pathlib import Path

from app.services.certificate_generator import generate_certificate


def test_generate_certificate(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.services.certificate_generator.OUTPUT_DIR",
        tmp_path,
    )

    certificate_id = "test-certificate-123"

    file_path = generate_certificate(
        certificate_id=certificate_id,
        recipient_name="Rahul Sharma",
        event_name="Python Workshop 2026",
        certificate_title="Certificate of Completion",
    )

    path = Path(file_path)

    assert path.exists()
    assert path.suffix == ".pdf"
    assert path.stat().st_size > 0