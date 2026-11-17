import io
import os
import sys
import unittest

from PIL import Image

from app import create_app


def png_upload():
    image = Image.new("RGB", (4, 4), color="purple")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


class CaptionApiTests(unittest.TestCase):
    def setUp(self):
        self.received_path = None

        def caption_generator(path):
            self.received_path = path
            self.assertTrue(os.path.exists(path))
            return "A purple square."

        self.app = create_app(caption_generator).test_client()

    def test_existing_model_is_loaded_lazily(self):
        self.assertNotIn("main_working", sys.modules)

    def test_homepage_renders_generator_interface(self):
        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Every picture", response.data)
        self.assertIn(b"Generate caption", response.data)

    def test_caption_endpoint_uses_generator_and_cleans_temporary_upload(self):
        response = self.app.post(
            "/api/caption",
            data={"image": (png_upload(), "sample.png")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"caption": "A purple square."})
        self.assertIsNotNone(self.received_path)
        self.assertFalse(os.path.exists(self.received_path))

    def test_caption_endpoint_rejects_non_image_upload(self):
        response = self.app.post(
            "/api/caption",
            data={"image": (io.BytesIO(b"not an image"), "sample.png")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("valid image", response.get_json()["error"])
        self.assertIsNone(self.received_path)

    def test_caption_endpoint_requires_an_upload(self):
        response = self.app.post("/api/caption")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Choose an image", response.get_json()["error"])

    def test_generation_failure_returns_a_clear_error(self):
        def failing_generator(_path):
            raise RuntimeError("model error")

        app = create_app(failing_generator)
        with self.assertLogs(app.logger, level="ERROR"):
            response = app.test_client().post(
                "/api/caption",
                data={"image": (png_upload(), "sample.png")},
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 500)
        self.assertIn("Caption generation failed", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
