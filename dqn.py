from itertools import count
import math
import random
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from board import Board
from gomoku_net import Net
from replay_memory import Transition, ReplayMemory

BATCH_SIZE = 128
GAMMA = 0.999
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 200
TARGET_UPDATE = 10

policy_net = Net()
target_net = Net()
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.RMSprop(policy_net.parameters())
memory = ReplayMemory(100)

steps_done = 0

def select_action(state):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1

    if sample > eps_threshold:
        # compute q-values
        state = torch.tensor(state.as_array()).unsqueeze(0)
        state = state.type(torch.FloatTensor)
        with torch.no_grad():
            q_values = net(state)

        # choose top (valid) move
        valid_moves = state.valid_moves()
        top_moves = torch.topk(q_values, 361)
        top_moves = top_moves[1].squeeze(0)
        for i in range(361):
            top_move = top_moves[i].item()
            if top_move in valid_moves:
                break
        return top_move

    else:
        return torch.tensor([[random.randrange(361)]], dtype=torch.long)

# TODO: util function for board transformation






