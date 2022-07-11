from node import node
import socket

node = node("0x2", (socket.gethostname(),100), "test-two")

if __name__ == "__main__":
    node.p2pInterface.addPeer((socket.gethostname(),90))
    node.run()