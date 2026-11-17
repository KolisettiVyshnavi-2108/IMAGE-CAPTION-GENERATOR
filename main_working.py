import os
from threading import Lock

from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor


MODEL_NAME = "Salesforce/blip-image-captioning-base"
processor = None
model = None
_model_lock = Lock()


def _load_model():
    global processor, model

    if processor is None or model is None:
        with _model_lock:
            if processor is None or model is None:
                processor = BlipProcessor.from_pretrained(MODEL_NAME)
                model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME)


def generate_caption(image_path):
    """Generate an image caption with the BLIP image-captioning model."""
    _load_model()
    with Image.open(image_path) as image:
        inputs = processor(image.convert("RGB"), return_tensors="pt")
    output = model.generate(**inputs, max_length=50, num_beams=5)
    return processor.decode(output[0], skip_special_tokens=True)


def _run_demo():
    import matplotlib.pyplot as plt

    image_path = (
        r"C:\Users\VYSHNAVI\OneDrive\Desktop\IMAGE CAPTION GENERATOR"
        r"\data\Images\3747543364_bf5b548527.jpg"
    )
    if os.path.exists(image_path):
        caption = generate_caption(image_path)
        print("Generated Caption:", caption)
        print(
            "Expected (ground truth): A child in a pink dress is climbing up a "
            "set of stairs in an entry way ."
        )
        with Image.open(image_path) as image:
            plt.imshow(image)
        plt.axis("off")
        plt.title(f"BLIP Caption: {caption}", fontsize=16, pad=20)
        plt.show()
    else:
        print(f"Image not found: {image_path}")

    print("BLIP zero-shot captioner - works on ANY image (edit path)!")


if __name__ == "__main__":
    _run_demo()
