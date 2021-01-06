import unittest

from .default_vars import state, params, default_state
from hangman import game


class TestUtils(unittest.TestCase):
    def test_create_inf(self):
        obj = params.copy()
        obj['time'] = 'inf'
        res = game.create_game(obj)

        correct = default_state.copy()
        changes = {
            'players': ['ngur'],
            'wins': {'ngur': 0},
            'hanger': 'ngur',
            'lives': 7,
            'rotation': 'robin',
            'numRounds': 8,
            'time': None
        }

        correct.update(changes)
        self.assertEqual(res, correct)

    def test_create_not_inf(self):
        obj = params.copy()
        res = game.create_game(obj)
        correct = default_state.copy()
        changes = {
            'players': ['ngur'],
            'wins': {'ngur': 0},
            'hanger': 'ngur',
            'lives': 7,
            'rotation': 'robin',
            'numRounds': 8,
            'time': 30
        }

        correct.update(changes)
        self.assertEqual(res, correct)

    def test_start_game(self):
        obj = state.copy()
        obj['gameStart'] = False

        game.start_game(obj)

        self.assertTrue(obj['gameStart'])
        self.assertEqual(obj['guesser'], 'vthirupathi')

    def test_add_player(self):
        obj = state.copy()
        user = 'ngur'
        game.add_player(obj, user)

        self.assertIn(user, obj['players'])
        self.assertIn(user, obj['wins'])
        self.assertEqual(obj['wins'][user], 0)

    def test_remove_valid_player(self):
        obj = state.copy()
        player = 'rimazk'

        game.remove_player(obj, player)

        self.assertNotIn(player, obj['players'])
        self.assertNotIn(player, obj['wins'])
