from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
from pathlib import Path

from pdf_processor import PDFProcessor
from embedder import EmbeddingGenerator
from vector_store import VectorStore
from rag_engine import RAGEngine

app = FastAPI(title="RAG Pipeline API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pdf_processor = PDFProcessor(chunk_size=500, chunk_overlap=50)
embedder = EmbeddingGenerator()
vector_store = VectorStore(dimension=embedder.dimension)
rag_engine = RAGEngine(pdf_processor, embedder, vector_store)

# Try to load existing index
vector_store.load()

class Query(BaseModel):
    question: str
    top_k: int = 3

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF"""
    pdf_path = Path("data/pdfs") / file.filename
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    with pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "status": "uploaded"}

@app.post("/index")
async def index_pdfs():
    """Index all PDFs in the data directory"""
    rag_engine.index_pdfs("data/pdfs")
    return {"status": "indexing complete", "total_chunks": len(vector_store.chunks)}

@app.post("/query")
async def query(q: Query):
    """Query the RAG system"""
    result = rag_engine.query(q.question, top_k=q.top_k)
    return result

@app.get("/stats")
async def get_stats():
    """Get index statistics"""
    return {
        "total_chunks": len(vector_store.chunks),
        "index_size": vector_store.index.ntotal if vector_store.index else 0
    }
