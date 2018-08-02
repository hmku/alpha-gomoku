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

    def select(self):
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

    def expand(self):
        '''
        add all valid moves as child nodes
        '''
        self.children = {
            Node(self, *self.board.copy().make_move(move, self.player))
            for move in self.board.valid_moves()
        }

    def simulate(self):
        # get win or loss
        pass

    def update(self, win_prob):
        '''
        updates win count of current node
        '''
        self.wins += win_prob
        self.plays += 1

    def is_root(self):
        return self.parent == None

    def is_leaf(self):
        return len(self.children) == 0

    def _get_win_ratio(self):
        return 1 if self.wins == 0 and self.plays == 0 else self.wins/self.plays


class MCTSTree:
    def __init__(self):
        root = MCTSNode(None, Board(), False)

    def playout(self):
        # selection
        curr = self.root
        while not curr.is_leaf():
            curr = curr.select()

        # expansion
        if curr.won:
            win_prob = 1 # active player wins
        else:
            curr.expand()
            curr = curr.select()
            win_prob = curr.simulate() # simulation

        # backpropagation
        while curr.parent is not None:
            curr.update(win_prob)
            curr = curr.parent
            win_prob = 1 - win_prob

    def train(self):
        for _ in range(1000):
            self.playout()

