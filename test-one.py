from node import node
import socket

node = node("0x0", (socket.gethostname(),80), "test-one")

if __name__ == "__main__":
    node.run()