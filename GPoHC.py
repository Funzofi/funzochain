from gan import GAN
from block import Block, LogBlock

class GPoHC():
    def __init__(self, node, name):
        self.strenght = 50
        self.node = node
        self.model = GAN(name)
        self.new = True
        if self.new:
            self.node.chain.append(LogBlock(self.node, "Initializing Gan"))
            self.model.initialize()
            self.model.feedData(self.chain)
            self.model.train()
            self.model.trainClassifier()
        self.node.chain.append(LogBlock(self.node, "Gan initialized"))

    def create_consensus(self, block, chain):
        hash = block.calculate_hash()

        SOURCE_BLOCKS = []
        for validator_block in range(self.strenght):
            if self.validator_online(chain[-self.strenght[validator_block]]):
                SOURCE_BLOCKS.append(validator_block)

        SOURCE_SEED = ""
        for block in SOURCE_BLOCKS:
            SOURCE_SEED.append(block.seed)

        SEED_ROOT = ""
        for root in self.collect_roots(SOURCE_BLOCKS):
            SEED_ROOT = self.add_by_each_byte(SOURCE_SEED, root)

        SEED_ROOT_PROCESSED = self.preprocess_seed_root(SEED_ROOT)

        SUPER_SEED = self.model.generator_forward(SEED_ROOT_PROCESSED)
        self.score_super_seed(SUPER_SEED)

    def preprocess_seed_root(self, seed_root):
        seed_root_processed = []
        for char in seed_root:
            seed_root_processed.extend([int(y) for y in list("".join(format(ord(x), 'b') for x in str(char)))])
        
        return seed_root_processed

    def add_by_each_byte(self, a, b):
        result = ""
        for i in range(len(a)):
            result += ord(a[i]) + b[i]

        return result


    def validator_online(self, block):
        pass

    def seed_score_broadcast_handler(self, sock, seed):
        score_len = int(sock.recv(2).decode())
        score = (sock.getpeername(), int(sock.recv(score_len).decode()))
        return score

    def score_super_seed(self, super_seed):
        self.model.clf_score(super_seed)