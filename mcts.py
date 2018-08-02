from __future__ import division # enable float division
import random
from game.board import Board

class MCTSNode:
    def __init__(self, parent, board, won):
        self.parent = parent
        self.board = board
        self.won = won
        self.children = {}
        self.wins = 0
        self.plays = 0

    def select():
        '''
        chooses a child node with probability = relative win ratio
        precondition: node has children
        '''
        sum_ratios = sum({child._get_win_ratio() for child in self.children})
        for child in self.children:
            child_ratio = child._get_win_ratio()
            if random.random() < child_ratio/sum_ratios:
                return child
            else:
                sum_ratios -= child_ratio
        return None

    def expand():
        '''
        add all valid moves as child nodes
        '''
        self.children = {
            Node(self, *self.board.copy().make_move(move, self.player))
            for move in self.board.valid_moves()
        }

    def simulate():
        # get win or loss
        pass

    def update(winner):
        '''
        recursively backpropagates and updates wins/plays of parent nodes
        '''
        self.wins += int(self.board.active_player == winner)
        self.plays += 1
        self.parent.update(winner) if self.parent else pass

    def is_root():
        return self.parent == None

    def is_leaf():
        return len(self.children) == 0

    def _get_win_ratio():
        return 1 if self.wins == 0 and self.plays == 0 else self.wins/self.plays


class MCTSTree:
    def __init__(self):
        root = MCTSNode(None, Board(), False)

    def playout():
        # selection
        curr = self.root
        while not curr.is_leaf():
            curr = curr.select()

        # expansion
        if curr.won:
            winner = curr.board.active_player
        else:
            curr.expand()
            curr = curr.select()
            winner = curr.simulate() # simulation

        # backpropagation
        curr.update(winner)

    def train():
        for _ in range(1000):
            self.playout()

