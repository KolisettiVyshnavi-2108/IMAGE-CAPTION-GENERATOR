import matplotlib.pyplot as plt
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import numpy as np
import os

# Load BLIP model and processor (Salesforce/blip-image-captioning-base)
# First run downloads ~500MB model automatically
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_caption(image_path):
    """Generate caption using BLIP zero-shot model."""
    # Load and preprocess image
    raw_image = Image.open(image_path).convert('RGB')
    inputs = processor(raw_image, return_tensors="pt")
    
    # Generate caption
    out = model.generate(**inputs, max_length=50, num_beams=5)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

# IMAGE PATH (Flickr8k sample - user's example)
image_path = r"C:\Users\VYSHNAVI\OneDrive\Desktop\IMAGE CAPTION GENERATOR\data\Images\3747543364_bf5b548527.jpg"

# Generate caption
if os.path.exists(image_path):
    caption = generate_caption(image_path)
    print("Generated Caption:", caption)
    print("Expected (ground truth): A child in a pink dress is climbing up a set of stairs in an entry way .")
    
    # Show image + caption
    image = Image.open(image_path)
    plt.imshow(image)
    plt.axis("off")
    plt.title(f"✅ BLIP Caption: {caption}", fontsize=16, pad=20)
    plt.show()
else:
    print(f"❌ Image not found: {image_path}")

print("✅ BLIP zero-shot captioner - works on ANY image (edit path)!")

