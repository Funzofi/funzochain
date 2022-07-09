from imports import *
from block import Block
import json

class Blockchain(list):
    def __init__(self, mainfile):
        self.chain = list()
        self.index = dict()
        self.mainfile = mainfile
        self.load()

    def __getitem__(self, key):
        return self.chain[key]

    def append(self, item):
        if isinstance(item, Block):
            if item.hash in self.index:
                raise ValueError("Block already exists")
            self.index[item.calculate_hash()] = len(self.chain)
            self.chain.append(item)
            self.save()
            block_data = item.serialised
            self.p2pInterface.broadcast([
                "blck:new",
                f'{len(block_data):05d}'.encode(),
                block_data
            ])
        else:
            raise TypeError("Blockchain can only append blocks")

    def save(self):
        with open(self.currfile, "wb") as f:
            f.write(json.dumps(self.chain[:50]).encode())
            if len(self.chain[:50]) == 50:
                f.write("\n\n".encode())
                f.write(self.chain[50].calculate_hash().encode())
                
        self.currfile = self.mainfile

    def load(self):
        self.currfile = self.mainfile
        while True:
            try:
                with open(self.currfile, "rb") as f:
                    if f.readline()[-2] == f.readline()[-3] == b"\n":
                        self.currfile = f.readline()[-1].decode()
                    else:
                        break
            except:
                break
        try:
            with open(self.currfile, "rb") as f:
                data = f.read()
                self.chain = json.loads(data)
        except:
            self.chain = list()
            

    def __setitem__(self, key, value):
        raise IndexError("Cannot set in blockchain")

    def __delitem__(self, key):
        raise IndexError("Cannot delete from blockchain")

    def __len__(self):
        return len(self.chain)

    def __iter__(self):
        return iter(self.chain)

    def __contains__(self, item):
        return item in self.index