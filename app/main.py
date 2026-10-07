
from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routes.jobs import router as jobs_router
from app.routes.certificates import router as certificates_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator",
    description="API for bulk certificate generation",
    version="1.0.0",
)

app.include_router(jobs_router)
app.include_router(certificates_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
