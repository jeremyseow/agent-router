from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from typing import List
from core.knowledge_base import ingest_document_content
from core.constants import MAX_INGEST_FILES, SUPPORTED_INGEST_EXTENSIONS
import logfire
import os

router = APIRouter()

@router.post("/ingest")
async def ingest_files(
    files: list[UploadFile] = File(..., description="Up to 5 documents to ingest"),
    overwrite: bool = Form(False),
    request: Request = None
):
    """
    Ingests up to 5 documents into the knowledge base.
    Supported formats: .md, .pdf, .csv, .yaml, .yml
    """
    if len(files) > MAX_INGEST_FILES:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_INGEST_FILES} files allowed per request.")

    db_pool=request.app.state.pool
    
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
            content = await file.read()
            result = await ingest_document_content(
                pool=db_pool,
                document_name=file.filename,
                content_bytes=content,
                overwrite=overwrite
            )
            results.append(result)
        except Exception as e:
            logfire.error(f"Error ingesting {file.filename}: {e}")
            results.append({
                "document": file.filename,
                "status": "error",
                "message": str(e)
            })
            
    return {"results": results}
