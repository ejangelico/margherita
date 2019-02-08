#Written by Evan Angelico, 9/20/18
#Talks to an ASM340 pfeiffer leak checker and 
#toggles sound mode on or off



import serial
import time
import sys


if(len(sys.argv) != 2):
	print "usage: python toggle_sound.py <1 = on, 0 = off>"
	sys.exit()


toggle_str = None
if(sys.argv[1] == "1"):
	toggle_str = 'E'
	print "Turning sound on"
elif(sys.argv[1] == "0"):
	toggle_str = 'D'
	print "Turning sound off"
else:
	print "usage: python toggle_sound.py <1 = on, 0 = off>"
	sys.exit()



asm = serial.Serial("/dev/ttyUSB1", baudrate=9600,bytesize=8,stopbits=1,parity="N",xonxoff=False,timeout=5)
asm.flushInput()
time.sleep(1)
if(asm.isOpen() is False):
	print "Could not open the ASM 340 serial port"
	sys.exit()

asm.write("=SO1"+toggle_str+"\r\n")
time.sleep(0.5)
print "Done."
asm.close()

