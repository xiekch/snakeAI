import socket
import struct
from snake.proto.message_pb2 import S2CStartMessage, S2CRoundMessage, S2CEndMessage, MessageId
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32
from typing import Any, Tuple, List


class SocketClient:
    def __init__(self) -> None:
        self._socket = None
        self.isConnected = False
        pass

    def connect(self, host, port) -> None:
        # TCP
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(1)
        self._socket.connect((host, port))
        self.isConnected = True

    def disconnect(self) -> None:
        self._socket.close()
        self.isConnected = False

    def sendMessage(self, id, message) -> None:
        data = Protocols.encode(id, message)

        size = 4  # protocol id 占 4 个字节
        for x in data:
            size += len(x)

        # big-endian required
        # 必须是大端
        # 直接写入流中，这样不用做数组拼接
        self._socket.send(struct.pack(">ii", size, id))

        for x in data:
            self._socket.send(x)

    def pollMessage(self) -> Tuple[int, Any]:
        # size, protocol id, 共 8 个字节
        data = self.__read(8)  # blocking

        # big-endian required
        # 必须是大端
        size, id = struct.unpack(">ii", data)

        size = size - 4  # 减去 protocol id 的 4 字节

        # recv 是流读取
        # 一次调用可能只读取到一个片段的数据
        # 需要重复读取直至获得 size 个字节的数据
        data = self.__read(size)

        return (id, Protocols.decode(id, data))

    def __read(self, size) -> str:
        data = self._socket.recv(size, socket.MSG_WAITALL)
        if len(data) < size:
            raise EOFError()  # 远端断开了
        return data


class Protocols:
    @staticmethod
    def encode(id, message) -> List[str]:
        if id == MessageId.C2SAuth:
            pass
        elif id == MessageId.S2CStart:
            raise "should not call `encode` on Start"
        elif id == MessageId.S2CRound:
            raise "should not call `encode` on Round"
        elif id == MessageId.S2CEnd:
            raise "should not call `encode` on END"
        elif id == MessageId.C2SCommand:
            pass
        else:
            raise f"unknown message to `encode`: {id}"

        size = message.ByteSize()

        # server side is delimited, 需要先把消息大小写进去
        sizeData = _VarintBytes(size)
        messageData = message.SerializeToString()

        return [sizeData, messageData]

    @staticmethod
    def decode(id, data) -> Any:
        message = None
        if id == MessageId.C2SAuth:
            raise "should not call `decode` on Auth"
        elif id == MessageId.S2CStart:
            message = S2CStartMessage()
        elif id == MessageId.S2CRound:
            message = S2CRoundMessage()
        elif id == MessageId.S2CEnd:
            message = S2CEndMessage()
        elif id == MessageId.C2SCommand:
            raise "should not call `decode` on Command"
        else:
            raise f"unknown message to `decode`: {id}"

        # server side is delimited, 需要先把消息大小读出来
        _, pos = _DecodeVarint32(data, 0)

        data = data[pos:]
        message.ParseFromString(data)

        return message
