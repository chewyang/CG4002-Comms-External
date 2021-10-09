import sys
sys.path.append('..')

import time
from randomvalues.random_eval_string_gen import StringGen
from dancedanceobjects.objects import RequestMessagePacket, syncMessagePacket
from ssh.ssh_tunneling import TunnelNetwork
import threading
import zmq
from pymongotest import DashboardServer


# from plswork import main as BLEMain

NUM_WORKERS = 2
#TARGET_ADDRESS = "137.132.86.227"  # Target of 1st Ultra96
TARGET_ADDRESS = "137.132.86.231" # Target of 2nd ultra96
TARGET_PORT = 15016  # Target port of the Ultra96 to connect to

# Credentials for first jump to sunfire servers
#PKEY_FILE = '/home/owenchew/.ssh/id_rsa'
FIRST_JUMP_SSH_ADDRESS = "sunfire.comp.nus.edu.sg"
FIRST_JUMP_USERNAME = "e0406642"
FIRST_JUMP_PASSWORD = "Mrbombustic5488"

# Credentials for second jump to Ultra96
SECOND_JUMP_ADDRESS = TARGET_ADDRESS
SECOND_JUMP_USERNAME = "xilinx"
SECOND_JUMP_PASSWORD = "xilinx"

TUNNEL_INFO = [
    {"ssh_address_or_host": FIRST_JUMP_SSH_ADDRESS,
     "ssh_username": FIRST_JUMP_USERNAME,
     #"ssh_pkey": PKEY_FILE,
     "ssh_password": FIRST_JUMP_PASSWORD
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
    def __init__(self, clientId):
        super(Ultra96Client, self).__init__()
        self.dashboardServer = DashboardServer()
        self.sshTunnel = self.estSSHtunnel()
        self.port_num = self.sshTunnel.get_local_connect_port()  #15016

        self.context, self.connection = self.estConnection()

        self.clientId = clientId
        self.blunoEmulator = StringGen(self.clientId)
        self.shutDown = threading.Event()
        self.requestNum = 1
        self.sensorQueue = []
        self.requestQueue = []

        # Daemonise this thread so that it can run in the background to detect for sync and logout messages that are inputted manually.
        self.p2 = threading.Thread(target=self.sendMsgSyncLogout)
        self.p2.setDaemon(True)
        self.p2.start()

        self.p3 = threading.Thread(target=self.updateDBThread)
        self.p3.setDaemon(True)
        self.p3.start()

        self.p4 = threading.Thread(target=self.popQueueToUltra96)
        self.p4.setDaemon(True)
        self.p4.start()

    """
    Establishes the REP-REQ socket connections to the Ultra96.
    """

    def estConnection(self):
        try:
            context = zmq.Context()
            connection = context.socket(zmq.REQ)
            connection.connect("tcp://127.0.0.1:" + str(self.port_num))
            return context, connection

        except Exception as e:
            print(e)

    """
    Establishes the SSH tunnel to the target IP and target port of the Ultra96
    """

    def estSSHtunnel(self):
        tunnel = TunnelNetwork(TUNNEL_INFO, TARGET_ADDRESS, TARGET_PORT)
        try:
            print("trying")
            tunnel.start_tunnels()
            localPort = tunnel.get_local_connect_port()  # This is the random port that the local socket should connect to
            print("Tunnel to Ultra96 at %s:%s created at local port %s" % (TARGET_ADDRESS, TARGET_PORT, localPort))
            return tunnel
        except Exception as e:
            print("Failed to create SSH tunnel")

    """
    Takes in a python object and sends it over to the Ultra96.
    """

    def sendMsg(self, data):
        self.connection.send_pyobj(data)
        self.requestNum = self.requestNum + 1

    """
    Receives a python object from the Ultra96.
    """

    def recvMsg(self):
        message = self.connection.recv_pyobj()

        # If the object received is a syncMessagePacket, add in the time when it receives the reply.
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
                self.requestQueue.append(syncMsg)
                #self.sendMsg(syncMsg)
                #self.recvMsg()

            elif "send" in msg:
                msg = RequestMessagePacket(self.clientId, self.requestNum, self.blunoEmulator.sendRawBleData())
                self.sensorQueue.append(msg)
                # self.dashboardServer.printCollection()
                self.sendMsg(msg)
                self.recvMsg()

    """
    This method extracts the information that is needed in the mongoDB and
    enqueues it to a queue, ready for sending over to the database.
    """
    def prepareDbData(self, sensorData):
        gyroData = {
            "dancerId": self.clientId,
            "gyroX": sensorData["gyroX"],
            "gyroY": sensorData["gyroY"],
            "gyroZ": sensorData["gyroZ"],
            "time": time.ctime(time.time())
        }
        self.sensorQueue.append(gyroData)
        return gyroData

    """
    Prepares the data for mongoDB and sends the sensor data to the ultra96.
    """
    def sendSensorData(self, msg):
        self.prepareDbData(msg)
        reqmsgPacket = RequestMessagePacket(self.clientId, self.requestNum, msg)
        # self.dashboardServer.printCollection()
        self.requestQueue.append(reqmsgPacket)
        #self.sendMsg(reqmsgPacket)
        #self.recvMsg()

    """
    This thread pops the queue and inserts the raw sensor data into the MongoDB server
    The purpose of this is to speed up the process of sending the sensor data over to the ultra96
    """
    def updateDBThread(self):
        while not self.shutDown.is_set():
            if len(self.sensorQueue) > 0:
                sensorData = self.sensorQueue.pop(0)
                self.dashboardServer.insertSensorValues(sensorData)

    """
       This thread pops the queue and sends the requests to the ultra96 server
       The purpose of this is to avoid collisions between each message being sent.
       """
    def popQueueToUltra96(self):
        while not self.shutDown.is_set():
            if len(self.requestQueue) > 0:
                msg = self.requestQueue.pop(0)
                self.sendMsg(msg)
                self.recvMsg()
    """
    Main thread that repeatedly generates the fake BLE sensor data and sends over to the Ultra96.
    """
    def run(self):
        while not self.shutDown.is_set():
            # self.recvMsg()
            # self.rawBleData = StringGen(self.clientId)
            # sensor = self.blunoEmulator.sendRawBleData()
            # msg = RequestMessagePacket(self.clientId, self.requestNum, sensor)
            if self.shutDown.is_set():
                pass
            else:
                try:
                    # self.sendMsg(msg)
                    # self.sensorQueue.append(msg)
                    # self.dashboardServer.insertSensorValues(self.blunoEmulator.sendRawBleData())

                    # msgReceived = self.recvMsg()
                    pass
                except Exception as e:
                    print(e)

            # time.sleep(3)

    """
    Stops the program.
    """

    def stop(self):
        self.shutDown.set()
        self.connection.close()
        self.context.destroy()
        # self.sshTunnel.stop_tunnels()

    def getCurrentMilliTime(self):
        return round(time.time() * 1000)


def main():
    # localPort = 15016
    # for client_id in range(NUM_WORKERS):
    Ultra96Client(clientId=0).start()


if __name__ == '__main__':
    main()
