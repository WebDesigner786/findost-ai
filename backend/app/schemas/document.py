"""Document Pydantic Schemas"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class DocumentOut(BaseModel):
    id: str
    workspaceId: str = Field(..., alias="workspace_id")
    filename: str
    fileType: str = Field(..., alias="file_type")
    mimeType: str = Field(..., alias="mime_type")
    fileSizeBytes: int = Field(..., alias="file_size_bytes")
    sourceRef: str = Field(..., alias="source_ref")
    status: str
    extractionMetadata: Dict[str, Any] = Field(default_factory=dict, alias="extraction_metadata")
    uploadedAt: str = Field(..., alias="uploaded_at")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class DocumentUploadResponse(BaseModel):
    document: DocumentOut
    extractedTransactionsCount: int
    message: str
