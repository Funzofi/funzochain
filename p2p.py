import os
from random import shuffle
from imports import *
import connection_handler

class p2pInterface:
    def __init__(self):
        self.peerList = {}

    def addPeer(self, peer, ping=True):
        if peer not in self.peerList.keys():
            self.peerList[peer] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.peerList[peer].connect(peer)
            self.peerList[peer].send(b"conn:req")
            return True

    def removePeer(self, peer):
        self.peerList[peer].close()
        del self.peerList[peer]

    def broadcast(self, message):
        for _,sock in self.peerList:
            sock.send(message)

    def sync_chain(self, node):
        shuffled_nodes = list(self.peerList.keys())
        shuffle(shuffled_nodes)
        node_c = 0
        sync_candidates = {}
        for peer in shuffled_nodes:
            if node_c < 3:
                try:
                    self.peerList[peer].send("data:int".encode())
                    remote = node.socket.recv(64)
                    sync_candidates[peer] = remote
                except:
                    self.removePeer(peer)
            node_c += 1
        valid_candidates = max(list({rem: [peer for peer in sync_candidates.keys() if sync_candidates[peer] == rem] for rem in sync_candidates.values()}.values()),key=len)
        progress = 0
        if "\\" in node.chainFile:
            os.makedirs(os.path.dirname(node.chainFile), exist_ok=True)
        with open(node.chainFile, "wb") as f:
            for peer in valid_candidates:
                self.peerList[peer].send("data:syn".encode())
                self.peerList[peer].send(str(progress).encode())
                while True:
                    remote = node.socket.recv(64)
                    print(remote)
                    f.write(remote)
                    if len(remote) < 64:
                        print("Reached end of chain")
                        node.chain = pickle.load(open(node.chainFile, "rb"))
                        return
                    progress += 1

    def listen(self, port):
        self.listening = True
        self.open_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.open_port.bind(('', port))
        self.open_port.listen(5)
        while self.listening:
            for sock,_,_ in select.select([self.peerList[sock] for _,sock in self.peerList].append(self.open_port), [], [],1):
                if sock == self.open_port:
                    sock, addr = self.open_port.accept()
                data = sock.recv(8)
                class_, type = connection_handler.parse_data(data)
                connection_handler.handlers[class_].getattr(type)(self, sock)