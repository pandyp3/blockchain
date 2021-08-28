# -*- coding: utf-8 -*-
"""
Created on Mon Aug  9 21:11:36 2021

@author: Parth
"""

# Module 1 - Create a blockchain

import datetime
import hashlib
import json
from flask import Flask, jsonify

# Part 1 - Building a Blockchain

class Blockchain:
    def __init__(self):
        self.chain = []
        self.createBlock(proof = 1, prevHash = '0') #genesis block prev hash is null
        
    def createBlock(self, proof, prevHash):
        block = {'index': len(self.chain) + 1, 'timestamp': str(datetime.datetime.now()), 'proof': proof, 'Previous Hash': prevHash}
        self.chain.append(block)
        return block
    
    def getPrevBlock(self):
        return self.chain[-1]
    
    def proofOfWork(self, prevProof):
        newProof = 1 #starting at 1 because we iterate by one in a while loop until the right proof is found
        checkProof = False
        while checkProof is False:
            hashOperation = hashlib.sha256(str(newProof**2 - prevProof**2).encode()).hexdigest()
            if hashOperation[:4] == '0000':
                checkProof = True
            else:
                newProof += 1
        return newProof
    
    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encodedBlock).hexdigest()
    
    def isChainValid(self, chain):
        prevBlock = chain[0]
        blockIndex = 1
        while blockIndex < len(chain):
            block = chain[blockIndex]
            if block['Previous Hash'] != self.hash(prevBlock):
                return False
            prevProof = prevBlock['proof']
            proof = block['proof']
            hashOperation = hashlib.sha256(str(proof**2 - prevProof**2).encode()).hexdigest()
            if hashOperation[:4] != '0000':
                return False
            prevBlock = block
            blockIndex += 1
        return True
    
# Part 2 - Mining our blockchain
# Creating a web app via Flask
        
app = Flask(__name__)    
#app.config['JSONIFY_PRETTYPRINT_REGULAR'] = FALSE


# Creating a blockchain

blockchain = Blockchain()

@app.route('/mineblock', methods=['GET'])
def mineblock():
    prevBlock = blockchain.getPrevBlock()
    prevProof = prevBlock['proof']
    proof = blockchain.proofOfWork(prevProof)
    prevHash = blockchain.hash(prevBlock)
    block = blockchain.createBlock(proof, prevHash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'Previous Hash': block['Previous Hash']
                }
    return jsonify(response), 200

#Getting the full blockchain
    
@app.route('/getchain', methods=['GET'])
def getchain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain),
                }
    return jsonify(response), 200

@app.route('/isvalid', methods=['GET'])
def isValid():
    chain = blockchain.chain
    chainResp = blockchain.isChainValid(chain)
    if chainResp == False:
        response = {'message': 'The chain is not valid; please review'}
        return jsonify(response), 200
    elif chainResp == True:
        response = {'message': 'This chain is valid'}
        return jsonify(response), 200
        
    
#Running the app
app.run(host= '0.0.0.0', port=5000)
        
