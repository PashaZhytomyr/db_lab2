import logging

logging.basicConfig(filename='info.log', level=logging.INFO)


class Service:
    def __init__(self, connection):
        self.connection = connection

    def serviceSenders(self):
        initSenders = self.connection.zrange('sent:', 0, 5, withscores=True, desc=True)
        return self.printResult(initSenders)

    def serviceSpamers(self):
        initSpamers = self.connection.zrange('spam:', 0, 5, withscores=True, desc=True)
        return self.printResult(initSpamers)

    def printResult(self, value):
        for i, value in enumerate(value):
            print(f' {value[0]} - count: {int(value[1])}')

    def connectionPipeLine(self, connectionPipeline, user, messageFrom):
        connectionPipeline.zincrby('sent:', 1, f'user:{user}')
        connectionPipeline.hincrby(f'user:{messageFrom}', 'queue', 1)
        connectionPipeline.execute()

    def registration(self, login):
        if self.connection.hget('users:', login):
            return print('User exists')

        id = self.connection.incr('user:id:')
        connectionPipeline = self.connection.pipeline(True)
        connectionPipeline.hset('users:', login, id)
        connectionPipeline.hmset('user:%s' % id, {'id': id,'login': login, 'queue': 0, 'check': 0, 'block': 0, 'sent': 0, 'deliver': 0
        })
        connectionPipeline.execute()
        return id

    def login(self, login):
        loginIdentifier = self.connection.hget('users:', login)
        if not loginIdentifier:
            return -1
        self.connection.sadd('online:', login)
        return int(loginIdentifier)

    def logout(self, usersId):
        return self.connection.srem('online:', self.connection.hmget(f'user:{ usersId }', ['login'])[0])

    def sendMessage(self, text, messageFromId, recipient):
        status = 'status'
        messageId = int(self.connection.incr('message:id:'))
        recipientId = int(self.connection.hget('users:', recipient))
        if not recipientId:
            print(f'{ recipient } not exist')
            return -1

        connectionPipeline = self.connection.pipeline(True)
        connectionPipeline.hmset(f'message:{ messageId }', {'text': text,'id': messageId,'messageFromId': messageFromId,'recipientId': recipientId,'status': 'created'})
        connectionPipeline.lpush('queue:', messageId)
        connectionPipeline.hmset(f'message:{messageId}', {
            status: 'queue'
        })
        user = self.connection.hmget(f'user:{messageFromId}', ['login'])[0]
        self.connectionPipeLine(connectionPipeline, user, messageFromId)
        return messageId

    def initOnlineUsers(self):
        onlineUsers = self.connection.smembers('online:')
        print(f'sign in users length: {len(onlineUsers)}')
        for onlineUser in onlineUsers:
            print(onlineUser)
        return onlineUsers




