import hashlib
import json

class Block(object):

    def __init__(self,index=None,timestamp=None,data=None,previous_hash=None,proof=None):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.proof = proof

    def calculate_hash(self):
        """
        Calculate the hash for the block
        :return: <string> the SHA256 Hash of the block
        """
        return hashlib.sha256(json.dumps(self.__dict__)).hexdigest()
