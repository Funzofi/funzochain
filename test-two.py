import time
from node import node
from block import Block
import socket

from transaction import Transaction

node = node("0x1", (socket.gethostname(),90), "test-two")

def runtime(first_run=True):
    if first_run:
        for _ in range(100):
            transaction = Transaction(node, "0x0", "0x1", 1, "0x0")
            block = Block(node, [transaction.serialised], "0x1")
            node.chain.append(block)
            time.sleep(0.1)

if __name__ == "__main__":
    node.p2pInterface.addPeer((socket.gethostname(),80),False)
    node.runtime = runtime
    node.run()