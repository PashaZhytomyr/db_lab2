import redis
import atexit
from service import Service


def mainMenu():
    print('0>: exit')
    print('1>: registration')
    print('2>: authorization')

    return int(input('>: '))


def menuForLoggedUser():
    print('0>: exit from user account and return to previous menu')
    print('1>: send message')
    print('2>: all messages')
    print('3>: get result messages')
    return int(input('>: '))


def main():
    connect = redis.Redis(charset='UTF-8', decode_responses=True)
    service = Service(connect)
    currentId = -1

    def endH():
        service.logout(currentId)

    atexit.register(endH)
    menu = mainMenu
    while 1:
        switch = menu()
        if switch == 1:
            login = input('Enter login: ')
            service.registration(login)
        elif switch == 2:
            login = input('Enter login: ')
            currentId = service.login(login)
            if currentId != -1:
                connect.publish('users', f'User {login} connected')
                while 1:
                    switch = menuForLoggedUser()
                    if switch == 1:
                        message = input('message: ')
                        recipient = input('recipient login: ')
                        service.sendMessage(message, currentId, recipient)

                    elif switch == 2:
                        mssList = service.connection.smembers(f'sentto:{currentId}')
                        for mssId in mssList:
                            message = service.connection.hmget(f'message:{mssId}',
                                                               ['messageFromId', 'text', 'status'])
                            messageFromId = message[0]
                            getValueFrom = service.connection.hmget(f'user:{messageFromId}', ['login'])[0]
                            print(f'Message by: {getValueFrom} - {message[1]} ')
                            if message[2] != 'deliver':
                                connectPipeline = service.connection.pipeline(True)
                                connectPipeline.hset(f'message:{mssId}', 'status', 'deliver')
                                connectPipeline.hincrby(f'user:{messageFromId}', 'sent', -1)
                                connectPipeline.hincrby(f'user:{messageFromId}', 'deliver', 1)
                                connectPipeline.execute()
                    elif switch == 3:
                        loggedUser = connect.hmget(f'user:{currentId}',['queue', 'check', 'block', 'sent', 'deliver'])
                        print('QUEUE message: {} || CHECK message: {} ||BLOCK message: {} ||SENT message: {} '
                              '||DELIVER message: {} '
                                .format(*tuple(loggedUser)))
                    elif switch == 0:
                        service.logout(currentId)
                        connect.publish('users', f'User signed out')
                        return
        elif switch == 0:
            return


if __name__ == '__main__':
    main()
