import tensorflow as tf

MODEL_PATH = "../models/retinal_cnn_final.keras"

retinal_model = tf.keras.models.load_model(MODEL_PATH)
