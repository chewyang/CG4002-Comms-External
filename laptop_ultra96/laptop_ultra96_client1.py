import sys
sys.path.append('..')
import time
from randomvalues.random_eval_string_gen import StringGen
from dancedanceobjects.objects import RequestMessagePacket, syncMessagePacket
from ssh.ssh_tunneling import TunnelNetwork
import threading
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
            self.context = zmq.Context()
            self.connection  = self.context.socket(zmq.REQ)
            self.connection.connect("tcp://localhost:"+str(self.port_num))

            
        except Exception as e:
            print(e)
            
        
    def sendMsg(self, data):
        self.connection.send_pyobj(data)
        self.requestNum = self.requestNum +1

    def recvMsg(self):
        message = self.connection.recv_pyobj()
        if isinstance(message, syncMessagePacket):
            message.blunoRecvTime = self.getCurrentMilliTime()
            print(message.printSyncString())
            print(message.getClockOffset())

        return message
            

    def estSSHtunnel(self):
        self.tunnel = TunnelNetwork(tunnel_i, TARGET_ADDRESS, TARGET_PORT)
        try:
        
            self.tunnel.start_tunnels()
            print("Tunnel created")
            return self.tunnel.get_local_connect_port()
        except Exception as e:
            print("Failed to create SSH tunnel")

    def sendMsgSyncLogout(self):
        
        while not self.shutDown.is_set():
            msg = input()
            if "logout" in msg:
                self.sendMsg("logout")
                print("Logout request sent!")
                self.stop()

            elif "sync" in msg:
                syncMsg = syncMessagePacket(self.getCurrentMilliTime())
                self.sendMsg(syncMsg)
                self.recvMsg()
    

    def run(self):
        while not self.shutDown.is_set():
            self.rawBleData = StringGen()
            msg = RequestMessagePacket(self.clientId, self.requestNum, self.rawBleData.sendRawBleData())
            print(msg.printReqString())
            try:
                self.sendMsg(msg)
                print("sent")
            except Exception as e:
                print(e)
            msgReceived = self.recvMsg()
            time.sleep(3)

    
    def stop(self):
        self.shutDown.set()
        self.connection.close()
        self.context.destroy()
        self.tunnel.stop_tunnels()
        
        self.p2
        
    def getCurrentMilliTime(self):
        return round(time.time() * 1000)


def main():
    my_server = Ultra96Client(1)
    my_server.start()
    



if __name__ == '__main__':
    main()