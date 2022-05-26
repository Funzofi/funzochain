from imports import *

class block(object):
    def __init__(self, node, data, seed=b"", validators=[]):
        self.creator = node.address
        self.data = data
        self.timestamp = time.time()
        self.seed = seed
        self.validators = validators
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256(self.serialised).hexdigest()

    @property
    def serialised(self):
        return pickle.dumps(self.__dict__)

    def deserialised(self, data):
        block = self.__class__()
        block.__dict__ = pickle.loads(data)
        return block

class LogBlock(block):
    def __init__(self, node, msg):
        self.creator = node.address
        self.message = msg
        self.timestamp = time.time()
        self.hash = self.calculate_hash()