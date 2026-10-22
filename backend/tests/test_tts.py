import pytest
import base64
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.tts import TTSRequest, TTSResponse
from app.services.tts_service import TTSService


class TestTTSModels:
    def test_tts_request_valid(self):
        req = TTSRequest(text="Hello world", language="en")
        assert req.text == "Hello world"
        assert req.language == "en"
        assert req.speed == 1.0
        assert req.speaker_wav is None

    def test_tts_request_with_speaker(self):
        wav_data = b"RIFF" + b"\x00" * 44
        b64 = base64.b64encode(wav_data).decode()
        req = TTSRequest(text="Hello", language="es", speaker_wav=b64, speed=1.2)
        assert req.speaker_wav == b64
        assert req.speed == 1.2

    def test_tts_request_invalid_language(self):
        with pytest.raises(ValueError):
            TTSRequest(text="Hello", language="english")

    def test_tts_request_invalid_speed(self):
        with pytest.raises(ValueError):
            TTSRequest(text="Hello", language="en", speed=5.0)
        with pytest.raises(ValueError):
            TTSRequest(text="Hello", language="en", speed=0.1)

    def test_tts_request_invalid_base64(self):
        with pytest.raises(ValueError):
            TTSRequest(text="Hello", language="en", speaker_wav="not-base64!")

    def test_tts_request_non_wav(self):
        mp3_data = b"ID3" + b"\x00" * 100
        b64 = base64.b64encode(mp3_data).decode()
        with pytest.raises(ValueError):
            TTSRequest(text="Hello", language="en", speaker_wav=b64)


class TestTTSService:
    @pytest.fixture
    def service(self):
        return TTSService()

    def test_service_initialization(self, service):
        assert service.is_loaded() is False
        assert service.get_device() == "cpu"

    @patch("app.services.tts_service.TTS")
    def test_load_model_success(self, mock_tts_class, service):
        mock_tts = MagicMock()
        mock_tts_class.return_value.to.return_value = mock_tts

        service.load_model()

        assert service.is_loaded() is True
        mock_tts_class.assert_called_once()

    @patch("app.services.tts_service.TTS")
    def test_load_model_failure(self, mock_tts_class, service):
        mock_tts_class.side_effect = RuntimeError("Model not found")

        with pytest.raises(RuntimeError, match="TTS model initialization failed"):
            service.load_model()

        assert service.is_loaded() is False


class TestTTSAPI:
    @pytest.mark.asyncio
    async def test_synthesize_endpoint_exists(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/tts/synthesize",
                json={"text": "Test", "language": "en"},
            )
            assert response.status_code in (200, 500)

    @pytest.mark.asyncio
    async def test_synthesize_invalid_request(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/tts/synthesize",
                json={"text": "", "language": "en"},
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_synthesize_invalid_language(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/tts/synthesize",
                json={"text": "Test", "language": "english"},
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_tts_health_endpoint(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/tts/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "version" in data
            assert "tts_model_loaded" in data
            assert "device" in data


class TestTTSIntegration:
    @pytest.mark.asyncio
    @patch("app.api.tts.get_tts_service")
    async def test_synthesize_mocked(self, mock_get_service):
        mock_response = TTSResponse(
            audio_base64="dGVzdA==",
            duration_seconds=1.5,
            sample_rate=24000,
            language="en",
            text_length=4,
        )
        mock_service = mock_get_service.return_value
        mock_service.synthesize.return_value = mock_response
        mock_service.is_loaded.return_value = True
        mock_service.get_device.return_value = "cpu"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/tts/synthesize",
                json={"text": "Test", "language": "en"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["audio_base64"] == "dGVzdA=="
            assert data["duration_seconds"] == 1.5