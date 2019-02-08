#This program meant to act as a quick way to 
#enter python in interactive mode with a loaded
#motor to make manual changes


import os
import serial
import sys
import motor # this is the motor library

global motorSer

# enter the position EleksMaker is mounted
motorSer = "/dev/ttyUSB1"

# define the motor class
mot = motor.Motor(motorSer)

# open the serial and test connection
mot.motorOpen()
