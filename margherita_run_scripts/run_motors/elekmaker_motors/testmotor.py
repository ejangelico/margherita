import os
import serial
import sys
import motor # this is the motor library

global motorSer

# enter the position EleksMaker is mounted
motorSer = "/dev/ttyUSB0"


if __name__ == "__main__": 

    # define the motor class
    mot = motor.Motor(motorSer)

    # open the serial and test connection
    mot.motorOpen()

    # set current motor position as orginal point
    mot.setOrigin()

    # set the step length to 2cm
    mot.redefineStep(2)

    # let the stage move to coordinate (4,4).
    # The program will inform when the movement is finished
    mot.takeCor(4,4)

    # return the current position of the stage
    mot.returnPos()

    # close the serial
    mot.motorClose()
