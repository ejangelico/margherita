import sys
import numpy as np
import time
import os
import subprocess

#this program takes in an instruction
#of powers for delivering to an 
#"upper heater" hup and "lower heater" hlow
#using the "python hup_power.py" type commands

#the instructional datafile has an initial time of t=0
#and counts number of seconds past since this initial time. 
#it applies powers after some given number of seconds. 

#for generating the instruction file, see "make_power_instructional.py"


#checks the setfile and returns
#the parameter that says that 
#a heater is on or off
def get_setfile_enables(setfile):
	f = open(setfile, 'r')
	setfilelines = f.readlines()
	f.close()
	hup_enable = setfilelines[1].split(',')[1]
	hlow_enable = setfilelines[2].split(',')[1]
	return int(hup_enable), int(hlow_enable)

#runs the python commands
#to set a power on upper and lower
#heater
def set_powers(plow, pup, starttime):
    #kluge for setting powers close to 0
    #without disabling the controller
    if(pup == 0):
	    pup = 0.1
    if(plow == 0):
	    plow = 0.1
    
    #temporarily disabled
    print "Set powers at " + str(time.time() - starttime) + "s at " + str(pup) + " and " + str(plow)
    subprocess.call(['python', 'hup_power.py', str(pup)])
    subprocess.call(['python', 'hlow_power.py', str(plow)])




#the function that intiates and clocks
#all power input changes over ~24 hours
def run_automation(inst_data, setfile):
    tinit = time.time()
    print "Starting at " + str(tinit)
    lastt = None
    lastpup = None
    lastplow = None
    for i, d in enumerate(inst_data):
	plow = float(d[0])
	pup = float(d[1])
	thist = float(d[2])
	print d
	if(i == 0):
		lastt = tinit
		lastpup = pup
		lastplow = plow
		set_powers(plow, pup, tinit)
		continue

	while True:
		if((time.time() - tinit) >= thist):
		    #safety checks!!!!

		    #if both are the same, do nothing
		    if(lastpup == pup and lastplow == plow):
			    print 'equality fired'
			    lastt = time.time()
			    break

		    #if time since last change is less
		    #than 2 seconds, wait 2 seconds. 
		    #even if this truly is in the instructions
		    #2 seconds is never gonna mess with thermal cycle
		    mintime = 4
		    if((time.time() - lastt) < mintime):
			    print 'time delay fired'
			    time.sleep(mintime)


		    #otherwise, set the power
		    set_powers(plow, pup, tinit)
		    lastplow = plow
		    lastpup = pup
		    lastt = time.time()
		    break

		else:
		    #wait roughly until the correct time
		    nexttime = thist
		    waittime = nexttime - (time.time() - tinit)
		    print 'waiting' + str(waittime)
		    time.sleep(waittime)

	    
	    	


if __name__ == "__main__":
	if(len(sys.argv) > 2):
		print "Arguments are:"
		print "python run_power_instructions.py <instruction_file>"

	instructional = sys.argv[1]

	#the setfile will be used for process control
	#to make sure things aren't going wrong in automation
	setfile = "setpoints.txt"

	#you must start this program with the
	#heaters being already on, since it uses
	#the hup_power.py functions. 
	hup_enable, hlow_enable = get_setfile_enables(setfile)
	if(hup_enable != 1 or hlow_enable != 1):
		print "Heaters must start in the on state before beginning a long term automation"
		print "Killing"
		#sys.exit() #uncomment this before running fully

	#Load in the instructions
	inst_data = np.genfromtxt(instructional, delimiter=',', dtype=str)
	first_time = float(inst_data[0][-1])
	end_time = float(inst_data[-1][-1])
	totaltime = end_time - first_time #in seconds
	#require confirmation from the user that the timing is correct
	print "The total time this automation will run is : " + str(totaltime) + " seconds or " + str(totaltime/3600.0) + " hours" 
	#conf = raw_input("Do you accept that this is correct? (y/n)")
	#if(conf == "n"):
		#print "Exiting"
		#sys.exit()


	maxp = 250 #max allowed power input for one heater controller
	#check for bad typos in the datafile
	for j,d in enumerate(inst_data):
		plow = float(d[0])
		pup = float(d[1])
		thist = float(d[2])
		if(thist > end_time or thist < first_time):
			print "Typo in times on line " + str(j) + ": " 
			print d
			sys.exit()
		if(pup > maxp or plow > maxp):
			print "One instruction has too high a power. Line " + str(j) + ": "
			print d
			sys.exit()
		if(pup < 0 or plow < 0):
			print "One instruction has negative power. Line " + str(j) + ": "
			print d
			sys.exit()
	

	#all is good at this point, run automation 
	run_automation(inst_data, setfile)	
	
	
