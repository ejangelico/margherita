#Written by Evan Angelico, 10/10/18
#Talks to an ASM340 pfeiffer leak checker and 
#toggles sniff mode on or off



import serial
import time
import sys
import os



def read_leakrate(asm):
	asm.write("?LE\r\n")
	time.sleep(0.2)
	output = asm.read(6)
	asm.flushInput()
	asm.flushOutput()
	timestamp = str(time.strftime("%m-%d-%y %H:%M:%S"))
	#format output into a float
	output = output.split('-')
	if(len(output) != 2):
		print "Error, got unexpected message from asm"
		return 1, timestamp
	output = output[0]+"e-"+output[1]
	return float(output),timestamp

if __name__ == "__main__":

	if(len(sys.argv) != 1):
		print "usage: python log_leakrate.py"
		sys.exit()



	asm = serial.Serial("/dev/ttyUSB1", baudrate=9600,bytesize=8,stopbits=1,parity="N",xonxoff=False,timeout=5)
	asm.flushInput()
	time.sleep(1)
	if(asm.isOpen() is False):
		print "Could not open the ASM 340 serial port"
		sys.exit()

	sample_time = 1
	#start logging and watching
	while True:
		#update filename to reflect current date
		logfile = "../data/leak_data/leakLog%s.txt" % time.strftime('%y%m%d')
		 
		if(os.path.exists(logfile)):
		    f = open(logfile, 'a')
		else:
		    f = open(logfile, 'w')

		leak, timestamp = read_leakrate(asm)
		outstr = str(leak)+","+timestamp+"\n"
		print outstr
		f.write(outstr)
		time.sleep(sample_time)



