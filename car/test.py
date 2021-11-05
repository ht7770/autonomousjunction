import time
from Led import *

led = Led()


def test_Led():
    try:
        led.ledIndex(0x01, 255, 0, 0)  # Red
        led.ledIndex(0x02, 255, 125, 0)  # orange
        led.ledIndex(0x04, 255, 255, 0)  # yellow
        led.ledIndex(0x08, 0, 255, 0)  # green
        led.ledIndex(0x10, 0, 255, 255)  # cyan-blue
        led.ledIndex(0x20, 0, 0, 255)  # blue
        led.ledIndex(0x40, 128, 0, 128)  # purple
        led.ledIndex(0x80, 255, 255, 255)  # white'''
        print("The LED has been lit, the color is red orange yellow green cyan-blue blue white")
        time.sleep(3)  # wait 3s
        led.colorWipe(led.strip, Color(0, 0, 0))  # turn off the light
        print("\nEnd of program")
    except KeyboardInterrupt:
        led.colorWipe(led.strip, Color(0, 0, 0))  # turn off the light
        print("\nEnd of program")


from Motor import *

PWM = Motor()


def test_Motor():
    try:
        PWM.setMotorModel(1000, 1000, 1000, 1000)  # Forward
        print("The car is moving forward")
        time.sleep(1)
        PWM.setMotorModel(-1000, -1000, -1000, -1000)  # Back
        print("The car is going backwards")
        time.sleep(1)
        PWM.setMotorModel(-1500, -1500, 2000, 2000)  # Left
        print("The car is turning left")
        time.sleep(1)
        PWM.setMotorModel(2000, 2000, -1500, -1500)  # Right
        print("The car is turning right")
        time.sleep(1)
        PWM.setMotorModel(0, 0, 0, 0)  # Stop
        print("\nEnd of program")
    except KeyboardInterrupt:
        PWM.setMotorModel(0, 0, 0, 0)
        print("\nEnd of program")



# Main program logic follows:
if __name__ == '__main__':

    print('Program is starting ... ')
    import sys

    if len(sys.argv) < 2:
        print("Parameter error: Please assign the device")
        exit()
    if sys.argv[1] == 'Led':
        test_Led()
    elif sys.argv[1] == 'Motor':
        test_Motor()
    elif sys.argv[1] == 'Ultrasonic':
        test_Ultrasonic()
    elif sys.argv[1] == 'Infrared':
        test_Infrared()
    elif sys.argv[1] == 'Servo':
        test_Servo()
    elif sys.argv[1] == 'ADC':
        test_Adc()
    elif sys.argv[1] == 'Buzzer':
        test_Buzzer()
