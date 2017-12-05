from block import Block
from datetime import datetime
import time
import hashlib
from uuid import uuid4

class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.newBlock(previous_hash=1, proof=100)

    def getChain(self):
        """
        Get the blockchain
        :return: <list> returns a list of blocks
        """
        chain = []
        for block in self.chain:
            chain.append(block.__dict__)
        return chain

    def getLatestBlock(self):
        """
        Get the latest block in the chain
        :return: <object> Block if the length of the chain list is greater than 1 else returns None
        """
        if len(self.chain) > 0:
            return self.chain[-1]
        return None

    def newBlock(self,proof,previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        new_block = Block(
            len(self.chain) + 1,
            time.mktime(datetime.now().timetuple()),
            self.current_transactions,
            self.getLatestBlock().hash if self.getLatestBlock() else previous_hash,
            proof)
        self.current_transactions = []
        self.chain.append(new_block)

        return new_block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            })

        last_block = self.getLatestBlock()
        return  last_block.index + 1 if last_block else 1

    def isChainValid(self):
        """
        Check if the chain is valid
        :return <bool> The validity of the chain
        """
        for i in range(1, len(self.chain)):
            currentBlock = self.chain[i]
            previousBlock = self.chain[i-1]
            if currentBlock.hash != currentBlock.calculateHash():
                return False
            elif currentBlock.previous_hash != previousBlock.hash:
                return False
            else:
                return True

    def proof_of_work(self,last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof,proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof,proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        guess = "{last_proof}{proof}".format(last_proof=last_proof,proof=proof).encode()
        return hashlib.sha256(guess).hexdigest()[:4] == "0000"
