"""
Main Application Entrypoint for HOMEOPATHY_AGENT.
Enterprise Zero-Trust Homeopathic Hospital Information System (HHIS).
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import db
from app.api.v1 import api_v1_router

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("homeopathy.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event manager: boots DB schema and async WAL commit worker."""
    logger.info(f"Booting {settings.PROJECT_NAME} v{settings.VERSION}...")
    db.init_schema()
    await db.start_worker()
    yield
    logger.info("Gracefully shutting down asynchronous workers...")
    await db.stop_worker()
    logger.info("Shutdown complete.")

app = FastAPI(
    title="HOMEOPATHY_AGENT HHIS",
    description="Autonomous Classical Homeopathic AI, Repertorization Kernel & Zero-Trust HHIS",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (Restricted origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:3000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. The incident has been logged for audit.",
            "path": request.url.path
        }
    )

# Include API v1 Router
app.include_router(api_v1_router, prefix="/api")

@app.get("/", tags=["System Root"])
async def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "docs": "/docs",
        "jurisdiction": settings.DEFAULT_JURISDICTION,
        "architecture": "Zero-Trust SQLite WAL Asynchronous Commit Pipeline"
    }
