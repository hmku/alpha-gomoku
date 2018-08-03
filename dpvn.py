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
RESULTS_PATH='results_dpvn.log'

# NOTE: if loading model, set steps_done to a million
policy_net = Net()
#target_net = Net()
#target_net.load_state_dict(policy_net.state_dict())
#target_net.eval()

optimizer = optim.RMSprop(policy_net.parameters())
memory = ReplayBuffer(10000)

steps_done = 0

def select_action(state):
    '''
    takes Board and selects action

    returns policy and action
    '''
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    valid_actions = state.valid_moves()
    t = mcts.MCTSTree(policy_net, board=state, playouts=1000)

    if sample > eps_threshold:
        print 'calculating...'
        move = t.get_move()
        print move
        return t.get_move_dist(), move
        '''
        # compute q-values
        state = get_tensor(state) 
        with torch.no_grad():
            q_values = policy_net(state)

        # choose top (valid) action
        actions = torch.topk(q_values, BOARD_SIZE)
        actions = actions[1].squeeze(0)
        for i in range(BOARD_SIZE):
            action = actions[i]
            if action.item() in valid_actions:
                return torch.tensor([[action.item()]], dtype=torch.long)
        '''
    else:
        action = random.sample(valid_actions, 1)[0]
        return t.get_move_dist(), action

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
    policy_batch = torch.cat(batch.policy)
    reward_batch = torch.cat(batch.reward)
    reward_batch = reward_batch.type(torch.FloatTensor)

    # Compute p, v with model acting on state
    policy_value = policy_net(state_batch) # 32 x 362
    expected_policy = policy_value[:, :361]
    expected_value = policy_value[:, 361].unsqueeze(1)

    # Compute loss
    mse_loss = nn.MSELoss()
    ce_loss = nn.CrossEntropyLoss()
    loss = mse_loss(reward_batch, expected_value) + ce_loss(policy_batch, expected_policy)

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()

# train
if __name__ == '__main__':
    results = [0, 0] # black wins, white wins
    num_episodes = 100000
    for i_episode in range(num_episodes):
        state = Board(x_dim=BOARD_DIM, y_dim=BOARD_DIM)
        for t in count():
            # Select and perform action and compute policy with MCTS
            policy, action = select_action(state)
            prev_state = state.copy()
            _, done = state.make_move(action)
            if done:
                if i_episode % SAVE_STEP == 0:
                    print state
                    print '\n\n\n'
                results[prev_state.active_player] += 1
                reward = torch.tensor([1])
            else:
                reward = torch.tensor([-1])

            # Store the step in memory and move to next state
            memory.push(get_tensor(prev_state), torch.tensor(policy), reward)

            if done:
                break

        optimize_model() # optimize after playing a game

        # Update the target network
        if i_episode % TARGET_UPDATE == 0:
            target_net.load_state_dict(policy_net.state_dict())

        # Save model
        if i_episode % SAVE_STEP == 0:
            path = 'models/gomoku_dpvn_net_{}'.format(i_episode)
            torch.save(policy_net.state_dict(), path)
            with open(RESULTS_PATH, 'a') as f:
                f.write(str(results) + '\n')

    print('Training complete.')
