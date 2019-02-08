import serial
from time import sleep
import struct

portname = "/dev/ttyUSB0"


port = serial.Serial(portname, baudrate=28800, timeout=0.1)
print "baudrate is %d" % port.baudrate
while True:
	senddata = raw_input(" >")
	port.write('{:s}\r'.format(senddata))
	sleep(.05)
	rcv = port.read(100)
	print "You received back: %r" % rcv
