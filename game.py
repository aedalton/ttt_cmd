import api

import models
import peewee as pw
from config import Config

class GameInitError(Exception):
    """User not in Slack Team"""


class BoardError(Exception):
    """Invalid board state"""

    
def get_current_game(channel_id):
    """ Return the current (only) game set in channel
        channel_id: current channel
    """
    try:
        return models.Game.get(models.Game.channel_id == channel_id)
    except models.Game.DoesNotExist:
        new_game = models.Game(channel_id=channel_id)
        new_game.save()
        return new_game


def get_current_board(channel_id):
    """Retrieve current (active) board in game set / channel
       Args:
         channel_id: channel_id to query Boards
    """
    try:
        return models.Board.select().where(models.Board.game == channel_id,
                                    models.Board.is_active == True).get()
    except models.Board.DoesNotExist:
        raise BoardError("Board does not exist")


def get_piece(board, user):
    """Retrieve marker for space in board
       Args: 
         board: current board
         user: move maker
    """
    if user[0] == Config.TIE:
        return Config.TIE_PIECE
    return Config.P1_PIECE if user[0] == board.player1 else Config.P2_PIECE


def make_challenge(from_user, to_user, channel_id):
    """Return active game set if present, else initialize a new one with players
       Args:
         from_user: player name beloning to command caller
         to_user: player name belonging to mention within command
         channel_id: channel_id of command origin channel
    """
    if not api.check_user_in_channel(check_user=from_user, channel_id=channel_id, value='name') or not \
       api.check_user_in_channel(check_user=to_user, channel_id=channel_id, value='name'):
        raise GameInitError("cannot start game with user not in team")
    
    # check if there is an active board in this channel 
    new_game = get_current_game(channel_id)

    if new_game.active:  # FUTURE IMPROVEMENTS: remove these redundant ops
        board = get_current_board(channel_id)
        option = "\nIts your turn. Please type a move (/ttt +number)" \
                 if from_user == board.next else " "
        
        raise GameInitError("Cannot make a new game because there is an active game in this channel between <@%s> and <@%s>. %s" % (board.player1, board.player2, option))

    try:
        # no active game, make a new one
        board = models.Board(game=new_game, is_active=True, player1=from_user, 
                      player2=to_user, prev=from_user)
        board.save()

    except pw.IntegrityError:  # check constraint
        raise GameInitError("Cannot init a game between the same two players %s and %s" % (from_user, to_user))

    return new_game


def check_for_win(board):
    """Return boolean value for winning set of moves in board
    Args: 
       board: (Board object) the current board in play
    """
    wins = [['0', '1', '2'], ['3', '4', '5'], ['6', '7', '8'], # horizontal
            ['0', '3', '6'], ['1', '4', '7'], ['2', '5', '8'], # vertical
            ['0', '4', '8'], ['2', '4', '6']  # diagonal
            ]
    for win in wins:
        if board.moves > 8:
            return (True, Config.TIE)  # cat's game
        if board.state[win[0]] != Config.BLANK_CHAR and\
           board.state[win[1]] != Config.BLANK_CHAR and\
           board.state[win[2]] != Config.BLANK_CHAR:
            if board.state[win[0]] == \
               board.state[win[1]] and\
               board.state[win[1]] == \
               board.state[win[2]]:
                return (True, board.prev)  # return winner
        
    return (False, board.next)  # game not over


def check_move(board, move, user):
    """ Return boolean value determining validity of move
    Args:
      board: current board
      move: move from text field of command response
      user: user name belonging to command caller/move maker
    """
    move = int(move[0])

    if 0 <= move < 9:
        if user != board.player1 and user != board.player2:
            # potentially should perform user auth, but for the sake of
            # response time, simple auth against board participants
            raise BoardError("Sorry! You are not in this game. Game is between <@%s> and <@%s>" % (board.player1, board.player2))
    
        if user == board.prev: # could have checked above
            raise BoardError("Turn error: Sorry! It is not your turn; it's %s's turn" % (str(board.next)))
        
        elif board.state[str(move)] != Config.BLANK_CHAR:
            raise BoardError("Whoops! Board position %d not empty, please select new" % move)

        else:
            return True
        
    raise BoardError("Move not between positions 1 and 9")  # RET??


def make_move(board, from_user, channel_id, move):
    """ Return game status, next user 
    Args:
      board: current Board object
      from_user: user who called command
      channel_id: channel of command call
      move: integer, first index of list of arguments in text field of command
    """
    if board:
        if check_move(board, move, from_user[0]):
            board.update_state(from_user[0], move)
            game_over, user = check_for_win(board)
            if game_over:
                board.update_is_active()
            return (game_over, user)
    raise BoardError("No Moves Made")
