import multiprocessing
import os
import sys
import random
import time

import socket
import threading
from ssh_tunneling import TunnelNetwork

import base64
#import numpy as np
from tkinter import Label, Tk
#import pandas as pd
#from Crypto.Cipher import AES
#from Crypto import Random

LOCAL_ADDRESS = "localhost"
TARGET_ADDRESS = "137.132.86.227"
TARGET_PORT = 15006

PKEY_FILE = '/home/owenchew/.ssh/id_rsa'
FIRST_JUMP_SSH_ADDRESS = "sunfire.comp.nus.edu.sg"
FIRST_JUMP_USERNAME = "e0406642"

SECOND_JUMP_ADDRESS ="137.132.86.227"
SECOND_JUMP_USERNAME = "xilinx"
SECOND_JUMP_PASSWORD = "xnilix_toor"

tunnel_i = [
        
        {"ssh_address_or_host": FIRST_JUMP_SSH_ADDRESS,
        "ssh_username": FIRST_JUMP_USERNAME,
        "ssh_pkey": PKEY_FILE,
        },
        {"ssh_address_or_host": SECOND_JUMP_ADDRESS,
        "ssh_username": SECOND_JUMP_USERNAME,
        "ssh_password": SECOND_JUMP_PASSWORD,
        }
    ]



class Server(threading.Thread):
    def __init__(self):
        super(Server, self).__init__()
        

        self.shutdown = threading.Event()
        self.connection = None
        self.logout = False
        self.ipaddr = LOCAL_ADDRESS
        self.port_num = 8082 #self.estSSHtunnel()
        print(self.port_num)
        self.estSocketComms()
        time.sleep(5)

    def estSocketComms(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:#socket.gethostbyname(socket.gethostname())
            addr = ("localhost", self.port_num)
            self.socket.connect(addr)
            print("connected!")
            p = multiprocessing.Process(target=self.receive_msg)
            p.start()

        except Exception as e:
            print(e)
            
        
    def receive_msg(self):
        while not self.shutdown.is_set():
            data = self.socket.recv(1024)
            if data:
                try:
                    msg = data.decode("utf8")
                    print("Host sent " + msg)
                except Exception as e:
                    print("error bitch")
                    print(e)
            else:
                print('no more data')
                self.stop()
            

    def estSSHtunnel(self):
        tunnel = TunnelNetwork(tunnel_i, TARGET_ADDRESS, TARGET_PORT)
        try:
        
            tunnel.start_tunnels()
            print("Tunnel created")
            return tunnel.get_local_connect_port()
        except Exception as e:
            print("Failed to create SSH tunnel")

        
    
    def run(self):
        while not self.shutdown.is_set():

            plaintext = input("Enter text to be sent: ")
            if "logout" in plaintext:
                self.logout = True

            self.socket.send(plaintext.encode("utf-8"))
            print("sent!")
            
            if self.logout:
                self.stop()
    
    def stop(self):
        self.socket.close()
        self.shutdown.set()
        

def main():
    my_server = Server()
    my_server.start()
    



if __name__ == '__main__':
    main()