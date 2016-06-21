#!/usr/bin/python
import os
import sys
import subprocess

#class representing a single zone of the temperature controller
class ControlZone:
	def __init__(self, z = 0, e = False, s = 25, h = 10, l = 10):
		self.zone = z 				#zone number
		self.enable = e 			#boolean, enable zone = 1, disable zone = 0
		self.setpoint = s 			#temperature setpoint for zone when enabled
		self.ha = h 				#alarm at "high alarm", 'ha' degrees above setpoint
		self.la = l 				#alarm at "low alarm", 'la' degrees below setpoint
		self.changed = False		#marks if the zone has recently had a changed parameter, 0 for false 1 for true

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

	def getZoneTemp(self):
		process = subprocess.Popen(['./rtm.py', str(chNum)], stdout=subprocess.PIPE)
		out, err = process.communicate()
		outfile.write(str(out.split('\n')[0]))




	
