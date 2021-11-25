from Motor import *
import time
PWM=Motor()

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



if __name__ == '__main__':

    print("Starting...")
    import sys
    if sys.argv[1] == 'forward':
        motor_forward()
    elif sys.argv[1] == 'backward':
        motor_backward()
    elif sys.argv[1] == 'left':
        motor_left()
    elif sys.argv[1] == 'right':
        motor_right()
    elif sys.argv[1] == 'test':
        motor_test()


