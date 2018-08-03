import torch

from board import Board
from gomoku_net import Net

board = Board()
net = Net()
player = False
done = False

while not done:
    # compute q-values
    board_state = torch.tensor(board.as_array()).unsqueeze(0)
    board_state = board_state.type(torch.FloatTensor)
    q_values = net(board_state)

    # choose top (valid) move
    valid_moves = board.valid_moves()
    top_moves = torch.topk(q_values, 361)
    top_moves = top_moves[1].squeeze(0)
    for i in range(361):
        top_move = top_moves[i].item()
        if top_move in valid_moves:
            break

    # play top (valid) move
    done = board.make_move(top_move, player)[1]
    player = not player

print(board)





