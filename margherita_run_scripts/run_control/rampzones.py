import sys
import time
import os
from datetime import datetime


class Zone:
	def __init__(self, z, r, T, dT, timestep):
		self.zone = z
		self.rampEnable = bool(r)
		self.endTemp = T 				#endpoint temperature for when to stop ramping
		self.dT = dT					#temperature increment at each timestep
		self.timestep = timestep 		#converted to seconds immediately
		self.lastChange = None 			#is a timestep of when the setpoint was most recently updated


	def getZone(self):
		return self.zone

	def getRampEnable(self):
		return self.rampEnable

	def getEndTemp(self):
		return self.endTemp

	def getdT(self):
		return self.dT

	def getTimestep(self):
		return self.timestep

	def getLastChange(self):
		return self.lastChange

	def setLastChange(self, t):
		self.lastChange = t

	def setRampEnable(self, e):
		self.rampEnable = e

	def setEndTemp(self, s):
		self.endTemp = s

	def setdT(self, t):
		self.dT = t

	def setTimestep(self, ts):
		self.timestep = ts





def minToSec(m):
	return m*60.0

#safely and cleanly rewrites a new setpoints file
#making only one change so that the zoneController program
#does not get confused
def writeNewSetFile(linelist,setfile):
	tmptag = ".tmp"
	newfile = open(setfile+tmptag, 'w')
	for l in linelist:
		newfile.write(l)

	newfile.close()
	os.rename(setfile+tmptag, setfile)



#check if a change is "due" for being applied
#then increment the setpoints in the setfile
def applyChanges(zoneArray, setfile):

	#pull in the setfile (which holds setpoint information)
	ctrlFile = open(setfile, 'r')
	ctrlLines = ctrlFile.readlines()
	ctrlFile.close()

	#separate each line in setpoint file into accessible variables
	splitLinesArray = [x.split(',') for x in ctrlLines]

	print "***" + datetime.now().strftime("%y-%m-%d %H:%M:%S") + "***"
	for i in range(len(zoneArray)):

		#special case of setting for the first time
		if(zoneArray[i].getLastChange() == None):
			#"De-Nullify" the variable
			#Subtract timestep so that the changes
			#become made right away
			tstep = zoneArray[i].getTimestep()
			zoneArray[i].setLastChange(time.time() - tstep - 1)

		#if the zone is enabled, 
		#and if the time has passed and we are ready for a change
		#this line limits us to ONLY do temperature ramp-ups and not downs
		if(zoneArray[i].getRampEnable() and (time.time() - zoneArray[i].getLastChange()) >= zoneArray[i].getTimestep()):
			#disable the zone if you have reached the setpoint
			curSetPt = int(splitLinesArray[i][2])
			increment = zoneArray[i].getdT()
			if((curSetPt + increment) > zoneArray[i].getEndTemp()):
				zoneArray[i].setRampEnable(False)
				print "Zone " + str(zoneArray[i].getZone()) + " is DONE ramping"

			#otherwise, increment the setpoint
			else:
				splitLinesArray[i][2] = str(curSetPt + increment)
				zoneArray[i].setLastChange(time.time())
				print "Zone " + str(zoneArray[i].getZone()) + " has been INCREMENTED by " + str(zoneArray[i].getdT()) + "C"


	#rejoin the list with commas
	rejoinedList = []
	for x in splitLinesArray:
		rejoinedList.append(",".join(x))

	writeNewSetFile(rejoinedList,setfile)


#if a zone array exists, load all parameters from the paramsFile
def loadParams(zoneArray, pname):
	paramFile = open(pname, 'r')
	plines = paramFile.readlines()
	paramFile.close()


	if(len(zoneArray) != (len(plines) - 1)):
		print "Number of zones and Parameter File does not match!!!"
		return

	for i in range(len(zoneArray)):
		zpar = plines[i+1].split(',')
		timestep = minToSec(float(zpar[4]))

		zoneArray[i].setRampEnable(bool(zpar[1]))
		zoneArray[i].setEndTemp(int(zpar[2]))
		zoneArray[i].setdT(int(zpar[3]))
		zoneArray[i].setTimestep(timestep)



#return 1 if any zones are still enabled
#return 0 if all zones are disabled
def anyZonesEnabled(zoneArray):
	for x in zoneArray:
		if(x.getRampEnable()):
			return True 

	print "All zones are done ramping--"
	return False

def getSmallestTimeInterval(zoneArray):
	smallest = 10000000
	for x in zoneArray:
		if(smallest > x.getTimestep()):
			smallest = x.getTimestep()

	return smallest 

	

def main(argv):
	if(len(argv) != 2):
		print "Usage: python rampzones.py <rampParamsFile>.txt"
		return

	pfilename = argv[1]
	paramFile = open(pfilename, 'r')
	setfile = "setpoints.txt"
	paramLines = paramFile.readlines()
	paramFile.close()

	#initialize the zones
	#this "zone loading" is done repeatedly if the rampParams file is changed
	zoneArray = []
	for l in paramLines[1:]:
		zpar = l.split(',')
		timestep = minToSec(float(zpar[4]))
		zoneArray.append(Zone(int(zpar[0]),int(zpar[1]),int(zpar[2]),int(zpar[3]),timestep))

	#apply the first changes
	applyChanges(zoneArray, setfile)

	#least amount of time to wait until checking the time
	leastTimestep = getSmallestTimeInterval(zoneArray)

	#keep a check on when rampParams file is changed
	(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(pfilename)
	lastmod =  mtime
	
	try:
		while anyZonesEnabled(zoneArray):
			#sleep a bit
			#apply changes checks to see if each zone is "ready" for a temp increment
			#if they are, it applies the change
			#when all zones are done, they are disabled and this code exits
			time.sleep(leastTimestep)

			#if the params file has changed, load new parameters into zone array
			(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(pfilename)
			if (lastmod != mtime):
				print "PARAMETER FILE CHANGED: Loading new parameters-----------"
				loadParams(zoneArray, pfilename)
				lastmod = mtime

			applyChanges(zoneArray, setfile)
	except KeyboardInterrupt:
		print "Keyboard interrupt"


	







main(sys.argv)


