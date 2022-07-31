from queue import Queue
from gan import GAN
from block import Block, LogBlock
from p2p import p2pInterface
from blockchain import Blockchain
from GPoHC import GPoHC
import threading
import sys

class Node():
    def __init__(self, private_key, host, name="chain"):
        self.host = host
        self.private_key = private_key
        self.address = private_key
        self.p2pInterface = p2pInterface(self)
        self.chain = Blockchain(self, name,self.p2pInterface)
        self.initialize_consensus(name)

    def initialize_consensus(self, name):
        self.consensus = GPoHC(self, name)

    @staticmethod
    def runtime(self, first_run=True):
        pass

    def run(self):
        try:
            data_queue = Queue()
            self.main_thread = threading.Thread(target=self.p2pInterface.listen, args=(data_queue,), daemon=True)
            self.main_thread.start()
            first_run = True
            while self.p2pInterface.listening:
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

    def shutdown(self):
        self.p2pInterface.listening = False
        self.main_thread.terminate()

    def restart(self):
        self.shutdown()
        self.run()