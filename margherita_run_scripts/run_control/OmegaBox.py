import serial
import sys
import time
import re


class OmegaBox:
    def __init__(self, devAddr):
	self.dev = devAddr	    #string that is, for example, '/dev/ttyUSB1'
	self.ser_io = serial.Serial(port=devAddr, baudrate=4800, timeout=3) 

	#do an initial check that the serial port has been opened 
	#and communications are going well. It should be open at first
	#by default
	
	self.ser_io.flushInput()
	self.ser_io.flushOutput()
	if(self.ser_io.isOpen()):
	    pass
	else:
	    print "Serial port is not open. Please fix serial connection to Omega box"
	    return

    #returns the temperatures of each zone
    #in the form of a list
    def readAllTemps(self):
	#open the stream
	self.ser_io.open()
	#write command to get all temperatures
	self.ser_io.write("L0T")
	time.sleep(0.3)
	#receive the result
	result = self.ser_io.read(28)
	result = result[:-4]
	#close the stream
	self.ser_io.flushInput()
	self.ser_io.flushOutput()
	self.ser_io.close()
	#parse result into a list
	temps = re.findall('....',result)
	
	
	#remove leading zeros so that 
	#strings like '0020' go to '20'
	finaltemps = []
	for tt in temps:
	    finaltemps.append(tt.lstrip('0'))
	return finaltemps

    
    #write all setpoints for all zones. 
    #this takes fewer serial communications then
    #writing one setpoint at a time
    #takes a list of setpoints [sp, sp, sp, sp...]
    #of length 6
    def writeAllSetPoints(self, setpoints):
	filledString = ''
	for sp in setpoints:
	    filledString = filledString + sp.zfill(4)

	self.ser_io.open()
	self.ser_io.write('L0b'+filledString)
	time.sleep(0.3)
	self.ser_io.flushInput()
	self.ser_io.flushOutput()
	self.ser_io.close()

    #returns a list of setpoints that
    #are the current values for each zone
    def readAllSetPoints(self):
	self.ser_io.open()
	self.ser_io.write('L0B')
	time.sleep(0.3)
	result = self.ser_io.read(24)
	self.ser_io.flushInput()
	self.ser_io.flushOutput()
	self.ser_io.close()
	sepresult = re.findall('....',result)

	#remove leading zeros so that 
	#strings like '0020' go to '20'
	setpoints = []
	for sp in sepresult:
	    setpoints.append(sp.lstrip('0'))

	    
	return setpoints


	
    #set enabled zones
    #takes a list of booleans
    #[1,0,1,1,0,...], one value for each
    #zone
    def writeEnabledZones(self, en):
	#one integer associated with
	#zones 1 2 3, one for zones 4, 5, 6
	#[77] corresponds to [0111 0111]
	#which is 6 5 4, 3 2 1
	str321 = '0' 
	str321 = str321 + str(en[2]) + str(en[1]) + str(en[0])
	str654 = '0' 
	str654 = str654 + str(en[5]) + str(en[4]) + str(en[3])
	#turn each binary word into an integer 0 - 7
	zeInt = ''
	zeInt = zeInt + str(int(str654, 2))
	zeInt = zeInt + str(int(str321, 2))
	#now this number is like "77" as a string


	#to change the enabled zones, I need to append
	#to a longer string that also sets operation modes
	#"idstring" info can be found on page 9 of manual
	idstring = '00300400051011'

	result = str(zeInt) + idstring
	
	#send the new data back
	self.ser_io.open()
	self.ser_io.write('L0j'+result)
	time.sleep(0.3)
	self.ser_io.flushInput()
	self.ser_io.flushOutput()
	self.ser_io.close()
	return




