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


def userOptions(connection, messageService, currentUserId):
    while 1:
        switch = menuForLoggedUser()
        if switch == 1:
            message = input('message: ')
            recipient = input('recipient login: ')
            messageService.sendMessage(message, currentUserId, recipient)

        elif switch == 2:
            mssList = messageService.connection.smembers(f'sentto:{ currentUserId }')
            for mssId in mssList:
                message = messageService.connection.hmget(f'message:{ mssId }', ['messageFromId', 'text', 'status'])
                messageFromId = message[0]
                getValueFrom = messageService.connection.hmget(f'user:{ messageFromId }', ['login'])[0]
                print(f'Message by: { getValueFrom } - { message[1] } ')
                if message[2] != 'deliver':
                    connectPipeline = messageService.connection.pipeline(True)
                    connectPipeline.hset(f'message:{mssId}', 'status', 'deliver')
                    connectPipeline.hincrby(f'user:{ messageFromId }', 'sent', -1)
                    connectPipeline.hincrby(f'user:{ messageFromId }', 'deliver', 1)
                    connectPipeline.execute()
        elif switch == 3:
            loggedUser = connection.hmget(f'user:{currentUserId}', ['queue', 'check', 'block', 'sent', 'deliver'])
            print('QUEUE message: {} || CHECK message: {} ||BLOCK message: {} ||SENT message: {} ||DELIVER message: {}'
                  .format(*tuple(loggedUser)))
        elif switch == 0:
            messageService.logout(currentUserId)
            connection.publish('users', f'User signed out')
            return


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
                userOptions(connect, service, currentId)
            else:
                print('wrong login')
        elif switch == 0:
            return


if __name__ == '__main__':
    main()
