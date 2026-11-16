"""Voice cloning tests for the voice-cloning feature."""

import pytest
import base64
import tempfile
import wave
import struct
from pathlib import Path
from unittest.mock import patch, MagicMock

import numpy as np

from app.models.tts import TTSRequest, TTSResponse
from app.models.voices import VoiceProfile, list_voices, save_voice, get_voice, delete_voice, VoiceProfile
from app.services.voice_service import upload_voice_profile, list_voice_profiles, get_voice_profile, synthesize_with_voice, delete_voice_profile


def _make_mock_wav_base64(duration_sec: float = 5.0, sample_rate: int = 24000) -> str:
    """Generate a minimal valid WAV file as base64 for testing."""
    n_frames = int(sample_rate * duration_sec)
    t = np.linspace(0, duration_sec, n_frames, False)
    wave_data = np.sin(2 * np.pi * 440 * t) * 0.5
    wave_data = wave_data.astype(np.int16)
    wav_io = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    with wave.open(wav_io.name, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(wave_data.tobytes())
    wav_io.close()
    with open(wav_io.name, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    Path(wav_io.name).unlink(missing_ok=True)
    return b64


class TestVoiceProfiles:
    """Test voice profile management."""

    def test_create_voice_profile(self):
        """Test creating a voice profile from reference audio."""
        ref_b64 = _make_mock_wav_base64(5.0)
        profile = upload_voice_profile(
            name="Test Voice",
            description="A test voice for cloning",
            reference_audio_b64=ref_b64,
        )
        assert profile is not None
        assert profile.name == "Test Voice"
        assert profile.reference_audio_b64 == ref_b64
        assert profile.id != ""

    def test_list_voices(self):
        """Test listing voice profiles."""
        # Should start empty or with pre-existing voices
        voices = list_voices()
        assert isinstance(voices, list)

    def test_get_voice_profile(self):
        """Test retrieving a voice profile by ID."""
        ref_b64 = _make_mock_wav_base64(5.0)
        profile = upload_voice_profile(
            name="Get Test Voice",
            description="Test profile retrieval",
            reference_audio_b64=ref_b64,
        )
        retrieved = get_voice_profile(profile.id)
        assert retrieved is not None
        assert retrieved.name == profile.name
        assert retrieved.id == profile.id

    def test_get_nonexistent_voice(self):
        """Test getting a voice profile that doesn't exist."""
        result = get_voice_profile("nonexistent-id")
        assert result is None

    def test_delete_voice_profile(self):
        """Test deleting a voice profile."""
        ref_b64 = _make_mock_wav_base64(5.0)
        profile = upload_voice_profile(
            name="Delete Test Voice",
            description="Test profile deletion",
            reference_audio_b64=ref_b64,
        )
        success = delete_voice_profile(profile.id)
        assert success is True
        # Voice should be gone
        result = get_voice_profile(profile.id)
        assert result is None


class TestVoiceCloningSynthesis:
    """Test voice cloning synthesis with stored profiles."""

    @patch("app.services.tts_service.TTS")
    def test_synthesize_with_stored_voice(self, mock_tts_class):
        """Test synthesizing speech using a stored voice profile."""
        # Create a voice profile first
        ref_b64 = _make_mock_wav_base64(5.0)
        profile = upload_voice_profile(
            name="Clone Test Voice",
            description="Voice for cloning tests",
            reference_audio_b64=ref_b64,
        )

        # Mock the TTS service
        mock_tts_instance = MagicMock()
        mock_tts_instance.tts.return_value = [0.5] * 24000  # 1 second at 24kHz
        mock_tts_class.return_value = mock_tts_instance

        # Synthesize using the voice ID
        from app.models.tts import TTSRequest
        request = TTSRequest(
            text="Hello, this is cloned voice",
            language="en",
            voice_id=profile.id,
            speed=1.0,
        )

        # This should attempt to use the stored voice
        from app.services.voice_service import synthesize_with_voice
        result = synthesize_with_voice(
            text="Hello, this is cloned voice",
            language="en",
            voice_id=profile.id,
            speed=1.0,
        )
        assert result is not None
        assert hasattr(result, 'audio_base64')
        assert hasattr(result, 'duration_seconds')

    @patch("app.services.tts_service.TTS")
    def test_synthesize_with_invalid_voice_id(self, mock_tts_class):
        """Test synthesizing with a voice ID that doesn't exist."""
        mock_tts_class.side_effect = None

        from app.models.tts import TTSRequest
        request = TTSRequest(
            text="Hello",
            language="en",
            voice_id="nonexistent-id",
            speed=1.0,
        )

        from app.services.voice_service import synthesize_with_voice
        try:
            result = synthesize_with_voice(
                text="Hello",
                language="en",
                voice_id="nonexistent-id",
                speed=1.0,
            )
            # Should raise an error since voice doesn't exist
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not found" in str(e).lower() or "Voice profile" in str(e)


class TestTTSRequestModels:
    """Test TTS request model validation."""

    def test_tts_request_with_voice_id(self):
        """Test TTSRequest with voice_id but no speaker_wav."""
        req = TTSRequest(
            text="Hello world",
            language="en",
            voice_id="some-voice-id",
            speaker_wav=None,
        )
        assert req.voice_id == "some-voice-id"
        assert req.speaker_wav is None

    def test_tts_request_with_speaker_wav_no_voice_id(self):
        """Test TTSRequest with speaker_wav but no voice_id."""
        req = TTSRequest(
            text="Hello world",
            language="en",
            speaker_wav="base64encodedwavaudio",
            voice_id=None,
        )
        assert req.speaker_wav == "base64encodedwavaudio"
        assert req.voice_id is None

    def test_tts_request_both_speaker_wav_and_voice_id(self):
        """Test TTSRequest with both speaker_wav and voice_id (voice_id takes precedence)."""
        ref_b64 = "base64referenceaudio"
        req = TTSRequest(
            text="Hello world",
            language="en",
            speaker_wav=ref_b64,
            voice_id="some-voice-id",
        )
        assert req.speaker_wav == ref_b64
        assert req.voice_id == "some-voice-id"


class TestIntegration:
    """Integration-level tests."""

    @patch("app.services.tts_service.TTS")
    def test_full_voice_cloning_workflow(self, mock_tts_class):
        """Test the full workflow: upload voice -> synthesize with voice -> delete voice."""
        mock_tts_instance = MagicMock()
        mock_tts_instance.tts.return_value = [0.5] * 24000
        mock_tts_class.return_value = mock_tts_instance

        # Step 1: Upload a voice profile
        t = np.linspace(0, 5, 120000, False)
        wave_data = np.sin(2 * np.pi * 440 * t) * 0.5
        wave_data = wave_data.astype(np.int16)
        wav_io = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        with wave.open(wav_io.name, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(24000)
            wav.writeframes(wave_data.tobytes())
        wav_io.close()
        with open(wav_io.name, 'rb') as f:
            ref_b64 = base64.b64encode(f.read()).decode('ascii')
        Path(wav_io.name).unlink(missing_ok=True)

        profile = upload_voice_profile(
            name="Integration Test Voice",
            description="Voice used in integration test",
            reference_audio_b64=ref_b64,
        )
        assert profile is not None
        assert profile.name == "Integration Test Voice"

        # Step 2: Synthesize with the voice
        from app.models.tts import TTSRequest
        request = TTSRequest(
            text="This is my cloned voice speaking",
            language="en",
            voice_id=profile.id,
            speed=1.0,
        )

        from app.services.voice_service import synthesize_with_voice
        result = synthesize_with_voice(
            text="This is my cloned voice speaking",
            language="en",
            voice_id=profile.id,
            speed=1.0,
        )
        assert result is not None
        assert len(result.audio_base64) > 0
        assert result.duration_seconds > 0
        assert result.sample_rate == 24000

        # Step 3: Delete the voice profile
        delete_success = delete_voice_profile(profile.id)
        assert delete_success is True
        assert get_voice_profile(profile.id) is None
