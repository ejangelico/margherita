import serial
import sys
import os
import time


#this class is currently configured
#to accept and return all values in centimeters


class TwoMotors:
	def __init__(self, motx, moty):
		self.motx = motx
		self.moty = moty
		self.pos = None 	#position in [x, y]
		self.bounds = [[0,None],[0,None]]	#make sure that the motors dont exceed the abs pos bounds


	def __str__(self):
		(x, y) = self.getPos()
		st = "Motors at position: (" + str(round(x,2)) + "," + str(round(y,2)) + ")"
		return st

	def openMotors(self):
		self.motx.motorOpen()
		self.moty.motorOpen()

	def closeMotors(self):
		self.motx.motorClose()
		self.moty.motorClose()

	#move to absolute position value
	#on both motors (xy in cm)
	def ma(self, x, y):
		print "Starting absolute motion..."
		goodX, goodY = self.checkBounds(x, y, False)
		self.motx.ma(goodX)
		self.moty.ma(goodY)
		#wait until it has arrived to return
		arrivedx = False
		arrivedy = False
		while (arrivedx == False or arrivedy == False):
			curx = round(float(self.motx.getPos()),3)
			cury = round(float(self.moty.getPos()),3)
			time.sleep(0.3)	#arbitrary number of milliseconds
			newx = round(float(self.motx.getPos()),3)
			newy = round(float(self.moty.getPos()),3)
			if(curx == newx):
				arrivedx = True
			if(cury == newy):
				arrivedy = True

		#both have arrived
		print "Arrived at : " + str(self.getPos()) + " at time " + time.strftime('%H:%M:%S')
		return


	#move to relative position value
	#on both motors (xy in cm)
	def mr(self, x, y):
		print "Starting relative motion..."
		goodX, goodY = self.checkBounds(x, y, True)
		print "Good x = " + str(goodX)
		print "Good y = " + str(goodY)
		self.motx.mr(goodX)
		self.moty.mr(goodY)
		#wait until it has arrived to return
		arrivedx = False
		arrivedy = False
		while (arrivedx == False or arrivedy == False):
			curx = round(float(self.motx.getPos()),3)
			cury = round(float(self.moty.getPos()),3)
			time.sleep(0.3)	#arbitrary number of milliseconds
			newx = round(float(self.motx.getPos()),3)
			newy = round(float(self.moty.getPos()),3)
			if(curx == newx):
				arrivedx = True
			if(cury == newy):
				arrivedy = True

		#both have arrived
		print "Arrived at : " + str(self.getPos())
		return


	
	#move only the x motor
	def maX(self, x):
		print "Starting absolute motion..."
		goodX, temp = self.checkBounds(x, 0, False)
		self.motx.ma(goodX)
		arrivedx = False
		while (arrivedx == False):
			curx = round(float(self.motx.getPos()),3)
			time.sleep(0.3)	#arbitrary number of milliseconds
			newx = round(float(self.motx.getPos()),3)
			if(curx == newx):
				arrivedx = True

		print "Arrived at : " + str(self.getPos())
		return

	def mrX(self, x):
		print "Starting relative motion..."
		goodX, temp = self.checkBounds(x, 0, True)
		self.motx.mr(goodX)
		arrivedx = False
		while (arrivedx == False):
			curx = round(float(self.motx.getPos()),3)
			time.sleep(0.3)	#arbitrary number of milliseconds
			newx = round(float(self.motx.getPos()),3)
			if(curx == newx):
				arrivedx = True

		print "Arrived at : " + str(self.getPos())
		return


	#move only the y motor
	def maY(self, y):
		print "Starting absolute motion..."
		temp, goodY = self.checkBounds(0, y, False)
		self.moty.ma(goodY)
		arrivedy = False
		while (arrivedy == False):
			cury = round(float(self.moty.getPos()),3)
			time.sleep(0.3)	#arbitrary number of milliseconds
			newy = round(float(self.moty.getPos()),3)
			if(cury == newy):
				arrivedy = True

		print "Arrived at : " + str(self.getPos())
		return

	def mrY(self, y):
		print "Starting relative motion..."
		temp, goodY = self.checkBounds(0, y, True)
		self.moty.mr(goodY)
		arrivedy = False
		while (arrivedy == False):
			cury = round(float(self.moty.getPos()),3)
			time.sleep(0.3)	#arbitrary number of milliseconds
			newy = round(float(self.moty.getPos()),3)
			if(cury == newy):
				arrivedy = True

		print "Arrived at : " + str(self.getPos())
		return



	#set both motors to be zero at the current position
	def zeroHere(self):
		self.motx.redefineAbsPosition(0)
		self.moty.redefineAbsPosition(0)
		return


	#when motors are power cycled,
	#they set their position to be 0. 
	#Therefore, to move negative, one
	#needs to free up the absolute zero.
	def freeZero(self):
		self.motx.redefineAbsPosition(100)
		self.moty.redefineAbsPosition(100)
		self.setBounds(None, None)
		print "You have set the current position to be very high."
		print "Be cautious, as this could result in collision with walls"
		print "*You have also removed the boundaries"
		print "--Please re-zero yourself asap"
		return

	#gets position of both motors
	def getPos(self):
		x = self.motx.getPos()
		y = self.moty.getPos()
		self.pos = (float(x), float(y))
		return self.pos


	def printBounds(self):
		if(self.bounds[0][1] == None or self.bounds[1][1] == None):
			print "Bounds haven't been set yet!"
			return

		print "X: [" + str(self.bounds[0][0]) + ", " + str(self.bounds[0][1])
		print "Y: [" + str(self.bounds[1][0]) + ", " + str(self.bounds[1][1])
		return

	#sets the boundaries 
	#only sets upper bound, lower bound is 0
	def setBounds(self, xup, yup):
		#if you are setting the bounds to none
		if(xup == None and yup == None):
			self.bounds[0][1] = None
			self.bounds[1][1] = None
			return


		curx,cury = self.getPos()
		self.bounds[0][1] = None
		self.bounds[1][1] = None

		#special case when you are trying to set
		#bounds where the motor is currently not
		#within the boundaries
		if(float(curx) >= float(xup)):
			print "Cannot set bounds lower than current position"
			print "Setting bound to the current position"
			self.bounds[0][1] = curx
		if(float(cury) >= float(yup)):
			print "Cannot set bounds lower than current position"
			print "Setting bound to the current position"
			self.bounds[1][1] = cury
		
		#regular operation
		if(self.bounds[0][1] == None):
			self.bounds[0][1] = xup
		if(self.bounds[1][1] == None):
			self.bounds[1][1] = yup
		return

	#checks if a relative (or absolute)
	#movement will exceed bounds.
	#return the "acceptable" x and y motion
	#values in cm
	def checkBounds(self, x, y, rel):

		#if bounds havent been set, just 
		#let x and y be FREE
		if(self.bounds[0][1] == None or self.bounds[1][1] == None):
			return (x, y)

		acceptableX = None
		acceptableY = None
		xpos, ypos = self.getPos()
		#if this is relative motion
		#(note, rounding helps prevent
		#very small numbers like 5e-5 to result)
		if(rel == True):
			if(float(xpos) + float(x) > self.bounds[0][1]):
				acceptableX = round(self.bounds[0][1] - float(xpos),2)
			elif(float(xpos) + float(x) < self.bounds[0][0]):
				acceptableX = round(self.bounds[0][0] - float(xpos),2)
			else:
				acceptableX = x

			if(float(ypos) + float(y) > self.bounds[1][1]):
				print "First triggered y"
				acceptableY = round(self.bounds[0][1] - float(ypos),2)
			elif(float(ypos) + float(y) < self.bounds[1][0]):
				acceptableY = round(self.bounds[0][1] - float(ypos),2)
				print "second triggered y"
			else:
				print "Third triggered y"
				acceptableY = y

		#if this is absolute motion
		elif(rel == False):
			if(x > self.bounds[0][1]):
				acceptableX = self.bounds[0][1]
			elif(x < self.bounds[0][0]):
				acceptableX = self.bounds[0][0]
			else:
				acceptableX = x

			if(y > self.bounds[1][1]):
				acceptableY = self.bounds[1][1]
			elif(y < self.bounds[1][0]):
				acceptableY = self.bounds[1][0]
			else:
				acceptableY = y

		else:
			print "Please set REL to be true or false"
			sys.exit()

		if(acceptableX == None or acceptableY == None):
			print "Somehow we could not check your boundaries"
			sys.exit()

		else:
			if(y != acceptableY or x != acceptableX):
				print "Hit a software boundary--"

			return (acceptableX, acceptableY)
