''' This code measures and logs temperature from thermocouples, pressure from a Pfeiffer PK-251 gauge. 
The output files will be located in the logs folder. The logging program can be stopped with a keyboard 
interrupt, but will catch other errors and print them to console.

Hannah and John's edits to Eric's code 7/3/17

7/18: Evan deleted "getOffsets" function and just put in the indexing math in the measurement line
7/25: Hannah changed the indexing math to work with 4 CB37s.
'''

import u6
import time
import typeKthermocouple
import os
import pfeiffer
import pfeifferGauge
from thermocoupleCalibrations2 import rt_offsets
from muxChans import muxChans

# Structure: [[gauge channel, gauge type], ... ]
pgaugechannel = [[53,1],[80,0]]  # This is the channel that 'signal output' is plugged into.
# ch 53 is measuring the large tube manifold's pressure gauge.
# ch 80 is measuring the internal pressure


# These channels are for measuring cold junction temperature from each CB37. 
# List structure: calChannel[Xi][differential?]
# For Xi = X2 X3 X4 X5 and differential? True or False
calChannels = [[0,False],[48,False],[72,False]]
# Index number of calChannels is important.
# As of July 25th 2017, channels 48, 72 & 0 are measuring the temp of the Labjack.

# Channels for measurement.
# muxChans[channel][channel#, differential?, Xi]
# As of July 26th, this order is correct. Indices are commented at the right:
'''muxChans = [[52,0,3],[54,0,3],[55,0,3],[58,0,3], #0-3
[60,0,3],[62,0,3],[63,0,3],[65,0,3], #4-7
[66,0,3],[67,0,3],[64,0,3],[69,0,3], #8-11
[70,0,3],[73,0,4],[74,0,4],[75,0,4], #12-15
[76,0,4],[83,0,4],[84,0,4],[85,0,4], #16-19
[2,0,2],[3,0,2],[120,0,2],[121,0,2], #20-23
[96,1,5],[97,1,5],[98,1,5],[99,1,5], #24-27
[100,1,5],[101,1,5],[102,1,5],[103,1,5]]''' #28-31

# We have 4 CB37s in use, X2, X3, X4 & X5.

# Declare a labjack U6 object from the u6 module.
labJack = u6.U6()

time.sleep(1)

# This code will run indefinitely, it can be quit with a keyboard interrupt. (Ctrl C)
while True:
	if(int(time.strftime('%S')) % 3 == 0):
		try:
			# to collect current readout data on internal heaters, write to this file:
			# ivFile = open('./data/iv_data/ivLog%s.txt' % time.strftime('%y%m%d'),'a')
			# thermocouple data file:
			tempFile = open('./data/thermocouple_data/tcLog%s.txt' % time.strftime('%y%m%d'), 'a')
			# pressure log file:
			pressureFile = open('./data/pressure_data/pressureLog%s.txt' % time.strftime('%y%m%d'), 'a')
			# The cold junction temperature in celsius, compensating for the screw junction temperature.
			# We measure the cold junction on each CB37 separately to correct the offset.
			# Convert K to C 
			coldJunctionTemp = labJack.getTemperature() - 273.15
			coldJunctionVolts = typeKthermocouple.tempToVolts(coldJunctionTemp)
#			print "Cold Junction: " + str(coldJunctionTemp)
#			print "Cold Junction volts: " + str(coldJunctionVolts)
			
			# Create an empty list called calOffsets.
			calOffsets = []
			for calchan in calChannels:
				v = (labJack.getAIN(calchan[0], resolutionIndex = 9, gainIndex = 2, differential = calchan[1]))*1000
				t = typeKthermocouple.voltsToTemp(v)
				print "Temp measured from channel " + str(calchan) + " = " + str(t)
				calOffsets.append(abs(coldJunctionVolts - v))
				print calOffsets
				# This line used to say calOffsets.append (v - coldJunctionVolts)
			calOffsets.append(coldJunctionVolts) # no offset for X5 differential thermocouples

			# Create an empty list called temps.
			temps = []
			# The following for loop converts voltage measured by thermocoulpes to temp (in C).
			for tc in muxChans:
				channel = tc[0]
				isDifferential = tc[1]
				Xi = tc[2]
				# Temporarily ignore the following channels:
				if (channel == 54 or channel == 63):
					temps.append(str(34))
					continue

				# calOffsets[int(Xi) - 4] adds the offset calculated from calChannels
				v = calOffsets[int(Xi) - 2] + (labJack.getAIN(channel, resolutionIndex = 9, gainIndex = 2, differential=isDifferential))*1000 
				raw = (labJack.getAIN(channel, resolutionIndex = 9, gainIndex = 2, differential=isDifferential))*1000 
				T=typeKthermocouple.voltsToTemp(raw+calOffsets[int(Xi)-2])
				print '{0:.3f} mV on {1:d} on X{2:d}: {3:.2f} C'.format(raw,channel,int(Xi),T)
				# Convert voltage measured to temperature.
				# (rt_offsets[str(channel)] adds the calibrated offset for each individual thermocouple.  We set room temp = 20.5 C.
				temps.append('{0:.2f}'.format(T))


			# The following lines print out all the recorded temperatures and the date on the same line.  
			# The entry gets added to tempFile.			
			entry = (','.join(temps) + ',' + str(time.strftime("%m-%d-%y %H:%M:%S")) + '\n')
#			print ('Temp entry: '+ entry + '\n')
			print entry
			tempFile.write(entry)
						 
			pressures=[]
			# The following for loop measures and stores pressure data.
			for ch in pgaugechannel:
				channel = ch[0]
				gtype = ch[1]
				pvolt = labJack.getAIN(channel, resolutionIndex = 9, gainIndex = 0, differential = True)
				print channel, pvolt, "V before converting to pressure"
				pressures.append(str(pfeifferGauge.voltsToPressure(pvolt,gtype)))

			entry = (','.join(pressures) + ',' + str(time.strftime("%m-%d-%y %H:%M:%S")) + '\n')
			print ('Pressure entry: '+entry + '\n')
			pressureFile.write(entry)
			
			tempFile.close()
			pressureFile.close()
			time.sleep(1)

		except Exception as e:
			# NOTE: the 'pfeifferGauge.py' file sets voltage limits that constrain this script's ability to
			# operate when not at vacuum - adjust accordingly if such measurement is necessary
			# This will catch all exceptions and simply print them to console, allowing the program to indefinitely 
			#print e
			#pass
			raise

		finally:
			pass
