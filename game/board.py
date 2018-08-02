from bitstring import BitArray

class Board:
    """
    Models a Gomoku board.
    """
    def __init__(self, x_dim=19, y_dim=19):
        self.x_dim = x_dim
        self.y_dim = y_dim
        size = x_dim * y_dim
        self.black = BitArray(int=0, length=size)
        self.white = BitArray(int=0, length=size)

    def get_index(self, x, y):
        return self.x_dim * x + y

    def get_coords(self, index):
        return index // self.x_dim, index % self.x_dim

    def valid_coord(self, x, y):
        return isinstance(x, int) and isinstance(y, int) and\
            x >= 0 and x < self.x_dim and y >= 0 and y < self.y_dim

    def valid_move(self, x, y, player):
        '''
        checks whether given move is valid
        '''
        if not self.valid_coord(x, y):
            return False
        if player != 0 and player != 1:
            return False
        index = self.get_index(x, y)
        return not self.black[index] and not self.white[index]

    def valid_moves(self):
        '''
        returns a list of all valid moves
        '''
        moves = []
        for index in range(self.x_dim * self.y_dim):
            if not self.white[index] and not self.black[index]:
                moves.append(self.get_coords(index))
        return moves

    def is_winning_move(self, x, y, player):
        '''
        returns whether the given move is a winning move
        '''
        if not self.valid_move(x, y, player):
            return False
        if player == 0:
            color = self.black
        else:
            color = self.white
        for dx, dy in [(1, 0), (1, 1), (0, 1), (-1, 1)]:
            cx, cy = x, y
            in_dir = 0
            for _ in range(4):
                cx += dx
                cy += dy
                if not self.valid_coord(cx, cy):
                    break
                index = self.get_index(cx, cy)
                if color[index]:
                    in_dir += 1
                else:
                    break
            cx, cy = x, y
            for _ in range(4 - in_dir):
                cx -= dx
                cy -= dy
                if not self.valid_coord(cx, cy):
                    break
                index = self.get_index(cx, cy)
                if color[index]:
                    in_dir += 1
                else:
                    break
            if in_dir >= 4:
                return True
        return False

    def copy(self):
        '''
        returns a copy of the board
        '''
        copy = Board()
        copy.white = self.white[:]
        copy.black = self.black[:]
        return copy

    def make_move(self, x, y, player):
        '''
        makes the given move on the board

        then returns whether that move won the game
        '''
        assert(self.valid_move(x, y, player))

        index = self.get_index(x, y)

        win = self.is_winning_move(x, y, player)

        if player == 0:
            self.black.set(1, index)

        if player == 1:
            self.white.set(1, index)

        return win

    def __str__(self):
        index = 0
        vals = []
        for x in range(self.x_dim):
            for y in range(self.y_dim):
                if self.black[index]:
                    vals.append('X')
                elif self.white[index]:
                    vals.append('O')
                else:
                    vals.append('.')
                index += 1
            vals.append('\n')
        return ''.join(vals)

    def __repr__(self):
        return str(self.black.bin) + str(self.white.bin)
