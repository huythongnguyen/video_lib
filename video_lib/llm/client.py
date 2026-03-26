"""LLM client for generating video content (Claude Code CLI or Gemini API)."""
import os
import subprocess
from typing import Optional, Union
from video_lib.models import Paragraph
from video_lib.content.prompts import get_filter_prompt, get_writer_prompt
from video_lib.utils import TextProcessor
from video_lib.content.content_styles import ContentStyle


class LLMClient:
    """Generate video content using Claude Code or Gemini."""

    def __init__(
        self,
        language: str = "Vietnamese",
        provider: str = "claude",
        content_style: Optional[Union[ContentStyle, str]] = None
    ):
        """
        Initialize LLM client.

        Args:
            language: Target language for content
            provider: "claude" (Claude Code CLI) or "gemini" (Gemini API)
            content_style: Content generation style (ContentStyle enum or name string)
        """
        self.language = language
        self.provider = provider.lower()

        if content_style is None:
            self.content_style = ContentStyle.get_default()
        elif isinstance(content_style, ContentStyle):
            self.content_style = content_style
        elif isinstance(content_style, str):
            resolved_style = ContentStyle.get_by_name(content_style)
            if resolved_style is None:
                raise ValueError(
                    f"Unknown content style: {content_style}. "
                    f"Use ContentStyle.list_styles() to see available styles."
                )
            self.content_style = resolved_style
        else:
            raise TypeError(f"content_style must be ContentStyle enum or str, got {type(content_style)}")

        if self.provider == "gemini":
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            genai.configure(api_key=api_key)
            model_name = (
                os.getenv("GEMINI_MODEL", "").strip()
                or "gemini-3.1-flash-lite-preview"
            )
            self.model = genai.GenerativeModel(model_name)

    def generate_content(self, paragraph: Paragraph) -> Optional[str]:
        """
        Generate video content for a paragraph.

        Returns:
            Video content string or None if skip
        """
        should_create = self._filter(paragraph)
        if not should_create:
            return None

        content = self._write_content(paragraph)
        return content

    def _filter(self, paragraph: Paragraph) -> bool:
        """Decide if paragraph should become video content."""
        if paragraph.is_heading:
            return False

        prompt = get_filter_prompt(paragraph.text)
        response = self._call_llm(prompt, max_tokens=100)

        decision = response.strip().upper()
        return "CREATE" in decision

    def _write_content(self, paragraph: Paragraph) -> str:
        """Generate video content with specified style."""
        prompt = get_writer_prompt(paragraph.text, self.language, self.content_style)
        response = self._call_llm(prompt, max_tokens=1000)

        return TextProcessor.extract_from_code_block(response)

    def _call_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call LLM provider (Claude Code or Gemini)."""
        if self.provider == "claude":
            return self._call_claude_code(prompt)
        if self.provider == "gemini":
            return self._call_gemini(prompt, max_tokens)
        raise ValueError(f"Unknown provider: {self.provider}")

    def _call_claude_code(self, prompt: str) -> str:
        """Call Claude Code CLI."""
        cmd = [
            "claude",
            "--dangerously-skip-permissions",
            "--print",
            prompt
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude Code failed: {result.stderr}")

        return result.stdout.strip()

    def _call_gemini(self, prompt: str, max_tokens: int) -> str:
        """Call Gemini API."""
        response = self.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": 0.7,
            }
        )
        return response.text
