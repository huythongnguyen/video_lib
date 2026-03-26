"""Web viewer for short videos."""
from flask import Flask, render_template, send_file, request
from pathlib import Path

from video_lib.viewer.viewer_helper import ViewerHelper

# Initialize Flask app
app = Flask(__name__)

# Get project root (3 levels up from this file)
project_root = Path(__file__).parent.parent.parent

# Initialize viewer helper
viewer = ViewerHelper(project_root)


@app.route("/")
def index():
    """Home page - list all books."""
    books = viewer.list_books()
    return render_template("index.html", sorted_books=books)


@app.route("/book/<book>")
def book_detail(book):
    """List chapters and subchapters for a book."""
    filter_generated = request.args.get("filter", "all") == "generated"
    chapters = viewer.list_chapters(book, filter_generated=filter_generated)

    return render_template(
        "book.html",
        book=book,
        chapters=chapters,
        filter_generated=filter_generated
    )


@app.route("/viewer/<book>/<chapter>/<subchapter>")
def view_subchapter(book, chapter, subchapter):
    """View videos for a sub-chapter."""
    language = request.args.get("language", "Vietnamese")

    try:
        videos, metadata = viewer.load_subchapter_videos(
            book, chapter, subchapter, language
        )

        return render_template(
            "viewer.html",
            book=book,
            chapter=chapter,
            subchapter=subchapter,
            display_chapter=chapter,
            display_subchapter=subchapter,
            language=language,
            videos=videos,
            completion=metadata["completion"]
        )
    except FileNotFoundError as e:
        return f"Error: {e}", 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error loading subchapter: {e}", 500


@app.route("/audio/<book>/<chapter>/<subchapter>/<filename>")
def serve_audio(book, chapter, subchapter, filename):
    """Serve audio file."""
    audio_path = viewer.get_audio_file_path(book, chapter, subchapter, filename)

    if not audio_path:
        return "Audio file not found", 404

    return send_file(audio_path, mimetype="audio/mpeg")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
