from pylab import *
import numpy as numpy
from paramiko import *
import matplotlib.pyplot as plt 
import time
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from datetime import datetime
from subprocess import call
import csv



def main():
		timestep = 2 #seconds in between data acquisitions on raspberry pi
		datawindow = 2.0*60*60          #hours * 3600 = seconds
		nArray = int(datawindow/timestep)
		print "pulling from servers"

		call(["/local/data2/margherita/data/liveplotter_data/pull_data.sh"])
		print 'Server pulling-from complete.'
		tempfile = '/local/data2/margherita/data/liveplotter_data/temprun0.txt'
		tail_tempfile = '/local/data2/margherita/data/liveplotter_data/tail_temprun0.txt'
		#label data loading
		templabels_file = 'TC_index_es.txt'
		temp_table = '/local/data2/margherita/data/liveplotter_data/table_of_temperatures.php'
		temp_table_template = '/local/data2/margherita/data/liveplotter_data/es_example_table.php'
		templabels_array=numpy.genfromtxt(templabels_file, delimiter=',', dtype=None)
		tempstructure = genfromtxt(tail_tempfile, delimiter=',',dtype='float',
usecols=list(range(len(templabels_array[0,:]))), invalid_raise = False )

		controlfile = '/local/data2/margherita/data/control_data/controlrun0.txt'
		controlstructure = genfromtxt(controlfile, delimiter=',',dtype=None, invalid_raise = False)
		
		pressfile = '/local/data2/margherita/data/liveplotter_data/pressrun0.txt'
		pressstructure = genfromtxt(pressfile,delimiter=',',dtype=None, invalid_raise = False)

		formatter = DateFormatter('%H:%M')

		if(len(pressstructure) < nArray):
			nArray = len(pressstructure)
		nArrayControl = int(datawindow/8)   
		if(len(controlstructure) < nArrayControl):
			nArrayControl = len(controlstructure)
		#temperature data loading
		T = [[] for _ in range(len(tempstructure[0]) - 1)] #create an array T[number of channels][data point number]
		tdate = list(genfromtxt(tail_tempfile,delimiter=',',dtype=None,usecols=(-1),invalid_raise = False))
		for n in range(len(tempstructure) - nArray, len(tempstructure)):
			for i in range(len(tempstructure[0]) - 1):
				T[i].append(tempstructure[n][i])
			#tdate.append(tempstructure[n][-1])

		#control data loading
		C = [[] for _ in range(len(controlstructure[0]) - 1)]
		cdate = []
		for n in range(len(controlstructure) - nArrayControl, len(controlstructure)):
			for i in range(len(controlstructure[0])-1):
				C[i].append(controlstructure[n][i])
			cdate.append(controlstructure[n][-1])

		L=list(templabels_array[0,:])
		descriptions=list(templabels_array[1,:])
		
		template = open(temp_table_template, 'r')
		table_output = open(temp_table, 'w')
		for i in range(20):
			table_output.write(template.readline())
		table_output.write("""  <tr>
    <th class=\"tg-yw4l\" colspan=\"7\"> now = {0}</th>
  </tr>
""".format(tdate[-1]))
		for i in range(9):
			table_output.write(template.readline())
		for i in range(len(templabels_array[0,:])):
			fieldlist=[L[i],descriptions[i],tempstructure[-1,i],tempstructure[-1,i],tempstructure[-1,i],tempstructure[-1,i],L[i][1]]
			#table_output.write('  <tr>\n'+
#''.join('    <td class=\"tg-yw4l\">{0}</td>\n'.format(field) for field in fieldlist)+
#'  </tr>\n')
			table_output.write("""  <tr>
    <td class=\"tg-yw4l\">{0}</td>
    <td class=\"tg-yw4l\">{1}</td>
    <td class=\"tg-yw4l\">{2:8.2f}</td>
    <td class=\"tg-yw4l\">{3:8.2f}</td>
    <td class=\"tg-yw4l\">{4:8.2f}</td>
    <td class=\"tg-yw4l\">{5:8.2f}</td>
    <td class=\"tg-yw4l\">{6}</td>
  </tr>
""".format(*fieldlist))
		table_output.write('</table>\n</body>\n</html>\n')
		table_output.close()

		#pressure data loading
		P = [[] for _ in range(len(pressstructure[0]) - 1)]
		pdate = []
		for n in range(len(pressstructure) - nArray, len(pressstructure)):
			for i in range(len(pressstructure[0]) - 1):
				P[i].append(pressstructure[n][i])
			pdate.append(pressstructure[n][-1])


		#timediff = datetime.strptime("1-31-16 03:39:00","%m-%d-%y %H:%M:%S") - datetime.strptime("1-30-16 21:39:00","%m-%d-%y %H:%M:%S")
		pressstime = np.array([(datetime.strptime(pdate[i], "%m-%d-%y %H:%M:%S")) for i in range(len(pdate))])
		temptime = np.array([(datetime.strptime(tdate[i], "%m-%d-%y %H:%M:%S")) for i in range(len(tdate))])
		controltime = np.array([(datetime.strptime(cdate[i], "%m-%d-%y %H:%M:%S")) for i in range(len(cdate))])
		
		pfmts = ['r', 'k']
		zone1 = [20,17,9,5,6]	#a5, a6, b6, b8
		zone2 = [2,7]		#a2, b5
		zone4 = [14,13,19,12,18]	#b1, b2, b10, b11
		zone5 = [10,4,3,11,8]	#a3, a4, b9, b13, b7
		zone6 = [1,0,15]	#a0, a1, b3
		zone_marg = [16,21,22,23,24,25,26,27,28]
		QE = [21]
		tfmts = ['g','b','y','m','c','k','r','go','bo']
	#	tlabels = ['a0','a1','a2','a3','a4','a5','a6','b5','b6','b7','b8','b9','b13','pump','b1','b2','b3','m1','b10','b11','m2','m3','m4','m5','m6','m7','m8','m9']
		plabels = ['Margherita', 'Manifold']
		controlL = ['Z1T2','Z2T2','zone 3 off','Z4T6','Z5T4','Z6T4']

		fmtcount = 0 #counts the number of fmt's we have iterated through
		#plot zone 1
		figure(1, figsize=(19,20))
		subplot(521)
		for i in zone1:
			plot(temptime, tempstructure[:,i], tfmts[fmtcount], label=L[i],markevery=50)
			fmtcount+=1
		yticks(arange(20.0, 300.0, 20))
		xticks(rotation=70)
		plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
		gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
		gca().yaxis.set_ticks_position("right")
		grid(b=True, which='major', color='pink', linestyle='--')
		xlabel('timestamp')
		ylim([0, 300])
		title('Zone 1, Cs Source')
		ylabel('temperature (C)')
		legend(loc=3)


		fmtcount = 0 #counts the number of fmt's we have iterated through
		#plot zone 2
		figure(1, figsize=(19,20))
		subplot(522)
		for i in zone2:
			plot(temptime, tempstructure[:,i], tfmts[fmtcount], label=L[i],markevery=50)
			fmtcount+=1
		yticks(arange(20.0, 300.0, 20))
		xticks(rotation=70)
		plt.gcf().axes[1].xaxis.set_major_formatter(formatter)
		gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
		gca().yaxis.set_ticks_position("right")
		grid(b=True, which='major', color='pink', linestyle='--')
		xlabel('timestamp')
		ylim([0, 300])
		title('Zone 2, Sniffer Line')
		ylabel('temperature (C)')
		legend(loc=3)


		fmtcount = 0 #counts the number of fmt's we have iterated through
		#plot zone 4
		figure(1, figsize=(19,20))
		subplot(523)
		for i in zone4:
			plot(temptime, tempstructure[:,i], tfmts[fmtcount], label=L[i],markevery=50)
			fmtcount+=1
		yticks(arange(20.0, 300.0, 20))
		xticks(rotation=70)
		plt.gcf().axes[2].xaxis.set_major_formatter(formatter)
		gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
		gca().yaxis.set_ticks_position("right")
		grid(b=True, which='major', color='pink', linestyle='--')
		xlabel('timestamp')
		ylim([0, 300])
		title('Zone 4, Pump Manifold')
		ylabel('temperature (C)')
		legend(loc=3)


		fmtcount = 0 #counts the number of fmt's we have iterated through
		#plot zone 5
		figure(1, figsize=(19,20))
		subplot(524)
		for i in zone5:
			plot(temptime, tempstructure[:,i], tfmts[fmtcount], label=L[i],markevery=50)
			fmtcount+=1
		yticks(arange(20.0, 300.0, 20))
		xticks(rotation=70)
		plt.gcf().axes[3].xaxis.set_major_formatter(formatter)
		gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
		gca().yaxis.set_ticks_position("right")
		grid(b=True, which='major', color='pink', linestyle='--')
		xlabel('timestamp')
		ylim([0, 300])
		title('Zone 5, Cs Upstream')
		ylabel('temperature (C)')
		legend(loc=3)


		fmtcount = 0 #counts the number of fmt's we have iterated through
		#plot zone 6
		figure(1, figsize=(19,20))
		subplot(525)
		for i in zone6:
			plot(temptime, tempstructure[:,i], tfmts[fmtcount], label=L[i],markevery=50)
			fmtcount+=1
		yticks(arange(20.0, 300.0, 20))
		xticks(rotation=70)
		plt.gcf().axes[4].xaxis.set_major_formatter(formatter)
		gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
		gca().yaxis.set_ticks_position("right")
		grid(b=True, which='major', color='pink', linestyle='--')
		xlabel('timestamp')
		ylim([0, 300])
		title('Zone 6, Cs Downstream')
		ylabel('temperature (C)')
		legend(loc=3)

		fmtcount = 0
		#plot marg
		figure(1, figsize=(19,20))
		subplot(526)
		for i in zone_marg:	
			plot(temptime, tempstructure[:,i], tfmts[fmtcount], label=L[i], markevery=50)
			fmtcount+=1
		yticks(arange(20.0, 300.0, 20))
		xticks(rotation=70)
		plt.gcf().axes[5].xaxis.set_major_formatter(formatter)
		gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
		gca().yaxis.set_ticks_position("right")
		grid(b=True, which='major', color='pink', linestyle='--')
		xlabel('timestamp')
		ylim([0, 200])
		title('Marg')
		ylabel('temperature (C)')
		legend(loc=3)


	#	fmtcount = 0
	#	#plot control 
	#	figure(1, figsize=(19,20))
	#	subplot(527)
	#	for i in range(6): #6 control zones
	#		plot(controltime, C[i], tfmts[fmtcount], label=controlL[i])
	#		fmtcount+=1
	#	yticks(arange(20.0, 300.0, 20))
	#	xticks(rotation=70)
	#	plt.gcf().axes[6].xaxis.set_major_formatter(formatter)
	#	gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
	#	gca().yaxis.set_ticks_position("right")
	#	grid(b=True, which='major', color='pink', linestyle='--')
	#	xlabel('timestamp')
	#	ylim([0, 200])
	#	title('Control TC')
	#	ylabel('temperature (C)')
	#	legend(loc=3)

	#	fmtcount = 0
		#plot QE
	#	figure (1, figsize = (19,20))
	#	subplot(528)
	#	for i in QE:
	#		plot(temptime, tempstructure[:,i], tfmts[fmtcount], markevery = 50)
	#		fmtcount += 1
	#	yticks(arange(0.0, 300, 20))
	#	xticks(rotation=70)
	#	plt.gcf().axes[7].xaxis.set_major_formatter(formatter)
	#	gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
	#	gca().yaxis.set_ticks_position("right")
	#	grid(b=True, which = 'major', color = 'pink', linestyle = '--')
	#	xlabel('timestamp')
	#	ylabel('voltage')
	#	title('QE voltage')
		#plot pressure
		#figure(1, figsize =(19,20))
		#subplot(427)
		#yscale('log')
		#xlabel('time')
		#ylabel('pressure (torr)')
		#grid(b=True, which='major', color='b', linestyle='-')
		#grid(b=True, which='minor', color='black', linestyle='--')
		#for i in range(len(P)):
			#plot(pressstime, P[i], pfmts[i], label=plabels[i])
		#legend(loc=3)	
		#xticks(rotation=70)
		#title("Pressures")
		#gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
		
		plt.tight_layout()

		savefig('/local/data2/margherita/data/liveplotter_data/plots.png',bbox_inches='tight')
		close()
		print "pushing to server"
		call(["/local/data2/margherita/data/liveplotter_data/push_pic.sh"])	
		time.sleep(10)
		return 

while True:
	if(int(time.strftime('%S')) % 15 != 0):
		main()
	else:
		time.sleep(0.1)
