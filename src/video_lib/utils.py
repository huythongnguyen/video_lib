"""Shared utilities used across the library."""
import re
import hashlib
import json
import urllib.request
from typing import Optional


class TextProcessor:
    """Text processing utilities for normalization, hashing, and formatting."""

    @staticmethod
    def normalize(text: str, remove_spaces: bool = True, lowercase: bool = False) -> str:
        """
        Normalize text by removing markdown, punctuation, and optionally spaces.

        Args:
            text: Input text
            remove_spaces: If True, remove all spaces
            lowercase: If True, convert to lowercase

        Returns:
            Normalized text

        Examples:
            >>> TextProcessor.normalize("### My Heading")
            'MyHeading'
            >>> TextProcessor.normalize("The pre-eminent qualities", remove_spaces=False, lowercase=True)
            'the preeminent qualities'
        """
        # Remove markdown heading markers
        clean = re.sub(r'^#+\s*', '', text)

        # Remove punctuation
        clean = re.sub(r'[^\w\s]', '', clean)

        # Optionally lowercase
        if lowercase:
            clean = clean.lower()

        # Optionally remove spaces
        if remove_spaces:
            clean = re.sub(r'\s+', '', clean)
        else:
            # Normalize whitespace
            clean = re.sub(r'\s+', ' ', clean)

        return clean.strip()

    @staticmethod
    def to_snippet(text: str, max_words: int = 4) -> str:
        """
        Convert text to URL-friendly snippet (first N words).

        Args:
            text: Input text
            max_words: Maximum number of words to include

        Returns:
            Underscore-separated snippet

        Examples:
            >>> TextProcessor.to_snippet("The pre-eminent qualities of the author")
            'the_preeminent_qualities_of'
            >>> TextProcessor.to_snippet("What is bodhichitta?")
            'what_is_bodhichitta'
        """
        clean = TextProcessor.normalize(text, remove_spaces=False, lowercase=True)
        words = clean.split()[:max_words]
        return "_".join(words)

    @staticmethod
    def make_hash(text: str, length: int = 16) -> str:
        """
        Generate a SHA256 hash of text.

        Args:
            text: Input text
            length: Hash length (default 16 characters)

        Returns:
            Hex hash string

        Examples:
            >>> TextProcessor.make_hash("Hello world")[:8]
            '64ec88ca'
        """
        return hashlib.sha256(text.encode()).hexdigest()[:length]

    @staticmethod
    def extract_from_code_block(text: str) -> str:
        """
        Extract content from markdown code blocks.

        Args:
            text: Text potentially containing ```code blocks```

        Returns:
            Extracted content or original text if no code blocks

        Examples:
            >>> TextProcessor.extract_from_code_block("```json\\n{\"key\": \"value\"}\\n```")
            '{"key": "value"}'
            >>> TextProcessor.extract_from_code_block("plain text")
            'plain text'
        """
        text = text.strip()

        if "```" not in text:
            return text

        # Split by code blocks
        parts = text.split("```")
        if len(parts) < 2:
            return text

        # Get content inside first code block
        content = parts[1]

        # Remove language identifier (e.g., "json", "text")
        if content.startswith("json") or content.startswith("text"):
            content = "\n".join(content.split("\n")[1:])

        return content.strip()

    @staticmethod
    def normalize_book_name(book: str) -> str:
        """
        Normalize book filename by removing .md extension.

        Args:
            book: Book filename (e.g., "Meaningful-to-Behold.md")

        Returns:
            Normalized name (e.g., "Meaningful-to-Behold")

        Examples:
            >>> TextProcessor.normalize_book_name("My-Book.md")
            'My-Book'
            >>> TextProcessor.normalize_book_name("My-Book")
            'My-Book'
        """
        return book.replace(".md", "")


class HttpClient:
    """HTTP client utilities for API requests and file downloads."""

    @staticmethod
    def request(
        url: str,
        headers: dict,
        method: str = "GET",
        data: Optional[dict] = None
    ) -> dict:
        """
        Make HTTP request and return JSON response.

        Args:
            url: Request URL
            headers: HTTP headers
            method: HTTP method (GET, POST, etc.)
            data: Optional JSON data for POST requests

        Returns:
            Parsed JSON response

        Raises:
            urllib.error.URLError: If request fails
        """
        # Prepare request data
        request_data = None
        if data:
            request_data = json.dumps(data).encode("utf-8")

        # Create request
        req = urllib.request.Request(
            url,
            data=request_data,
            headers=headers,
            method=method
        )

        # Execute and parse response
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def download(url: str, dest_path, headers: Optional[dict] = None) -> None:
        """
        Download file from URL to local path.

        Args:
            url: Download URL
            dest_path: Destination path (Path or str)
            headers: Optional HTTP headers
        """
        headers = headers or {}
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req) as resp:
            content = resp.read()

        # Write to file (supports both Path and str)
        if hasattr(dest_path, 'write_bytes'):
            dest_path.write_bytes(content)
        else:
            with open(dest_path, 'wb') as f:
                f.write(content)
