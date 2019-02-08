import serial
import time
import re

ser=serial.Serial(port='/dev/ttyUSB0',baudrate=9600,bytesize=8,parity=serial.PARITY_EVEN,stopbits=1,timeout=None,xonxoff=False,rtscts=False,dsrdtr=False)


