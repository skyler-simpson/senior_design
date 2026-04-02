"""
Unit tests for character NER training data and game-stat logic.

Run: python test_character_ner.py
Requires spaCy + trained model only for integration tests (skipped otherwise).
"""

import importlib.util
import unittest

import character_ner_training_data as td
from character_ner_inference import (
    calculate_game_stats,
    validate_extraction_and_stats,
)


class TestTrainingData(unittest.TestCase):
    def test_at_least_100_examples(self):
        self.assertGreaterEqual(len(td.TRAINING_DATA), 100)

    def test_validate_passes(self):
        td.validate_training_data()

    def test_labels_used(self):
        labels = set()
        for _, ann in td.TRAINING_DATA:
            for _, _, lab in ann["entities"]:
                labels.add(lab)
        for expected in (
            "HEIGHT",
            "SPECIES",
            "ELEMENT",
            "PRIMARY_COLOR",
            "SECONDARY_COLOR",
            "CLOTHING",
            "EQUIPMENT",
            "SPECIAL_TRAIT",
            "FACIAL_FEATURE",
            "BUILD",
            "MARKING",
            "ARMOR_DETAIL",
        ):
            self.assertIn(expected, labels)


class TestGameStats(unittest.TestCase):
    def test_stats_in_range(self):
        attrs = {
            "height": "tall",
            "species": "knight",
            "element": "fire",
            "special_traits": ["fierce"],
            "equipment": ["steel longsword"],
            "clothing": ["plate armor"],
            "armor_details": ["greaves"],
        }
        stats = calculate_game_stats(attrs)
        for k in ("speed", "jump_velocity", "damage_amount"):
            self.assertIn(k, stats)
            self.assertGreaterEqual(stats[k], 0)
            self.assertLessEqual(stats[k], 100)

    def test_mage_damage_lower_than_warrior(self):
        warrior = calculate_game_stats(
            {"species": "knight", "equipment": ["sword"], "height": "tall"}
        )
        mage = calculate_game_stats(
            {"species": "mage", "equipment": ["wand"], "element": "fire", "height": "average"}
        )
        self.assertGreater(warrior["damage_amount"], mage["damage_amount"])

    def test_no_attack_keys(self):
        attrs = {"species": "rogue", "equipment": ["dagger"]}
        stats = calculate_game_stats(attrs)
        self.assertNotIn("attack1_strength", stats)
        self.assertNotIn("attack2_strength", stats)
        self.assertNotIn("jump_height", stats)


class TestValidation(unittest.TestCase):
    def test_high_damage_low_speed_warning(self):
        attrs = {"species": "knight", "equipment": ["sword"]}
        game = {"damage_amount": 90, "speed": 20, "jump_velocity": 40}
        v = validate_extraction_and_stats("A warrior", attrs, game)
        self.assertTrue(any("damage" in w.lower() for w in v.get("stat_warnings", [])))


@unittest.skipUnless(importlib.util.find_spec("spacy"), "spaCy not installed")
class TestIntegration(unittest.TestCase):
    """Load a trained model and run the full pipeline (optional)."""

    @classmethod
    def setUpClass(cls):
        import os

        from character_ner_inference import DEFAULT_MODEL_PATH, generate_json_response, load_model

        # staticmethod: plain functions on the class would otherwise bind `self` as the first arg.
        cls._generate = staticmethod(generate_json_response)
        if not os.path.isdir(DEFAULT_MODEL_PATH):
            raise unittest.SkipTest("Trained model directory missing")
        cls._nlp = load_model(DEFAULT_MODEL_PATH)
        if cls._nlp is None:
            raise unittest.SkipTest("Could not load model")

    def test_sample_prompt_json(self):
        r = self._generate(
            "A tall fire wizard with crimson robes and a staff",
            self._nlp,
        )
        self.assertTrue(r["success"])
        self.assertIn("game_stats", r)
        gs = r["game_stats"]
        self.assertEqual(set(gs.keys()), {"speed", "jump_velocity", "damage_amount"})


if __name__ == "__main__":
    unittest.main()
