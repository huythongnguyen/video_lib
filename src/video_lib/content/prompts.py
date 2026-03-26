"""Prompt templates for LLM."""
from typing import Optional
from video_lib.content.content_styles import ContentStyle


def get_filter_prompt(text: str) -> str:
    """Prompt for filtering content."""
    return f"""You are a content filter for short videos (TikTok/Shorts).

Analyze this paragraph and decide if it should be turned into video content.

CREATE content for:
- Meaningful teachings
- Stories and examples
- Practice instructions
- Philosophical concepts

SKIP:
- Headings and titles
- Citations and references
- Transitional text
- Acknowledgments

Paragraph:
{text}

Respond with ONLY one word: "CREATE" or "SKIP"
"""


def get_writer_prompt(
    text: str,
    language: str,
    content_style: Optional[ContentStyle] = None
) -> str:
    """
    Prompt for writing video content.

    Args:
        text: Original text to transform
        language: Target language
        content_style: Content generation style (default: Conversational)

    Returns:
        Formatted prompt string
    """
    # Use default style if not provided
    if content_style is None:
        content_style = ContentStyle.get_default()

    style_config = content_style.value

    # Language-specific base guidelines
    base_guidelines = {
        "Vietnamese": """
Write natural Vietnamese content for a short video (30-60 seconds when read aloud).

Base Guidelines:
- Use inclusive pronouns ("ta", "chúng ta")
- Natural flow for social media
- 3-7 sentences total
""",
        "English": """
Write natural English content for a short video (30-60 seconds when read aloud).

Base Guidelines:
- Natural flow for social media
- 3-7 sentences total
"""
    }

    base_guide = base_guidelines.get(language, base_guidelines["English"])

    # Add style-specific instructions
    style_instructions = f"""
Content Style: {style_config.name}
- Tone: {style_config.tone}
- Approach: {style_config.approach}

Apply this style consistently throughout your writing.
"""

    return f"""You are a video content writer for short videos (TikTok/Shorts/Reels).

{base_guide}

{style_instructions}

Original text (English):
{text}

Write the {language} video content following the specified style. Output ONLY the content text, no explanation, no labels, no markdown formatting.
"""
