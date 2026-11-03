from pydantic import BaseModel


class DocumentResponse(BaseModel):
    document_id: str
    document_name: str
    file_hash: str
    chunks: int
