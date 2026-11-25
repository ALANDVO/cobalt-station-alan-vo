import base64
import uuid
import io
import logging
from pathlib import Path
from typing import Optional, List
import torch
import torchaudio

from app.models.voices import VoiceProfile, list_voices, get_voice, save_voice, delete_voice
from app.core.config import settings
from app.services.tts_service import tts_service, TTSRequest, TTSResponse

logger = logging.getLogger(__name__)

# Directory for cached reference audio files
_REF_DIR = Path(settings.tts_cache_dir) / "voices"
_REF_DIR.mkdir(parents=True, exist_ok=True)


def upload_voice_profile(name: str, description: str, reference_audio_b64: str) -> VoiceProfile:
    """Upload and validate a voice profile from reference audio."""
    # Decode and save reference audio
    try:
        audio_bytes = base64.b64decode(reference_audio_b64)
    except Exception as e:
        raise ValueError(f"Invalid base64 audio: {e}") from e

    # Validate it's a WAV file (basic check)
    if len(audio_bytes) < 1000:
        raise ValueError("Reference audio too short (minimum 1KB required)")

    # Generate a unique ID and save
    profile = VoiceProfile(
        id=str(uuid.uuid4()),
        name=name or f"Voice {len(list_voices()) + 1}",
        description=description or "",
        reference_audio_b64=reference_audio_b64,
    )

    # Also save the decoded audio file for later use
    ref_path = _REF_DIR / f"voice_{profile.id}.wav"
    ref_path.write_bytes(audio_bytes)

    # Try to extract language info from the reference
    try:
        import torchaudio.info as tinfo
        # Read WAV info
        try:
            info = tinfo(str(ref_path))
            profile.language_code = "en"  # Default; could parse from filename/metadata
            profile.sample_rate = info.sample_rate
        except Exception:
            profile.sample_rate = 24000
    except Exception:
        profile.sample_rate = 24000

    save_voice(profile)
    logger.info(f"Voice profile saved: {profile.id} ({profile.name})")
    return profile


def list_voice_profiles() -> List[VoiceProfile]:
    """List all stored voice profiles."""
    return list_voices()


def get_voice_profile(voice_id: str) -> Optional[VoiceProfile]:
    """Get a specific voice profile by ID."""
    return get_voice(voice_id)


def synthesize_with_voice(text: str, language: str, voice_id: str, speed: float = 1.0) -> TTSResponse:
    """Synthesize speech using a stored voice profile."""
    profile = get_voice_profile(voice_id)
    if profile is None:
        raise ValueError(f"Voice profile {voice_id} not found")

    # Use the reference audio from the profile
    reference_b64 = profile.reference_audio_b64
    if not reference_b64:
        raise ValueError(f"Voice profile {voice_id} has no reference audio")

    # Decode the reference audio bytes
    try:
        audio_bytes = base64.b64decode(reference_b64)
    except Exception as e:
        raise ValueError(f"Invalid reference audio in profile {voice_id}: {e}") from e

    # Save reference audio temporarily for XTTS
    ref_path = _REF_DIR / f"ref_{voice_id}.wav"
    ref_path.write_bytes(audio_bytes)

    # Synthesize using the TTS service with the voice profile
    # We reuse the existing TTS synthesize path but with the stored voice
    from app.models.tts import TTSRequest

    request = TTSRequest(
        text=text,
        language=language,
        speaker_wav=reference_b64,
        speed=speed,
    )

    return tts_service.synthesize(request)


def delete_voice_profile(voice_id: str) -> bool:
    """Delete a voice profile and its cached audio file."""
    # Remove the cached reference file
    ref_path = _REF_DIR / f"voice_{voice_id}.wav"
    if ref_path.exists():
        ref_path.unlink()

    return delete_voice(voice_id)
