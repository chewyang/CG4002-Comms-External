import random
from time import sleep
import multiprocessing
import threading

ACTIONS = ['mermaid', 'jamesbond', 'dab']
POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']


class StringGen():
    def __init__(self, randSeed = None):
        super(StringGen, self).__init__()
        self.isShutDown = False
        self.randSeed = randSeed
        
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
    def sendEvalString(self):
        #while not self.isShutDown:
        if self.randSeed:
            random.seed(self.randSeed)
            
        
        actionIdx = random.randint(0,2)
        positionIdx = random.randint(0,5)
        syncDelay = random.randrange(0, 500)



        randMsg = str(POSITIONS[positionIdx]) + "|" + ACTIONS[actionIdx] + "|" + str(syncDelay)
        print(randMsg)
        return randMsg
        #sleep(3)
    
    


def main():
    myGen = StringGen()
    myGen.sendEvalString()
    



if __name__ == '__main__':
    main()