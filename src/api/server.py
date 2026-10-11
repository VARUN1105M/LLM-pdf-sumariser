import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database.session import init_db
from src.api.routes import router as api_router, kb

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("lenny_assistant.server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing The Lenny Growth Assistant...")
    # 1. Initialize DB
    await init_db()
    # 2. Build or load knowledge base index
    count = kb.build_index()
    logger.info(f"Lenny Growth Assistant online. Loaded {count} transcript knowledge chunks.")
    yield
    logger.info("Shutting down Lenny Growth Assistant...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Forward Deployed AI Assistant for Product & Growth, powered by Lenny's Podcast transcripts.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router, prefix="/api")

# Static files for the web application UI
static_dir = Path(__file__).resolve().parent.parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def root():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "The Lenny Growth Assistant API is operational.",
        "documentation": "/docs",
        "api_health": "/api/health"
    }

# Structured error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing your request.",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "Refer to server logs."
        }
    )
