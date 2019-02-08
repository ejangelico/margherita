import DPS
import time
import sys
import os

#reads the setfile line by line and
#sends the parameters to each heater
def sendSetfileParameters(setfile, hlow, hup):
    f = open(setfile, 'r')
    lines = f.readlines()   
    
    #upper heater values
    upline = lines[1].split(',')
    up_enable = bool(int(upline[1]))
    up_v = float(upline[2])
    up_i = float(upline[3])


    #lower heater values
    lowline = lines[2].split(',')
    low_enable = bool(int(lowline[1]))
    low_v = float(lowline[2])
    low_i = float(lowline[3])

    #set voltages and currents
    hup.set_v(up_v)
    hlow.set_v(low_v)
    hup.set_i(up_i)
    hlow.set_i(low_i)

    #turn on or off
    if(up_enable):
	hup.turn_on()
    else:
	hup.turn_off()

    if(low_enable):
	hlow.turn_on()
    else:
	hlow.turn_off()

    return


def logData(logfile, hlow, hup):
    up_v, up_i, up_p = hup.read_vcp_applied()
    low_v, low_i, low_p = hlow.read_vcp_applied()
    data = [low_v, low_i, low_p, up_v, up_i, up_p]
    data = [str(_) for _ in data]
    outstr = ','.join(data) + ',' + str(time.strftime("%m-%d-%y %H:%M:%S")) + '\n'
    if(os.path.exists(logfile)):
	f = open(logfile, 'a')
    else:
	f = open(logfile, 'w')

    f.write(outstr)
    f.close()

if __name__ == "__main__":
    setfile = "./setpoints.txt"		#file to look in for setpoint configurations
    logfile = "../data/marg2heater_data/marg2heaterLog%s.txt" % time.strftime('%y%m%d') #file to log control TC's into


    
    hlow = DPS.DPS('/dev/ttyUSB1')
    hup = DPS.DPS('/dev/ttyUSB2')
    #hlow = None
    #hup = None

    #get the initial timestamp for file modification on the setfile
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(setfile)
    lastmod =  mtime


    #load the setfile for the first time
    #set all zone parameters for the first time
    sendSetfileParameters(setfile, hlow, hup)

    #log data
    logData(logfile, hlow, hup)
    

    waitTime = 2
    #start logging and watching
    while True:
    	#check if the setfile has been modified
    	(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(setfile)
    	if (lastmod != mtime):
		#update filename to reflect current date
		logfile = "../data/marg2heater_data/marg2heaterLog%s.txt" % time.strftime('%y%m%d') 

		logData(logfile, hlow, hup)
		sendSetfileParameters(setfile, hlow, hup)
    		lastmod = mtime
    		time.sleep(waitTime) #wait for powers to settle

		#update logfile name again just in case of coincidence
		logfile = "../data/marg2heater_data/marg2heaterLog%s.txt" % time.strftime('%y%m%d') 
		#log again
		logData(logfile, hlow, hup)

	time.sleep(waitTime)
