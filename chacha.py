import os
import math
import sys
import hashlib
from chacha20poly1305 import ChaCha20Poly1305



def conint(byte:bytes):
    s1 = byte.decode()
    s2 = int(s1)
    return s2
def conbyte(ints:int):
    s1 = str(ints)
    b1 = s1.encode()
    return b1

def md5(byte:bytes):
    
    dig = hashlib.md5()
    dig.update(byte)
    return dig.digest()
        

def w_files(filepath:str,data:bytes):

    with open(filepath,'wb') as wf:
        wf.write(data)
        wf.close()

def read_files(filepath):
    with open(filepath,'rb') as fp:
        content=fp.read()
    return content

def encrypt_chacha(infile:str,chacha_key_file:str,outfile:str):
    
    key1 = open(chacha_key_file,'rb')
    key = key1.read(32)
    nonce = key1.read(12)
    key1.close()
    cip = ChaCha20Poly1305(key)
    head = b'\x45\x6e\x63\x56'
    enc = cip.encrypt(nonce, read_files(infile))
    md5dat = md5(enc)
    w_files(outfile,head+md5dat+enc)
def decrypt_chacha(infile:str,chacha_key_file:str,outfile:str):
    key1 = open(chacha_key_file,'rb')
    
    key = key1.read(32)
    nonce = key1.read(12)
    with open(infile,'rb') as fp:
        head = fp.read(4)
        md5out = fp.read(16)
        data = fp.read()
    if not (head == b'\x45\x6e\x63\x56') or not (md5out == md5(data)):
        print('Error: File corrupted.')
        sys.exit(1)
    
    cip = ChaCha20Poly1305(key)
    w_files (outfile,cip.decrypt(nonce, data)) 
