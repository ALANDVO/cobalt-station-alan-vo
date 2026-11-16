from typing import List
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
import logging

from app.models.voices import VoiceProfile, list_voices, get_voice, delete_voice, VoiceProfile
from app.services.voice_service import upload_voice_profile, list_voice_profiles, get_voice_profile, synthesize_with_voice, delete_voice_profile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/voices", tags=["voices"])


@router.post(
    "",
    response_model=dict,
    summary="Upload a voice profile for cloning",
    description="Upload reference audio to create a voice profile that can be used for voice cloning. Reference audio should be clean, single-speaker WAV audio (minimum 6 seconds recommended).",
)
async def upload_voice(
    name: str = "",
    description: str = "",
    reference_audio: UploadFile = File(...),
):
    """Upload a voice profile from reference audio file."""
    # Read the uploaded file and convert to base64
    audio_bytes = await reference_audio.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No audio file uploaded",
        )

    # Basic validation: must be WAV format
    if not audio_bytes.startswith(b"RIFF") or b"WAVE" not in audio_bytes[:12]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reference audio must be in WAV format",
        )

    # Convert to base64
    import base64
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

    # Upload and validate using the voice service
    try:
        profile = upload_voice_profile(name, description, audio_b64)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return {
        "id": profile.id,
        "name": profile.name,
        "description": profile.description,
        "message": "Voice profile created successfully",
        "reference_audio_duration_estimate": "~6s+",
    }


@router.get(
    "",
    response_model=List[dict],
    summary="List all voice profiles",
    description="List all stored voice profiles available for cloning.",
)
async def list_voices_endpoint():
    """List all stored voice profiles."""
    profiles = list_voice_profiles()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "language_code": p.language_code,
            "sample_rate": p.sample_rate,
            "created_at": p.created_at,
        }
        for p in profiles
    ]


@router.get(
    "/{voice_id}",
    response_model=dict,
    summary="Get a specific voice profile",
    description="Retrieve a voice profile by ID.",
)
async def get_voice_endpoint(voice_id: str):
    """Get a specific voice profile."""
    profile = get_voice_profile(voice_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile {voice_id} not found",
        )

    return {
        "id": profile.id,
        "name": profile.name,
        "description": profile.description,
        "reference_audio_b64": profile.reference_audio_b64,
        "language_code": profile.language_code,
        "sample_rate": profile.sample_rate,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }


@router.delete(
    "/{voice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a voice profile",
    description="Delete a stored voice profile.",
)
async def delete_voice_endpoint(voice_id: str):
    """Delete a voice profile."""
    success = delete_voice_profile(voice_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile {voice_id} not found",
        )
    return None
