#!/opt/rh/python27/root/usr/bin/python
import time
import os
import sys
import subprocess


global usrFile
usrFile = "../../user"

global timeSpacing
timeSpacing = 1.0	#seconds to wait between commands to Omega

global timeOut
timeOut = 4.0		#seconds to wait for timeout of commands

def getUserFileDirectory():
	return usrFile

def getTimeSpacing():
	return timeSpacing

def getTimeOut():
	return timeOut



#class representing a single zone of the temperature controller
class ControlZone:
	def __init__(self, z = 0, e = False, s = 25, h = 10, l = 10):
		self.zone = z 				#zone number
		self.enable = e 			#boolean, enable zone = 1, disable zone = 0
		self.setpoint = s 			#temperature setpoint for zone when enabled
		self.ha = h 				#alarm at "high alarm", 'ha' degrees above setpoint
		self.la = l 				#alarm at "low alarm", 'la' degrees below setpoint
		self.changed = False		#marks if the zone has recently had a changed parameter, 0 for false 1 for true
		self.enableChanged = True

	def printZone(self):
		print "-----------------------"
		print "- zone: " + str(self.zone) + " -"
		print "- enabled: " + str(self.enable) + " -"
		print "- setpoint: " + str(self.setpoint) + " -"
		print "- high alarm: " + str(self.ha) + " -"
		print "- low alarm: " + str(self.la) + " -"
		print "-----------------------"

	def __str__(self):
		output = "--------------------\n"
		output += "- zone: " + str(self.zone) + " -\n"
		output += "- enabled: " + str(self.enable) + " -\n"
		output += "- setpoint: " + str(self.setpoint) + " -\n"
		output += "- high alarm: " + str(self.ha) + " -\n"
		output += "- low alarm: " + str(self.la) + " -\n"
		output += "-----------------------\n"
		return output

	def sendParameters(self):

		print "deciding to send regular parameters on zone " + str(self.zone)

		try:
			#send setpoint
			val = subprocess.call([usrFile + "/ssp.py", str(self.zone), str(self.setpoint)], timeout = timeOut )
			time.sleep(timeSpacing)
			#send high alarm
			val = subprocess.call([usrFile + "/sha.py", str(self.zone), str(self.ha)], timeout = timeOut)
			time.sleep(timeSpacing)
			#send low alarm
			val = subprocess.call([usrFile + "/sla.py", str(self.zone),str(self.la)], timeout = timeOut)
			time.sleep(timeSpacing)
		except subprocess.TimeoutExpired:
			print "CALL() timed out, trying again"
			time.sleep(timeSpacing)
			self.sendParameters()

		print "SENT NEW PARAMETERS on zone " + str(self.zone)
		self.changed = False

	def setZone(self, z):
		self.zone = z

	def setEnable(self, e):
		self.enable = e

	def setSetpoint(self, s):
		if(s > 500): print "Warning, setting the setpoint above 500C"
		self.setpoint = s

	def setHA(self, h):
		self.ha = h

	def setLA(self, l):
		self.la = l

	def setChanged(self, c):
		self.changed = c

	def setEnableChanged(self, c):
		self.enableChanged = c

	def getZone(self):
		return self.zone

	def getEnable(self):
		return self.enable

	def getSetpoint(self):
		return self.setpoint

	def getHA(self):
		return self.ha

	def getLA(self):
		return self.la

	def hasChanged(self):
		return self.changed

	def hasEnableChanged(self):
		return self.enableChanged

	def getZoneTemp(self):
		try:
			process = subprocess.Popen([usrFile + '/rtm.py', str(self.zone)],stdin=subprocess.PIPE, stdout=subprocess.PIPE )
			out, err = process.communicate(timeout=timeOut)
		except subprocess.TimeoutExpired:
			print "Popen() timed out, trying again"
			process.kill()
			self.getZoneTemp()

		return out.split('\n')[0]
	






	
