import os
import sys
import random
import time

from socketclient import Client
import socket
import threading

import base64
import numpy as np
from tkinter import Label, Tk
import pandas as pd
from Crypto.Cipher import AES
from Crypto import Random

BLOCK_SIZE = 16
POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']
TARGET_IP = "localhost" #To be changed to evaluation server's IP address
TARGET_PORT = 8088 #To be changed to evaluation server's port
pad = lambda s:  ((BLOCK_SIZE - len(s) % BLOCK_SIZE) -1 ) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE) + "#" +  s

PASSWORD = "aaaaaaaaaaaaaaaa"



class EvalClient(Client):
    def __init__(self, targetIp, targetPort):
        super().__init__(targetIp, targetPort)

        
    def encrypt(self, raw):
        secret_key = bytes(str(PASSWORD), encoding="utf8") 

        raw = pad(raw).encode("utf-8")
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        #print(iv)
        return base64.b64encode(iv + cipher.encrypt(raw))
    

    
    def sendEncryptedMsg(self, plaintext):
        #print("plaintext is " + plaintext)
        ciphertext = self.encrypt(plaintext)
        #self.socket.send(ciphertext)
        self.connection.send(ciphertext)
        
    def sendLogoutMsg(self):
        plaintextLogoutMsg = "|logout|"
        #ciphertextLogoutMsg = self.encrypt(plaintextLogoutMsg)
        self.sendEncryptedMsg(plaintextLogoutMsg)
        self.stop()
        

def main():
    my_server = EvalClient(TARGET_IP, TARGET_PORT)
    my_server.start()



if __name__ == '__main__':
    main()