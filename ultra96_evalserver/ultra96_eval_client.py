from pickle import FALSE
import time
import socket
import threading
import base64
from Crypto.Cipher import AES
from Crypto import Random
import sys
sys.path.append('..')
from randomvalues import random_eval_string_gen
BLOCK_SIZE = 16
TARGET_IP = "localhost" #To be changed to evaluation server's IP address
TARGET_PORT = 8089 #To be changed to evaluation server's port

#Pads the plaintext to be a multiple of the block size of the cipher.
pad = lambda s:  ((BLOCK_SIZE - len(s) % BLOCK_SIZE) -1 ) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE) + "#" +  s

PASSWORD = "aaaaaaaaaaaaaaaa"
MAIN_FLAG = False


class EvalClient(threading.Thread):
    def __init__(self, targetIp, targetPort):
        super().__init__()
        self.shutDown = threading.Event()
        self.targetIp = targetIp
        self.targetPort = targetPort
        self.estSocketComms()
        

    """Establishes the socket connections to the evaluation server"""
    def estSocketComms(self):
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self.targetIp, self.targetPort))
            print("connected!")
    
        except Exception as e:
            print("Connection error")
            print(e)

    """Main thread that repeatedly waits for the position data from the evaluation server"""
    def run(self):
         while not self.shutDown.is_set():
            data = self.receiveMsg()
            if data:
                try:
                    msg = data.decode("utf8")
                    print("Data received from evaluation server is: " + msg)
                    #If this program is run as the main program instead of being invoked from the u96 host script
                    if MAIN_FLAG:
                        self.sendEncryptedMsg(random_eval_string_gen.StringGen().sendEvalString())
                        time.sleep(4)
                except Exception as e:
                    print("Error in receiving messages")
                    print(e)
            else:
                print('no more data')
                self.stop() 
                


    """Pads the plaintext and encryptes the plaintext with a random IV"""
    def encrypt(self, raw):
        secret_key = bytes(str(PASSWORD), encoding="utf8") 
        raw = pad(raw).encode("utf-8")
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))
    

    def receiveMsg(self):
        data = self.connection.recv(1024)
        return data
            
    
    def sendEncryptedMsg(self, plaintext):
        ciphertext = self.encrypt(plaintext)
        self.connection.send(ciphertext)
        
    
    def sendLogoutMsg(self):
        plaintextLogoutMsg = "|logout|"
        self.sendEncryptedMsg(plaintextLogoutMsg)
        self.stop()
        
    
    def stop(self):
        self.connection.close()
        self.shutDown.set()
        print("Bye")


def main():
    my_server = EvalClient(TARGET_IP, TARGET_PORT)
    my_server.start()



if __name__ == '__main__':
    main()
    MAIN_FLAG = True