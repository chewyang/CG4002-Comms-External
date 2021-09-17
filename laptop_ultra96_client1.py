import multiprocessing
import os
import sys
import random
import time
import random_eval_string_gen

import socket
import threading
from ssh_tunneling import TunnelNetwork

import base64
#import numpy as np
from tkinter import Label, Tk
#import pandas as pd
#from Crypto.Cipher import AES
#from Crypto import Random
import zmq
LOCAL_ADDRESS = "localhost"
TARGET_ADDRESS = "137.132.86.227"
TARGET_PORT = 15016

PKEY_FILE = '/home/owenchew/.ssh/id_rsa'
FIRST_JUMP_SSH_ADDRESS = "sunfire.comp.nus.edu.sg"
FIRST_JUMP_USERNAME = "e0406642"
FIRST_JUMP_PASSWORD = "Mrbombustic5488"


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



class Ultra96Client(threading.Thread):
    def __init__(self, clientId):
        super(Ultra96Client, self).__init__()
        
        self.clientId = clientId
        self.shutDown = threading.Event()
        self.connection = None
        self.requestNum = 1
        self.port_num = self.estSSHtunnel()
        print(self.port_num)
        self.estConnection()
        #time.sleep(5)
        self.p2 = threading.Thread(target=self.sendMsgSyncLogout)
        self.p2.setDaemon(True)
        self.p2.start()

        
    def estConnection(self):
        
        try:
            context = zmq.Context()

            #  Socket to talk to server
            print("Connecting to hello world server…")
            self.connection  = context.socket(zmq.REQ)
            self.connection.connect("tcp://localhost:"+str(self.port_num))

            
        except Exception as e:
            print(e)
            
        
    def sendMsg(self, msg):
        self.connection.send (("Request#%s, from client#%s: %s" % (str(self.requestNum), str(self.clientId), msg)).encode("utf-8"))
        self.requestNum = self.requestNum +1

    def recvMsg(self):
        message = self.connection.recv()
        return message.decode("utf8")
            

    def estSSHtunnel(self):
        tunnel = TunnelNetwork(tunnel_i, TARGET_ADDRESS, TARGET_PORT)
        try:
        
            tunnel.start_tunnels()
            print("Tunnel created")
            return tunnel.get_local_connect_port()
        except Exception as e:
            print("Failed to create SSH tunnel")

    def sendMsgSyncLogout(self):
        
        while not self.shutDown.is_set():
            msg = input()
            if "logout" in msg:
                self.shutDown.set()
                self.sendMsg("logout")
                print("Logout request sent!")
            elif "sync" in msg:
                self.sendMsg("sync," + str(round(time.time() * 1000)))
                print("Sync message from "+ self.recvMsg())
                #self.stop()
    

    def run(self):
        while not self.shutDown.is_set():
            self.rawBleData = random_eval_string_gen.StringGen()
            #print(self.rawBleData.sendRawBleData())
            try:
                self.sendMsg(self.rawBleData.sendRawBleData())
            except Exception as e:
                print(e)
            msgReceived = self.recvMsg()
            #print(msgReceived)
            time.sleep(3)

    
    def stop(self):
        self.connection.close()
        self.shutDown.set()
        self.p2
        

def main():
    my_server = Ultra96Client(1)
    my_server.start()
    



if __name__ == '__main__':
    main()