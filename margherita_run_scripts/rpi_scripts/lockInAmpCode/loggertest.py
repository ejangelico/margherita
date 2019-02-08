import serial
import time
import re

ser=serial.Serial(port='/dev/ttyUSB0',baudrate=9600,bytesize=8,parity=serial.PARITY_EVEN,stopbits=1,timeout=None,xonxoff=False,rtscts=False,dsrdtr=False)

ser.write('id\r')
time.sleep(2)
print ser.read(ser.inWaiting())

while True:
	ser.write('sen\r')
	time.sleep(1)
	ser.write('out\r')
	currentTime=time.strftime('%m-%d-%y %H:%M:%S')
	time.sleep(2)
	reply=(ser.read(ser.inWaiting()))
	print "reply is: " + reply
	items =  re.split('\r\n',reply)
	senRangeCode=int(items[1])
	print 'parsed list of reply is: ' + ','.join(items)
	print 'status prompts are: {0} and {1}'.format(items[2][0],items[4])
	print 'senRangeCode = {0}'.format(senRangeCode)
	output=int(items[3])
	senRange=(1+2*(senRangeCode % 2))*10**(senRangeCode/2-13)
	current = senRange*output*1e-4
	entry='{0},{1},{2}\n'.format(current,senRange,currentTime)
	print "logfile entry is: " + entry
	print "0-10000 integer output is: " + str(abs(output))
	if abs(output) > 1e4:
		ser.write('sen {0}\r'.format(senRangeCode+1))
		print 'sen {0}\r'.format(senRangeCode+1)
		time.sleep(1)
		ser.flushInput()
		time.sleep(1)
	elif abs(output) < 2500:
		ser.write('sen {0}\r'.format(senRangeCode-1))
		print 'sen {0}\r'.format(senRangeCode-1)
		time.sleep(1)
		ser.flushInput()
		time.sleep(1)
