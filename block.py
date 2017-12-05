import hashlib

class Block():

    def __init__(self,index=None,timestamp=None,data=None,previous_hash=None):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculateHash()

    def calculateHash(self):
        return hashlib.sha224(str(self.index)+str(self.previous_hash)+str(self.timestamp)+str(self.data)).hexdigest()
