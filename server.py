from uuid import uuid4
from flask import Flask,jsonify,request
from blockchain import Blockchain
import json
import sys

#Instantiate the Node
app = Flask(__name__)

#Generate a globally unique address for this node
node_identifier =  str(uuid4()).replace('-','')

#Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine',methods=['GET'])
def mine():
    #Run the proof of work algorithm to get the next proof

    last_block = blockchain.get_latest_block()
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)

    # Miner must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(sender="0",recipient=node_identifier,amount=1)

    # Forge the new Block by adding it to the chain
    block = blockchain.new_block(proof)

    response = {
        'message': "New Block Forged",
        'index': block.index,
        'transactions': block.data,
        'proof': block.proof,
        'previous_hash': block.previous_hash,
    }

    return jsonify(response), 200

@app.route('/transactions/new',methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender','recipient','amount']
    if not all(k in values for k in required):
        return 'Missing values',400

    # Create a new transaction
    index = blockchain.new_transaction(values['sender'],values['recipient'], values['amount'])

    response = {'message': "Transaction will be added to Block {index}".format(index=index)}
    return jsonify(response), 201

@app.route('/chain',methods=['GET'])
def full_chain():
    chain = blockchain.get_chain()
    response = {
        'chain':chain,
        'length':len(chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register',methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message':'New nodes have been added',
        'total_nodes':[node.__dict__ for node in blockchain.nodes]
    }

    return jsonify(response), 201

@app.route('/nodes/resolve',methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.get_chain()
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.get_chain()
        }

    return jsonify(response), 200

def getopts(argv):
    """Collect command-line options in a dictionary"""
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts

if __name__ == '__main__':
    from sys import argv
    args = getopts(argv)
    if '-p' in args:
        app.run(host='0.0.0.0',port=args['-p'])
