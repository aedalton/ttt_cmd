import os
import urlparse
import datetime

import peewee as pw
import playhouse.postgres_ext as playhouse
from playhouse.db_url import connect

import utils
from config import Config


db = connect(os.environ.get('DATABASE_URL', None))

class BaseModel(pw.Model):
    class Meta:
        database = db

class Game(BaseModel):
    channel_id = pw.CharField(unique=True) # unique constraint only one

    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        return super(Game, self).save(*args, **kwargs)

    @property
    def active(self):
        if self.boards:
            try:
                return Board.select().where(Board.game == self.channel_id,
                                            Board.is_active == True).get()
            except Board.DoesNotExist:
                return None  # FIXME: improve this catch
        return None

    @property
    def board_count(self):
        return Board.select().where(Board.game == self.channel_id)

    class Meta:
        order_by = ('channel_id',)


def board_default():
    """Return the default dict/JSON for an empty game board
    Left as module-level function for reuse outside of class instead of @staticmethod"""
    bc = Config.BLANK_CHAR
    # could make into loop, but for the sake of simplicity
    return {'0': bc, '1': bc, '2': bc,
            '3': bc, '4': bc, '5': bc,
            '6': bc, '7': bc, '8': bc,
            }


class Board(BaseModel):
    """
    Game State
    """
    game = pw.ForeignKeyField(Game, related_name="boards", to_field="channel_id")
    state = playhouse.JSONField(default=board_default)

    is_active = pw.BooleanField(default=False)
    updated = pw.DateTimeField(default=datetime.datetime.now)

    player1 = pw.CharField()
    player2 = pw.CharField()
    prev = pw.CharField(null=True)
    moves = pw.IntegerField(default=0)

    @property
    def next(self):
        if self.player1 == self.prev:
            return self.player2
        return self.player1

    def update_state(self, user, move):
        if user == self.player1:
            self.state[str(move[0])] = ':x:'
        else:
            self.state[str(move[0])] = ':o:'

        self.prev = user
        self.moves += 1
        self.save()

    def update_is_active(self):
        self.is_active = False
        self.save()

    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        return super(Board, self).save(*args, **kwargs)

    def display(self):
        top = utils.ascii_generator(self.state['0'],
                                    self.state['1'],
                                    self.state['2'])

        middle = utils.ascii_generator(self.state['3'],
                                       self.state['4'],
                                       self.state['5'])

        bottom = utils.ascii_generator(self.state['6'],
                                       self.state['7'],
                                       self.state['8'])

        return top + '\n' + middle + '\n' + bottom

    @classmethod
    def board_count(cls, query):
        return Board.select().where(Board.game == query)

    class Meta:
        constraints = [pw.Check('player1 != player2')]  # (p1 & p2 cannot be the same)
        order_by  = ('updated',)

if __name__ == '__main__':
    db.drop_tables([Game, Board], safe=True)
    pw.create_model_tables([Game, Board])
