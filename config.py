RPC_ADDRESS = ('host.docker.internal', 7000)
RPC_SERVER_ADDRESS = ('localhost', 7000)
TRAIN_MODE = False

MAX_DONUTS_SIZE = 20
PADDING_DATA = (0, 0, -1)
MAX_SNAKE_LEN = 20

MY_SNAKE_STATE_LEN = MAX_SNAKE_LEN * 2
DONUTS_STATE_LEN = MAX_DONUTS_SIZE * 3
AVOID_WALL_POINTS = 10
AVOID_SNAKE_POINTS = 10
AVOID_POINTS = AVOID_WALL_POINTS + AVOID_SNAKE_POINTS
AVOID_STATE_LEN = AVOID_POINTS * 2
STATE_LEN = MY_SNAKE_STATE_LEN + DONUTS_STATE_LEN + AVOID_STATE_LEN

MID_DIM = 200
ACTION_DIM = 8

MEMEORY_SIZE = 3000
BATCH_SIZE = 128
GAMMA = 0.99
EPS_START = 0.5
EPS_END = 0.1
EPS_DECAY = 300
TARGET_UPDATE = 20

DEAD_REWARD = -100

# SCORE_FILE_NAME = 'score.txt'
# WEIGHT_FILE_NAME = 'weight.pkl'

SCORE_FILE_NAME = 'score2.txt'
WEIGHT_FILE_NAME = 'weight2.pkl'