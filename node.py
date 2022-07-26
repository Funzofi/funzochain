from queue import Queue
from gan import Gan
from block import Block, LogBlock
from p2p import p2pInterface
from blockchain import Blockchain
import threading
import sys

class Node():
    def __init__(self, private_key, host, name="chain"):
        self.host = host
        self.private_key = private_key
        self.address = private_key
        self.p2pInterface = p2pInterface(self)
        self.chain = Blockchain(self, name,self.p2pInterface)

    def initialize_gan(self):
        self.gan = Gan(self.host, self.private_key)
        if not self.gan.is_initialized():
            self.p2pInterface.sync_chain(self)
            block = LogBlock(self, "Initializing Gan")
            self.chain.append(block)
            gan = GAN()
            gan.initialize()
            gan.feedData()
            gan.train(self.chain)
            gan.trainClassifier()
        
        block = LogBlock(self, "Gan initialized")
        self.chain.append(block)

    @staticmethod
    def runtime(self, first_run=True):
        pass

    def run(self):
        try:
            data_queue = Queue()
            thread = threading.Thread(target=self.p2pInterface.listen, args=(data_queue,), daemon=True)
            thread.start()
            first_run = True
            while True:
                self.runtime(self, first_run)
                first_run = False
                if data_queue.qsize() > 0:
                    data_type, data = data_queue.get(timeout=1)
                    if data_type == "blck":
                        print("Received Block Data")
                        block = Block(self,"").deserialised(data.decode())
                        if not block.valid():
                            try:
                                self.chain.append(block)
                                print(f"Block {block.hash[:6]} added to chain")
                            except ValueError as e:
                                print(e)
                        else:
                            print(f"Block {block.hash[:6]} invalid")
        except KeyboardInterrupt as e:
            print("Shutting down")
            sys.exit(0)