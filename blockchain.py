from imports import *
from block import Block
import json

class Blockchain(list):
    def __init__(self, node, mainfile, p2pInterface):
        self.chain = list()
        self.index = dict()
        self.node = node
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
            print(f"Added block {item.hash[:6]} to chain")
            self.save()
            block_data = item.serialised
            self.p2pInterface.broadcast([
                b"blck:new",
                f'{len(block_data):05d}'.encode(),
                block_data.encode()
            ])
        else:
            raise TypeError("Blockchain can only append blocks")

    def save(self):
        old_file = self.currfile
        block_index = 0
        with open(self.currfile, "r") as f:
            file_size = len(f.readlines())
        for iter_ in range(int(len(self.chain)/50)+1):
            with open(self.currfile, "w") as f:
                for item in self.chain[block_index:(50-file_size)]:
                    f.write(item.serialised)
                    f.write("\n")
                if len(self.chain) > 50*(iter_+1):
                    f.write("\n\n")
                    self.currfile = self.chain[(iter_+1)*50].calculate_hash()
                    f.write(self.currfile)
                    file_size = 0
        if old_file != self.currfile:
            self.load()

    def load(self):
        self.currfile = self.mainfile
        self.index = dict()
        if os.path.exists(self.currfile):
            print("Loading blockchain")
            while True:
                chain_lenght = 0
                with open(self.currfile, "r") as f:
                    for line in f.readlines():
                        if line != "\n":
                            print(line)
                            block = Block(self.node, "").deserialised(line)
                            print(block.__dict__)
                            self.index[block.hash] = chain_lenght
                            chain_lenght += 1
                            self.chain.append(block)
                        else:
                            break
                    print(f.readlines())
                    if len(f.readlines()) > 50:
                        self.currfile = f.readline()[-1]
                        break
                    else:
                        return
        else:
            print("Started A New Chain")
            open(self.currfile, "w")
            

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