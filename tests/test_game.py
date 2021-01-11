import unittest
import copy

from .default_vars import state, params, default_state
from hangman import db, game, routes


class TestGame(unittest.TestCase):

    def test_new_round_reset_guessed_word(self):
        obj = state.copy()
        game.handle_new_round(obj, "animals", "cat", "ngur")
        self.assertEqual(obj['guessedWord'], '___')

    def test_new_round_hanger_robin(self):
        obj = state.copy()
        game.handle_new_round(obj, "animals", "cat", "ssrihari")
        self.assertEqual(obj['hanger'], 'vthirupathi')

    def test_new_round_hanger_king(self):
        obj = state.copy()
        obj['rotation'] = 'king'
        game.handle_new_round(obj, "animals", "cat", "ssrihari")
        self.assertEqual(obj['hanger'], 'ssrihari')

    def test_new_round_guesser_notend(self):
        obj = state.copy()
        game.handle_new_round(obj, "animals", "cat", "ssrihari")
        self.assertEqual(obj['guesser'], 'rimazk')

    def test_new_round_guesser_end(self):
        obj = state.copy()
        obj['hanger'] = 'rimazk'
        obj['rotation'] = 'king'
        obj['numIncorrect'] = obj['lives']
        game.handle_new_round(obj, "animals", "cat", "ssrihari")
        self.assertEqual(obj['guesser'], 'ssrihari')

    def test_new_round_numincorrect(self):
        obj = state.copy()
        game.handle_new_round(obj, "animals", "cat", "ssrihari")
        self.assertEqual(obj['numIncorrect'], 0)

    def test_new_round_round_increase(self):
        obj = state.copy()
        game.handle_new_round(obj, "animals", "cat", "ssrihari")
        self.assertEqual(obj['round'], 3)

    def test_guess_word_wrong(self):
        obj = state.copy()
        game.guess(obj)
        self.assertIn(obj['curGuess'], obj['guessedWords'])
        self.assertEqual(obj['numIncorrect'], 4)

    def test_guess_word_correct(self):
        obj = state.copy()
        obj['curGuess'] = 'zebra'
        game.guess(obj)
        self.assertTrue(len(obj['guessedWords'])==0)
        self.assertEqual(obj['numIncorrect'], 3)

    def test_guess_letter_wrong(self):
        obj = state.copy()
        obj['curGuess'] = 'q'
        game.guess(obj)
        self.assertIn(obj['curGuess'], obj['guessedLetters'])
        self.assertEqual(obj['numIncorrect'], 4)

    def test_guess_letter_correct(self):
        obj = state.copy()
        obj['curGuess'] = 'z'
        game.guess(obj)
        self.assertIn(obj['curGuess'], obj['guessedLetters'])
        self.assertEqual(obj['numIncorrect'], 3)
    def test_guess_empty_cur(self):
        obj = state.copy()
        obj['curGuess'] = ''
        game.guess(obj)
        self.assertNotIn(obj['curGuess'], obj['guessedLetters'])
        self.assertEqual(obj['numIncorrect'], 4)
        
    # def test_guess_NonLowerCase_correct(self):
    #     obj = state.copy()
    #     obj['curGuess'] = 'ZEBRA9$'
    #     game.guess(obj)
    #     self.assertTrue(len(obj['guessedWords'])==0)
    #     self.assertEqual(obj['numIncorrect'], 3)

    def test_guess_win_round(self):
        obj = state.copy()
        obj['curGuess'] = 'zebra'
        game.guess(obj)
        self.assertTrue(obj['wins']['vthirupathi'] == 5)
        self.assertEqual(obj['category'], "")
        self.assertEqual(obj['curGuess'], "")
        self.assertEqual(obj['guessedWord'], "")
        self.assertTrue(len(obj['guessedWords'])==0)
        self.assertTrue(len(obj['guessedLetters'])==0)


    def test_set_new_guessers(self):
        obj = copy.deepcopy(state)
        game.set_new_guesser(obj)
        self.assertEqual(obj['guesser'], 'rimazk')
        
        # One guesser
        obj = copy.deepcopy(state)
        changes = {
            "players": ["ssrihari", "vthirupathi"],
            "wins": {"ssrihari": 1, "vthirupathi": 4}
        }
        obj.update(changes)
        game.set_new_guesser(obj)
        self.assertEqual(obj['guesser'], 'vthirupathi')

    
