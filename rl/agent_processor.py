import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
from settings import *
from tensorflow.python.compiler.tensorrt import trt_convert as trt
from tensorflow.python.saved_model import tag_constants
import sys
import os


class AgentProcessor:
    def __init__(self, viewport):
        self.viewport = viewport

        self.model = None
        self.model_path = os.path.join(os.path.dirname(__file__), "models", str(id(self)))

        self.build_model()
        # self.optimize_model()

        self.randomize()

    # z q s d space l_up l_left l_down l_right place destroy
    def build_model(self):
        model = tf.keras.models.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.viewport),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.Flatten(),
            layers.Dense(64, activation='relu'),
            layers.Dense(11, activation='softmax')
        ])

        model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                      metrics=['accuracy'])
        # save model
        # model.save(self.model_path)
        self.model = model

    # requires a GPU
    def optimize_model(self):
        # path is rl/models/[agent_id]
        path = os.path.join(os.path.dirname(__file__), "models", str(id(self)))
        dir_path = os.path.join(path, "trt_optimized_model")
        converter = tf.experimental.tensorrt.Converter(input_saved_model_dir=path)
        converter.convert()
        converter.save("trt_optimized_model")
        self.model = tf.saved_model.load(dir_path, tags=[tag_constants.SERVING])
        signature_keys = list(self.model.signatures.keys())
        self.graph_func = self.model.signatures[signature_keys[0]]
    
    def predict_rt(self, stream):
        stream = np.expand_dims(stream, axis=0)
        return self.graph_func(stream)

    def predict(self, stream):
        # save img as file
        stream = np.expand_dims(stream, axis=0)
        return self.model.predict(stream, verbose=0, workers=8, use_multiprocessing=True)

    def set_weights(self, weights):
        self.model.set_weights(weights)
    
    def get_weights(self):
        return self.model.get_weights()

    def randomize(self):
        # randomize each models weights
        weights = self.model.get_weights()
        for i in range(len(weights)):
            weights[i] = np.random.uniform(-1, 1, weights[i].shape)
        self.model.set_weights(weights)

    def mutate(self):
        # mutate each models weights
        weights = self.model.get_weights()
        for i in range(len(weights)):
            for j in range(len(weights[i])):
                if np.random.uniform(0, 1) > 0.85:
                    change = np.random.uniform(-1, 1)
                    weights[i][j] += change
        self.model.set_weights(weights)
        return self.model.get_weights()
