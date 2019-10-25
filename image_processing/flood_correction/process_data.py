from __future__ import absolute_import, division, print_function, unicode_literals

# Install TensorFlow

import tensorflow as tf
from tensorflow.keras.layers import Dense, Conv3D, Conv2D, Flatten, Dropout, MaxPooling3D, MaxPooling2D, Reshape
from tensorflow.keras.callbacks import ModelCheckpoint

import numpy as np

model = tf.keras.models.Sequential([
    Conv3D(16, (2, 3, 3), padding='same', activation='relu', input_shape=(2, 41, 41, 1)),
    MaxPooling3D(pool_size=(1, 2, 2), padding='same'),
    Conv3D(32, (2, 3, 3), padding='same', activation='relu', input_shape=(2, 21, 21, 16)),
    MaxPooling3D(pool_size=(2, 2, 2), padding='same'),
    Reshape((11, 11, 32)),
    Conv2D(64, 3, padding='same', activation='relu', input_shape=(1, 11, 11, 32)),
    MaxPooling2D(),
    Flatten(),
    Dense(512, activation='relu'),
    Dropout(0.2),
    Dense(1, activation='relu')
])

model.compile(optimizer='adam',
              loss='mean_squared_error',
              metrics=['accuracy'])



train_X = np.load("data/data.npy").reshape((-1, 2, 41, 41, 1))
train_Y = np.load("data/result.npy")
model = tf.keras.models.load_model("color_model")

#https://machinelearningmastery.com/check-point-deep-learning-models-keras/
filepath="tmp/model_improv-{epoch:02d}.hdf5"
checkpoint = ModelCheckpoint(filepath)
callbacks_list = [checkpoint]


model.fit(train_X, train_Y, epochs=10, callbacks=callbacks_list, verbose=1)


model.save("color_model")




exit()
result = model.evaluate(train_X,  train_Y, verbose=2)