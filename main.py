from snake.game import Game

import sys


def parseArgv():
    def usage():
        print(f"Usage: python {sys.argv[0]} <ip> <port>")

    if len(sys.argv) != 3 and len(sys.argv) != 4:
        usage()
        sys.exit(-1)

    try:
        ip = sys.argv[1]
        port = int(sys.argv[2])

        return (ip, port)
    except Exception as e:
        print("argv error, try again: \n\t" + str(e) + "\n")
        usage()
        sys.exit(-1)


def startUp(ai, ip, port):
    Game(ip, port, "7009228152635473964", "").start(ai)


if __name__ == "__main__":
    from ai import SnakeAI
    ip, port = parseArgv()
    startUp(SnakeAI(), ip, port)
