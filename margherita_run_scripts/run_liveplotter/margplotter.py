#Running assumptions:
#	-pull_data.sh script pulls in the data files you want to plot
# 	-these data files are specified in the correct format in the config file (argument 1)
#	-datafiles have a timestamp suffix and are of the format <prefix>160728.txt
#	-datafiles have data as such: float,float,float...,%m-%d-%y %H:%M:%S\n
#	-anything with a "P" as the first letter of the group name will be plotted with log scale




import numpy as np 
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
import matplotlib.dates as mdates
import matplotlib as mpl
from matplotlib.patches import Circle
import matplotlib.image as mpimg
from matplotlib.collections import PatchCollection
import sys
import os
import time
import subprocess
import math
import re
import Trace

#define global variables
global livePlotWindow
global liveTimeInterval
global liveMode
global httpLiveFileLocation
global httpTableFileLocation
global plotTimeStart
global plotTimeEnd
global plotDate
global xAxisTicks
global plotTimeFormat
global dataDateFormat
global pullScript
global prefferedImgType
global averageMode
global avNpoints
global schemPicPath
global schemDataPath
global makeSchemFig

#time window, in hours, for which to plot
#assumes that one wants the most recent data window
livePlotWindow = 1.50

#how many seconds to wait before pulling data
#from raspberry pi
liveTimeInterval = 5

#do you want to be in liveplotting mode?
#this continuously updates images on the
#psec webpage
liveMode = True

#will average over N data points for all traces
averageMode = False
avNpoints = 10

#if liveMode is false, this program will plot
#a given time interval from one date of data
#the next three variables give that time window
plotDate = ['181225']
plotTimeStart = "1:00:00"
plotTimeEnd = "12:00:00"

#time or date format of the ticks on the x axes of subplots
plotTimeFormat = "%H:%M"
#how many ticks to put on the x axis of each plot
xAxisTicks = 10

#format of the string date that appears in datafiles
dataDateFormat = "%m-%d-%y %H:%M:%S"

#the file path for the "pull data" script, assuming bash
pullScript = "../../data/liveplotter_data/pull_data.sh"

#location for which to save liveplotter figures 
#to be served on a webpage
httpLiveFileLocation = "/psec/web/psec/margdata/"
httpTableFileLocation = "/psec/web/psec/margdata/table_of_temperatures.html"

#if you want to make a color dot figure that
#overlays temps on a schematic "PNG" file, fill
#these info out
makeSchemFig = 0
#schemPicPath = "/local/data2/margherita/data/liveplotter_data/diagrams/marg1manifold_v4.png"
#schemDataPath = "/local/data2/margherita/data/liveplotter_data/diagrams/marg1manifold_v4_locations.txt"
schemPicPath = "/local/data2/margherita/data/liveplotter_data/diagrams/m2mani_schem_v2.png"
schemDataPath = "/local/data2/margherita/data/liveplotter_data/diagrams/m2manifold_v2_locations.txt"





#------------Data Loading Functions: START-----------#

#create an appropriately sized array of Trace objects
#based on a given configuration file, and datafiles which
#go with the names in the configuration file
def loadTraces(configFile):
	conf = open(configFile, 'r')
	fullContents = conf.read()
	conf.close()
	
	#split contents such that the structure is
	#in an array: [fileprefix\ndata,data,data...', 'fileprefix\ndata,data...']
	filechunks = fullContents.split('*')[1:]

	#-----append all traces from all files to one list

	#this list is the returned object
	traces = []

	#for each file in the filechunks list, 
	#create a list of traces and then append to the full list
	for chunk in filechunks:
		filetraces = initializeTraces(chunk, liveMode)
		if(filetraces == None): continue
		for x in filetraces:
			traces.append(x)
	
	return traces

def initializeTraces(chunk, live):


	#create a new "smaller" set of data based on the
	#specified data window
	windowData = []

	#find specified window, if we are in "liveMode"
	if(live):
		today = date.today()
		filesuffix = datetime.strftime(today, "%y%m%d")
		filesuffix += ".txt"
		_ = chunk.split('\n')
		dataFileName = _[0] + filesuffix

		#throw an error if the file does not exist
		if(os.path.isfile(dataFileName) == False):
			print "Sorry, could not find the filename: " + dataFileName
			print "Continuing without that data"
			return None

		#throw an error if the file has no lines
		f = open(dataFileName, 'r')
		linecount = f.readlines()
		f.close()
		if(len(linecount) == 0):
			print "There are no lines in the file: " + dataFileName + "!"
			print "Continuing without that file"
			return None

		filecontent = np.genfromtxt(dataFileName, delimiter=',', dtype=None, invalid_raise=False)
		print dataFileName

		#this catches a data file with 
		#only one entry in it. 
		if(filecontent.ndim == 0):
			#learn how to deal with this
			#later. It's wierd... 
			print "Datafile " + dataFileName + " has only one entry in it!"
			print "I don't know how to handle one entry (i know... silly)"
			print "Continuing without it"
			return None


		windowlength = timedelta(hours=livePlotWindow)
		endTime = datetime.strptime(filecontent[-1][-1], getCorrectDateForm(filecontent[-1][-1]))
		startTime = endTime - windowlength

		#is the data long enough yet? 
		#if not, just take all that exists
		firstTime = datetime.strptime(filecontent[0][-1], getCorrectDateForm(filecontent[0][-1]))
		if((endTime - firstTime) <= windowlength):
			windowData = filecontent
		else:
			i = 1
			#break when you have found the lower time bound
			while i < len(filecontent):
				currentTime = datetime.strptime(filecontent[-1*i][-1], getCorrectDateForm(filecontent[-1*i][-1]))
				if((endTime - currentTime) > windowlength):
					break
				else:
					windowData.append(filecontent[-1*i])
					i += 1
		
			#window data is backwards
			windowData = windowData[::-1]


	#find specified window, if you are not in liveMode
	#non-live mode takes in multiple files given in the global 
	#variable "plotDate". 
	else:
		filesuffix = [suf + ".txt" for suf in plotDate]
		_ = chunk.split('\n')
		dataFileName = [_[0] + suf for suf in filesuffix]

		#load data from multiple files
		#assumes in chronological order
		for nfile in range(len(dataFileName)):
			#throw an error if the file does not exist
			if(os.path.isfile(dataFileName[nfile]) == False):
				print "Sorry, could not find the filename: " + dataFileName[nfile]
				print "Continuing without that data"
				return None

			#throw an error if the file has no lines
			f = open(dataFileName[nfile], 'r')
			linecount = f.readlines()
			f.close()
			if(len(linecount) == 0):
				print "There are no lines in the file: " + dataFileName[nfile] + "!"
				print "Continuing without that file"
				return None


			filecontent = np.genfromtxt(dataFileName[nfile], delimiter=',', dtype=None, invalid_raise=False)


			plotStartForm = "%H:%M:%S"
			plotEndForm = "%H:%M:%S"
			if(len(plotTimeStart.split('.')) == 2):
				plotStartForm = plotStartForm + ".%f"
			if(len(plotTimeEnd.split('.')) == 2):
				plotEndForm = plotEndForm + ".%f"

			plotStartForm = "%y%m%d " + plotStartForm 
			plotEndForm = "%y%m%d "  + plotEndForm

			#the time frame of the data
			#changes depending on which file we are on
			#(if it contains a time endpoint)

			fileEnd = datetime.strptime(filecontent[-1][-1], getCorrectDateForm(filecontent[-1][-1]))
			fileStart = datetime.strptime(filecontent[0][-1], getCorrectDateForm(filecontent[0][-1]))

			#only one file
			if(len(dataFileName) == 1):
				startTime = datetime.strptime(plotDate[nfile] + " " + plotTimeStart, plotStartForm)
				endTime = datetime.strptime(plotDate[nfile] + " " + plotTimeEnd, plotEndForm)

			#on the first file
			elif(nfile == 0):
				startTime = datetime.strptime(plotDate[nfile] + " " + plotTimeStart, plotStartForm)
				endTime = fileEnd

			#on the last file
			elif(nfile == len(dataFileName) - 1):
				startTime = fileStart
				endTime = datetime.strptime(plotDate[nfile] + " " + plotTimeEnd, plotEndForm)

			#somewhere in the middle, use the entire
			#file content
			else:
				startTime = fileStart
				endTime = fileEnd

			#Make sure that the times exist in the current file
			bufferTime = timedelta(seconds=10)
			if(startTime > fileEnd):
				print "The time window specified does not exist in the requested datafile. ENDING PROGRAM (3)"
				sys.exit()
			elif(endTime < fileStart):	
				print "The time window specified does not exist in the requested datafile. ENDING PROGRAM (2)"
				sys.exit()

			#find the startTime in the file content
			for point in filecontent:
				curTime = datetime.strptime(point[-1], getCorrectDateForm(point[-1]))
				if(curTime >= startTime):
					if(curTime >= endTime):
						break
					windowData.append(point)



			#another breaking case, one never finds the specified times for the window
			if(len(windowData) == 0):
				print "The time window specified does not exist in the requested datafile. ENDING PROGRAM (1)"
				sys.exit()




	#FINALLY, the windowed data exists
	#We now can create a list of trace objects
	#each with their own description and data list

	#each trace gets the same timestamp data
	datatimes = [datetime.strptime(x[-1], getCorrectDateForm(x[-1])) for x in windowData]
	datatimes = np.array(datatimes)

	#_ contains extraneous elements at the beginning and end of the list
	#each element of _ is a trace to be plotted, comma delimited
	trList = []
	for trace in _[1:-1]:
		#ignore trace if commented out
		if(trace[0] == "#"):
			continue
		trElements = trace.split(',')
		trLabel = trElements[1][2:]
		trGroup = trElements[1][:2]
		trDesc = trElements[2]
		trFmt = trElements[3]
		trUnit = trElements[4]
		trData = [float(d[int(trElements[0])]) for d in windowData]
		trData = np.array(trData)
		trList.append(Trace.Trace(datatimes, trData, trLabel, trGroup, trDesc, trFmt, trUnit))

	return trList


#------------------------------Data Loading Functions: END------------------------------#


#------------------------------Plotting/Looping functions: Begin-----------------------#


#this function does the liveplotter loop
def liveLoop(config):
	while True:
		#if it is currently close to midnight, where 
		#filenames change their tag
		if(closeToMidnight()):
			#sleep for 1 minute while filenames change
			time.sleep(500)

		#pull the data
		#as of 9/1/17 Evan removed this line
		#because a separate program pulls data on 
		#a cycle for every live plotter
		#subprocess.call([pullScript])

		#generate/update traces: this knows about the live time window
		traces = loadTraces(config)


		#create schematic figure if optioned
		if(makeSchemFig):
			schematicFig = assembleSchematicFigure(traces, schemPicPath, schemDataPath)
			figname = schemPicPath.split('/')[-1]
			schematicFig.savefig("/psec/web/psec/margdata/"+figname, bbox_inches='tight')
			schematicFig.clf()
			plt.close()

		#create a figure to post
		print "Created the figure"
		liveFig = assembleFigure(traces)
		print "Creating the table"
		tabString = assembleTable(traces)
		del traces
		
		#post the figure
		liveFig.savefig(httpLiveFileLocation, bbox_inches='tight')

		liveFig.clf()
		plt.close()
		print "Figure memory deallocated"
		#post the table
		tabfile = open(httpTableFileLocation, 'w')
		tabfile.write(tabString)
		tabfile.close()
		#wait to give the system some time
		print "Sleeping a moment"
		time.sleep(liveTimeInterval)


#the function for non-live mode functionality
#it plots one plot, shows it, asks if you want to save it
#asks what the name and location of the file should be
def singlePlot(config):

	#generate trace objects
	traces = loadTraces(config)
	finalFig = assembleFigure(traces)
	finalFig.show()

	#ask user if they want to save the figure and where
	while True:
		answer = raw_input("Would you like to save this figure? (y/n)  > ")
		if(answer == 'y'):
			saveLocation = raw_input("What location/filename would you like to use? (include image extension) > ")
			finalFig.savefig(saveLocation, bbox_inches='tight')
			return
		elif(answer == 'n'):
			return
		else:
			print "Sorry, please type y/n to save or not save the figure"



#function assumes traces are loaded
#returns a figure object which is a figure
#of many subplots based on the configuration file and traces
def assembleFigure(traces):
	#sort the traces by zone/plotgroup
	sortedTraces = sortTraces(traces)

	#how many plots am I making?
	N = len(sortedTraces)

	#how many columns am I doing?
	#how many rows?
	C, R = chooseColRow(N)
	
	#----make the plots 

	fig, axes = plt.subplots(nrows = R, ncols = C, figsize=(25, 20))
	#fig, axes = plt.subplots(nrows = R, ncols = C, figsize=(10, 8))
	#special case of only one plot to make
	if(N == 1):
		axes = [axes]
	#make it more iteratable, print this object if you are interested
	else:
		axes = axes.reshape(-1)
	if(N > len(axes)):
		print "Error occured in attempting to plot using " + str(N) + " plots and " + str(R) + " rows and " + str(C) + "columns."
		sys.exit()

	#delete the unused subplots, because subplot creates more than needed
	extraNumber = len(axes) - N
	if(extraNumber > 0):
		for i in range(-1*extraNumber, 0):
			fig.delaxes(axes[i])

	currentGroup = ""   #for the plot title

	#go through all plot groups and match to axes
	for p in range(len(sortedTraces)):
		for tr in sortedTraces[p]:
			if(averageMode == True):
				times, data = tr.averageData(avNpoints)
				axes[p].plot(times, data, tr.getFmt(), label=tr.getLabel())
			else:
				axes[p].plot(tr.getTimes(), tr.getData(), tr.getFmt(), label=tr.getLabel())

		#get a trace which represents the zone's general properties
		traceRep = getLongestTrace(sortedTraces[p])


		
		#find trace with the largest data range
		#this is used to fix the "no ticks" problem
		#on a log plot
		absmaxrange = 0
		maxrange = None
		for tr in sortedTraces[p]:
			r = tr.getDataRange()
			absr = abs(r[0] - r[1])
			if(absr > absmaxrange):
				absmaxrange = absr
				maxrange = r

		if(maxrange is None):
			maxrange = [0, 0]

		#format the current plot group plot
		currentGroup = traceRep.getGroup()
		currentDate = datetime.strftime(traceRep.getTimes()[-1], "%m/%d/%y")

		#basic plot formatting
		axes[p].set_title(currentGroup + ";" + currentDate, fontsize=20)
		axes[p].get_yaxis().set_tick_params(labelsize=20, length=20, width=2, which='major')
		axes[p].get_xaxis().set_tick_params(labelsize=17, length=20, width=2, which='major')
		axes[p].get_xaxis().set_tick_params(length=10, width=2, which='minor')
		axes[p].get_yaxis().set_tick_params(length=10, width=2, which='minor')
		axes[p].set_ylabel(traceRep.getUnit(), fontsize=23)
		minorLocator = AutoMinorLocator()
		axes[p].get_yaxis().set_minor_locator(minorLocator)
		axes[p].get_yaxis().set_ticks_position("right")
		axes[p].get_yaxis().set_label_position("right")
		axes[p].grid(b=True, which='major', color='k', linestyle='--', alpha=0.75)
		axes[p].grid(b=True, which='minor', color='pink', linestyle='--', alpha=0.75)
		axes[p].legend(loc='lower left')

		#trigger for log scale on pressures
		if(currentGroup[0] == 'P'):
			axes[p].set_yscale('log')
			axes[p].grid(b=True, which='minor', color='k', linestyle='--', alpha=0.5)

			#this checks if the range of data is less than one unit
			#in the lowest exponential of the log scale
			if(np.log10(absmaxrange) < np.log10(min(maxrange))):
				axes[p].set_yscale('linear')

		if(currentGroup[0] == 'L'):
			axes[p].set_yscale('log')
			axes[p].set_ylim([3e-10, 1e-7])
			axes[p].grid(b=True, which='minor', color='k', linestyle='--', alpha=0.5)
			#this checks if the range of data is less than one unit
			#in the lowest exponential of the log scale
			if(np.log10(absmaxrange) < np.log10(min(maxrange))):
				axes[p].set_yscale('linear')



		#change the format and number of ticks to be used on the x axis
		#number of ticks in a global variable
		axes[p].xaxis.set_major_formatter(mdates.DateFormatter(plotTimeFormat))
		deltaMins = traceRep.getTickInterval(xAxisTicks)
		axes[p].xaxis.set_major_locator(mdates.MinuteLocator(interval=deltaMins))
		axes[p].set_xlim(traceRep.getTimeLimits())	

	return fig


def assembleSchematicFigure(traces, schemPic, schemData):
	#sort the traces by zone/plotgroup
	sortedTraces = sortTraces(traces)


	#get the schematic bare loaded
	img = mpimg.imread(schemPic)

	#get the pixel location data loaded
	data = np.genfromtxt(schemData, delimiter=' ', dtype=str)
	chan = list(data[:,0]) #channel numbers, the first part of config trace names
	x = data[:,1]
	x = [int(_) for _ in x]
	y = data[:,2]
	y = [int(_) for _ in y]


	#create a figure to post
	fig, ax = plt.subplots(figsize=(15,15))
	ax.set_aspect('equal')
	ax.imshow(img)

	#make a color map for temperatures
	maxT = 350 #Centigrade
	minT = 15
	cmap = plt.cm.jet
	cmaplist = [cmap(i) for i in range(cmap.N)]
	cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)
	bounds = range(minT, maxT)
	norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

	#lists of circles ("patches") and colors
	colors = []
	patches = []

	#set cirlce size based on dimensions of image
	ymax = abs(max(ax.get_ylim()))
	xmax = abs(max(ax.get_xlim()))
	img_area = xmax*ymax
	relative_circle_area = 5128*3091/(np.pi*70*70)
	this_circle_area = img_area/relative_circle_area
	circle_rad = int(np.sqrt(this_circle_area)/(0.5*np.pi))
	for grp in sortedTraces:
		for tr in grp:
			#if its not a temperature, get outa here
			if(tr.getUnit() != 'C'):
				continue

			#get the integer channel number
			#here is where the assumption that 
			#in the config file, the first part of the
			#label is the channel number, and anything after
			#is separated by a '-' character
			chnum = tr.getLabel().split('-')[0]

			#if this channel exists in the schemFig data file
			#if this channel exists in the schemFig data file
			#make a patch 
			if(chnum in chan):
				idx = chan.index(chnum) #index of the channel in the x,y data
				patches.append(Circle((x[idx], y[idx]), circle_rad))

				#annotate circle with the temperature
				temperature = tr.getMostRecentDataPoint()
				ax.annotate(str(int(float(temperature))), (x[idx], y[idx]), color='k', weight='bold', fontsize=11, ha='center', va='center')

				#later, get the jet color corresponding to that temp
				colors.append(temperature)
	
	p = PatchCollection(patches, cmap=cmap, norm=norm)
	p.set_array(np.array(colors)) #sets the colors of each patch in order
	ax.add_collection(p)
	ax.set_title("Last updated " + str(datetime.strftime(datetime.now(), "%m-%d-%y %H:%M:%S")), fontsize=17)
	return fig			





#assembles a text string to be written to an 
#html page. It is the table of temperatures and data values
#for quick display of numerical measurements
def assembleTable(traces):
	#header of html file
	header = "<!DOCTYPE HTML PUBLIC\"-//W3C//DTD HTML 4.01//EN\"\"http://www.w3.org/TR/html4/strict.dtd\"><HTML><HEAD>"
	tableStyle = "<HEAD><style>table {font-family: arial, sans-serif;border-collapse: collapse;width: 100%;}td, th {border: 1px solid #dddddd;text-align: left;padding: 8px;}tr:nth-child(even) {background-color: #dddddd;}</style><HEAD><BODY>"
	table = "<table>"
	headRow = "<tr><th>Name</th><th>Description</th><th>Value (now)</th><th>-5 min</th><th>-10 min</th><th>-15 min</th></tr>"

	tableRows = ""
	#sort traces for a sorted table
	sortedTraces = sortTraces(traces)
	for grp in sortedTraces:
		for tr in grp:
			#get data values from 5, 10, and 15
			#minutes ago
			dataNow = tr.getDataFromPast(0)
			data5 = tr.getDataFromPast(5)
			data10 = tr.getDataFromPast(10)
			data15 = tr.getDataFromPast(15)

			#skip pressures
			if(tr.getGroup()[0] == 'P'):
				continue

			#form a single row out of strings
			row_o = "<tr>"
			row_c = "</tr>"
			closeopen = "</td><td>"
			rowstring = row_o
			rowstring += "<td>"
			rowstring += tr.getGroup() + tr.getLabel()
			rowstring += closeopen
			rowstring += tr.getDesc()
			rowstring += closeopen
			rowstring += str(round(dataNow, 2))
			rowstring += closeopen
			rowstring += str(round(data5, 2))
			rowstring += closeopen
			rowstring += str(round(data10, 2))
			rowstring += closeopen
			rowstring += str(round(data15, 2))
			rowstring += "</td>"
			rowstring += row_c
			rowstring += "\n"
			tableRows += rowstring

	htmlDoc = header + tableStyle + table + headRow + tableRows + "</table>" + "</BODY>" + "</HTML>"
	return htmlDoc



	sys.exit()

#takes already created traces and
#separates them by zone, returning a list of lists
#this isn't the most efficient, but only order n 
def sortTraces(traces):
	#list of strings of plotgroups
	groupStrings = []
	#get all zone names
	for _ in traces:
		groupStrings.append(_.getGroup())

	#remove duplicates in the list, fastest way in python, O(1)
	seen = set()
	seen_add = seen.add
	groupStrings = [x for x in groupStrings if not (x in seen or seen_add(x))]
	
	sortedTraces = []
	for z in groupStrings:
		templist = []
		for t in traces:
			if(t.getGroup() == z):
				templist.append(t)
		sortedTraces.append(templist)

	return sortedTraces


#this is a funny function which chooses
#how to lay out all of the plots onto one PNG
#returns (column, row)
def chooseColRow(N):
	#this versions restrictions:
		#--have two columns at least
		#--populate with infinite rows

	if N == 0:
		print "Somehow, you got here with NO PLOT GROUPs. Check configuration file!"
		sys.exit()

	elif N == 1:
		return (1, 1)

	elif N == 2:
		return (1, 2)

	elif N > 2:
		col = 2
		row = math.ceil(N/2.0)
		return (int(col), int(row))

	else:
		print "How did this happen?"
		return (None, None)

def hoursToMin(hours):
	return hours*60.0


#------------------------------Auxhillary functions: begin-----------------------#

#check if it is close to midnight
#this checks both before and after midnight
def closeToMidnight():
	now = datetime.now()
	today = date.today()
	dateStr = datetime.strftime(today, "%m-%d-%y")
	bufferTime = timedelta(seconds=30)
	midnight = datetime.strptime(dateStr + " 00:00:00", "%m-%d-%y %H:%M:%S")
	beforeMidnight = datetime.strptime(dateStr + " 23:59:59", "%m-%d-%y %H:%M:%S")
	if(now > (beforeMidnight - bufferTime)):
		return True
	elif(now < (midnight + bufferTime)):
		return True
	else:
		return False


#return the longest trace 
#i.e. the one with the most data points
#in a list of traces
def getLongestTrace(traces):
	#check to see if there is more than
	#one trace in the list
	if(isinstance(traces, list)):
		longest = traces[0]
		if(len(traces) == 1):
			return traces[0]
		for tr in traces:
			if(tr.getLength() > longest.getLength()):
				longest = tr
		return longest
			
	else:
		return traces

#checks if the datestring has a decimal
#point in it, and if so, returns the propper
#strptime date format
def getCorrectDateForm(datestring):
	if(len(datestring.split('.')) == 2):
		return dataDateFormat+".%f"
	else:
		return dataDateFormat


#------------------------------Auxhillary functions: end-----------------------#


if __name__ == "__main__":
	
	if(len(sys.argv) != 3 and liveMode):
		print "Please use the following arguments:"
		print "python margplotter.py <configfile>.txt <margdata_filename>.png"
		sys.exit()
	elif(not liveMode and len(sys.argv) != 2):
		print "Please use the following arguments:"
		print "python margplotter.py <configfile>.txt"
		sys.exit()

	if(liveMode):
		print "You are entering into LIVE mode"
		httpLiveFileLocation += sys.argv[2]
		liveLoop(sys.argv[1])
	else:
		print "You are entering into SINGLE PLOT mode"
		singlePlot(sys.argv[1])


