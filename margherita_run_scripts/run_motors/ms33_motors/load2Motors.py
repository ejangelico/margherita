import serial
import os
import sys

import Motor
import TwoMotors

global motorSerX
global motorSerY
global motorIdX
global motorIdY


motorSerX = "/dev/ttyUSB1"
motorSerY = "/dev/ttyUSB2"
motorIdX = 1
motorIdY = 1




def loadMotors():
	motx = Motor.Motor(motorSerX, motorIdX)
	moty = Motor.Motor(motorSerY, motorIdY)
	motors = TwoMotors.TwoMotors(motx, moty)
	motors.openMotors()
	print str(motors)
	return motors


def main():
	mots = loadMotors()
	for i in range(100):
		mots.mr(-4, 0)
		mots.mr(4,0)

	mots.closeMotors()
	print "DONE"

#main()
