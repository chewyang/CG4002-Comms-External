import os
import sys
import random
import time

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
ip_address = "localhost"
port_number = 8088
pad = lambda s:  ((BLOCK_SIZE - len(s) % BLOCK_SIZE) -1 ) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE) + "#" +  s

password = "aaaaaaaaaaaaaaaa"



class Server(threading.Thread):
    def __init__(self, ipaddr, port_num):
        super(Server, self).__init__()

        self.shutdown = threading.Event()
        self.connection = None
        self.logout = False
        self.ipaddr = ipaddr
        self.port_num = port_num
        self.estSocketComms()

    def estSocketComms(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connection = self.socket.connect((self.ipaddr, self.port_num))
        except Exception as e:
            print("Connection error. IP address and/or port number is incorrect")
            self.ipaddr = input("Enter IP address: ")
            self.port_num = input("Enter port number")
            
        
        
        
        
        

    def encrypt(self, raw, password):
        secret_key = bytes(str(password), encoding="utf8") 

        raw = pad(raw).encode("utf-8")
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        print(iv)
        return base64.b64encode(iv + cipher.encrypt(raw))
    
    def run(self):
        while not self.shutdown.is_set():
            """data = self.socket.recv(1024)
            print(data)"""
            plaintext = input("Enter text to be encrypted: ")
            if "logout" in plaintext:
                plaintext = "|logout|"
                self.logout = True

            ciphertext = self.encrypt(plaintext, password)
            self.socket.send(ciphertext)
            
            if self.logout:
                self.stop()
    
    def stop(self):
        self.connection.close()
        self.shutdown.set()
        
     

def main():
    my_server = Server(ip_address, port_number)
    my_server.start()



if __name__ == '__main__':
    main()