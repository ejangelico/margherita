#!/usr/bin/python
import time
import os
import numpy as np
import ControlZone



def updatePoints(modtime):
	print "File was modified at " + str(time.ctime(modtime))
	return 

#sets the zone parameters for each zone in the controller set
def setAllZoneParameters(setfile, zoneArray):
	lineStructure = np.genfromtxt(setfile, delimiter=)

	

#(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(setfile)
#lastmod =  mtime

if __name__ == '__main__':
	setfile = "setpoints.txt"

	#initialize an array of zones based on how many lines are in the set file
	with open(setfile) as f:
		for i, l in enumerate(f):
			pass
	NZones = i + 1
	zoneArray = [ControlZone for _ in range(NZones)]


	#load the setfile for the first time
	#set all zone parameters for the first time
	setAllZoneParameters(setfile, zoneArray)

'''
while True:
	print "Checking for modification"
	(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(setfile)
	if (lastmod != mtime):
		updatePoints(mtime)
		lastmod = mtime

	time.sleep(1)
'''
	