from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
import logging

from app.models.tts import TTSRequest, TTSResponse, HealthResponse
from app.services.tts_service import get_tts_service
from app.services.voice_service import synthesize_with_voice, get_voice_profile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tts", tags=["tts"])


@router.post(
    "/synthesize",
    response_model=TTSResponse,
    summary="Synthesize speech from text",
    description="Generate speech audio from text using XTTS v2. "
                "Optional voice cloning with reference audio (base64) or stored voice profile ID.",
)
async def synthesize(
    text: str,
    language: str = "en",
    speaker_wav: Optional[str] = None,
    voice_id: Optional[str] = Query(default=None, description="Voice profile ID for cloning"),
    speed: float = 1.0,
):
    """Synthesize speech, supporting both raw reference audio and stored voice profiles."""
    try:
        # If voice_id is provided, use the stored voice profile
        if voice_id:
            profile = get_voice_profile(voice_id)
            if profile is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Voice profile {voice_id} not found",
                )
            # Build a TTSRequest using the stored voice's reference audio
            from app.models.tts import TTSRequest as TTSReq
            request = TTSReq(
                text=text,
                language=language,
                speaker_wav=profile.reference_audio_b64,
                speed=speed,
            )
            # Synthesize using the voice profile's reference audio
            return synthesize_with_voice(
                text=text,
                language=language,
                voice_id=voice_id,
                speed=speed,
            )
        
        # Default path: use speaker_wav if provided, otherwise synthesize without reference
        from app.models.tts import TTSRequest as TTSReq
        request = TTSReq(
            text=text,
            language=language,
            speaker_wav=speaker_wav,
            speed=speed,
        )
        return get_tts_service().synthesize(request)
    except HTTPException:
        raise
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
