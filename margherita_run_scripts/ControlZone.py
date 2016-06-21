#!/usr/bin/python


#class representing a single zone of the temperature controller
class ControlZone():
	def __init__(self, z = 0, e = 0, s = 25, h = 10, l = 10):
		self.zone = z 				#zone number
		self.enable = e 			#boolean, enable zone = 1, disable zone = 0
		self.setpoint = s 			#temperature setpoint for zone when enabled
		self.ha = h 				#alarm at "high alarm", 'ha' degrees above setpoint
		self.la = l 				#alarm at "low alarm", 'la' degrees below setpoint
		self.changed = 0			#marks if the zone has recently had a changed parameter, 0 for false 1 for true

	def printZone(self):
		print "-----------------------"
		print "- zone: " + str(self.zone) + " -"
		print "- enabled: " + str(self.enable) + " -"
		print "- setpoint: " + str(self.setpoint) + " -"
		print "- high alarm: " + str(self.ha) + " -"
		print "- low alarm: " + str(self.la) + " -"
		print "-----------------------"

	def setEnable(self, e):
		if(e != 0 or e != 1): 
			print "Please give the enable either 1 or 0"
			return

		self.enable = e

	def setSetpoint(self, s):
		if(s > 500): print "Warning, setting the setpoint above 500C"
		self.setpoint = s

	def setHA(self, h):
		if(h <= self.setpoint): 
			print "Error: trying to set the high alarm less than or equal to the setpoint"
			return
		self.ha = h

	def setLA(self, l):
		if(l >= self.setpoint):
			print "Error: trying to set the low alarm greater than or equal to the setpoint"
			return
		self.la = l


	
