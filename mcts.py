from __future__ import division # enable float division
import random
import numpy as np
import torch

from board import Board
from gomoku_net import Net
from dqn import get_tensor


class MCTSNode(object):
    def __init__(self, board, won, parent=None, last_move=None, net=None):
        self.board = board.copy()
        self.moves = board.valid_moves()
        self.won = won
        self.parent = parent
        self.last_move = last_move
        self.children = {}
        self.wins = 0
        self.plays = 0
        vals = [x.item() for x in net(get_tensor(board))[0]]
        self.p = vals[:-1]
        self.v = vals[-1]
        self.net = net

    def select(self):
        '''
        chooses a move
        '''
        max_weight = 0
        for move in self.moves:
            if move in self.children:
                child = self.children[move]
                if child.won:
                    q = float('inf')
                else:
                    q = child.wins / child.plays
                u = child.p[move] / (1 + child.plays)
                weight = q + u
            else:
                q = 1
                u = self.p[move]
                weight = q + u

            if weight > max_weight:
                max_weight = weight
                max_child = move
        return max_child

    def expand(self, move):
        '''
        add child node
        '''
        assert move not in self.children
        new_board, won = self.board.copy().make_move(move)
        new_node = MCTSNode(
                new_board,
                won,
                parent=self,
                last_move=move,
                net=self.net
            )
        self.children[move] = new_node
        return new_node

    def simulate(self):
        return self.v

    def update(self, win_prob):
        '''
        updates win count of current node
        '''
        self.wins += win_prob
        self.plays += 1

    def is_root(self):
        return self.parent == None

    def get_win_ratio(self):
        return 1 if self.plays == 0 else self.wins / self.plays


class MCTSTree(object):
    def __init__(self, net, board=Board(), playouts=1000):
        self.root = MCTSNode(board, False, net=net)
        self.playouts = playouts

    def _playout(self):
        # selection
        curr = self.root
        while not curr.won:
            move = curr.select()
            if move in curr.children:
                curr = curr.children[move]
            else:
                break

        # expansion
        if curr.won:
            win_prob = 1 # active player wins
        else:
            curr = curr.expand(move)
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
        c = self.root.children.values()
        chosen = np.random.choice(c, 1, [child.plays for child in c])[0]
        return chosen.last_move

    def get_move_dist(self):
        return [float(self.children[move].plays) / self.plays if move in self.children else 0.0 for move in range(361)]
