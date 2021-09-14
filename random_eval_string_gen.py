import random
from time import sleep
import multiprocessing
import threading

ACTIONS = ['mermaid', 'jamesbond', 'dab']
POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']

bleDict = dict.fromkeys([
    'roll',
    'pitch',
    'yaw',
    'AccX',
    'AccY',
    'AccZ',
    'mil'
    ])


class StringGen():
    def __init__(self):
        super(StringGen, self).__init__()
        self.isShutDown = False
        
        
        #p = threading.Thread(target=self.stop)
        #p.start()


    """def stop(self):
        while self.isShutDown == False:
            try:
                stopMsg = input()
                if "stop" in stopMsg:
                    self.isShutDown = True
            except Exception as e:
                pass
"""
    def sendRawBleData(self):
    
        
        bleDict["roll"] = random.randint(0, 100)
        bleDict["pitch"] = random.randint(0, 100)
        bleDict["yaw"] = random.randint(0, 100)
        bleDict["AccX"] = random.randint(0, 100)
        bleDict["AccY"] = random.randint(0, 100)
        bleDict["AccZ"] = random.randint(0, 100)
        bleDict["mil"] = random.randint(0, 100)

        #print(bleDict)

        return str(bleDict)


    def sendEvalString(self):
 
        actionIdx = random.randint(0,2)
        positionIdx = random.randint(0,5)
        syncDelay = random.randrange(0, 500)



        randMsg = str(POSITIONS[positionIdx]) + "|" + ACTIONS[actionIdx] + "|" + str(syncDelay)
        #print(randMsg)
        return randMsg
        #sleep(3)
    
    




def main():
    myGen = StringGen()
    myGen.sendRawBleData()
    



if __name__ == '__main__':
    main()