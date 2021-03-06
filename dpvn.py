from itertools import count
import math
import random
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from board import Board
from gomoku_net import Net
from replay_memory import Step, ReplayBuffer
import mcts

BATCH_SIZE = 32
GAMMA = 1.000
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 200
TARGET_UPDATE = 10
SAVE_STEP = 1
BOARD_DIM = 19
BOARD_SIZE = BOARD_DIM * BOARD_DIM
LOAD_FROM = 0
RESULTS_PATH='results_dpvn.log'

# NOTE: if loading model, set steps_done to a million
policy_net = Net()
if LOAD_FROM > 0:
	policy_net.load_state_dict(torch.load('models/gomoku_dpvn_net_{}'.format(LOAD_FROM)))
#target_net = Net()
#target_net.load_state_dict(policy_net.state_dict())
#target_net.eval()

optimizer = optim.RMSprop(policy_net.parameters(), lr=0.001)
memory = ReplayBuffer(10000)

# steps_done = 0

def select_action(state):
    '''
    takes Board and selects action

    returns policy and action
    '''
    t = mcts.MCTSTree(policy_net, board=state, playouts=1000)
    print 'Calculating with MCTS.'
    move = t.get_move()
    print move
    return t.get_move_dist(), move

def get_tensor(board):
    '''
    returns FloatTensor representation of Board object
    '''
    if board != None:
        state = torch.tensor(board.as_array()).unsqueeze(0)
        return state.type(torch.FloatTensor)
    else:
        return None

def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    steps = memory.sample(BATCH_SIZE)
    batch = Step(*zip(*steps))

    state_batch = torch.cat(batch.state)
    policy_batch = torch.stack(batch.policy, 0)
    reward_batch = torch.cat(batch.reward)

    # Compute p, v with model acting on state
    policy_value = policy_net(state_batch) # 32 x 362
    expected_policy = policy_value[:, :361]
    expected_value = policy_value[:, 361].unsqueeze(1)

    # Compute loss
    mse_loss = nn.MSELoss()
    # ce_loss = nn.CrossEntropyLoss()
    kldiv_loss = nn.KLDivLoss()
    reward_batch = reward_batch.type(torch.FloatTensor)
    expected_value = expected_value.type(torch.FloatTensor)
    
    expected_policy = expected_policy.type(torch.FloatTensor)
    expected_policy = torch.log(expected_policy)
    policy_batch = policy_batch.type(torch.FloatTensor)

    print(reward_batch.size())
    print(expected_value.size())
    print(policy_batch.size())
    print(expected_policy.size())
    print(reward_batch.type())
    print(expected_value.type())
    print(policy_batch.type())
    print(expected_policy.type())
    loss = mse_loss(reward_batch, expected_value) + kldiv_loss(expected_policy, policy_batch)

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()

if __name__ == '__main__':
    results = [0, 0] # black wins, white wins
    num_episodes = 100000
    for i_episode in range(LOAD_FROM+1, num_episodes):
        moves_played = [[], []]
        state = Board(x_dim=BOARD_DIM, y_dim=BOARD_DIM)
        for t in count():
            # Select and perform action and compute policy with MCTS
            policy, action = select_action(state)
            prev_state = state.copy()
            _, done = state.make_move(action)
            print state
            print '\n'
            if done:
                '''
                if i_episode % SAVE_STEP == 0:
                    print state
                    print '\n\n\n'
                '''
                results[prev_state.active_player] += 1

            # Store the step in memory and move to next state
            moves_played[prev_state.active_player].append((get_tensor(prev_state), torch.tensor(policy)))

            if done:
                winner = prev_state.active_player
                break

        for move in moves_played[winner]:
            reward = torch.tensor([1])
            memory.push(move[0], move[1], reward)
        for move in moves_played[1 - winner]:
            reward = torch.tensor([-1])
            memory.push(move[0], move[1], reward)

        optimize_model() # optimize after playing a game

        # Save model
        if i_episode % SAVE_STEP == 0:
            path = 'models/gomoku_dpvn_net_{}'.format(i_episode)
            torch.save(policy_net.state_dict(), path)
            with open(RESULTS_PATH, 'a') as f:
                f.write(str(results) + '\n')

    print('Training complete.')
