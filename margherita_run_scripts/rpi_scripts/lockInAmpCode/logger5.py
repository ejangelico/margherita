import serial
import time
import re

ser=serial.Serial(port='/dev/lock',baudrate=9600,bytesize=8,parity=serial.PARITY_EVEN,stopbits=1,timeout=None,xonxoff=False,rtscts=False,dsrdtr=False)
# open serial communications port to the amplifier

ser.write('id\r')
# query the id of the amplifier
time.sleep(2)
# wait for a response
print ser.read(ser.inWaiting())
# read everything in the serial buffer

while True:
	file=open('./data/photoCurrentLog{0}.txt'.format(time.strftime('%y%m%d')),'a')
	# open a file for writing data corresponding to today's date
	ser.flushInput()
	# flush input to prevent stuff from previous loops from breaking the
	# parser

	ser.write('sen\r')
	# query the sensitivity setting of the amplifier
	time.sleep(1)
	# wait for the amplifier to complete the query
	ser.write('out\r')
	# get a reading from the amplifier
	currentTime=time.strftime('%m-%d-%y %H:%M:%S')
	# get the time at which the reading was taken
	time.sleep(2)
	# wait for comletion
	
	reply=(ser.read(ser.inWaiting()))
	# read everything in the buffer
	items =  re.split('\r\n',reply)
	"""
	split the reply into chunks separated by the terminator, \r\n
	these correspond to:
	0:	echo 'sen'
	1:	sensitivity code, an integer between 0 and 15 which should be >5
	2: ('*' or '?') + 'out'
	3:	amplifier reading, signed integer of magnitude <15000
	4: ('*' or '?')
	"""
	
	print ','.join(items)
	senRangeCode=int(items[1])
	# get current amplifier sensitivity code from serial buffer
	print 'senRangeCode = {0}'.format(senRangeCode)
	output=int(items[3])
	# get last amplifier reading from serial buffer
	senRange=(1+2*(senRangeCode % 2))*10**(senRangeCode/2-13)
	# convert amplifier sensitivity code to amplifier sensitivity
	current = senRange*output*1e-4
	# parse sensitivity and reading into a current value
	entry='{0},{1},{2}\n'.format(current,senRange,currentTime)
	# write the current, amplifier sensitivity and time into a logfile entry
	print entry
	file.write(entry)
	file.close()
	# write to file and close file

	if (items[4] == '*') and (items[2][0] == '*'):
		# if amplifier is not in error, proceed to check sensitivity
		if abs(output) > 1e4:
			# if reading is high, go to higher scale
			r=senRangeCode+1
			if r < 6:
				r = 6
			# never set range code below 6 in current configuration
			print r
			ser.write('sen {0}\r'.format(r))
			# set new sensitivity on amplifier
			print 'sen {0}\r'.format(r)
			time.sleep(1)
			ser.flushInput()
			time.sleep(1)
		elif abs(output) < 2000:
			# if reading is low, go to lower scale
			r=senRangeCode-1
			if r < 6:
				r = 6
			# never set range code below 6 in current configuration
			print r
			ser.write('sen {0}\r'.format(r))
			# set new sensitivity on amplifier
			print 'sen {0}\r'.format(r)
			time.sleep(1)
			ser.flushInput()
			time.sleep(1)
	elif (items[4] == '?') or (items[2][0] == '?'):
		# if error condition exists
		ovld=16
		# assume error condition is overload, so set ovld=16
		while ovld==16:
			print ovld
			ser.write('st\r')
			# query status byte
			time.sleep(0.5)
			reply=(ser.read(ser.inWaiting()))
			items =  re.split('\r\n',reply)
			# read everything in the buffer and split it by the terminator
			if ((int(items[1]))&16) == 16:
				# if bit 4 ==1, amplifier is in overload
				ser.write('sen {0}\r'.format(senRangeCode+1))
				senRangeCode += 1
				# increase the scale to get out of overload
				print 'sen {0}\r'.format(senRangeCode+1)
				time.sleep(0.5)
				ser.flushInput()
			else:
				ovld=0
				# once amplifier is no longer in overload, set ovld=0 to break loop
	else:
		print "Something unexpected occurred. Exiting now."
		exit()
