import random
import time
import redis
from threading import Thread


class QueueMessageWorker(Thread):
    def __init__(self, connect, delay):
        Thread.__init__(self)
        self.connect = connect
        self.delay = delay

    def run(self):
        status = 'status'
        while 1:
            getQueryMessageFromService = self.connect.brpop('queue:')

            if getQueryMessageFromService:
                messageStatusChanges = int(getQueryMessageFromService[1])
                self.connect.hmset(f'message:{messageStatusChanges}', {
                    status: 'check'
                })
                messageStatusChanges = self.connect.hmget(f'message:{messageStatusChanges}',['messageFromId', 'recipientId'])
                messageFromId = int(messageStatusChanges[0])
                recipientId = int(messageStatusChanges[1])
                self.getMessageReload(messageFromId)
                if random.random() > 0.3:
                    self.toSpamMessage(messageFromId, messageStatusChanges)
                else:
                    status = 'status'
                    self.connect.hmset(f'message:{messageStatusChanges}', {
                        status: 'sent'
                    })
                    self.connect.hincrby(f'user:{messageFromId}', 'sent', 1)
                    self.connect.sadd(f'sentto:{recipientId}', messageStatusChanges)

    def getMessageReload(self, messageFromId):
        self.connect.hincrby(f'user:{messageFromId}', 'queue', -1)
        self.connect.hincrby(f'user:{messageFromId}', 'check', 1)
        time.sleep(self.delay)
        self.connect.pipeline(True)
        self.connect.hincrby(f'user:{messageFromId}', 'check', -1)

    def toSpamMessage(self, messageFromId, messageStatusChanges):
        status = 'status'
        fromLogin = self.connect.hmget(f'user:{messageFromId}', ['login'])[0]
        self.connect.zincrby('spam:', 1, f'user:{messageFromId}')
        self.connect.hmset(f'message:{messageStatusChanges}', {
            status: 'block'
        })
        self.connect.hincrby(f'user:{messageFromId}', 'block', 1)
        message = self.connect.hmget(f'message:{messageStatusChanges}', ['text'])[0]
        self.connect.publish('spam', f'User {fromLogin} sent spam message: {message}')


if __name__ == '__main__':
    for x in range(1):
        handlers = random.randint(0, 3)
        connection = redis.Redis(charset='UTF-8', decode_responses=True)
        queryWorkers = QueueMessageWorker(connection, handlers)
        queryWorkers.daemon = True
        queryWorkers.start()
    while 1:
        pass
