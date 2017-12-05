from datetime import datetime
import time
import hashlib
from uuid import uuid4

from block import Block
from node import Node

import requests

class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash=1, proof=100)
        self.nodes = set()

    def register_node(self,address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """
        self.nodes.add(Node(address))

    def get_chain(self):
        """
        Get the blockchain
        :return: <list> returns a list of blocks
        """
        chain = []
        for block in self.chain:
            chain.append(block.__dict__)
        return chain

    def unserialize_chain(self,chain):
        """
        Unserialize a chain
        :return: <list> returns list of objects
        """
        unserialized_chain = []
        for block in chain:
            unserialized_chain.append(Block(
                block['index'],
                block['timestamp'],
                block['data'],
                block['previous_hash'],
                block['proof']))
        return unserialized_chain

    def get_latest_block(self):
        """
        Get the latest block in the chain
        :return: <object> Block if the length of the chain list is greater than 1 else returns None
        """
        if len(self.chain) > 0:
            return self.chain[-1]
        return None

    def new_block(self,proof,previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        block = Block(
            len(self.chain) + 1,
            time.mktime(datetime.now().timetuple()),
            self.current_transactions,
            self.get_latest_block().hash if self.get_latest_block() else previous_hash,
            proof)
        self.current_transactions = []
        self.chain.append(block)

        return block

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

        last_block = self.get_latest_block()
        return  last_block.index + 1 if last_block else 1

    def is_chain_valid(self,chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # Check that the hash of the block is correct
            if block.previous_hash != last_block.hash:
                return False
            if not self.valid_proof(last_block.proof,block.proof):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        Consensus Algorithm, which resolves conflicts
        by replacing the chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """
        neighbours = self.nodes
        new_chain = None

        # Look for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get('http://{node_location}/chain'.format(node_location=node.get_network_location()))

            if response.status_code == 200:
                length = response.json()['length']
                chain = self.unserialize_chain(response.json()['chain'])

                # Check if the length is longer and the chain is valid
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

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
