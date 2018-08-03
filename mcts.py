from __future__ import division # enable float division
import random
import numpy as np
import torch

from board import Board
from gomoku_net import Net
from dqn import get_tensor


class MCTSNode(object):
    def __init__(self, board, won, q=None, parent=None, last_move=None):
        self.board = board
        self.won = won
        self.q = q
        self.parent = parent
        self.last_move = last_move
        self.children = {}
        self.wins = 1
        self.plays = 2

    def select(self):
        '''
        chooses a child node with probability = relative win ratio
        '''
        assert not self.is_leaf()
        max_weight = 0
        for child in self.children:
            weight = np.random.beta(child.wins, child.plays-child.wins)
            if weight > max_weight:
                max_weight = weight
                max_child = child
        return max_child

    def expand(self, net):
        '''
        add all valid moves as child nodes
        '''
        state = get_tensor(self.board)
        q_values = net(state)[0]
        self.children = {
            MCTSNode(
                *self.board.copy().make_move(move),
                q=q_values[move].item(),
                parent=self,
                last_move=move
            )
            for move in self.board.valid_moves()
        }

    def simulate(self):
        return self.q

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


class MCTSTree(object):
    def __init__(self, net, board=Board(), playouts=1000):
        self.root = MCTSNode(board, False)
        self.playouts = playouts
        self.net = net

    def _playout(self):
        # selection
        curr = self.root
        while not curr.is_leaf():
            curr = curr.select()

        # expansion
        if curr.won:
            win_prob = 1 # active player wins
        else:
            curr.expand(self.net)
            curr = curr.select()
            win_prob = curr.simulate() # simulation

        # backpropagation
        while curr.parent is not None:
            curr.update(win_prob)
            curr = curr.parent
            win_prob = 1 - win_prob

    def _train(self):
        for _ in range(self.playouts):
            self._playout()

    def get_move(self):
        self._train()
        c = list(self.root.children)
        chosen = np.random.choice(c, 1, [child.plays for child in c])[0]
        return chosen.last_move
