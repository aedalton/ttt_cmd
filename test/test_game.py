import sys
import os
import unittest

sys.path.append("../")  # REMOVE hardcoding
import api
import game
import models
import utils
from config import Config

import peewee as pw


def ping():
	api.mention_user(Config.TEST_CHANNEL)

	
def teardown():  # TODO: remove redundancy
    b = get_current_board(Config.TEST_CHANNEL)
    if b:
        b.update_is_active()
		
    return b

def test_data(msg =" "):
	msg = "%s" % msg
	test = {
    "ok": True,
    "ts": "1405895017.000506",
    "channel": "#general",
    "message": {"text": msg}
	}
	return test


class TestGameMethods(unittest.TestCase):
	def test_get_current_game(self):
		with utils.TestBoard() as curr:
			result = game.get_current_game(Config.TEST_CHANNEL)
			self.assertEqual(result.channel_id, Config.TEST_CHANNEL)
			
	def test_make_challenge(self):
		with utils.TestBoard() as curr:
			self.assertEqual(Config.TEST_CHANNEL, curr.board.game_id)
			self.assertEqual(Config.TEST_P1, curr.board.player1)
			self.assertEqual(Config.TEST_P2, curr.board.player2)

		
	def test_make_challenge_with_same_p1_p2(self):
		self.assertRaises(game.GameInitError, game.make_challenge, 
						  Config.TEST_P1, Config.TEST_P1, Config.TEST_CHANNEL)
	
	def test_check_for_win(self):
		with utils.TestBoard() as curr:
			result, user = game.check_for_win(curr.board)
			self.assertEqual(result, False)
			curr.set_board([0,1,2,3,4,5,8])  # winning seq
			result, user = game.check_for_win(curr.board)
			self.assertEqual(result, True)
		with utils.TestBoard() as curr:
			curr.set_board([0,1,2,3,5,6,8])  # winning seq
			result, user = game.check_for_win(curr.board)
			self.assertEqual(result, True)

	def test_check_move(self):
		with utils.TestBoard() as curr:
			# err, func, args
			self.assertRaises(game.BoardError, game.check_move, curr.board, [10], curr.board.next)
	def make_move(self):
		pass


def main():
    unittest.main()

if __name__ == "__main__":
    main()
