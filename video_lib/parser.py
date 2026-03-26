"""Parse markdown books into structured data."""
import re
from pathlib import Path
from .models import Paragraph
from .utils import TextProcessor


class BookParser:
    """Parse a markdown book into chapters and paragraphs."""

    def __init__(self, book_path: Path):
        self.book_path = book_path
        self.content = book_path.read_text(encoding="utf-8")

    def parse_subchapter(self, chapter: str, subchapter: str) -> list[Paragraph]:
        """
        Extract all paragraphs from a specific sub-chapter.

        Args:
            chapter: Chapter name (e.g., "08_TheBenefitsofBodhichitta")
            subchapter: Sub-chapter name (e.g., "19_DEVELOPINGBODHICHITTA")

        Returns:
            List of Paragraph objects
        """
        blocks = re.split(r'\n\s*\n', self.content)

        paragraphs = []
        in_target = False
        current_chapter = None
        current_subchapter = None

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            if block.startswith('# ') or block.startswith('## '):
                current_chapter = self._normalize_name(block)
                current_subchapter = None
                in_target = False

            elif block.startswith('### ') or block.startswith('#### '):
                current_subchapter = self._normalize_name(block)
                if current_chapter == chapter and current_subchapter == subchapter:
                    in_target = True
                    paragraphs.append(self._make_paragraph(block, is_heading=True))
                else:
                    in_target = False

            elif in_target:
                paragraphs.append(self._make_paragraph(block))

        return paragraphs

    def _make_paragraph(self, text: str, is_heading: bool = False) -> Paragraph:
        """Create a Paragraph with hash."""
        para_hash = TextProcessor.make_hash(text)
        return Paragraph(text=text, hash=para_hash, is_heading=is_heading)

    def _normalize_name(self, heading: str) -> str:
        """Convert '### My Heading' to 'MyHeading'."""
        return TextProcessor.normalize(heading, remove_spaces=True)
