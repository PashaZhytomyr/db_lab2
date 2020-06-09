import redis
import logging
from service import Service
from threading import Thread

logging.basicConfig(filename='info.log', level=logging.INFO)


def menuInterface():
    print('0: return')
    print('1: users')
    print('2: user send message count')
    print('3: users spam message')


def connection():
    connection = redis.Redis(charset='utf-8', decode_responses=True)
    subscriber = InitListener(connection)
    subscriber.setDaemon(True)
    subscriber.start()
    return Service(connection)


class InitListener(Thread):
    def __init__(self, connection):
        Thread.__init__(self)
        self.connection = connection


if __name__ == '__main__':
    def mainMenu():
        menuInterface()
        return int(input('>: '))
    service = connection()
    while 1:
        switch = mainMenu()
        if switch != 1 and switch != 2 and switch != 3:
            print('exit from admin tools')
            break
        elif switch == 1:
            service.initOnlineUsers()
        elif switch == 2:
            service.serviceSenders()
        elif switch == 3:
            service.serviceSpamers()
