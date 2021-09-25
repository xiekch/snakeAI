import os

from config import *
from Vector import Vector
import torch.nn as nn
import torch.optim as optim
import random
import math
import torch
from dqn import DQN
from ReplayMemory import ReplayMemory, Transition

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
policy_net = DQN(STATE_LEN, MID_DIM, ACTION_DIM).to(device)
target_net = DQN(STATE_LEN, MID_DIM, ACTION_DIM).to(device)
optimizer = optim.RMSprop(policy_net.parameters())
memory = ReplayMemory(MEMEORY_SIZE)
i_episode = 0
maxScore = 0
steps_done = 0


def select_action(state):
    global steps_done
    if TRAIN_MODE:
        sample = random.random()
        eps_threshold = EPS_END + (EPS_START - EPS_END) * \
                        math.exp(-1. * steps_done / EPS_DECAY)
        steps_done += 1
        if sample > eps_threshold:
            with torch.no_grad():
                # t.max(1) will return largest column value of each row.
                # second column on max result is index of where max element was
                # found, so we pick action with the larger expected reward.
                return policy_net.forward(state).max(0)[1].view(1, 1)
        else:
            return torch.tensor([[random.randrange(ACTION_DIM)]], device=device, dtype=torch.long)
    else:
        with torch.no_grad():
            # t.max(1) will return largest column value of each row.
            # second column on max result is index of where max element was
            # found, so we pick action with the larger expected reward.
            return policy_net.forward(state).max(0)[1].view(1, 1)


def distance(a, b) -> float:
    return math.sqrt((a.X - b.X) * (a.X - b.X) + (a.Y - b.Y) * (a.Y - b.Y))


def act(donuts, selfPosition, safeDis, m):
    for d in donuts:
        dp = Vector(d[0], d[1])
        if distance(dp,
                    selfPosition) > safeDis * 2 and safeDis < dp.X < m.X - safeDis and safeDis < dp.Y < m.Y - safeDis:
            return dp.X - selfPosition.X, dp.Y - selfPosition.Y


def train(last_state, action, curr_state, reward):
    # num_episodes = 50
    global maxScore
    global i_episode

    if reward != 0:
        memory.push(torch.tensor(last_state).view(1, -1), action, curr_state,
                    torch.tensor([reward]))
    if reward == DEAD_REWARD:
        for i in range(DEAD_TRAIN_REPEAT):
            memory.push(torch.tensor(last_state).view(1, -1), action, curr_state,
                        torch.tensor([reward]))
    i_episode += 1
    # for i_episode in range(num_episodes):
    # Initialize the environment and state
    # for t in count():

    # Store the transition in memory

    # Move to the next state

    # Perform one step of the optimization (on the policy network)
    print(f"train {i_episode}")
    optimize_model(reward < 0)
    # if done:
    #     episode_durations.append(t + 1)
    #     plot_durations()
    #     break
    # Update the target network, copying all weights and biases in DQN
    if i_episode % TARGET_UPDATE == 0:
        target_net.load_state_dict(policy_net.state_dict())


def optimize_model(needLast=False):
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE, needLast)
    # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
    # detailed explanation). This converts batch-array of Transitions
    # to Transition of batch-arrays.
    batch = Transition(*zip(*transitions))

    # Compute a mask of non-final states and concatenate the batch elements
    # (a final state would've been the one after which simulation ended)
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                            batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                       if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
    # columns of actions taken. These are the actions which would've been taken
    # for each batch state according to policy_net
    state_action_values = policy_net(state_batch).gather(1, action_batch)
    # Compute V(s_{t+1}) for all next states.
    # Expected values of actions for non_final_next_states are computed based
    # on the "older" target_net; selecting their best reward with max(1)[0].
    # This is merged based on the mask, such that we'll have either the expected
    # state value or 0 in case the state was final.
    next_state_values = torch.zeros(BATCH_SIZE)
    next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()
    # Compute the expected Q values
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    # Compute Huber loss
    criterion = nn.SmoothL1Loss()

    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()


def train_start():
    global maxScore
    if os.path.exists(SCORE_FILE_NAME):
        f = open(SCORE_FILE_NAME)
        line = f.readline()
        if len(line) == 0:
            maxScore = 0
        else:
            maxScore = int(line)
    else:
        f = open(SCORE_FILE_NAME,'w')
        f.write('0')
        maxScore = 0
    f.close()
    if os.path.exists(WEIGHT_FILE_NAME):
        policy_net.load_state_dict(torch.load(WEIGHT_FILE_NAME))
        target_net.load_state_dict(torch.load(WEIGHT_FILE_NAME))
    print(maxScore)


def reset_train():
    global steps_done
    steps_done = 0


def train_end(score):
    global maxScore
    print(f"end {maxScore} {score}")
    if score > maxScore:
        maxScore = score
        print(f'Save Model! score: {score}')
        torch.save(policy_net.state_dict(), WEIGHT_FILE_NAME)
        f = open(SCORE_FILE_NAME, 'w')
        f.write(f'{score}')
        f.close()
