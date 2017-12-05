from uuid import uuid4
from flask import Flask,jsonify,request
from blockchain import Blockchain
import json

#Instantiate the Node
app = Flask(__name__)

#Generate a globally unique address for this node
node_identifier =  str(uuid4()).replace('-','')

#Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine',methods=['GET'])
def mine():
    #Run the proof of work algorithm to get the next proof

    last_block = blockchain.getLatestBlock()
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)

    # Miner must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(sender="0",recipient=node_identifier,amount=1)

    # Forge the new Block by adding it to the chain
    block = blockchain.newBlock(proof)

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
    chain = blockchain.getChain()
    response = {
        'chain':chain,
        'length':len(chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
