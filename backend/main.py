"""
FastAPI application for Skill Executor API

Main entry point for the backend service
"""

import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from backend.api.routes import router
from backend.api.websocket import chat_websocket
from backend.services.executor_service import startup_executor_service, shutdown_executor_service
from backend.schemas import HealthResponse

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("skill_executor.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Skill Executor API...")

    # Get configuration from environment
    skills_dir = os.getenv("SKILLS_DIR", "./skills")
    provider = os.getenv("DEFAULT_PROVIDER", "openai") or os.getenv("LLM_PROVIDER", "openai")

    # Get model name - support both LLM_MODEL and OPENAI_MODEL/ANTHROPIC_MODEL
    model = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL") or os.getenv("ANTHROPIC_MODEL")

    max_execution_time = int(os.getenv("MAX_EXECUTION_TIME", "300"))
    audit_level = os.getenv("AUDIT_LEVEL", "basic")

    # Parse allowed paths from environment
    allowed_paths_str = os.getenv("ALLOWED_PATHS", "")
    allowed_paths = [p.strip() for p in allowed_paths_str.split(",") if p.strip()] or None

    try:
        executor_service = await startup_executor_service(
            skills_dir=skills_dir,
            provider=provider,
            model=model,
            max_execution_time=max_execution_time,
            audit_level=audit_level,
            allowed_paths=allowed_paths
        )
        logger.info(f"✓ Loaded {executor_service.skills_count} skills with {executor_service.total_scripts_count} scripts")
        logger.info(f"✓ LLM Provider: {provider}")
    except Exception as e:
        logger.error(f"Failed to initialize executor service: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down Skill Executor API...")
    await shutdown_executor_service()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Skill Executor API",
    description="通过自然语言搜索、调度并执行 Skills",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint - serve frontend
@app.get("/")
async def root():
    """Root endpoint - serve frontend HTML"""
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "Skill Executor API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/health"
    }


# Mount static files for frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    logger.info(f"✓ Static files mounted at /static from {frontend_dir}")
else:
    logger.warning(f"Frontend directory not found: {frontend_dir}")


# Include API routes
app.include_router(router)
logger.info("✓ API routes registered")

# WebSocket endpoint
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await chat_websocket(websocket)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check (no auth required)
@app.get("/health")
async def health():
    """Simple health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
