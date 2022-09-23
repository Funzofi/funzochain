import ctypes
from libp2p import Libp2p

def echo(msg):
    print(msg)

# Convert echo to ctype
echo = ctypes.CFUNCTYPE(None, ctypes.c_char_p)(echo)

if __name__ == "__main__":
    libp2p = Libp2p()
    print(libp2p.start(b"/ip4/0.0.0.0/tcp/0"))
    libp2p.createHandler(b"/echo/1.0.0", echo)
    print(libp2p.getPeerAddr())
    if input("Connect? (y/n)") == "y":
        libp2p.connect(f'/ip4/{input("Address: ")}/tcp/{input("Port: ")}'.encode())
    while True:
        pass