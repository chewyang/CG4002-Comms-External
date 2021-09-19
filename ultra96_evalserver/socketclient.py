import socket 
import threading
import time


class Client(threading.Thread):
    def __init__(self, targetIp, targetPort):
        super().__init__()
        self.shutDown = threading.Event()
        self.targetIp = targetIp
        self.targetPort = targetPort
        self.estSocketComms()


    def estSocketComms(self):
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self.targetIp, self.targetPort))
            print("connected!")
            time.sleep(5)
            self.sendMsg("hello")
            print("sent")
        except Exception as e:
            print("Connection error")
            print(e)

    def stop(self):
        self.connection.close()
        self.shutDown.set()
        print("Bye")



    def sendMsg(self, msg):
        self.connection.send(msg.encode("utf-8"))

    def receiveMsg(self):
        while not self.shutDown.is_set():
            data = self.connection.recv(1024)
            if data:
                try:
                    msg = data.decode("utf8")
                    print("Data received is: " + msg)
                    
                except Exception as e:
                    print("Error in receiving messages")
                    print(e)
            else:
                print('no more data')
                self.stop()
    
    def sendLogoutMsg(self):
        
        while not self.shutDown.is_set():
            logoutMsg = input()
            if "logout" in logoutMsg:
                self.shutDown.set()
                self.sendMsg(logoutMsg)
                print("Logout request sent!")
                

