from imports import *
from block import Block
import json

class Blockchain(list):
    def __init__(self, mainfile, p2pInterface):
        self.chain = list()
        self.index = dict()
        self.mainfile = mainfile
        self.p2pInterface = p2pInterface
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
                b"blck:new",
                f'{len(block_data):05d}'.encode(),
                block_data
            ])
        else:
            raise TypeError("Blockchain can only append blocks")

    def save(self):
        block_index = 0
        for iter_ in range(len(self.chain)):
            with open(self.currfile, "wb") as f:
                print(self.currfile)
                for item in self.chain[block_index:50]:
                    f.write(item.serialised)
                    f.write("\n".encode())
                if len(self.chain) > 50*(iter_+1):
                    f.write("\n\n".encode())
                    print(50*(iter_+1))
                    print((iter_+1)*50)
                    self.currfile = self.chain[(iter_+1)*50].calculate_hash()
                    f.write(self.currfile.encode())
        self.load()
                
        self.currfile = self.mainfile

    def load(self):
        self.currfile = self.mainfile
        self.index = dict()
        while True:
            try:
                chain_lenght = 0
                with open(self.currfile, "rb") as f:
                    for line in f.readlines():
                        if line != b"\n":
                            block = Block(self, "").deserialised(line)
                            self.index[block.hash] = chain_lenght
                            chain_lenght += 1
                            self.chain.append(block)
                    if f.readline()[-2] == f.readline()[-3] == b"\n":
                        print(f.readline[-1])
                        self.currfile = f.readline()[-1].decode()
                    else:
                        break
            except:
                break
            

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