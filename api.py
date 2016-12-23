import os
import re

from slackclient import SlackClient

from config import Config
import game
import utils

slack_client = SlackClient(Config.SLACK_TOKEN)


class CommandError(Exception):
	""" Error with command parsing, please re-try"""


def get_command(user, text, channel_id):
	"""
	Return parsed text field of JSON response to command
	Args:
	  username: command caller
	  text: text field of slash command JSON response
	  channel_id: channel_id value of slash command JSON response
	"""
	mentions = re.findall('(@\w*)', text)
	
	if len(mentions) > Config.MENTION_LIMIT:
		raise CommandError("TicTacToe games can only involve two players, sorry!")
	
	text = text.split()
	if '@' in text[0]:	# if someone has been 'at'-mentioned
		new_game = game.make_challenge(from_user=user[0],
								   to_user=text[0][1:],
								   channel_id=channel_id)
		return "Game initialized between <@%s> :x:'s and <@%s> :o:'s; I\
		t's <@%s>'s turn! \n\n %s" % (new_game.active.player1, new_game.active.player2,
									  new_game.active.next, new_game.active.display())

	else:  # check if number
		board = game.get_current_board(channel_id)
		cmd = str(text[0]).lower()
		if 'next' in cmd:
			return "The next turn is <@%s> %s" %\
				(board.next, game.get_piece(board, board.next))
		elif 'board' in cmd:
			return board.display()
		elif 'help' in cmd:
			return utils.show_help_screen()
		elif 'quit' in cmd:
			board.update_is_active()  # IMPRV
			return "Game Over: <@%s|%s> ended the game. Final state of play: \n%s" % (user[0], user[1], board.display())
		elif utils.is_number(text[0]):
			game_over, current_user = game.make_move(board=board, from_user=user,
											 move=text, channel_id=channel_id)
			
			if game_over:
				return "%s \n\n Winner: <@%s|%s> %s" %\
					(board.display(), user[0], user[1], game.get_piece(board, current_user))
			
			return "%s \n\n Next move: <@%s|%s> %s" %\
				(board.display(), user[0], user[1], game.get_piece(board, current_user))

	raise CommandError("didn't find any keywords, please try again")


def get_users_in_team(value='id'):
	"""Return list of all users in slack team
	Args:
	  value: type of information to store in list, i.e. user_name or User_id
	"""
	team_list = slack_client.api_call("users.list")
	try:
		return [[user['id'], user['name']]
				for user in team_list['members'] if not user['deleted']]
	except KeyError as e:
		CommandError("%s: team_list response = %s" % (e, team_list))


def get_users_in_channel(channel_id, value):
	""" Return list of all users in channel cross ref. with users in team
	"""
	users_in_team = get_users_in_team(value=value)
	
	# FUTURE optimization: could remove cross reference with team
	# with other validation; potentially cache results
	users_in_channel = channel_info(channel_id)['members']

	valid_users = []
	for user in users_in_team:
		if user[0] in users_in_channel or user[1] in users_in_channel:
			valid_users.append(user)
	return valid_users


def check_user_in_channel(check_user, channel_id, value):
	""" Return list of all users in channel cross ref. with users in team
	"""
	user_list = get_users_in_channel(channel_id, value='id')

	for user in user_list:
		if check_user == user[0] or check_user == user[1]:
			return True

	raise CommandError("User %s Not in Channel" % check_user)


def lookup_user(user, value='id'):
	""" Return user if found in team
	Args:
	  user: user to search for in team member list returned by API call
	  value: return either the user_id or user_name
	  
	"""
	team_list = get_users_in_team(value=value)

	for member in team_list:
		# remove 'at' symbol
		if user == member[0] or user == member[1] or user[1:] == member[1]:
			return member[0]
	raise CommandError("user not found")  # todo: return err or handle

def list_channels():
	"""Return all channels in team. Utility method for testing"""
	channels_call = slack_client.api_call("channels.list")

	if channels_call['ok']:
		return channels_call['channels']  # raise elsewise?


def channel_info(channel_id):
	"""Return channel info JSON from api call. Utility method for testing"""
	try:
		info = slack_client.api_call("channels.info", channel=channel_id)
		if 'channel' in info:
			return info['channel']
		return slack_client.api_call("groups.info", channel=channel_id)['group']
	except KeyError as e:
		raise CommandError('Key Error: %s: API call returned: %s' % (e, info))
