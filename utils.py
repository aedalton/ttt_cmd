import game
import models
import api
from config import Config


class TestBoard(object):
    def __init__(self, channel_id=Config.TEST_CHANNEL, p1=Config.TEST_P1, p2=Config.TEST_P2):
        self.game = game.get_current_game(channel_id)
        self.board = self.get_board(p1, p2)
        
    # TODO: @staticmethod
    def get_board(self, p1, p2):
        if not self.game.active:  # fix
            new_board = models.Board(game=self.game, is_active=True, player1=p1, player2=p2, prev=p1)
            new_board.save()
            return new_board
    
    def set_board(self, moves=[0, 1, 2]):
        for idx in moves:
            self.board.state[str(idx)] = game.get_piece(self.board, self.board.next)
            self.board.prev = self.board.next  # improvement: use only props
            
        self.board.save()

    def __enter__(self):
        return self  # or return board?
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        q = models.Board.delete().where(models.Board.game == self.game, models.Board.is_active == True)
        q.execute()
        q = models.Game.delete()
        q.execute()  # TODO: more here to wrap up 


def is_number(s):
    """Util function"""
    try:
        int(s)
        return True
    except ValueError:
        return False


def ascii_generator(*vals):
    ascii_string = '------------------------\n'
    ascii_string += '|'
    for arg in range(len(vals)):
        ascii_string += '  {0: <3}  |'.format(vals[arg])

    return ascii_string

def show_help_screen():
    """Helper method to display pre-formatted help screen
    In the future, I would probably add params and/or derive these
    values from the current board for extensibility
    """
    top = ascii_generator(':zero:', ':one:', ':two:')
    middle = ascii_generator(':three:', ':four:', ':five:')
    bottom = ascii_generator(':six:', ':seven:', ':eight:')

    positions = top + '\n' + middle + '\n' + bottom
    move_tip = "To make a move, type */ttt :zero: - :eight:* \n Positions in board are: \n%s" % positions
    
    next_tip = "\nTo see who is next, type */ttt next*"
    board_tip = "\nTo see the board, type */ttt board*"
    return move_tip + next_tip + board_tip



