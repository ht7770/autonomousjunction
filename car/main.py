from Motor import *
import socket
import time
import os
import random
import _thread
PWM=Motor()

serverIP = '192.168.1.154'
hostIP = '192.168.1.156'
port = 8888
bufferSize = 2048
serverAddress = (serverIP, port)

UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



possibleTurns = ["right", "left", "forward"]
deviceID = "car1"


def motor_forward():
    PWM.setMotorModel(1000, 1000, 1000, 1000)
    print("Moving forwards...")
    time.sleep(1)
    PWM.setMotorModel(0,0,0,0)


def motor_backward():
    PWM.setMotorModel(-1000, -1000, -1000, -1000)
    print("Moving backwards...")
    time.sleep(1)
    PWM.setMotorModel(0, 0, 0, 0)

def motor_left():
    PWM.setMotorModel(600, 600, 4000, 4000)
    print("Moving left...")
    time.sleep(1.5)
    PWM.setMotorModel(0, 0, 0, 0)

def motor_right():
    PWM.setMotorModel(4000, 4000, 600, 600)
    print("Moving right...")
    time.sleep(1.5)
    PWM.setMotorModel(0, 0, 0, 0)

def motor_test():
    leftfront = int(input("Enter value for left front motor: "))
    leftrear = int(input("Enter value for left rear motor: "))
    rightfront = int(input("Enter value for right front motor: "))
    rightrear = int(input("Enter value for right rear motor: "))
    usertime = int(input("Enter a time till motor shutoff: "))
    PWM.setMotorModel(leftfront, leftrear, rightfront, rightrear)
    time.sleep(usertime)
    PWM.setMotorModel(0,0,0,0)

def getRandomMove():
    global possibleTurns
    choice = random.choice(possibleTurns)
    print("Vehicle wants to turn: {}".format(choice))
    return choice

def UDPlistener():
    global message
    while True:
        data, clientMessage = UDPsocket.recvfrom(bufferSize)
        message = data.decode("utf-8")


def MakeMessage(deviceID, action, data=''):
    if data:
        return '{{ "device" : "{}", "action":"{}", "data" : "{}" }}'.format(
            deviceID, action, data)
    else:
        return '{{ "device" : "{}", "action":"{}" }}'.format(deviceID, action)

def sendCommand(message):
    UDPsocket.sendto(message.encode('utf8'), serverAddress)

def RunAction(action):
    message = MakeMessage(deviceID, action)
    sendCommand(message)

def main():
    motor_forward()
    move = getRandomMove().upper()

    message = MakeMessage(deviceID, 'attach')
    sendCommand(message)
    time.sleep(1)
    message = MakeMessage(deviceID, 'subscribe')
    sendCommand(message)
    time.sleep(1)
    message = MakeMessage(deviceID, 'event', move)
    sendCommand(message)
    time.sleep(1)
    while True:
        data, clientMessage = UDPsocket.recvfrom(bufferSize)
        message = data.decode("utf-8")

        if message == "APPROVED":
            print("Action approved, car is moving...")
            if move == 'right':
                motor_right()
            elif move == 'left':
                motor_left()
            elif move == 'forward':
                motor_forward()
        else:
            time.sleep(1)









if __name__ == '__main__':
    main()



