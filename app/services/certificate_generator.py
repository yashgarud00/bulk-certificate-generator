from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path("generated_certificates")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_certificate(
    certificate_id: str,
    recipient_name: str,
    event_name: str,
    certificate_title: str,
) -> str:
    """
    Generate a certificate PDF and return its file path.
    """

    file_path = OUTPUT_DIR / f"{certificate_id}.pdf"

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        str(file_path),
        pagesize=(page_width, page_height),
    )

    # Outer border
    pdf.setLineWidth(3)
    pdf.rect(
        15 * mm,
        15 * mm,
        page_width - 30 * mm,
        page_height - 30 * mm,
    )

    # Certificate title
    pdf.setFont("Helvetica-Bold", 28)

    title_width = pdf.stringWidth(
        certificate_title,
        "Helvetica-Bold",
        28,
    )

    pdf.drawString(
        (page_width - title_width) / 2,
        page_height - 60 * mm,
        certificate_title,
    )

    # Introductory text
    pdf.setFont("Helvetica", 16)

    text = "This is to certify that"

    text_width = pdf.stringWidth(
        text,
        "Helvetica",
        16,
    )

    pdf.drawString(
        (page_width - text_width) / 2,
        page_height - 85 * mm,
        text,
    )

    # Recipient name
    pdf.setFont("Helvetica-Bold", 26)

    name_width = pdf.stringWidth(
        recipient_name,
        "Helvetica-Bold",
        26,
    )

    pdf.drawString(
        (page_width - name_width) / 2,
        page_height - 110 * mm,
        recipient_name,
    )

    # Event information
    pdf.setFont("Helvetica", 16)

    event_text = f"has successfully completed {event_name}"

    event_width = pdf.stringWidth(
        event_text,
        "Helvetica",
        16,
    )

    pdf.drawString(
        (page_width - event_width) / 2,
        page_height - 135 * mm,
        event_text,
    )

    # Date
    date_text = datetime.now().strftime("%d %B %Y")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        35 * mm,
        30 * mm,
        f"Date: {date_text}",
    )

    # Certificate ID
    pdf.drawRightString(
        page_width - 35 * mm,
        30 * mm,
        f"Certificate ID: {certificate_id}",
    )

    pdf.save()

    return str(file_path)