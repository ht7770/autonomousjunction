from Motor import *
PWM=Motor()
def motor_forward():
    PWM.setMotorModel(1000, 1000, 1000, 1000)
    print("Moving forwards...")
    time.sleep(1)
    PWM.setMotorModel(0,0,0,0)


if __name__ == '__main__':

    print("Starting...")
    import sys
    if sys.argv[1] == 'Motor':
        motor_forward()

