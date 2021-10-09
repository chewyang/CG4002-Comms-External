import random
import time

ACTIONS = ['mermaid', 'jamesbond', 'dab']
POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']




"""This is the class that generates the fake sensor data and the fake predicted data."""
class StringGen():
    def __init__(self, dancerId = None):
        super(StringGen, self).__init__()
        self.isShutDown = False
        self.dancerId = dancerId
        self.counter = 0
        self.danceMoveNum = 1
        
    """
    This is the emulated bluno which sends the raw sensor data. 
    The start time of the dance move is only sent every 10 data to indicate the start of a different moves
    """
    def sendRawBleData(self):
        bleDict = dict.fromkeys([
            'dancerId',
            'danceMoveNum, startTime',
            'roll',
            'pitch',
            'yaw',
            'AccX',
            'AccY',
            'AccZ',
            'mil'
        ])

        #time.sleep(random.randint(1,3))
        #time.sleep(random.random())
        time.sleep(0.0001)

        if self.counter == 0: #start of the next dance move
            bleDict["danceMoveNum, startTime"] = self.danceMoveNum, self.current_milli_time()

        else:
            bleDict["danceMoveNum, startTime"] = None

        bleDict["dancerId"] = self.dancerId
        bleDict["roll"] = random.randint(0, 100)
        bleDict["pitch"] = random.randint(0, 100)
        bleDict["yaw"] = random.randint(0, 100)
        bleDict["AccX"] = random.randint(0, 100)
        bleDict["AccY"] = random.randint(0, 100)
        bleDict["AccZ"] = random.randint(0, 100)
        bleDict["mil"] = random.randint(0, 100)

        #if self.counter == 0:
        #    print(f" dancer id: {self.dancerId}, counter: {self.counter} data: {bleDict}")
    
        if self.counter == 10:
            self.counter = 0
            self.danceMoveNum = self.danceMoveNum + 1
        else: 
            self.counter = self.counter + 1

        return bleDict

    def current_milli_time(self):
        return round(time.time() * 1000)

    def sendEvalString(self, syncDelay = None):
        predict = dict.fromkeys([
           'position',
           'danceMove',
           'syncDelay'
        ])
        
        if syncDelay == None:
            predict["syncDelay"] = random.randint(0,200)
        else:
            predict["syncDelay"] = syncDelay

        actionIdx = random.randint(0,2)
        predict["danceMove"] = ACTIONS[actionIdx]

        positionIdx = random.randint(0,5)
        predict["position"] = POSITIONS[positionIdx]

        
        randMsg = str(predict["position"] + "|" + predict["danceMove"] + "|" + str(predict["syncDelay"]))
        print(randMsg)
        return randMsg, predict

def main():
    myGen = StringGen()
    myGen.sendRawBleData()
    



if __name__ == '__main__':
    main()