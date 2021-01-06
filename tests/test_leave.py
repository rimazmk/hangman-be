import unittest
import copy

from .default_vars import state, params, default_state
from hangman import db, game, routes


class TestLeave(unittest.TestCase):
    def test_handle_leave_empty(self):
        obj = copy.deepcopy(state)
        res = copy.deepcopy(obj)
        game.handle_leave(res, "")
        self.assertEqual(res, obj)

    def test_handle_leave_two(self):
        obj = copy.deepcopy(state)
        changes = {
            "players": ["vthirupathi", "ssrihari"],
            "wins": {"vthirupathi": 1, "ssrihari": 2}
        }

        obj.update(changes)
        res = copy.deepcopy(obj)
        game.handle_leave(res, "rimazk")

        correct = default_state.copy()
        correct_updates = {
            "players": ["vthirupathi"],
            "hanger": "vthirupathi",
            "lives": 6,
            "rotation": "robin",
            "numRounds": 10,
            "time": 30,
            "wins": {"vthirupathi": 0}
        }
        correct.update(correct_updates)
        self.assertDictEqual(res, correct)

    def test_handle_player_leave(self):
        obj = copy.deepcopy(state)
        res = copy.deepcopy(obj)
        game.handle_leave(res, "rimazk")
        correct = {
            "players": ["ssrihari", "vthirupathi"],
            "wins": {"ssrihari": 1, "vthirupathi": 4},
        }
        obj.update(correct)
        self.assertDictEqual(res, obj)

    def test_handle_guesser_leave(self):
        obj = copy.deepcopy(state)
        res = copy.deepcopy(obj)
        game.handle_leave(res, "vthirupathi")
        correct = {
            "players": ["ssrihari", "rimazk"],
            "wins": {"ssrihari": 1, "rimazk": 3},
            "guesser": "rimazk",
        }
        obj.update(correct)
        self.assertDictEqual(res, obj)

    def test_handle_hanger_leave(self):
        obj = copy.deepcopy(state)
        res = copy.deepcopy(obj)
        game.handle_leave(res, "ssrihari")
        correct = {
            "players": ["vthirupathi", "rimazk"],
            "wins": {"vthirupathi": 4, "rimazk": 3},
            "hanger": "vthirupathi",
            "guesser": "rimazk",
            "word": "",
            "category": ""
        }
        obj.update(correct)
        self.assertDictEqual(res, obj)
