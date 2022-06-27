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
        "scr"
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
    def req(self, peer):
        remote_host = peer.recv(64).decode().split(":")
        remote_host = (remote_host[0],int(remote_host[1]))
        self.addPeer(remote_host,False)

    def ack(self, peer):
        peer.send(b"conn:ack")

    def drp(self, peer):
        self.removePeer(peer.getpeername())

class block_handler():
    def new(self, peer):
        data_lenght = peer.recv(5)
        data = peer.recv(int(data_lenght))
        return "blck", data

    def req(self, peer):
        pass

    def ack(self, peer):
        pass

class transaction_handler():
    def new(self, peer):
        pass

    def req(self, peer):
        pass

    def ack(self, peer):
        pass

class seed_handler():
    def scr(self, peer):
        seed = peer.recv(512)
        peer.send(self.score_seed(seed))

    def score_seed(self, seed):
        return "0"

handlers = {
    "conn": connection_handler,
    "blck": block_handler,
    "trnx": transaction_handler
}