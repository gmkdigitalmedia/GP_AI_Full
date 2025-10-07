from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
import aiofiles
from pathlib import Path
import shutil

from agents.multimodal_rag import MultimodalRAG

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI(title="Multimodal RAG System", version="1.0.0")
templates = Jinja2Templates(directory="templates")

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize RAG system
rag = MultimodalRAG()

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    n_results: int = 5
    include_chat_history: bool = True

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    context_used: int

class ChatRequest(BaseModel):
    message: str

class IngestResponse(BaseModel):
    success: bool
    document_id: Optional[str] = None
    filename: Optional[str] = None
    file_type: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    error: Optional[str] = None

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_model=IngestResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and ingest a document"""
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename

        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Ingest the document
        result = rag.ingest_document(str(file_path))

        return IngestResponse(**result)

    except Exception as e:
        logging.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system"""
    try:
        result = rag.query(
            question=request.question,
            n_results=request.n_results,
            include_chat_history=request.include_chat_history
        )

        return QueryResponse(**result)

    except Exception as e:
        logging.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/chat")
async def chat_with_rag(request: ChatRequest):
    """Chat with the RAG system"""
    try:
        result = rag.chat(request.message)
        return result

    except Exception as e:
        logging.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/documents")
async def list_documents(limit: int = 20):
    """List all ingested documents"""
    try:
        documents = rag.list_documents(limit=limit)
        return {"documents": documents}

    except Exception as e:
        logging.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    try:
        success = rag.delete_document(doc_id)
        if success:
            return {"success": True, "message": f"Document {doc_id} deleted"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    except Exception as e:
        logging.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@app.get("/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        doc_stats = rag.get_document_stats()
        system_status = rag.check_system_status()

        return {
            "documents": doc_stats,
            "system": system_status
        }

    except Exception as e:
        logging.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.post("/bulk-ingest")
async def bulk_ingest_directory(directory_path: str = Form(...)):
    """Ingest all supported files from a directory"""
    try:
        if not os.path.exists(directory_path):
            raise HTTPException(status_code=404, detail="Directory not found")

        result = rag.bulk_ingest(directory_path)
        return result

    except Exception as e:
        logging.error(f"Bulk ingest failed: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk ingest failed: {str(e)}")

@app.delete("/chat/history")
async def clear_chat_history():
    """Clear chat history"""
    try:
        rag.clear_chat_history()
        return {"success": True, "message": "Chat history cleared"}

    except Exception as e:
        logging.error(f"Failed to clear chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        status = rag.check_system_status()
        return {"status": "healthy", "details": status}

    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)