
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Certificate

CERTIFICATE_DIR = Path("generated_certificates")


router = APIRouter(
    prefix="/api/v1/certificates",
    tags=["Certificates"],
)


@router.get("/{certificate_id}")
def download_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
):
    certificate = db.query(Certificate).filter(
        Certificate.id == certificate_id
    ).first()

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found",
        )

    if certificate.status != "SUCCESS" or not certificate.file_path:
        raise HTTPException(
            status_code=409,
            detail="Certificate is not available for download",
        )

    # Build the path from the trusted certificate ID
    # rather than accepting an arbitrary client file path.
    '''project_root = Path(__file__).resolve().parents[2]
    file_path = (
        project_root
        / "generated_certificates"
        / f"{certificate.id}.pdf"
    )'''

    file_path = CERTIFICATE_DIR / f"{certificate.id}.pdf"

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Certificate PDF file not found",
        )

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf",
    )
