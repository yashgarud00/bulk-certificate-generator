from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RecipientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class CertificateJobCreate(BaseModel):
    event_name: str = Field(min_length=2, max_length=200)
    certificate_title: str = Field(min_length=2, max_length=200)
    recipients: list[RecipientCreate] = Field(
        min_length=1,
        max_length=1000,
    )


class CertificateJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_name: str
    certificate_title: str
    status: str
    total_count: int
    success_count: int
    failed_count: int


class CertificateStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recipient_name: str
    recipient_email: str
    status: str
    file_path: str | None = None
    error_message: str | None = None


class CertificateJobStatusResponse(BaseModel):
    id: str
    event_name: str
    certificate_title: str
    status: str
    total_count: int
    success_count: int
    failed_count: int
    progress_percentage: float
    certificates: list[CertificateStatusResponse]