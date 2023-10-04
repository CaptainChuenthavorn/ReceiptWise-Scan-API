# Example TensorFlow Lite conversion command
import tensorflow as tf

saved_model_dir = 'model'
tflite_model = 'output_tflite_model.tflite'

converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir)
tflite_model = converter.convert()
open(tflite_model, "wb").write(tflite_model)
