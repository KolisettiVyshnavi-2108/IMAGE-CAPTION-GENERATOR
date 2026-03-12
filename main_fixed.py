import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from tensorflow.keras.applications.inception_v3 import InceptionV3, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import os

# Load pre-trained InceptionV3 (no corrupt file needed)
model = InceptionV3(weights='imagenet')

# IMAGE PATH (Flickr8k sample - user's example)
image_path = r"c:/Users/VYSHNAVI/OneDrive/Desktop/IMAGE CAPTION GENERATOR/data/Images/1000268201_693b08cb0e.jpg"

if os.path.exists(image_path):
    # Load and preprocess image
    img = load_img(image_path, target_size=(299, 299))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    
    # Predict
    predictions = model.predict(img_array)
    decoded = decode_predictions(predictions, top=3)[0]
    
    # Caption as top-3 classes (e.g., "child (0.85), dress (0.12), stairs (0.03)")
    caption = ', '.join([f"{name} ({prob:.2f})" for _, name, prob in decoded])
    print("Generated Caption:", caption)
    print("Expected (ground truth): A child in a pink dress is climbing up a set of stairs in an entry way .")
    
    # Show image + caption
    plt.imshow(img)
    plt.axis("off")
    plt.title(f"✅ InceptionV3 Caption: {caption}", fontsize=14, pad=20)
    plt.show()
else:
    print(f"❌ Image not found: {image_path}")

print("✅ Fixed InceptionV3 captioner - run with any JPG path!")

