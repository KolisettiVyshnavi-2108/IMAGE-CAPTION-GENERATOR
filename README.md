# Frame — AI Image Caption Generator

A responsive web interface for generating real image captions with the existing
Salesforce BLIP image-captioning model in `main_working.py`. The Flask server
accepts JPEG, PNG, and WebP uploads (up to 10 MB) at `POST /api/caption`; the
model is loaded only when the first caption is requested.

## Run locally

1. Install the project dependencies: `python -m pip install -r requirements.txt`
2. Start the app: `python app.py`
3. Open `http://127.0.0.1:5000`

The first generation downloads the `Salesforce/blip-image-captioning-base`
model if it is not already cached and may take longer than subsequent requests.
The existing standalone scripts `main_working.py` and `main_fixed.py` remain
available for their original command-line workflows.

## Verify

Run the API tests with `python -m unittest discover -s tests`. Upload an image
through the page and confirm that the caption is returned from BLIP; the browser
also supports drag-and-drop, preview/removal, copy, regenerate, and light/dark
themes.