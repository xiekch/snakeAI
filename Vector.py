from typing import Tuple


class Vector:
    def __init__(self, x, y) -> None:
        self.X = x
        self.Y = y

    def __str__(self) -> str:
        return f'({self.X},{self.Y})'

    @staticmethod
    def fromVector2(vec):
        return Vector(vec.X, vec.Y)

    @staticmethod
    def fromTuple(tup: Tuple):
        return Vector(tup[0], tup[1])
