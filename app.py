import logging
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import RequestEntityTooLarge


MAX_UPLOAD_BYTES = 10 * 1024 * 1024
IMAGE_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


def _blip_caption(image_path):
    from main_working import generate_caption

    return generate_caption(image_path)


def create_app(caption_generator=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
    app.config["CAPTION_GENERATOR"] = (
        caption_generator if caption_generator is not None else _blip_caption
    )

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_upload(_error):
        return jsonify(error="Image must be 10 MB or smaller."), 413

    @app.post("/api/caption")
    def caption():
        upload = request.files.get("image")
        if upload is None or not upload.filename:
            return jsonify(error="Choose an image to generate a caption."), 400

        try:
            image = Image.open(upload.stream)
            image_format = image.format
            if image_format not in IMAGE_FORMATS:
                return jsonify(error="Use a JPEG, PNG, or WebP image."), 400
            image.verify()
            upload.stream.seek(0)
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            return jsonify(error="That file is not a valid image."), 400

        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                suffix=IMAGE_FORMATS[image_format], delete=False
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                upload.save(temporary_file)

            generated_caption = app.config["CAPTION_GENERATOR"](str(temporary_path))
            if not isinstance(generated_caption, str) or not generated_caption.strip():
                raise ValueError("The caption model returned an empty result.")
            return jsonify(caption=generated_caption.strip())
        except Exception:
            app.logger.exception("Caption generation failed")
            return jsonify(error="Caption generation failed. Please try again."), 500
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="127.0.0.1", port=5000, debug=False)
