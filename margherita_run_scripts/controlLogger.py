#!/usr/bin/python
import time
import os
import sys
import numpy as np
import ControlZone


#sets the zone parameters for each zone in the controller set
def setAllZoneParameters(setfile, zoneArray):
	lineStructure = np.genfromtxt(setfile, delimiter=',')
	if len(lineStructure) != len(zoneArray):
		print "ERROR: Number of zones/lines in parameter file has changed or is incorrect!"
		return

	#go through each line/zone and set the parameters
	#for each parameter, it checks if it is making any "changes"
	#if it is not making a change, it passes by, if it does, it makes the "change" flag
	for i in range(len(zoneArray)):
		if(int(lineStructure[i][0]) != zoneArray[i].getZone()):
			zoneArray[i].setZone(int(lineStructure[i][0]))
			zoneArray[i].setChanged(True)

		if(bool(lineStructure[i][1]) != zoneArray[i].getEnable()):
			zoneArray[i].setEnable(bool(lineStructure[i][1]))
			zoneArray[i].setChanged(True)
			
		if(int(lineStructure[i][2]) != zoneArray[i].getSetpoint()):
			zoneArray[i].setSetpoint(int(lineStructure[i][2]))
			zoneArray[i].setChanged(True)

		if(int(lineStructure[i][3]) != zoneArray[i].getHA()):
			zoneArray[i].setHA(int(lineStructure[i][3]))
			zoneArray[i].setChanged(True)

		if(int(lineStructure[i][4]) != zoneArray[i].getLA()):
			zoneArray[i].setLA(int(lineStructure[i][4]))
			zoneArray[i].setChanged(True)	

def sendModifiedParameters(zoneArray):
	#look at each zone and see if they have changed
	for i in range(len(zoneArray)):
		if(zoneArray[i].hasChanged()):
			zoneArray[i].sendParameters()




def logTemperatures(templogfile):
	outfile = open(templogfile,'a')
	output = []
	for x in zoneArray:
		output.append(x.getZoneTemp())


	print "Logged temps..."



def saveSetfileSnapshot(snapshotfile, zoneArray):
	try:
		outfile = open(snapshotfile, "a")
	except IOError:
		print "Could not open snapshot file"
		return

	outfile.write("********" + time.strftime("%y:%m:%d %H:%M:%S") + "*********")
	for x in zoneArray:
		outfile.write(str(x))

	outfile.close()

	



if __name__ == '__main__':

	setfile = "setpoints.txt"		#file to look in for setpoint configurations
	snapshotfile = "snapshots.txt" 	#file to save each change in the setpoint configuration
	templogfile = "controlrun0.txt" #file to log control TC's into

	#get the initial timestamp for file modification on the setfile
	(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(setfile)
	lastmod =  mtime

	#initialize an array of zones based on how many lines are in the set file
	with open(setfile) as f:
		for i, l in enumerate(f):
			pass
	NZones = i + 1
	zoneArray = [ControlZone.ControlZone() for _ in range(NZones)]


	#load the setfile for the first time
	#set all zone parameters for the first time
	setAllZoneParameters(setfile, zoneArray)

	#save a snapshot of the first configurations
	saveSetfileSnapshot(snapshotfile,zoneArray)

	#send these initial parameters
	sendModifiedParameters(zoneArray)

	
	#start logging and watching
	while True:
		#check if the setfile has been modified
		(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(setfile)
		if (lastmod != mtime):
			setAllZoneParameters(setfile,zoneArray)
			saveSetfileSnapshot(snapshotfile, zoneArray)
			sendModifiedParameters(zoneArray)
			lastmod = mtime

		logTemperatures(templogfile)
		time.sleep(3)

	


	