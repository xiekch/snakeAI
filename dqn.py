import torch
import torch.nn as nn
import torch.nn.functional as F
import random
from config import *
import math



class DQN(nn.Module):

    def __init__(self, state_dim, mid_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(state_dim, mid_dim), nn.ReLU(),
                                 # nn.Linear(mid_dim, mid_dim), nn.ReLU(),
                                 nn.Linear(mid_dim, action_dim))

    # Called with either one element to determine next action, or a batch
    # during optimization. Returns tensor([[left0exp,right0exp]...]).
    def forward(self, state):
        return self.net(torch.as_tensor(state))
