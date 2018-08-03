import random
import sys
import pytest

from mcts import MCTSNode, MCTSTree
from board import Board

class MCTSNodeMock(MCTSNode):
    def __init__(self, *args, **kwargs):
        super(MCTSNodeMock, self).__init__(*args, **kwargs)

    def expand(self):
        '''
        add all valid moves as child nodes
        '''
        self.children = set()
        print self.board.valid_moves()
        for move in self.board.valid_moves():
            print move
            self.children.add(
                MCTSNodeMock(
                    *self.board.copy().make_move(move, self.board.active_player),
                    parent=self,
                    last_move=move
                )
            )

    def simulate(self):
        '''
        override the parent class's simulate() method
        '''
        random.seed(self.board)
        return random.random()

class MCTSTreeMock(MCTSTree):
    def __init__(self, board=Board(), playouts=1000):
        self.root = MCTSNodeMock(Board(), False)
        self.playouts = playouts

tree = MCTSTreeMock()
assert len(tree.root.board.valid_moves()) == 361
assert tree.playouts == 1000
move = tree.get_move()
print move
assert move >= 0 and move < 361
print tree.root.board
