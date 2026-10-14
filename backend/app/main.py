from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.api import tts
from app.services.tts_service import tts_service

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting VoiceStudio backend...")
    if settings.debug:
        try:
            tts_service.load_model()
            logger.info("TTS model preloaded")
        except Exception as e:
            logger.warning(f"TTS model preload failed (will lazy-load): {e}")
    yield
    logger.info("Shutting down VoiceStudio backend...")


app = FastAPI(
    title="VoiceStudio API",
    description="Open-source, fully-local ElevenLabs alternative for voice AI",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts.router)


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.app_env,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )