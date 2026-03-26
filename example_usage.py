#!/usr/bin/env python3
"""
Example usage of the video_lib library.

This script demonstrates how to:
1. Generate video content from a book sub-chapter
2. Generate audio for the content
3. View the results
"""

from video_lib.generator import VideoGenerator


def main():
    # Create a video generator
    print("🎬 Video Library - Example Usage\n")

    # Example 1: Vietnamese videos with Claude Code
    print("=" * 60)
    print("Example 1: Generate Vietnamese videos using Claude Code")
    print("=" * 60)

    gen = VideoGenerator(
        book="Meaningful-to-Behold.md",
        language="Vietnamese",
        llm_provider="claude"
    )

    # Process a sub-chapter
    result = gen.process(
        chapter="08_TheBenefitsofBodhichitta",
        subchapter="19_DEVELOPINGBODHICHITTA"
    )

    print(f"\n📊 Results:")
    print(f"   Total videos: {len(result.videos)}")
    print(f"   With audio: {result.audio_count()}")
    print(f"   Completion: {result.completion_rate():.1f}%")

    # Show first video
    if result.videos:
        video = result.videos[0]
        print(f"\n📹 First video ({video.video_id}):")
        print(f"   Original: {video.original_text[:100]}...")
        print(f"   Content: {video.video_content[:100]}...")
        print(f"   Has audio: {video.has_audio()}")

    # Example 2: English videos with Gemini (if available)
    print("\n" + "=" * 60)
    print("Example 2: Generate English videos using Gemini")
    print("=" * 60)
    print("(Uncomment below if you have GEMINI_API_KEY set)\n")

    # Uncomment to use Gemini:
    # gen_en = VideoGenerator(
    #     book="Meaningful-to-Behold.md",
    #     language="English",
    #     llm_provider="gemini"
    # )
    #
    # result_en = gen_en.process(
    #     chapter="08_TheBenefitsofBodhichitta",
    #     subchapter="19_DEVELOPINGBODHICHITTA"
    # )
    #
    # print(f"English videos: {len(result_en.videos)}")

    print("\n🌐 To view in browser:")
    print("   python video_lib/viewer/app.py")
    print("   Then open: http://localhost:5000/viewer/Meaningful-to-Behold/08_TheBenefitsofBodhichitta/19_DEVELOPINGBODHICHITTA")


if __name__ == "__main__":
    main()
