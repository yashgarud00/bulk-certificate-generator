import uuid
from datetime import datetime, UTC

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    event_name = Column(String(200), nullable=False)
    certificate_title = Column(String(200), nullable=False)

    status = Column(String(30), nullable=False, default="PENDING")

    total_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failed_count = Column(Integer, nullable=False, default=0)

    created_at = Column(
    DateTime,
    default=lambda: datetime.now(UTC),
    )
    completed_at = Column(DateTime, nullable=True)

    certificates = relationship(
        "Certificate",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    job_id = Column(
        String(36),
        ForeignKey("generation_jobs.id"),
        nullable=False,
    )

    recipient_name = Column(String(100), nullable=False)
    recipient_email = Column(String(255), nullable=False)

    status = Column(String(30), nullable=False, default="PENDING")

    file_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
    )
    completed_at = Column(DateTime, nullable=True)

    job = relationship(
        "GenerationJob",
        back_populates="certificates",
    )