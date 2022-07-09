from queue import Queue
from gan import Gan
from block import Block, LogBlock
from p2p import p2pInterface
from blockchain import Blockchain
import threading

class node():
    def __init__(self, private_key, host, name="chain"):
        self.host = host
        self.private_key = private_key
        self.address = private_key
        self.p2pInterface = p2pInterface(self)
        self.chain = Blockchain(name,self.p2pInterface)

    def initialize_gan(self):
        self.gan = Gan(self.host, self.private_key)
        if not self.gan.is_initialized():
            self.p2pInterface.sync_chain(self)
            block = LogBlock(self, "Initializing Gan")
            self.p2pInterface.broadcast("blck:new".encode())
            self.p2pInterface.broadcast(block.serialised)
            self.gan.train(self.chain)
        
        block = LogBlock(self, "Gan initialized")
        self.p2pInterface.broadcast("blck:new".encode())
        self.p2pInterface.broadcast(block.serialised)

    def run(self, runtime=function()):
        data_queue = Queue.Queue()
        thread = threading.Thread(target=self.p2pInterface.listen, args=(data_queue,))
        thread.start()
        first_run = True
        while True:
            runtime(first_run)
            first_run = False
            try:
                data_type, data = data_queue.get(timeout=1)
                if data_type == "blck":
                    if Block.valid(Block.deserialize(data)):
                        self.node.chain.append(Block.deserialize(data))
            except Queue.Empty:
                pass