#!/opt/rh/python27/root/usr/bin/python
import time
import os
import sys
import subprocess
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
			zoneArray[i].setEnableChanged(True)
			
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
	for x in zoneArray:
		if(x.hasChanged()):
			#changed parameters
			x.sendParameters()


	#One must send all of the "enable" parameters
	#for each zone, because the enable zones controller command requires
	#all zones-to-be-enabled to be passed
	enChangeCount = 0
	for x in zoneArray:
		if(x.hasEnableChanged()):
			enChangeCount += 1
			#will set new enabled channels in a second, so reset to False
			x.setEnableChanged(False)

	if(enChangeCount > 0):
		enabledZones = findEnabledZones(zoneArray)
		sendEnabledZones(enabledZones)
		print "SENT Enabled Zones"



def findEnabledZones(zoneArray):
	zonesToBe = []
	for x in zoneArray:
		if(x.getEnable()):
			zonesToBe.append(x.getZone())

	#The Omega controller must have 1 zone active
	#at all times. Temporarily, we designate zone 3
	#to fill that role, as it has a broken relay
	#In the future, this should change to 
	#trigger the alarm relay, shutting all zones off
	if(len(zonesToBe) == 0):
		zonesToBe.append(3)

	return zonesToBe

def sendEnabledZones(zones):
	#the command for enabling zones requires one to give
	#all of the zones-to-be-enabled as an argument
	#any zones which are not passed to ./stczn.py are Disabled by default

	command = ["../user/stczn.py"]
	for z in zones:
		command.append(str(z))

	val = subprocess.call(command )

#a debugging function
def readEnabledZones():
	process = subprocess.Popen(['../user/rtczn.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE )
	out, err = process.communicate()
	print out



def logTemperatures(templogfile):
	outfile = open(templogfile,'a')
	output = []
	for x in zoneArray:
		output.append(x.getZoneTemp())
		time.sleep(0.2)
	outfile.write(','.join(output) + ',' + time.strftime("%m-%d-%y %H:%M:%S") + "\n")
	outfile.close()
	print "Logged temps..."



def saveSetfileSnapshot(snapshotfile, zoneArray):
	try:
		outfile = open(snapshotfile, "a")
	except IOError:
		print "Could not open snapshot file"
		return

	outfile.write("********" + time.strftime("%m-%d-%y %H:%M:%S") + "*********")
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
			time.sleep(0.3)

		logTemperatures(templogfile)
		time.sleep(0.3)

	


	
