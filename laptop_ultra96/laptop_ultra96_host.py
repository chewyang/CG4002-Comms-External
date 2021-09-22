import time
import ultra96_eval_client
import random_eval_string_gen
import threading
import multiprocessing
import zmq
from dancedanceobjects.objects import ReplyMessagePacket, RequestMessagePacket, syncMessagePacket



FRONTEND_PORT = 15016
BACKEND_PORT = 15017
THREADS = []
ULTRA96_IP = "137.132.86.227"

class Server(threading.Thread):
    def __init__(self, backendPort):
        super(Server, self).__init__()


        self.backendPort = backendPort
        self.connection = None
        self.replyNum = 1
        self.estConnection()
        self.shutdown = threading.Event()
        print("Listening...")


    """
    Establishes the socket connections to the evaluation server.
    """
    def estConnection(self):
        self.context = zmq.Context()
        self.connection = self.context.socket(zmq.REP)
        self.connection.connect("tcp://137.132.86.227:%s" % BACKEND_PORT)


    """
    Sends the respective reply according to the request from laptop.
    """
    def sendMsg(self, data):
        repMsg = object()

        #If the data received is the BLE sensor data, send over the fake predicted results to evalserver and acknowledgement msg to laptop
        if isinstance(data, RequestMessagePacket):
            repMsg = ReplyMessagePacket(data.clientId, data.msgCount)
            print(data.printReqString())
            print(repMsg.printReqString())
            THREADS[0].sendEncryptedMsg(random_eval_string_gen.StringGen().sendEvalString())

        #If the data received is a sync, send over the timestamps when it receives and reply. Then send it over back to the laptop
        elif isinstance(data, syncMessagePacket):
            data.ultra96RecvTime = self.ultra96ReceiveTime
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


    """
    Main loop that waits for a Request from the laptop and responds to it respectively.
    """
    def run(self):
        print("waiting for msg")
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
        THREADS[0].stop()
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

    
    ultra96EvalClient = ultra96_eval_client.EvalClient("localhost", 8088)
    queueDeviceProcess = multiprocessing.Process(target= queueDevice)
    my_server = Server(BACKEND_PORT)

    THREADS.append(ultra96EvalClient)
    THREADS.append(my_server)

    queueDeviceProcess.start()
    ultra96EvalClient.start()
    my_server.start()



if __name__ == '__main__':
    main()