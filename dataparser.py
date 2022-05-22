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
    ]
}

def parse_data(data):
    data = data.split(":")
    if data[0] in comm_types.keys():
        if data[1] in comm_types[data[0]]:
            return data[0], data[1]
        else:
            return None, None
    else:
        return None, None

class connection_handler():
    def req(self, peer):
        pass

    def ack(self, peer):
        pass

    def drp(self, peer):
        pass

class block_handler():
    def new(self, peer, block):
        pass

    def req(self, peer, block):
        pass

    def ack(self, peer, block):
        pass

class transaction_handler():
    def new(self, peer, transaction):
        pass

    def req(self, peer, transaction):
        pass

    def ack(self, peer, transaction):
        pass

handlers = {
    "conn": connection_handler,
    "blck": block_handler,
    "trnx": transaction_handler
}