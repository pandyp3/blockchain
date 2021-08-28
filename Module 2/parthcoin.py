# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 22:30:00 2021

@author: Parth
"""

# Module 2 - Create a cryptocurrency
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse 

# Part 1 - Building a Blockchain

class Blockchain:
    def __init__(self):
        # will need to create a list of transactions before it's added to a block (medpool)
        self.chain = []
        self.transactions = []
        self.createBlock(proof = 1, prevHash = '0') #genesis block prev hash is null
        self.nodes = set() #define as set since order doesnt matter
        
    def createBlock(self, proof, prevHash):
        block = {
            'index': len(self.chain) + 1, 
            'timestamp': str(datetime.datetime.now()), 
            'proof': proof, 
            'Previous Hash': prevHash, 
            'Transactions': self.transactions}
        self.transactions = [] #after the transactions are added to the block, the list must be emptied (start over) so that another mined block does not contain the same list
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
    
    def addTransaction(self, sender, receiver, amount):
        # add new transaction (dictionary) to medpool
        self.transactions.append({
            'sender': sender, 
            'receiver': receiver, 
            'amount': amount})
        # find the index of the last block + 1 (equal to next block index)
        previousBlock = self.getPrevBlock()
        return previousBlock['index'] + 1
    
    def addNode(self, address):
        #add node based on address, to set
        parsedURL = urlparse(address)
        self.nodes.add(parsedURL.netloc)
        
    def replaceChain():
        network = self.nodes
        longestChain = None
        maxLength = len(self.chain) #initializing maxLength as the length of the current node's chain
        for node in network:
            response = requests.get(f'http://{node}/getchain')
            if response.status_code == 200:
                #take the length
                length = response.json()['length']
                chain = response.json()['chain']
                if length > maxLength and self.isChainValid(chain):
                    maxLength = length
                    longestChain = chain
        if longestChain:
            self.chain = longestChain
            return True
        return False #if longest chain was never replaced, then the initial chain was the longest the whole time
    
# Part 2 - Mining our blockchain
# Creating a web app via Flask
        
#Creating an address for the node on Port 5000
nodeAddress = str(uuid4()).replace('-', '')
        
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
    blockchain.addTransaction(sender = nodeAddress, receiver = 'Hadelin', amount= 1)    
    block = blockchain.createBlock(proof, prevHash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'Previous Hash': block['Previous Hash'],
                'Transactions': block['Transactions']
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
    elif chainResp == True:
        response = {'message': 'This chain is valid'}
    return jsonify(response), 200
    
#Adding a new transaction to the blockchain
@app.route('/addTransaction', methods=['POST'])
def addTransaction():
    #the post request content type must be JSON for this to work
    json = request.get_json()
    transactionKeys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transactionKeys): #***Rmbr this syntax to check between two lists
        return 'Some elements for the transaction are missing', 400
    index = blockchain.addTransaction(
        sender = json['sender'], 
        receiver = json['receiver'], 
        amount = json['amount'])
    response = {'message': f'This transaction will be added to block {index}'}
    return jsonify(response), 201
    
# Part 3 - Decentralizing our blockchain
#Connecting new nodes
@app.route('/connectNode', methods=['POST'])
def connectNode():
    json = request.get_json()
    nodes = json.get('nodes') #will return list of nodes
    #make sure list is not empty
    if nodes is None:
        return 'No nodes', 400
    else:
        for node in nodes:
            blockchain.addNode(node)
    response = {'message': f'All the nodes are now connected. The Parthcoin Blockchain now contains the following nodes:',
                'total nodes': list(blockchain.nodes)}
    return jsonify(response), 201

#Replacing the chain by the longest chain if needed
@app.route('/replaceChain', methods=['GET'])
def replaceChain():
    chainRepl = blockchain.replaceChain()
    if chainRepl == False:
        response = {'message': 'Chain was not replaced',
                    'New Chain': blockchain.chain}
    elif chainRepl == True:
        response = {'message': 'Chain was replaced',
                    'New Chain': blockchain.chain}
    return jsonify(response), 200

#Running the app
app.run(host= '0.0.0.0', port=5000)
        
