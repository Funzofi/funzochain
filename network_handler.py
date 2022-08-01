from imports import *

comm_types = {
    "conn": [
        "req",
        "ack",
        "drp"
    ],
    "blck": [
        "new",
        "req",
        "ack",
    ],
    "trnx": [
        "new",
        "req",
        "ack",
    ],
    "data": [
        "syn",
        "int",
    ],
    "seed": [
        "scr",
        "rot",
    ]
}

def parse_data(data):
    data = data.decode().split(":")
    if data[0] in comm_types.keys():
        if data[1] in comm_types[data[0]]:
            return data[0], data[1]
        else:
            return None, None
    else:
        return None, None

class connection_handler():
    def req(self, peer, node):
        addr_lenght = peer.recv(2)
        remote_host = peer.recv(int(addr_lenght)).decode().split(":")
        remote_host = (remote_host[0],int(remote_host[1]))
        self.addPeer(remote_host,False)

    def ack(self, peer, node):
        peer.send(b"conn:ack")

    def drp(self, peer, node):
        self.removePeer(peer.getpeername())

class block_handler():
    def new(self, peer, node):
        data_lenght = peer.recv(5)
        data = peer.recv(int(data_lenght))
        return "blck", data

    def req(self, peer, node):
        pass

    def ack(self, peer, node):
        pass

class transaction_handler():
    def new(self, peer, node):
        pass

    def req(self, peer, node):
        pass

    def ack(self, peer, node):
        pass

class seed_handler():
    def scr(self, peer, node):
        seed = peer.recv(512)
        score = node.consensus.model.clf_score(seed)
        peer.send(f'{len(score):02d}'.encode())
        peer.send(score)
        self.seed_store[seed] = score

    def rot(self, peer, node):
        seed_lenght = peer.recv(5)
        peer.send(rsa.encrypt(peer.recv(seed_lenght), node.private_key))

handlers = {
    "conn": connection_handler,
    "blck": block_handler,
    "trnx": transaction_handler,
    "seed": seed_handler,
}