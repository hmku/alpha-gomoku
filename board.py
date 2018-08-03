from bitstring import BitArray
import numpy as np

class Board:
    """
    Models a Gomoku board.
    """
    def __init__(self, x_dim=19, y_dim=19):
        self.x_dim = x_dim
        self.y_dim = y_dim
        size = x_dim * y_dim
        self.black = np.zeros((self.x_dim, self.y_dim))
        self.white = np.zeros((self.x_dim, self.y_dim))
        self.empty = {index for index in range(size)}
        self.active_player = 0

    def get_index(self, x, y):
        return self.x_dim * x + y

    def get_coords(self, index):
        return index // self.x_dim, index % self.x_dim

    def valid_coord(self, x, y):
        return isinstance(x, int) and isinstance(y, int) and\
            x >= 0 and x < self.x_dim and y >= 0 and y < self.y_dim

    def valid_move(self, move):
        '''
        checks whether given move is valid
        '''
        if isinstance(move, int):
            index = move
            x, y = self.get_coords(index)
        else:
            x, y = move

        if not self.valid_coord(x, y):
            return False
        return not self.black[x, y] and not self.white[x, y]

    def valid_moves(self):
        '''
        returns a set of all valid moves
        '''
        return self.empty

    def is_winning_move(self, move):
        '''
        returns whether the given move is a winning move
        '''
        if not self.valid_move(move):
            return False
        if self.active_player == 0:
            color = self.black
        else:
            color = self.white

        if isinstance(move, int):
            x, y = self.get_coords(move)
        else:
            x, y = move

        for dx, dy in [(1, 0), (1, 1), (0, 1), (-1, 1)]:
            cx, cy = x, y
            in_dir = 0
            for _ in range(4):
                cx += dx
                cy += dy
                if not self.valid_coord(cx, cy):
                    break
                if color[cx, cy]:
                    in_dir += 1
                else:
                    break
            cx, cy = x, y
            for _ in range(4 - in_dir):
                cx -= dx
                cy -= dy
                if not self.valid_coord(cx, cy):
                    break
                if color[cx, cy]:
                    in_dir += 1
                else:
                    break
            if in_dir >= 4:
                return True
        return False

    def as_array(self):
        if self.active_player == 0:
            return [self.black, self.white]
        else:
            return [self.white, self.black]

    def copy(self):
        '''
        returns a copy of the board
        '''
        copy = Board(x_dim = self.x_dim, y_dim = self.y_dim)
        copy.white = self.white.copy()
        copy.black = self.black.copy()
        copy.empty = set(self.empty)
        copy.active_player = self.active_player
        return copy

    def make_move(self, move):
        '''
        makes the given move on the board

        then returns whether that move won the game
        '''
        assert(self.valid_move(move))

        if isinstance(move, int):
            index = move
            x, y = self.get_coords(index)
        else:
            x, y = move
            index = self.get_index(x, y)

        win = self.is_winning_move(move)

        if self.active_player == 0:
            self.black[x, y] = 1
        if self.active_player == 1:
            self.white[x, y] = 1
        self.empty.remove(index)
        self.active_player = 1 - self.active_player

        self.updated = False
        return self, win

    def __str__(self):
        rows = []
        for x in range(self.x_dim):
            row = []
            for y in range(self.y_dim):
                if self.black[x, y]:
                    row.append('X')
                elif self.white[x, y]:
                    row.append('O')
                else:
                    row.append('.')
            rows.append(' '.join(row))
        return '\n'.join(rows)

    def __repr__(self):
        return str(self.black) + str(self.white)
