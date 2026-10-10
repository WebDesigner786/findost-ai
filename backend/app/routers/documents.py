"""Documents Intake Router"""

import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.document import Document
from app.models.workspace import Workspace
from app.schemas.document import DocumentOut, DocumentUploadResponse

router = APIRouter(tags=["Documents"])

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "webp", "csv", "xlsx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    workspaceId: str = Form(..., alias="workspace_id"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Handles financial receipt, bank statement, or spreadsheet upload.
    
    Validates file extension, bounds size, logs metadata, and stores document record.
    """
    ws = db.query(Workspace).filter(Workspace.id == workspaceId).first()
    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspaceId}' not found.",
        )

    # Check extension
    filename = file.filename or "uploaded_file"
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '.{ext}' is not supported. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}.",
        )

    # Read content & validate size
    content = await file.read()
    size_bytes = len(content)
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum permitted limit of 10 MB.",
        )

    ts = int(time.time() * 1000)
    doc_id = f"doc-{ts}"
    source_ref = f"SCAN-{doc_id.upper()[:12]}.{ext}"

    doc = Document(
        id=doc_id,
        workspace_id=workspaceId,
        filename=filename,
        file_type="pdf" if ext == "pdf" else "image" if ext in {"jpg", "jpeg", "png", "webp"} else "spreadsheet",
        mime_type=file.content_type or "application/octet-stream",
        file_size_bytes=size_bytes,
        source_ref=source_ref,
        status="processed",
        extraction_metadata={
            "original_filename": filename,
            "parsed_size_kb": round(size_bytes / 1024, 2),
            "parser": "synthetic_pakistani_ocr_engine",
        },
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    doc_out = DocumentOut(
        id=doc.id,
        workspaceId=doc.workspace_id,
        filename=doc.filename,
        fileType=doc.file_type,
        mimeType=doc.mime_type,
        fileSizeBytes=doc.file_size_bytes,
        sourceRef=doc.source_ref,
        status=doc.status,
        extractionMetadata=doc.extraction_metadata,
        uploadedAt=doc.uploaded_at.isoformat(),
    )

    return DocumentUploadResponse(
        document=doc_out,
        extractedTransactionsCount=1,
        message="Document uploaded and processed successfully.",
    )


@router.get("/api/workspaces/{workspace_id}/documents", response_model=List[DocumentOut])
def list_workspace_documents(workspace_id: str, db: Session = Depends(get_db)):
    """Lists all uploaded documents and source references for a workspace."""
    docs = (
        db.query(Document)
        .filter(Document.workspace_id == workspace_id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )
    return [
        DocumentOut(
            id=d.id,
            workspaceId=d.workspace_id,
            filename=d.filename,
            fileType=d.file_type,
            mimeType=d.mime_type,
            fileSizeBytes=d.file_size_bytes,
            sourceRef=d.source_ref,
            status=d.status,
            extractionMetadata=d.extraction_metadata,
            uploadedAt=d.uploaded_at.isoformat(),
        )
        for d in docs
    ]
