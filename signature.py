from imports import *

class Signature:
    def __init__(self, private_key=rsa.newkeys(2048)[0]):
        self.private_key = rsa.PrivateKey.load_pkcs1(private_key)
        self.public_key = self.get_public_key()

    @property
    def public_key(self):
        return self.private_key.public_key()

    def verify(self, data, signature, public_key):
        return rsa.verify(data, signature, self.public_key)

    def sign(self, data):
        return rsa.sign(data, self.private_key, 'SHA-256')