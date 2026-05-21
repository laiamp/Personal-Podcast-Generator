from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Iterable

from openai import OpenAI
from dotenv import load_dotenv

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@dataclass(slots=True)
class OpenAIClient:
    """Thin wrapper around the OpenAI SDK for podcast generation tasks."""

    api_key: str | None = None
    model: str = DEFAULT_MODEL
    _client: OpenAI = field(init=False, repr=False)

    def __post_init__(self) -> None:
        load_dotenv()  # Load environment variables from .env file if present
        print(os.getenv("OPENAI_API_KEY"))
        self._client = OpenAI(api_key=self.api_key or os.getenv("OPENAI_API_KEY"))

    def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1200,
    ) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        message = response.choices[0].message.content if response.choices else ""
        return message or ""

    def generate_podcast_script(
        self,
        sources: Iterable[dict[str, Any]],
        *,
        voice_type: str = "multi_host_banter",
        user_context: dict[str, Any] | None = None,
    ) -> str:
        system_prompt, user_prompt = build_podcast_prompt(
            sources,
            voice_type=voice_type,
            user_context=user_context,
        )
        return self.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )


def build_podcast_prompt(
    sources: Iterable[dict[str, Any]],
    *,
    voice_type: str = "single_host_informative",
    duration_minutes: int = 1,
    user_context: dict[str, Any] | None = None,
) -> tuple[str, str]:
    source_lines = []
    for source in sources:
        title = source.get("title", "Untitled story")
        summary = source.get("summary", "")
        source_url = source.get("source_url", "")
        points = source.get("points")
        comments = source.get("num_comments")
        extra_bits = []
        if points is not None:
            extra_bits.append(f"points={points}")
        if comments is not None:
            extra_bits.append(f"comments={comments}")
        extra = f" ({', '.join(extra_bits)})" if extra_bits else ""
        source_lines.append(f"- {title}{extra}\n  Summary: {summary}\n  URL: {source_url}")

    context_text = ""
    if user_context:
        context_text = f"\nUser context: {user_context}"

    system_prompt = (
        "You are a podcast script writer for a personal news briefing. "
        "Write a concise, vivid, spoken script that feels natural when read aloud. "
        "Avoid disclaimers, markdown, bullet points, and meta commentary."
    )

    if voice_type == "multi_host_banter":
        raise NotImplementedError("Multi-host banter style is not implemented yet. Please choose a different voice_type or implement the dialogue formatting logic.")
    user_prompt = (
        f"Create a podcast script in the voice style '{voice_type}'."
        f"{context_text}\n\n"
        "Use the following sources as the factual basis for the episode:\n"
        + "\n".join(source_lines)
        + "\n\n"
        "Requirements:\n"
        "- Open with a short intro.\n"
        "- Group related stories naturally.\n"
        "- Keep the language conversational and engaging.\n"
        f"- Target roughly {duration_minutes} minutes spoken length.\n"
        "- End with a short sign-off."
    )

    return system_prompt, user_prompt

if __name__ == "__main__":
    # Quick test with dummy data
    client = OpenAIClient()
    test_sources = [
        {
            "title": "AI Startup Raises $50M",
            "summary": "A new AI startup focused on healthcare has raised $50 million in Series A funding.",
            "source_url": "https://example.com/ai-startup-news",
            "points": 150,
            "num_comments": 45,
        },
        {
            "title": "New AI Model Released",
            "summary": "A major tech company has released a new AI model that can generate code from natural language descriptions.",
            "source_url": "https://example.com/new-ai-model",
            "points": 200,
            "num_comments": 60,
        },
    ]
    script = client.generate_podcast_script(test_sources, voice_type="multi_host_banter")
    print("Generated Podcast Script:\n")
    print(script)