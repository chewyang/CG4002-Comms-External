import sys
sys.path.append('..')
import time
from randomvalues.random_eval_string_gen import StringGen
from dancedanceobjects.objects import RequestMessagePacket, syncMessagePacket
from ssh.ssh_tunneling import TunnelNetwork
import threading
import zmq

NUM_WORKERS = 3
TARGET_ADDRESS = "137.132.86.227" #Target of Ultra96
TARGET_PORT = 15016 #Target port of the Ultra96 to connect to

#Credentials for first jump to sunfire servers
PKEY_FILE = '/home/owenchew/.ssh/id_rsa'
FIRST_JUMP_SSH_ADDRESS = "sunfire.comp.nus.edu.sg"
FIRST_JUMP_USERNAME = "e0406642"

#Credentials for second jump to Ultra96
SECOND_JUMP_ADDRESS ="137.132.86.227"
SECOND_JUMP_USERNAME = "xilinx"
SECOND_JUMP_PASSWORD = "xnilix_toor"

TUNNEL_INFO = [
        {"ssh_address_or_host": FIRST_JUMP_SSH_ADDRESS,
        "ssh_username": FIRST_JUMP_USERNAME,
        "ssh_pkey": PKEY_FILE,
        },
        {"ssh_address_or_host": SECOND_JUMP_ADDRESS,
        "ssh_username": SECOND_JUMP_USERNAME,
        "ssh_password": SECOND_JUMP_PASSWORD,
        }
    ]

"""
This is the client script that connects to the Ultra96.
"""
class Ultra96Client(threading.Thread):
    def __init__(self, localPort, clientId):
        super(Ultra96Client, self).__init__()
        
        self.clientId = clientId
        self.blunoEmulator = StringGen(self.clientId)

        self.shutDown = threading.Event()
        self.connection = None
        self.requestNum = 1
        self.port_num = localPort
        #print(self.port_num)
        self.estConnection()

        #Daemonise this thread so that it can run in the background to detect for sync and logout messages that are inputted manually.
        self.p2 = threading.Thread(target=self.sendMsgSyncLogout)
        self.p2.setDaemon(True)
        self.p2.start()
    
    """
    Establishes the REP-REQ socket connections to the Ultra96.
    """
    def estConnection(self):
        try:
            self.context = zmq.Context()
            self.connection  = self.context.socket(zmq.REQ)
            self.connection.connect("tcp://localhost:"+str(self.port_num))
            
        except Exception as e:
            print(e)
            
    """
    Takes in a python object and sends it over to the Ultra96.
    """
    def sendMsg(self, data):
        self.connection.send_pyobj(data)
        self.requestNum = self.requestNum +1

    """
    Receives a python object from the Ultra96.
    """
    def recvMsg(self):
        message = self.connection.recv_pyobj()

        #If the object received is a syncMessagePacket, add in the time when it receives the reply.
        if isinstance(message, syncMessagePacket):
            message.blunoRecvTime = self.getCurrentMilliTime()
            print(message.printSyncString())
            print(message.getClockOffset())
        return message
            
   


    """
    This is the thread that detects for a 'sync' or 'logout' input by the user and sends to the Ultra96.
    """
    def sendMsgSyncLogout(self):
        while not self.shutDown.is_set():
            msg = input()
            if "logout" in msg:
                self.sendMsg("logout")
                print("Logout request sent!")
                self.shutDown.set()

            elif "sync" in msg:
                syncMsg = syncMessagePacket(self.getCurrentMilliTime())
                self.sendMsg(syncMsg)
                self.recvMsg()
    
    """
    Main thread that repeatedly generates the fake BLE sensor data and sends over to the Ultra96.
    """
    def run(self):
        while not self.shutDown.is_set():
            #self.rawBleData = StringGen(self.clientId)
            msg = RequestMessagePacket(self.clientId, self.requestNum, self.blunoEmulator.sendRawBleData())
            if self.shutDown.is_set():
                pass
            else:
                try:
                    self.sendMsg(msg)
                    msgReceived = self.recvMsg()

                except Exception as e:
                    print(e)
            
            #time.sleep(3)

    """
    Stops the program.
    """
    def stop(self):
        self.shutDown.set()
        self.connection.close()
        self.context.destroy()
        #self.tunnel.stop_tunnels()
        
        self.p2
        
    def getCurrentMilliTime(self):
        return round(time.time() * 1000)


"""
Establishes the SSH tunnel to the target IP and target port of the Ultra96
"""
def estSSHtunnel():
    tunnel = TunnelNetwork(TUNNEL_INFO, TARGET_ADDRESS, TARGET_PORT)
    try:
    
        tunnel.start_tunnels()
        localPort = tunnel.get_local_connect_port() #This is the random port that the local socket should connect to
        print("Tunnel to Ultra96 at %s:%s created at local port %s" % (TARGET_ADDRESS, TARGET_PORT, localPort))
        return tunnel 
    except Exception as e:
        print("Failed to create SSH tunnel")

def main():

    sshTunnel = estSSHtunnel()
    localPort = sshTunnel.get_local_connect_port()
    for client_id in range(NUM_WORKERS):
        Ultra96Client(clientId= client_id, localPort= localPort).start()
    
    



if __name__ == '__main__':
    main()