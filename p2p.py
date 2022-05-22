from imports import *

class p2pInterface:
    def __init__(self):
        self.peerList = {}

    def addPeer(self, peer, ping=True):
        if peer not in self.peerList.keys():
            self.peerList[peer] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.peerList[peer].connect(peer)
            if self.listening:
                self.peerList[peer].send(b"conn:req")
            return True

    def removePeer(self, peer):
        self.peerList[peer].close()
        del self.peerList[peer]

    def broadcast(self, message):
        for _,sock in self.peerList:
            sock.send(message)

    def listen(self, port):
        self.listening = True
        self.open_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.open_port.bind(('', port))
        self.open_port.listen(5)
        while self.listening:
            for sock,_,_ in select.select([self.peerList[sock] for _,sock in self.peerList].append(self.open_port), [], [],1):
                if sock == self.open_port:
                    conn, addr = self.open_port.accept()
                    data = sock.recv(1024)
                    if data == b"conn:req":
                        self.addPeer(sock.getpeername())
                else:
                    pass #TODO: handle communication