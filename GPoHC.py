from imports import *
from gan import MockGAN as GAN
from block import Block, LogBlock

class GPoHC():
    def __init__(self, node, name):
        self.strenght = 50
        self.node = node
        self.model = GAN(name)
        self.new = True

    def initialize(self):
        if self.new:
            self.model.initialize()
            self.model.feedData(self.node.chain)
            self.model.train()
            self.model.trainClassifier()

    def create_consensus(self, block, chain):
        hash = block.calculate_hash()

        SOURCE_BLOCKS = []
        for validator_block in range(self.strenght):
            if self.validator_online(chain[validator_block]):
                SOURCE_BLOCKS.append(validator_block)

        SOURCE_SEED = ""
        for block in SOURCE_BLOCKS:
            SOURCE_SEED.append(block.seed)

        SEED_ROOT = self.collect_seed_root(SOURCE_SEED)

        SEED_ROOT_PROCESSED = self.preprocess_seed_root(SEED_ROOT)

        SUPER_SEED = self.model.generator_forward(SEED_ROOT_PROCESSED)

        score, scores = self.score_super_seed(SUPER_SEED)
        block.validators = scores

        SEED = rsa.encrypt(SUPER_SEED, self.node.private_key)

        return SEED

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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(block.address)
        sock.send(b"conn:ack")
        if sock.recv(8) == b"conn:ack":
            return True
        return False

    def roots_broadcast_handler(self, sock, seed):
        return list(sock.recv(128))

    def collect_seed_root(self, source_seed):
        roots = self.node.p2pInterface.broadcast([
            b"seed:rot",
            f'{len(source_seed):05d}'.encode(),
            source_seed.encode()
        ])

        out = [0]*128
        for root in roots:
            for byte in range(128):
                out[byte] += root[byte]
            out[byte] = out[byte] % 255

    def seed_score_broadcast_handler(self, sock, seed):
        score_len = int(sock.recv(2).decode())
        score = (sock.getpeername(), int(sock.recv(score_len).decode()))
        return score

    def score_super_seed(self, super_seed):
        scores = self.node.p2pInterface.broadcast([
            b"seed:scr",
            f'{len(super_seed):05d}'.encode(),
            super_seed.encode()
        ])

        total_score = 0
        for score in scores:
            total_score += score[1]

        return total_score, scores