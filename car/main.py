from Motor import *
import socket
import time
import os
import random
import _thread
PWM=Motor()

# Addresses for server and client
serverIP = '192.168.1.154'
hostIP = socket.gethostbyname(socket.gethostname())
port = 8888
bufferSize = 2048
serverAddress = (serverIP, port)
hostAddress = (hostIP, port)

# Creates a UDP socket and binds to it for sending and receiving messages
UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPsocket.bind(hostAddress)

# List of possible turns
possibleTurns = ["right", "left", "forward"]

# car ID, will be stored in gateway with address to know which vehicle to send which data to
deviceID = "car1"

# function for forward movement
def motor_forward():
    PWM.setMotorModel(1000, 1000, 1000, 1000)
    print("Moving forwards...")
    time.sleep(1)
    PWM.setMotorModel(0,0,0,0)

# function for backward movement
def motor_backward():
    PWM.setMotorModel(-1000, -1000, -1000, -1000)
    print("Moving backwards...")
    time.sleep(1)
    PWM.setMotorModel(0, 0, 0, 0)

# function for left turns
def motor_left():
    PWM.setMotorModel(600, 600, 4000, 4000)
    print("Moving left...")
    time.sleep(1.5)
    PWM.setMotorModel(0, 0, 0, 0)

# function for right turns
def motor_right():
    PWM.setMotorModel(4000, 4000, 600, 600)
    print("Moving right...")
    time.sleep(1.5)
    PWM.setMotorModel(0, 0, 0, 0)

# Chooses a random direction to turn at junction, in principle this would be based on car navigation data
def getRandomMove():
    global possibleTurns
    choice = random.choice(possibleTurns)
    print("Vehicle wants to turn: {}".format(choice))
    return choice

# Crafts the message dependent on if data is being sent or not
def MakeMessage(deviceID, action, data=''):
    if data:
        return '{{ "device" : "{}", "action":"{}", "data" : "{}" }}'.format(
            deviceID, action, data)
    else:
        return '{{ "device" : "{}", "action":"{}" }}'.format(deviceID, action)

# Sends message to gateway
def sendCommand(message):
    UDPsocket.sendto(message.encode('utf8'), serverAddress)

def main():
    # Pulls up to junction
    motor_forward()
    # Chooses random move
    move = getRandomMove().upper()

    # Attach to gateway
    message = MakeMessage(deviceID, 'attach')
    sendCommand(message)
    time.sleep(1)

    # Subscribe to topics
    message = MakeMessage(deviceID, 'subscribe')
    sendCommand(message)
    time.sleep(1)

    # Send direction of travel
    message = MakeMessage(deviceID, 'event', move)
    sendCommand(message)
    time.sleep(1)

    # Listen for messages from the gateway
    while True:
        data, dataAddress = UDPsocket.recvfrom(bufferSize)
        message = data.decode("utf-8").upper()
        print("Received message from gateway: {}".format(message))

        # if direction of travel is authorised then move in intended direction
        if message == "AUTHORISED":
            print("Action approved, car is moving...")
            if move == 'RIGHT':
                motor_right()
            elif move == 'LEFT':
                motor_left()
            elif move == 'FORWARD':
                motor_forward()
            break
        elif message == "UNAUTHORISED":
            print("Maneuver is not yet allowed, waiting for 3 seconds...")
            time.sleep(3)

    # Detach from the gateway and close UDP socket after maneuver is complete
    print("Maneuver Complete")
    message = MakeMessage(deviceID, 'detach')
    sendCommand(message)
    UDPsocket.close()

if __name__ == '__main__':
    main()



