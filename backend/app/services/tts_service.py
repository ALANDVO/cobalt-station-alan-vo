import base64
import io
import time
import logging
from pathlib import Path
from typing import Optional
import torch
import torchaudio
from TTS.api import TTS

from app.core.config import settings
from app.models.tts import TTSRequest, TTSResponse

logger = logging.getLogger(__name__)


class TTSService:
    def __init__(self):
        self._tts: Optional[TTS] = None
        self._model_name = settings.tts_model
        self._device = settings.tts_device
        self._cache_dir = settings.tts_cache_dir
        self._loaded = False

    def load_model(self) -> None:
        if self._loaded:
            return

        logger.info(f"Loading TTS model: {self._model_name} on {self._device}")
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        try:
            self._tts = TTS(
                model_name=self._model_name,
                progress_bar=True,
                gpu=self._device == "cuda",
            ).to(self._device)
            self._loaded = True
            logger.info("TTS model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            raise RuntimeError(f"TTS model initialization failed: {e}") from e

    def is_loaded(self) -> bool:
        return self._loaded and self._tts is not None

    def get_device(self) -> str:
        return self._device

    def synthesize(self, request: TTSRequest) -> TTSResponse:
        if not self.is_loaded():
            self.load_model()

        assert self._tts is not None

        start_time = time.time()

        speaker_wav_path = None
        if request.speaker_wav:
            try:
                audio_bytes = base64.b64decode(request.speaker_wav)
                speaker_wav_path = self._cache_dir / f"ref_{hash(audio_bytes) & 0xFFFFFFFF:08x}.wav"
                speaker_wav_path.write_bytes(audio_bytes)
            except Exception as e:
                logger.warning(f"Failed to save reference audio, using default: {e}")
                speaker_wav_path = None

        try:
            if speaker_wav_path and speaker_wav_path.exists():
                wav = self._tts.tts(
                    text=request.text,
                    speaker_wav=str(speaker_wav_path),
                    language=request.language,
                    speed=request.speed,
                )
            else:
                wav = self._tts.tts(
                    text=request.text,
                    language=request.language,
                    speed=request.speed,
                )
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise RuntimeError(f"Speech synthesis failed: {e}") from e

        synthesis_time = time.time() - start_time
        logger.info(f"Synthesized {len(request.text)} chars in {synthesis_time:.2f}s")

        wav_tensor = torch.tensor(wav, dtype=torch.float32).unsqueeze(0)
        sample_rate = 24000

        buffer = io.BytesIO()
        torchaudio.save(buffer, wav_tensor, sample_rate, format="wav")
        audio_bytes = buffer.getvalue()

        duration = len(wav) / sample_rate
        audio_base64 = base64.b64encode(audio_bytes).decode("ascii")

        return TTSResponse(
            audio_base64=audio_base64,
            duration_seconds=round(duration, 2),
            sample_rate=sample_rate,
            language=request.language,
            text_length=len(request.text),
        )


tts_service = TTSService()