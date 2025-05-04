import numpy as np
import joblib
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Layer
import tensorflow as tf

# Define fuzzy layer again (must match training definition)


class FuzzyMembershipLayer(Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self, input_shape):
        self.aqi_low = self._create_tf_trimf(0, 0, 50)
        self.aqi_mod = self._create_tf_trimf(35, 75, 125)
        self.aqi_high = self._create_tf_trimf(100, 175, 300)
        self.aqi_severe = self._create_tf_trimf(250, 400, 500)

        self.pm25_low = self._create_tf_trimf(0, 0, 15)
        self.pm25_mod = self._create_tf_trimf(10, 25, 40)
        self.pm25_high = self._create_tf_trimf(35, 50, 75)
        self.pm25_severe = self._create_tf_trimf(60, 100, 250)

        self.risk_low = self._create_tf_trimf(0, 0, 25)
        self.risk_mod = self._create_tf_trimf(20, 50, 80)
        self.risk_high = self._create_tf_trimf(70, 85, 100)

    def _create_tf_trimf(self, a, b, c):
        def trimf(x):
            return tf.maximum(tf.minimum((x - a) / (b - a + 1e-7), (c - x) / (c - b + 1e-7)), 0.0)
        return trimf

    def call(self, inputs):
        aqi = inputs[:, 0]
        pm25 = inputs[:, 2]
        aqi_mem = {
            'low': self.aqi_low(aqi),
            'mod': self.aqi_mod(aqi),
            'high': self.aqi_high(aqi),
            'severe': self.aqi_severe(aqi)
        }
        pm25_mem = {
            'low': self.pm25_low(pm25),
            'mod': self.pm25_mod(pm25),
            'high': self.pm25_high(pm25),
            'severe': self.pm25_severe(pm25)
        }

        rule1 = tf.minimum(aqi_mem['low'], pm25_mem['low'])
        rule2 = tf.minimum(aqi_mem['mod'], pm25_mem['mod'])
        rule3 = tf.minimum(aqi_mem['high'], pm25_mem['high'])
        rule4 = tf.minimum(aqi_mem['severe'], pm25_mem['severe'])

        risk_low = rule1 * self.risk_low(tf.constant(12.5))
        risk_mod = rule2 * self.risk_mod(tf.constant(50.0))
        risk_high = (rule3 + rule4) * self.risk_high(tf.constant(85.0))

        numerator = risk_low + risk_mod + risk_high
        denominator = rule1 + rule2 + rule3 + rule4 + 1e-7
        crisp_output = numerator / denominator
        return tf.reshape(crisp_output, (-1, 1))


# Load assets (model and scaler)
model = load_model(
    "../models/health_impact_predictor_model.keras",
    custom_objects={"FuzzyMembershipLayer": FuzzyMembershipLayer}
)
scaler = joblib.load("../models/health_impact_predictor_scaler.pkl")


def predict_health_impact(features: list[float]) -> tuple[float, int]:
    scaled_input = scaler.transform(np.array([features]))
    score, class_probs = model.predict(scaled_input)
    risk_class = np.argmax(class_probs[0])
    return float(score[0][0]), int(risk_class)
