
import os
import sys
import random
import time
import ultra96_eval_client
import socket
import threading
import multiprocessing
import base64
import numpy as np
from tkinter import Label, Tk
import pandas as pd
from Crypto.Cipher import AES
import zmq
import zmq
from zmq.devices.basedevice import ProcessDevice
from zmq.devices.monitoredqueuedevice import MonitoredQueue
from zmq.utils.strtypes import asbytes
monitor_port = 5512


def monitor():
    print ("Starting monitoring process")
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    print ("Collecting updates from server...")
    socket.connect ("tcp://127.0.0.1:%s" % monitor_port)
    socket.setsockopt(zmq.SUBSCRIBE, "".encode("utf-8"))
    while True:
        try:
            print("waiting")
            string = socket.recv_multipart()
            #string1 = string.decode("utf8")
            print ("\nMonitoring Client: %s" % string)
        except Exception as e:
            print(e)
def main():
    monitorclient_p = multiprocessing.Process(target=monitor)
    monitorclient_p.start()  
    
if __name__ == '__main__':
    main()
