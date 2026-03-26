"""Resona TTS API client."""
import os
import time
from pathlib import Path
from typing import Union, Optional
from video_lib.utils import HttpClient
from video_lib.audio.voices import ResonaVoice


class ResonaClient:
    """Generate audio via Resona API."""

    def __init__(
        self,
        language: str = "Vietnamese",
        voice: Optional[Union[ResonaVoice, str]] = None
    ):
        """
        Initialize Resona TTS client.

        Args:
            language: Target language (for backward compatibility, ignored if voice is set)
            voice: Voice to use - can be:
                   - ResonaVoice enum member (e.g., ResonaVoice.VAN_ANH)
                   - Voice name as string (e.g., "Vân Anh" or "Thanh Nhã")
                   - None to use default (Vân Anh)
        """
        self.api_key = os.getenv("RESONA_API_KEY")
        if not self.api_key:
            raise ValueError("RESONA_API_KEY environment variable not set")

        self.base_url = "https://resona.live"

        # Resolve voice
        if voice is None:
            self.voice = ResonaVoice.get_default()
        elif isinstance(voice, ResonaVoice):
            self.voice = voice
        elif isinstance(voice, str):
            resolved_voice = ResonaVoice.get_by_name(voice)
            if resolved_voice is None:
                raise ValueError(
                    f"Unknown voice: {voice}. "
                    f"Use ResonaVoice.list_voices() to see available voices."
                )
            self.voice = resolved_voice
        else:
            raise TypeError(f"voice must be ResonaVoice enum or str, got {type(voice)}")

        self.voice_id = self.voice.value.voice_id

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Origin": "https://resona.live",
            "Referer": "https://resona.live/",
        }

    def generate_audio(self, text: str, output_path: Path) -> None:
        """Generate audio from text and save to file."""
        request_id = self._submit_job(text)
        audio_url = self._wait_for_completion(request_id)
        self._download(audio_url, output_path)

    def _submit_job(self, text: str) -> str:
        """Submit TTS job, return request_id."""
        url = f"{self.base_url}/api/v1/generate-speech"
        data = {
            "text": f"Speaker 1: {text}",
            "voice_ids": [self.voice_id]
        }

        result = HttpClient.request(url, self.headers, method="POST", data=data)
        return result["request_id"]

    def _wait_for_completion(self, request_id: str, timeout: int = 180) -> str:
        """Poll until completed, return audio URL."""
        deadline = time.time() + timeout

        while time.time() < deadline:
            status = self._check_status(request_id)

            if status["status"] == "completed":
                result = self._get_result(request_id)
                return result["audio_urls"][0]

            elif status["status"] == "failed":
                raise RuntimeError(f"TTS job {request_id} failed")

            time.sleep(3)

        raise TimeoutError(f"TTS job {request_id} timed out")

    def _check_status(self, request_id: str) -> dict:
        """Check job status."""
        url = f"{self.base_url}/api/v1/generate-speech/{request_id}/status"
        return HttpClient.request(url, self.headers)

    def _get_result(self, request_id: str) -> dict:
        """Get completed job result."""
        url = f"{self.base_url}/api/v1/generate-speech/{request_id}"
        return HttpClient.request(url, self.headers)

    def _download(self, url: str, dest: Path) -> None:
        """Download audio file."""
        headers = {"User-Agent": self.headers["User-Agent"]}
        HttpClient.download(url, dest, headers)
