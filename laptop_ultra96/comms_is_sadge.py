from concurrent.futures.thread import _worker
from bluepy import btle
from bluepy.btle import BTLEException, Scanner, BTLEDisconnectError
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from laptop_ultra96_client1 import Ultra96Client

# Global Vars
connections = {}
connection_threads = {}
beetle_count = 1 #number of beetles being used

#Add MAC Addresses of beetles into BTAddress dictionary before running!
#BTAddress = ['C8:DF:84:FE:3C:EB','C8:DF:84:FE:4F:39', 'B0:B1:13:2D:D4:A6']
BTAddress = ['B0:B1:13:2D:D3:71']
threads = list()
char_uuid = "0000dfb1-0000-1000-8000-00805f9b34fb"
service_uuid = "0000dfb0-0000-1000-8000-00805f9b34fb"

class MyDelegate(btle. DefaultDelegate):
    def __init__(self, connection_index):
        btle.DefaultDelegate.__init__(self)
        self.connection_index = connection_index
        #self.ID=str(connection_index)

    def handleNotification(self, cHandle, data):

        data_string = data.decode("utf-8") # decode to string
        if not connection_threads[self.connection_index].frag_front == "":
            data_fragment = connection_threads[self.connection_index].frag_front
            print("Fixing packet by adding incomplete <" + data_fragment + "> to current data packet " + data_string)
            data_string = connection_threads[self.connection_index].frag_front + data_string
            print(data_string + " is the new stitched output.")
            connection_threads[self.connection_index].frag_front = ""
        '''if not connection_threads[self.connection_index].frag_end == "":
            data_string += connection_threads[self.connection_index].frag_front
            connection_threads[self.connection_index].frag_front = ""'''
        #print(data_string)
        #print(connection_threads[self.connection_index].packet)
        try:

            if data_string =="HANDSHAKE":
                connection_threads[self.connection_index].handshake = True

            elif data_string =="ACK":
                connection_threads[self.connection_index].ACK = True

            elif "T|" in data_string:
                text = data_string.split("|")
                connection_threads[self.connection_index].first_sync = text[1]
                connection_threads[self.connection_index].sync = True

            elif data_string[0] =="P":
                connection_threads[self.connection_index].packet += data_string
                if connection_threads[self.connection_index].packet.count("|") > 14:
                    index = connection_threads[self.connection_index].packet.count("|")
                    split = connection_threads[self.connection_index].packet.split("|")
                    connection_threads[self.connection_index].current_data["roll"] = split[1]
                    connection_threads[self.connection_index].current_data["pitch"] = split[2]
                    connection_threads[self.connection_index].current_data["gyroX"] = split[3]
                    connection_threads[self.connection_index].current_data["gyroY"] = split[4]
                    connection_threads[self.connection_index].current_data["gyroZ"] = split[5]
                    connection_threads[self.connection_index].current_data["accelX"] = split[6]
                    connection_threads[self.connection_index].current_data["accelY"] = split[7]
                    connection_threads[self.connection_index].current_data["accelZ"] = split[8]
                    connection_threads[self.connection_index].current_data["movingPacket"] = split[9]
                    connection_threads[self.connection_index].current_data["movingCount"] = split[10]
                    connection_threads[self.connection_index].current_data["emg1"] = split[11]
                    connection_threads[self.connection_index].current_data["emg2"] = split[12]
                    connection_threads[self.connection_index].current_data["emg3"] = split[13]
                    connection_threads[self.connection_index].current_data["millis"] = split[14]

                    if connection_threads[self.connection_index].packet.count("|") > 15: #EXTRA STUFF, STITCH PLS
                        for x in split:
                            if x > 14:
                                split[x] += "|"
                                connection_threads[self.connection_index].frag_front += split[x]
                                #Remove extra "|" delimiter
                                connection_threads[self.connection_index].frag_front = connection_threads[self.connection_index].frag_front[:-1]
                    connection_threads[self.connection_index].packet = ""
                    connection_threads[self.connection_index].data_ready = True

            else:
                connection_threads[self.connection_index].packet += data_string
                if connection_threads[self.connection_index].packet.count("|") > 14:
                    split = connection_threads[self.connection_index].packet.split("|")
                    connection_threads[self.connection_index].current_data["roll"] = split[1]
                    connection_threads[self.connection_index].current_data["pitch"] = split[2]
                    connection_threads[self.connection_index].current_data["gyroX"] = split[3]
                    connection_threads[self.connection_index].current_data["gyroY"] = split[4]
                    connection_threads[self.connection_index].current_data["gyroZ"] = split[5]
                    connection_threads[self.connection_index].current_data["accelX"] = split[6]
                    connection_threads[self.connection_index].current_data["accelY"] = split[7]
                    connection_threads[self.connection_index].current_data["accelZ"] = split[8]
                    connection_threads[self.connection_index].current_data["movingPacket"] = split[9]
                    connection_threads[self.connection_index].current_data["movingCount"] = split[10]
                    connection_threads[self.connection_index].current_data["emg1"] = split[11]
                    connection_threads[self.connection_index].current_data["emg2"] = split[12]
                    connection_threads[self.connection_index].current_data["emg3"] = split[13]
                    connection_threads[self.connection_index].current_data["millis"] = split[14]
                    #print(connection_threads[self.connection_index].current_data)

                    if connection_threads[self.connection_index].packet.count("|") > 15: #EXTRA STUFF, STITCH PLS
                        for x in split:
                            if x > 14:
                                split[x] += "|"
                                connection_threads[self.connection_index].frag_front += split[x]
                                #Remove extra "|" delimiter
                                connection_threads[self.connection_index].frag_front = connection_threads[self.connection_index].frag_front[:-1]
                    connection_threads[self.connection_index].packet = ""
                    connection_threads[self.connection_index].data_ready = True
        except Exception:
            # flag for packet error, this packet will be ignored
            #print("packt error due to exception")
            #connection_threads[self.connection_index].packet_error = True
            pass

class ConnectionHandlerThread (threading.Thread):
    handshake = False
    packet = ""
    sync = False
    frag_front = ""
    frag_end = ""
    first_sync = 0
    latest_time = 0
    packet_error = False
    data_ready = False
    error_count = 0 # once reach more than 3 errors attempt to reconnect
    success_count = 0 # for checking reliability
    ACK = False
    current_data={
        "roll" : "#",
        "pitch" : "#",
        "gyroX" : "#",
        "gyroY" : "#",
        "gyroZ" : "#",
        "accelX" : "#",
        "accelY" : "#",
        "accelZ" : "#",
        "movingPacket": "#",
        "movingCount": "#",
        "emg1" : "#",
        "emg2" : "#",
        "emg3" : "#",
        "millis" : "#",
    }

    def __init__(self, connection_index, btaddress):
        #print ("Successful Connection to BLE " + str(btaddress))
        threading.Thread.__init__(self)
        self.connection_index = connection_index
        self.connection = (connections[self.connection_index])
        self.connection.setDelegate(MyDelegate(self.connection_index))
        self.service = self.connection.getServiceByUUID(service_uuid)
        self.characteristic=self.service.getCharacteristics()[0]
        self.btaddress = btaddress
        self.service = self.connection.getServiceByUUID(service_uuid)
        self.characteristic=self.service.getCharacteristics()[0]

    def connect(self):
        self.connection.setDelegate(MyDelegate(self.connection_index))

    def run(self):
        while True:
            try:
                if not self.handshake:
                    self.handshake_proto(self.connection)
                else:
                    self.data_proto(self.connection)
            except BTLEException:
                    self.connection.disconnect()
                    print(str(self.btaddress[self.connection_index]) + " reconnecting")
                    self.reconnect_beetle()
            except Exception:
                pass

    def handshake_proto(self,p):
        # Send handshake packet
        print("Handshake for Bluno # " + str(self.connection_index +1))
        # Wait for Handshake packet from bluno
        while not self.handshake:
            self.characteristic.write(bytes("H", "utf-8"), withResponse=False)
            p.waitForNotifications(2)
        # Send back ACK
        print("Handshake received, return ACK")
        while not self.ACK:
            self.characteristic.write(bytes("A", "utf-8"), withResponse=False)
            p.waitForNotifications(2)
        self.ACK=False
        self.time_sync(self.connection)
        while len(connection_threads) != beetle_count: # make sure all beetles connect
            continue
        self.characteristic.write(bytes("B", "utf-8"), withResponse=False)
        p.waitForNotifications(2)

    def data_proto(self,p):
        if not p.waitForNotifications(5): # no notif from beetle after 5 seconds -> reconnect!
            print("Reconnecting with beetle " + str(self.connection_index + 1))
            self.handshake = False
            self.connection.disconnect()
            self.reconnect_beetle()

        while not self.data_ready:
            p.waitForNotifications(0.2)
        self.data_ready = False

        if not self.packet_error:
            for x in self.current_data: # filter out bad pckts
                if "P" in self.current_data[x] or "#" in self.current_data[x]:
                    #print("error due to invalid char")
                    self.packet_error = True
            '''if len(self.current_data["millis"]) < 4 or len(self.current_data["gyroX"]) > 4 or \
                    len(self.current_data["gyroY"]) > 4 or len(self.current_data["gyroZ"]) > 4:
                #print("error due to extra values")
                self.packet_error = True'''

        if self.packet_error:
            self.error_count += 1
            connection_threads[self.connection_index].packet_error = False
            self.frag_front = ""
            self.frag_end = ""
            print("Err in " + str(self.connection_index + 1) + ". " + str(self.error_count) + str(self.current_data))

        else:
            #print out packet data
            #print("beetle " + str(self.connection_index + 1) + "'s data_packet")
            #self.success_count +=1
            print(str(self.connection_index + 1) + ": " + str(self.current_data))
            #print(self.success_count)

        self.current_data={
            "roll" : "#",
            "pitch" : "#",
            "gyroX" : "#",
            "gyroY" : "#",
            "gyroZ" : "#",
            "accelX" : "#",
            "accelY" : "#",
            "accelZ" : "#",
            "movingPacket": "#",
            "movingCount": "#",
            "emg1" : "#",
            "emg2" : "#",
            "emg3" : "#",
            "millis" : "#",
        }

    #def gyro_proto(self,p):

    def time_sync(self,p):
        self.sync=False
        #print("SEND SYNC REQ")
        while not self.sync:
            self.characteristic.write(bytes("T", "utf-8"), withResponse=False)
            p.waitForNotifications(1)
        #self.first_sync -> is updated
        #print(self.first_sync)


    def reconnect_beetle(self):
        index = self.connection_index
        beetle_address = self.btaddress[self.connection_index]
        while True:
            try:
                p1 = btle.Peripheral()
                p1.connect(beetle_address, btle.ADDR_TYPE_PUBLIC)
                connections[self.connection_index]=p1
                t = ConnectionHandlerThread(self.connection_index, self.btaddress)
                #start thread
                t.start()
                connection_threads[self.connection_index]=t
                break
            except Exception:
                time.sleep(0.69)

def beetles_establish_connection(Beetle_Addr, index):
    global startTime
    while True:
        try:
            p = btle.Peripheral()
            p.connect(Beetle_Addr, btle.ADDR_TYPE_PUBLIC)
            connections[index]=p
            t = ConnectionHandlerThread(index, BTAddress)
            #start thread
            t.start()
            connection_threads[index]=t
            print ("Successful Connection to BLE " + str(Beetle_Addr))
            break
        except BTLEException:
            print("Connection Fail. Retrying now...")
            time.sleep(1)
            continue
        except Exception:
            print("Unable to locate beetles, please try reconnecting and restarting the beetles!")
            continue

def reestablish_connection(Beetle_Addr, index):
    while True:
        try:
            print("trying to reconnect with beetle " + index + " at " + str(Beetle_Addr))
            p1 = btle.Peripheral()
            connections[index]=p1
            t = ConnectionHandlerThread(index, Beetle_Addr)
            #start thread
            t.start()
            connection_threads[index]=t
            break
        except Exception:
            time.sleep(0.69)




def main():
    #only calls for connection for bluno
    #establish_connection()
    client = Ultra96Client(clientId=0)
    client.start()
    #Test concurrency
    index = 0
    with ThreadPoolExecutor(max_workers=beetle_count) as executor:
        for Beetle_Addr in BTAddress:
            executor.submit(beetles_establish_connection(Beetle_Addr,index))
            index += 1

if __name__ == "__main__":
    main()