from service import Service
import redis
import atexit
import random
from threading import Thread
from faker import Faker


class Thread(Thread):
    def __init__(self, connection, login, initList):
        Thread.__init__(self)
        self.c = connection
        self.d = Service(self.c)
        self.d.registration(login)
        self.id = self.d.login(login)
        self.l = initList

    def run(self):
        randomChoice = random.choice(self.l)
        messages = Faker().sentence(nb_words=7)
        self.d.sendMessage(messages, self.id, randomChoice)


def end():
    online = 'online'
    connection = redis.Redis(charset='utf-8', decode_responses=True)
    online = connection.smembers(online)
    connection.srem(online, list(online))


def startThread(threads):
    for thread in threads:
        thread.start()


if __name__ == '__main__':
    atexit.register(end)
    logs = 'username'
    loginUsers = [Faker().profile(fields=[logs])[logs] for exist in range(3)]
    threads = []
    print(loginUsers)
    for login in loginUsers:
        threads.append(Thread(redis.Redis(charset='utf-8', decode_responses=True), login, loginUsers))
    startThread(threads)
