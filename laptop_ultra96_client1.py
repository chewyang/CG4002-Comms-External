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
import zmq
from zmq.devices.basedevice import ProcessDevice
from zmq.devices.monitoredqueuedevice import MonitoredQueue
from zmq.utils.strtypes import asbytes

#------------------------------------
frontend_port = 5519
backend_port = 5510
monitor_port = 5512
number_of_workers = 2
#------------------------------------
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



class Ultra96Client(threading.Thread):
    def __init__(self, frontendPort, clientId):
        super(Ultra96Client, self).__init__()
        self.frontendPort = frontendPort
        self.clientId = clientId
        self.requestNum = 1
        self.shutDown = threading.Event()

        self.estConnection()

        self.p2 = threading.Thread(target=self.sendMsgSyncLogout)
        self.p2.setDaemon(True)
        self.p2.start()


        #self.estSSHtunnel()


    def estConnection(self):
        context = zmq.Context()
        self.connection = context.socket(zmq.REQ)
        self.connection.connect("tcp://127.0.0.1:%s" % self.frontendPort)

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
    
    def stop(self):
        self.connection.close()
        self.shutDown.set()
        self.p2

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
            self.sendMsg(self.rawBleData.sendRawBleData())
            #print("waiting for reply")
            msgReceived = self.recvMsg()
            #print("host sent:" + msgReceived)

            time.sleep(2)
            

def main():
    my_server = Ultra96Client(frontend_port, 1)
    my_server.start()
    



if __name__ == '__main__':
    main()