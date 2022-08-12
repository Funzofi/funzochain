from imports import *
import gan

class GPoHC():
    def __init__(self, node, name):
        self.strenght = 50
        self.node = node
        self.model = object()
        self.generator = gan.Generator()
        self.discriminator = gan.Descriminator()
        self.new = True

    def initialize(self):
        if self.generator.new == True:
            self.generator.train(self.node.chain)

        if self.discriminator.new == True:
            self.discriminator.train(self.node.chain)

    def create_consensus(self, block, chain):
        hash = block.calculate_hash()

        SOURCE_BLOCKS = []
        for validator_block in range(min([self.strenght, len(chain)])):
            if self.validator_online(chain[validator_block]):
                SOURCE_BLOCKS.append(validator_block)

        SOURCE_SEED = ""
        for block in SOURCE_BLOCKS:
            SOURCE_SEED.append(block.seed)

        SEED_ROOT = self.collect_seed_root(SOURCE_SEED)

        SUPER_SEED = self.generator.gen(SEED_ROOT)

        score, scores = self.score_super_seed(SUPER_SEED)
        block.validators = scores

        SEED = rsa.encrypt(bytes(SUPER_SEED[:117]), self.node.private_key)

        return True, SEED

    def add_by_each_byte(self, a, b):
        result = ""
        for i in range(len(a)):
            result += ord(a[i]) + b[i]

        return result

    def validator_online(self, block):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(block.creator)
        sock.send(b"conn:ack")
        if sock.recv(8) == b"conn:ack":
            return True
        return False

    def roots_broadcast_handler(self, sock):
        return list(sock.recv(128))

    def collect_seed_root(self, source_seed):
        roots = self.node.p2pInterface.broadcast([
            b"seed:rot",
            f'{len(source_seed):05d}'.encode(),
            source_seed.encode()
        ], handler=self.roots_broadcast_handler)

        out = [0]*128
        for root in roots:
            for byte in range(128):
                out[byte] += root[byte]
            out[byte] = out[byte] % 255

        return out

    def seed_score_broadcast_handler(self, sock):
        score_len = int(sock.recv(2).decode())
        score = (sock.getpeername(), float(sock.recv(score_len).decode()))
        return score

    def score_super_seed(self, super_seed):
        scores = self.node.p2pInterface.broadcast([
            b"seed:scr",
            f'{len(super_seed):05d}'.encode(),
            bytes(super_seed)
        ], handler=self.seed_score_broadcast_handler)

        total_score = 0
        for score in scores:
            total_score += score[1]

        return total_score, scores