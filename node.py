from gan import Gan
from block import LogBlock
from p2p import p2pInterface

class node():
    def __init__(self, private_key, host, name="chain"):
        self.host = host
        self.private_key = private_key
        self.chainfile = f"{name}.chf"
        self.chain = []
        self.p2pInterface = p2pInterface()

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

    def run(self):
        self.p2pInterface.listen(self.host)