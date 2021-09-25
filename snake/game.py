# -*- coding: utf-8 -*-
from typing import Tuple
from snake.netcode import SocketClient
from snake.proto.shared_pb2 import DonutInfo, SnakeInfo
from snake.proto.message_pb2 import C2SAuthMessage, C2SCommandMessage, MessageId


class GameLifeCycle:
    def __init__(self) -> None:
        pass

    """
    游戏开始，3 秒后会开始第一回合
    world 包含了初始世界状态
    """

    def onStarted(self, gameInfo, worldInfo) -> None:
        raise "not implemented"

    """
    游戏结束
    """

    def onEnded(self, score) -> None:
        raise "not implemented"

    """
    新的回合
    world 包含了当前回合的世界状态
    """

    def onRound(self, roundIndex, gameInfo, worldInfo) -> Tuple[float, float]:
        raise "not implemented"


class WorldInfo:
    def __init__(self) -> None:
        self.roundIndex = -1
        self.snakes = []
        self.donuts = []
        self.donutsMap = {}
        self.donutsSpawned = []
        self.donutsRemoved = []
        self.mySnake = None
        self.otherSnakes = []
        self.__mySnakeId = -1

    def setMySnakeId(self, id) -> None:
        self.__mySnakeId = id

    def update(self, snapshot) -> None:
        self.roundIndex = snapshot.RoundIndex
        self.snakes = snapshot.Snakes
        self.mySnake = self.findSnake(self.__mySnakeId)
        self.otherSnakes = [x for x in self.snakes if x.Id != self.__mySnakeId]

        # 增量更新豆子数组
        self.donutsRemoved = []
        for i in range(len(self.donuts)-1, -1, -1):
            if self.donuts[i].Id in snapshot.DonutsRemoved:
                self.donutsRemoved.append(self.donuts[i])
                del self.donutsMap[self.donuts[i].Id]
                del self.donuts[i]
        self.donuts.extend(snapshot.DonutsSpawned)
        self.donutsSpawned = snapshot.DonutsSpawned
        for x in snapshot.DonutsSpawned:
            self.donutsMap[x.Id] = x

    def findSnake(self, id) -> SnakeInfo:
        for x in self.snakes:
            if x.Id == id:
                return x
        return None

    def findDonut(self, id) -> DonutInfo:
        return self.donutsMap[id]


class CommandCommiter:
    def __init__(self, socketClient) -> None:
        self.socketClient = socketClient

    def __call__(self, x, y) -> None:
        self.commit(x, y)

    def commit(self, x, y) -> None:
        print(f"commit command, x={x}, y={y}")

        commandMessage = C2SCommandMessage()
        commandMessage.Direction.X = x
        commandMessage.Direction.Y = y
        self.socketClient.sendMessage(MessageId.C2SCommand, commandMessage)


class Game:
    def __init__(self, host, port, token, playerName) -> None:
        self.host = host
        self.port = port
        self.token = token
        self.playerName = playerName

    def start(self, gameLifeCycle) -> None:
        print(
            f"game start, host={self.host}, port={self.port}, token={self.token}")

        print("socket connecting ...")
        client = SocketClient()
        client.connect(self.host, self.port)

        print("socket connected.")

        commandCommiter = CommandCommiter(client)

        print("authenticating ...")
        authMessage = C2SAuthMessage()
        authMessage.Token = self.token
        authMessage.Type = C2SAuthMessage.ClientType.Player
        authMessage.PlayerName = self.playerName

        client.sendMessage(MessageId.C2SAuth, authMessage)
        print("authenticated.")

        print("waiting for starting ...")

        worldInfo = WorldInfo()
        gameInfo = None
        while True:
            try:
                messageId, message = client.pollMessage()
                if messageId == MessageId.S2CStart:
                    print("game start.")
                    gameInfo = message.GameInfo
                    print(gameInfo)
                    worldInfo.setMySnakeId(gameInfo.YourSnakeId)
                    worldInfo.update(message.World)

                    gameLifeCycle.onStarted(gameInfo, worldInfo)

                elif messageId == MessageId.S2CEnd:
                    print("game end, disconnect.")
                    gameLifeCycle.onEnded(message.Score)
                    # client.disconnect()
                elif messageId == MessageId.S2CRound:
                    print(f"game round.")
                    worldInfo.update(message.World)
                    try:
                        (x, y) = gameLifeCycle.onRound(
                            worldInfo.roundIndex, gameInfo, worldInfo)
                        commandCommiter(x, y)
                    except Exception as e:
                        print("error occurred: " + str(e))

                else:
                    raise f"Unknown message: {messageId}"

                if not client.isConnected:
                    break
            except EOFError:
                print("remote disconnected")
                break
            except KeyboardInterrupt:
                break
