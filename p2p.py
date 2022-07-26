import os
from random import shuffle
from block import Block
from imports import *
import network_handler

class p2pInterface:
    def __init__(self, node):
        self.peerList = {}
        self.node = node

    def addPeer(self, peer, ping=True):
        if peer not in self.peerList.keys():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(peer)
            self.peerList[sock.getpeername()] = sock
            if ping:
                self.peerList[sock.getpeername()].send(b"conn:req")
                message = f"{self.node.host[0]}:{self.node.host[1]}"
                self.peerList[sock.getpeername()].send(f"{len(message):02d}".encode())
                self.peerList[sock.getpeername()].send(message.encode())
            return True
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(peer)
            self.peerList[sock.getpeername()] = sock



    def removePeer(self, peer):
        self.peerList[peer].close()
        del self.peerList[peer]

    def broadcast(self, message):
        print(self.peerList.items())
        for addr, sock in self.peerList.items():
            try:
                print(sock.getpeername())
                if type(message) == bytes:
                    sock.send(message)
                elif type(message) == list:
                    for m in message:
                        sock.send(m)
                        
                sock.close()
                sock = -1
                self.addPeer(addr, False)
            except ConnectionResetError:
                    print(f"Peer {sock.getpeername()} Disconnected", flush=True)
                    self.removePeer(sock.getpeername())
            except OSError:
                print(f"Peer {sock.getpeername()} Disconnected", flush=True)
                self.removePeer(sock.getpeername())

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

    def listen(self, queue):
        self.listening = True
        self.open_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.open_port.bind(self.node.host)
        self.open_port.listen(5)
        while self.listening:
            read_sockets = []
            read_sockets.append(self.open_port)
            for peer in self.peerList.values():
                read_sockets.append(peer)
            for sock in select.select(read_sockets, [], [])[0]:
                try:
                    if sock == self.open_port:
                        sock, addr = self.open_port.accept()
                        print("Connected to", addr, flush=True)
                    data = sock.recv(8)
                    if len(data) == 8:
                        class_, type_ = network_handler.parse_data(data)
                        data = getattr(network_handler.handlers[class_],type_)(self, sock)
                        if data:
                            queue.put(data)
                except ConnectionResetError:
                    print(f"Peer {sock.getpeername()} Disconnected", flush=True)
                    self.removePeer(sock.getpeername())
    
    def stop(self):
        self.listening = False
        self.open_port.close()