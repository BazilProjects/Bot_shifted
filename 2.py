import os
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense

# Create a simple model
model = Sequential([
    Dense(32, activation='relu', input_shape=(10,)),
    Dense(16, activation='relu'),
    Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mse')

# Test with random data
import numpy as np
x = np.random.random((100, 10))
y = np.random.random((100, 1))

model.fit(x, y, epochs=5, batch_size=8)


print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
