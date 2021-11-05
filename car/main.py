from Motor import *
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


if __name__ == '__main__':

    print("Starting...")
    import sys
    if sys.argv[1] == 'forward':
        motor_forward()
    elif sys.argv[1] == 'backward':
        motor_backward()

