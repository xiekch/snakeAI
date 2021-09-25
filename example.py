import math
from typing import Tuple


def distance(a, b):
    return math.sqrt((a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]))


class ExampleSnakeAI:
    def getTeamId(self) -> str:
        return "6834003718317277198"

    def onStarted(self, gameInfo, worldInfo) -> None:
        print(f"life cycle: started. gameInfo={gameInfo}")

    def onEnded(self, score) -> None:
        print(f"life cycle: ended, score={score}")

    def onRound(self, roundIndex, gameInfo, worldInfo) -> Tuple[float, float]:
        print(f"life cycle: round {roundIndex}")
        safeDis = gameInfo.SnakeProperty.Velocity / \
            gameInfo.SnakeProperty.AngularVelocity * 180
        m = gameInfo.MapProperty.Size
        p = (worldInfo.mySnake.Nodes[0].X, worldInfo.mySnake.Nodes[0].Y)

        for d in worldInfo.donuts:
            dp = (d.Position.X, d.Position.Y)
            if distance(dp, p) > safeDis * 2 and dp[0] > safeDis and dp[0] < m.X - safeDis and dp[1] > safeDis and dp[1] < m.Y - safeDis:
                return (dp[0] - p[0], dp[1] - p[1])
        return (0, 0)


if __name__ == "__main__":
    from main import parseArgv, startUp
    ip, port = parseArgv()
    startUp(ExampleSnakeAI(), ip, port)
