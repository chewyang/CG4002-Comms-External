import time
import sys
#sys.path.append('..')
import ultra96_eval_client

#import random_eval_string_gen
import threading
import multiprocessing
import zmq
sys.path.append('..')
from dancedanceobjects.objects import ReplyMessagePacket, RequestMessagePacket, syncMessagePacket
from collections import defaultdict
#from pymongotest import DashboardServer
from pathlib import Path

ML_DATA_PATH_NAME = "/home/xilinx/ml/randomTestCase2.txt"

NUM_WORKERS = 2
FRONTEND_PORT = 15016
BACKEND_PORT = 15017
THREADS = []
#ULTRA96_IP = "137.132.86.227
#ULTRA96_IP = "127.0.0.1"
ULTRA96_IP = "137.132.86.231" #ip address of 2nd ultra96


class Server(threading.Thread):
    def __init__(self, backendPort):
        super(Server, self).__init__()
        #self.dashboardServer = DashboardServer()


        self.startTimes= defaultdict(list)
        self.backendPort = backendPort
        self.connection = None
        self.replyNum = 1
        self.estConnection()
        self.dataCounter = 0
        self.shutdown = threading.Event()
        print("Listening...")


    """
    Establishes the socket connections to the evaluation server.
    """
    def estConnection(self):
        self.context = zmq.Context()
        self.connection = self.context.socket(zmq.REP)
        self.connection.connect("tcp://%s:%s" % (ULTRA96_IP, BACKEND_PORT))


    """
    Sends the respective reply according to the request from laptop.
    """
    def sendMsg(self, data):
        repMsg = object()

        #If the data received is the BLE sensor data, send over the fake predicted results to evalserver and acknowledgement msg to laptop
        if isinstance(data, RequestMessagePacket):
            repMsg = ReplyMessagePacket(data.clientId, data.msgCount)
            self.writeToFile(data.rawBleData)
            #print(data.printReqString())
            print(repMsg.printReqString())
            """danceMoveNumAndStartTime = data.rawBleData["danceMoveNum, startTime"]

            # if it detects a start of a move, append it appropriately to the dictionary.
            if isinstance( danceMoveNumAndStartTime, tuple):
                self.startTimes[str(danceMoveNumAndStartTime[0])].append(danceMoveNumAndStartTime[1])
                print(self.startTimes)
                self.calculateSyncDelay()"""

        #If the data received is a sync, send over the timestamps when it receives and reply. Then send it over back to the laptop
        elif isinstance(data, syncMessagePacket):
            print(data.printSyncString())
            data.ultra96RecvTime = self.ultra96ReceiveTime
            data.ultra96SentTime = self.current_milli_time()
            repMsg = data


        elif isinstance(data, str):
            if "logout" in data:
                self.shutdown.set()
                #THREADS[0].sendLogoutMsg()

        self.connection.send_pyobj(repMsg)



    """
    This method calculates the sync delay between the first and last dancers and sends the
    evaluation string over to the evaluation server. If there is only one dancer, send a sync delay of 0.
    """
    def calculateSyncDelay(self):
        keys = self.startTimes.keys()
        lastKey = list(keys)[-1]
        lastValue = self.startTimes[lastKey]

        #If the number of clients = x and x start times have been obtained, calculate sync delay and send to the evaluation server
        if NUM_WORKERS == 3 and len(lastValue) == 3:
            syncDelay = max(lastValue) - min(lastValue)
            randGen = random_eval_string_gen.StringGen().sendEvalString(syncDelay)
            predict = randGen[1]
            #self.dashboardServer.insertPredictedValues(predict)
            #THREADS[0].sendEncryptedMsg(random_eval_string_gen.StringGen().sendEvalString(syncDelay))

        elif NUM_WORKERS == 2 and len(lastValue) == 2:
            syncDelay = max(lastValue) - min(lastValue)
            print(syncDelay)
            randGen = random_eval_string_gen.StringGen().sendEvalString(syncDelay)
            predict = randGen[1]
            #print(predict)
            #self.dashboardServer.insertPredictedValues(predict)
            #self.dashboardServer.printCollection()
            #THREADS[0].sendEncryptedMsg(random_eval_string_gen.StringGen().sendEvalString(syncDelay))


        elif NUM_WORKERS == 1:
            #THREADS[0].sendEncryptedMsg(random_eval_string_gen.StringGen().sendEvalString(0))
            syncDelay =0
            print(syncDelay)
            randGen = random_eval_string_gen.StringGen().sendEvalString(syncDelay)
            predict = randGen[1]
            #self.dashboardServer.insertPredictedValues(predict)

    def writeToFile(self, data):
        #myFile = Path(ML_DATA_PATH_NAME)
        #if myFile.is_file(): #if the file exists
        #print("file exists bitch ass")
        sensorData = str(data)
        if self.dataCounter < 15:
            with open(ML_DATA_PATH_NAME, 'a') as f:
                f.write(sensorData)
                self.dataCounter = self.dataCounter + 1
        elif self.dataCounter ==15:
            with open(ML_DATA_PATH_NAME, 'w') as f:
                f.write(sensorData)
                self.dataCounter = 0


    def recvMsg(self):
        msg = self.connection.recv_pyobj()
        return msg



    """
    Main loop that waits for a Request from the laptop and responds to it respectively.
    """
    def run(self):
        #self.estConnection()
        print("waiting for msg")
        print(self.shutdown.is_set())
        while not self.shutdown.is_set():
            data = self.recvMsg()
            if data:
                try:
                    self.ultra96ReceiveTime = self.current_milli_time()
                    self.sendMsg(data)
                except Exception as e:
                    print("error")
                    print(e)
            else:
                print('no more data from', self.client_address)
                self.stop()

        self.stop()



    def stop(self):
        self.shutdown.set()
        self.connection.close()
        self.context.destroy()
        #THREADS[0].stop()
        print("bye")

    def current_milli_time(self):
        return round(time.time() * 1000)


"""
Pyzmq queue device that acts as the intermediary between laptop and ultra96,
to allow for easy scaling of the number of laptops used.
"""
def queueDevice():

    try:
        context = zmq.Context(1)
        #socket facing the clients
        frontend = context.socket(zmq.XREP)
        frontend.bind("tcp://" + ULTRA96_IP + ":%d" % FRONTEND_PORT)
        #socket facing services
        backend = context.socket(zmq.XREQ)
        backend.bind("tcp://" + ULTRA96_IP + ":%d" % BACKEND_PORT)
        zmq.device(zmq.QUEUE, frontend, backend)

    except Exception as e:
        print(e)
        print("bringing down zmq device")
    finally:
        pass
        frontend.close()
        backend.close()
        context.term()



def main():


    #ultra96EvalClient = ultra96_eval_client.EvalClient("localhost", 8088)
    queueDeviceProcess = multiprocessing.Process(target= queueDevice)
    my_server = Server(BACKEND_PORT)

    #THREADS.append(ultra96EvalClient)
    #THREADS.append(my_server)

    queueDeviceProcess.start()
    #ultra96EvalClient.start()
    my_server.start()



if __name__ == '__main__':
    main()