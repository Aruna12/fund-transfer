#!/usr/bin/env python

__author__ = 'aruna'

import os
import json
import hashlib
import datetime

from resources.block import Block
from resources.helper import proof_of_work

from flask import Flask, render_template, request

CHAIN_NAME = 'baby_chain1.txt'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('test.html')

@app.route('/hello', methods=['POST'])
def hello():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    amount = request.form['amount']
    global text 
    text = first_name+" "+last_name+" "+amount
    return 'The transaction from %s to %s of amount %s has been done. <br/> ' % (first_name, last_name, amount)


class Blockchain:
    def __init__(self):
        # path to chain
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.chainfile = os.path.join(dir_path, 'chain', CHAIN_NAME)

        self._create_chain_if_not_exists()
        # create genesis block if chainfile is empty
        if os.stat(self.chainfile).st_size == 0:
            self._create_genesis_block()

        self.validate_chain()
        self.data = []


    def _create_chain_if_not_exists(self):
        if not os.path.isfile(self.chainfile):
            f = open(self.chainfile,'w')
            f.close()
        return


    def _create_genesis_block(self):
        '''
        Creates the genesis block. Seperate routine due to the genesis block
            creation being a one-off event.
        '''
        b = Block(index=0,
            timestamp=str(datetime.datetime.now()),
            data='genesis block',
            previous_hash='0',
            nonce=1,
            num_zeros=0)

        self._write_to_chain(b.get_block_data())
        return


    def _write_to_chain(self, block_dictionary):
        '''
        Writes a dictionary to json, appends the json to the blockchain text
            file.
        '''
        with open(self.chainfile, 'a') as f:
            f.write(json.dumps(block_dictionary) + '\n')
            f.close()
        return


    def create_new_block(self):
        '''
        Creates a block using the data in `self.data`.
        '''
        with open(self.chainfile, 'r') as f:
            previous_block = f.readlines()[-1]
            previous_block = json.loads(previous_block)
            f.close()

        index = previous_block['index'] + 1
        previous_hash = previous_block['hash']
        timestamp = str(datetime.datetime.now())
        nonce, number_of_leading_zeros = proof_of_work(previous_hash)
        self.block = Block(index=index,
            timestamp=timestamp,
            data=self.data,
            previous_hash=previous_hash,
            nonce=nonce,
            num_zeros=number_of_leading_zeros)

        self._write_to_chain(self.block.get_block_data())
        self.data = " "
        return


    def add_data_to_block(self, new_data):
        '''
        Appends data to the newest block.
        '''
        self.data = str(new_data)


    def _return_hash(self, previous_hash, nonce):
        sha = hashlib.sha256()
        sha.update(
            str(previous_hash).encode('utf-8') +
            str(nonce).encode('utf-8')
            )
        return sha.hexdigest()


    def _validate_hash(self, _hash, num_zeros):
        if str(_hash[:num_zeros]) != "0" * num_zeros: # checks for leading zeros
            msg = 'Invalid chain.'
            raise ValueError(msg)
        else:
            return True


    def validate_chain(self, chain=''):
        '''
        Checks the chain for validity. Returns True on validation.
        '''
        num_of_indexes_at_0 = 0

        if not chain:
            chain = self.chainfile

        with open(chain, 'r') as f:
            for line in f:
                #print("VALIDATION OF NEXT BLOCK : ")
                #print()
                block_to_validate = json.loads(line)

                number_of_zeros = block_to_validate['num_zeros']
                nonce = block_to_validate['nonce']
                index = block_to_validate['index']
                previous_hash = block_to_validate['previous_hash']
                block_hash = block_to_validate['hash']
                timestamp = block_to_validate['timestamp']
                block_data = block_to_validate['data']

                #print("Validation : ",block_to_validate['data'])
                x = Block(index,timestamp,block_data,previous_hash,nonce,number_of_zeros)
                calculated_hash= x.hash_block()
                '''
                sha = hashlib.sha256()
                sha.update(
                    str(index).encode('utf-8')
                    + str(timestamp).encode('utf-8')
                    + str(block_data).encode('utf-8')
                    + str(previous_hash).encode('utf-8')
                    + str(number_of_zeros).encode('utf-8')
                    + str(nonce).encode('utf-8')
                )
                calculated_hash = sha.hexdigest()
                '''
                if index == 0:
                    num_of_indexes_at_0 += 1
                else:
                    if block_hash != calculated_hash:
                       # print(block_hash,"    ",calculated_hash)
                        msg = 'Invalid Chain. Message has been changed'
                        raise ValueError(msg)
                    if not _hash == previous_hash:
                        msg = 'Incorrect hashes. Broken chain.'
                        raise ValueError(msg)

                _hash = block_to_validate['hash']
                _hash_to_validate = self._return_hash(previous_hash, nonce)
                self._validate_hash(_hash_to_validate, number_of_zeros)

        if num_of_indexes_at_0 > 1:
            msg = 'Multiple genesis blocks.'
            raise ValueError(msg)

        return True



if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 3000)
    print(text)
    b = Blockchain()
    b.add_data_to_block(text)
    b.create_new_block()
    print(b.validate_chain())

    
