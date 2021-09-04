# Changing the actions in self.actions should automatically change the script to function with the new number of moves.
# Developed and improved by past CG3002 TAs and students: Tean Zheng Yang, Jireh Tan, Boyd Anderson,
# Paul Tan, Bernard Tan Ke Xuan, Ashley Ong, Kennard Ng, Xen Santos

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



class Server(multiprocessing.Process):
    def __init__(self, ip_addr, port_num, group_id):
        super(Server, self).__init__()

        

        self.has_no_response = False
        self.connection = None
        self.logout = False
        

        # Create a TCP/IP socket and bind to port
        self.shutdown = multiprocessing.Event()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (ip_addr, port_num)

        print('starting up on %s port %s' % server_address)
        self.socket.bind(server_address)
        print("Listening...")
        # Listen for incoming connections
     
        
        self.socket.listen(2)
        self.client_address = self.setup_connection()

        
    

    def run(self):
        
        print("ass")
        while not self.shutdown.is_set():
            
            data = self.connection.recv(1024)
            if data:
                msg = data.decode("utf8")

                try:
                    if(msg == "sync"):
                        self.send_msg(self.current_milli_time())
                    else:    
                
                        print("message received is " + msg)
                except Exception as e:
                    print("error bitch")
                    print(e)
            else:
                print('no more data from', self.client_address)
                self.stop()

    def send_msg(self, message):
        #msg = self.convertTuple(self.client_address)
        self.connection.send(message.encode("utf-8"))

    def setup_connection(self):

        # Wait for a connection
        print('waiting for a connection')
        self.connection, client_address = self.socket.accept()

        
        return client_address

    def stop(self):
        self.connection.close()
        self.shutdown.set()
        print("biys")


    def current_milli_time(self):
        return str(round(time.time() * 1000))

    """def convertTuple(self,tup):
        strings = ''.join(str(tup))
        return strings"""






def main():


    ip_addr = "localhost"
    port_num = 8082
    group_id = "4"

    ultra96_eval = ultra96_eval_client.Server("localhost", 8088)
    ultra96_eval.start()
    print("evalclient started")
    my_server = Server(ip_addr, port_num, group_id)
    my_server.start()

    #my_server2 = Server(ip_addr, 8083, group_id)
    #my_server2.start()

        

if __name__ == '__main__':
    main()

