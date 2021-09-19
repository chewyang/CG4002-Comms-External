
class RequestMessagePacket:
    def __init__(self, clientId, msgCount, rawBleData):
        self.clientId = clientId
        self.msgCount = msgCount
        self.rawBleData = rawBleData

    def printReqString(self):
        return "Request #%d, from client #%d: %s" % (self.msgCount, self.clientId, self.rawBleData)



class ReplyMessagePacket:
    def __init__(self, clientId, msgCount):
        self.clientId = clientId
        self.msgCount = msgCount

    def printReqString(self):
        return "Request #%d, from client #%d: %s, acknowledged" % (self.msgCount, self.clientId)

class syncMessagePacket:
    def __init__(self, blunoSentTime):
        self.blunoSentTime = blunoSentTime
        self.ultra96RecvTime = None
        self.ultra96SentTime = None
        self.blunoRecvTime = None

    def printSyncString(self):
        return "Bluno sent time: %s, Ultra96 received time: %s, Ultra96 sent time: %s, Bluno received time: %s" % (self.blunoSentTime, self.ultra96RecvTime, self.ultra96SentTime, self.blunoRecvTime)

    
    def getClockOffset(self):
        rtt = (self.ultra96RecvTime - self.blunoSentTime) - (self.ultra96SentTime - self.blunoRecvTime)
        clockOffset = (self.ultra96RecvTime - self.blunoSentTime) - (rtt / 2)
        return clockOffset
