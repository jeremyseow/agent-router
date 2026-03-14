from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, BackgroundTasks
from typing import List
from models.api import IngestionJobStatus, IngestResponse
from core.knowledge_base import (
    ingest_document_content, 
    process_ingestion_job, 
    create_ingestion_job, 
    get_existing_job,
    get_job_status
)
from core.constants import (
    MAX_INGEST_FILES, 
    SUPPORTED_INGEST_EXTENSIONS,
    IngestionStatus
)
import logfire
import os

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_files(
    background_tasks: BackgroundTasks,
    request: Request,
    files: list[UploadFile] = File(..., description="Up to 5 documents to ingest"),
    overwrite: bool = Form(False)
):
    """
    Ingests up to 5 documents into the knowledge base asynchronously.
    Returns a list of job IDs for tracking.
    Supported formats: .md, .pdf, .csv, .yaml, .yml
    """
    if len(files) > MAX_INGEST_FILES:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_INGEST_FILES} files allowed per request.")

    db_pool = request.app.state.pool
    results = []    

    for file in files:
        # Perform basic extension validation
        _, ext = os.path.splitext(file.filename.lower())
        if ext not in SUPPORTED_INGEST_EXTENSIONS:
            results.append({
                "document": file.filename,
                "status": "error",
                "message": f"Unsupported file type: {ext}"
            })
            continue
            
        try:
            # Check for existing jobs
            existing_job = await get_existing_job(db_pool, file.filename)
            
            # If the file has already been submitted, or has completed and we do not wish to overwrite, we should skip it
            if existing_job:
                status = existing_job["status"]
                if status in (IngestionStatus.PENDING, IngestionStatus.PROCESSING):
                    logfire.info(f"Job already in progress for {file.filename}: {existing_job['job_id']}")
                elif status == IngestionStatus.COMPLETED and not overwrite:
                    logfire.info(f"Document {file.filename} already ingested, skipping.")
                
                results.append({"document": file.filename, "job_id": existing_job["job_id"], "status": status})
                continue

            # Create new job
            job_id = await create_ingestion_job(db_pool, file.filename)
            content = await file.read()
            
            background_tasks.add_task(
                process_ingestion_job,
                pool=db_pool,
                job_id=job_id,
                document_name=file.filename,
                content_bytes=content,
                overwrite=overwrite
            )
            
            results.append({
                "document": file.filename,
                "job_id": job_id,
                "status": IngestionStatus.PENDING
            })
        except Exception as e:
            logfire.error(f"Error initiating ingestion for {file.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Error initiating ingestion for {file.filename}")
            
    return IngestResponse(results=results)

@router.get("/ingest/status/{job_id}", response_model=IngestionJobStatus)
async def get_ingestion_status(job_id: str, request: Request):
    """Retrieves the current status of an ingestion job including filename and timestamps."""
    db_pool = request.app.state.pool
    status = await get_job_status(db_pool, job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status
