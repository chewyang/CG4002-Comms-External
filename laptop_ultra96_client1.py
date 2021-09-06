import multiprocessing
import os
import sys
import random
import time
import random_eval_string_gen
import socket
import threading
from ssh_tunneling import TunnelNetwork
from socketclient import Client

import base64
#import numpy as np
from tkinter import Label, Tk
#import pandas as pd
#from Crypto.Cipher import AES
#from Crypto import Random

LOCAL_ADDRESS = "localhost"
LOCAL_PORT = 8082

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



class Ultra96Client(Client):
    def __init__(self, targetIP, targetPort):
        super().__init__(targetIP, targetPort)
        
        p1 = multiprocessing.Process(target=self.receiveMsg)
        p2 = threading.Thread(target=self.sendLogoutMsg)

        p1.start()
        p2.start()


        #self.estSSHtunnel()

    def estSSHtunnel(self):
        tunnel = TunnelNetwork(tunnel_i, TARGET_ADDRESS, TARGET_PORT)
        try:
        
            tunnel.start_tunnels()
            print("Tunnel created")
            return tunnel.get_local_connect_port()
        except Exception as e:
            print("Failed to create SSH tunnel")

        
    
    def run(self):
        while not self.shutDown.is_set():
            
            self.eval_string_from_bluno_processed = random_eval_string_gen.StringGen(random.random())
            self.sendMsg(self.eval_string_from_bluno_processed.sendEvalString())
            time.sleep(5)
            

def main():
    my_server = Ultra96Client(LOCAL_ADDRESS, LOCAL_PORT)
    my_server.start()
    



if __name__ == '__main__':
    main()