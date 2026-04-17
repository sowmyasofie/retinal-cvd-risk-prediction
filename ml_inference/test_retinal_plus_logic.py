import tensorflow as tf
import numpy as np
from risk_logic import compute_final_risk
from tensorflow.keras.preprocessing import image

MODEL_PATH = "../models/retinal_cnn_inference.keras"

def preprocess(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img = image.img_to_array(img) / 255.0
    return np.expand_dims(img, axis=0)

model = tf.keras.models.load_model(MODEL_PATH, compile=False)

img_path = "test_image.jpg"   # any EyePACS image
img_tensor = preprocess(img_path)

raw_score = float(model.predict(img_tensor)[0][0])
print("Raw retinal score:", raw_score)

result = compute_final_risk(
    raw_retinal_score=raw_score,
    age=45,
    sys_bp=130,
    dia_bp=85,
    diabetes_status="no"
)

print("Final decision:", result)
