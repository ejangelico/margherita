import numpy as np 
import sys
from datetime import datetime, timedelta


class Trace:
	def __init__(self, timestamps, data, label, plotGroup, desc, fmt, unit):
		self.timestamps = timestamps
		self.data = data
		self.label = label
		self.plotGroup = plotGroup
		self.desc = desc
		self.fmt = fmt
		self.unit = unit

	#typecast the object to display
	#string info on its public variables
	def __str__(self):
		thestring = ""
		thestring += "----------\n"
		thestring += self.desc + "\n"
		thestring += "Plot Group: " + self.plotGroup + "\n"
		thestring += "Label: " + self.label + "\n"
		thestring += "Data length: " + str(len(self.data)) + "(d), " + str(len(self.timestamps)) + "(t)\n"
		thestring += "----------\n"
		return thestring


	def getGroup(self):
		return self.plotGroup

	def getUnit(self):
		return self.unit

	def getFmt(self):
		return self.fmt

	def getLabel(self):
		return self.label

	def getData(self):
		return self.data

	def getTimes(self):
		return self.timestamps

	def getDesc(self):
		return self.desc

	#return the amount of time that is 
	#logged in this dataset
	def getLength(self):
		start = self.timestamps[0]
		end = self.timestamps[-1]
		length = end - start
		sec = abs(self.timedelta_total_seconds(length))
		return sec


	#returns the first and last time in the trace
	def getTimeLimits(self):
		return [self.timestamps[0], self.timestamps[-1]]

	#finds the data point from "mins" minutes before
	#the final data point in timestamps
	def getDataFromPast(self, mins):
		#create a timedelta object
		past = timedelta(minutes=mins)

		mostRecent = self.timestamps[-1]
		key = mostRecent - past
		i = -1
		while i > -1*len(self.timestamps):
			if(self.timestamps[i] < key):
				return self.data[i]

			i -= 1

		print "Unable to find data from " + str(past) + " minutes ago, giving back the most recent data point"
		return self.data[-1]


	#calculates the interval between x axis ticks by fixing the absolute
	def getTickInterval(self, xticks):
		start = self.timestamps[0]
		end = self.timestamps[-1]
		window = end - start
		deltaMins = int(self.timedelta_total_seconds(window)/(60*xticks))
		if(deltaMins < 1):
			return 1
		else:
			return deltaMins
	
	#returns an averaged array
	def averageData(self, npoints):
		avdata = []
		avtimes = []
		
		#if the length of the data is not 
		#0 modulo npoints, cut off the beginning
		#of the data instead of the end
		beg = len(self.data) - (npoints * int(len(self.data)/npoints))

		tempav = []


		for i in range(beg):
			tempav.append(self.data[i])

		avdata.append(np.average(tempav))
		tempav = []
		avtimes.append(self.timestamps[beg])


		for i in range(beg, len(self.data)):
			if(i % npoints == 0):
				if(i == 0): continue
				#push the averaged data
				avdata.append(np.average(tempav))
				tempav = []
				avtimes.append(self.timestamps[i])
			tempav.append(self.data[i])

		return (avtimes, avdata)

	#------------------------------Auxhillary functions: begin-----------------------#

	#takes a timedelta and finds how many total seconds
	#it represents
	def timedelta_total_seconds(self,timedelta):
	    return (
	        timedelta.microseconds + 0.0 +
	        (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6


	#------------------------------Auxhillary functions: end-----------------------#
	
