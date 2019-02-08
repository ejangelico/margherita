import serial
import sys
import time

#this class is currently configured
#to accept and return all values in centimeters


class Motor:
	def __init__(self, port, mId):
		self.port = port 	#string specifying serial port, ex: "/dev/ttyUSB1"
		self.ser = None		#the serial port that will be opened and closed during operation
		self.isopen = False	#is the serial port open
		self.mId = str(mId)	#string integer specifying motor ID indicated by dial on motor
		self.pos = None		#current motor position
		self.step = None	#current step size of motor
		self.vel = None		
		self.upperBound = None	#boundary of absolute position which one will not move past
		self.lowerBound = None	#same but on the lower end

	def __str__(self):
		if(self.isopen):
			self.loadAttributes()
			st = "Motor ID: " + self.mId + "\n"
			st += "Port: " + self.port + "\n"
			st += "Position: " + self.pos + " cm\n"
			st += "Step: " + self.step + "\n"
			st += "Velocity: " + self.vel + " steps/s\n"
			st += "Is Open?: " + str(self.isopen) + "\n"
			return st
		else:
			print "Please open communications with the motor using motorOpen()"
			return "ERR"

	#sets the top speed in position mod
	#this also takes a default 100,000 steps/s
	def setVel(self,speed = 200000):
		if(self.isopen):
			cmdstr = "/" + self.mId + "V"
			if(speed < 0):
				print "Cannot set speed to negative value"
				return
			else:
				cmdstr += str(int(speed)) + "R"
				self.vel = str(int(speed))
				self.ser.flushInput()
				self.ser.write(cmdstr+"\r")
				self.ser.readline()
				return
		else:
			print "Please first open the serial communication before executing commands"
			return


	#redefines the current absolute step number
	#must be greater than 0
	#upper bound?
	def redefineAbsPosition(self, s):
		if(self.isopen):
			cmdstr = "/" + self.mId + "z"
			if(s < 0):
				print "Tried redefining absolute position to a negative number!"
				print "Keeping current abs position definition the same"
				return
			else:
				cmdstr += str(int(cmToStep(self.getStep(), s))) + "R"
				self.ser.flushInput()
				self.ser.write(cmdstr+"\r")
				self.ser.readline()
				return
		else:
			print "Please first open the serial communication before executing commands"
			return

	#move the motor to absolute step number "s"
	def ma(self, s):
		if(self.isopen):
			cmdstr = "/" + self.mId + "A"
			if(s < 0):
				print "Tried moving motor to a negative absolute position!"
				print "Keeping current abs position the same"
				return
			else:
				newpos = int(cmToStep(self.getStep(),s)) #in steps
				cmdstr += str(newpos) + "R"
				self.ser.flushInput()
				self.ser.write(cmdstr+"\r")
				self.ser.readline() #for some reason, this is needed to clear the input
				return
		else:
			print "Please first open the serial communication before executing commands"
			return

	#move the motor relative number of steps "s"
	def mr(self, s):
		if(self.isopen):
			relsteps = None
			if(s < 0):
				cmdstr = "/" + self.mId + "D"
				relsteps = -1*s
			elif(s > 0):
				cmdstr = "/" + self.mId + "P"
				relsteps = s
			else:
				#don't move at all
				return
			relsteps = int(cmToStep(self.getStep(),relsteps))
			cmdstr += str(relsteps) + "R"
			self.ser.flushInput()
			self.ser.write(cmdstr+"\r")
			self.ser.readline() #for some reason, this is needed to clear the input
			return

		else:
			print "Please first open the serial communication before executing commands"
			return

	#force terminates the current command
	def killCmd(self):
		#this time, try your hardest to connect no matter what
		if(self.isopen):
			cmdstr = "/" + self.mId + "TR"
			self.ser.flushInput()
			self.ser.write(cmdstr+"\r")
			return
		else:
			self.motorOpen()
			self.killCmd()











	#----------Serial and Attribute Functions-----------#

	#opens serial communication with motor
	def motorOpen(self):
		self.ser = serial.Serial(port=self.port, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
		b = self.ser.isOpen()
		if(b == True):
			self.isopen = True
			print "Motor communication port has been opened"
			#if this is the first time opening communications, 
			#initialize all of the class attributes
			if(self.vel == None):
				self.loadAttributes()
		else:
			self.isopen = False
			print "Could not open motor serial port, please check serial configuration"
			sys.exit()


	def motorClose(self):
		if(self.isopen == False):
			print "Motor communication port has been closed"
			return
		else:
			self.isopen = False
			self.ser.close()
			print "Motor communication port has been closed"

	
	def loadAttributes(self):
		if(self.isopen):
			self.loadStep()
			self.getVel()
			self.loadPos()
		else:
			print "Serial port is closed!"
			print "Not loading attributes----"

	def loadPos(self):
		cmdstr = "/" + self.mId + "?0"
		self.ser.flushInput()
		self.ser.write(cmdstr+"\r")
		rawpos = self.ser.readline()
		stepPos = float(rawpos[4:-4])
		self.pos = str(stepToCm(self.getStep(), stepPos))

	def loadStep(self):
		cmdstr = "/" + self.mId + "?6"
		self.ser.flushInput()
		self.ser.write(cmdstr+"\r")
		rawstep = self.ser.readline()
		self.step = rawstep[4:-4]

	def loadVel(self):
		self.setVel()

	#returns current position in cm
	#relative to the absolute 0
	def getPos(self):
		self.loadPos()
		return self.pos

	#step is a motor attribute variable
	#that determines how many "steps" per
	#revolution of the motor. Look at manual
	def getStep(self):
		if(self.step == None):
			self.loadStep()
		
		return self.step

	def getVel(self):
		if(self.vel == None):
			self.loadVel()

		return self.vel


	#returns the number of seconds to wait
	#if one wants to move "stepsToMove" number of steps
	#takes into account motor velocity/etc
	def getWaitTime(self, stepsToMove):
		#velocity is in steps/s
		v = self.getVel()
		return (stepsToMove/float(v))
		

####CONVERSIONS########

#Notes:
#(200)*(self.step) = number of steps per motor revolution
#(0.125 inches) per translation stage revolution
#gives (self.step)*200*(1/0.125) = steps/in
#gives (self.step)*200*(1/0.125)*(1/2.54) = steps/cm

def inchToStep(step, inches):
	return (1/0.125)*(200)*(step)*inches 	#returns a number of steps to turn


def cmToStep(step, cm):
	return (1/0.125)*(200)*(float(step))*(1/2.54)*(float(cm)) 	#returns a number of steps to turn

def stepToCm(stepsize, steps):
	return (0.125)*(1/200.0)*(1/float(stepsize))*(2.54)*float(steps)	#returns number of cm for a given steps

def stepToInch(stepsize, steps):
	return (0.125)*(1/200.0)*(1/float(stepsize))*float(steps)		#returns a number of in for a given steps
