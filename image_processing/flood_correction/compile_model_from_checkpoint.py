

import tensorflow as tf
from tensorflow.keras.layers import Dense, Conv3D, Conv2D, Flatten, Dropout, MaxPooling3D, MaxPooling2D, Reshape
from tensorflow.keras.callbacks import ModelCheckpoint
import numpy as np

model = tf.keras.models.load_model("color_model")
model.load_weights('tmp/model_improv-04.hdf5')
print("loaded weights")

train_X = np.load("data/data.npy").reshape((-1, 2, 41, 41, 1))
train_Y = np.load("data/result.npy")
print("loaded data")

result = model.evaluate(train_X,  train_Y, verbose=2)
print(result)

model.save("color_model")