import ctypes
import string

class Libp2p:
    def __init__(self):
        lib = ctypes.CDLL("./_libp2p.so")
        
        self.start = string_at_wrapper(lib.Start, [ctypes.c_char_p], ctypes.c_char_p)

        self.stop = lib.Stop

        self.createHandler = lib.CreateHandler
        # Pass a function
        self.createHandler.argtypes = [ctypes.c_char_p, ctypes.c_void_p]
        self.createHandler.restype = None

        self.connect = lib.Connect
        self.connect.argtypes = [ctypes.c_char_p]
        self.connect.restype = None

        self.getPeerAddr = string_at_wrapper(lib.GetPeerAddrs, [], ctypes.c_char_p)
        
def string_at_wrapper(f, argtypes, restype):
    def wrapper(*args):
        f.argtypes = argtypes
        f.restype = restype
        return ctypes.string_at(f(*args))
    return wrapper
