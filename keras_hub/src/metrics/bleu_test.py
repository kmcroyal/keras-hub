import keras
import pytest
import tensorflow as tf

from keras_hub.src.metrics.bleu import Bleu
from keras_hub.src.tests.test_case import TestCase
from keras_hub.src.tokenizers.byte_tokenizer import ByteTokenizer


class BleuTest(TestCase):
    def test_initialization(self):
        bleu = Bleu()
        result = bleu.result()

        self.assertEqual(result, 0.0)

    def test_scalar_input(self):
        bleu = Bleu(smooth=True)
        y_true = [
            "He eats a sweet apple.",
            "He is eating a tasty apple, isn't he?",
        ]
        y_pred = "He He He eats sweet apple which is a fruit."

        bleu_val = bleu(y_true, y_pred)
        self.assertAlmostEqual(bleu_val, 0.212, delta=1e-3)

    def test_1d_list_input(self):
        bleu = Bleu()
        y_true = [
            ["He eats a sweet apple."],
            ["Silicon Valley is one of my favourite shows!"],
        ]
        y_pred = [
            "He He He eats sweet apple which is a fruit.",
            "I love Silicon Valley, it's one of my favourite shows.",
        ]

        bleu_val = bleu(y_true, y_pred)
        self.assertAlmostEqual(bleu_val, 0.243, delta=1e-3)

    def test_2d_list_input(self):
        bleu = Bleu()
        y_true = [
            [["He eats a sweet apple."]],
            [["Silicon Valley is one of my favourite shows!"]],
        ]
        y_pred = [
            ["He He He eats sweet apple which is a fruit."],
            ["I love Silicon Valley, it's one of my favourite shows."],
        ]

        bleu_val = bleu(y_true, y_pred)
        self.assertAlmostEqual(bleu_val, 0.243, delta=1e-3)

    def test_custom_tokenizer(self):
        byte_tokenizer = ByteTokenizer()
        bleu = Bleu(tokenizer=byte_tokenizer)
        y_true = [
            ["He eats a sweet apple."],
            ["Silicon Valley is one of my favourite shows!"],
        ]
        y_pred = [
            "He He He eats sweet apple which is a fruit.",
            "I love Silicon Valley, it's one of my favourite shows.",
        ]

        bleu_val = bleu(y_true, y_pred)
        self.assertAlmostEqual(bleu_val, 0.609, delta=1e-3)

    def test_different_order(self):
        bleu = Bleu(max_order=5)
        y_true = [
            ["He eats a sweet apple."],
            ["Silicon Valley is one of my favourite shows!"],
        ]
        y_pred = [
            "He He He eats sweet apple which is a fruit.",
            "I love Silicon Valley, it's one of my favourite shows.",
        ]

        bleu_val = bleu(y_true, y_pred)
        self.assertAlmostEqual(bleu_val, 0.188, delta=1e-3)

    def test_tensor_input(self):
        bleu = Bleu()
        y_true = tf.constant(
            [
                ["He eats a sweet apple."],
                ["Silicon Valley is one of my favourite shows!"],
            ]
        )
        y_pred = tf.constant(
            [
                "He He He eats sweet apple which is a fruit.",
                "I love Silicon Valley, it's one of my favourite shows.",
            ]
        )

        bleu_val = bleu(y_true, y_pred)
        self.assertAlmostEqual(bleu_val, 0.243, delta=1e-3)

    @pytest.mark.tf_only  # string model output only applies to tf.
    def test_model_compile(self):
        inputs = keras.Input(shape=(), dtype="string")
        outputs = keras.layers.Identity()(inputs)
        model = keras.Model(inputs, outputs)
        model.compile(metrics=[Bleu()])

        y_pred = x = tf.constant(
            [
                "He He He eats sweet apple which is a fruit.",
                "I love Silicon Valley, it's one of my favourite shows.",
            ]
        )
        y = tf.constant(
            [
                ["He eats a sweet apple."],
                ["Silicon Valley is one of my favourite shows!"],
            ]
        )

        output = model.compute_metrics(x, y, y_pred, sample_weight=None)
        self.assertAlmostEqual(output["bleu"], 0.243, delta=1e-3)

    def test_reset_state(self):
        bleu = Bleu()
        y_true = [
            ["He eats a sweet apple."],
            ["Silicon Valley is one of my favourite shows!"],
        ]
        y_pred = [
            "He He He eats sweet apple which is a fruit.",
            "I love Silicon Valley, it's one of my favourite shows.",
        ]

        bleu.update_state(y_true, y_pred)
        bleu_val = bleu.result()
        self.assertNotEqual(bleu_val, 0.0)

        bleu.reset_state()
        bleu_val = bleu.result()
        self.assertEqual(bleu_val, 0.0)

    def test_update_state(self):
        bleu = Bleu()
        y_true_1 = [
            ["He eats a sweet apple."],
            ["Silicon Valley is one of my favourite shows!"],
        ]
        y_pred_1 = [
            "He He He eats sweet apple which is a fruit.",
            "I love Silicon Valley, it's one of my favourite shows.",
        ]

        bleu.update_state(y_true_1, y_pred_1)
        bleu_val = bleu.result()
        self.assertAlmostEqual(bleu_val, 0.243, delta=1e-3)

        y_true_2 = ["Virat Kohli is the GOAT."]
        y_pred_2 = "Virat Kohli is the greatest of all time!"

        bleu.update_state(y_true_2, y_pred_2)
        bleu_val = bleu.result()
        self.assertAlmostEqual(bleu_val, 0.26, delta=1e-3)

    def test_get_config(self):
        byte_tokenizer = ByteTokenizer()
        bleu = Bleu(
            tokenizer=byte_tokenizer,
            max_order=8,
            smooth=True,
            dtype=tf.float64,
            name="bleu_test",
        )

        config = bleu.get_config()
        expected_config_subset = {
            "tokenizer": byte_tokenizer,
            "max_order": 8,
            "smooth": True,
        }
        self.assertEqual(config, {**config, **expected_config_subset})