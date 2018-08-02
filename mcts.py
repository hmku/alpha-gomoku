from __future__ import division # enable float division
import random
import numpy as np

from game.board import Board


class MCTSNode:
    def __init__(self, board, won, parent=None, last_move=None):
        self.board = board
        self.won = won
        self.parent = parent
        self.last_move = last_move
        self.children = {}
        self.wins = 0
        self.plays = 0

    def select(self):
        '''
        chooses a child node with probability = relative win ratio
        '''
        assert not self.is_leaf()
        max_weight = 0
        for child in self.children:
            if np.random.beta(child.wins+1, child.plays-child.wins+1) > max_weight:
                max_weight = weight
                max_child = child
        return max_child

    def expand(self):
        '''
        add all valid moves as child nodes
        '''
        self.children = {
            Node(*self.board.copy().make_move(move, self.player), self, move)
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

    def get_win_ratio(self):
        return 1 if self.wins == 0 and self.plays == 0 else self.wins/self.plays


class MCTSTree:
    def __init__(self, playouts=1000):
        root = MCTSNode(Board(), False)
        playouts = playouts

    def _playout(self):
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

    def _train(self):
        for _ in range(playouts):
            self._playout()

    def get_move(self):
        self._train()
        return max(root.children, key=lambda child: child.get_win_ratio()).last_move

