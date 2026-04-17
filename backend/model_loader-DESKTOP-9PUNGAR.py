import os
import tensorflow as tf

# Path to trained model
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "models",
    "retinal_cnn_inference.keras"
)

# Load ONCE at startup
retinal_model = tf.keras.models.load_model(
    MODEL_PATH,
    compile=False
)
