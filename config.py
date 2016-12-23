import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	DEBUG = False
	TESTING = False
	CSRF_ENABLED = True
	
	SLACK_TOKEN = os.environ.get('SLACK_TOKEN', None)
	SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')

	DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/tictactest')
	
	# Testing	
	TEST_CHANNEL = 'G3GBUQ95G'
	GENERAL_CHANNEL = 'C3A2E8E92'
	TEST_P1 = 'oxo'	 #'U3A2R01BP' # @oxo
	TEST_P1_ID = 'U3A2R01BP'
	TEST_P2 = 'player2' #'U3DVAB31P' # @rival
	TEST_P2_ID = 'U3DVAB31P'

	# Game specific Constants
	BLANK_CHAR = '____'
	P1_PIECE = ":x:"
	P2_PIECE = ":o:"
	TIE = "tie"
	TIE_PIECE = ":smirk_cat"
	MENTION_LIMIT = 1  # 2 players per game


class TestingConfig(Config):
	TESTING = True
	DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/tictactest'

class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True


class StagingConfig(Config):
	DEVELOPMENT = True
	DEBUG = True


class ProductionConfig(Config):
	DEBUG = False
