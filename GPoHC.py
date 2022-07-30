from gan import Gan

class GPoHC():
    def __init__(self):
        self.strenght = 50
        self.model = Gan()

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

        SEED_ROOT_PROCESSED = []
        for char in SEED_ROOT:
            SEED_ROOT_PROCESSED.extend([int(y) for y in list("".join(format(ord(x), 'b') for x in str(char)))])

        SUPER_SEED = self.model.generator_forward(SEED_ROOT_PROCESSED)
        self.broadcast_super_seed(SUPER_SEED)

    def add_by_each_byte(self, a, b):
        result = ""
        for i in range(len(a)):
            result += ord(a[i]) + b[i]

        return result


    def validator_online(self, block):
        pass