"""
CNN Architecture — LeNet / VGG-style hybrid
Input : 32 × 32 × 3
Output: 43 classes (GTSRB)

Uses tensorflow.compat.v2.keras — works on TF 2.13, 2.14, 2.15
without Pylance errors or import issues.
"""
import tensorflow as tf

# Safe import that works on ALL TF 2.x versions
keras  = tf.keras
layers = tf.keras.layers
models = tf.keras.models


def build_cnn(num_classes: int = 43,
              input_shape: tuple = (32, 32, 3)) -> tf.keras.Model:

    model = models.Sequential(name="TrafficSignCNN")

    # ── Block 1 ──────────────────────────────────────────────────────────────
    model.add(layers.Conv2D(32, (3, 3), padding="same",
                            activation="relu", input_shape=input_shape))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D((2, 2)))

    # ── Block 2 ──────────────────────────────────────────────────────────────
    model.add(layers.Conv2D(64, (3, 3), padding="same", activation="relu"))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D((2, 2)))

    # ── Block 3 ──────────────────────────────────────────────────────────────
    model.add(layers.Conv2D(128, (3, 3), padding="same", activation="relu"))
    model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling2D((2, 2)))

    # ── Dense head ───────────────────────────────────────────────────────────
    model.add(layers.Flatten())
    model.add(layers.Dense(512, activation="relu"))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(num_classes, activation="softmax"))

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


if __name__ == "__main__":
    m = build_cnn()
    m.summary()
