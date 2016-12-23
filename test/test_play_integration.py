import os
import sys

import unittest
import tempfile
import json

import peewee as pw
from playhouse.db_url import connect

sys.path.append("../")  # REMOVE hardcoding

import config
import models
import api
import game

class AppTestCase(unittest.TestCase):
	def setUp(self):
		models.app.config.from_object('config.TestingConfig')
		self.app = models.app.test_client()
		models.db.create_tables([models.Game, models.Board], safe=True)

	def tearDown(self):
		models.db.drop_tables([models.Board, models.Game], safe=True)  # create on
		
	def cmd(self, user, text_):  # need to set userid? 
		payload = {'token': config.Config.SLACK_WEBHOOK_SECRET, 
				   'channel_id': config.Config.TEST_CHANNEL,
				   'user_name': user[0],
				   'user_id': user[1],
				   'command': '/ttt',
				   'text': text_,
				   'response_url': 'https://hooks.slack.com/commands/'\
				   'T398TAD1N/118994401605/9c3Sqg2Qd8re4xbHnxVRDLwk'
		}  # hardcoded res_url for testing purposes
		
		r = self.app.post('/ttt', data=payload)

		return r
	
	def test_next_in_cmd(self):
		user1 = [config.Config.TEST_P1, config.Config.TEST_P1_ID]
		res = self.cmd(user1, text_='next')
		self.assertIn('NEXT command issued', res.data)

	def test_mention_in_cmd(self):
		user1 = [config.Config.TEST_P1, config.Config.TEST_P1_ID]
		res = self.cmd(user1, text_='@player2')
		self.assertIn('@', res.data)

	def test_player2_win_horz(self):
		user1 = [config.Config.TEST_P1, config.Config.TEST_P1_ID]
		user2 = [config.Config.TEST_P2, config.Config.TEST_P2_ID]
		self.cmd(user1, text_='@%s' % config.Config.TEST_P2)
		# probably would put these in a loop
		self.cmd(user2, text_='0')
		self.cmd(user1, text_='3')
		self.cmd(user2, text_='1')
		self.cmd(user1, text_='4')
		
		check_for_win = game.check_for_win(game.get_current_board(config.Config.TEST_CHANNEL))
		self.assertEqual(check_for_win[0], False)
		
		res = self.cmd(user2, text_='2')
		self.assertIn('Winner: <@%s|%s>' %(user2[0], user2[1]), res.data)
		self.assertRaises(game.BoardError, game.get_current_board, config.Config.TEST_CHANNEL)
		
	def test_player2_win_vert(self):
		user1 = [config.Config.TEST_P1, config.Config.TEST_P1_ID]
		user2 = [config.Config.TEST_P2, config.Config.TEST_P2_ID]
		
		self.cmd(user1, text_='@%s' % config.Config.TEST_P2)
		self.cmd(user2, text_='0')
		self.cmd(user1, text_='1')
		self.cmd(user2, text_='3')
		self.cmd(user1, text_='2')
		
		check_for_win = game.check_for_win(game.get_current_board(config.Config.TEST_CHANNEL))
		self.assertEqual(check_for_win[0], False)
		
		res = self.cmd(user2, text_='6')
		self.assertIn('Winner: <@%s|%s>' % (user2[0], user2[1]), res.data)
		self.assertRaises(game.BoardError, game.get_current_board, config.Config.TEST_CHANNEL)
		
	def test_new_game_req_with_active_game(self):
		user1 = [config.Config.TEST_P1, config.Config.TEST_P1_ID]
		user2 = [config.Config.TEST_P2, config.Config.TEST_P2_ID]
		
		self.cmd(user1, text_='@%s' % config.Config.TEST_P2)
		
		self.assertRaises(game.GameInitError, api.get_command, user=user1, text='@%s' % config.Config.TEST_P2, channel_id=config.Config.TEST_CHANNEL) 

	def test_quit_active_game(self):
		user1 = [config.Config.TEST_P1, config.Config.TEST_P1_ID]
		user2 = [config.Config.TEST_P2, config.Config.TEST_P2_ID]
		
		self.cmd(user1, text_='@%s' % config.Config.TEST_P2)
		curr_game = game.get_current_game(config.Config.TEST_CHANNEL)
		curr_board = game.get_current_board(config.Config.TEST_CHANNEL)
		self.assertEqual(curr_board.is_active, True)
		self.cmd(user2, text_='quit')
		self.assertRaises(game.BoardError, game.get_current_board, config.Config.TEST_CHANNEL)

		
if __name__ == '__main__':
	unittest.main()

