#!/usr/bin/env python3
"""
Video Library CLI - Main entry point for processing video content.

Usage:
    python video_lib_cli.py <job_file_path> [options]

Example:
    python video_lib_cli.py contents/books/Meaningful-to-Behold/14_Effort/08_EXAMININGTHECAUSEOFINDOLENCE/job.json
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from video_lib.job_processor import JobProcessor
from video_lib.audio.voices import ResonaVoice
from video_lib.content.content_styles import ContentStyle


def main():
    """Main CLI entry point."""
    # Get available voices and styles for help text
    buddhist_voices = [v.name for v in ResonaVoice.get_buddhist_voices()]
    all_styles = [s.name for s in ContentStyle]

    parser = argparse.ArgumentParser(
        description="Process video content from job files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
    # Process a job file with default settings (Vietnamese, Gemini, HO_MIN_MANG voice, Conversational style)
    python video_lib_cli.py contents/books/Meaningful-to-Behold/14_Effort/08_EXAMININGTHECAUSEOFINDOLENCE/job.json

    # Use different voice and content style (enum names)
    python video_lib_cli.py path/to/job.json --voice TUE_AN --style COMPASSIONATE

    # Use Claude Code CLI instead of Gemini
    python video_lib_cli.py path/to/job.json --llm claude

    # Force regeneration (ignore cache)
    python video_lib_cli.py path/to/job.json --force

    # Generate English content
    python video_lib_cli.py path/to/job.json --language English

Recommended Buddhist Voices:
    {', '.join(buddhist_voices)}

Available Content Styles:
    {', '.join(all_styles)}
        """
    )

    parser.add_argument(
        "job_file",
        type=Path,
        nargs='?',  # Make optional for --list-voices/--list-styles
        help="Path to job.json file"
    )

    parser.add_argument(
        "--language",
        default="Vietnamese",
        help="Target language (default: Vietnamese)"
    )

    parser.add_argument(
        "--llm",
        dest="llm_provider",
        default="gemini",
        choices=["claude", "gemini"],
        help="LLM provider (default: gemini)"
    )

    parser.add_argument(
        "--voice",
        default=None,
        help=f"TTS voice enum name (default: VAN_ANH). Recommended: {', '.join(buddhist_voices[:5])}..."
    )

    parser.add_argument(
        "--style",
        dest="content_style",
        default=None,
        help=f"Content style enum name (default: CONVERSATIONAL). Options: {', '.join(all_styles[:5])}..."
    )

    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List all available voices and exit"
    )

    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List all available content styles and exit"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration (ignore cache)"
    )

    args = parser.parse_args()

    # Handle list commands
    if args.list_voices:
        print(ResonaVoice.list_voices())
        sys.exit(0)

    if args.list_styles:
        print(ContentStyle.list_styles())
        sys.exit(0)

    # Validate job_file is provided
    if args.job_file is None:
        parser.error("job_file is required")

    # Create job processor
    processor = JobProcessor(project_root)

    # Load environment variables
    processor.load_environment()

    # Validate environment
    if not processor.validate_environment(args.llm_provider):
        sys.exit(1)

    # Process the job
    result = processor.process(
        args.job_file,
        language=args.language,
        llm_provider=args.llm_provider,
        voice=args.voice,
        content_style=args.content_style,
        force=args.force
    )

    # Exit with error code if processing failed
    if result is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
