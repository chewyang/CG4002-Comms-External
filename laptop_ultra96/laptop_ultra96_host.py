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
from dancedanceobjects.objects import ReplyMessagePacket, RequestMessagePacket, syncMessagePacket
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
        self.replyNum = 1
        self.estConnection()
        # Create a TCP/IP socket and bind to port
        self.shutdown = threading.Event()
        print("Listening...")

    def estConnection(self):
        self.context = zmq.Context()
        self.connection = self.context.socket(zmq.REP)
        self.connection.connect("tcp://137.132.86.227:%s" % backend_port)

    def sendMsg(self, data):
        repMsg = object()

        if isinstance(data, RequestMessagePacket):
            repMsg = ReplyMessagePacket(data.clientId, data.msgCount)
            print(data.printReqString())
            print(repMsg.printReqString())
            THREADS[0].sendEncryptedMsg(random_eval_string_gen.StringGen().sendEvalString())

        elif isinstance(data, syncMessagePacket):
            data.ultra96RecvTime = self.current_milli_time()
            data.ultra96SentTime = self.current_milli_time()
            repMsg = data


        elif isinstance(data, str):
            if "logout" in data:
                self.shutdown.set()
                THREADS[0].sendLogoutMsg()

        self.connection.send_pyobj(repMsg)

    def recvMsg(self):
        msg = self.connection.recv_pyobj()
        return msg


    def run(self):
        print("waiting for msg")
        while not self.shutdown.is_set():

            data = self.recvMsg()
            if data:
                try:
                    self.sendMsg(data)

                except Exception as e:
                    print("error bitch")
                    print(e)
            else:
                print('no more data from', self.client_address)
                self.stop()

        self.stop()



    def stop(self):
        self.shutdown.set()
        self.connection.close()
        self.context.destroy()
        THREADS[0].stop()
        print("bye")

    def current_milli_time(self):
        return round(time.time() * 1000)




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
        #print(string)
        #inOrOut = (string[0].decode("utf-8")).strip("'")
        #print(inOrOut)
        #msgBody = (string[3].decode("utf-8")).strip("'")
        #print("Monitoring client: " + inOrOut + ": " + msgBody)
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



if __name__ == '__main__':
    main()
