import tensorflow as tf
import numpy as np
from PIL import Image

TFLITE_FILE_PATH = '../models/7seg2312q.tflite'

# Load the TFLite model in TFLite Interpreter
interpreter = tf.lite.Interpreter(TFLITE_FILE_PATH)
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Test the model on random input data.
input_shape = input_details[0]['shape']

image_in = Image.open('../training/digits_resized/8_19_12_2023_18_48_08.jpg')
test_image = np.array(image_in, dtype="float32")
img = np.reshape(test_image, input_shape)

interpreter.set_tensor(input_details[0]['index'], img)

interpreter.invoke()

# The function `get_tensor()` returns a copy of the tensor data.
# Use `tensor()` in order to get a pointer to the tensor.
output_data = interpreter.get_tensor(output_details[0]['index'])
print(output_data)
print(output_data.argmax())
