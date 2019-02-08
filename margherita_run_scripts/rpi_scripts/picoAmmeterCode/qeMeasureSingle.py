import wiringpi 
import sys
import time
import serial

ttlOutputChannel=2
numSwitches=5
period=1.0

board_type = sys.argv[-1]
if board_type == "m":
    poss_channels = 7
else:
    poss_channels = 6

def reset_ports():
    wiringpi.digitalWrite(4, 0)         # switches off LED
    wiringpi.pinMode(4,0)               # set LED back to input mode

wiringpi.wiringPiSetupGpio()                        # Initialise GPIO
wiringpi.pinMode(4, 1)                              # set up LED for output

a=serial.Serial('/dev/ttyUSB0',baudrate=9600,bytesize=8,parity='N',timeout=None,xonxoff=False,stopbits=1)
a.flushInput()
a.write('\r*cls\r')
print('curr.nplc {0:.2f}\r'.format(period*0.3*60))
a.write('curr.nplc {0:.2f}\r'.format(period*0.3*60))
a.write('form:elem read\r')

logfile=open('./data/qeLog_{0}.txt'.format(time.strftime('%y%m%d_%H%M%S')),'a')
loglist=[]

try:
    for _ in range(numSwitches):
        wiringpi.digitalWrite(4, 1)                 # switch LED on
        time.sleep(period*0.05)
        a.write('read?\r')
        print('Reading with LED on')
        time.sleep(period*0.44)
        lastReading=a.read(a.inWaiting())
        loglist.append(lastReading[0:-1])
        wiringpi.digitalWrite(4, 0)                 # switch LED off
        time.sleep(period*0.05)
        a.write('read?\r')
        print('Reading with LED off')
        time.sleep(period*0.44)
        lastReading=a.read(a.inWaiting())
        loglist.append(lastReading[0:-1])

except KeyboardInterrupt:                   # trap a CTRL+C keyboard interrupt
    reset_ports()                           # reset ports

print(','.join(loglist)+'\n')
#logfile.write(','.join(loglist)+'\n')
reset_ports()       # reset ports on normal exit
