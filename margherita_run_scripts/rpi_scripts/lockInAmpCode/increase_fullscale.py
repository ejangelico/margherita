import serial
import time
import re

ser=serial.Serial(port='/dev/lock',baudrate=9600,bytesize=8,parity=serial.PARITY_EVEN,stopbits=1,timeout=None,xonxoff=False,rtscts=False,dsrdtr=False)
# open serial communications port to the amplifier

scaleTime=0.4
minScale=6
maxLoops=20

def fastCmd(ser,cmd):
	ser.flushInput()
	ser.write(cmd + '\r')
	start=time.time()
	reply=''
	term=False
	loops=0
	while (not(term))and(loops<maxLoops):
		char=ser.read(1)
		loops += 1
		if (char=='*'):
			error=False
			term=True
		elif (char=='?'):
			error=True
			term=True
		else:
			reply += char
	items=re.split('\r\n',reply)
	#print (time.time()-start)
	return (re.split('\r\n',reply),error)

def getScale(ser):
	reply=fastCmd(ser,'sen')
	print reply
	return int(reply[0][1])

def setScale(ser,scale):
	if scale < minScale:
		print "Scale < {} not acceptable".format(minScale)
		scale = minScale
	term=False
	loops=0
	while True:
                if(term == True or loops > maxLoops):
                    break
		print 'setting scale to: {}'.format(scale)
		reply=fastCmd(ser,'sen {}'.format(scale))
		print reply
		result=getScale(ser)
		if result==scale:
			term=True
		loops += 1


def getOvld(ser):
	reply=fastCmd(ser,'st')
	return (((int(reply[0][1]))&16)==16)


cursc = getScale(ser)
setScale(ser, cursc+1)
