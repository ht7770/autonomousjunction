from Motor import *
import socket
import time
import os
PWM=Motor()

serverIP = '192.168.1.154'
port = 8888
bufferSize = 2048
serverAddress = (serverIP, port)

UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



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



def main():
    message = "Hello Server"
    UDPsocket.sendto(message.encode(), serverAddress)
    print("message sent: {}".format(message))


if __name__ == '__main__':
    main()



