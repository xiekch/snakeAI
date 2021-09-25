from typing import List, Tuple
from config import *
from Vector import Vector
import torch
from trainer import select_action, train, train_start, train_end, reset_train
from dqn import DQN
import logging
import sys


def manhattanDistance(a, b) -> float:
    return abs(a.X - b.X) + abs(a.Y - b.Y)


directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
end = False


class SnakeAI:
    def __init__(self):
        train_start()

    def onStarted(self, gameInfo, worldInfo) -> None:
        # print(f"life cycle: started. gameInfo={gameInfo}")
        global end
        print(f"life cycle: started.")
        if TRAIN_MODE:
            reset_train()
        end = False
        mapProperty = gameInfo.MapProperty
        self.gameSize = Vector.fromVector2(mapProperty.Size)
        avoidWallPoints: List[Vector] = []
        for i in range(-50, 50):
            avoidWallPoints.append(Vector(i, 24))
            avoidWallPoints.append(Vector(i, -25))
        for j in range(-25, 25):
            avoidWallPoints.append(Vector(-49, j))
            avoidWallPoints.append(Vector(48, j))
        self.avoidWallPoints: List[Vector] = avoidWallPoints
        self.score = 0
        self.position = Vector.fromVector2(worldInfo.mySnake.Nodes[0])
        self.state = self.getState(worldInfo)
        self.action = None
        self.init = False

    def onEnded(self, score) -> None:
        print(f"life cycle: ended, score={score}")
        if TRAIN_MODE:
            train_end(self.score)

    def onRound(self, roundIndex, gameInfo, worldInfo) -> Tuple[float, float]:
        global end
        if end:
            return 0, 0
        try:
            print(f"life cycle: round {roundIndex}")

            self.position = Vector.fromVector2(worldInfo.mySnake.Nodes[0])
            self.isAlive = worldInfo.mySnake.IsAlive
            self.lastScore = self.score
            self.score = worldInfo.mySnake.Score
            self.lastState = self.state
            self.state = self.getState(worldInfo)
            # print(self.position)

            if TRAIN_MODE:
                action = select_action(self.state)
                self.lastAction = self.action
                self.action = action
                print(self.isAlive, roundIndex, self.score - self.lastScore)
                if roundIndex > 0:
                    if self.isAlive:
                        train(self.lastState, self.lastAction, torch.tensor(self.state).view(1, -1), self.score - self.lastScore)
                    else:
                        end = True
                        train(self.lastState, self.lastAction, None, DEAD_REWARD)
                if action is not None:
                    return self.selectDirection(action)
            else:
                return self.selectDirection(select_action(self.state))
        except Exception as e:
            logging.exception(e)
        return 0, 0

    def selectDirection(self, action) -> Tuple[float, float]:
        return directions[action.item()]

    def getState(self, worldInfo) -> List[float]:
        # relative position
        state = []
        selfPositionX = self.position.X
        selfPositionY = self.position.Y
        mySnake = worldInfo.mySnake

        # my snake state
        for n in mySnake.Nodes[1:]:
            nv = [n.X - selfPositionX, n.Y - selfPositionY]
            state.extend(nv)
        if len(state) < MY_SNAKE_STATE_LEN:
            state.extend(0 for _ in range(MY_SNAKE_STATE_LEN - len(state)))

        # donuts state
        donutsState = self.parseDonuts(worldInfo)
        for i in range(len(donutsState)):
            state.extend((donutsState[i][0] - selfPositionX,
                          donutsState[i][1] - selfPositionY, donutsState[i][2]))

        # for i in range(5):
        #     print(donutsState[i], manhattanDistance(
        #         Vector(donutsState[i][0], donutsState[i][1]), self.position))

        # avoid state: the nearest 30 points need to avoid
        self.avoidWallPoints.sort(key=lambda a: manhattanDistance(a, self.position))
        for i in self.avoidWallPoints[:AVOID_WALL_POINTS]:
            # print(f"w {i.X},{i.Y}")
            state.append(i.X - selfPositionX)
            state.append(i.Y - selfPositionY)

        otherSnakes = worldInfo.otherSnakes
        avoidSnakePoints = []
        for s in otherSnakes:
            for p in s.Nodes:
                avoidSnakePoints.append(p)
        avoidSnakePoints.sort(key=lambda a: manhattanDistance(a, self.position))

        if len(avoidSnakePoints) < AVOID_SNAKE_POINTS:
            avoidSnakePoints.extend(self.avoidWallPoints[AVOID_WALL_POINTS:AVOID_SNAKE_POINTS + AVOID_WALL_POINTS])

        for i in avoidSnakePoints[: AVOID_SNAKE_POINTS]:
            # print(f"s {i.X},{i.Y}")
            state.append(i.X - selfPositionX)
            state.append(i.Y - selfPositionY)

        # print(len(state))

        return state

    def parseDonuts(self, worldInfo) -> List[Tuple[float, float, float]]:
        def mapFun(donut):
            return (
                donut.Position.X, donut.Position.Y, donut.Type)

        worldInfo.donuts.sort(
            key=lambda a: manhattanDistance(a.Position, self.position))
        if len(worldInfo.donuts) >= MAX_DONUTS_SIZE:
            res = [mapFun(i) for i in worldInfo.donuts[:MAX_DONUTS_SIZE]]
        else:
            res = [mapFun(i) for i in worldInfo.donuts]
            res.extend(PADDING_DATA for _ in range(
                MAX_DONUTS_SIZE - len(worldInfo.donuts)))
        return res


if __name__ == "__main__":
    from main import parseArgv, startUp

    ip, port = parseArgv()
    startUp(SnakeAI(), ip, port)
