"""Content generation style configuration."""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


@dataclass
class StyleConfig:
    """Configuration for a content generation style."""
    name: str
    tone: str
    approach: str
    description: str


class ContentStyle(Enum):
    """Enum of content generation styles for short videos.

    Each style defines a different tone and approach for transforming
    Buddhist teachings into engaging short-form content.
    """

    CONVERSATIONAL = StyleConfig(
        name="Conversational",
        tone="Warm, inclusive, personal",
        approach="Use 'ta' and 'chúng ta', speak directly to viewer as a friend",
        description="Friendly, personal conversation style (DEFAULT)"
    )

    THOUGHT_PROVOKING = StyleConfig(
        name="Thought-Provoking",
        tone="Reflective, questioning, deep",
        approach="Ask open-ended questions, encourage self-reflection, avoid direct answers",
        description="Challenge viewers to think deeply about their lives"
    )

    CLAIMING = StyleConfig(
        name="Claiming",
        tone="Confident, assertive, clear",
        approach="Make bold statements, use definitive language, provide clarity",
        description="Strong, clear statements of Buddhist truths"
    )

    STORYTELLING = StyleConfig(
        name="Storytelling",
        tone="Narrative, engaging, vivid",
        approach="Use concrete examples, paint pictures, tell mini-stories",
        description="Transform teachings into relatable stories"
    )

    PRACTICAL = StyleConfig(
        name="Practical",
        tone="Action-oriented, concrete, helpful",
        approach="Focus on actionable steps, real-world application, how-to guidance",
        description="Practical advice for daily Buddhist practice"
    )

    COMPASSIONATE = StyleConfig(
        name="Compassionate",
        tone="Gentle, understanding, supportive",
        approach="Acknowledge struggles, offer comfort, emphasize self-compassion",
        description="Gentle, empathetic guidance for difficult times"
    )

    CHALLENGING = StyleConfig(
        name="Challenging",
        tone="Direct, confrontational, motivating",
        approach="Call out delusions, push for change, use tough love",
        description="Direct challenge to wake up and change"
    )

    INSPIRATIONAL = StyleConfig(
        name="Inspirational",
        tone="Uplifting, hopeful, encouraging",
        approach="Emphasize possibilities, celebrate progress, inspire action",
        description="Motivating and uplifting Buddhist wisdom"
    )

    PHILOSOPHICAL = StyleConfig(
        name="Philosophical",
        tone="Analytical, systematic, deep",
        approach="Break down concepts, explain reasoning, explore implications",
        description="Deeper philosophical exploration of teachings"
    )

    HUMOROUS = StyleConfig(
        name="Humorous",
        tone="Light, playful, relatable",
        approach="Use gentle humor, everyday examples, lighthearted observations",
        description="Make teachings accessible through gentle humor"
    )

    @classmethod
    def get_default(cls) -> 'ContentStyle':
        """Get default style (Conversational)."""
        return cls.CONVERSATIONAL

    @classmethod
    def get_by_name(cls, name: str) -> Optional['ContentStyle']:
        """
        Get style by display name or enum name (case-insensitive).

        Args:
            name: Style name (e.g., "Conversational") or enum name (e.g., "CONVERSATIONAL", "COMPASSIONATE")

        Returns:
            ContentStyle enum member or None if not found
        """
        # Try enum name first (e.g., "CONVERSATIONAL", "COMPASSIONATE")
        try:
            return cls[name.upper()]
        except KeyError:
            pass

        # Fall back to display name matching
        name_normalized = name.lower().replace(" ", "_").replace("-", "_")
        for style in cls:
            style_name_normalized = style.value.name.lower().replace(" ", "_").replace("-", "_")
            if style_name_normalized == name_normalized:
                return style
        return None

    @classmethod
    def list_styles(cls) -> str:
        """
        List all available content styles.

        Returns:
            Formatted string with style information
        """
        lines = ["Available content generation styles:", ""]

        for style in cls:
            config = style.value
            marker = " (DEFAULT)" if style == cls.CONVERSATIONAL else ""
            lines.append(f"  {config.name}{marker}")
            lines.append(f"    Tone: {config.tone}")
            lines.append(f"    Approach: {config.approach}")
            lines.append(f"    {config.description}")
            lines.append("")

        return "\n".join(lines)
