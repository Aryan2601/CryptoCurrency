"""
Created on Sun Mar 29 00:13:23 2020
@author: aryan
"""
#requests==2.18.4 : pip install requests==2.18.4 
    
#creating a CryptoCuurency
# Importing the Libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request #request library is for connecting node to decentralized blockchain network we will use getjson function that will 
#be taken from request 
import requests #this will be used to check the node in decentralized network re all in the same chain
from uuid import uuid4
from urllib.parse import urlparse




# Part 1 - Building a Blockchain
class BlockChain:
    
    def __init__(self): # here we are initializing the block chain
        self.chain = [] #it is a list where we will append diffrent blocks that will be mined
        self.transactions = [] #Making list of transactions before they are added to a block
        self.create_block(proof = 1, previous_hash = '0' ) #genesis block created by create block with proof 1 and prevous hash 0 
        #creating the genesis block
        self.nodes = set() 
    def create_block(self, proof, previous_hash):#here previous hash is the key element that links two blocks in a row here we will take proof as this is what our create block function will give us
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),#to check at what date and time the changes where made
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}#here it will take all the transactions 
        self.transactions = [] #here we make the transcations empty after adding the transactions in a block 
        self.chain.append(block) 
        return block 
    
    
    def get_previous_block(self): #here this will get us the previous proof of the blockchain
    
        return self.chain[-1] 
    
    def proof_of_work(self, previous_proof): # it is a piece of data where minors have to in oreder to mine a new block here function takes two argument self and previuos 
    #proof which is element of problem to be solved by minors
        new_proof = 1                        # here we will define a problem which minors have to solve and mine inside the block
        check_proof = False                  #here it will check if the new proof is the right proof
        while check_proof is False:          #here the wile loop will work unless the checkproof becomes true
            hash_operation = str(hashlib.sha256(new_proof**2 - previous_proof**2).encode()).hexdigest   # here this is the operation for finding the value by solving this         
            #here this will be a string of 64 character it will take new proof and checkproof
             #by adding here hexdigest we get the encode value in hexadecimal if we solve newproof and previuos proof and encode it then we will convert it to hexdecimal
            if hash_operation[:4] == "0000":    #if first four character of this hash are 0000 if that happens minor wins and check proof will be set to true  
                check_proof = True 
            else: 
                new_proof += 1
        return new_proof 
    def hash(self, block): #it will take a block as input and return the sha256
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    def is_chain_valid(self,chain):
        previous_block = chain(0)
        block_index = 1
        while block_index < len(chain):
            
            block = chain(block_index)                # here we will check if the hash of the block is equal to the previuos hash of the other block
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            #now we will check if previous proof and the proof of the block starts with 4 leading zeros
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest
            if hash_operation[:4] != '0000':
                return False 
            previous_block = block 
            block_index += 1
        return True 
    
    def add_transaction(self, sender, receiver, amount):#this is the method which will create transaction between the sender and reciever which will add our transaction to list of transactions
        
        self.transactions.append({'sender': sender,   #here we will be appending the new transactions 
                                  'receiver': receiver,
                                  'amount': amount,}) 
        previous_block = self.get_previous_block()
        return previous_block['index']+1
    
    def add_node(self, address):
        parsed_url = urlparse(address) #we will parse the address of the node here 
        self.nodes.add(parsed_url.netloc) #netloc is the url including the port 5000
       
    def replace_chain(self):
        network = self.nodes  #this is network containing all the set of nodes
        longest_chain = None 
        max_length = len(self.chain)
        for nodes in network:
            response = requests.get(f'http://{node}/get_chain') 
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain   
            return True
        return False #if the chain is not replaced 
             
        
# Part 2 - Mining our Blockchain


#creating a web app
app = Flask(__name__)  

#Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '') #adding unique id to every block 


#creating a blockchain 
blockchain  = Blockchain() 


#Mining a new block 
@app.route('/mine_block', methods = ['GET'])
def mine_block():#this function will mine a block 
    previous_block = blockchain.get_previous_block() 
    previous_proof = previous_block('proof')
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, reciever = 'Aryan', amount = 1)
    block = blockchain.create_block(proof,previous_hash)
    response = {'message':'Congrats You just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200

# Getting the full Blockchain

@app.route('/get_chain', methods = ['GET']) 
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)} 
    return jsonify(response), 200
   
#for checking blockchain is valid
@app.route('/is_valid', methods = ['GET'] )
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Block Chain is Valid.'}
    else:
        response = {'message': 'Blockchain is Invalid '}
    return jsonify(response), 200
#Adding a new transaction to the Blockchain 
@app.route('/add_transaction', methods = ['POST'] )
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']        #to check all the keys in json file are present
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 404
    index = blockchain.add_transaction(json['sender'], json['receiver'],json['amount'])
    response = {'message': f'This transaction will be added to Block (index)'}
    return jsonify(response), 201

# Decentralizing Blockchain 

#Connecting new nodes
@app.route('/connect_node', methods = ['POST'] )
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')#will get the values of the keys
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'all the nodes are now connected. the mycoin Blockchain now contains the Following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201


# Running the app by flask app
 
app.run(host = '0.0.0.0' port = 5000)   #here we will add host and port 

    
    
    







































