import sys
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

MODEL_PATH = "../models/retinal_cnn_inference.keras"

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img = image.img_to_array(img) / 255.0
    return np.expand_dims(img, axis=0)

if __name__ == "__main__":
    img_path = sys.argv[1]

    model = tf.keras.models.load_model(
        MODEL_PATH,
        compile=False
    )

    img_tensor = preprocess_image(img_path)
    raw_score = float(model.predict(img_tensor)[0][0])

    print(f"Raw retinal score: {raw_score:.4f}")
