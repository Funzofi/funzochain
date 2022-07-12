from imports import *
from signature import Signature

class Transaction(object):
    def __init__(self, node, sender, receiver, amount, signature):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()
        self.signature = signature
        self.node = node.address

    def valid(self, transaction):
        if Signature().verify(transaction.calculate_id(), transaction.signature, transaction.sender):
            return True

    def calculate_id(self):
        return hashlib.sha256(self.serialised).hexdigest()

    def calculate_hash(self):
        return hashlib.sha256(self.serialised).hexdigest()

    @property
    def serialised(self):
        dict_ = self.__dict__
        del dict_["node"]
        return pickle.dumps(self.__dict__).hex()

    def deserialised(self, data):
        transaction = self.__class__()
        transaction.__dict__ = pickle.loads(bytes.fromhex(data))
        return transaction