import serial
import time

asm = serial.Serial("/dev/ttyUSB3", baudrate=9600,bytesize=8,stopbits=1,parity="N",xonxoff=False,timeout=5)
time.sleep(1)
asm.flushInput()
if(asm.isOpen() is False):
	print "Could not open the ASM 340 serial port"
	sys.exit()

asm.write("!AC\r\n")
time.sleep(0.5)
print "Done."
asm.close()
