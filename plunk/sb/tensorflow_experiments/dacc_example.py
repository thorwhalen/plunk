import os
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf

from tensorflow.keras import layers
from tensorflow.keras import models
from IPython import display

# Set the seed value for experiment reproducibility.
seed = 42
tf.random.set_seed(seed)
np.random.seed(seed)


DFLT_DATASET_PATH = "data/mini_speech_commands"
DFLT_EPOCHS = 2


def load_dataset(path=DFLT_DATASET_PATH):
    data_dir = pathlib.Path(path)
    if not data_dir.exists():
        tf.keras.utils.get_file(
            "mini_speech_commands.zip",
            origin="http://storage.googleapis.com/download.tensorflow.org/data/mini_speech_commands.zip",
            extract=True,
            cache_dir=".",
            cache_subdir="data",
        )
    return data_dir


def squeeze(audio, labels):
    audio = tf.squeeze(audio, axis=-1)
    return audio, labels


DFLT_CONFIG = dict(
    batch_size=64,
    validation_split=0.2,
    seed=0,
    output_sequence_length=16000,
    subset="both",
)


def get_spectrogram(waveform):
    # Convert the waveform to a spectrogram via a STFT.
    spectrogram = tf.signal.stft(waveform, frame_length=255, frame_step=128)
    # Obtain the magnitude of the STFT.
    spectrogram = tf.abs(spectrogram)
    # Add a `channels` dimension, so that the spectrogram can be used
    # as image-like input data with convolution layers (which expect
    # shape (`batch_size`, `height`, `width`, `channels`).
    spectrogram = spectrogram[..., tf.newaxis]
    return spectrogram


def get_input_shape(ds):
    example, _ = next(iter(ds.take(1)))
    input_shape = example.shape[1:]

    return input_shape


def plot_results(history):
    metrics = history.history
    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    plt.plot(history.epoch, metrics["loss"], metrics["val_loss"])
    plt.legend(["loss", "val_loss"])
    plt.ylim([0, max(plt.ylim())])
    plt.xlabel("Epoch")
    plt.ylabel("Loss [CrossEntropy]")

    plt.subplot(1, 2, 2)
    plt.plot(
        history.epoch,
        100 * np.array(metrics["accuracy"]),
        100 * np.array(metrics["val_accuracy"]),
    )
    plt.legend(["accuracy", "val_accuracy"])
    plt.ylim([0, 100])
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy [%]")


def simple_cnn_model(input_shape, num_labels, norm_layer):
    return models.Sequential(
        [
            layers.Input(shape=input_shape),
            # Downsample the input.
            layers.Resizing(32, 32),
            # Normalize.
            norm_layer,
            layers.Conv2D(32, 3, activation="relu"),
            layers.Conv2D(64, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Dropout(0.25),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(num_labels),
        ]
    )


def string_to_audio(x):
    x = tf.io.read_file(x)
    x, _ = tf.audio.decode_wav(
        x,
        desired_channels=1,
        desired_samples=16000,
    )
    x = tf.squeeze(x, axis=-1)
    x = x[tf.newaxis, :]

    return x


def make_spec_ds(ds):
    return ds.map(
        map_func=lambda audio, label: (get_spectrogram(audio), label),
        num_parallel_calls=tf.data.AUTOTUNE,
    )


class Dacc:
    def __init__(self, directory=DFLT_DATASET_PATH, config=DFLT_CONFIG):
        data_dir = load_dataset(directory)
        self.data_dir = data_dir
        self.config = config

    def train_test_split(self):

        train_ds, val_ds = tf.keras.utils.audio_dataset_from_directory(
            directory=self.data_dir, **self.config
        )
        self.label_names = np.array(train_ds.class_names)

        train_ds = train_ds.map(squeeze, tf.data.AUTOTUNE)
        val_ds = val_ds.map(squeeze, tf.data.AUTOTUNE)
        test_ds = val_ds.shard(num_shards=2, index=0)
        val_ds = val_ds.shard(num_shards=2, index=1)

        return train_ds, test_ds, val_ds

    def preprocess(self):
        train_ds, test_ds, val_ds = self.train_test_split()
        train_spectrogram_ds = make_spec_ds(train_ds)
        val_spectrogram_ds = make_spec_ds(val_ds)
        test_spectrogram_ds = make_spec_ds(test_ds)
        self.train_spectrogram_ds = (
            train_spectrogram_ds.cache().shuffle(10000).prefetch(tf.data.AUTOTUNE)
        )
        self.val_spectrogram_ds = val_spectrogram_ds.cache().prefetch(tf.data.AUTOTUNE)
        self.test_spectrogram_ds = test_spectrogram_ds.cache().prefetch(
            tf.data.AUTOTUNE
        )

        self.input_shape = get_input_shape(train_spectrogram_ds)

        return (
            self.train_spectrogram_ds,
            self.test_spectrogram_ds,
            self.val_spectrogram_ds,
        )

    def mk_model(self):
        input_shape = self.input_shape
        print("Input shape:", input_shape)
        num_labels = len(self.label_names)

        # Instantiate the `tf.keras.layers.Normalization` layer.
        norm_layer = layers.Normalization()
        # Fit the state of the layer to the spectrograms
        # with `Normalization.adapt`.
        norm_layer.adapt(
            data=self.train_spectrogram_ds.map(map_func=lambda spec, label: spec)
        )

        model = simple_cnn_model(input_shape, num_labels, norm_layer)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=["accuracy"],
        )
        return model

    def fit(self, epochs=DFLT_EPOCHS):
        self.preprocess()
        model = self.mk_model()
        history = model.fit(
            self.train_spectrogram_ds,
            validation_data=self.val_spectrogram_ds,
            epochs=epochs,
            callbacks=tf.keras.callbacks.EarlyStopping(verbose=1, patience=2),
        )
        self.history = history
        self.model = model

        return self

    def predict(self, test_ds):
        return self.model.predict(test_ds)

    @tf.function
    def apply_model(self, x):

        # If they pass a string, load the file and decode it.
        if x.dtype == tf.string:
            x = string_to_audio(x)

        x = get_spectrogram(x)
        result = self.model(x, training=False)

        class_ids = tf.argmax(result, axis=-1)
        class_names = tf.gather(self.label_names, class_ids)
        return {
            "predictions": result,
            "class_ids": class_ids,
            "class_names": class_names,
        }


if __name__ == "__main__":
    data_dir = load_dataset()
    dacc = Dacc()

    # fit on CPU takes 2mn
    dacc.fit(epochs=10)

    # test on entire test dataset
    dacc.model.evaluate(dacc.test_spectrogram_ds, return_dict=True)

    # test on one item
    dacc.apply_model(tf.constant(str(data_dir / "no/01bb6a2a_nohash_0.wav")))
