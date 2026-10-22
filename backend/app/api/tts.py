from fastapi import APIRouter, HTTPException, status
import logging

from app.models.tts import TTSRequest, TTSResponse, HealthResponse
from app.services.tts_service import get_tts_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tts", tags=["tts"])


@router.post(
    "/synthesize",
    response_model=TTSResponse,
    summary="Synthesize speech from text",
    description="Generate speech audio from text using XTTS v2. Optional voice cloning with reference audio.",
)
async def synthesize(request: TTSRequest) -> TTSResponse:
    try:
        return get_tts_service().synthesize(request)
    except RuntimeError as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.exception("Unexpected TTS error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal synthesis error",
        ) from e


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="TTS service health",
)
async def tts_health() -> HealthResponse:
    return HealthResponse(
        status="healthy" if get_tts_service().is_loaded() else "degraded",
        version="0.1.0",
        tts_model_loaded=get_tts_service().is_loaded(),
        device=get_tts_service().get_device(),
    )