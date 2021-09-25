from collections import namedtuple, deque
import random

Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))


class ReplayMemory(object):

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        self.memory.append(Transition(*args))

    def sample(self, batch_size, needLast=False):
        if needLast:
            res = random.sample(self.memory, batch_size)
            res[-1] = self.memory[-1]
            return res
        else:
            return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)
