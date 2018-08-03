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
RESULTS_PATH='results.log'

# NOTE: if loading model, set steps_done to a million
policy_net = Net()
target_net = Net()
target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.RMSprop(policy_net.parameters())
memory = ReplayMemory(10000)

steps_done = 0

def select_action(state):
    '''
    takes Board and selects action

    note: the input must be Board
    to access all valid actions
    '''
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    valid_actions = state.valid_moves()

    if sample > eps_threshold:
        print 'calculating...'
        t = mcts.MCTSTree(policy_net, board=state, playouts=1000)
        move = t.get_move()
        print move
        return torch.tensor([[move]], dtype=torch.long)
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
        return torch.tensor([[action]], dtype=torch.long)

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
    transitions = memory.sample(BATCH_SIZE)
    batch = Transition(*zip(*transitions))

    # Compute a mask of non-final states and concatenate the batch elements
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                          batch.next_state)), dtype=torch.uint8)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                                if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)
    reward_batch = reward_batch.type(torch.FloatTensor)

    # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
    # columns of actions taken
    state_action_values = policy_net(state_batch).gather(1, action_batch)

    # Compute V(s_{t+1}) for all next states.
    next_state_values = torch.zeros(BATCH_SIZE)
    next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()
    # Compute the expected Q values
    #print(next_state_values.type())
    reward_batch.type(torch.FloatTensor)
    #print(reward_batch.type())
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    # Compute Huber loss
    loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))

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
            # Select and perform an action
            action = select_action(state)
            prev_state = state.copy()
            _, done = state.make_move(action.item())
            if done:
                if i_episode % SAVE_STEP == 0:
                    print state
                    print '\n\n\n'
                results[prev_state.active_player] += 1
                state = None
            reward = torch.tensor([done])

            # Store the transition in memory and move to next state
            memory.push(get_tensor(prev_state), action, get_tensor(state), reward)

            # Perform one step of the optimization (on the target network)
            if done:
                break

        optimize_model()

        # Update the target network
        if i_episode % TARGET_UPDATE == 0:
            target_net.load_state_dict(policy_net.state_dict())

        # Save model
        if i_episode % SAVE_STEP == 0:
            path = 'models/gomoku_net_{}'.format(i_episode)
            torch.save(policy_net.state_dict(), path)
            with open(RESULTS_PATH, 'a') as f:
                f.write(str(results) + '\n')

    print('Training complete.')
