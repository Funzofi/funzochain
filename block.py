from imports import *

class Block(object):
    def __init__(self, node, data, seed=b"", validators=[]):
        self.creator = node.address
        self.data = data
        self.timestamp = time.time()
        self.seed = seed
        self.validators = validators
        self.hash = self.calculate_hash()

    def valid(self):
        if self.hash != self.calculate_hash():
            return False
        try:
            rsa.decrypt(self.seed, self.creator)
        except:
            return False
        return True

    def calculate_hash(self):
        data = self.__dict__
        if "hash" in data.keys():
            del data["hash"]
        return hashlib.sha256(pickle.dumps(data)).hexdigest()

    @property
    def serialised(self):
        return pickle.dumps(self.__dict__)

    def deserialised(self, data):
        block = self.__class__()
        block.__dict__ = pickle.loads(data)
        return block

class LogBlock(Block):
    def __init__(self, node, msg):
        self.creator = node.address
        self.message = msg
        self.timestamp = time.time()
        self.hash = self.calculate_hash()