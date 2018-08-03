import random
import sys
import pytest

from mcts import MCTSNode, MCTSTree
from board import Board
from gomoku_net import Net

class MCTSNodeMock(MCTSNode):
    def __init__(self, *args, **kwargs):
        super(MCTSNodeMock, self).__init__(*args, **kwargs)

    def expand(self):
        '''
        add all valid moves as child nodes
        '''
        self.children = set()
        for move in self.board.valid_moves():
            self.children.add(
                MCTSNodeMock(
                    *self.board.copy().make_move(move),
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
        self.root = MCTSNodeMock(board, False)
        self.playouts = playouts

DIM = 19
PLAYOUTS = 100
tree = MCTSTree(Net(), board=Board(x_dim=DIM, y_dim=DIM), playouts=PLAYOUTS)
assert tree.playouts == PLAYOUTS
assert tree.root.board.x_dim == DIM and tree.root.board.y_dim == DIM
move = tree.get_move()
print "Best move: " + str(move)
assert move >= 0 and move < (DIM*DIM)
for child in tree.root.children:
    print (child.wins, child.plays, child.get_win_ratio())
assert len(tree.root.children) == (DIM*DIM)
