import os
import sys
import random
import time
import ultra96_eval_client
import random_eval_string_gen
import threading
import multiprocessing
import base64
import numpy as np
from tkinter import Label, Tk
import pandas as pd
from Crypto.Cipher import AES
import zmq

from zmq.devices.basedevice import ProcessDevice
from zmq.devices.monitoredqueuedevice import MonitoredQueue
from zmq.utils.strtypes import asbytes

#------------------------------------
frontend_port = 15016
backend_port = 15017
monitor_port = 15018
number_of_workers = 2
#------------------------------------
THREADS = []
MESSAGE_SIZE = 3
ULTRA96_IP = "137.132.86.227"
class Server(threading.Thread):
    def __init__(self, backendPort):
        super(Server, self).__init__()


        self.backendPort = backendPort
        self.has_no_response = False
        self.connection = None
        self.logout = False
        self.replyNum = 1
        self.estConnection()


        # Create a TCP/IP socket and bind to port
        self.shutdown = threading.Event()


        serverContext = zmq.Context()

        print("Listening...")

    def estConnection(self):
        context = zmq.Context()
        self.connection = context.socket(zmq.REP)

        self.connection.connect("tcp://137.132.86.227:%s" % backend_port)
        #print("niggs")
        #message = self.connection.recv()
        #print(message)
        #self.connection.send(b'world')

    def sendMsg(self, msg):
        self.connection.send(msg.encode("utf-8"))

    def recvMsg(self):
        msg = self.connection.recv().decode("utf-8")
        return msg


    def run(self):
        print("waiting for msg")
        while not self.shutdown.is_set():

            data = self.recvMsg()
            if data:
                split_msg = data.split(",")
                len_of_split = len(split_msg)
                print("length is "+ str(len_of_split))
                try:
                    if(len_of_split == 3): #sync or logout messages received

                        if "sync" in data:
                            receivedSyncTime = self.current_milli_time()
                            print("og timestamp: " + split_msg[2])
                            self.sendMsg(split_msg[2] + ',' + receivedSyncTime + "," + self.current_milli_time())
                    if(len_of_split == 2):
                        if "logout" in data:
                            THREADS[0].sendLogoutMsg()
                            self.shutdown.set()

                    if(len_of_split ==8): #sensor data received


                            requestNum = data[data.find("#")+1 : data.find(",")]
                            clientNum = data[data.find("#", data.find("#")+1)+1 : data.find(":")]
                            #print("found" + requestNum)

                            THREADS[0].sendEncryptedMsg(random_eval_string_gen.StringGen().sendEvalString()) #eval_client to send
                            #print(data)

                            self.sendMsg("Ultra received request #" + str(requestNum) +" from client# " + str(clientNum))



                except Exception as e:
                    print("error bitch")
                    print(e)
            else:
                print('no more data from', self.client_address)
                self.stop()

        self.stop()

    #def extractInfo(self):


    def stop(self):
        self.connection.close()
        self.shutdown.set()
        THREADS[0].stop()
        print("bye")

    def current_milli_time(self):
        return str(round(time.time() * 1000))

    """def convertTuple(self,tup):
        strings = ''.join(str(tup))
        return strings"""



def monitordevice():
    in_prefix=asbytes('in')
    out_prefix=asbytes('out')
    monitoringdevice = MonitoredQueue(zmq.XREP, zmq.XREQ, zmq.PUB, in_prefix, out_prefix)

    monitoringdevice.bind_in("tcp://"+ULTRA96_IP+":%d" % frontend_port)
    monitoringdevice.bind_out("tcp://"+ULTRA96_IP+":%d" % backend_port)
    monitoringdevice.bind_mon("tcp://"+ULTRA96_IP+":%d" % monitor_port)

    monitoringdevice.setsockopt_in(zmq.RCVHWM, 1)
    monitoringdevice.setsockopt_out(zmq.SNDHWM, 1)
    monitoringdevice.start()
    print( "Program: Monitoring device has started")

def monitor():
    table = []
    print ("Starting monitoring process")
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    print ("Collecting updates from server...")
    socket.connect ("tcp://"+ULTRA96_IP+":%s" % monitor_port)
    socket.setsockopt(zmq.SUBSCRIBE, "".encode("utf-8"))
    print("Monitoring client:")
    while True:
        #requ
        string = socket.recv_multipart()
        inOrOut = (string[0].decode("utf-8")).strip("'")
        print(inOrOut)
        msgBody = (string[3].decode("utf-8")).strip("'")
        print("Monitoring client: " + inOrOut + ": " + msgBody)
        #string1 = string.decode("utf8")
        #print ("\nMonitoring Client: %s" % string)
        #if inOrOut == "in":
        #    table[0] =



def main():


    ip_addr = "127.0.0.1"
    port_num = 8082
    group_id = "4"

    ultra96_eval = ultra96_eval_client.EvalClient("localhost", 8088)
    monitoring_p = multiprocessing.Process(target=monitordevice)
    monitoring_p.start()

    my_server = Server(backend_port)

    THREADS.append(ultra96_eval)
    THREADS.append(my_server)

    ultra96_eval.start()
    my_server.start()
    monitorclient_p = multiprocessing.Process(target=monitor)
    monitorclient_p.start()
    #my_server2 = Server(ip_addr, 8083, group_id)
    #my_server2.start()



if __name__ == '__main__':
    main()