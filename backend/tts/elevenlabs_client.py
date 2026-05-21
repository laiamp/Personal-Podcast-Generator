from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import requests
from dotenv import load_dotenv


ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"


@dataclass(slots=True)
class ElevenLabsClient:
    """Small wrapper around the ElevenLabs text-to-speech API."""

    api_key: str | None = None
    voice_id: str | None = None
    model_id: str = "eleven_multilingual_v2"

    def __post_init__(self) -> None:
        load_dotenv()
        self.api_key = self.api_key or os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = self.voice_id or os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    def synthesize_to_file(
        self,
        text: str,
        output_path: str | Path,
        *,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ) -> Path:
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is required")
        if not self.voice_id:
            raise ValueError("voice_id is required")

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        url = f"{ELEVENLABS_API_BASE}/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "accept": "audio/mpeg",
            "content-type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
            },
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        path.write_bytes(response.content)
        return path

    def synthesize_bytes(
        self,
        text: str,
        *,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ) -> bytes:
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is required")
        if not self.voice_id:
            raise ValueError("voice_id is required")

        url = f"{ELEVENLABS_API_BASE}/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "accept": "audio/mpeg",
            "content-type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
            },
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        return response.content


if __name__ == "__main__":
    # Quick local test to verify ElevenLabs integration
    client = ElevenLabsClient()
    test_text = "Hello, this is a test of the ElevenLabs text-to-speech API integration."
    output_file = Path("test_output.mp3")
    client.synthesize_to_file(test_text, output_file)
    print(f"Synthesized audio saved to {output_file.resolve()}")